<template>
  <div class="chat-interface">
    <!-- Chat Header -->
    <div class="chat-header">
      <h2>💬 Chat with AIDE</h2>
      <div class="project-info" v-if="projectName">
        <span class="project-badge">📁 {{ projectName }}</span>
        
        <!-- Generate Button - Only shows when requirements are collected -->
        <button 
          v-if="showGenerateButton"
          @click="generateCode"
          :disabled="!canGenerate || isGenerating"
          :class="['generate-btn', { 
            'ready': canGenerate && !isGenerating,
            'generating': isGenerating,
            'disabled': !canGenerate
          }]"
        >
          <span v-if="isGenerating">⏳ Generating...</span>
          <span v-else-if="canGenerate">🚀 Generate Code</span>
          <span v-else>⏳ {{ generationMessage }}</span>
        </button>
        
        <button @click="showNewProjectDialog = true" class="new-project-btn">
          New Project
        </button>
      </div>
      <button v-else @click="showNewProjectDialog = true" class="new-project-btn primary">
        🚀 Start New Project
      </button>
    </div>

    <!-- Generation Status Banner -->
    <div v-if="showGenerateButton && generationMessage" class="generation-status-banner" :class="statusClass">
      <div class="status-icon">{{ statusIcon }}</div>
      <div class="status-message">{{ generationMessage }}</div>
      <div class="status-details" v-if="agentContributions.length > 0">
        Agents contributed: {{ agentContributions.join(', ') }}
      </div>
    </div>

    <!-- Messages Container -->
    <div class="messages-container" ref="messagesContainer">
      <div 
        v-for="(message, index) in messages" 
        :key="index"
        :class="['message', message.role, { error: message.isError }]"
      >
        <!-- System Messages -->
        <div v-if="message.role === 'system'" class="system-message">
          <div class="message-icon">⚡</div>
          <div class="message-content">
            {{ message.content }}
          </div>
        </div>

        <!-- User Messages -->
        <div v-else-if="message.role === 'user'" class="user-message">
          <div class="message-avatar">👤</div>
          <div class="message-bubble">
            <div class="message-text">{{ message.content }}</div>
            <div class="message-time">{{ formatTime(message.timestamp) }}</div>
          </div>
        </div>

        <!-- Agent Messages -->
        <div v-else-if="message.role === 'agent'" class="agent-message">
          <div class="message-avatar">🤖</div>
          <div class="message-bubble">
            <div class="agent-badge">{{ getAgentDisplayName(message.agent) }}</div>
            <div class="message-text">{{ message.content }}</div>
            <div class="message-time">{{ formatTime(message.timestamp) }}</div>
          </div>
        </div>
      </div>

      <!-- Loading Indicator -->
      <div v-if="isLoading" class="loading-message">
        <div class="message-avatar">🤖</div>
        <div class="message-bubble">
          <div class="typing-indicator">
            <span></span>
            <span></span>
            <span></span>
          </div>
        </div>
      </div>
    </div>

    <!-- Input Area -->
    <div class="input-area">
      <div class="input-container">
        <textarea
          v-model="inputMessage"
          @keydown="handleKeydown"
          placeholder="Describe your project or ask for changes..."
          :disabled="!isConnected || isLoading"
          rows="2"
          ref="textArea"
        ></textarea>
        <button 
          @click="sendMessage" 
          :disabled="!inputMessage.trim() || !isConnected || isLoading"
          class="send-btn"
        >
          {{ isLoading ? '⏳' : '🚀' }}
        </button>
      </div>
      <div class="input-hint">
        💡 Describe your project features, design preferences, or technical requirements
      </div>
    </div>

    <!-- New Project Dialog -->
    <div v-if="showNewProjectDialog" class="dialog-overlay">
      <div class="dialog">
        <h3>🚀 Start New Project</h3>
        <input
          v-model="newProjectName"
          placeholder="Enter project name..."
          @keydown.enter="createProject"
          class="project-input"
        />
        <div class="dialog-actions">
          <button @click="showNewProjectDialog = false" class="btn-secondary">
            Cancel
          </button>
          <button 
            @click="createProject" 
            :disabled="!newProjectName.trim()"
            class="btn-primary"
          >
            Create Project
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, watch, nextTick, computed } from 'vue'
import { useProjectStore } from '../stores/project-store'

