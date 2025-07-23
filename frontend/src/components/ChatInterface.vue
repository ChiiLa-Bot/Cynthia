<template>
  <div class="chat-interface">
    <!-- Chat Messages Area -->
    <div class="chat-messages" ref="messagesContainer">
      <div 
        v-for="message in messages" 
        :key="message.id"
        class="message-container"
        :class="message.type"
      >
        <div class="message">
          <div class="message-header">
            <span class="message-sender">
              {{ getSenderName(message.type) }}
            </span>
            <span class="message-time">
              {{ formatTime(message.timestamp) }}
            </span>
          </div>
          
          <div class="message-content">
            {{ message.content }}
          </div>
          
          <!-- Emotion indicator for Cynthia's messages -->
          <div v-if="message.type === 'cynthia' && message.emotion" class="message-emotion">
            <span class="emotion-tag">{{ message.emotion }}</span>
          </div>
        </div>
      </div>
      
      <!-- Loading indicator -->
      <div v-if="isLoading" class="message-container cynthia">
        <div class="message loading-message">
          <div class="message-header">
            <span class="message-sender">Cynthia</span>
          </div>
          <div class="message-content">
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
    <div class="chat-input-area">
      <div class="input-container">
        <input 
          v-model="currentMessage"
          @keypress.enter="sendMessage"
          :disabled="!isConnected || isLoading"
          type="text" 
          placeholder="Type your message to Cynthia..."
          class="message-input"
          ref="messageInput"
        />
        
        <button 
          @click="sendMessage"
          :disabled="!isConnected || isLoading || !currentMessage.trim()"
          class="send-button"
        >
          <span v-if="!isLoading">Send</span>
          <span v-else class="loading-spinner"></span>
        </button>
        
        <button 
          @click="toggleVoiceInput"
          :disabled="!isConnected"
          class="voice-button"
          :class="{ 'recording': isRecording }"
        >
          🎤
        </button>
      </div>
      
      <!-- Voice recording indicator -->
      <div v-if="isRecording" class="voice-recording">
        <div class="recording-indicator">
          <span class="recording-dot"></span>
          Recording... Click to stop
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, watch, nextTick, onMounted, onUnmounted } from 'vue'

export default {
  name: 'ChatInterface',
  props: {
    messages: {
      type: Array,
      default: () => []
    },
    isConnected: {
      type: Boolean,
      default: false
    },
    isLoading: {
      type: Boolean,
      default: false
    }
  },
  emits: ['send-message', 'voice-input'],
  setup(props, { emit }) {
    // Template refs
    const messagesContainer = ref(null)
    const messageInput = ref(null)

    // Reactive state
    const currentMessage = ref('')
    const isRecording = ref(false)
    const speechRecognition = ref(null)

    // Initialize speech recognition
    const initSpeechRecognition = () => {
      if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
        speechRecognition.value = new SpeechRecognition()
        
        speechRecognition.value.continuous = false
        speechRecognition.value.interimResults = false
        speechRecognition.value.lang = 'en-US'

        speechRecognition.value.onstart = () => {
          isRecording.value = true
        }

        speechRecognition.value.onresult = (event) => {
          const transcript = event.results[0][0].transcript
          emit('voice-input', transcript)
          currentMessage.value = transcript
        }

        speechRecognition.value.onerror = (event) => {
          console.error('Speech recognition error:', event.error)
          isRecording.value = false
        }

        speechRecognition.value.onend = () => {
          isRecording.value = false
        }
      } else {
        console.warn('Speech recognition not supported')
      }
    }

    // Send message
    const sendMessage = () => {
      const message = currentMessage.value.trim()
      if (message && props.isConnected && !props.isLoading) {
        emit('send-message', message)
        currentMessage.value = ''
        
        // Focus back to input
        nextTick(() => {
          if (messageInput.value) {
            messageInput.value.focus()
          }
        })
      }
    }

    // Toggle voice input
    const toggleVoiceInput = () => {
      if (!speechRecognition.value) {
        console.warn('Speech recognition not available')
        return
      }

      if (isRecording.value) {
        speechRecognition.value.stop()
      } else {
        speechRecognition.value.start()
      }
    }

    // Scroll to bottom
    const scrollToBottom = () => {
      nextTick(() => {
        if (messagesContainer.value) {
          messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
        }
      })
    }

    // Get sender name
    const getSenderName = (type) => {
      switch (type) {
        case 'user': return 'You'
        case 'cynthia': return 'Cynthia'
        case 'system': return 'System'
        case 'error': return 'Error'
        default: return 'Unknown'
      }
    }

    // Format timestamp
    const formatTime = (timestamp) => {
      if (!timestamp) return ''
      const date = new Date(timestamp)
      return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }

    // Watch for new messages to auto-scroll
    watch(() => props.messages.length, () => {
      scrollToBottom()
    })

    // Lifecycle
    onMounted(() => {
      initSpeechRecognition()
      scrollToBottom()
      
      // Focus input on mount
      if (messageInput.value) {
        messageInput.value.focus()
      }
    })

    onUnmounted(() => {
      if (speechRecognition.value && isRecording.value) {
        speechRecognition.value.stop()
      }
    })

    return {
      messagesContainer,
      messageInput,
      currentMessage,
      isRecording,
      sendMessage,
      toggleVoiceInput,
      getSenderName,
      formatTime
    }
  }
}
</script>

