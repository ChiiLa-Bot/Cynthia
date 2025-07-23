<template>
  <div class="companion-avatar">
    <div class="avatar-display" ref="avatarContainer">
      <!-- Loading Screen -->
      <div v-if="isLoading" class="loading-screen">
        <div class="loading-spinner"></div>
        <div class="loading-content">
          <h3>Loading Cynthia...</h3>
          <div class="progress-container">
            <div class="progress-bar">
              <div class="progress-fill" :style="{ width: loadingProgress + '%' }"></div>
            </div>
            <span class="progress-text">{{ loadingProgress }}%</span>
          </div>
          <p class="loading-step">{{ loadingStep }}</p>
        </div>
      </div>

      <!-- Error Display -->
      <div v-if="hasError" class="error-display">
        <h3>Loading Error</h3>
        <p>{{ errorMessage }}</p>
        <button @click="retryLoad" class="retry-btn">Retry</button>
      </div>

      <!-- Live2D Canvas -->
      <canvas 
        v-show="!isLoading && !hasError && useRealModel" 
        ref="pixiCanvas" 
        class="live2d-canvas"
      ></canvas>

      <!-- Simple Avatar Fallback -->
      <div v-if="!useRealModel && !isLoading && !hasError" class="simple-avatar">
        <p class="fallback-message">Using simple avatar - Live2D not available</p>
        <div class="avatar-character">
          <div class="character-head">
            <div class="hair"></div>
            <div class="face">
              <div class="eyes">
                <div class="eye left"></div>
                <div class="eye right"></div>
              </div>
              <div class="mouth"></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import * as PIXI from 'pixi.js'
import { Live2DModel } from 'pixi-live2d-display'

export default {
  name: 'CompanionAvatar',
  props: {
    emotion: {
      type: String,
      default: 'happy'
    },
    speaking: {
      type: Boolean,
      default: false
    }
  },
  emits: ['model-loaded', 'animation-complete'],
  setup(props, { emit }) {
    // Template refs
    const avatarContainer = ref(null)
    const pixiCanvas = ref(null)

    // Reactive state
    const isLoading = ref(true)
    const hasError = ref(false)
    const errorMessage = ref('')
    const useRealModel = ref(true)
    const loadingProgress = ref(0)
    const loadingStep = ref('Initializing...')

    // PIXI and Live2D
    let pixiApp = null
    let live2dModel = null

    // Check Live2D runtime availability
    const checkLive2DRuntime = () => {
      console.log('Checking Live2D Cubism 4 runtime...')
      console.log('window.LIVE2DCUBISMCORE:', !!window.LIVE2DCUBISMCORE)
      console.log('Live2DModel available:', !!Live2DModel)
      
      if (!window.LIVE2DCUBISMCORE) {
        throw new Error('Live2D Cubism 4 runtime not found. Please check CDN script.')
      }
      
      return true
    }

    // Initialize PIXI Application
    const initializePixi = async () => {
      try {
        loadingStep.value = 'Checking Live2D runtime...'
        loadingProgress.value = 5
        await new Promise(resolve => setTimeout(resolve, 200))
        
        checkLive2DRuntime()
        
        loadingStep.value = 'Setting up graphics engine...'
        loadingProgress.value = 15
        await new Promise(resolve => setTimeout(resolve, 300))
        
        console.log('Creating PIXI application...')
        
        pixiApp = new PIXI.Application({
          view: pixiCanvas.value,
          width: 400,
          height: 600,
          backgroundColor: 0x000000,
          backgroundAlpha: 0,
          antialias: true,
        })

        loadingStep.value = 'Graphics engine ready!'
        loadingProgress.value = 25
        await new Promise(resolve => setTimeout(resolve, 300))
        
        console.log('PIXI application created successfully')
        await loadLive2DModel()
        
      } catch (error) {
        console.error('PIXI initialization error:', error)
        errorMessage.value = error.message
        loadingStep.value = `Error: ${error.message}`
        hasError.value = true
        isLoading.value = false
      }
    }

    // Load Live2D Model
    const loadLive2DModel = async () => {
      try {
        loadingStep.value = 'Preparing Live2D model...'
        loadingProgress.value = 30
        await new Promise(resolve => setTimeout(resolve, 300))
        
        loadingStep.value = 'Downloading model files...'
        loadingProgress.value = 50
        await new Promise(resolve => setTimeout(resolve, 500))
        
        console.log('Loading Live2D model...')
        
        const modelUrl = '/models/pachirisu anime girl - top half.model3.json'
        console.log('Model URL:', modelUrl)
        
        loadingStep.value = 'Processing model data...'
        loadingProgress.value = 70
        
        live2dModel = await Live2DModel.from(modelUrl)
        console.log('Live2D model loaded successfully:', live2dModel)
        
        loadingStep.value = 'Setting up animations...'
        loadingProgress.value = 85
        await new Promise(resolve => setTimeout(resolve, 300))
        
        // Add model to stage
        pixiApp.stage.addChild(live2dModel)
        
        // Scale and position the model
        const containerWidth = 400
        const containerHeight = 600
        
        // Scale model to fit container
        const scale = Math.min(
          containerWidth / live2dModel.width,
          containerHeight / live2dModel.height
        ) * 0.8
        
        live2dModel.scale.set(scale)
        
        // Center the model
        live2dModel.x = containerWidth / 2
        live2dModel.y = containerHeight * 0.9
        live2dModel.anchor.set(0.5, 1)
        
        console.log('Model positioned and scaled')
        
        loadingStep.value = 'Enabling interactions...'
        loadingProgress.value = 95
        await new Promise(resolve => setTimeout(resolve, 300))
        
        // Enable interaction
        live2dModel.interactive = true
        live2dModel.on('hit', (hitAreas) => {
          console.log('Model hit areas:', hitAreas)
          triggerRandomMotion()
        })
        
        loadingStep.value = 'Ready!'
        loadingProgress.value = 100
        await new Promise(resolve => setTimeout(resolve, 500))
        
        isLoading.value = false
        emit('model-loaded', true)
        
      } catch (error) {
        console.error('Failed to load Live2D model:', error)
        errorMessage.value = `Failed to load model: ${error.message}`
        loadingStep.value = `Model Error: ${error.message}`
        hasError.value = true
        isLoading.value = false
      }
    }

    // Trigger random motion
    const triggerRandomMotion = () => {
      if (live2dModel && live2dModel.internalModel && live2dModel.internalModel.motionManager) {
        const motionGroup = 'idle'
        live2dModel.motion(motionGroup)
        console.log(`Playing motion: ${motionGroup}`)
      }
    }

    // Retry loading
    const retryLoad = async () => {
      hasError.value = false
      isLoading.value = true
      loadingProgress.value = 0
      loadingStep.value = 'Retrying...'
      
      // Clean up previous instance
      if (pixiApp) {
        pixiApp.destroy(true, true)
        pixiApp = null
      }
      
      await nextTick()
      await initializePixi()
    }

    // Cleanup
    const cleanup = () => {
      if (pixiApp) {
        pixiApp.destroy(true, true)
        pixiApp = null
      }
      live2dModel = null
    }

    // Lifecycle
    onMounted(async () => {
      console.log('CompanionAvatar mounted - starting Live2D loading...')
      await nextTick()
      await initializePixi()
    })

    onUnmounted(() => {
      cleanup()
    })

    return {
      avatarContainer,
      pixiCanvas,
      isLoading,
      hasError,
      errorMessage,
      useRealModel,
      loadingProgress,
      loadingStep,
      retryLoad
    }
  }
}
</script>

