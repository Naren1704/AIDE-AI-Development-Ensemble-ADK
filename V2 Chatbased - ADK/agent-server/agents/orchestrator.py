"""
ADK Orchestrator - Fixed with proper agent switching and session management
"""

import asyncio
from typing import Dict, Any
import sys
from pathlib import Path

# Add the root directory to Python path
root_dir = Path(__file__).parent.parent.parent
sys.path.append(str(root_dir))

from config import settings
from storage.local_storage import LocalStorage
from .core.adk_components import ADKManager  # ✅ FIXED: Correct import path

class ADKOrchestrator:
    def __init__(self):
        self.storage = LocalStorage()
        self.adk_manager = ADKManager()
        self.agent_chain = settings.AGENT_CHAIN
        self.agent_progress = {}  # Track agent contributions
        # ✅ FIXED: Agents are already registered in ADKManager, no need to re-register
    
    async def start_conversation(self, project_id: str) -> str:
        """Enhanced welcome with ADK session setup"""
        welcome_message = """🤖 Welcome to AIDE ADK! I'm your AI Development Ensemble powered by Google Gemini.

I'll help you build a complete web application by gathering requirements across different domains:

• **Requirements Evolution** - Understanding your goals
• **UX Architecture** - User experience and navigation  
• **UI Design** - Visual design and styling
• **Frontend Engineering** - Technical implementation
• **Data Architecture** - Database and storage
• **API Design** - Backend functionality
• **DevOps** - Deployment and hosting

Let's start with the basics: What kind of application would you like to build?"""
        
        self.storage.set_active_agent(project_id, 'requirements_evolver')
        self.agent_progress[project_id] = set()  # Initialize progress tracking            
        return welcome_message
    
    async def route_message(self, project_id: str, user_message: str) -> Dict[str, Any]:
        """Route message through sequential ADK agents with proper switching"""
        project_data = self.storage.get_project(project_id)
        current_agent = project_data.get('active_agent', 'requirements_evolver')
        
        # Determine next agent based on user message and context
        next_agent = self._determine_next_agent(current_agent, user_message, project_data)
        
        # Update active agent if changed
        if next_agent != current_agent:
            self.storage.set_active_agent(project_id, next_agent)
            current_agent = next_agent
            print(f"🔄 ADK: Switched to agent: {current_agent}")
        
        # Run only the current agent (not all sequentially)
        agent_response = await self._run_single_agent(project_id, current_agent, user_message, project_data)
        
        # Extract and store requirements
        requirements_updated = self._extract_requirements_enhanced(
            project_id, current_agent, agent_response, user_message
        )
        
        # Track agent progress
        if project_id in self.agent_progress and requirements_updated:
            self.agent_progress[project_id].add(current_agent)
        
        return {
            'message': agent_response,
            'agent': current_agent,
            'should_generate': False
        }
    
    async def _run_single_agent(self, project_id: str, agent_name: str, user_message: str, project_data: Dict[str, Any]) -> str:
        """Run a single agent with session context"""
        try:
            # Build context for the agent
            context = self._build_agent_context(project_data, agent_name)
            
            # Get agent-specific instructions
            instructions = self._get_agent_instructions(agent_name)
            full_prompt = f"{instructions}\n\n{context}\n\nUser: {user_message}"
            
            # ✅ FIXED: Use run_agent_with_instructions method
            result = await self.adk_manager.run_agent_with_instructions(
                session_id=project_id,
                agent_name=agent_name,
                instructions=instructions,
                user_input=full_prompt
            )
            
            if result.get('success', False):
                return result['response']
            else:
                error_msg = result.get('response', 'Unknown error occurred')
                print(f"❌ ADK Agent {agent_name} execution failed: {error_msg}")
                return f"I encountered an issue while processing your request. Please try again. Error: {error_msg}"
            
        except Exception as e:
            print(f"❌ ADK Agent {agent_name} error: {e}")
            return f"I encountered an issue. Please try again. Error: {str(e)}"
    
    def _get_agent_instructions(self, agent_name: str) -> str:
        """Get agent-specific instructions"""
        instructions_map = {
            'requirements_evolver': """You are a Requirements Evolver Agent. Your goal is to understand what the user wants to build.
            - Ask clarifying questions to understand their goals
            - Identify key features and functionality needed
            - Understand target users and their needs
            - Note any technical constraints or preferences
            - Be conversational and focused
            - When you have enough information, summarize requirements clearly""",
            
            'ux_architect': """You are a UX Architect Agent. Your role is to design the user experience.
            - User navigation and flow
            - Page structure and layout
            - Information architecture  
            - Mobile vs desktop experience
            - User interaction patterns
            - Ask specific questions about user experience
            - Suggest optimal navigation structures""",
            
            'ui_designer': """You are a UI Designer Agent. Your role is to define the visual design.
            CRITICAL RULES - STRICTLY ENFORCED:
            🚫 ABSOLUTELY NO CODE GENERATION
            🚫 NEVER write HTML, CSS, JavaScript, or any programming code
            - Color schemes and themes
            - Typography and fonts  
            - Layout and spacing
            - Visual style and aesthetics
            - Ask about design preferences (colors, styles, themes)
            - When user says "approved", "perfect", "looks good", etc., provide final specs""",
            
            'frontend_engineer': """You are a Frontend Engineer Agent. Your role is technical implementation.
            CRITICAL RULES - STRICTLY ENFORCED:
            🚫 ABSOLUTELY NO CODE GENERATION
            - JavaScript frameworks or vanilla JS
            - Interactive features and functionality
            - Performance considerations
            - Browser compatibility
            - Ask technical questions about implementation""",
            
            'data_architect': """You are a Data Architect Agent. Your role is data design.
            - Data storage requirements
            - Database design (SQL vs NoSQL)
            - Data relationships and schema
            - Security and privacy considerations""",
            
            'api_designer': """You are an API Designer Agent. Your role is backend design.
            - API endpoints and routes
            - Authentication and authorization
            - Data formats (JSON, etc.)
            - Backend functionality""",
            
            'devops': """You are a DevOps Agent. Your role is deployment planning.
            - Deployment platforms and hosting
            - Domain and SSL configuration
            - Environment setup
            - Scalability and performance""",
            
            'code_generator': """You are a Code Generation Agent. Your role is to generate clean, working code for web applications.
            
            CRITICAL RULES:
            - Generate complete, executable code
            - Follow specified architecture and constraints
            - For Flask: Use proper route decorators and render_template()
            - For JavaScript: Use vanilla JS only, no frameworks
            - For CSS: Create responsive, modern styling
            - For HTML: Use semantic HTML5 with proper structure
            
            OUTPUT FORMAT:
            Generate complete code files ready for execution."""
        }
        
        return instructions_map.get(agent_name, "You are a helpful AI assistant.")
    
    def _determine_next_agent(self, current_agent: str, user_message: str, project_data: Dict[str, Any]) -> str:
        """Enhanced agent switching with explicit approval detection"""
        message_lower = user_message.lower()
        requirements = project_data.get('requirements', {})
        
        # 🚨 CRITICAL FIX: Check for explicit approval to force agent switch
        approval_keywords = [
            'approved', 'perfect', 'looks good', 'proceed', 'move forward', 
            'next phase', 'next agent', 'switch to', 'yes', 'sure', 'go ahead',
            'continue', 'next', 'ready', 'sounds good'
        ]
        if any(keyword in message_lower for keyword in approval_keywords):
            print(f"🎯 ADK: Explicit approval detected in: '{user_message}'")
            
            # Define approval-based progression
            approval_progression = {
                'requirements_evolver': 'ux_architect',
                'ux_architect': 'ui_designer', 
                'ui_designer': 'frontend_engineer',
                'frontend_engineer': 'data_architect',
                'data_architect': 'api_designer',
                'api_designer': 'devops'
            }
            
            if current_agent in approval_progression:
                next_agent = approval_progression[current_agent]
                print(f"🎯 ADK: Approval progression: {current_agent} -> {next_agent}")
                return next_agent
        
        # Check for explicit agent mentions with priority
        agent_keywords = {
            'requirements_evolver': ['requirements', 'what i want', 'project goal', 'objective'],
            'ux_architect': ['navigate', 'user flow', 'ux', 'experience', 'usability', 'interface', 'flow', 'navigation', 'user journey'],
            'ui_designer': ['change design', 'change color', 'ui design', 'ui', 'design', 'color', 'style', 'theme', 'look', 'appearance'],
            'data_architect': ['database', 'data', 'store', 'save', 'storage', 'persist', 'db', 'sql', 'information'],
            'api_designer': ['api', 'backend', 'server', 'endpoint', 'rest', 'json', 'backend', 'server-side'],
            'frontend_engineer': ['javascript', 'react', 'vue', 'frontend', 'client', 'browser', 'technical', 'implementation', 'code', 'functionality'],
            'devops': ['deploy', 'host', 'server', 'domain', 'production', 'cloud', 'hosting', 'deployment', 'server']
        }
        
        for agent_name, keywords in agent_keywords.items():
            if any(keyword in message_lower for keyword in keywords):
                print(f"🎯 ADK: Keyword match '{keywords}' switching to {agent_name}")
                return agent_name
        
        # Progress-based switching: Move to next agent in chain if current has contributed
        if current_agent in self.agent_chain:
            current_index = self.agent_chain.index(current_agent)
            
            # Check if current agent has made substantial contribution
            current_has_contributed = (
                current_agent in requirements and 
                requirements[current_agent].get('has_substance', False)
            )
            
            # Also switch if we have multiple messages with this agent
            message_count = len([msg for msg in project_data.get('messages', []) 
                           if msg.get('agent') == current_agent])
            
            if (current_has_contributed or message_count >= 2) and current_index < len(self.agent_chain) - 1:
                next_agent = self.agent_chain[current_index + 1]
                print(f"📈 ADK: Progress-based switch: {current_agent} -> {next_agent} (contributions: {current_has_contributed}, messages: {message_count})")
                return next_agent
        
        # Stay with current agent if no better option
        return current_agent
    
    def _build_agent_context(self, project_data: Dict[str, Any], agent_name: str) -> str:
        """Build comprehensive context for agents"""
        requirements = project_data.get('requirements', {})
        recent_messages = project_data.get('messages', [])[-3:]  # Last 3 messages
        
        context = f"## PROJECT OVERVIEW\n"
        context += f"Project: {project_data['name']}\n"
        context += f"Current Agent: {agent_name.replace('_', ' ').title()}\n\n"
        
        # Include relevant requirements from other agents
        if requirements:
            context += "## EXISTING REQUIREMENTS\n"
            substantial_requirements = 0
            
            for other_agent, req_data in requirements.items():
                if other_agent != agent_name and req_data.get('has_substance', False):
                    summary = self._create_agent_summary(req_data['full_response'])
                    context += f"- {other_agent.replace('_', ' ').title()}: {summary}\n"
                    substantial_requirements += 1
            
            if substantial_requirements == 0:
                context += "No substantial requirements gathered yet.\n"
            context += "\n"
        
        # Include recent conversation
        if recent_messages:
            context += "## RECENT CONVERSATION\n"
            for msg in recent_messages:
                role = "User" if msg['role'] == 'user' else "Assistant"
                context += f"{role}: {msg['message'][:150]}\n"
            context += "\n"
        
        # ✅ FIXED: Added missing _get_agent_guidance method
        context += "## YOUR ROLE\n"
        context += self._get_agent_guidance(agent_name)
        
        return context
    
    def _get_agent_guidance(self, agent_name: str) -> str:
        """Get specific guidance for each agent type"""
        guidance = {
            'requirements_evolver': """Focus on understanding the user's goals and requirements. Ask clarifying questions about features, target audience, and constraints.""",
            'ux_architect': """Design the user experience flow. Focus on navigation, user journeys, and information architecture. Ask about user interactions and flow.""",
            'ui_designer': """Focus on visual design aspects like colors, layout, typography. Ask about design preferences, themes, and visual style. DO NOT generate code.""",
            'frontend_engineer': """Discuss technical implementation details. Focus on functionality, interactions, and technical constraints. DO NOT generate code.""",
            'data_architect': """Design data storage and management. Ask about data types, relationships, and storage requirements.""",
            'api_designer': """Design backend API structure. Focus on endpoints, data formats, and server functionality.""",
            'devops': """Plan deployment and hosting. Ask about deployment platforms, domains, and infrastructure needs.""",
            'code_generator': """Generate complete, working code based on the requirements gathered. Focus on creating executable, well-structured code files."""
        }
        return guidance.get(agent_name, "Provide helpful assistance based on your role.")
    
    def _create_agent_summary(self, response: str) -> str:
        """Create intelligent summary of agent responses"""
        if len(response) <= 100:
            return response
        
        # Try to extract the main point
        lines = response.split('.')
        if lines and len(lines[0]) > 20:
            return lines[0] + "..."
        
        return response[:97] + "..."
    
    def _extract_requirements_enhanced(self, project_id: str, agent_name: str, response: str, user_message: str) -> bool:
        """Enhanced requirement extraction with substance detection"""
        has_substance = self._has_substantial_content(response, agent_name)
        
        requirements = {
            'full_response': response,
            'user_message': user_message,
            'summary': self._create_intelligent_summary(response),
            'technical_specs': self._extract_technical_specs(response, agent_name),
            'timestamp': asyncio.get_event_loop().time(),
            'agent': agent_name,
            'has_substance': has_substance
        }
        
        self.storage.update_requirements(project_id, agent_name, requirements)
        print(f"📝 ADK: Stored requirements from {agent_name} (substance: {has_substance})")
        return has_substance
        
    def _create_intelligent_summary(self, response: str) -> str:
        """Create better summaries that capture the essence"""
        if len(response) <= 200:
            return response
        
        # Extract the first meaningful paragraph
        lines = response.split('\n')
        meaningful_lines = []
        
        for line in lines:
            stripped = line.strip()
            if (stripped and 
                not stripped.startswith(('#', '//', '/*')) and
                len(stripped) > 10):
                meaningful_lines.append(stripped)
                if len('\n'.join(meaningful_lines)) > 150:
                    break
        
        summary = '\n'.join(meaningful_lines)
        if len(summary) > 200:
            summary = summary[:197] + "..."
            
        return summary
    
    def _extract_technical_specs(self, response: str, agent_name: str) -> Dict[str, Any]:
        """Extract technical specifications from response"""
        specs = {}
        response_lower = response.lower()
        
        # Common specifications
        if 'responsive' in response_lower or 'mobile' in response_lower:
            specs['responsive'] = True
        if 'modern' in response_lower:
            specs['style'] = 'modern'
        if 'minimal' in response_lower or 'clean' in response_lower:
            specs['style'] = 'minimal'
        if 'dark' in response_lower and 'theme' in response_lower:
            specs['theme'] = 'dark'
        if 'light' in response_lower and 'theme' in response_lower:
            specs['theme'] = 'light'
        
        # Agent-specific specifications
        if agent_name == 'ui_designer':
            import re
            color_pattern = r'#([a-fA-F0-9]{6}|[a-fA-F0-9]{3})'
            colors = re.findall(color_pattern, response)
            if colors:
                specs['colors'] = [f"#{color}" for color in colors[:3]]
            
        return specs
    
    def _has_substantial_content(self, response: str, agent_name: str) -> bool:
        """Substance detection for agent responses"""
        if not response or len(response.strip()) < 25:
            return False

        response_clean = response.strip()

        # Early agents: Accept most meaningful responses
        if agent_name in ['requirements_evolver', 'ux_architect', 'ui_designer']:
            is_pure_question = (
                response_clean.endswith('?') and 
                len(response_clean) < 80 and
                any(phrase in response_clean.lower() for phrase in ['what would', 'can you', 'please provide', 'could you tell me'])
            )
            
            return len(response_clean) >= 30 and not is_pure_question

        # Technical agents: Need some technical content
        else:
            technical_indicators = {
                'frontend_engineer': ['javascript', 'framework', 'component', 'interaction', 'functionality', 'implementation'],
                'data_architect': ['database', 'storage', 'data', 'schema', 'table', 'model'],
                'api_designer': ['endpoint', 'api', 'rest', 'backend', 'route', 'request', 'response'],
                'devops': ['deployment', 'hosting', 'server', 'cloud', 'domain', 'ssl', 'environment'],
                'code_generator': ['import', 'def ', 'class ', 'function', 'const ', 'let ', 'app.route']
            }
            
            agent_indicators = technical_indicators.get(agent_name, [])
            has_technical_content = any(indicator in response_clean.lower() for indicator in agent_indicators)
            
            return len(response_clean) >= 40 and has_technical_content
    
    async def can_generate_code(self, project_id: str) -> Dict[str, Any]:
        """Check if we have enough requirements to generate code"""
        project_data = self.storage.get_project(project_id)
        requirements = project_data.get('requirements', {})
        
        # Count substantial contributions
        substantial_agents = 0
        agent_contributions = []
        
        for agent_name, req_data in requirements.items():
            if req_data and req_data.get('has_substance', False):
                substantial_agents += 1
                agent_contributions.append(agent_name)
        
        # Define minimum requirements for code generation
        has_minimal_requirements = self._has_minimal_requirements(project_data)
        
        status = {
            'can_generate': has_minimal_requirements,
            'substantial_agents': substantial_agents,
            'agent_contributions': agent_contributions,
            'has_minimal_requirements': has_minimal_requirements,
            'message': self._get_generation_status_message(has_minimal_requirements, substantial_agents)
        }
        
        print(f"🔍 ADK Code generation check: {status}")
        return status
    
    def _has_minimal_requirements(self, project_data: Dict[str, Any]) -> bool:
        """Check if we have basic requirements to generate meaningful code"""
        requirements = project_data.get('requirements', {})
        
        substantial_agents = sum(
            1 for agent_data in requirements.values() 
            if agent_data and agent_data.get('has_substance', False)
        )
        
        has_requirements_evolver = (
            'requirements_evolver' in requirements and 
            requirements['requirements_evolver'].get('has_substance', False)
        )
        
        # Require at least 3 substantial contributions OR
        # requirements + 2 other agents OR 4+ agents total
        return (
            substantial_agents >= 3 or
            (has_requirements_evolver and substantial_agents >= 2) or
            substantial_agents >= 4
        )
    
    def _get_generation_status_message(self, can_generate: bool, substantial_agents: int) -> str:
        """Get user-friendly message about generation readiness"""
        if can_generate:
            return f"Ready to generate! Collected substantial requirements from {substantial_agents} agents."
        elif substantial_agents == 0:
            return "Please describe your project requirements first."
        elif substantial_agents == 1:
            return "Getting there! A bit more detail about design or functionality would help."
        elif substantial_agents == 2:
            return "Making progress! A few more details about your preferences would be great."
        else:
            return f"Almost ready! We have {substantial_agents} agents with good requirements."