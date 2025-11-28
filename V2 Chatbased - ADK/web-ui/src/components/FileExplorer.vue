<template>
  <div class="file-explorer">
    <!-- Header -->
    <div class="explorer-header">
      <h3>📁 Generated Files</h3>
      <div class="header-actions">
        <button 
          @click="refreshFiles" 
          class="action-btn"
          title="Refresh Files"
        >
          🔄
        </button>
        <button 
          @click="toggleView" 
          class="action-btn"
          title="Toggle View"
        >
          {{ isTreeView ? '📄' : '🌳' }}
        </button>
      </div>
    </div>

    <!-- File Stats -->
    <div v-if="files.length > 0" class="file-stats">
      <div class="stat-item">
        <span class="stat-label">Total Files:</span>
        <span class="stat-value">{{ files.length }}</span>
      </div>
      <div class="stat-item">
        <span class="stat-label">Total Size:</span>
        <span class="stat-value">{{ totalSize }}</span>
      </div>
    </div>

    <!-- Empty State -->
    <div v-if="!files || files.length === 0" class="empty-state">
      <div class="empty-icon">📁</div>
      <h4>No Files Generated</h4>
      <p>Generated files will appear here once you start building your project.</p>
    </div>

    <!-- Tree View -->
    <div v-else-if="isTreeView" class="tree-view">
      <div class="tree-container">
        <FileTreeNode
          v-for="file in organizedFiles"
          :key="file.path"
          :node="file"
          :depth="0"
          @file-select="onFileSelect"
        />
      </div>
    </div>

    <!-- List View -->
    <div v-else class="list-view">
      <div class="file-list">
        <div 
          v-for="file in files" 
          :key="file.path"
          :class="['file-item', { selected: selectedFile?.path === file.path }]"
          @click="selectFile(file)"
        >
          <div class="file-icon">{{ getFileIcon(file.path) }}</div>
          <div class="file-info">
            <div class="file-name">{{ getFileName(file.path) }}</div>
            <div class="file-path">{{ file.path }}</div>
            <div class="file-meta">
              <span class="file-size">{{ formatFileSize(file.size) }}</span>
              <span class="file-type">{{ getFileType(file.path) }}</span>
            </div>
          </div>
          <div class="file-actions">
            <button @click.stop="previewFile(file)" class="file-action-btn" title="Preview">
              👁️
            </button>
            <button @click.stop="downloadFile(file)" class="file-action-btn" title="Download">
              📥
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- File Preview Modal -->
    <div v-if="showPreviewModal" class="preview-modal-overlay" @click="closePreviewModal">
      <div class="preview-modal" @click.stop>
        <div class="modal-header">
          <h4>📄 {{ previewFile?.path }}</h4>
          <button @click="closePreviewModal" class="close-btn">✕</button>
        </div>
        <div class="modal-content">
          <div class="file-preview">
            <pre v-if="isTextFile(previewFile)">{{ previewFile.content }}</pre>
            <div v-else class="binary-file">
              <div class="binary-icon">📦</div>
              <p>Binary file - cannot preview</p>
              <button @click="downloadFile(previewFile)" class="download-btn">
                Download File
              </button>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button @click="downloadFile(previewFile)" class="btn-primary">
            📥 Download
          </button>
          <button @click="closePreviewModal" class="btn-secondary">
            Close
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'

// File Tree Node Component
const FileTreeNode = {
  name: 'FileTreeNode',
  props: {
    node: Object,
    depth: Number
  },
  emits: ['file-select'],
  setup(props, { emit }) {
    const isExpanded = ref(true)

    const toggleExpand = () => {
      if (props.node.children) {
        isExpanded.value = !isExpanded.value
      }
    }

    const handleFileSelect = (file) => {
      emit('file-select', file)
    }

    const getFileIcon = (name) => {
      if (!name) return '📁'
      if (name.includes('.')) {
        const ext = name.split('.').pop()
        const icons = {
          'html': '🌐', 'css': '🎨', 'js': '📜', 'json': '📋',
          'md': '📝', 'py': '🐍', 'txt': '📄', 'xml': '📊'
        }
        return icons[ext] || '📄'
      }
      return '📁'
    }

    return {
      isExpanded,
      toggleExpand,
      handleFileSelect,
      getFileIcon
    }
  },
  template: `
    <div class="tree-node">
      <div 
        class="node-line"
        :style="{ paddingLeft: depth * 16 + 'px' }"
        @click="toggleExpand"
      >
        <span class="expand-icon">
          {{ node.children ? (isExpanded ? '📂' : '📁') : getFileIcon(node.name) }}
        </span>
        <span class="node-name">{{ node.name }}</span>
        <span v-if="node.children" class="node-count">({{ node.children.length }})</span>
      </div>
      
      <div v-if="node.children && isExpanded" class="node-children">
        <FileTreeNode
          v-for="child in node.children"
          :key="child.path"
          :node="child"
          :depth="depth + 1"
          @file-select="handleFileSelect"
        />
      </div>
    </div>
  `
}

