"""
ADK Local Storage - Enhanced with Session Management & Memory
"""

import time
import json
import uuid
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from config import settings

logger = logging.getLogger('ADK.Storage')

class ADKSession:
    """Session & Memory Management for Agent Conversations"""
    
    def __init__(self, project_id: str):
        self.project_id = project_id
        self.messages = []
        self.agent_states = {}
        self.context_summary = ""
        self.last_activity = datetime.now()
        
    def add_message(self, role: str, message: str, agent: str = None):
        """Add message with session context"""
        message_data = {
            'role': role,
            'message': message,
            'agent': agent,
            'timestamp': datetime.now().isoformat(),
            'message_id': str(uuid.uuid4())[:8]
        }
        self.messages.append(message_data)
        self.last_activity = datetime.now()
        
        # Context compaction (Context Engineering)
        self._compact_context()
        
    def _compact_context(self):
        """Compact context when message limit is reached"""
        if len(self.messages) > settings.SESSION_CONFIG["max_messages"]:
            if settings.SESSION_CONFIG["compaction_strategy"] == "recent":
                # Keep most recent messages
                keep_count = settings.SESSION_CONFIG["max_messages"] // 2
                self.messages = self.messages[-keep_count:]
                logger.info(f"🔄 Context compacted: kept {keep_count} recent messages")
                
    def get_recent_context(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent conversation context for agents"""
        return self.messages[-limit:]
    
    def get_agent_state(self, agent_name: str) -> Dict[str, Any]:
        """Get or initialize agent state"""
        if agent_name not in self.agent_states:
            self.agent_states[agent_name] = {
                'interaction_count': 0,
                'last_interaction': None,
                'requirements_provided': False,
                'context_used': []
            }
        return self.agent_states[agent_name]
    
    def update_agent_state(self, agent_name: str, updates: Dict[str, Any]):
        """Update agent state with new information"""
        state = self.get_agent_state(agent_name)
        state.update(updates)
        state['last_interaction'] = datetime.now().isoformat()
        state['interaction_count'] += 1

class LocalStorage:
    """Enhanced storage with session management"""
    
    def __init__(self):
        current_dir = Path(__file__).parent.parent.parent
        self.projects_dir = current_dir / "projects"
        self.sessions = {}  # In-memory session cache (Session & Memory Concept)
        
        # Ensure projects directory exists
        self.projects_dir.mkdir(exist_ok=True)
        logger.info(f"📁 ADK Storage initialized: {self.projects_dir.absolute()}")
        
    def _get_session(self, project_id: str) -> ADKSession:
        """Get or create session for project"""
        if project_id not in self.sessions:
            self.sessions[project_id] = ADKSession(project_id)
            logger.debug(f"🆕 Session created for project: {project_id}")
        return self.sessions[project_id]
    
    def create_project(self, name: str) -> str:
        """Create a new project with session initialization"""
        project_id = str(uuid.uuid4())[:8]
        session = self._get_session(project_id)  # Initialize session
    
        project_data = {
            'id': project_id,
            'name': name,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'status': 'active',
            'requirements': {},
            'messages': [],
            'generated_files': [],
            'active_agent': 'requirements_evolver',
            'session_metadata': {
                'message_count': 0,
                'agent_interactions': {},
                'context_size': 0
            }
        }
    
        # Save project file
        project_file = self.projects_dir / f"project-{project_id}.json"
        try:
            logger.info(f"💾 Creating project: {name} ({project_id})")
            with open(project_file, 'w', encoding='utf-8') as f:
                json.dump(project_data, f, indent=2)
        except Exception as e:
            logger.error(f"❌ Failed to create project file: {str(e)}")
            raise Exception(f"Failed to create project file: {str(e)}")
    
        # Create project directory
        project_dir = self.projects_dir / f"project-{project_id}"
        try:
            project_dir.mkdir(parents=True, exist_ok=True)
            (project_dir / "src").mkdir(exist_ok=True)
            (project_dir / "preview").mkdir(exist_ok=True)
            logger.debug(f"📁 Project directories created: {project_id}")
        except Exception as e:
            logger.error(f"❌ Failed to create project directories: {str(e)}")
            raise Exception(f"Failed to create project directories: {str(e)}")
    
        logger.info(f"🎉 Project created: {name} ({project_id})")
        return project_id
    
    def get_project(self, project_id: str) -> Dict[str, Any]:
        """Get project data with session context"""
        project_file = self.projects_dir / f"project-{project_id}.json"
        
        if not project_file.exists():
            raise FileNotFoundError(f"Project {project_id} not found at {project_file}")
            
        try:
            with open(project_file, 'r', encoding='utf-8') as f:
                project_data = json.load(f)
                
            # Enhance with session data if available
            if project_id in self.sessions:
                session = self.sessions[project_id]
                project_data['session_metadata'] = {
                    'message_count': len(session.messages),
                    'agent_interactions': {k: v['interaction_count'] for k, v in session.agent_states.items()},
                    'context_size': len(str(session.messages))
                }
                
            return project_data
        except Exception as e:
            logger.error(f"❌ Failed to read project file: {str(e)}")
            raise Exception(f"Failed to read project file: {str(e)}")
    
    def update_project(self, project_id: str, updates: Dict[str, Any]):
        """Update project data with session awareness"""
        project_data = self.get_project(project_id)
        project_data.update(updates)
        project_data['updated_at'] = datetime.now().isoformat()
        
        project_file = self.projects_dir / f"project-{project_id}.json"
        try:
            with open(project_file, 'w', encoding='utf-8') as f:
                json.dump(project_data, f, indent=2)
            logger.debug(f"📝 Project updated: {project_id}")
        except Exception as e:
            logger.error(f"❌ Failed to update project file: {str(e)}")
            raise Exception(f"Failed to update project file: {str(e)}")
    
    def add_message(self, project_id: str, role: str, message: str, agent: str = None):
        """Add message with session management"""
        # Update session first
        session = self._get_session(project_id)
        session.add_message(role, message, agent)
        
        # Update agent state in session
        if agent:
            session.update_agent_state(agent, {'last_message': message[:100]})
        
        # Then update persistent storage
        project_data = self.get_project(project_id)
        
        message_data = {
            'role': role,
            'message': message,
            'timestamp': datetime.now().isoformat(),
            'agent': agent
        }
        
        project_data['messages'].append(message_data)
        project_data['updated_at'] = datetime.now().isoformat()
        
        project_file = self.projects_dir / f"project-{project_id}.json"
        try:
            with open(project_file, 'w', encoding='utf-8') as f:
                json.dump(project_data, f, indent=2)
            logger.debug(f"💬 Message stored: {project_id} ({role})")
        except Exception as e:
            logger.error(f"❌ Failed to save message: {str(e)}")
            raise Exception(f"Failed to save message: {str(e)}")
    
    def get_conversation_context(self, project_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get conversation context with session management"""
        session = self._get_session(project_id)
        return session.get_recent_context(limit)
    
    def update_requirements(self, project_id: str, agent_name: str, requirements: Dict[str, Any]):
        """Update requirements with session tracking"""
        project_data = self.get_project(project_id)
        
        if 'requirements' not in project_data:
            project_data['requirements'] = {}
            
        project_data['requirements'][agent_name] = requirements
        project_data['updated_at'] = datetime.now().isoformat()
        
        # Update session state
        session = self._get_session(project_id)
        session.update_agent_state(agent_name, {
            'requirements_provided': True,
            'last_requirements_update': datetime.now().isoformat()
        })
        
        project_file = self.projects_dir / f"project-{project_id}.json"
        try:
            with open(project_file, 'w', encoding='utf-8') as f:
                json.dump(project_data, f, indent=2)
            logger.info(f"📝 Requirements updated by {agent_name} for {project_id}")
        except Exception as e:
            logger.error(f"❌ Failed to update requirements: {str(e)}")
            raise Exception(f"Failed to update requirements: {str(e)}")
    
    def set_active_agent(self, project_id: str, agent_name: str):
        """Set active agent with session tracking"""
        self.update_project(project_id, {'active_agent': agent_name})
        
        # Update session
        session = self._get_session(project_id)
        session.update_agent_state(agent_name, {'activated_at': datetime.now().isoformat()})
        logger.debug(f"🔄 Active agent set: {agent_name} for {project_id}")
    
    def add_generated_file(self, project_id: str, file_path: str, content: str):
        """Track generated files"""
        project_data = self.get_project(project_id)
        
        file_data = {
            'path': file_path,
            'content': content[:500] + "..." if len(content) > 500 else content,
            'generated_at': datetime.now().isoformat(),
            'size': len(content)
        }
        
        project_data['generated_files'].append(file_data)
        project_data['updated_at'] = datetime.now().isoformat()
        
        project_file = self.projects_dir / f"project-{project_id}.json"
        try:
            with open(project_file, 'w', encoding='utf-8') as f:
                json.dump(project_data, f, indent=2)
            logger.info(f"📄 File tracked: {file_path} for {project_id}")
        except Exception as e:
            logger.error(f"❌ Failed to track generated file: {str(e)}")
            raise Exception(f"Failed to track generated file: {str(e)}")
    
    def get_conversation_history(self, project_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get conversation history with session context"""
        session = self._get_session(project_id)
        return session.get_recent_context(limit)
    
    def list_projects(self) -> List[Dict[str, Any]]:
        """List all projects with session metadata"""
        projects = []
        try:
            for project_file in self.projects_dir.glob("project-*.json"):
                try:
                    with open(project_file, 'r', encoding='utf-8') as f:
                        project_data = json.load(f)
                        
                    # Add session metadata if available
                    project_id = project_data['id']
                    if project_id in self.sessions:
                        session = self.sessions[project_id]
                        project_data['session_metadata'] = {
                            'active_session': True,
                            'message_count': len(session.messages),
                            'last_activity': session.last_activity.isoformat()
                        }
                    
                    projects.append({
                        'id': project_data['id'],
                        'name': project_data['name'],
                        'created_at': project_data['created_at'],
                        'status': project_data['status'],
                        'message_count': len(project_data['messages']),
                        'session_metadata': project_data.get('session_metadata', {})
                    })
                except Exception as e:
                    logger.warning(f"⚠️ Skipping corrupt project file {project_file}: {e}")
                    continue
        
        except Exception as e:
            logger.error(f"❌ Error listing projects: {e}")
        
        return sorted(projects, key=lambda x: x['created_at'], reverse=True)
    
    def cleanup_project(self, project_id: str):
        """Clean up a project and its session"""
        project_file = self.projects_dir / f"project-{project_id}.json"
        project_dir = self.projects_dir / f"project-{project_id}"
        
        try:
            if project_file.exists():
                project_file.unlink()
            if project_dir.exists():
                import shutil
                shutil.rmtree(project_dir)
            if project_id in self.sessions:
                del self.sessions[project_id]
            logger.info(f"🧹 Cleaned up project and session: {project_id}")
        except Exception as e:
            logger.error(f"⚠️ Failed to cleanup project {project_id}: {e}")
    
    def get_session_stats(self, project_id: str) -> Dict[str, Any]:
        """Get session statistics for observability"""
        if project_id not in self.sessions:
            return {"active_session": False}
            
        session = self.sessions[project_id]
        return {
            "active_session": True,
            "message_count": len(session.messages),
            "agent_count": len(session.agent_states),
            "last_activity": session.last_activity.isoformat(),
            "agent_interactions": {k: v['interaction_count'] for k, v in session.agent_states.items()}
        }