import { defineStore } from 'pinia'
import { agentService } from '../services/agent-service'
import JSZip from 'jszip'
export const useProjectStore = defineStore('project', {
  state: () => ({
    // Connection
    isConnected: false,
    
    // Project State
    projectId: null,
    projectName: '',
    activeAgent: 'requirements_evolver',
    
    // Messages
    messages: [],
    
    // Generated Content
    previewUrl: '',
    generatedFiles: [],
    
    // UI State
    isLoading: false,
    
    // 🚨 NEW: Generation Status State
    generationStatus: {
      isReady: false,
      requirementsMet: false,
      agentsContributed: [],
      missingRequirements: []
    }
  }),

  actions: {
    // Connection Management
    connect() {
      const store = this // Capture store reference
      
      agentService.connect({
        onOpen: () => {
          store.isConnected = true
          console.log('🟢 Connected to AIDE server')
        },
        
        onMessage: (data) => {
          store.handleServerMessage(data)
        },
        
        onClose: () => {
          store.isConnected = false
          console.log('🔴 Disconnected from AIDE server')
        },
        
        onError: (error) => {
          console.error('WebSocket error:', error)
          store.isConnected = false
        }
      })
    },
    
    disconnect() {
      agentService.disconnect()
      this.isConnected = false
    },
    
    // 🚨 NEW: Generation Management Methods
    async generateCode(projectId) {
      if (!this.isConnected) {
        alert('Not connected to server. Please check if the backend is running.')
        return
      }
    
      console.log('🚀 project-store: Sending generate_code for project:', projectId)
    
    // ENHANCED: Set loading state with timeout protection
      this.isLoading = true
      console.log('🔄 Set isLoading to true for code generation')
    
    // SAFETY: Auto-reset loading state after timeout (120 seconds)
      const loadingTimeout = setTimeout(() => {
        if (this.isLoading) {
            console.warn('⏰ Generation timeout - resetting loading state')
            this.isLoading = false
            this.messages.push({
                role: 'system',
                content: '⏰ Generation timeout. Please wait if the project is big or try again.',
                timestamp: new Date().toISOString(),
                isError: true
            })
        }
      }, 240000)

      try {
        await agentService.send({
            type: 'generate_code',
            project_id: projectId || this.projectId
        })
        
        this.messages.push({
            role: 'system',
            content: '🚀 Starting code generation...',
            timestamp: new Date().toISOString()
        })
        
      } catch (error) {
        console.error('❌ Failed to send generate_code:', error)
        
        // CRITICAL: Reset loading state on send failure
        this.isLoading = false
        clearTimeout(loadingTimeout)
        console.log('🔄 Reset isLoading after send failure')
        
        this.messages.push({
            role: 'system',
            content: `❌ Failed to start generation: ${error.message}`,
            timestamp: new Date().toISOString(),
            isError: true
        })
      }
    },
    
    async checkGenerationStatus(projectId) {
      if (!this.isConnected) {
        console.warn('Not connected to server')
        return
      }
      
      console.log('🔍 project-store: Checking generation status for project:', projectId)
      
      try {
        await agentService.send({
          type: 'check_generation_status',
          project_id: projectId || this.projectId
        })
      } catch (error) {
        console.error('❌ Failed to check generation status:', error)
      }
    },
    
    // Project Management
    async createNewProject(projectName) {
      if (!this.isConnected) {
        alert('Not connected to server. Please check if the backend is running.')
        return
      }
      
      this.resetProject()
      this.projectName = projectName
      
      try {
        await agentService.send({
          type: 'new_project',
          project_name: projectName
        })
      } catch (error) {
        console.error('❌ Failed to send project creation:', error)
        this.messages.push({
          role: 'system',
          content: `❌ Failed to create project: ${error.message}`,
          timestamp: new Date().toISOString(),
          isError: true
        })
      }
    },
    
    resetProject() {
      this.projectId = null
      this.projectName = ''
      this.messages = []
      this.previewUrl = ''
      this.generatedFiles = []
      this.activeAgent = 'requirements_evolver'
      // 🚨 NEW: Reset generation status
      this.generationStatus = {
        isReady: false,
        requirementsMet: false,
        agentsContributed: [],
        missingRequirements: []
      }
    },
    
    _triggerUIUpdate() {
      // Force Vue reactivity updates
      this.generatedFiles = [...this.generatedFiles]
      this.generationStatus = {...this.generationStatus}
    
      // Optional: Add a small delay to ensure DOM updates
      setTimeout(() => {
        console.log('🔄 UI update triggered')
      }, 100)
    },

    // Message Handling
    async sendMessage(message) {
      if (!this.projectId) {
        await this.createNewProject('New Project')
        // Wait a bit for project creation
        await new Promise(resolve => setTimeout(resolve, 1000))
      }
      
      // Add user message to UI immediately
      this.messages.push({
        role: 'user',
        content: message,
        timestamp: new Date().toISOString()
      })
      
      try {
        await agentService.send({
          type: 'user_message',
          project_id: this.projectId,
          message: message
        })
      } catch (error) {
        console.error('❌ Failed to send message:', error)
        this.messages.push({
          role: 'system',
          content: `❌ Failed to send message: ${error.message}`,
          timestamp: new Date().toISOString(),
          isError: true
        })
      }
    },
    
    handleServerMessage(data) {
      console.log('📨 Server message:', data)
      switch (data.type) {
        case 'project_created':
            this.handleProjectCreated(data)
            break
            
        case 'agent_response':
            this.handleAgentResponse(data)
            break
            
        case 'code_generated':
            this.handleCodeGenerated(data)
            break
            
        case 'code_generation_error': // NEW: Handle generation errors specifically
            this.handleCodeGenerationError(data)
            break
            
        case 'preview_url':
            this.handlePreviewUrl(data)
            break
            
        case 'generation_status':
            this.handleGenerationStatus(data)
            break
            
        case 'generation_started': // NEW: Handle generation start confirmation
            console.log('🚀 Generation started confirmed by server')
            break
            
        case 'error':
            this.handleError(data)
            // CRITICAL: Reset loading state on any error
            this.isLoading = false
            console.log('🔄 Reset isLoading after general error')
            break
            
        default:
            console.warn('Unknown message type:', data.type)
      }
    },
    
    handleProjectCreated(data) {
      this.projectId = data.project_id
      this.projectName = data.project_name
      
      this.messages.push({
        role: 'system',
        content: `Project "${data.project_name}" created successfully!`,
        timestamp: new Date().toISOString()
      })
      
      console.log('✅ Project created in store:', this.projectId)
    },
    
    handleAgentResponse(data) {
      this.activeAgent = data.agent
      
      this.messages.push({
        role: 'agent',
        content: data.message,
        agent: data.agent,
        timestamp: new Date().toISOString()
      })
      
      // 🚨 NEW: Auto-check generation status after each agent response
      if (this.projectId) {
        setTimeout(() => {
          this.checkGenerationStatus(this.projectId)
        }, 500)
      }
    },
    
    // 🚨 NEW: Handle generation status updates
    handleGenerationStatus(data) {
      console.log('📊 Generation status update:', data)
    
      this.generationStatus = {
        canGenerate: data.can_generate || false,
        substantialAgents: data.substantial_agents || 0,
        agentContributions: data.agent_contributions || [],
        hasMinimalRequirements: data.has_minimal_requirements || false,
        message: data.message || ''
      }
    
      console.log('📊 Updated generation status:', this.generationStatus)
    
      // ENHANCED: Ensure loading state is reset if generation is complete
      if (this.isLoading && data.status === 'completed') {
        this.isLoading = false
        console.log('🔄 Reset isLoading based on generation status completion')
      }
    },

    
    // ENHANCED: Handle code generation completion with proper state reset
    handleCodeGenerated(data) {
      console.log('🔴 DEBUG - Raw code_generated data:', JSON.stringify(data, null, 2))
      console.log('🔴 DEBUG - Files array:', data.files)
      console.log('🔴 DEBUG - Files type:', typeof data.files)
      console.log('🔴 DEBUG - Files length:', data.files?.length)
      console.log('📦 Raw code generated data:', data)

      // CRITICAL: Reset loading state immediately upon generation completion
      this.isLoading = false
      console.log('🔄 Reset isLoading state after code generation')

      // Ensure files array exists and has proper structure
      this.generatedFiles = Array.isArray(data.files) ? data.files : []
      this.previewUrl = data.preview_url || ''

      console.log(`📁 Processing ${this.generatedFiles.length} files`)

      // Enhanced file data validation
      this.generatedFiles = this.generatedFiles.map((file, index) => {
        const filePath = file.path || `file-${index}.txt`
        return {
            path: filePath,
            content: file.content || '',
            size: file.size || (file.content ? file.content.length : 0),
            type: file.type || this._inferFileType(filePath),
            icon: file.icon || this._getFileIcon(filePath)
        }
      })

      const fileCount = this.generatedFiles.length
      const totalSize = this.generatedFiles.reduce((sum, f) => sum + (f.size || 0), 0)

      this.messages.push({
        role: 'system',
        content: `✅ Code generated! ${fileCount} files created (${this._formatFileSize(totalSize)}). ${this.previewUrl ? 'Preview available.' : 'Preview not available.'}`,
        timestamp: new Date().toISOString()
      })

      console.log('📁 Final processed files:', this.generatedFiles)
      console.log('🌐 Preview URL:', this.previewUrl)
    
      // ENHANCED: Force UI refresh and state consistency
      this._triggerUIUpdate()
    },

    // NEW: Enhanced error handling for generation failures
    handleCodeGenerationError(data) {
      console.error('❌ Code generation failed:', data)
    
      // CRITICAL: Reset loading state on error
      this.isLoading = false
      console.log('🔄 Reset isLoading state after generation error')
    
      this.messages.push({
        role: 'system',
        content: `❌ Code generation failed: ${data.error || 'Unknown error'}`,
        timestamp: new Date().toISOString(),
        isError: true
      })
    
    this._triggerUIUpdate()
},

    _getFileIcon(filePath) {
      if (!filePath) return '📄'
      const ext = filePath.split('.').pop().toLowerCase()
      const iconMap = {
        'py': '🐍', 'html': '🌐', 'css': '🎨', 'js': '📜',
        'json': '📋', 'md': '📝', 'txt': '📄'
      }
      return iconMap[ext] || '📄'
    },
    
    _inferFileType(filePath) {
      if (!filePath) return 'text'
      const ext = filePath.split('.').pop().toLowerCase()
      const typeMap = {
        'js': 'javascript', 'vue': 'vue', 'css': 'stylesheet',
        'html': 'html', 'json': 'json', 'md': 'markdown'
      }
      return typeMap[ext] || 'text'
    },

    _formatFileSize(bytes) {
      if (!bytes) return '0 B'
      const sizes = ['B', 'KB', 'MB', 'GB']
      const i = Math.floor(Math.log(bytes) / Math.log(1024))
      return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i]
    }, 

    handlePreviewUrl(data) {
      this.previewUrl = data.preview_url
    },
    
    handleError(data) {
      // CRITICAL: Reset loading state on any error
      this.isLoading = false
      console.log('🔄 Reset isLoading in error handler')
    
      this.messages.push({
        role: 'system',
        content: `❌ Error: ${data.message}`,
        timestamp: new Date().toISOString(),
        isError: true
      })
    
      this._triggerUIUpdate()
    },

    async requestAutoDebug(projectId, errorLog, problematicFile) {
      await agentService.send({
        type: 'debug_request',
        project_id: projectId,
        error_log: errorLog,
        problematic_file: problematicFile
      })
    },
    // Quick Actions Implementation
    async refreshPreview() {
      if (!this.projectId) {
        this.messages.push({
          role: 'system',
          content: 'No active project to refresh',
          timestamp: new Date().toISOString()
        })
        return
      }
      
      this.messages.push({
        role: 'system', 
        content: '🔄 Refreshing preview...',
        timestamp: new Date().toISOString()
      })
      
      try {
        await agentService.send({
          type: 'get_preview',
          project_id: this.projectId
        })
      } catch (error) {
        console.error('❌ Failed to refresh preview:', error)
      }
    },
    
    async suggestImprovements() {
      if (!this.projectId) {
        this.messages.push({
          role: 'system',
          content: 'No active project to improve',
          timestamp: new Date().toISOString()
        })
        return
      }
      
      await this.sendMessage("Can you suggest any improvements or additional features for my project?")
    },
    
    async exportProject() {
      if (!this.projectId) {
        this.messages.push({
            role: 'system',
            content: 'No active project to export',
            timestamp: new Date().toISOString()
        })
        return
      }

      try {
        console.log('📦 Starting project export for:', this.projectId)
        
        // Show export started message
        this.messages.push({
            role: 'system',
            content: '📦 Preparing project export...',
            timestamp: new Date().toISOString()
        })

        // Create a zip file with all generated files
        const zip = new JSZip()
        
        // Add all generated files to the zip
        this.generatedFiles.forEach(file => {
            if (file.content && file.path) {
                zip.file(file.path, file.content)
                console.log(`📁 Added to zip: ${file.path}`)
            }
        })

        // Generate zip content
        const zipContent = await zip.generateAsync({
            type: 'blob',
            compression: 'DEFLATE',
            compressionOptions: { level: 6 }
        })

        // Create download link
        const url = URL.createObjectURL(zipContent)
        const a = document.createElement('a')
        a.href = url
        a.download = `${this.projectName || 'project'}-${this.projectId}.zip`
        
        // Trigger download
        document.body.appendChild(a)
        a.click()
        document.body.removeChild(a)
        
        // Clean up
        URL.revokeObjectURL(url)

        // Success message
        this.messages.push({
            role: 'system',
            content: `✅ Project exported successfully! Downloaded as ${a.download}`,
            timestamp: new Date().toISOString()
        })

        console.log('📦 Project export completed successfully')

        } catch (error) {
        console.error('❌ Project export failed:', error)
        
        this.messages.push({
            role: 'system',
            content: `❌ Export failed: ${error.message}`,
            timestamp: new Date().toISOString(),
            isError: true
        })
      }
    },    
    // File Management
    async refreshFiles() {
      if (!this.projectId) return
      
      // This would typically fetch updated file list from server
      this.messages.push({
        role: 'system',
        content: '📁 File list refreshed',
        timestamp: new Date().toISOString()
      })
    }
  }
})