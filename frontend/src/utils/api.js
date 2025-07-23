/**
 * Cynthia API Client
 * Handles all HTTP requests to the Cynthia AI Companion backend
 */

class CynthiaAPI {
  constructor(baseURL = 'http://localhost:8000') {
    this.baseURL = baseURL
    this.defaultHeaders = {
      'Content-Type': 'application/json',
      'Accept': 'application/json'
    }
  }

  /**
   * Make a generic API request
   */
  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`
    const config = {
      headers: { ...this.defaultHeaders, ...options.headers },
      ...options
    }

    try {
      const response = await fetch(url, config)
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`)
      }

      const contentType = response.headers.get('content-type')
      if (contentType && contentType.includes('application/json')) {
        return await response.json()
      }
      
      return await response.text()
    } catch (error) {
      console.error('API Request failed:', error)
      throw error
    }
  }

  /**
   * GET request
   */
  async get(endpoint) {
    return this.request(endpoint, { method: 'GET' })
  }

  /**
   * POST request
   */
  async post(endpoint, data = {}) {
    return this.request(endpoint, {
      method: 'POST',
      body: JSON.stringify(data)
    })
  }

  // === API Endpoints ===

  /**
   * Check server health
   */
  async getHealth() {
    return this.get('/health')
  }

  /**
   * Get comprehensive system status
   */
  async getStatus() {
    return this.get('/status')
  }

  /**
   * Send a message to Cynthia
   */
  async sendMessage(message) {
    return this.post('/chat', { message })
  }

  /**
   * Change interaction mode (safe/nsfw)
   */
  async changeMode(mode) {
    return this.post('/mode', { mode })
  }

  /**
   * Reset conversation context
   */
  async resetConversation() {
    return this.post('/reset')
  }

  /**
   * Test connection to server
   */
  async testConnection() {
    try {
      const response = await this.get('/')
      return { connected: true, message: response.message }
    } catch (error) {
      return { connected: false, error: error.message }
    }
  }
}

export { CynthiaAPI }