export default {
  name: 'ChatInterface',
  props: {
    messages: Array,
    isConnected: Boolean,
    projectName: String,
    projectId: String,
    generationStatus: Object
  },
  emits: ['send-message', 'new-project', 'generate-code', 'check-generation-status'],
  
  setup(props, { emit }) {
    const projectStore = useProjectStore()
    const inputMessage = ref('')
    const showNewProjectDialog = ref(false)
    const newProjectName = ref('')
    const messagesContainer = ref(null)
    const textArea = ref(null)
    
    // Generation state
    const canGenerate = ref(false)
    const isGenerating = computed(() => projectStore.isLoading)
    const generationMessage = ref('')
    const agentContributions = ref([])
    const showGenerateButton = ref(false)

    // Handle generation status updates from parent
    const updateGenerationStatus = (status) => {
      canGenerate.value = status.canGenerate || false
      generationMessage.value = status.message
      agentContributions.value = status.agentContributions || []
      
      if (status.canGenerate && !showGenerateButton.value) {
        showGenerateButton.value = true
      }
      console.log('🔄 Generation status updated:', { 
        canGenerate: canGenerate.value,
        message: generationMessage.value,
        contributions: agentContributions.value 
      })
    }

    watch(() => props.generationStatus, (newStatus) => {
      if (newStatus) {
        updateGenerationStatus(newStatus)
      }
    }, { immediate: true })

    // Watch for store isLoading changes to handle completion
    watch(() => projectStore.isLoading, (newLoadingState) => {
      console.log('🔄 Store isLoading changed:', newLoadingState)
      if (!newLoadingState && generationMessage.value === 'Generating code...') {
        generationMessage.value = 'Generation completed!'
        // Auto-clear message after 3 seconds
        setTimeout(() => {
          generationMessage.value = canGenerate.value ? 'Ready to generate!' : generationMessage.value
        }, 3000)
      }
    })

    // Auto-scroll to bottom when new messages arrive
    watch(() => props.messages.length, async () => {
      await nextTick()
      if (messagesContainer.value) {
        messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
      }
      
      // Show generate button after some messages are exchanged
      if (props.messages.length > 2 && props.projectId) {
        showGenerateButton.value = true
        checkGenerationStatus()
      }
    })

    // Check generation status when project changes
    watch(() => props.projectId, (newProjectId) => {
      if (newProjectId) {
        showGenerateButton.value = true
        checkGenerationStatus()
      } else {
        showGenerateButton.value = false
      }
    })

    const sendMessage = () => {
      if (!inputMessage.value.trim() || !props.isConnected || projectStore.isLoading) return
      
      const message = inputMessage.value.trim()
      emit('send-message', message)
      inputMessage.value = ''
      
      // Reset textarea height
      if (textArea.value) {
        textArea.value.style.height = 'auto'
      }
    }

    const handleKeydown = (event) => {
      if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault()
        sendMessage()
      }
    }

    const createProject = () => {
      if (!newProjectName.value.trim()) return
      
      emit('new-project', newProjectName.value.trim())
      showNewProjectDialog.value = false
      newProjectName.value = ''
    }

    const generateCode = async () => {
      if (!canGenerate.value || isGenerating.value || !props.projectId) return
      
      generationMessage.value = 'Generating code...'
      
      try {
        emit('generate-code', props.projectId)
      } catch (error) {
        console.error('Generation error:', error)
        generationMessage.value = 'Generation failed. Please try again.'
      }
    }

    const checkGenerationStatus = () => {
      if (!props.projectId) return
      emit('check-generation-status', props.projectId)
    }

    // Handle generation completion
    const handleGenerationComplete = () => {
      generationMessage.value = 'Code generated successfully!'
      
      // Reset status after a delay
      setTimeout(() => {
        checkGenerationStatus()
      }, 3000)
    }

    // Handle generation error
    const handleGenerationError = (errorMessage) => {
      generationMessage.value = errorMessage || 'Generation failed. Please try again.'
    }

    const formatTime = (timestamp) => {
      return new Date(timestamp).toLocaleTimeString('en-US', {
        hour: '2-digit',
        minute: '2-digit'
      })
    }

    const getAgentDisplayName = (agentName) => {
      const names = {
        'requirements_evolver': 'Requirements Evolver',
        'ux_architect': 'UX Architect',
        'ui_designer': 'UI Designer',
        'frontend_engineer': 'Frontend Engineer',
        'data_architect': 'Data Architect',
        'api_designer': 'API Designer',
        'devops': 'DevOps',
        'validation': 'Validation',
        'code_quality': 'Code Quality',
        'integration': 'Integration'
      }
      return names[agentName] || agentName
    }

    // Auto-resize textarea
    watch(inputMessage, () => {
      if (textArea.value) {
        textArea.value.style.height = 'auto'
        textArea.value.style.height = Math.min(textArea.value.scrollHeight, 120) + 'px'
      }
    })

    // Computed properties for status styling
    const statusClass = computed(() => {
      if (isGenerating.value) return 'generating'
      if (canGenerate.value) return 'ready'
      return 'waiting'
    })

    const statusIcon = computed(() => {
      if (isGenerating.value) return '⏳'
      if (canGenerate.value) return '✅'
      return '⏳'
    })

    return {
      inputMessage,
      showNewProjectDialog,
      newProjectName,
      messagesContainer,
      textArea,
      canGenerate,
      isGenerating,
      generationMessage,
      agentContributions,
      showGenerateButton,
      sendMessage,
      handleKeydown,
      createProject,
      generateCode,
      checkGenerationStatus,
      updateGenerationStatus,
      handleGenerationComplete,
      handleGenerationError,
      formatTime,
      getAgentDisplayName,
      statusClass,
      statusIcon
    }
  }
}
</script>

