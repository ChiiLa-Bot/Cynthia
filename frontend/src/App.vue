<template>
  <div class="cynthia-chatbot">
    <!-- Chat Messages -->
    <div class="chat-container" ref="chatContainer">
      <div class="messages">
        <div 
          v-for="message in messages" 
          :key="message.id"
          class="message"
          :class="{ 'user': message.type === 'user', 'ai': message.type === 'cynthia', 'system': message.type === 'system' }"
        >
          <div class="message-content">
            <div v-if="message.type === 'cynthia'" class="ai-name">Cynthia</div>
            <div v-if="message.type === 'system'" class="system-name">System</div>
            <div class="message-text">{{ message.content }}</div>
            <div class="message-time">{{ formatTime(message.timestamp) }}</div>
          </div>
        </div>
        
        <!-- Typing indicator -->
        <div v-if="isTyping" class="message ai typing-message">
          <div class="message-content">
            <div class="ai-name">Cynthia</div>
            <div class="typing-indicator">
              <span></span>
              <span></span>
              <span></span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Input Area -->
    <div class="input-area">
      <div class="input-container">
        <!-- Mode Switch Button -->
        <button 
          @click="toggleMode"
          :disabled="!isConnected"
          class="mode-button"
          :class="{ 'nsfw-mode': currentMode === 'nsfw' }"
          :title="currentMode === 'safe' ? 'Switch to NSFW Mode' : 'Switch to Safe Mode'"
        >
          <div class="mode-icon">
            <svg v-if="currentMode === 'safe'" width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12,1L3,5V11C3,16.55 6.84,21.74 12,23C17.16,21.74 21,16.55 21,11V5L12,1M12,7C13.4,7 14.8,8.6 14.8,10V11.5C15.4,11.5 16,12.1 16,12.7V16.7C16,17.4 15.4,18 14.8,18H9.2C8.6,18 8,17.4 8,16.8V12.8C8,12.1 8.6,11.5 9.2,11.5V10C9.2,8.6 10.6,7 12,7M12,8.2C11.2,8.2 10.5,8.7 10.5,10V11.5H13.5V10C13.5,8.7 12.8,8.2 12,8.2Z"/>
            </svg>
            <svg v-else width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12,1L3,5V11C3,16.55 6.84,21.74 12,23C17.16,21.74 21,16.55 21,11V5L12,1M12,7C13.4,7 14.8,8.6 14.8,10V11.5C15.4,11.5 16,12.1 16,12.7V16.7C16,17.4 15.4,18 14.8,18H9.2C8.6,18 8,17.4 8,16.8V12.8C8,12.1 8.6,11.5 9.2,11.5V10C9.2,8.6 10.6,7 12,7M12,8.2C11.2,8.2 10.5,8.7 10.5,10V11.5H13.5V10C13.5,8.7 12.8,8.2 12,8.2Z"/>
            </svg>
          </div>
          <span class="mode-text">{{ currentMode.toUpperCase() }}</span>
        </button>
        
        <input 
          v-model="currentMessage"
          @keyup.enter="sendMessage"
          :disabled="!isConnected || isTyping"
          placeholder="Message Cynthia..."
          class="message-input"
        />
        <button 
          @click="sendMessage"
          :disabled="!currentMessage.trim() || !isConnected || isTyping"
          class="send-button"
        >
          <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
            <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/>
          </svg>
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'

