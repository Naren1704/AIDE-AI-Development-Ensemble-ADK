<template>
  <div class="live-preview">
    <!-- Preview Header -->
    <div class="preview-header">
      <h3>🌐 Live Preview</h3>
      <div class="preview-controls">
        <button 
          @click="refreshPreview" 
          class="control-btn"
          :disabled="!previewUrl || isLoading"
          title="Refresh Preview"
        >
          🔄
        </button>
        <button 
          @click="openInNewTab" 
          class="control-btn"
          :disabled="!previewUrl"
          title="Open in New Tab"
        >
          ↗️
        </button>
        <button 
          @click="toggleFullscreen" 
          class="control-btn"
          :disabled="!previewUrl"
          title="Toggle Fullscreen"
        >
          {{ isFullscreen ? '⤢' : '⛶' }}
        </button>
      </div>
    </div>

    <!-- Preview Content -->
    <div class="preview-content" :class="{ fullscreen: isFullscreen }">
      <!-- Loading State -->
      <div v-if="!previewUrl" class="preview-placeholder">
        <div class="placeholder-icon">🚀</div>
        <h4>No Preview Available</h4>
        <p>Start a project and generate some code to see the live preview here.</p>
      </div>

      <!-- Loading Indicator -->
      <div v-else-if="isLoading" class="preview-loading">
        <div class="loading-spinner"></div>
        <p>Loading Preview...</p>
      </div>

      <!-- Error State -->
      <div v-else-if="previewError" class="preview-error">
        <div class="error-icon">❌</div>
        <h4>Preview Failed to Load</h4>
        <p>{{ previewError }}</p>
        <button @click="refreshPreview" class="retry-btn">
          Try Again
        </button>
      </div>

      <!-- Preview Frame -->
      <div v-else class="preview-frame-container">
        <!-- Preview Toolbar -->
        <div class="preview-toolbar">
          <div class="url-display">
            <span class="url-icon">🌐</span>
            <span class="url-text">{{ previewUrl }}</span>
          </div>
          <div class="preview-stats">
            <span class="stat">
              <span class="stat-icon">📊</span>
              {{ previewStats.loadTime }}ms
            </span>
            <span class="stat">
              <span class="stat-icon">📅</span>
              {{ previewStats.lastUpdate }}
            </span>
          </div>
        </div>

        <!-- Responsive Controls -->
        <div class="responsive-controls">
          <button 
            v-for="size in responsiveSizes" 
            :key="size.name"
            @click="setPreviewSize(size)"
            :class="['size-btn', { active: currentSize.name === size.name }]"
          >
            {{ size.icon }}
          </button>
        </div>

        <!-- Preview Frame -->
        <div class="preview-wrapper" :style="previewWrapperStyle">
          <iframe
            ref="previewFrame"
            :src="previewUrl"
            :style="previewStyle"
            @load="onPreviewLoad"
            @error="onPreviewError"
            title="Project Preview"
            sandbox="allow-scripts allow-same-origin allow-forms allow-popups"
          ></iframe>
          <div class="preview-overlay" @click="focusPreview"></div>
        </div>
      </div>
    </div>

    <!-- Fullscreen Overlay -->
    <div 
      v-if="isFullscreen" 
      class="fullscreen-overlay"
      @click="toggleFullscreen"
    >
      <button class="close-fullscreen">✕</button>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted } from 'vue'