export default {
  name: 'FileExplorer',
  components: {
    FileTreeNode
  },
  props: {
    files: Array,
    projectId: String
  },
  
  setup(props) {
    console.log('📁 FileExplorer received files:', props.files)
    const isTreeView = ref(true)
    const selectedFile = ref(null)
    const showPreviewModal = ref(false)
    const previewFile = ref(null)

    const totalSize = computed(() => {
      const totalBytes = props.files.reduce((sum, file) => sum + (file.size || 0), 0)
      return formatFileSize(totalBytes)
    })

    const organizedFiles = computed(() => {
      // Use project root instead of forcing "src"
      const root = { name: 'project', path: '', children: [] }
      const actualFiles = props.files.filter(file => !file.path.endsWith('/'))
      actualfiles.forEach(file => {
        const parts = file.path.split('/')
        let current = root
        
        for (let i = 0; i < parts.length; i++) {
            const part = parts[i]
            const isFile = i === parts.length - 1
            
            if (!current.children) {
                current.children = []
            }
            
            let child = current.children.find(c => c.name === part)
            
            if (!child) {
                child = {
                    name: part,
                    path: parts.slice(0, i + 1).join('/'),
                    isFile: isFile,
                    ...(isFile ? file : {})
                }
                current.children.push(child)
            }
            
            current = child
        }
      })
      console.log('🌳 Final organized tree:', root)
      return [root]
    })

    const toggleView = () => {
      isTreeView.value = !isTreeView.value
    }

    const refreshFiles = () => {
      // This would refresh the file list from the server
      console.log('Refreshing files...')
    }

    const selectFile = (file) => {
      selectedFile.value = file
    }

    const onFileSelect = (file) => {
      selectedFile.value = file
      previewFile.value = file
      showPreviewModal.value = true
    }

    const previewFileAction = (file) => {
      previewFile.value = file
      showPreviewModal.value = true
    }

    const downloadFile = (file) => {
      // Create and download the file
      const blob = new Blob([file.content], { type: 'text/plain' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = file.path.split('/').pop()
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)
    }

    const closePreviewModal = () => {
      showPreviewModal.value = false
      previewFile.value = null
    }

    const getFileIcon = (filePath) => {
      const ext = filePath.split('.').pop()
      const icons = {
        'html': '🌐', 'htm': '🌐',
        'css': '🎨',
        'js': '📜', 'jsx': '⚛️', 'ts': '📘', 'tsx': '⚛️',
        'json': '📋',
        'md': '📝',
        'py': '🐍',
        'txt': '📄',
        'xml': '📊',
        'yml': '⚙️', 'yaml': '⚙️',
        'gitignore': '👁️',
        'license': '📜'
      }
      return icons[ext] || '📄'
    }

    const getFileName = (filePath) => {
      return filePath.split('/').pop()
    }

    const getFileType = (filePath) => {
      const ext = filePath.split('.').pop()
      return ext.toUpperCase() + ' file'
    }

    const formatFileSize = (bytes) => {
      if (!bytes) return '0 B'
      const sizes = ['B', 'KB', 'MB', 'GB']
      const i = Math.floor(Math.log(bytes) / Math.log(1024))
      return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i]
    }

    const isTextFile = (file) => {
      if (!file) return false
      const textExtensions = ['html', 'css', 'js', 'json', 'md', 'txt', 'py', 'xml', 'yml', 'yaml']
      const ext = file.path.split('.').pop()
      return textExtensions.includes(ext)
    }

    return {
      isTreeView,
      selectedFile,
      showPreviewModal,
      previewFile,
      totalSize,
      organizedFiles,
      toggleView,
      refreshFiles,
      selectFile,
      onFileSelect,
      previewFile: previewFileAction,
      downloadFile,
      closePreviewModal,
      getFileIcon,
      getFileName,
      getFileType,
      formatFileSize,
      isTextFile
    }
  }
}
</script>

<style scoped>
.file-explorer {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.explorer-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid #e2e8f0;
  background: #f8fafc;
}

.explorer-header h3 {
  margin: 0;
  color: #1e293b;
  font-size: 1.1rem;
}

.header-actions {
  display: flex;
  gap: 0.5rem;
}

.action-btn {
  background: white;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  padding: 0.5rem;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 1rem;
}

.action-btn:hover {
  background: #3b82f6;
  color: white;
  border-color: #3b82f6;
}

