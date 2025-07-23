<template>
  <div class="grok-interface">
    <!-- Messages Overlay -->
    <div class="messages-overlay" ref="messagesContainer">
      <div 
        v-for="(message, index) in messages" 
        :key="message.id"
        class="message-bubble"
        :class="[message.type, { 'user': message.type === 'user', 'ai': message.type === 'cynthia' }]"
        :style="{ 
          '--distance-from-bottom': messages.length - index - 1,
          '--opacity': calculateOpacity(messages.length - index - 1)
        }"
      >
        <div class="message-content">
          {{ message.content }}
        </div>
        <div v-if="message.emotion" class="emotion-indicator">
          {{ message.emotion }}
        </div>
      </div>
    </div>

    <!-- Central Avatar -->
    <div class="avatar-container">
      <div class="avatar-model">
        <CompanionAvatar 
          :emotion="currentEmotion"
          :speaking="isSpeaking"
          :animation="currentAnimation"
          @model-loaded="onModelLoaded"
        />
      </div>
    </div>

    <!-- Bottom Controls -->
    <div class="bottom-controls">
      <!-- Mode Toggle -->
      <button 
        class="mode-toggle"
        :class="currentMode"
        @click="toggleMode"
        :disabled="isLoading"
      >
        {{ currentMode.toUpperCase() }}
      </button>

      <!-- Input Form -->
      <div class="input-form">
        <div class="input-container">
          <input 
            v-model="currentMessage"
            @keypress.enter="sendMessage"
            :disabled="!isConnected || isLoading"
            type="text"
            placeholder="Message Cynthia..."
            class="message-input"
            ref="messageInput"
          />
          
          <button 
            @click="toggleVoiceInput"
            :disabled="!isConnected"
            class="voice-button"
            :class="{ 'recording': isRecording, 'pulse': isRecording }"
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 1c-1.1 0-2 .9-2 2v8c0 1.1.9 2 2 2s2-.9 2-2V3c0-1.1-.9-2-2-2zm0 18c-2.76 0-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V23h2v-2.08c3.39-.49 6-3.39 6-6.92h-2c0 2.76-2.24 5-5 5z"/>
            </svg>
          </button>
          
          <button 
            @click="sendMessage"
            :disabled="!isConnected || isLoading || !currentMessage.trim()"
            class="send-button"
          >
            <svg v-if="!isLoading" width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
              <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/>
            </svg>
            <div v-else class="loading-spinner"></div>
          </button>
        </div>
      </div>
    </div>

    <!-- Connection Status -->
    <div class="connection-status" :class="{ 'connected': isConnected, 'disconnected': !isConnected }">
      {{ isConnected ? 'Connected' : 'Disconnected' }}
    </div>
  </div>
</template>

<script>
import { ref, reactive, onMounted, onUnmounted, watch, nextTick } from 'vue'
import CompanionAvatar from './components/CompanionAvatar.vue'
import { CynthiaAPI } from './utils/api.js'
import { WebSocketManager } from './utils/websocket.js'