export default {
  name: 'LivePreview',
  props: {
    previewUrl: String,
    projectId: String
  },
  
  setup(props) {
    const previewFrame = ref(null)
    const isLoading = ref(false)
    const previewError = ref('')
    const isFullscreen = ref(false)
    const currentSize = ref({ name: 'desktop', width: '100%', height: '100%', icon: '💻' })
    const loadStartTime = ref(0)
    const previewTimeout = ref(null)

    const previewStats = ref({
      loadTime: 0,
      lastUpdate: new Date().toLocaleTimeString()
    })

    const responsiveSizes = ref([
      { name: 'mobile', width: '375px', height: '667px', icon: '📱' },
      { name: 'tablet', width: '768px', height: '1024px', icon: '📟' },
      { name: 'desktop', width: '100%', height: '100%', icon: '💻' }
    ])

    const previewStyle = computed(() => ({
      width: currentSize.value.width,
      height: currentSize.value.height,
      border: 'none',
      borderRadius: currentSize.value.name === 'desktop' ? '0' : '8px',
      boxShadow: currentSize.value.name === 'desktop' ? 'none' : '0 4px 12px rgba(0, 0, 0, 0.1)'
    }))

    const previewWrapperStyle = computed(() => ({
      justifyContent: currentSize.value.name === 'desktop' ? 'flex-start' : 'center',
      alignItems: currentSize.value.name === 'desktop' ? 'flex-start' : 'center'
    }))

    const refreshPreview = () => {
      if (!props.previewUrl) return
      
      isLoading.value = true
      previewError.value = ''
      loadStartTime.value = Date.now()
      
      // Add timeout for preview loading
      previewTimeout.value = setTimeout(() => {
        if (isLoading.value) {
          isLoading.value = false
          previewError.value = 'Preview loading timeout. The development server might be taking too long to start.'
          console.error('Preview loading timeout')
        }
      }, 15000)
      
      if (previewFrame.value) {
        previewFrame.value.src = props.previewUrl + '?t=' + Date.now()
      }
    }

    const openInNewTab = () => {
      if (props.previewUrl) {
        window.open(props.previewUrl, '_blank')
      }
    }

    const toggleFullscreen = () => {
      isFullscreen.value = !isFullscreen.value
    }

    const setPreviewSize = (size) => {
      currentSize.value = size
    }

    const onPreviewLoad = () => {
      // Clear timeout if preview loads successfully
      if (previewTimeout.value) {
        clearTimeout(previewTimeout.value)
        previewTimeout.value = null
      }
      
      isLoading.value = false
      previewError.value = ''
      previewStats.value.loadTime = Date.now() - loadStartTime.value
      previewStats.value.lastUpdate = new Date().toLocaleTimeString()
    }

    const onPreviewError = () => {
      // Clear timeout on error
      if (previewTimeout.value) {
        clearTimeout(previewTimeout.value)
        previewTimeout.value = null
      }
      
      isLoading.value = false
      previewError.value = 'Failed to load the preview. The development server might not be running or the project files may be missing.'
      
      // Auto-retry after 3 seconds
      setTimeout(() => {
        if (props.previewUrl && !isLoading.value) {
          console.log('🔄 Auto-retrying preview...')
          refreshPreview()
        }
      }, 3000)
    }

    const focusPreview = () => {
      if (previewFrame.value) {
        previewFrame.value.focus()
      }
    }

    // Auto-refresh when previewUrl changes
    onMounted(() => {
      if (props.previewUrl) {
        refreshPreview()
      }
    })

    // Handle escape key for fullscreen
    const handleKeydown = (event) => {
      if (event.key === 'Escape' && isFullscreen.value) {
        toggleFullscreen()
      }
    }

    onMounted(() => {
      document.addEventListener('keydown', handleKeydown)
    })

    onUnmounted(() => {
      if (previewTimeout.value) {
        clearTimeout(previewTimeout.value)
      }
      document.removeEventListener('keydown', handleKeydown)
    })

    return {
      previewFrame,
      isLoading,
      previewError,
      isFullscreen,
      currentSize,
      previewStats,
      responsiveSizes,
      previewStyle,
      previewWrapperStyle,
      refreshPreview,
      openInNewTab,
      toggleFullscreen,
      setPreviewSize,
      onPreviewLoad,
      onPreviewError,
      focusPreview
    }
  }
}
</script>

<style scoped>
.live-preview {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.preview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid #e2e8f0;
  background: #f8fafc;
}

.preview-header h3 {
  margin: 0;
  color: #1e293b;
  font-size: 1.1rem;
}

.preview-controls {
  display: flex;
  gap: 0.5rem;
}

.control-btn {
  background: white;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  padding: 0.5rem;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 1rem;
}

.control-btn:hover:not(:disabled) {
  background: #3b82f6;
  color: white;
  border-color: #3b82f6;
}

.control-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.preview-content {
  flex: 1;
  position: relative;
  background: #f8fafc;
}

.preview-content.fullscreen {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 1000;
  background: white;
}

.preview-placeholder,
.preview-loading,
.preview-error {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  padding: 2rem;
  text-align: center;
  color: #6b7280;
}

.placeholder-icon,
.error-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
  opacity: 0.5;
}

.preview-loading h4,
.preview-error h4 {
  margin: 0 0 0.5rem 0;
  color: #374151;
}

.preview-loading p,
.preview-error p {
  margin: 0;
  font-size: 0.9rem;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #e2e8f0;
  border-top: 3px solid #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.retry-btn {
  background: #3b82f6;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  cursor: pointer;
  margin-top: 1rem;
  font-weight: 600;
}

.retry-btn:hover {
  background: #2563eb;
}

.preview-frame-container {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.preview-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1rem;
  background: white;
  border-bottom: 1px solid #e2e8f0;
}

.url-display {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.8rem;
  color: #6b7280;
  background: #f8fafc;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
}

.url-text {
  font-family: monospace;
}

.preview-stats {
  display: flex;
  gap: 1rem;
  font-size: 0.8rem;
  color: #6b7280;
}

.stat {
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.stat-icon {
  font-size: 0.9rem;
}

.responsive-controls {
  display: flex;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.75rem;
  background: #f8fafc;
  border-bottom: 1px solid #e2e8f0;
}

.size-btn {
  background: white;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  padding: 0.5rem;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 1rem;
}

.size-btn:hover {
  border-color: #3b82f6;
}

.size-btn.active {
  background: #3b82f6;
  color: white;
  border-color: #3b82f6;
}

.preview-wrapper {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 1rem;
  background: #f1f5f9;
  position: relative;
  overflow: auto;
}

.preview-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  cursor: pointer;
}

.fullscreen-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.8);
  z-index: 999;
  display: flex;
  align-items: flex-start;
  justify-content: flex-end;
  padding: 1rem;
}

.close-fullscreen {
  background: white;
  border: none;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  cursor: pointer;
  font-size: 1.2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.close-fullscreen:hover {
  background: #f1f5f9;
}

/* Mobile responsiveness */
@media (max-width: 768px) {
  .preview-toolbar {
    flex-direction: column;
    gap: 0.5rem;
    align-items: flex-start;
  }
  
  .preview-stats {
    align-self: flex-end;
  }
}
</style>