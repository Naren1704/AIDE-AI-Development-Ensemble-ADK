<template>
  <div class="agent-status">
    <h3>🛠️ Active Agents</h3>
    
    <!-- Project Info -->
    <div v-if="projectName" class="project-card">
      <div class="project-header">
        <h4>📁 {{ projectName }}</h4>
        <span class="project-id">#{{ projectId }}</span>
      </div>
      <div class="project-meta">
        <div class="meta-item">
          <span class="label">Status:</span>
          <span class="value" :class="isConnected ? 'connected' : 'disconnected'">
            {{ isConnected ? 'Active' : 'Disconnected' }}
          </span>
        </div>
        <div class="meta-item" v-if="generatedFiles && generatedFiles.length > 0">
          <span class="label">Files:</span>
          <span class="value">{{ generatedFiles.length }} generated</span>
        </div>
      </div>
    </div>

    <!-- Current Agent -->
    <div class="current-agent">
      <div class="section-title">🎯 Currently Active</div>
      <div class="agent-card active">
        <div class="agent-icon">{{ getAgentIcon(activeAgent) }}</div>
        <div class="agent-info">
          <div class="agent-name">{{ getAgentDisplayName(activeAgent) }}</div>
          <div class="agent-role">{{ getAgentRole(activeAgent) }}</div>
        </div>
        <div class="status-indicator"></div>
      </div>
    </div>

    <!-- All Agents -->
    <div class="all-agents">
      <div class="section-title">👥 All Specialists</div>
      <div class="agents-list">
        <div 
          v-for="agent in allAgents" 
          :key="agent.id"
          :class="['agent-item', { active: agent.id === activeAgent, completed: isAgentCompleted(agent.id) }]"
        >
          <div class="agent-icon">{{ agent.icon }}</div>
          <div class="agent-details">
            <div class="agent-name">{{ agent.name }}</div>
            <div class="agent-description">{{ agent.description }}</div>
          </div>
          <div class="completion-indicator">
            <span v-if="isAgentCompleted(agent.id)">✅</span>
            <span v-else-if="agent.id === activeAgent" class="pulse">🔵</span>
            <span v-else>⏳</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Quick Actions -->
    <div class="quick-actions">
      <div class="section-title">⚡ Quick Actions</div>
      <div class="actions-grid">
        <button @click="requestPreview" class="action-btn" :disabled="!isConnected || !projectId">
          <span class="action-icon">🌐</span>
          <span class="action-text">Refresh Preview</span>
        </button>
        <button @click="suggestImprovements" class="action-btn" :disabled="!isConnected || !projectId">
          <span class="action-icon">💡</span>
          <span class="action-text">Suggest Improvements</span>
        </button>
        <button @click="exportProject" class="action-btn" :disabled="!projectId">
          <span class="action-icon">📥</span>
          <span class="action-text">Export Project</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import { useProjectStore } from '../stores/project-store'

export default {
  name: 'AgentStatus',
  props: {
    activeAgent: String,
    projectName: String,
    projectId: String,
    isConnected: Boolean,
    generatedFiles: {
      type: Array,
      default: () => []
    }
  },
  
  setup(props) {
    const projectStore = useProjectStore()
    
    const allAgents = ref([
      {
        id: 'requirements_evolver',
        name: 'Requirements Evolver',
        icon: '🔍',
        description: 'Understands project goals and scope',
        completed: false
      },
      {
        id: 'ux_architect',
        name: 'UX Architect', 
        icon: '📐',
        description: 'Designs user experience and navigation',
        completed: false
      },
      {
        id: 'ui_designer',
        name: 'UI Designer',
        icon: '🎨',
        description: 'Creates visual design and styling',
        completed: false
      },
      {
        id: 'frontend_engineer',
        name: 'Frontend Engineer',
        icon: '💻',
        description: 'Implements frontend functionality',
        completed: false
      },
      {
        id: 'data_architect',
        name: 'Data Architect',
        icon: '🗄️',
        description: 'Designs database and storage',
        completed: false
      },
      {
        id: 'api_designer',
        name: 'API Designer',
        icon: '🔗',
        description: 'Creates backend APIs',
        completed: false
      },
      {
        id: 'devops',
        name: 'DevOps',
        icon: '🚀',
        description: 'Handles deployment and hosting',
        completed: false
      },
      {
        id: 'validation',
        name: 'Validation',
        icon: '✅',
        description: 'Validates requirements',
        completed: false
      },
      {
        id: 'code_quality',
        name: 'Code Quality',
        icon: '📊',
        description: 'Ensures code standards',
        completed: false
      },
      {
        id: 'integration',
        name: 'Integration',
        icon: '🔄',
        description: 'Integrates all components',
        completed: false
      }
    ])

    const getAgentDisplayName = (agentId) => {
      const agent = allAgents.value.find(a => a.id === agentId)
      return agent ? agent.name : agentId
    }

    const getAgentIcon = (agentId) => {
      const agent = allAgents.value.find(a => a.id === agentId)
      return agent ? agent.icon : '🤖'
    }

    const getAgentRole = (agentId) => {
      const roles = {
        'requirements_evolver': 'Understanding your needs',
        'ux_architect': 'Designing user experience', 
        'ui_designer': 'Creating visual design',
        'frontend_engineer': 'Building frontend',
        'data_architect': 'Structuring data',
        'api_designer': 'Designing APIs',
        'devops': 'Planning deployment',
        'validation': 'Validating requirements',
        'code_quality': 'Checking code quality',
        'integration': 'Integrating components'
      }
      return roles[agentId] || 'Processing your request'
    }

    const isAgentCompleted = (agentId) => {
      // Simple logic - in real app, this would check project state
      const agentIndex = allAgents.value.findIndex(a => a.id === agentId)
      const activeIndex = allAgents.value.findIndex(a => a.id === props.activeAgent)
      return agentIndex < activeIndex
    }

    const requestPreview = () => {
      projectStore.refreshPreview()
    }

    const suggestImprovements = () => {
      projectStore.suggestImprovements()
    }

    const exportProject = () => {
      projectStore.exportProject()
    }

    return {
      allAgents,
      getAgentDisplayName,
      getAgentIcon,
      getAgentRole,
      isAgentCompleted,
      requestPreview,
      suggestImprovements,
      exportProject
    }
  }
}
</script>

