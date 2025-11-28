#!/usr/bin/env python3
"""
AIDE ADK - Agent Development Kit Version
Single command to start entire system with Gemini
"""

import os
import sys
import subprocess
import threading
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

def check_gemini_setup():
    """Verify Google AI setup"""
    try:
        # Check if GOOGLE_API_KEY is set
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            print("❌ GOOGLE_API_KEY environment variable not set")
            print("Please set your Google AI API key:")
            print("export GOOGLE_API_KEY='your-api-key-here'")
            return False
        
        print("✅ Google AI API key found")
        return True
    except Exception as e:
        print(f"❌ Gemini setup check failed: {e}")
        return False

def start_backend():
    """Start the Python WebSocket server"""
    print("🚀 Starting ADK Agent Server...")
    backend_dir = Path('agent-server')
    subprocess.run([sys.executable, 'main.py'], cwd=backend_dir)

def start_frontend():
    """Start the Vue frontend"""
    print("🎨 Starting Web UI...")
    frontend_dir = Path('web-ui')
    subprocess.run(['npm', 'run', 'dev'], shell=True, cwd=frontend_dir)
    
def main():
    print("=" * 50)
    print("🤖 AIDE ADK - Agent Development Kit with Gemini")
    print("=" * 50)
    
    # Check dependencies
    if not check_gemini_setup():
        return
    
    # Create necessary directories
    Path("projects").mkdir(exist_ok=True)
    Path("projects/templates").mkdir(exist_ok=True)
    
    print("📁 Project structure verified")
    
    # Start services in threads
    backend_thread = threading.Thread(target=start_backend, daemon=True)
    frontend_thread = threading.Thread(target=start_frontend, daemon=True)
    
    backend_thread.start()
    frontend_thread.start()
    
    print("✅ Both services starting...")
    print("🌐 Web UI will open at: http://localhost:3000")
    print("🔧 ADK Server at: ws://localhost:8765")
    print("🧠 Using Gemini:", os.getenv('GEMINI_MODEL', 'gemini-1.5-flash'))
    
    try:
        # Keep main thread alive
        while True:
            import time
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down AIDE ADK...")

if __name__ == "__main__":
    main()