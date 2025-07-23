<template>
  <div class="chat-app">
    <!-- Header -->
    <div class="chat-header">
      <div class="status-indicator" :class="{ 'connected': isConnected }"></div>
      <h1>Cynthia AI Companion</h1>
      <div class="connection-status">
        {{ isConnected ? 'Connected' : 'Disconnected' }}
      </div>
    </div>

    <!-- Messages Area -->
    <div class="messages-container" ref="messagesContainer">
      <div 
        v-for="message in messages" 
        :key="message.id"
        class="message"
        :class="[message.type]"
      >
        <div class="message-content">
          <div class="message-text">{{ message.content }}</div>
          <div class="message-time">{{ formatTime(message.timestamp) }}</div>
        </div>
      </div>
      
      <!-- Typing indicator -->
      <div v-if="isTyping" class="message cynthia">
        <div class="message-content">
          <div class="typing-indicator">
            <span></span>
            <span></span>
            <span></span>
          </div>
        </div>
      </div>
    </div>

    <!-- Input Area -->
    <div class="input-container">
      <div class="input-wrapper">
        <input 
          v-model="currentMessage"
          @keypress.enter="sendMessage"
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
      
      <!-- Voice Controls -->
      <div class="voice-controls">
        <button 
          @click="toggleVoiceInput"
          :class="{ 'active': isListening }"
          class="voice-button"
        >
          🎤
        </button>
        <button 
          @click="toggleVoiceOutput"
          :class="{ 'active': voiceEnabled }"
          class="voice-button"
        >
          🔊
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'

export default {
  name: 'ChatApp',
  setup() {
    // Reactive state
    const messages = ref([
      {
        id: 1,
        type: 'cynthia',
        content: 'สวัสดีค่ะ! ฉันชื่อซินเธีย ยินดีที่ได้รู้จักนะคะ 😊',
        timestamp: new Date(),
        emotion: 'happy'
      }
    ])
    
    const currentMessage = ref('')
    const isConnected = ref(false)
    const isTyping = ref(false)
    const isListening = ref(false)
    const voiceEnabled = ref(false)
    const messagesContainer = ref(null)

    // WebSocket connection
    let websocket = null
    let messageIdCounter = 2

    // Connect to WebSocket
    const connectWebSocket = () => {
      try {
        websocket = new WebSocket('ws://localhost:8000/ws')
        
        websocket.onopen = () => {
          console.log('Connected to Cynthia')
          isConnected.value = true
        }
        
        websocket.onmessage = (event) => {
          const data = JSON.parse(event.data)
          
          if (data.type === 'response') {
            isTyping.value = false
            addMessage({
              type: 'cynthia',
              content: data.content,
              emotion: data.emotion || 'happy'
            })
            
            // Speak if voice is enabled
            if (voiceEnabled.value && data.content) {
              speak(data.content)
            }
          }
        }
        
        websocket.onclose = () => {
          console.log('Disconnected from Cynthia')
          isConnected.value = false
          
          // Try to reconnect after 3 seconds
          setTimeout(connectWebSocket, 3000)
        }
        
        websocket.onerror = (error) => {
          console.error('WebSocket error:', error)
          isConnected.value = false
        }
        
      } catch (error) {
        console.error('Failed to connect:', error)
        isConnected.value = false
        setTimeout(connectWebSocket, 3000)
      }
    }

    // Send message
    const sendMessage = async () => {
      if (!currentMessage.value.trim() || !isConnected.value || isTyping.value) {
        return
      }

      const messageText = currentMessage.value.trim()
      currentMessage.value = ''

      // Add user message
      addMessage({
        type: 'user',
        content: messageText
      })

      // Show typing indicator
      isTyping.value = true

      // Send to backend
      if (websocket && websocket.readyState === WebSocket.OPEN) {
        websocket.send(JSON.stringify({
          type: 'message',
          content: messageText
        }))
      } else {
        // Fallback if WebSocket is not connected
        setTimeout(() => {
          isTyping.value = false
          addMessage({
            type: 'cynthia',
            content: 'ขอโทษนะคะ ตอนนี้ฉันไม่สามารถตอบได้ เซิร์ฟเวอร์ไม่ได้เชื่อมต่ออยู่ค่ะ',
            emotion: 'sad'
          })
        }, 1000)
      }
    }

    // Add message to chat
    const addMessage = (message) => {
      messages.value.push({
        id: messageIdCounter++,
        ...message,
        timestamp: new Date()
      })
      
      // Scroll to bottom
      nextTick(() => {
        if (messagesContainer.value) {
          messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
        }
      })
    }

    // Format time
    const formatTime = (timestamp) => {
      return timestamp.toLocaleTimeString('th-TH', {
        hour: '2-digit',
        minute: '2-digit'
      })
    }

    // Voice functions
    const toggleVoiceInput = () => {
      isListening.value = !isListening.value
      
      if (isListening.value) {
        startVoiceRecognition()
      } else {
        stopVoiceRecognition()
      }
    }

    const toggleVoiceOutput = () => {
      voiceEnabled.value = !voiceEnabled.value
    }

    let recognition = null

    const startVoiceRecognition = () => {
      if ('webkitSpeechRecognition' in window) {
        recognition = new webkitSpeechRecognition()
        recognition.continuous = false
        recognition.interimResults = false
        recognition.lang = 'th-TH'

        recognition.onresult = (event) => {
          const transcript = event.results[0][0].transcript
          currentMessage.value = transcript
          isListening.value = false
        }

        recognition.onerror = () => {
          isListening.value = false
        }

        recognition.onend = () => {
          isListening.value = false
        }

        recognition.start()
      }
    }

    const stopVoiceRecognition = () => {
      if (recognition) {
        recognition.stop()
      }
    }

    const speak = (text) => {
      if ('speechSynthesis' in window) {
        const utterance = new SpeechSynthesisUtterance(text)
        utterance.lang = 'th-TH'
        utterance.rate = 0.9
        utterance.pitch = 1.1
        speechSynthesis.speak(utterance)
      }
    }

    // Lifecycle
    onMounted(() => {
      connectWebSocket()
    })

    onUnmounted(() => {
      if (websocket) {
        websocket.close()
      }
      if (recognition) {
        recognition.stop()
      }
    })

    return {
      messages,
      currentMessage,
      isConnected,
      isTyping,
      isListening,
      voiceEnabled,
      messagesContainer,
      sendMessage,
      formatTime,
      toggleVoiceInput,
      toggleVoiceOutput
    }
  }
}
</script>

