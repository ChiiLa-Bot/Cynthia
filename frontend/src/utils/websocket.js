/**
 * WebSocket Manager for real-time communication with Cynthia
 */

class WebSocketManager {
  constructor(url = 'ws://localhost:8000/ws') {
    this.url = url
    this.socket = null
    this.reconnectAttempts = 0
    this.maxReconnectAttempts = 5
    this.reconnectDelay = 1000
    this.eventHandlers = {
      open: [],
      message: [],
      close: [],
      error: []
    }
    this.isReconnecting = false
  }

  /**
   * Connect to WebSocket
   */
  connect() {
    try {
      this.socket = new WebSocket(this.url)
      this.setupEventListeners()
    } catch (error) {
      console.error('WebSocket connection failed:', error)
      this.handleError(error)
    }
  }

  /**
   * Disconnect from WebSocket
   */
  disconnect() {
    if (this.socket) {
      this.socket.close()
      this.socket = null
    }
    this.isReconnecting = false
  }

  /**
   * Send message through WebSocket
   */
  send(data) {
    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      const message = typeof data === 'string' ? data : JSON.stringify(data)
      this.socket.send(message)
      return true
    } else {
      console.warn('WebSocket is not connected')
      return false
    }
  }

  /**
   * Setup WebSocket event listeners
   */
  setupEventListeners() {
    if (!this.socket) return

    this.socket.onopen = (event) => {
      console.log('WebSocket connected')
      this.reconnectAttempts = 0
      this.isReconnecting = false
      this.triggerHandlers('open', event)
    }

    this.socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        this.triggerHandlers('message', data)
      } catch (error) {
        // If not JSON, treat as plain text
        this.triggerHandlers('message', { type: 'text', content: event.data })
      }
    }

    this.socket.onclose = (event) => {
      console.log('WebSocket disconnected', event.code, event.reason)
      this.triggerHandlers('close', event)
      
      // Attempt to reconnect if not intentionally closed
      if (!event.wasClean && this.reconnectAttempts < this.maxReconnectAttempts) {
        this.attemptReconnect()
      }
    }

    this.socket.onerror = (error) => {
      console.error('WebSocket error:', error)
      this.handleError(error)
    }
  }

  /**
   * Attempt to reconnect
   */
  attemptReconnect() {
    if (this.isReconnecting) return

    this.isReconnecting = true
    this.reconnectAttempts++
    
    console.log(`Attempting to reconnect... (${this.reconnectAttempts}/${this.maxReconnectAttempts})`)

    setTimeout(() => {
      if (this.reconnectAttempts <= this.maxReconnectAttempts) {
        this.connect()
      } else {
        console.error('Max reconnection attempts reached')
        this.isReconnecting = false
      }
    }, this.reconnectDelay * this.reconnectAttempts)
  }

  /**
   * Handle WebSocket errors
   */
  handleError(error) {
    this.triggerHandlers('error', error)
  }

  /**
   * Add event listener
   */
  on(event, handler) {
    if (this.eventHandlers[event]) {
      this.eventHandlers[event].push(handler)
    }
  }

  /**
   * Remove event listener
   */
  off(event, handler) {
    if (this.eventHandlers[event]) {
      const index = this.eventHandlers[event].indexOf(handler)
      if (index > -1) {
        this.eventHandlers[event].splice(index, 1)
      }
    }
  }

  /**
   * Trigger event handlers
   */
  triggerHandlers(event, data) {
    if (this.eventHandlers[event]) {
      this.eventHandlers[event].forEach(handler => {
        try {
          handler(data)
        } catch (error) {
          console.error(`Error in ${event} handler:`, error)
        }
      })
    }
  }

  // === Convenience methods ===

  /**
   * Add connection event listener
   */
  onConnect(handler) {
    this.on('open', handler)
  }

  /**
   * Add message event listener
   */
  onMessage(handler) {
    this.on('message', handler)
  }

  /**
   * Add disconnection event listener
   */
  onDisconnect(handler) {
    this.on('close', handler)
  }

  /**
   * Add error event listener
   */
  onError(handler) {
    this.on('error', handler)
  }

  /**
   * Get connection status
   */
  get isConnected() {
    return this.socket && this.socket.readyState === WebSocket.OPEN
  }

  /**
   * Get connection state
   */
  get readyState() {
    return this.socket ? this.socket.readyState : WebSocket.CLOSED
  }

  /**
   * Get connection state as string
   */
  get connectionState() {
    if (!this.socket) return 'DISCONNECTED'
    
    switch (this.socket.readyState) {
      case WebSocket.CONNECTING: return 'CONNECTING'
      case WebSocket.OPEN: return 'CONNECTED'
      case WebSocket.CLOSING: return 'CLOSING'
      case WebSocket.CLOSED: return 'CLOSED'
      default: return 'UNKNOWN'
    }
  }
}

export { WebSocketManager }
