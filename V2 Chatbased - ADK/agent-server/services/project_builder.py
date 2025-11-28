"""
ADK Project Builder - Generates projects with Gemini integration
"""

import os
import shutil
import asyncio
from pathlib import Path
from typing import Dict, List, Any
import http.server
import socketserver
import threading
import time
import requests
import re
from config import settings
from agents.integration_agent import ADKIntegrationAgent  # ✅ FIXED: Correct import path

class ADKProjectBuilder:
    def __init__(self):
        current_dir = Path(__file__).parent.parent.parent
        self.projects_dir = current_dir / "projects"
        self.preview_ports = {}
        self.integration_agent = ADKIntegrationAgent()
        
        # Ensure projects directory exists
        self.projects_dir.mkdir(exist_ok=True)
    
    async def generate_project(self, project_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate project with ADK integration"""
        project_id = project_data['id']
        project_dir = self.projects_dir / f"project-{project_id}" / "src"
    
        print(f"🚀 Starting ADK project generation for {project_id}")
        print(f"📋 Project requirements: {project_data.get('requirements', {}).keys()}")
    
        # Clean regeneration
        await self._clean_project_directory(project_dir)
        project_dir.mkdir(parents=True, exist_ok=True)
    
        generated_files = []
    
        # Phase 1: Plan structure with ADK
        print("🔧 Phase 1: Planning project structure with ADK...")
        file_structure = await self.integration_agent.plan_project_structure(project_data)
        print(f"📁 Planned {len(file_structure)} files: {file_structure}")
    
        # Phase 2: Generate files with ADK
        print("🔧 Phase 2: Generating file contents with ADK...")
        successful_files = 0
    
        for i, file_path in enumerate(file_structure):
            print(f"   Generating: {file_path}")
            try:
                # Pass existing files as context
                existing_files_context = [
                    {'path': f['path'], 'content_preview': f['content'][:500]} 
                    for f in generated_files
                ]
                
                content = await self.integration_agent.generate_file_content_with_context(
                    project_data, file_path, existing_files_context
                )
            
                # ADK validation - more trusting
                if not self._is_valid_generated_content_trusted(content, file_path):
                    print(f"   ⚠️  Content validation warning for {file_path}, trusting ADK output")
            
                # Write file
                full_path = project_dir / file_path
                full_path.parent.mkdir(parents=True, exist_ok=True)
            
                with open(full_path, 'w', encoding='utf-8') as f:
                    f.write(content)
            
                # Create file metadata
                file_data = {
                    'path': file_path,
                    'content': content,
                    'size': len(content),
                    'type': self._get_file_type(file_path),
                    'icon': self._get_file_icon(file_path),
                    'language': self._get_file_language(file_path)
                }
                generated_files.append(file_data)
                successful_files += 1
                print(f"   ✅ Generated: {file_path} ({len(content)} bytes)")
            
            except Exception as e:
                print(f"   ❌ Failed to generate {file_path}: {e}")
                # Create a placeholder file to avoid complete failure
                placeholder_content = self._create_placeholder_content(file_path, str(e))
                full_path = project_dir / file_path
                full_path.parent.mkdir(parents=True, exist_ok=True)
                
                with open(full_path, 'w', encoding='utf-8') as f:
                    f.write(placeholder_content)
                
                file_data = {
                    'path': file_path,
                    'content': placeholder_content,
                    'size': len(placeholder_content),
                    'type': self._get_file_type(file_path),
                    'icon': self._get_file_icon(file_path),
                    'language': self._get_file_language(file_path),
                    'error': True,
                    'error_message': str(e)
                }
                generated_files.append(file_data)
                print(f"   ⚠️  Created placeholder for: {file_path}")
                continue
    
        print(f"🔧 Generated {successful_files}/{len(file_structure)} files successfully")
    
        # Phase 3: Build preview
        await self._build_preview_reliable(project_id)
    
        return generated_files
    
    def _create_placeholder_content(self, file_path: str, error_message: str) -> str:
        """Create placeholder content for failed file generation"""
        if file_path.endswith('.py'):
            return f'''# Placeholder file for {file_path}
# Error during generation: {error_message}

print("Placeholder for {file_path} - generation failed")
'''
        elif file_path.endswith('.html'):
            return f'''<!DOCTYPE html>
<html>
<head>
    <title>Placeholder - {file_path}</title>
</head>
<body>
    <h1>Placeholder for {file_path}</h1>
    <p>Error during generation: {error_message}</p>
</body>
</html>'''
        elif file_path.endswith('.css'):
            return f'''/* Placeholder CSS for {file_path} */
/* Error during generation: {error_message} */

body {{
    font-family: Arial, sans-serif;
    margin: 20px;
}}
'''
        elif file_path.endswith('.js'):
            return f'''// Placeholder JavaScript for {file_path}
// Error during generation: {error_message}

console.log("Placeholder for {file_path}");
'''
        elif file_path == 'requirements.txt':
            return f'''# Placeholder requirements.txt
# Error during generation: {error_message}

flask>=2.0.0
'''
        else:
            return f"# Placeholder for {file_path}\n# Error: {error_message}"
    
    def _is_valid_generated_content_trusted(self, content: str, file_path: str) -> bool:
        """ADK validation - trust Gemini output more"""
        if not content or len(content.strip()) < 5:
            print(f"   ⚠️  Validation: Content too short for {file_path}")
            return False
        
        # File-specific validation with lenient rules
        if file_path.endswith('.py'):
            return self._is_valid_python_content_trusted(content, file_path)
        elif file_path.endswith('.html'):
            return self._is_valid_html_content_trusted(content)
        elif file_path.endswith('.css'):
            return self._is_valid_css_content_trusted(content)
        elif file_path.endswith('.js'):
            return self._is_valid_javascript_content_trusted(content)
        elif file_path.endswith('.txt') or file_path.endswith('.md'):
            return len(content.strip()) > 3
        else:
            return len(content.strip()) > 5
    
    def _is_valid_python_content_trusted(self, content: str, file_path: str) -> bool:
        """Lenient Python validation for ADK"""
        content_lower = content.lower()
        
        if file_path == 'app.py':
            flask_indicators = [
                'flask' in content_lower,
                '@app.route' in content,
                'render_template' in content,
                'from flask' in content
            ]
            return any(flask_indicators) or len(content.strip()) > 100
            
        elif file_path == 'requirements.txt':
            return any(char in content for char in ['=', '>', '<', '\n']) and len(content.strip()) > 5
            
        else:
            python_indicators = [
                'import ' in content,
                'def ' in content,
                'class ' in content,
                'from ' in content
            ]
            return any(python_indicators) or len(content.strip()) > 50
    
    def _is_valid_html_content_trusted(self, content: str) -> bool:
        """Lenient HTML validation for ADK"""
        html_indicators = [
            '<!doctype' in content.lower(),
            '<html' in content.lower(),
            '<head' in content.lower(),
            '<body' in content.lower(),
            '<div' in content
        ]
        return any(html_indicators) and '<' in content and '>' in content

    def _is_valid_css_content_trusted(self, content: str) -> bool:
        """Lenient CSS validation for ADK"""
        if not content or len(content.strip()) < 10:
            return False

        clean_content = content.strip()
    
        css_indicators = [
            '{' in clean_content and '}' in clean_content,
            any(char in clean_content for char in [':', ';', '#', '.']),
            any(word in clean_content.lower() for word in ['color', 'font', 'margin', 'padding'])
        ]
    
        has_any_css = any(css_indicators)
        balanced_braces = clean_content.count('{') == clean_content.count('}')
    
        return has_any_css or (balanced_braces and len(clean_content) > 20)
        
    def _is_valid_javascript_content_trusted(self, content: str) -> bool:
        """Lenient JavaScript validation for ADK"""
        content_lower = content.lower()
        
        js_indicators = [
            'function' in content,
            'const ' in content,
            'let ' in content,
            'document.' in content,
            'addeventlistener' in content_lower,
            'console.' in content
        ]
        
        no_frameworks = not any(fw in content_lower for fw in ['import react', 'from react', 'vue', 'angular', 'import vue'])
        
        return (any(js_indicators) or len(content.strip()) > 50) and no_frameworks

    async def _clean_project_directory(self, project_dir: Path):
        """Safely clean project directory"""
        if project_dir.exists():
            for attempt in range(3):
                try:
                    shutil.rmtree(project_dir)
                    print(f"🧹 Cleaned project directory: {project_dir}")
                    return
                except Exception as e:
                    if attempt == 2:
                        print(f"❌ Failed to clean directory {project_dir}: {e}")
                        raise
                    print(f"⚠️  Clean attempt {attempt + 1} failed, retrying...")
                    await asyncio.sleep(0.5)

    async def _build_preview_reliable(self, project_id: str):
        """Build preview with Flask server"""
        src_dir = self.projects_dir / f"project-{project_id}" / "src"
        preview_dir = self.projects_dir / f"project-{project_id}" / "preview"
    
        print(f"🔧 Building preview for project {project_id}...")
    
        for attempt in range(3):
            try:
                if preview_dir.exists():
                    shutil.rmtree(preview_dir)
            
                if src_dir.exists():
                    shutil.copytree(src_dir, preview_dir)
                    print(f"✅ Preview files copied successfully for {project_id}")
                
                    # Create Flask preview server
                    await self._create_flask_preview_server(project_id, preview_dir)
                    return
                else:
                    print(f"❌ Source directory not found: {src_dir}")
                    return
                
            except Exception as e:
                print(f"⚠️  Preview build attempt {attempt + 1} failed: {e}")
                if attempt == 2:
                    print(f"❌ Preview build failed after 3 attempts")
                await asyncio.sleep(1)

    async def _create_flask_preview_server(self, project_id: str, preview_dir: Path):
        """Create Flask preview server"""
        try:
            flask_app_content = self._generate_flask_preview_app(preview_dir)
            flask_app_file = preview_dir / "preview_app.py"

            with open(flask_app_file, 'w', encoding='utf-8') as f:
                f.write(flask_app_content)

            print(f"✅ Created Flask preview app for {project_id}")

        except Exception as e:
            print(f"❌ Failed to create Flask preview app: {e}")

    def _generate_flask_preview_app(self, preview_dir: Path) -> str:
        """Generate Flask preview app"""
        return '''"""
Flask Preview Server - ADK Version
"""
import os
from flask import Flask, render_template, send_from_directory

app = Flask(__name__, 
    template_folder='templates' if os.path.exists('templates') else '.',
    static_folder='static' if os.path.exists('static') else None
)

@app.route('/')
def index():
    try:
        if os.path.exists('templates/index.html'):
            return render_template('index.html')
        elif os.path.exists('index.html'):
            with open('index.html', 'r', encoding='utf-8') as f:
                return f.read()
        else:
            # List available files
            html_files = []
            for root, dirs, files in os.walk('.'):
                for file in files:
                    if file.endswith('.html'):
                        html_files.append(os.path.relpath(os.path.join(root, file)))
            
            if html_files:
                # Serve the first HTML file found
                with open(html_files[0], 'r', encoding='utf-8') as f:
                    return f.read()
            else:
                return "<h1>ADK Preview Server Running</h1><p>No HTML files found. Generated files:</p><ul>" + \
                       "".join([f"<li>{f}</li>" for f in os.listdir('.') if os.path.isfile(f)]) + "</ul>"
    except Exception as e:
        return f"<h1>Error rendering template</h1><p>{str(e)}</p>"

@app.route('/static/<path:filename>')
def serve_static(filename):
    static_dir = 'static'
    if not os.path.exists(static_dir):
        return "Static directory not found", 404
    return send_from_directory(static_dir, filename)

@app.route('/css/<path:filename>')
def serve_css(filename):
    css_dir = 'static/css' if os.path.exists('static/css') else 'static'
    if not os.path.exists(css_dir):
        return "CSS directory not found", 404
    return send_from_directory(css_dir, filename)

@app.route('/js/<path:filename>')
def serve_js(filename):
    js_dir = 'static/js' if os.path.exists('static/js') else 'static'
    if not os.path.exists(js_dir):
        return "JS directory not found", 404
    return send_from_directory(js_dir, filename)

@app.route('/<path:page>')
def serve_page(page):
    try:
        if page.endswith('.html'):
            template_name = page[:-5] if page.endswith('.html') else page
            if os.path.exists(f'templates/{template_name}.html'):
                return render_template(f'{template_name}.html')
            elif os.path.exists(page):
                with open(page, 'r', encoding='utf-8') as f:
                    return f.read()
        return "Page not found", 404
    except Exception as e:
        return f"Error serving page: {str(e)}", 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
'''

    def _get_available_port(self) -> int:
        """Find an available port for the preview server"""
        import socket
        def is_port_available(port):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(('localhost', port))
                    return True
            except OSError:
                return False
    
        start_port = settings.PREVIEW_PORT_RANGE[0]
        end_port = settings.PREVIEW_PORT_RANGE[1]
    
        for port in range(start_port, end_port + 1):
            if port not in self.preview_ports.values() and is_port_available(port):
                print(f"🔍 Found available port: {port}")
                return port

        for port in range(8000, 9000):
            if port not in self.preview_ports.values() and is_port_available(port):
                print(f"🔍 Found fallback available port: {port}")
                return port

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('localhost', 0))
            random_port = s.getsockname()[1]
            print(f"🔍 Using random available port: {random_port}")
            return random_port
        
    def _start_preview_server(self, project_id: str) -> int:
        """Start the preview server for a project"""
        try:
            port = self._get_available_port()
            preview_dir = self.projects_dir / f"project-{project_id}" / "preview"
    
            if not preview_dir.exists():
                print(f"❌ Preview directory not found: {preview_dir}")
                return 0

            flask_app_file = preview_dir / "preview_app.py"

            def serve_preview():
                try:
                    os.chdir(str(preview_dir))

                    if flask_app_file.exists():
                        import subprocess
                        import sys

                        # Update Flask app port before starting
                        self._update_flask_app_port(flask_app_file, port)

                        cmd = [sys.executable, "preview_app.py"]
                        env = os.environ.copy()
                        env['FLASK_APP'] = 'preview_app.py'
                        env['FLASK_ENV'] = 'development'
                        env['PORT'] = str(port)

                        print(f"🚀 Starting ADK Flask preview server on port {port}")
                        process = subprocess.Popen(
                            cmd,
                            env=env,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            text=True
                        )
                        process.wait()

                    else:
                        print(f"🔄 No Flask app found, using SimpleHTTP")
                        handler = http.server.SimpleHTTPRequestHandler
                        with socketserver.TCPServer(("", port), handler) as httpd:
                            print(f"🌐 SimpleHTTP server on port {port}")
                            httpd.serve_forever()

                except Exception as e:
                    print(f"❌ Preview server error: {e}")

            server_thread = threading.Thread(target=serve_preview, daemon=True)
            server_thread.start()

            if self._wait_for_server_ready(port, server_type='flask'):
                print(f"✅ ADK Preview server ready on port {port}")
                return port
            else:
                print(f"❌ ADK Preview server failed to start on port {port}")
                return 0

        except Exception as e:
            print(f"❌ Error starting ADK preview server: {e}")
            return 0

    def _update_flask_app_port(self, flask_app_file: Path, port: int):
        """Update the Flask app to use the specified port"""
        try:
            with open(flask_app_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Replace port in app.run() call
            if 'app.run(' in content:
                # Find and replace port parameter
                import re
                port_pattern = r'port=(\d+)'
                if re.search(port_pattern, content):
                    content = re.sub(port_pattern, f'port={port}', content)
                else:
                    # Add port parameter if not present
                    content = content.replace('app.run(', f'app.run(port={port}, ')
            
            with open(flask_app_file, 'w', encoding='utf-8') as f:
                f.write(content)

            print(f"🔧 Updated ADK Flask app to use port {port}")
        except Exception as e:
            print(f"⚠️  Could not update ADK Flask app port: {e}")

    def _wait_for_server_ready(self, port: int, max_attempts: int = 15, server_type: str = 'flask') -> bool:
        """Wait for the server to be ready"""
        url = f"http://localhost:{port}"

        print(f"⏳ Waiting for ADK {server_type} server on {url}...")

        for attempt in range(max_attempts):
            try:
                response = requests.get(url, timeout=3)
                if response.status_code == 200:
                    print(f"✅ ADK Server is ready after {attempt + 1} attempts")
                    return True
                elif response.status_code in [404, 500]:
                    # Server is running but route might not exist
                    print(f"✅ ADK Server is running (status {response.status_code})")
                    return True
            except (requests.ConnectionError, requests.Timeout) as e:
                if attempt % 3 == 0:
                    print(f"   Attempt {attempt + 1}/{max_attempts}: {type(e).__name__}")
            except Exception as e:
                print(f"   Attempt {attempt + 1} error: {e}")

            time.sleep(1)

        print(f"❌ ADK Server not ready after {max_attempts} attempts")
        return False

    def get_preview_url(self, project_id: str) -> str:
        """Get the preview URL for a project"""
        try:
            if project_id not in self.preview_ports:
                port = self._start_preview_server(project_id)
                if port:
                    self.preview_ports[project_id] = port
                    print(f"✅ ADK Preview assigned port {port} for {project_id}")
                    time.sleep(2)  # Give server time to start
                else:
                    print(f"❌ Failed to start ADK preview for {project_id}")
                    return ""

            preview_url = f"http://localhost:{self.preview_ports[project_id]}"
            print(f"🌐 ADK Preview URL: {preview_url}")
            return preview_url

        except Exception as e:
            print(f"❌ Error getting ADK preview URL: {e}")
            return ""

    # File type detection methods
    def _get_file_type(self, file_path: str) -> str:
        ext = file_path.split('.')[-1].lower()
        type_map = {
            'py': 'python', 'html': 'html', 'css': 'stylesheet', 
            'js': 'javascript', 'json': 'json', 'md': 'markdown', 'txt': 'text',
            'yml': 'yaml', 'yaml': 'yaml', 'env': 'environment'
        }
        return type_map.get(ext, 'text')

    def _get_file_icon(self, file_path: str) -> str:
        ext = file_path.split('.')[-1].lower()
        icon_map = {
            'py': '🐍', 'html': '🌐', 'css': '🎨', 'js': '📜',
            'json': '📋', 'md': '📝', 'txt': '📄', 'yml': '⚙️',
            'yaml': '⚙️', 'env': '🔧'
        }
        return icon_map.get(ext, '📄')

    def _get_file_language(self, file_path: str) -> str:
        ext = file_path.split('.')[-1].lower()
        lang_map = {
            'py': 'python', 'html': 'html', 'css': 'css', 
            'js': 'javascript', 'json': 'json', 'md': 'markdown',
            'yml': 'yaml', 'yaml': 'yaml'
        }
        return lang_map.get(ext, 'text')