<style scoped>
.chat-app {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: #1a1a1a;
  color: white;
}

.chat-header {
  display: flex;
  align-items: center;
  padding: 1rem 2rem;
  background: rgba(255, 255, 255, 0.05);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  gap: 1rem;
}

.status-indicator {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: #ff6b6b;
  transition: background-color 0.3s ease;
}

.status-indicator.connected {
  background: #51cf66;
}

.chat-header h1 {
  font-size: 1.5rem;
  font-weight: 600;
  color: #ff6b9d;
  flex: 1;
}

.connection-status {
  font-size: 0.9rem;
  opacity: 0.7;
}

.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.messages-container::-webkit-scrollbar {
  width: 6px;
}

.messages-container::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.1);
}

.messages-container::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.3);
  border-radius: 3px;
}

.message {
  display: flex;
  max-width: 70%;
  animation: fadeInUp 0.3s ease;
}

.message.user {
  align-self: flex-end;
}

.message.user .message-content {
  background: #ff6b9d;
  color: white;
}

.message.cynthia {
  align-self: flex-start;
}

.message.cynthia .message-content {
  background: rgba(255, 255, 255, 0.1);
  color: white;
}

.message-content {
  padding: 0.75rem 1rem;
  border-radius: 18px;
  position: relative;
  word-wrap: break-word;
}

.message-text {
  line-height: 1.4;
}

.message-time {
  font-size: 0.75rem;
  opacity: 0.7;
  margin-top: 0.25rem;
}

.typing-indicator {
  display: flex;
  gap: 4px;
  align-items: center;
  padding: 0.5rem 0;
}

.typing-indicator span {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: currentColor;
  opacity: 0.4;
  animation: typing 1.4s infinite ease-in-out;
}

.typing-indicator span:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-indicator span:nth-child(3) {
  animation-delay: 0.4s;
}

.input-container {
  padding: 1rem 2rem;
  background: rgba(255, 255, 255, 0.05);
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.input-wrapper {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.message-input {
  flex: 1;
  padding: 0.75rem 1rem;
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 25px;
  background: rgba(255, 255, 255, 0.1);
  color: white;
  font-size: 1rem;
  outline: none;
  transition: all 0.3s ease;
}

.message-input::placeholder {
  color: rgba(255, 255, 255, 0.5);
}

.message-input:focus {
  border-color: #ff6b9d;
  background: rgba(255, 255, 255, 0.15);
}

.message-input:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.send-button {
  padding: 0.75rem;
  border: none;
  border-radius: 50%;
  background: #ff6b9d;
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  min-width: 44px;
  height: 44px;
}

.send-button:hover:not(:disabled) {
  background: #ff8fb3;
  transform: scale(1.05);
}

.send-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

.voice-controls {
  display: flex;
  justify-content: center;
  gap: 1rem;
}

.voice-button {
  padding: 0.5rem 1rem;
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.1);
  color: white;
  cursor: pointer;
  font-size: 1.2rem;
  transition: all 0.3s ease;
}

.voice-button:hover {
  background: rgba(255, 255, 255, 0.2);
}

.voice-button.active {
  background: #ff6b9d;
  border-color: #ff6b9d;
}

/* Animations */
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes typing {
  0%, 60%, 100% {
    transform: translateY(0);
    opacity: 0.4;
  }
  30% {
    transform: translateY(-10px);
    opacity: 1;
  }
}
</style>
