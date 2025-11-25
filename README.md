# AIDE ADK: Agent Development Kit 🚀

A modular, extensible multi-agent system for AI-powered web application development. Built with Google's Agent Development Kit (ADK) featuring Gemini integration, session management, and enterprise-ready architecture.

![ADK Architecture](https://img.shields.io/badge/Architecture-Modular_Multi--Agent-blue)
![Gemini Powered](https://img.shields.io/badge/Powered%20By-Google%20Gemini-red)
![Python](https://img.shields.io/badge/Python-3.8%2B-green)
![Vue.js](https://img.shields.io/badge/Frontend-Vue.js-brightgreen)
![Google ADK](https://img.shields.io/badge/Framework-Google%20ADK-purple)

## 🌟 What is AIDE ADK?

AIDE ADK (Agent Development Kit) is an enterprise-ready evolution of the original AIDE system, now powered by Google's Agent Development Kit and Gemini models. It features a modular multi-agent architecture with enhanced session management, comprehensive observability, and seamless integration with Google's AI ecosystem.

## 🏗️ ADK Architecture Overview

```
AIDE-ADK/
├── 🎯 Google ADK Core
│   ├── Gemini Integration & LLM Management
│   ├── Session Management (InMemorySessionService)
│   ├── Sequential Agent Runner
│   └── Retry Configuration & Error Handling
├── 🤖 Multi-Agent Ensemble
│   ├── Requirements Evolver Agent
│   ├── UX Architect Agent  
│   ├── UI Designer Agent
│   ├── Frontend Engineer Agent
│   ├── Data Architect Agent
│   ├── API Designer Agent
│   └── DevOps Agent
├── 🔧 ADK Services
│   ├── Session-Aware Storage
│   ├── Modular Project Builder
│   ├── Enhanced Integration Agent
│   └── Observable WebSocket Server
└── 🌐 Web UI (Compatible)
    ├── Vue.js 3 Frontend
    ├── Real-time Chat Interface
    └── Live Preview & File Explorer
```

## 🆚 ADK vs Original AIDE

| Feature | Original AIDE | AIDE ADK |
|---------|---------------|----------|
| **AI Backend** | Ollama (Local) | Google Gemini (Cloud) |
| **Framework** | Custom Implementation | Google Agent Development Kit |
| **Session Management** | Basic conversation history | InMemorySessionService with context compaction |
| **Agent Coordination** | Custom routing logic | Sequential Runner with session context |
| **Error Handling** | Basic retries | Configurable retry policies |
| **Extensibility** | Hard-coded agents | ADK-based plugin architecture |

## 🎯 Core ADK Concepts Implemented

### 1. **Agent Powered by LLM** 🤖
- **Gemini Integration**: Complete shift from Ollama to Google Gemini
- **ADK Agent Framework**: Built on Google's official Agent Development Kit
- **Configurable Models**: Support for Gemini 1.5 Flash, Pro, and other variants
- **Retry Mechanisms**: Built-in retry policies for reliable API calls

### 2. **Sequential Agents** ⚡
- **Runner-based Execution**: Coordinated agent flow using ADK Runner
- **Session Context**: Each agent receives proper session context
- **Ordered Processing**: Sequential execution with memory persistence
- **Context Engineering**: Smart context building from session memory

### 3. **Sessions & Memory** 💾
- **InMemorySessionService**: Google ADK's session management
- **State Persistence**: Agent interactions stored across sessions
- **Memory Compaction**: Automatic context optimization
- **Session-aware Generation**: Context-informed project building

## ✨ Key ADK Features

### 🎭 Enterprise-Grade Agent System

```python
# Google ADK Agent Management
from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini
from google.adk.runners import Runner

# Register agents with ADK
agent = Agent(
    name="requirements_evolver",
    system_prompt="Your specialized prompt...",
    llm=Gemini(model="gemini-1.5-flash")
)
```

### 💾 Advanced Session Management

```python
# ADK Session Configuration
from google.adk.sessions import InMemorySessionService

session_service = InMemorySessionService()
session = await session_service.get_session(project_id)

# Session memory with automatic compaction
session.memory.append({
    'agent': agent_name,
    'user_input': user_message,
    'response': agent_response
})
```

### 🔄 Sequential Agent Coordination

```python
# Run agents sequentially with ADK Runner
results = await self.adk_manager.run_sequential_agents(
    session_id=project_id,
    user_input=user_message,
    agent_chain=settings.AGENT_CHAIN
)
```

### 🛡️ Production-Ready Configuration

```python
# Gemini & Retry Configuration
GEMINI_MODEL = "gemini-1.5-flash"
RETRY_CONFIG = {
    "max_retries": 3,
    "backoff_factor": 1.0,
    "retryable_status_codes": [429, 500, 503]
}
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- Google AI API Key

### Installation

1. **Clone the ADK Repository**
   ```bash
   git clone https://github.com/your-username/AIDE-ADK.git
   cd AIDE-ADK
   ```

2. **Set up Google AI API Key**
   ```bash
   export GOOGLE_API_KEY='your-google-ai-api-key-here'
   ```

3. **Backend Setup**
   ```bash
   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   # Install dependencies
   pip install -r requirements.txt
   ```

4. **Frontend Setup** (Same as original AIDE)
   ```bash
   cd web-ui
   npm install
   cd ..
   ```

### Running AIDE ADK

1. **Start the ADK Backend**
   ```bash
   python run.py
   ```

2. **Start the Frontend** (in a new terminal)
   ```bash
   cd web-ui
   npm run dev
   ```

3. **Access ADK**
   - Open http://localhost:3000
   - Start chatting with the Google Gemini-powered multi-agent system!

## 🔧 ADK Configuration

### Gemini Configuration (`config/settings.py`)
```python
# Gemini Configuration
GEMINI_MODEL = "gemini-1.5-flash"  # Fast and cost-effective
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

# Agent Sequence
AGENT_CHAIN = [
    'requirements_evolver',
    'ux_architect', 
    'ui_designer',
    'frontend_engineer',
    'data_architect',
    'api_designer',
    'devops'
]
```

### Supported Gemini Models
- `gemini-1.5-flash` (Recommended for speed and cost)
- `gemini-1.5-pro` (Higher quality, more expensive)
- `gemini-1.0-pro` (Legacy, stable)

## 🛠️ Development & Extension

### Adding New Agents with ADK

```python
from google.adk.agents import Agent

class ADKOrchestrator:
    def _register_agents(self):
        """Register agents with Google ADK"""
        self.adk_manager.register_agent(
            'custom_agent',
            """You are a Custom Agent. Your role is...
            - Specialized task description
            - Domain-specific guidelines
            - Interaction rules"""
        )
```

### Custom Session Management

```python
from google.adk.sessions import InMemorySessionService

class CustomADKManager:
    def __init__(self):
        self.session_service = InMemorySessionService()
        self.llm = Gemini(model=GEMINI_MODEL)
        self.runner = Runner()
```

### Extending with ADK Tools

```python
# Example of adding tools (future enhancement)
from google.adk.tools import Tool

custom_tool = Tool(
    name="code_validator",
    description="Validates generated code",
    function=validate_code_function
)
```

## 📊 Monitoring & Observability

### Logging
- **Structured Logging**: Comprehensive ADK system logs
- **Agent Activity**: Track Gemini API calls and responses
- **Session Tracking**: Monitor session lifecycle and memory usage
- **Performance Metrics**: Response times and success rates

### Health Checks
```bash
# Check Gemini API connectivity
curl -X GET "http://localhost:8765/health"

# Monitor system logs
tail -f adk_system.log
```

## 🎯 Enhanced Use Cases

### 🏢 Enterprise Applications
- **Scalable Architecture**: Google ADK provides enterprise-grade foundation
- **Reliable API Integration**: Built-in retry mechanisms and error handling
- **Session Persistence**: Maintain context across complex conversations
- **Production Ready**: Battle-tested Google infrastructure

### 🔬 Research & Development
- **Experimental Configurations**: Easy agent and model swapping
- **Performance Metrics**: Detailed timing and success rate tracking
- **Context Engineering**: Advanced session memory management
- **Extensible Framework**: Built on Google's evolving ADK platform

### 🌐 Multi-Platform Development
- **Framework Agnostic**: Easy to adapt for different tech stacks
- **API-First Design**: Clean separation between agents and frontend
- **Cloud Native**: Designed for deployment on Google Cloud Platform
- **Scalable Sessions**: Efficient memory management for many concurrent users

## 🔄 Migration from Original AIDE

### Smooth Upgrade Path
1. **Backup your projects**
2. **Set up Google AI API key**
3. **Install ADK version**
4. **Existing projects work immediately**
5. **Enjoy enhanced Google ADK features**

### Breaking Changes
- **None!** ADK maintains full backward compatibility
- All existing projects and frontend code work unchanged
- Enhanced features are opt-in through configuration
- Same WebSocket API and data structures

### Benefits of Migration
- **Enterprise Reliability**: Google's infrastructure and support
- **Better Performance**: Optimized Gemini models and ADK framework
- **Future Proof**: Built on Google's evolving agent platform
- **Enhanced Features**: Session management, retry policies, and more

## 🤝 Contributing to ADK

We welcome contributions to enhance the ADK platform! Areas for contribution:

### Core Enhancements
- New agent specializations using ADK framework
- Additional session management strategies
- Enhanced observability features
- Performance optimizations for Gemini integration

### Plugin Development
- Framework adapters (React, Django, etc.)
- Database integrations with session persistence
- External tool integrations using ADK Tools
- Custom validation systems

### Documentation & Examples
- Agent development guides for Google ADK
- Configuration examples for different use cases
- Performance tuning guides
- Deployment guides for Google Cloud Platform

## 📞 Support & Community

- 📧 **Email**: narendren2006@gmail.com
- 💬 **Discussions**: GitHub Discussions
- 🐛 **Issues**: GitHub Issue

## 🙏 Acknowledgments

- **Google ADK Team** - Agent Development Kit framework
- **Google Gemini** - Powerful AI models and infrastructure
- **Original AIDE Project** - Foundation for this evolution
- **Vue.js Community** - Excellent frontend framework
- **AI/ML Community** - Continuous inspiration and innovation

## 🐛 Troubleshooting

### Common ADK Issues

**Gemini API Issues**
```bash
# Check API key
echo $GOOGLE_API_KEY

# Test Gemini connectivity
python -c "import google.generativeai as genai; genai.configure(api_key='$GOOGLE_API_KEY'); print('API OK')"
```

**Session Management Problems**
```bash
# Check session logs
grep "SESSION" adk_system.log

# Reset specific session
rm projects/project-{id}.json
```

**Performance Optimization**
```python
# Adjust retry configuration
RETRY_CONFIG = {
    "max_retries": 5,  # Increase for unstable connections
    "backoff_factor": 2.0,  # More aggressive backoff
}
```

---

<div align="center">

**AIDE ADK: Enterprise Multi-Agent Development**

*Powered by Google Gemini and Agent Development Kit*

[🏠 Home](https://github.com/your-username/AIDE-ADK) • 
[📖 Docs](https://github.com/your-username/AIDE-ADK/wiki) • 
[🚀 Getting Started](#quick-start) • 
[🎯 ADK Features](#-core-adk-concepts-implemented)

</div>
