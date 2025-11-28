class AgentService {
  constructor() {
    this.ws = null
    this.messageHandlers = []
    this.reconnectAttempts = 0
    this.maxReconnectAttempts = 5
    this.pingInterval = null
    this.connectionHandlers = null
  }

  connect(handlers) {
    this.connectionHandlers = handlers // Store handlers for reconnection
    
    try {
      this.ws = new WebSocket('ws://localhost:8765')
      
      this.ws.onopen = () => {
        console.log('✅ WebSocket connected - readyState:', this.ws.readyState)
        this.reconnectAttempts = 0
        handlers.onOpen?.()
        
        // Start ping interval to keep connection alive
        this.pingInterval = setInterval(() => {
          if (this.isConnected()) {
            console.log('🏓 Sending ping...')
            this.send({ type: 'ping' })
          }
        }, 30000)
      }
      
      this.ws.onmessage = (event) => {
        console.log('📩 WebSocket message received:', event.data)
        try {
          const data = JSON.parse(event.data)
          
          // Ignore pong messages
          if (data.type !== 'pong') {
            console.log('📨 Processing message:', data.type)
            handlers.onMessage?.(data)
          } else {
            console.log('🏓 Pong received')
          }
        } catch (error) {
          console.error('❌ Error parsing message:', error)
        }
      }
      
      this.ws.onclose = (event) => {
        console.log('🔴 WebSocket closed:', event.code, event.reason)
        
        // Clear ping interval
        if (this.pingInterval) {
          clearInterval(this.pingInterval)
          this.pingInterval = null
        }
        
        handlers.onClose?.(event)
        
        // Attempt reconnection
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
          setTimeout(() => {
            this.reconnectAttempts++
            console.log(`🔄 Reconnecting... (attempt ${this.reconnectAttempts})`)
            this.connect(handlers)
          }, 2000 * this.reconnectAttempts)
        }
      }
      
      this.ws.onerror = (error) => {
        console.error('❌ WebSocket error:', error)
        handlers.onError?.(error)
      }
      
    } catch (error) {
      console.error('❌ Failed to connect:', error)
      handlers.onError?.(error)
    }
  }

  disconnect() {
    if (this.ws) {
      // Clear ping interval
      if (this.pingInterval) {
        clearInterval(this.pingInterval)
        this.pingInterval = null
      }
      
      this.ws.close()
      this.ws = null
    }
  }

  async send(message) {
    console.log('📤 Sending WebSocket message:', message.type)
    
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      console.error('❌ WebSocket not connected - readyState:', this.ws?.readyState)
      throw new Error('WebSocket not connected')
    }
    
    try {
      this.ws.send(JSON.stringify(message))
      console.log('✅ Message sent successfully')
    } catch (error) {
      console.error('❌ Error sending message:', error)
      throw error
    }
  }

  isConnected() {
    const connected = this.ws && this.ws.readyState === WebSocket.OPEN
    console.log('🔍 Connection check:', connected, 'readyState:', this.ws?.readyState)
    return connected
  }
}

// Export singleton instance
export const agentService = new AgentService()