<style scoped>
.chat-interface {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: #f8fafc;
}

.chat-header {
  padding: 1.5rem;
  border-bottom: 1px solid #e2e8f0;
  background: white;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chat-header h2 {
  margin: 0;
  color: #1e293b;
  font-size: 1.5rem;
}

.project-info {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.project-badge {
  background: #e0f2fe;
  color: #0369a1;
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-weight: 600;
  font-size: 0.9rem;
}

/* Generate Button Styles */
.generate-btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 0.9rem;
  min-width: 160px;
}

.generate-btn.ready {
  background: #10b981;
  color: white;
  box-shadow: 0 4px 6px rgba(16, 185, 129, 0.3);
}

.generate-btn.ready:hover {
  background: #059669;
  transform: translateY(-2px);
  box-shadow: 0 6px 8px rgba(16, 185, 129, 0.4);
}

.generate-btn.generating {
  background: #f59e0b;
  color: white;
  cursor: not-allowed;
}

.generate-btn.disabled {
  background: #e2e8f0;
  color: #64748b;
  cursor: not-allowed;
}

.new-project-btn {
  background: #3b82f6;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
  transition: background 0.2s;
}

.new-project-btn:hover {
  background: #2563eb;
}

.new-project-btn:disabled {
  background: #94a3b8;
  cursor: not-allowed;
}

.new-project-btn.primary {
  background: #10b981;
}

.new-project-btn.primary:hover {
  background: #059669;
}

/* Generation Status Banner */
.generation-status-banner {
  padding: 1rem 1.5rem;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  border-bottom: 1px solid #e2e8f0;
}

.generation-status-banner.ready {
  background: #d1fae5;
  color: #065f46;
}

.generation-status-banner.waiting {
  background: #fef3c7;
  color: #92400e;
}

.generation-status-banner.generating {
  background: #dbeafe;
  color: #1e40af;
}

.status-icon {
  font-size: 1.2rem;
}

.status-message {
  font-weight: 600;
  flex: 1;
}

.status-details {
  font-size: 0.875rem;
  opacity: 0.8;
}

.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.message {
  max-width: 80%;
}

.message.user {
  align-self: flex-end;
}

.message.agent {
  align-self: flex-start;
}

.message.system {
  align-self: center;
  max-width: 90%;
}

.system-message {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: #f1f5f9;
  padding: 0.75rem 1rem;
  border-radius: 12px;
  color: #475569;
  font-size: 0.9rem;
}

.system-message.error {
  background: #fef2f2;
  color: #dc2626;
}

.message-icon {
  font-size: 1.2rem;
}

.user-message, .agent-message {
  display: flex;
  gap: 0.75rem;
  align-items: flex-start;
}

.user-message {
  flex-direction: row-reverse;
}

.message-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: white;
  border: 2px solid #e2e8f0;
  font-size: 1.2rem;
  flex-shrink: 0;
}