export default {
  name: 'App',
  components: {
    CompanionAvatar
  },
  setup() {
    // Template refs
    const messagesContainer = ref(null)
    const messageInput = ref(null)

    // Reactive state
    const messages = reactive([])
    const isConnected = ref(false)
    const isLoading = ref(false)
    const isSpeaking = ref(false)
    const isRecording = ref(false)
    const currentMode = ref('safe')
    const currentEmotion = ref('happy')
    const currentAnimation = ref('idle')
    const currentMessage = ref('')

    // API and WebSocket managers
    let api = null
    let wsManager = null
    let speechRecognition = null

    // Initialize application
    const initializeApp = async () => {
      try {
        api = new CynthiaAPI('http://localhost:8000')
        wsManager = new WebSocketManager('ws://localhost:8000/ws')
        
        // Check server status
        const status = await api.getStatus()
        isConnected.value = true
        currentMode.value = status.personality?.current_mode || 'safe'
        
        // Setup WebSocket events
        wsManager.onMessage((data) => {
          if (data.type === 'response') {
            handleAPIResponse(data)
          }
        })
        
        wsManager.onConnect(() => {
          isConnected.value = true
        })
        
        wsManager.onDisconnect(() => {
          isConnected.value = false
        })
        
        // Add welcome message
        messages.push({
          id: Date.now(),
          type: 'system',
          content: 'Cynthia AI Companion is ready! 💕',
          timestamp: new Date()
        })
        
      } catch (error) {
        console.error('Failed to initialize app:', error)
        isConnected.value = false
      }
    }

    // Initialize speech recognition
    const initSpeechRecognition = () => {
      if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
        speechRecognition = new SpeechRecognition()
        
        speechRecognition.continuous = false
        speechRecognition.interimResults = false
        speechRecognition.lang = 'en-US'

        speechRecognition.onstart = () => {
          isRecording.value = true
        }

        speechRecognition.onresult = (event) => {
          const transcript = event.results[0][0].transcript
          currentMessage.value = transcript
          sendMessage()
        }

        speechRecognition.onerror = (event) => {
          console.error('Speech recognition error:', event.error)
          isRecording.value = false
        }

        speechRecognition.onend = () => {
          isRecording.value = false
        }
      }
    }

    // Calculate opacity based on distance from bottom
    const calculateOpacity = (distanceFromBottom) => {
      const maxDistance = 10 // Messages beyond this are completely transparent
      const minOpacity = 0.1
      const maxOpacity = 1.0
      
      if (distanceFromBottom <= 2) return maxOpacity // Recent messages fully visible
      if (distanceFromBottom >= maxDistance) return minOpacity
      
      // Linear fade for messages in between
      const fadeRange = maxDistance - 2
      const fadePosition = (distanceFromBottom - 2) / fadeRange
      return maxOpacity - (fadePosition * (maxOpacity - minOpacity))
    }

    // Send message
    const sendMessage = async () => {
      const message = currentMessage.value.trim()
      if (!message || !isConnected.value || isLoading.value) return

      // Add user message
      messages.push({
        id: Date.now(),
        type: 'user',
        content: message,
        timestamp: new Date()
      })

      currentMessage.value = ''
      isLoading.value = true
      isSpeaking.value = false

      try {
        const response = await api.sendMessage(message)
        handleAPIResponse(response)
      } catch (error) {
        console.error('Error sending message:', error)
        messages.push({
          id: Date.now(),
          type: 'error',
          content: 'Sorry, I encountered an error. Please try again.',
          timestamp: new Date()
        })
      } finally {
        isLoading.value = false
      }

      // Focus back to input
      nextTick(() => {
        if (messageInput.value) {
          messageInput.value.focus()
        }
      })
    }

    // Handle API response
    const handleAPIResponse = (response) => {
      // Add Cynthia's response
      messages.push({
        id: Date.now(),
        type: 'cynthia',
        content: response.response,
        emotion: response.emotion,
        animation: response.animation,
        timestamp: new Date()
      })

      // Update avatar state
      currentEmotion.value = response.emotion || 'happy'
      currentAnimation.value = response.animation || 'idle'
      currentMode.value = response.mode || currentMode.value

      // Simulate speaking animation
      isSpeaking.value = true
      setTimeout(() => {
        isSpeaking.value = false
      }, response.response?.length * 50 || 2000)
    }

    // Toggle voice input
    const toggleVoiceInput = () => {
      if (!speechRecognition) {
        console.warn('Speech recognition not available')
        return
      }

      if (isRecording.value) {
        speechRecognition.stop()
      } else {
        speechRecognition.start()
      }
    }

    // Toggle interaction mode
    const toggleMode = async () => {
      if (isLoading.value) return

      const newMode = currentMode.value === 'safe' ? 'nsfw' : 'safe'
      
      try {
        isLoading.value = true
        await api.changeMode(newMode)
        currentMode.value = newMode
        
        messages.push({
          id: Date.now(),
          type: 'system',
          content: `Mode changed to ${newMode.toUpperCase()}`,
          timestamp: new Date()
        })
      } catch (error) {
        console.error('Error changing mode:', error)
      } finally {
        isLoading.value = false
      }
    }

    // Handle model loaded
    const onModelLoaded = (loaded) => {
      console.log('Model loaded:', loaded)
    }

    // Lifecycle
    onMounted(() => {
      initializeApp()
      initSpeechRecognition()
      
      // Focus input on mount
      if (messageInput.value) {
        messageInput.value.focus()
      }
    })

    onUnmounted(() => {
      if (wsManager) {
        wsManager.disconnect()
      }
      if (speechRecognition && isRecording.value) {
        speechRecognition.stop()
      }
    })

    return {
      messagesContainer,
      messageInput,
      messages,
      isConnected,
      isLoading,
      isSpeaking,
      isRecording,
      currentMode,
      currentEmotion,
      currentAnimation,
      currentMessage,
      calculateOpacity,
      sendMessage,
      toggleVoiceInput,
      toggleMode,
      onModelLoaded
    }
  }
}
</script>

<style scoped>
.grok-interface {
  width: 100vw;
  height: 100vh;
  background: #1a1a1a;
  position: relative;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

/* Messages Overlay */
.messages-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 120px;
  z-index: 10;
  pointer-events: none;
  overflow-y: auto;
  padding: 20px;
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
}

