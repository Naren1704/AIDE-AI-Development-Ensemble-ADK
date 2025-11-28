"""
ADK Configuration - Gemini & Agent Development Kit
"""

import os
from pathlib import Path

# Project Paths
PROJECTS_DIR = Path("projects")
TEMPLATES_DIR = PROJECTS_DIR / "templates"
GEMINI_API_KEY='your-api-key'
# Gemini Configuration
GEMINI_MODEL = "gemini-1.0-pro-latest"  # Fast and cost-effective
# Alternatives: "gemini-1.5-pro", "gemini-1.0-pro"

# ADK Agent Settings
MAX_RESPONSE_TOKENS = 2000
TEMPERATURE = 0.7

# Retry Configuration for ADK
RETRY_CONFIG = {
    "max_retries": 3,
    "backoff_factor": 1.0,
    "retryable_status_codes": [429, 500, 503]
}

# Session Configuration
SESSION_CONFIG = {
    'timeout': 3600,  # 1 hour session timeout
    'max_sessions': 100,
    'cleanup_interval': 300,  # 5 minutes
    'memory_limit': 10,  # Keep last 10 messages in memory
    'max_messages': 50,  # Maximum messages per session
    'session_cleanup': True
}

# Web Server Settings
WEB_UI_PORT = 3000
WS_SERVER_PORT = 8765
PREVIEW_PORT_RANGE = (3001, 3010)

# Agent Configuration
AGENT_CHAIN = [
    'requirements_evolver',
    'ux_architect', 
    'ui_designer',
    'frontend_engineer',
    'data_architect',
    'api_designer',
    'devops'
]

# Create directories
PROJECTS_DIR.mkdir(exist_ok=True)
TEMPLATES_DIR.mkdir(exist_ok=True)


print("✅ ADK Config Loaded - Using Gemini & Agent Development Kit")