export default {
  name: 'CynthiaChatbot',
  setup() {
    // Reactive state
    const messages = ref([])
    const currentMessage = ref('')
    const isConnected = ref(false)
    const isTyping = ref(false)
    const chatContainer = ref(null)
    const currentMode = ref('safe') // Default to safe mode

    // WebSocket connection
    let ws = null

    // Initialize welcome message
    const initializeChat = () => {
      messages.value = [
        {
          id: 1,
          type: 'cynthia',
          content: 'สวัสดีค่ะ! ฉันชื่อ Cynthia 💕 มีอะไรให้ช่วยไหมคะ?',
          timestamp: new Date()
        }
      ]
    }

    // Connect to WebSocket
    const connectWebSocket = () => {
      try {
        ws = new WebSocket('ws://localhost:8000/ws')
        
        ws.onopen = () => {
          console.log('WebSocket connected')
          isConnected.value = true
        }
        
        ws.onmessage = (event) => {
          const data = JSON.parse(event.data)
          
          if (data.type === 'message') {
            isTyping.value = false
            addMessage('cynthia', data.content)
          }
        }
        
        ws.onclose = () => {
          console.log('WebSocket disconnected')
          isConnected.value = false
          
          // Try to reconnect after 3 seconds
          setTimeout(() => {
            connectWebSocket()
          }, 3000)
        }
        
        ws.onerror = (error) => {
          console.error('WebSocket error:', error)
          isConnected.value = false
        }
        
      } catch (error) {
        console.error('Failed to connect WebSocket:', error)
        isConnected.value = false
        
        // Fallback to HTTP API
        setTimeout(() => {
          connectWebSocket()
        }, 5000)
      }
    }

    // Add message to chat
    const addMessage = (type, content) => {
      const message = {
        id: Date.now(),
        type,
        content,
        timestamp: new Date()
      }
      
      messages.value.push(message)
      scrollToBottom()
    }

    // Send message
    const sendMessage = async () => {
      if (!currentMessage.value.trim() || isTyping.value) {
        return
      }
      
      const messageText = currentMessage.value.trim()
      currentMessage.value = ''
      
      // Add user message
      addMessage('user', messageText)
      
      // Show typing indicator
      isTyping.value = true
      
      try {
        if (ws && ws.readyState === WebSocket.OPEN) {
          // Send via WebSocket
          ws.send(JSON.stringify({
            type: 'message',
            content: messageText
          }))
        } else {
          // Fallback to HTTP API
          const response = await fetch('http://localhost:8000/chat', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({
              message: messageText
            })
          })
          
          if (response.ok) {
            const data = await response.json()
            isTyping.value = false
            addMessage('cynthia', data.response)
          } else {
            throw new Error('API request failed')
          }
        }
      } catch (error) {
        console.error('Failed to send message:', error)
        isTyping.value = false
        addMessage('cynthia', 'ขอโทษค่ะ เกิดข้อผิดพลาดในการเชื่อมต่อ กรุณาลองใหม่อีกครั้งค่ะ')
      }
    }

    // Scroll to bottom
    const scrollToBottom = async () => {
      await nextTick()
      if (chatContainer.value) {
        const messagesElement = chatContainer.value.querySelector('.messages')
        if (messagesElement) {
          messagesElement.scrollTop = messagesElement.scrollHeight
        }
      }
    }

    // Toggle mode between safe and nsfw
    const toggleMode = async () => {
      if (!isConnected.value) return
      
      const newMode = currentMode.value === 'safe' ? 'nsfw' : 'safe'
      
      try {
        const response = await fetch('http://localhost:8000/mode', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            mode: newMode
          })
        })
        
        if (response.ok) {
          const data = await response.json()
          currentMode.value = newMode
          
          // Add system message about mode change
          addMessage('system', `Mode switched to ${newMode.toUpperCase()}`)
          
          console.log('Mode changed:', data)
        } else {
          throw new Error('Failed to change mode')
        }
      } catch (error) {
        console.error('Error changing mode:', error)
        addMessage('system', 'Failed to change mode. Please try again.')
      }
    }

    // Format time
    const formatTime = (date) => {
      return date.toLocaleTimeString('th-TH', {
        hour: '2-digit',
        minute: '2-digit'
      })
    }

    // Lifecycle
    onMounted(() => {
      initializeChat()
      connectWebSocket()
    })

    onUnmounted(() => {
      if (ws) {
        ws.close()
      }
    })

    return {
      messages,
      currentMessage,
      isConnected,
      isTyping,
      chatContainer,
      currentMode,
      sendMessage,
      toggleMode,
      formatTime
    }
  }
}
</script>

<style scoped>
/* Reset และ override styles */
* {
  box-sizing: border-box;
}

.cynthia-chatbot * {
  background-image: none !important;
}

.cynthia-chatbot {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: #1a1a1a;
  color: white;
  position: relative;
  font-family: 'Orbitron', monospace;
}

.chat-container {
  flex: 1;
  overflow: hidden;
  padding: 2rem;
  display: flex;
  justify-content: center;
}

.messages {
  width: 100%;
  max-width: 600px;
  height: 100%;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  padding-right: 0.5rem;
}

.messages::-webkit-scrollbar {
  width: 6px;
}

.messages::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 3px;
}

.messages::-webkit-scrollbar-thumb {
  background: rgba(255, 107, 157, 0.5);
  border-radius: 3px;
}

.message {
  display: flex;
  margin-bottom: 0.5rem;
}

.message.user {
  justify-content: flex-end;
}

.message.ai {
  justify-content: flex-start;
}

.message.system {
  justify-content: center;
}

.message-content {
  max-width: 80%;
  padding: 1rem 1.25rem;
  border-radius: 1.5rem;
  position: relative;
}

.cynthia-chatbot .message.user .message-content {
  background: #282828 !important;
  background-color: #282828 !important;
  background-image: none !important;
  background-attachment: initial !important;
  background-origin: initial !important;
  background-clip: initial !important;
  background-size: initial !important;
  background-repeat: initial !important;
  background-position: initial !important;
  color: white !important;
  border-bottom-right-radius: 0.5rem;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  word-wrap: break-word;
  overflow-wrap: break-word;
  white-space: normal;
}

