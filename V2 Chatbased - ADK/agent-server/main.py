"""
ADK WebSocket Server - Agent Development Kit Version
"""

import asyncio
import websockets
import json
import logging
from pathlib import Path
import sys

# Add agent modules to path - FIXED: Use proper path resolution
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))
sys.path.insert(0, str(current_dir.parent))

# ✅ FIXED: Use absolute imports with proper error handling
try:
    from agents.orchestrator import ADKOrchestrator
    from services.project_builder import ADKProjectBuilder
    from storage.local_storage import LocalStorage
    from config import settings
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("🔄 Trying alternative import paths...")
    # Alternative import paths
    try:
        from .agents.orchestrator import ADKOrchestrator
        from .services.project_builder import ADKProjectBuilder  
        from .storage.local_storage import LocalStorage
        from ..config import settings
    except ImportError as e2:
        print(f"❌ Alternative import also failed: {e2}")
        raise

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ADKAIDEServer:
    def __init__(self):
        self.orchestrator = ADKOrchestrator()
        self.project_builder = ADKProjectBuilder()
        self.storage = LocalStorage()
        self.active_connections = set()
    
    async def handle_connection(self, websocket):
        """Handle new WebSocket connection"""
        self.active_connections.add(websocket)
        client_info = f"{websocket.remote_address[0]}:{websocket.remote_address[1]}" if websocket.remote_address else "unknown"
        logger.info(f"🟢 ADK Client connected: {client_info}. Total: {len(self.active_connections)}")
        
        try:
            async for message in websocket:
                await self.process_message(websocket, message)
                
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"🔴 ADK Client disconnected: {client_info}")
        except Exception as e:
            logger.error(f"❌ ADK Error with client {client_info}: {str(e)}")
        finally:
            self.active_connections.discard(websocket)
            logger.info(f"🟡 ADK Client removed: {client_info}. Remaining: {len(self.active_connections)}")
    
    async def process_message(self, websocket, message):
        """Process incoming WebSocket message"""
        try:
            data = json.loads(message)
            await self.process_request(websocket, data)
        except json.JSONDecodeError:
            await self.send_error(websocket, "Invalid JSON format")
        except Exception as e:
            logger.error(f"❌ ADK Message processing error: {str(e)}")
            await self.send_error(websocket, f"ADK Processing error: {str(e)}")
    
    async def process_request(self, websocket, data):
        """Process different types of requests"""
        message_type = data.get('type', 'message')
        
        if message_type == 'new_project':
            await self.handle_new_project(websocket, data)
        elif message_type == 'user_message':
            await self.handle_user_message(websocket, data)
        elif message_type == 'get_preview':
            await self.handle_get_preview(websocket, data)
        elif message_type == 'check_generation_status':
            await self.handle_check_generation_status(websocket, data)
        elif message_type == 'generate_code':
            await self.handle_generate_code(websocket, data)
        elif message_type == 'ping':
            await self.send_pong(websocket)
        else:
            await self.send_error(websocket, f"Unknown ADK message type: {message_type}")
    
    async def handle_new_project(self, websocket, data):
        """Start a new project with ADK"""
        project_id = None
        try:
            project_name = data.get('project_name', 'New Project')
            project_id = self.storage.create_project(project_name)
        
            response = {
                'type': 'project_created',
                'project_id': project_id,
                'project_name': project_name
            }
            await websocket.send(json.dumps(response))
        
            # Send ADK welcome message
            welcome_msg = await self.orchestrator.start_conversation(project_id)
            await self.send_agent_response(websocket, welcome_msg, 'requirements_evolver')
        
        except Exception as e:
            logger.error(f"❌ ADK New project error: {str(e)}")
        
            if project_id:
                self.storage.cleanup_project(project_id)
            
            await self.send_error(websocket, f"ADK Failed to create project: {str(e)}")  
                          
    async def handle_user_message(self, websocket, data):
        """Process user message through ADK agents"""
        try:
            project_id = data.get('project_id')
            user_message = data.get('message', '')
            
            if not project_id:
                await self.send_error(websocket, "No project ID provided")
                return
            
            # Store user message
            self.storage.add_message(project_id, 'user', user_message)
            
            # Route through ADK orchestrator
            agent_response = await self.orchestrator.route_message(project_id, user_message)
            
            # Store agent response
            self.storage.add_message(project_id, 'agent', agent_response['message'])
            
            # Send response to frontend
            await self.send_agent_response(websocket, agent_response['message'], agent_response['agent'])
            
            logger.info(f"💬 ADK Chat message processed for {project_id}")
            
            # Send generation status
            generation_status = await self.orchestrator.can_generate_code(project_id)
            await self.send_generation_status(websocket, project_id, generation_status)
                
        except Exception as e:
            logger.error(f"❌ ADK User message error: {str(e)}")
            await self.send_error(websocket, f"ADK Failed to process message: {str(e)}")
    
    async def handle_check_generation_status(self, websocket, data):
        """Check ADK generation status"""
        try:
            project_id = data.get('project_id')
            
            if not project_id:
                await self.send_error(websocket, "No project ID provided")
                return
            
            generation_status = await self.orchestrator.can_generate_code(project_id)
            await self.send_generation_status(websocket, project_id, generation_status)
            
        except Exception as e:
            logger.error(f"❌ ADK Generation status check error: {str(e)}")
            await self.send_error(websocket, f"ADK Failed to check generation status: {str(e)}")
    
    async def handle_generate_code(self, websocket, data):
        """Generate code with ADK"""
        try:
            project_id = data.get('project_id')
            
            if not project_id:
                await self.send_error(websocket, "No project ID provided")
                return
            
            # Check generation status
            generation_status = await self.orchestrator.can_generate_code(project_id)
            
            if not generation_status['can_generate']:
                error_response = {
                    'type': 'generation_failed',
                    'project_id': project_id,
                    'error': 'Insufficient requirements',
                    'message': generation_status['message'],
                    'status': 'failed'
                }
                await websocket.send(json.dumps(error_response))
                logger.warning(f"⚠️  ADK Code generation blocked for {project_id}: {generation_status['message']}")
                return
            
            # Proceed with ADK code generation
            logger.info(f"🎯 ADK Manual code generation triggered for project {project_id}")
            await self.generate_project_code(websocket, project_id)
            
        except Exception as e:
            logger.error(f"❌ ADK Generate code error for {project_id}: {str(e)}")
            await self.send_error(websocket, f"ADK Failed to generate code: {str(e)}")
    
    async def handle_get_preview(self, websocket, data):
        """Get ADK project preview URL"""
        try:
            project_id = data.get('project_id')
            if not project_id:
                await self.send_error(websocket, "No project ID provided")
                return
                
            preview_url = self.project_builder.get_preview_url(project_id)
            
            response = {
                'type': 'preview_url',
                'project_id': project_id,
                'preview_url': preview_url
            }
            await websocket.send(json.dumps(response))
        except Exception as e:
            logger.error(f"❌ ADK Preview error: {str(e)}")
            await self.send_error(websocket, f"ADK Failed to get preview: {str(e)}")
    
    async def generate_project_code(self, websocket, project_id):
        """Generate project code with ADK"""
        try:
            project_data = self.storage.get_project(project_id)
            
            if not project_data:
                await self.send_error(websocket, f"Project {project_id} not found")
                return
            
            # Send generation started message
            await self.send_generation_started(websocket, project_id)
            
            # Generate project files with ADK
            generated_files = await self.project_builder.generate_project(project_data)
            
            # Store generated files
            for file_data in generated_files:
                self.storage.add_generated_file(project_id, file_data['path'], file_data['content'])
            
            # Get preview URL
            preview_url = self.project_builder.get_preview_url(project_id)
        
            response = {
                'type': 'code_generated',
                'files': generated_files,
                'preview_url': preview_url,
                'project_id': project_id,
                'file_count': len(generated_files),
                'total_size': sum(f.get('size', 0) for f in generated_files),
                'status': 'success'
            }
        
            await websocket.send(json.dumps(response))
            logger.info(f"✅ ADK Code generated for project {project_id}: {len(generated_files)} files")
        
        except Exception as e:
            logger.error(f"❌ ADK Code generation error for {project_id}: {str(e)}")
            
            error_response = {
                'type': 'code_generation_error',
                'project_id': project_id,
                'error': str(e),
                'status': 'failed'
            }
            await websocket.send(json.dumps(error_response))
            
            await self.send_error(websocket, f"ADK Failed to generate code: {str(e)}")
    
    async def send_generation_status(self, websocket, project_id, status):
        """Send generation status to client"""
        response = {
            'type': 'generation_status',
            'project_id': project_id,
            'can_generate': status['can_generate'],
            'substantial_agents': status['substantial_agents'],
            'agent_contributions': status['agent_contributions'],
            'has_minimal_requirements': status['has_minimal_requirements'],
            'message': status['message'],
            'timestamp': asyncio.get_event_loop().time()
        }
        await websocket.send(json.dumps(response))
    
    async def send_generation_started(self, websocket, project_id):
        """Send generation started message"""
        response = {
            'type': 'generation_started',
            'project_id': project_id,
            'message': 'Starting ADK code generation...'
        }
        await websocket.send(json.dumps(response))
    
    async def send_agent_response(self, websocket, message, agent_name):
        """Send agent response to client"""
        response = {
            'type': 'agent_response',
            'message': message,
            'agent': agent_name,
            'timestamp': asyncio.get_event_loop().time()
        }
        await websocket.send(json.dumps(response))
    
    async def send_error(self, websocket, error_msg):
        """Send error message to client"""
        response = {
            'type': 'error',
            'message': error_msg,
            'timestamp': asyncio.get_event_loop().time()
        }
        await websocket.send(json.dumps(response))
    
    async def send_pong(self, websocket):
        """Send pong response"""
        response = {
            'type': 'pong',
            'message': 'pong'
        }
        await websocket.send(json.dumps(response))

    async def run_server(self):
        """Start the ADK WebSocket server"""
        try:
            logger.info(f"🚀 Starting ADK AIDE Server on port {settings.WS_SERVER_PORT}")
            
            # Test if port is available
            import socket
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', settings.WS_SERVER_PORT))
            
            async with websockets.serve(self.handle_connection, "localhost", settings.WS_SERVER_PORT):
                logger.info(f"✅ ADK AIDE Server running on ws://localhost:{settings.WS_SERVER_PORT}")
                logger.info("📋 Available endpoints:")
                logger.info("  - new_project: Start a new project")
                logger.info("  - user_message: Send message to agents") 
                logger.info("  - generate_code: Generate project code")
                logger.info("  - get_preview: Get project preview URL")
                logger.info("  - check_generation_status: Check if ready to generate")
                
                # Keep server running
                await asyncio.Future()
                
        except OSError as e:
            if "Address already in use" in str(e):
                logger.error(f"❌ Port {settings.WS_SERVER_PORT} is already in use")
                logger.error("💡 Please check if another server is running or use a different port")
            else:
                logger.error(f"❌ Failed to start ADK server: {e}")
        except Exception as e:
            logger.error(f"❌ ADK Server startup error: {e}")

async def main():
    """Main entry point"""
    server = ADKAIDEServer()
    await server.run_server()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("🛑 ADK Server stopped by user")
    except Exception as e:
        logger.error(f"❌ ADK Server fatal error: {e}")