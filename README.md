
# AIDE ADK: Agent Development Kit 🚀

A modular, extensible multi-agent system for AI-powered web application development. Built on the foundation of AIDE with enhanced architecture, observability, and session management.

![ADK Architecture](https://img.shields.io/badge/Architecture-Modular_Multi--Agent-blue)
![Ollama Powered](https://img.shields.io/badge/Powered%20By-Ollama-orange)
![Python](https://img.shields.io/badge/Python-3.8%2B-green)
![Vue.js](https://img.shields.io/badge/Frontend-Vue.js-brightgreen)
![Observability](https://img.shields.io/badge/Observability-Enhanced-yellow)

## 🌟 What is AIDE ADK?

AIDE ADK (Agent Development Kit) is an evolved version of the original AIDE system, featuring a modular multi-agent architecture with enhanced session management, comprehensive observability, and extensible plugin support. It transforms AI-powered development from a fixed pipeline into a configurable, observable platform.

## 🏗️ ADK Architecture Overview

AIDE-ADK/

├── 🎯 ADK Core System

│ ├── Configurable Agent Registry

│ ├── Session Management & Memory

│ ├── Enhanced Observability

│ └── Plugin System Foundation

├── 🤖 Multi-Agent Ensemble

│ ├── Requirements Evolver Agent

│ ├── UX Architect Agent

│ ├── UI Designer Agent

│ ├── Frontend Engineer Agent

│ ├── Data Architect Agent

│ ├── API Designer Agent

│ └── DevOps Agent

├── 🔧 ADK Services

│ ├── Session-Aware Storage

│ ├── Modular Project Builder

│ ├── Enhanced Integration Agent

│ └── Observable WebSocket Server

└── 🌐 Web UI (Compatible)

├── Vue.js 3 Frontend

├── Real-time Chat Interface

└── Live Preview & File Explorer


## 🆚 ADK vs Original AIDE

| Feature | Original AIDE | AIDE ADK |
|---------|---------------|----------|
| **Architecture** | Fixed agent pipeline | Modular, configurable |
| **Session Management** | Basic conversation history | Enhanced sessions with memory compaction |
| **Observability** | Basic logging | Comprehensive metrics & tracing |
| **Extensibility** | Hard-coded agents | Plugin-ready architecture |
| **Validation** | Strict rules | Trust-based, Ollama-optimized |
| **Configuration** | Simple settings | YAML-ready, environment-aware |

## 🎯 Core ADK Concepts Implemented

### 1. **Multi-agent System** 🎭
- **Configurable Agent Registry**: Dynamic agent loading from configuration
- **Sequential Agent Chain**: Ordered execution with intelligent switching
- **Specialized Agent Classes**: Domain-specific expertise with shared base
- **Context-Aware Routing**: Smart message routing based on session context

### 2. **Sessions & Memory** 💾
- **ADKSession Class**: Dedicated session management with state tracking
- **Context Engineering**: Smart memory compaction and optimization
- **Agent State Persistence**: Individual agent interaction history
- **Session-Aware Generation**: Context-informed project building

### 3. **Observability** 📊
- **Structured Logging**: Comprehensive, leveled logging throughout
- **Performance Metrics**: Request counting, timing, connection tracking
- **System Monitoring**: Health checks and status reporting
- **Traceability**: Full request/response flow with agent activity

## ✨ Key ADK Features

### 🎭 Enhanced Multi-Agent Coordination

# Configurable agent system

AGENTS_CONFIG = {
    "requirements_evolver": {
        "description": "📋 Core Features & Goals",
        "temperature": 0.7,
        "max_tokens": 800
    },
    # ... more agents
}

AGENT_SEQUENCE = [
    'requirements_evolver',
    'ux_architect', 
    'ui_designer',
    # ... sequential flow
]

💾 Advanced Session Management

# Session configuration
SESSION_CONFIG = {
    "max_messages": 50,
    "context_window": 4000,
    "compaction_strategy": "recent",  # recent/summary/priority
    "retention_days": 30
}
📊 Comprehensive Observability

# Observability setup
OBSERVABILITY_CONFIG = {
    "log_level": "INFO",
    "enable_tracing": True,
    "enable_metrics": True,
    "trace_agent_calls": True,
    "log_agent_responses": True
}

🚀 Quick Start

Prerequisites

Python 3.8+

Node.js 16+

Ollama (with at least one model installed)

Installation

Clone the ADK Repository

git clone https://github.com/your-username/AIDE-ADK.git
cd AIDE-ADK
Backend Setup

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
Frontend Setup (Same as original AIDE)

cd web-ui
npm install
cd ..
Ollama Setup

# Install Ollama (if not already installed)
# Visit: https://ollama.ai/

# Pull a model
ollama pull llama2
ADK Configuration

# Edit config/settings.py
OLLAMA_MODEL = "llama2"
# Configure agents, sessions, observability as needed
Running AIDE ADK
Start the ADK Backend

python run.py
Start the Frontend (in a new terminal)

cd web-ui
npm run dev
Access ADK

Open http://localhost:3000

Start chatting with the enhanced multi-agent system!

🔧 ADK Configuration
Agent Configuration (config/settings.py)
python
AGENTS_CONFIG = {
    "requirements_evolver": {
        "description": "📋 Core Features & Goals",
        "prompt_template": "requirements_evolver",
        "temperature": 0.7,
        "max_tokens": 800
    },
    # Add more agents or modify existing ones
}

AGENT_SEQUENCE = [
    'requirements_evolver',
    'ux_architect', 
    # Customize the agent flow
]
Session & Memory Configuration
python
SESSION_CONFIG = {
    "max_messages": 50,
    "context_window": 4000,
    "compaction_strategy": "recent",  # recent/summary/priority
    "retention_days": 30
}
Observability Configuration

OBSERVABILITY_CONFIG = {
    "log_level": "INFO",  # DEBUG/INFO/WARNING/ERROR
    "enable_tracing": True,
    "enable_metrics": True,
    "log_file": "adk_system.log"
}

🛠️ Development & Extension
Adding New Agents
Create Agent Class

class CustomAgent(ADKAgent):
    def _build_prompt(self, user_message: str, context: Dict[str, Any]) -> str:
        # Custom prompt logic
        return custom_prompt
Register in Configuration

AGENTS_CONFIG = {
    "custom_agent": {
        "description": "🎯 Custom Domain",
        "temperature": 0.6,
        "max_tokens": 600
    }
}

AGENT_SEQUENCE = [
    'requirements_evolver',
    'custom_agent',  # Add to sequence
    # ... other agents
]
Customizing Session Management

class CustomSession(ADKSession):
    def _compact_context(self):
        # Custom compaction logic
        if len(self.messages) > self.max_messages:
            # Implement custom strategy
            pass
Extending Observability

# Custom metrics collection
def track_custom_metric(metric_name: str, value: float):
    logger.info(f"METRIC {metric_name}: {value}")
    # Add to custom metrics storage
    
📊 Monitoring & Logs
Log Files
adk_system.log - Main system log

adk_websocket.log - WebSocket communication log

adk_storage.log - Storage operations log

Key Metrics Tracked
Agent interaction counts

Message processing times

Generation success rates

Session activity levels

Connection statistics

Health Checks
bash
# Check system status via WebSocket
curl -X GET "http://localhost:8765/health"

# Monitor log files
tail -f adk_system.log
🎯 Use Cases Enhanced by ADK
🏥 Complex Healthcare Systems
Multi-specialist agent coordination

Session persistence for patient contexts

Compliance and audit trails

🏢 Enterprise Applications
Configurable agent teams per department

Enhanced observability for debugging

Custom agent extensions for business logic

🔬 Research & Development
Experimental agent configurations

Detailed interaction tracing

Performance metrics for optimization

🔄 Migration from Original AIDE
Smooth Upgrade Path
Backup your projects

Install ADK version

Existing projects work immediately

Enjoy enhanced features

Breaking Changes
None! ADK maintains full backward compatibility

All existing projects and frontend code work unchanged

Enhanced features are opt-in through configuration

🤝 Contributing to ADK
We welcome contributions to enhance the ADK platform! Areas for contribution:

Core Enhancements
New agent specializations

Additional session strategies

Enhanced observability features

Performance optimizations

Plugin Development
Framework adapters (React, Django, etc.)

Database integrations

External tool integrations

Custom validation systems

Documentation & Examples
Agent development guides

Configuration examples

Use case tutorials

Performance tuning guides

🙏 Acknowledgments
Original AIDE Project - Foundation for this evolution

Ollama - Local AI inference capabilities

Vue.js & Flask Communities - Excellent frameworks

AI/ML Community - Continuous inspiration and innovation

🐛 Troubleshooting
Common ADK Issues
Session Memory Issues

# Check session logs
grep "SESSION" adk_system.log

# Reset specific session
rm projects/project-{id}.json
Agent Configuration Problems

# Enable debug logging
OBSERVABILITY_CONFIG = {
    "log_level": "DEBUG",
    # ... other settings
}
Performance Optimization

# Adjust context compaction
SESSION_CONFIG = {
    "compaction_strategy": "summary",  # More aggressive compaction
    "max_messages": 30  # Reduce context window
}

📞 Support & Community
📧 Email: narendren2006@gmail.com

💬 Discussions: GitHub Discussions

🐛 Issues: GitHub Issues


<div align="center">
AIDE ADK: Evolved Multi-Agent Development

Building on AIDE's foundation with modular architecture, enhanced observability, and enterprise-ready features.

🏠 Home • 📖 Docs • 🚀 Getting Started • 🎯 ADK Features

</div>