.message.ai .message-content {
  background: #282828;
  color: white;
  border-bottom-left-radius: 0.5rem;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  word-wrap: break-word;
  overflow-wrap: break-word;
  white-space: normal;
}

.message.system .message-content {
  background: rgba(158, 158, 158, 0.3);
  color: white;
  border-radius: 1rem;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  text-align: center;
  max-width: 300px;
  font-size: 0.9rem;
}

.ai-name {
  font-size: 0.8rem;
  color: #ff6b9d;
  font-weight: 700;
  margin-bottom: 0.5rem;
  font-family: 'Orbitron', monospace;
  letter-spacing: 1px;
}

.system-name {
  font-size: 0.8rem;
  color: #9e9e9e;
  font-weight: 700;
  margin-bottom: 0.5rem;
  font-family: 'Orbitron', monospace;
  letter-spacing: 1px;
}

.message-text {
  font-size: 1rem;
  line-height: 1.5;
  word-wrap: break-word;
  font-family: 'Orbitron', monospace;
  font-weight: 500;
  white-space: normal;
  overflow-wrap: break-word;
  hyphens: none;
}

.message-time {
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.6);
  margin-top: 0.5rem;
  text-align: right;
}

.message.ai .message-time {
  text-align: left;
}

.typing-message .typing-indicator {
  display: flex;
  gap: 0.25rem;
  align-items: center;
  height: 1rem;
}

.typing-indicator span {
  width: 6px;
  height: 6px;
  background: #ff6b9d;
  border-radius: 50%;
  animation: typing-bounce 1.4s infinite ease-in-out;
}

.typing-indicator span:nth-child(1) {
  animation-delay: -0.32s;
}

.typing-indicator span:nth-child(2) {
  animation-delay: -0.16s;
}

.input-area {
  padding: 1rem 2rem 2rem;
  background: #1a1a1a;
  display: flex;
  justify-content: center;
}

.input-container {
  display: flex;
  gap: 0.75rem;
  align-items: center;
  width: 100%;
  max-width: 600px;
  position: relative;
}

.message-input {
  flex: 1;
  padding: 1rem 1.25rem;
  background: rgba(40, 40, 40, 0.8);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 2rem;
  color: white;
  font-size: 1rem;
  outline: none;
  transition: all 0.3s ease;
  font-family: 'Orbitron', monospace;
  font-weight: 500;
}

.message-input::placeholder {
  color: rgba(255, 255, 255, 0.5);
}

.message-input:focus {
  border-color: #ff6b9d;
  box-shadow: 0 0 0 2px rgba(255, 107, 157, 0.2);
  background: rgba(40, 40, 40, 0.9);
}

.message-input:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.send-button {
  padding: 1rem;
  background: rgba(40, 40, 40, 0.9);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 50%;
  color: white;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 48px;
  height: 48px;
}

.send-button:hover:not(:disabled) {
  transform: scale(1.05);
  background: rgba(50, 50, 50, 0.9);
}

.send-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

.mode-button {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  background: rgba(40, 40, 40, 0.9);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 1.5rem;
  color: white;
  cursor: pointer;
  transition: all 0.3s ease;
  font-family: 'Orbitron', monospace;
  font-weight: 600;
  font-size: 0.8rem;
  min-width: 80px;
  justify-content: center;
}

.mode-button:hover:not(:disabled) {
  transform: scale(1.05);
  background: rgba(50, 50, 50, 0.9);
  border-color: rgba(255, 255, 255, 0.3);
}

.mode-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

.mode-button.nsfw-mode {
  background: rgba(255, 107, 157, 0.2);
  border-color: rgba(255, 107, 157, 0.4);
  color: #ff6b9d;
}

.mode-button.nsfw-mode:hover:not(:disabled) {
  background: rgba(255, 107, 157, 0.3);
  border-color: rgba(255, 107, 157, 0.6);
}

.mode-icon {
  display: flex;
  align-items: center;
  justify-content: center;
}

.mode-text {
  font-size: 0.75rem;
  letter-spacing: 0.5px;
}

@keyframes typing-bounce {
  0%, 80%, 100% {
    transform: scale(0);
    opacity: 0.5;
  }
  40% {
    transform: scale(1);
    opacity: 1;
  }
}

@media (max-width: 768px) {
  .input-area {
    padding: 1rem;
  }
  
  .message-content {
    max-width: 90%;
  }
  
  .chat-container {
    padding: 1rem;
  }
}
</style>
