<template>
  <div id="app">
    <header class="app-header">
      <div class="header-content">
        <h1>🤖 AIDE V2</h1>
        <p>AI Development Ensemble - Build Apps with AI Agents</p>
      </div>
    </header>

    <main class="app-main">
      <div class="container">
        <div class="layout">
          <!-- Left Sidebar - Agent Status -->
          <aside class="sidebar">
            <AgentStatus 
              :active-agent="activeAgent"
              :project-name="projectName"
              :project-id="projectId"
              :is-connected="isConnected"
              :generated-files="generatedFiles"
            />
          </aside>

          <!-- Main Chat Area -->
          <section class="chat-section">
            <ChatInterface
              :messages="messages"
              :is-loading="isLoading"
              :is-connected="isConnected"
              :project-name="projectName"
              :project-id="projectId"
              :generation-status="generationStatus"
              @send-message="sendMessage"
              @new-project="createNewProject"
              @generate-code="generateCode"
              @check-generation-status="checkGenerationStatus"
            />
          </section>

          <!-- Right Preview Panel -->
          <aside class="preview-section">
            <LivePreview
              :preview-url="previewUrl"
              :project-id="projectId"
            />
            <FileExplorer
              v-if="projectId"
              :files="generatedFiles"
              :project-id="projectId"
            />
          </aside>
        </div>
      </div>
    </main>

    <!-- Connection Status -->
    <div class="connection-status" :class="{ connected: isConnected }">
      {{ isConnected ? '🟢 Connected' : '🔴 Disconnected' }}
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted, watch, computed } from 'vue' // ADD computed import
import { useProjectStore } from './stores/project-store'
import AgentStatus from './components/AgentStatus.vue'
import ChatInterface from './components/ChatInterface.vue'
import LivePreview from './components/LivePreview.vue'
import FileExplorer from './components/FileExplorer.vue'

export default {
  name: 'App',
  components: {
    AgentStatus,
    ChatInterface,
    LivePreview,
    FileExplorer
  },
  setup() {
    const projectStore = useProjectStore()
    
    const isConnected = ref(false)
    const isLoading = ref(false)
    const previewUrl = ref('')
    
    // Direct reactive references to store state
    const messages = ref(projectStore.messages)
    const activeAgent = ref(projectStore.activeAgent)
    const projectName = ref(projectStore.projectName)
    const projectId = ref(projectStore.projectId)
    const generatedFiles = ref(projectStore.generatedFiles)
    
    // Watch individual store properties for changes
    watch(
      () => projectStore.messages,
      (newMessages) => {
        messages.value = newMessages
      }
    )

    watch(
      () => projectStore.activeAgent,
      (newAgent) => {
        activeAgent.value = newAgent
      }
    )
    
    watch(
      () => projectStore.projectName,
      (newName) => {
        projectName.value = newName
      }
    )
    
    watch(
      () => projectStore.projectId,
      (newId) => {
        projectId.value = newId
      }
    )
    
    watch(
      () => projectStore.generatedFiles,
      (newFiles) => {
        generatedFiles.value = newFiles
      }
    )
    
    watch(
      () => projectStore.previewUrl,
      (newUrl) => {
        previewUrl.value = newUrl
      }
    )
    
    watch(
      () => projectStore.isConnected,
      (newStatus) => {
        isConnected.value = newStatus
      }
    )

    const sendMessage = async (message) => {
      isLoading.value = true
      await projectStore.sendMessage(message)
      isLoading.value = false
    }

    const createNewProject = async (projectName) => {
      console.log('🎯 App.vue: createNewProject called with:', projectName)
      await projectStore.createNewProject(projectName)
      console.log('✅ App.vue: createNewProject completed')
    }

    // 🚨 NEW: Generation-related methods
    // In App.vue setup() function - REPLACE the existing methods:
    const generateCode = async (projectId) => {
      console.log('🎯 App.vue: generateCode called for project:', projectId)
      isLoading.value = true
      try {
        await projectStore.generateCode(projectId)
      } catch (error) {
        console.error('❌ Generation failed:', error)
      } finally {
        isLoading.value = false
      }
    }
  
  const generationStatus = computed(() => projectStore.generationStatus)

  const checkGenerationStatus = async (projectId) => {
    console.log('🔍 App.vue: Checking generation status for project:', projectId)
    await projectStore.checkGenerationStatus(projectId)
  }

    onMounted(() => {
      console.log('🚀 App.vue: Connecting to store...')
      projectStore.connect()
    })

    onUnmounted(() => {
      projectStore.disconnect()
    })

    return {
      messages,
      activeAgent,
      projectName,
      projectId,
      previewUrl,
      generatedFiles,
      isConnected,
      isLoading,
      generationStatus,
      sendMessage,
      createNewProject,
      generateCode, // 🚨 ADD this
      checkGenerationStatus // 🚨 ADD this
    }
  }
}
</script>

<style scoped>
#app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.app-header {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
  padding: 1rem 0;
  color: white;
}

.header-content {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 2rem;
  text-align: center;
}

.header-content h1 {
  font-size: 2.5rem;
  margin-bottom: 0.5rem;
  font-weight: 700;
}

.header-content p {
  opacity: 0.9;
  font-size: 1.1rem;
}

.app-main {
  flex: 1;
  padding: 2rem 0;
}

.container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 1rem;
}

.layout {
  display: grid;
  grid-template-columns: 300px 1fr 400px;
  gap: 2rem;
  height: 80vh;
}

.sidebar {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.chat-section {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.preview-section {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.connection-status {
  position: fixed;
  bottom: 1rem;
  right: 1rem;
  padding: 0.5rem 1rem;
  border-radius: 20px;
  background: #ef4444;
  color: white;
  font-size: 0.9rem;
  font-weight: 600;
}

.connection-status.connected {
  background: #10b981;
}

@media (max-width: 1200px) {
  .layout {
    grid-template-columns: 250px 1fr;
  }
  
  .preview-section {
    display: none;
  }
}

@media (max-width: 768px) {
  .layout {
    grid-template-columns: 1fr;
    height: auto;
  }
  
  .sidebar {
    order: 2;
  }
}
</style>