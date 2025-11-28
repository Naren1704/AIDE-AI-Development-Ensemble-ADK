"""
ADK Core Components - With Model Discovery
"""

import asyncio
from typing import Dict, List, Any, Optional, AsyncGenerator
import logging
import google.generativeai as genai
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini
from config.settings import GEMINI_API_KEY, RETRY_CONFIG

logger = logging.getLogger("ADK.Manager")

class ADKManager:
    """Complete ADK manager with automatic model discovery"""
    
    def __init__(self):
        self.session_service = InMemorySessionService()
        self.llm = self._setup_gemini_with_discovery()
        self.agents: Dict[str, Agent] = {}
        self.app_name = "aide_adk_app"
        self.runners: Dict[str, Runner] = {}
        
        self._register_default_agents()
        self._initialize_runners()
        logger.info("✅ ADK Manager initialized with Google ADK integration")
    
    def _discover_working_models(self):
        """Discover which Gemini models actually work with the current API"""
        # Configure the API
        genai.configure(api_key=GEMINI_API_KEY)
        
        working_models = []
        
        # Test models in priority order
        test_models = [
            # Try latest versions first
            "gemini-1.5-flash-latest",
            "gemini-1.0-pro-latest", 
            "gemini-1.5-pro-latest",
            
            # Try specific versions
            "gemini-1.5-flash-001",
            "gemini-1.0-pro-001",
            "gemini-1.5-pro-001",
            
            # Try legacy names
            "gemini-pro",
            "gemini-pro-vision",
            
            # Try experimental
            "gemini-2.0-flash-exp",
        ]
        
        logger.info("🔍 Discovering working Gemini models...")
        
        for model_name in test_models:
            try:
                # Try to get model info
                model = genai.get_model(model_name)
                
                # Check if it supports generateContent
                if 'generateContent' in model.supported_generation_methods:
                    working_models.append(model_name)
                    logger.info(f"✅ Found working model: {model_name}")
                    logger.info(f"   Methods: {model.supported_generation_methods}")
                    logger.info(f"   Input tokens: {model.input_token_limit}")
                    
                    # Return the first working model
                    return model_name
                    
            except Exception as e:
                logger.debug(f"❌ Model {model_name} not available: {str(e)[:100]}...")
        
        # If no models found, list all available
        logger.warning("⚠️  No standard models found, listing all available models...")
        try:
            all_models = genai.list_models()
            available_models = []
            
            for model in all_models:
                if 'generateContent' in model.supported_generation_methods:
                    available_models.append(model.name)
                    logger.info(f"📋 Available: {model.name} - {model.display_name}")
            
            if available_models:
                logger.info(f"🎯 Try using one of these: {available_models[:3]}")
                return available_models[0]  # Use first available
                
        except Exception as e:
            logger.error(f"❌ Could not list models: {e}")
        
        raise Exception("No working Gemini models found. Please check your API configuration.")
    
    def _setup_gemini_with_discovery(self) -> Gemini:
        """Setup Gemini model with automatic model discovery"""
        try:
            # Discover working model
            model_name = self._discover_working_models()
            
            logger.info(f"🚀 Using model: {model_name}")
            
            return Gemini(
                model=model_name,
                temperature=0.7,
                max_output_tokens=2000,
                retry_config=RETRY_CONFIG
            )
            
        except Exception as e:
            logger.error(f"❌ Model discovery failed: {e}")
            logger.info("🔄 Falling back to manual model configuration...")
            
            # Fallback models to try
            fallback_models = [
                "gemini-1.5-flash-latest",
                "gemini-1.0-pro-latest", 
                "gemini-pro"
            ]
            
            for model_name in fallback_models:
                try:
                    logger.info(f"🔄 Trying fallback: {model_name}")
                    return Gemini(
                        model=model_name,
                        temperature=0.7,
                        max_output_tokens=2000,
                        retry_config=RETRY_CONFIG
                    )
                except Exception:
                    continue
            
            raise Exception("All model configurations failed. Please check your API key and model availability.")
    
    def _register_default_agents(self):
        """Register default agents with proper Google ADK Agent instances"""
        try:
            # Requirements Evolver
            self.agents["requirements_evolver"] = Agent(
                name="requirements_evolver",
                model=self.llm
            )
            
            # UX Architect
            self.agents["ux_architect"] = Agent(
                name="ux_architect",
                model=self.llm
            )
            
            # UI Designer
            self.agents["ui_designer"] = Agent(
                name="ui_designer",
                model=self.llm
            )
            
            # Frontend Engineer
            self.agents["frontend_engineer"] = Agent(
                name="frontend_engineer",
                model=self.llm
            )
            
            # Data Architect
            self.agents["data_architect"] = Agent(
                name="data_architect",
                model=self.llm
            )
            
            # API Designer
            self.agents["api_designer"] = Agent(
                name="api_designer",
                model=self.llm
            )
            
            # DevOps
            self.agents["devops"] = Agent(
                name="devops",
                model=self.llm
            )
            
            # Code Generator Agent
            self.agents["code_generator"] = Agent(
                name="code_generator",
                model=self.llm
            )
            
            logger.info("✅ All ADK agents registered successfully")
            
        except Exception as e:
            logger.error(f"❌ Error registering ADK agents: {e}")
            raise
    
    def _initialize_runners(self):
        """Initialize a runner for each agent"""
        try:
            for agent_name, agent in self.agents.items():
                self.runners[agent_name] = Runner(
                    session_service=self.session_service,
                    app_name=self.app_name,
                    agent=agent
                )
            logger.info(f"✅ Initialized {len(self.runners)} agent runners")
        except Exception as e:
            logger.error(f"❌ Error initializing runners: {e}")
            raise
    
    def register_agent(self, name: str, instructions: str = "", description: str = "") -> Agent:
        """Register a new agent with the system and RETURN the agent instance"""
        try:
            agent = Agent(
                name=name,
                model=self.llm
            )
            self.agents[name] = agent
            
            # Also create a runner for the new agent
            self.runners[name] = Runner(
                session_service=self.session_service,
                app_name=self.app_name,
                agent=agent
            )
            
            logger.info(f"✅ Registered ADK agent: {name}")
            return agent
        except Exception as e:
            logger.error(f"❌ Error registering agent {name}: {e}")
            raise
    
    async def run_sequential_agents(self, session_id: str, user_input: str, agent_chain: List[str]) -> List[Dict[str, Any]]:
        """Run agents sequentially with proper Google ADK execution"""
        results = []
        
        for agent_name in agent_chain:
            if agent_name in self.agents and agent_name in self.runners:
                try:
                    # Get the runner for this specific agent
                    runner = self.runners[agent_name]
                    
                    # Ensure session exists before running
                    session = await self._ensure_session_exists(session_id)
                    
                    # Create Content object for new_message
                    new_message = types.Content(parts=[types.Part(text=user_input)])
                    
                    # Run the agent using async method
                    response_text = await self._run_agent_async(
                        runner=runner,
                        user_id=session_id,
                        session_id=session_id,
                        new_message=new_message
                    )
                    
                    # Update session memory
                    await self._update_session_memory(session, agent_name, user_input, response_text)
                    
                    result = {
                        'agent': agent_name,
                        'response': response_text,
                        'timestamp': asyncio.get_event_loop().time(),
                        'agent_info': {
                            'name': agent_name,
                            'description': f"Google ADK Agent: {agent_name}"
                        }
                    }
                    results.append(result)
                    logger.info(f"✅ ADK Agent {agent_name} processed message")
                    
                except Exception as e:
                    logger.error(f"❌ ADK Agent {agent_name} execution error: {e}")
                    results.append({
                        'agent': agent_name,
                        'response': f"Agent '{agent_name}' encountered an error: {str(e)}",
                        'timestamp': asyncio.get_event_loop().time()
                    })
            else:
                logger.warning(f"⚠️  ADK Agent or Runner not found: {agent_name}")
                results.append({
                    'agent': agent_name,
                    'response': f"Agent '{agent_name}' is not available.",
                    'timestamp': asyncio.get_event_loop().time()
                })
        
        return results
    
    async def _ensure_session_exists(self, session_id: str):
        """Ensure a session exists, create if it doesn't"""
        try:
            # Use correct get_session signature
            session = await self.session_service.get_session(
                app_name=self.app_name,
                user_id=session_id,
                session_id=session_id
            )
            
            if session:
                logger.debug(f"📁 Session exists: {session_id}")
                return session
            else:
                # Session doesn't exist, create it
                logger.debug(f"📁 Creating new session: {session_id}")
                session = await self.session_service.create_session(
                    app_name=self.app_name,
                    user_id=session_id,
                    session_id=session_id
                )
                logger.debug(f"📁 Created session: {session_id}")
                return session
                
        except Exception as e:
            # If get_session fails, create a new session
            logger.debug(f"📁 Creating new session (get failed): {session_id}")
            session = await self.session_service.create_session(
                app_name=self.app_name,
                user_id=session_id,
                session_id=session_id
            )
            logger.debug(f"📁 Created session: {session_id}")
            return session
    
    async def _run_agent_async(self, runner: Runner, user_id: str, session_id: str, new_message: types.Content) -> str:
        """Run agent using the async method"""
        try:
            events_generator = runner.run_async(
                user_id=user_id,
                session_id=session_id,
                new_message=new_message
            )
            
            # Process events asynchronously
            response_text = await self._process_events_async(events_generator)
            return response_text
            
        except Exception as e:
            logger.error(f"❌ Async agent execution error: {e}")
            raise
    
    async def _process_events_async(self, events_generator: AsyncGenerator) -> str:
        """Process events from the async generator and extract the final response"""
        try:
            response_parts = []
            
            async for event in events_generator:
                # Look for events that contain response text
                if hasattr(event, 'text') and event.text:
                    response_parts.append(event.text)
                elif hasattr(event, 'content') and event.content:
                    response_parts.append(str(event.content))
                elif hasattr(event, 'message') and event.message:
                    response_parts.append(event.message)
                # Log event type for debugging
                logger.debug(f"🔍 Event type: {type(event).__name__}")
            
            response_text = " ".join(response_parts).strip()
            return response_text if response_text else "No response generated"
            
        except Exception as e:
            logger.error(f"❌ Error processing async events: {e}")
            return f"Error processing response: {str(e)}"
    
    async def _update_session_memory(self, session, agent_name: str, user_input: str, response: str):
        """Update session memory"""
        try:
            # Store memory directly in session state
            if not hasattr(session, 'state'):
                session.state = {}
            
            if 'memory' not in session.state:
                session.state['memory'] = []
            
            session.state['memory'].append({
                'agent': agent_name,
                'user_input': user_input,
                'response': response,
                'timestamp': asyncio.get_event_loop().time()
            })
            
            # Compact memory if too large
            if len(session.state['memory']) > 10:
                session.state['memory'] = session.state['memory'][-8:]
            
            logger.debug(f"📝 Updated session memory for {agent_name}")
            
        except Exception as e:
            logger.error(f"❌ Error updating session memory: {e}")
    
    async def run_single_agent(self, session_id: str, agent_name: str, user_input: str) -> Dict[str, Any]:
        """Run a single agent with proper session handling"""
        if agent_name not in self.agents or agent_name not in self.runners:
            raise ValueError(f"Agent '{agent_name}' not found")
        
        try:
            # Get the runner for this specific agent
            runner = self.runners[agent_name]
            
            # Ensure session exists before running
            session = await self._ensure_session_exists(session_id)
            
            # Create Content object for new_message
            new_message = types.Content(parts=[types.Part(text=user_input)])
            
            # Run the agent using async method
            response_text = await self._run_agent_async(
                runner=runner,
                user_id=session_id,
                session_id=session_id,
                new_message=new_message
            )
            
            # Update session memory
            await self._update_session_memory(session, agent_name, user_input, response_text)
            
            return {
                'agent': agent_name,
                'response': response_text,
                'timestamp': asyncio.get_event_loop().time(),
                'success': True
            }
            
        except Exception as e:
            logger.error(f"❌ Single agent execution error for {agent_name}: {e}")
            return {
                'agent': agent_name,
                'response': f"Error: {str(e)}",
                'timestamp': asyncio.get_event_loop().time(),
                'success': False
            }
    
    async def run_agent_with_instructions(self, session_id: str, agent_name: str, instructions: str, user_input: str) -> Dict[str, Any]:
        """Run agent with custom instructions included in the prompt"""
        if agent_name not in self.agents or agent_name not in self.runners:
            raise ValueError(f"Agent '{agent_name}' not found")
        
        try:
            # Get the runner for this specific agent
            runner = self.runners[agent_name]
            
            # Ensure session exists before running
            session = await self._ensure_session_exists(session_id)
            
            # Combine instructions with user input
            full_prompt = f"{instructions}\n\nUser: {user_input}"
            
            # Create Content object for new_message
            new_message = types.Content(parts=[types.Part(text=full_prompt)])
            
            # Run the agent using async method
            response_text = await self._run_agent_async(
                runner=runner,
                user_id=session_id,
                session_id=session_id,
                new_message=new_message
            )
            
            # Update session memory
            await self._update_session_memory(session, agent_name, user_input, response_text)
            
            return {
                'agent': agent_name,
                'response': response_text,
                'timestamp': asyncio.get_event_loop().time(),
                'success': True
            }
            
        except Exception as e:
            logger.error(f"❌ Agent with instructions execution error for {agent_name}: {e}")
            return {
                'agent': agent_name,
                'response': f"Error: {str(e)}",
                'timestamp': asyncio.get_event_loop().time(),
                'success': False
            }
    
    def get_agent_info(self, agent_name: str) -> Dict[str, Any]:
        """Get information about a specific agent"""
        if agent_name in self.agents:
            agent = self.agents[agent_name]
            return {
                'name': agent_name,
                'has_agent': True,
                'description': f"Google ADK Agent: {agent_name}"
            }
        return {}
    
    def list_agents(self) -> List[str]:
        """List all registered agents"""
        return list(self.agents.keys())