.message-bubble {
  margin-bottom: 16px;
  pointer-events: auto;
  transition: opacity 0.3s ease, transform 0.3s ease;
  opacity: var(--opacity);
  transform: translateY(calc(var(--distance-from-bottom) * -2px));
}

.message-bubble.user {
  align-self: flex-end;
  max-width: 70%;
}

.message-bubble.ai,
.message-bubble.cynthia {
  align-self: flex-start;
  max-width: 70%;
}

.message-bubble.system {
  align-self: center;
  max-width: 50%;
}

.message-content {
  background: rgba(255, 255, 255, 0.12);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 18px;
  padding: 12px 16px;
  color: white;
  font-size: 14px;
  line-height: 1.4;
  backdrop-filter: blur(20px);
}

.message-bubble.user .message-content {
  background: rgba(0, 122, 255, 0.3);
  border-color: rgba(0, 122, 255, 0.5);
}

.message-bubble.ai .message-content,
.message-bubble.cynthia .message-content {
  background: rgba(255, 255, 255, 0.15);
  border-color: rgba(255, 255, 255, 0.25);
}

.message-bubble.system .message-content {
  background: rgba(255, 193, 7, 0.2);
  border-color: rgba(255, 193, 7, 0.4);
  text-align: center;
  font-size: 13px;
}

.emotion-indicator {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.6);
  margin-top: 4px;
  text-align: right;
  text-transform: capitalize;
}

/* Central Avatar */
.avatar-container {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  z-index: 5;
  width: 300px;
  height: 400px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.avatar-model {
  width: 100%;
  height: 100%;
}

/* Bottom Controls */
.bottom-controls {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  z-index: 20;
  padding: 20px;
  background: linear-gradient(transparent, rgba(26, 26, 26, 0.9));
  display: flex;
  align-items: center;
  gap: 16px;
}

.mode-toggle {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 20px;
  color: white;
  padding: 8px 16px;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.mode-toggle:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.2);
  border-color: rgba(255, 255, 255, 0.3);
}

.mode-toggle.safe {
  border-color: rgba(0, 122, 255, 0.5);
  background: rgba(0, 122, 255, 0.2);
}

.mode-toggle.nsfw {
  border-color: rgba(255, 69, 58, 0.5);
  background: rgba(255, 69, 58, 0.2);
}

.mode-toggle:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.input-form {
  flex: 1;
}

.input-container {
  display: flex;
  align-items: center;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 24px;
  padding: 4px;
  backdrop-filter: blur(20px);
}

.message-input {
  flex: 1;
  background: transparent;
  border: none;
  outline: none;
  color: white;
  font-size: 16px;
  padding: 12px 16px;
  placeholder-color: rgba(255, 255, 255, 0.5);
}

.message-input::placeholder {
  color: rgba(255, 255, 255, 0.5);
}

.message-input:disabled {
  opacity: 0.5;
}

.voice-button,
.send-button {
  width: 40px;
  height: 40px;
  border-radius: 20px;
  border: none;
  background: rgba(255, 255, 255, 0.12);
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  margin-left: 4px;
}

.voice-button:hover:not(:disabled),
.send-button:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.2);
  transform: scale(1.05);
}

.voice-button.recording {
  background: rgba(255, 69, 58, 0.8);
  animation: pulse 1.5s ease-in-out infinite;
}

.send-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.loading-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top: 2px solid white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

/* Connection Status */
.connection-status {
  position: absolute;
  top: 20px;
  right: 20px;
  z-index: 30;
  padding: 6px 12px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.connection-status.connected {
  background: rgba(52, 199, 89, 0.2);
  color: rgb(52, 199, 89);
  border: 1px solid rgba(52, 199, 89, 0.3);
}

.connection-status.disconnected {
  background: rgba(255, 69, 58, 0.2);
  color: rgb(255, 69, 58);
  border: 1px solid rgba(255, 69, 58, 0.3);
}

/* Animations */
@keyframes pulse {
  0%, 100% {
    transform: scale(1);
    opacity: 1;
  }
  50% {
    transform: scale(1.1);
    opacity: 0.8;
  }
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Scrollbar for messages */
.messages-overlay::-webkit-scrollbar {
  width: 4px;
}

.messages-overlay::-webkit-scrollbar-track {
  background: transparent;
}

.messages-overlay::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 2px;
}

.messages-overlay::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.3);
}

/* Responsive */
@media (max-width: 768px) {
  .avatar-container {
    width: 250px;
    height: 350px;
  }
  
  .bottom-controls {
    padding: 16px;
    flex-direction: column;
    gap: 12px;
  }
  
  .mode-toggle {
    align-self: center;
  }
  
  .message-bubble {
    max-width: 85% !important;
  }
}
</style>