<style scoped>
.agent-status {
  height: 100%;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.agent-status h3 {
  margin: 0 0 0.5rem 0;
  color: #1e293b;
  font-size: 1.25rem;
}

.project-card {
  background: #f0f9ff;
  border: 1px solid #bae6fd;
  border-radius: 8px;
  padding: 1rem;
}

.project-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 0.75rem;
}

.project-header h4 {
  margin: 0;
  color: #0369a1;
  font-size: 1rem;
}

.project-id {
  background: #0ea5e9;
  color: white;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 600;
}

.project-meta {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.meta-item {
  display: flex;
  justify-content: between;
}

.label {
  font-weight: 600;
  color: #475569;
  margin-right: 0.5rem;
}

.value.connected {
  color: #10b981;
  font-weight: 600;
}

.value.disconnected {
  color: #ef4444;
  font-weight: 600;
}

.section-title {
  font-size: 0.875rem;
  font-weight: 600;
  color: #6b7280;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 0.75rem;
}

.current-agent {
  margin-top: 0.5rem;
}

.agent-card {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: white;
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  transition: all 0.2s;
}

.agent-card.active {
  border-color: #3b82f6;
  background: #f8fafc;
}

.agent-icon {
  font-size: 1.5rem;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: white;
  border-radius: 8px;
  flex-shrink: 0;
}

.agent-info {
  flex: 1;
}

.agent-name {
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 0.25rem;
}

.agent-role {
  font-size: 0.875rem;
  color: #6b7280;
}

.status-indicator {
  width: 8px;
  height: 8px;
  background: #10b981;
  border-radius: 50%;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.all-agents {
  flex: 1;
  overflow: hidden;
}

.agents-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  max-height: 300px;
  overflow-y: auto;
}

.agent-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem;
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  transition: all 0.2s;
  cursor: pointer;
}

.agent-item:hover {
  border-color: #3b82f6;
  background: #f8fafc;
}

.agent-item.active {
  border-color: #3b82f6;
  background: #eff6ff;
}

.agent-item.completed {
  border-color: #10b981;
  background: #f0fdf4;
}

.agent-details {
  flex: 1;
}

.agent-item .agent-name {
  font-size: 0.875rem;
  margin-bottom: 0.125rem;
}

.agent-description {
  font-size: 0.75rem;
  color: #6b7280;
  line-height: 1.3;
}

.completion-indicator {
  font-size: 0.75rem;
}

.pulse {
  animation: pulse 2s infinite;
}

.quick-actions {
  margin-top: auto;
}

.actions-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 0.5rem;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem;
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
  width: 100%;
  text-align: left;
}

.action-btn:hover:not(:disabled) {
  border-color: #3b82f6;
  background: #f8fafc;
}

.action-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.action-icon {
  font-size: 1.25rem;
}

.action-text {
  font-size: 0.875rem;
  font-weight: 500;
  color: #374151;
}

/* Scrollbar for agents list */
.agents-list::-webkit-scrollbar {
  width: 4px;
}

.agents-list::-webkit-scrollbar-track {
  background: #f1f5f9;
}

.agents-list::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 2px;
}
</style>