.message-bubble {
  background: white;
  padding: 1rem 1.25rem;
  border-radius: 18px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  position: relative;
}

.user-message .message-bubble {
  background: #3b82f6;
  color: white;
}

.agent-badge {
  font-size: 0.75rem;
  font-weight: 600;
  color: #6b7280;
  margin-bottom: 0.5rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.message-text {
  line-height: 1.5;
  white-space: pre-wrap;
}

.message-time {
  font-size: 0.75rem;
  opacity: 0.7;
  margin-top: 0.5rem;
}

.user-message .message-time {
  text-align: right;
}

.loading-message {
  display: flex;
  gap: 0.75rem;
  align-items: flex-start;
  align-self: flex-start;
}

.typing-indicator {
  display: flex;
  gap: 4px;
  padding: 1rem;
}

.typing-indicator span {
  height: 8px;
  width: 8px;
  background: #9ca3af;
  border-radius: 50%;
  animation: typing 1.4s infinite ease-in-out;
}

.typing-indicator span:nth-child(1) { animation-delay: 0s; }
.typing-indicator span:nth-child(2) { animation-delay: 0.2s; }
.typing-indicator span:nth-child(3) { animation-delay: 0.4s; }

@keyframes typing {
  0%, 60%, 100% { transform: translateY(0); }
  30% { transform: translateY(-10px); }
}

.input-area {
  padding: 1.5rem;
  border-top: 1px solid #e2e8f0;
  background: white;
}

.input-container {
  display: flex;
  gap: 0.75rem;
  align-items: flex-end;
}

.input-container textarea {
  flex: 1;
  border: 2px solid #e2e8f0;
  border-radius: 12px;
  padding: 1rem;
  font-family: inherit;
  font-size: 1rem;
  resize: none;
  outline: none;
  transition: border-color 0.2s;
  max-height: 120px;
}

.input-container textarea:focus {
  border-color: #3b82f6;
}

.input-container textarea:disabled {
  background: #f8fafc;
  cursor: not-allowed;
}

.send-btn {
  background: #10b981;
  color: white;
  border: none;
  width: 50px;
  height: 50px;
  border-radius: 50%;
  cursor: pointer;
  font-size: 1.2rem;
  transition: background 0.2s;
  flex-shrink: 0;
}

.send-btn:hover:not(:disabled) {
  background: #059669;
}

.send-btn:disabled {
  background: #94a3b8;
  cursor: not-allowed;
}

.input-hint {
  font-size: 0.875rem;
  color: #6b7280;
  margin-top: 0.5rem;
  text-align: center;
}

/* Dialog Styles */
.dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.dialog {
  background: white;
  padding: 2rem;
  border-radius: 12px;
  width: 90%;
  max-width: 400px;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
}

.dialog h3 {
  margin: 0 0 1.5rem 0;
  color: #1e293b;
}

.project-input {
  width: 100%;
  padding: 1rem;
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  font-size: 1rem;
  margin-bottom: 1.5rem;
  outline: none;
  transition: border-color 0.2s;
}

.project-input:focus {
  border-color: #3b82f6;
}

.dialog-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
}

.btn-primary, .btn-secondary {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
  transition: background 0.2s;
}

.btn-primary {
  background: #10b981;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #059669;
}

.btn-primary:disabled {
  background: #94a3b8;
  cursor: not-allowed;
}

.btn-secondary {
  background: #f1f5f9;
  color: #475569;
}

.btn-secondary:hover {
  background: #e2e8f0;
}

/* Scrollbar Styling */
.messages-container::-webkit-scrollbar {
  width: 6px;
}

.messages-container::-webkit-scrollbar-track {
  background: #f1f5f9;
}

.messages-container::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 3px;
}

.messages-container::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}
</style>