<style scoped>
.companion-avatar {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}

.avatar-display {
  width: 100%;
  height: 100%;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}

.loading-screen {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2rem;
  color: white;
  text-align: center;
  min-width: 350px;
  z-index: 10;
}

.loading-spinner {
  width: 50px;
  height: 50px;
  border: 4px solid rgba(255, 255, 255, 0.3);
  border-top: 4px solid #ff6b9d;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.loading-content h3 {
  margin: 0 0 1rem 0;
  font-size: 1.5rem;
  font-weight: 600;
  color: #ff6b9d;
}

.progress-container {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.progress-bar {
  width: 100%;
  height: 8px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 4px;
  overflow: hidden;
  box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.2);
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #ff6b9d, #ff8fb3, #ffa726);
  border-radius: 4px;
  transition: width 0.3s ease;
  position: relative;
  overflow: hidden;
}

.progress-fill::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(
    90deg,
    transparent,
    rgba(255, 255, 255, 0.3),
    transparent
  );
  animation: shimmer 1.5s infinite;
}

.progress-text {
  align-self: flex-end;
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.8);
  font-weight: 500;
}

.loading-step {
  margin: 0;
  font-size: 1rem;
  color: rgba(255, 255, 255, 0.9);
  font-weight: 400;
  min-height: 1.2rem;
}

.error-display {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  color: white;
  text-align: center;
  min-width: 300px;
  z-index: 10;
}

.error-display h3 {
  color: #ff6b6b;
  margin-bottom: 0.5rem;
}

.retry-btn {
  padding: 0.5rem 1rem;
  background: #ff6b9d;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
}

.retry-btn:hover {
  background: #ff8fb3;
}

.live2d-canvas {
  width: 400px !important;
  height: 600px !important;
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}

.simple-avatar {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  color: white;
}

.fallback-message {
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.9rem;
}

.avatar-character {
  position: relative;
  height: 200px;
}

.character-head {
  position: relative;
  width: 80px;
  height: 100px;
  margin: 0 auto;
}

.hair {
  position: absolute;
  top: -5px;
  left: -5px;
  width: 90px;
  height: 60px;
  background: linear-gradient(145deg, #ffd700, #ffb347);
  border-radius: 50% 50% 45% 45%;
  z-index: 1;
}

.face {
  position: absolute;
  top: 15px;
  left: 5px;
  width: 70px;
  height: 80px;
  background: linear-gradient(145deg, #ffd6cc, #ffb3a0);
  border-radius: 50% 50% 45% 45%;
  z-index: 2;
}

.eyes {
  position: absolute;
  top: 25px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  gap: 15px;
}

.eye {
  width: 8px;
  height: 12px;
  background: #333;
  border-radius: 50%;
}

.mouth {
  position: absolute;
  top: 45px;
  left: 50%;
  transform: translateX(-50%);
  width: 15px;
  height: 8px;
  border: 2px solid #ff6b9d;
  border-top: none;
  border-radius: 0 0 15px 15px;
}

/* Animations */
@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

@keyframes shimmer {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(100%); }
}
</style>
