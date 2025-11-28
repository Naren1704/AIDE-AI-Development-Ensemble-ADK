"""
ADK Integration Agent - Complete Google ADK integration for code generation
"""

import asyncio
from typing import Dict, List, Any
from pathlib import Path
import re
from config import settings
from .core.adk_components import ADKManager  # ✅ FIXED: Correct import path

class ADKIntegrationAgent:
    def __init__(self):
        self.adk_manager = ADKManager()
        # ✅ FIXED: Use existing code_generator agent instead of re-registering
        # The code_generator agent is now included in default agents
        
    async def plan_project_structure(self, project_data: Dict[str, Any]) -> List[str]:
        """Generate optimal project structure with Google ADK"""
        requirements = project_data.get('requirements', {})
        project_name = project_data['name']
        
        structure_prompt = f"""Generate a complete Flask project structure for: {project_name}

Requirements Summary:
{self._build_requirements_summary(requirements)}

Output a list of file paths needed for a complete web application:"""

        try:
            # ✅ FIXED: Use the existing code_generator agent
            session_id = f"structure_{project_data['id']}"
            results = await self.adk_manager.run_sequential_agents(
                session_id=session_id,
                user_input=structure_prompt,
                agent_chain=['code_generator']  # ✅ Now this agent exists
            )
            
            if results and len(results) > 0:
                response = results[0]['response']
                file_list = self._extract_file_list_deduplicated(response)
                return file_list
            else:
                # Fallback to essential structure
                return self._get_essential_structure()
            
        except Exception as e:
            print(f"❌ Structure planning failed: {e}")
            # Fallback to essential structure
            return self._get_essential_structure()
    
    def _get_essential_structure(self) -> List[str]:
        """Get essential project structure as fallback"""
        return [
            "app.py", 
            "requirements.txt", 
            "templates/index.html", 
            "static/css/style.css", 
            "static/js/app.js", 
            "README.md"
        ]
    
    async def generate_file_content_with_context(self, project_data: Dict[str, Any], file_path: str, existing_files: List[Dict[str, Any]]) -> str:
        """Generate file content with Google ADK and context awareness"""
        requirements = project_data.get('requirements', {})
        project_name = project_data['name']
        
        prompt = self._build_adk_prompt(project_name, file_path, requirements, existing_files)
        
        try:
            session_id = f"generation_{project_data['id']}_{file_path.replace('/', '_')}"
            # ✅ FIXED: Use run_single_agent for better error handling
            result = await self.adk_manager.run_single_agent(
                session_id=session_id,
                agent_name='code_generator',
                user_input=prompt
            )
            
            if result.get('success', False):
                response = result['response']
                clean_code = self._extract_pure_code(response)
                
                # Validate generated content
                if not self._is_valid_file_content_trusted(clean_code, file_path):
                    print(f"⚠️  Content validation warning for {file_path}")
                    # Still return the code but log the warning
                
                return clean_code
            else:
                raise Exception(f"Agent execution failed: {result.get('response', 'Unknown error')}")
            
        except Exception as e:
            print(f"❌ File generation failed for {file_path}: {e}")
            return f"# Error generating {file_path}. Please try again.\n# {str(e)}"
    
    def _build_adk_prompt(self, project_name: str, file_path: str, requirements: Dict[str, Any], existing_files: List[Dict[str, Any]]) -> str:
        """Build prompt for ADK code generation"""
        
        file_context = self._build_file_context(existing_files)
        requirements_context = self._build_requirements_context(requirements)
        
        prompt = f"""GENERATE {file_path} for {project_name}

PROJECT CONTEXT:
{requirements_context}

EXISTING FILES:
{file_context}

TECHNICAL CONSTRAINTS:
{self._get_technical_constraints(file_path)}

FILE REQUIREMENTS:
{self._get_file_requirements(file_path)}

OUTPUT:
Pure code only - no additional text, no markdown code blocks:"""
        
        return prompt

    def _build_file_context(self, existing_files: List[Dict[str, Any]]) -> str:
        """Build context about existing files"""
        if not existing_files:
            return "No other files generated yet."
        
        context = "Files already created:\n"
        for file_data in existing_files:
            preview = file_data['content_preview'][:100] + "..." if len(file_data['content_preview']) > 100 else file_data['content_preview']
            context += f"- {file_data['path']}: {preview}\n"
        
        return context

    def _build_requirements_context(self, requirements: Dict[str, Any]) -> str:
        """Build requirements context"""
        if not requirements:
            return "Create a functional web application."
            
        context = "Project Requirements:\n"
        for agent_name, req_data in requirements.items():
            if req_data and req_data.get('full_response'):
                summary = req_data['full_response'][:150] + "..." if len(req_data['full_response']) > 150 else req_data['full_response']
                context += f"- {agent_name}: {summary}\n"
        
        return context

    def _get_technical_constraints(self, file_path: str) -> str:
        """Get technical constraints for file generation"""
        constraints = {
            'app.py': [
                "USE Flask framework with proper route decorators",
                "INCLUDE necessary imports (Flask, render_template, request, jsonify)",
                "IMPLEMENT input validation and error handling",
                "USE render_template() for HTML responses, NOT render_template_string()",
                "INCLUDE app.run(debug=True) in __main__ block"
            ],
            'templates/index.html': [
                "USE proper HTML5 structure with semantic elements",
                "INCLUDE Jinja2 templating syntax where appropriate",
                "USE url_for() for static file references",
                "IMPLEMENT responsive design foundation"
            ],
            'static/css/style.css': [
                "CREATE responsive, mobile-first CSS",
                "USE modern CSS features (Flexbox/Grid)",
                "DEFINE clear color scheme and typography",
                "ENSURE good contrast and accessibility"
            ],
            'static/js/app.js': [
                "USE vanilla JavaScript ONLY - no frameworks",
                "IMPLEMENT proper error handling for API calls",
                "USE modern ES6+ features",
                "HANDLE form submissions and user interactions"
            ],
            'requirements.txt': [
                "LIST Python dependencies with version pinning",
                "INCLUDE Flask and necessary packages"
            ]
        }
        
        file_constraints = constraints.get(file_path, [])
        if not file_constraints:
            # Default constraints for unknown file types
            if file_path.endswith('.py'):
                file_constraints = ["Write clean, well-documented Python code"]
            elif file_path.endswith('.html'):
                file_constraints = ["Use proper HTML5 semantic structure"]
            elif file_path.endswith('.css'):
                file_constraints = ["Create modern, responsive CSS"]
            elif file_path.endswith('.js'):
                file_constraints = ["Use vanilla JavaScript with modern ES6+ features"]
        
        return "\n".join([f"- {constraint}" for constraint in file_constraints])

    def _get_file_requirements(self, file_path: str) -> str:
        """Get file-specific requirements"""
        requirements = {
            'app.py': "Create complete Flask application with routes, error handling, and template rendering",
            'templates/index.html': "Create complete HTML page with proper structure, forms, and responsive design",
            'static/css/style.css': "Create comprehensive CSS stylesheet with responsive design and modern features",
            'static/js/app.js': "Create complete JavaScript functionality with API communication and user interactions",
            'requirements.txt': "List Python dependencies for Flask project with proper versioning"
        }
        
        default_requirements = {
            '.py': "Create appropriate Python module",
            '.html': "Create appropriate HTML file",
            '.css': "Create appropriate CSS stylesheet", 
            '.js': "Create appropriate JavaScript file",
            '.json': "Create appropriate JSON configuration",
            '.md': "Create appropriate documentation",
            '.txt': "Create appropriate text file"
        }
        
        if file_path in requirements:
            return requirements[file_path]
        
        # Find matching extension
        for ext, desc in default_requirements.items():
            if file_path.endswith(ext):
                return desc
        
        return "Create appropriate content for this file type"

    def _extract_pure_code(self, raw_response: str) -> str:
        """Extract only pure code from response"""
        if not raw_response:
            return ""
        
        # Remove markdown code blocks
        clean = re.sub(r'```[a-z]*\n?', '', raw_response, flags=re.IGNORECASE)
        clean = re.sub(r'```', '', clean)
        
        # Remove obvious explanation lines
        lines = clean.split('\n')
        code_lines = []
        found_code_start = False
        
        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue
            
            # Skip lines that are clearly explanations
            if not found_code_start:
                explanation_patterns = [
                    'here is', 'here\'s', 'this is', 'the following', 
                    'sure,', 'certainly,', 'i\'ll create', 'i will generate',
                    'below is', 'generated code:', 'code:'
                ]
                if (any(pattern in stripped.lower() for pattern in explanation_patterns) and
                    '{' not in stripped and '<' not in stripped and 'import' not in stripped and 'def ' not in stripped):
                    continue
                else:
                    found_code_start = True
            
            code_lines.append(line)
        
        result = '\n'.join(code_lines).strip()
        return result if result and len(result) > 10 else raw_response.strip()

    def _is_valid_file_content_trusted(self, content: str, file_path: str) -> bool:
        """Trust-based validation for generated content"""
        if not content or len(content.strip()) < 15:
            return False
        
        if file_path.endswith('.py'):
            return any(keyword in content for keyword in ['import', 'def ', 'class ', '@app.route']) or len(content.strip()) > 50
        elif file_path.endswith('.html'):
            return '<!DOCTYPE' in content or '<html' in content or ('<' in content and '>' in content)
        elif file_path.endswith('.css'):
            return '{' in content and '}' in content and any(char in content for char in [':', ';'])
        elif file_path.endswith('.js'):
            return any(keyword in content for keyword in ['function', 'const ', 'let ', 'document.']) and 'import' not in content
        elif file_path.endswith('.txt') or file_path.endswith('.md'):
            return len(content.strip()) > 5
        
        return True

    def _build_requirements_summary(self, requirements: Dict[str, Any]) -> str:
        """Build requirements summary for planning"""
        summary_parts = []
        for agent_name, agent_req in requirements.items():
            if agent_req and agent_req.get('full_response'):
                response = agent_req['full_response']
                summary = response.split('.')[0] if '.' in response else response[:200]
                if len(summary.strip()) > 20:
                    summary_parts.append(f"{agent_name}: {summary}")
        return "\n".join(summary_parts) if summary_parts else "Create a functional web application."

    def _extract_file_list_deduplicated(self, response: str) -> List[str]:
        """Extract and deduplicate file list"""
        lines = response.strip().split('\n')
        file_list = []
        
        valid_extensions = ['.py', '.html', '.css', '.js', '.json', '.md', '.txt', '.yml', '.yaml', '.env']
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Skip code patterns and comments
            code_patterns = ['from ', 'import ', '@app', 'def ', 'class ', '<!DOCTYPE', '// ', '/*', '*/']
            if any(pattern in line for pattern in code_patterns):
                continue
            
            if any(char in line for char in ['(', ')', '{', '}', '[', ']', '==', '=']):
                continue
            
            if line.startswith('#') or '://' in line or line.startswith('//'):
                continue
            
            clean_path = line.split('#')[0].split('[')[0].strip()
            
            if clean_path and (any(ext in clean_path for ext in valid_extensions) or 
                      ('/' in clean_path and '.' in clean_path.split('/')[-1])):
                if (len(clean_path) < 100 and 
                not any(bad_char in clean_path for bad_char in ['*', '?', '"', '<', '>', '|']) and
                not clean_path.endswith('/')):
                    
                    normalized_path = self._normalize_file_path(clean_path)
                    if normalized_path not in file_list:
                        file_list.append(normalized_path)
        
        # Remove duplicates and ensure essentials
        file_list = self._resolve_file_conflicts(file_list)
        
        # Add essential files if missing
        essential_files = self._get_essential_structure()
        for essential in essential_files:
            if essential not in file_list:
                file_list.append(essential)
        
        print(f"📁 Final file structure: {file_list}")
        return file_list

    def _normalize_file_path(self, file_path: str) -> str:
        """Normalize file paths to standard structure"""
        path_mapping = {
            'style.css': 'static/css/style.css',
            'app.js': 'static/js/app.js', 
            'index.html': 'templates/index.html',
            'scripts.js': 'static/js/app.js',
            'styles.css': 'static/css/style.css',
            'main.py': 'app.py',
            'server.py': 'app.py'
        }
        return path_mapping.get(file_path, file_path)

    def _resolve_file_conflicts(self, file_list: List[str]) -> List[str]:
        """Resolve conflicts between duplicate files"""
        conflict_groups = {
            'index.html': ['index.html', 'templates/index.html', 'templates/home.html'],
            'style.css': ['style.css', 'static/css/style.css', 'styles.css', 'static/css/styles.css'],
            'app.js': ['app.js', 'static/js/app.js', 'scripts.js', 'static/js/scripts.js', 'main.js']
        }
        
        resolved_files = []
        used_groups = set()
        
        for file_path in file_list:
            matched = False
            for group_name, conflict_group in conflict_groups.items():
                if file_path in conflict_group:
                    if group_name not in used_groups:
                        # Use the preferred path for this group
                        preferred = [f for f in conflict_group if f.startswith(('templates/', 'static/'))]
                        if preferred:
                            resolved_files.append(preferred[0])
                        else:
                            resolved_files.append(conflict_group[0])
                        used_groups.add(group_name)
                    matched = True
                    break
            
            if not matched and file_path not in resolved_files:
                resolved_files.append(file_path)
        
        return resolved_files