.file-stats {
  display: flex;
  gap: 1rem;
  padding: 0.75rem 1.5rem;
  background: #f0f9ff;
  border-bottom: 1px solid #e2e8f0;
}

.stat-item {
  display: flex;
  gap: 0.5rem;
  font-size: 0.875rem;
}

.stat-label {
  color: #6b7280;
  font-weight: 500;
}

.stat-value {
  color: #1e293b;
  font-weight: 600;
}

.empty-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  text-align: center;
  color: #6b7280;
}

.empty-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
  opacity: 0.5;
}

.empty-state h4 {
  margin: 0 0 0.5rem 0;
  color: #374151;
}

.empty-state p {
  margin: 0;
  font-size: 0.9rem;
}

.tree-view,
.list-view {
  flex: 1;
  overflow: auto;
  padding: 0.5rem;
}

.tree-container {
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 0.875rem;
}

.tree-node {
  user-select: none;
}

.node-line {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.25rem 0.5rem;
  cursor: pointer;
  border-radius: 4px;
  transition: background 0.2s;
}

.node-line:hover {
  background: #f1f5f9;
}

.expand-icon {
  font-size: 1rem;
  width: 16px;
  text-align: center;
}

.node-name {
  color: #1e293b;
}

.node-count {
  color: #6b7280;
  font-size: 0.75rem;
}

.node-children {
  margin-left: 8px;
  border-left: 1px solid #e2e8f0;
}

.file-list {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.file-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
  border: 1px solid transparent;
}

.file-item:hover {
  background: #f8fafc;
  border-color: #e2e8f0;
}

.file-item.selected {
  background: #eff6ff;
  border-color: #3b82f6;
}

.file-icon {
  font-size: 1.25rem;
  width: 24px;
  text-align: center;
  flex-shrink: 0;
}

.file-info {
  flex: 1;
  min-width: 0;
}

.file-name {
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 0.25rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.file-path {
  font-size: 0.75rem;
  color: #6b7280;
  margin-bottom: 0.25rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.file-meta {
  display: flex;
  gap: 1rem;
  font-size: 0.7rem;
  color: #9ca3af;
}

.file-actions {
  display: flex;
  gap: 0.25rem;
  opacity: 0;
  transition: opacity 0.2s;
}

.file-item:hover .file-actions {
  opacity: 1;
}

.file-action-btn {
  background: white;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  padding: 0.25rem;
  cursor: pointer;
  font-size: 0.75rem;
  transition: all 0.2s;
}

.file-action-btn:hover {
  background: #3b82f6;
  color: white;
  border-color: #3b82f6;
}

/* Preview Modal */
.preview-modal-overlay {
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
  padding: 2rem;
}

.preview-modal {
  background: white;
  border-radius: 12px;
  width: 90%;
  max-width: 800px;
  max-height: 80vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid #e2e8f0;
}

.modal-header h4 {
  margin: 0;
  color: #1e293b;
  font-family: monospace;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  padding: 0.25rem;
  border-radius: 4px;
}

.close-btn:hover {
  background: #f1f5f9;
}

.modal-content {
  flex: 1;
  overflow: auto;
  padding: 0;
}

.file-preview {
  height: 100%;
}

.file-preview pre {
  margin: 0;
  padding: 1.5rem;
  background: #1e293b;
  color: #e2e8f0;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 0.875rem;
  line-height: 1.5;
  white-space: pre-wrap;
  height: 400px;
  overflow: auto;
}

.binary-file {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem;
  color: #6b7280;
}

.binary-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
  opacity: 0.5;
}

.download-btn {
  background: #3b82f6;
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 6px;
  cursor: pointer;
  margin-top: 1rem;
  font-weight: 600;
}

.download-btn:hover {
  background: #2563eb;
}

.modal-footer {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  padding: 1.5rem;
  border-top: 1px solid #e2e8f0;
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

.btn-primary:hover {
  background: #059669;
}

.btn-secondary {
  background: #f1f5f9;
  color: #475569;
}

.btn-secondary:hover {
  background: #e2e8f0;
}

/* Scrollbar Styling */
.tree-view::-webkit-scrollbar,
.list-view::-webkit-scrollbar,
.file-preview pre::-webkit-scrollbar {
  width: 6px;
}

.tree-view::-webkit-scrollbar-track,
.list-view::-webkit-scrollbar-track,
.file-preview pre::-webkit-scrollbar-track {
  background: #f1f5f9;
}

.tree-view::-webkit-scrollbar-thumb,
.list-view::-webkit-scrollbar-thumb,
.file-preview pre::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 3px;
}

.tree-view::-webkit-scrollbar-thumb:hover,
.list-view::-webkit-scrollbar-thumb:hover,
.file-preview pre::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}
</style>