<style scoped>
.chat-interface {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  min-height: 0;
}

.message-container {
  display: flex;
  width: 100%;
}

.message-container.user {
  justify-content: flex-end;
}

.message-container.cynthia {
  justify-content: flex-start;
}

.message-container.system {
  justify-content: center;
}

.message-container.error {
  justify-content: center;
}

.message {
  max-width: 70%;
  min-width: 200px;
  padding: 1rem;
  border-radius: 20px;
  position: relative;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.user .message {
  background: rgba(33, 150, 243, 0.3);
  color: white;
  border-bottom-right-radius: 5px;
}

.cynthia .message {
  background: rgba(233, 30, 99, 0.3);
  color: white;
  border-bottom-left-radius: 5px;
}

.system .message {
  background: rgba(158, 158, 158, 0.3);
  color: white;
  border-radius: 15px;
  text-align: center;
  max-width: 300px;
  font-size: 0.9rem;
}

.error .message {
  background: rgba(244, 67, 54, 0.3);
  color: white;
  border-radius: 15px;
  text-align: center;
  max-width: 300px;
}

.message-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
  font-size: 0.8rem;
  opacity: 0.8;
}

.message-sender {
  font-weight: 600;
}

.message-time {
  font-size: 0.7rem;
}

.message-content {
  line-height: 1.4;
  word-wrap: break-word;
}

.message-emotion {
  margin-top: 0.5rem;
  display: flex;
  justify-content: flex-end;
}

.emotion-tag {
  background: rgba(255, 255, 255, 0.2);
  padding: 0.2rem 0.5rem;
  border-radius: 10px;
  font-size: 0.7rem;
  text-transform: capitalize;
}

.loading-message .message-content {
  display: flex;
  align-items: center;
  min-height: 24px;
}

.typing-indicator {
  display: flex;
  gap: 4px;
  align-items: center;
}

.typing-indicator span {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.7);
  animation: typing-bounce 1.4s ease-in-out infinite both;
}

.typing-indicator span:nth-child(1) { animation-delay: -0.32s; }
.typing-indicator span:nth-child(2) { animation-delay: -0.16s; }

.chat-input-area {
  padding: 1rem;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-top: 1px solid rgba(255, 255, 255, 0.2);
}

.input-container {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.message-input {
  flex: 1;
  padding: 1rem;
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 25px;
  background: rgba(255, 255, 255, 0.1);
  color: white;
  font-size: 1rem;
  backdrop-filter: blur(10px);
}

.message-input::placeholder {
  color: rgba(255, 255, 255, 0.7);
}

.message-input:focus {
  outline: none;
  border-color: rgba(255, 255, 255, 0.5);
  background: rgba(255, 255, 255, 0.15);
}

.message-input:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.send-button, .voice-button {
  padding: 1rem;
  border: none;
  border-radius: 50%;
  width: 50px;
  height: 50px;
  cursor: pointer;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
  display: flex;
  align-items: center;
  justify-content: center;
}

.send-button {
  background: rgba(33, 150, 243, 0.8);
  color: white;
}

.send-button:hover:not(:disabled) {
  background: rgba(33, 150, 243, 1);
  transform: scale(1.05);
}

.send-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.voice-button {
  background: rgba(76, 175, 80, 0.8);
  color: white;
  font-size: 1.2rem;
}

.voice-button:hover:not(:disabled) {
  background: rgba(76, 175, 80, 1);
  transform: scale(1.05);
}

.voice-button.recording {
  background: rgba(244, 67, 54, 0.8);
  animation: recording-pulse 1s ease-in-out infinite;
}

.voice-recording {
  margin-top: 1rem;
  text-align: center;
}

.recording-indicator {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: rgba(244, 67, 54, 0.3);
  border-radius: 20px;
  color: white;
  font-size: 0.9rem;
}

.recording-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: #f44336;
  animation: recording-blink 1s ease-in-out infinite;
}

.loading-spinner {
  width: 20px;
  height: 20px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top: 2px solid white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

/* Animations */
@keyframes typing-bounce {
  0%, 80%, 100% { 
    transform: translateY(0);
    opacity: 0.5;
  }
  40% { 
    transform: translateY(-10px);
    opacity: 1;
  }
}

@keyframes recording-pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.1); }
}

@keyframes recording-blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.3; }
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Scrollbar styling */
.chat-messages::-webkit-scrollbar {
  width: 8px;
}

.chat-messages::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
}

.chat-messages::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.3);
  border-radius: 4px;
}

.chat-messages::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.5);
}
</style>
