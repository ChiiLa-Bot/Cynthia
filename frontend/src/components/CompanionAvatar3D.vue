<template>
  <div class="companion-avatar-3d">
    <div class="avatar-display" ref="avatarContainer">
      <!-- Loading Screen -->
      <div v-if="isLoading" class="loading-screen">
        <div class="loading-spinner"></div>
        <div class="loading-content">
          <h3>Loading Cynthia 3D...</h3>
          <div class="progress-container">
            <div class="progress-bar">
              <div class="progress-fill" :style="{ width: loadingProgress + '%' }"></div>
            </div>
            <span class="progress-text">{{ loadingProgress }}%</span>
          </div>
          <p class="loading-step">{{ loadingStep }}</p>
        </div>
      </div>

      <!-- 3D Canvas -->
      <canvas 
        v-show="!isLoading" 
        ref="threeCanvas" 
        class="three-canvas"
      ></canvas>

      <!-- Controls -->
      <div v-if="!isLoading" class="model-controls">
        <button @click="changeAnimation('idle')" class="control-btn">Idle</button>
        <button @click="changeAnimation('wave')" class="control-btn">Wave</button>
        <button @click="changeAnimation('dance')" class="control-btn">Dance</button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import * as THREE from 'three'
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js'
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js'

export default {
  name: 'CompanionAvatar3D',
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
    const threeCanvas = ref(null)

    // Reactive state
    const isLoading = ref(true)
    const loadingProgress = ref(0)
    const loadingStep = ref('Initializing 3D engine...')

    // Three.js variables
    let scene = null
    let camera = null
    let renderer = null
    let controls = null
    let model = null
    let mixer = null
    let currentAction = null
    let animationActions = {}

    // Initialize Three.js scene
    const initializeThreeJS = async () => {
      try {
        loadingStep.value = 'Setting up 3D scene...'
        loadingProgress.value = 10
        await new Promise(resolve => setTimeout(resolve, 300))

        // Create scene
        scene = new THREE.Scene()
        scene.background = new THREE.Color(0x1a1a1a)

        // Create camera
        camera = new THREE.PerspectiveCamera(
          50,
          400 / 600,
          0.1,
          1000
        )
        camera.position.set(0, 1.5, 3)

        loadingStep.value = 'Initializing renderer...'
        loadingProgress.value = 25
        await new Promise(resolve => setTimeout(resolve, 300))

        // Create renderer
        renderer = new THREE.WebGLRenderer({
          canvas: threeCanvas.value,
          antialias: true,
          alpha: true
        })
        renderer.setSize(400, 600)
        renderer.setPixelRatio(window.devicePixelRatio)
        renderer.shadowMap.enabled = true
        renderer.shadowMap.type = THREE.PCFSoftShadowMap

        // Create lights
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.6)
        scene.add(ambientLight)

        const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8)
        directionalLight.position.set(10, 10, 5)
        directionalLight.castShadow = true
        scene.add(directionalLight)

        loadingStep.value = 'Setting up controls...'
        loadingProgress.value = 40
        await new Promise(resolve => setTimeout(resolve, 300))

        // Create controls
        controls = new OrbitControls(camera, renderer.domElement)
        controls.enableDamping = true
        controls.dampingFactor = 0.05
        controls.maxDistance = 10
        controls.minDistance = 1

        console.log('Three.js scene initialized successfully')
        await loadOrCreate3DModel()

      } catch (error) {
        console.error('Three.js initialization error:', error)
        loadingStep.value = `3D Error: ${error.message}`
        // Create fallback model if initialization fails
        createFallbackModel()
      }
    }

    // Load or create 3D model
    const loadOrCreate3DModel = async () => {
      try {
        loadingStep.value = 'Creating 3D character...'
        loadingProgress.value = 60
        await new Promise(resolve => setTimeout(resolve, 500))

        // Create a simple 3D character using basic geometries
        createSimple3DCharacter()

        loadingStep.value = 'Setting up animations...'
        loadingProgress.value = 85
        await new Promise(resolve => setTimeout(resolve, 300))

        setupAnimations()

        loadingStep.value = 'Ready!'
        loadingProgress.value = 100
        await new Promise(resolve => setTimeout(resolve, 300))

        isLoading.value = false
        emit('model-loaded', true)
        
        // Start render loop
        animate()

      } catch (error) {
        console.error('3D model creation error:', error)
        createFallbackModel()
      }
    }

    // Create simple 3D character
    const createSimple3DCharacter = () => {
      const character = new THREE.Group()

      // Head
      const headGeometry = new THREE.SphereGeometry(0.3, 32, 32)
      const headMaterial = new THREE.MeshLambertMaterial({ color: 0xffd6cc })
      const head = new THREE.Mesh(headGeometry, headMaterial)
      head.position.y = 1.5
      head.castShadow = true
      character.add(head)

      // Hair
      const hairGeometry = new THREE.SphereGeometry(0.35, 32, 32)
      const hairMaterial = new THREE.MeshLambertMaterial({ color: 0xffd700 })
      const hair = new THREE.Mesh(hairGeometry, hairMaterial)
      hair.position.y = 1.6
      hair.scale.set(1, 0.8, 1)
      character.add(hair)

      // Eyes
      const eyeGeometry = new THREE.SphereGeometry(0.05, 16, 16)
      const eyeMaterial = new THREE.MeshLambertMaterial({ color: 0x333333 })
      
      const leftEye = new THREE.Mesh(eyeGeometry, eyeMaterial)
      leftEye.position.set(-0.1, 1.55, 0.25)
      character.add(leftEye)
      
      const rightEye = new THREE.Mesh(eyeGeometry, eyeMaterial)
      rightEye.position.set(0.1, 1.55, 0.25)
      character.add(rightEye)

      // Body
      const bodyGeometry = new THREE.CylinderGeometry(0.2, 0.3, 0.8, 32)
      const bodyMaterial = new THREE.MeshLambertMaterial({ color: 0xff6b9d })
      const body = new THREE.Mesh(bodyGeometry, bodyMaterial)
      body.position.y = 0.8
      body.castShadow = true
      character.add(body)

      // Arms
      const armGeometry = new THREE.CylinderGeometry(0.05, 0.08, 0.6, 16)
      const armMaterial = new THREE.MeshLambertMaterial({ color: 0xffd6cc })
      
      const leftArm = new THREE.Mesh(armGeometry, armMaterial)
      leftArm.position.set(-0.35, 1, 0)
      leftArm.rotation.z = 0.3
      character.add(leftArm)
      
      const rightArm = new THREE.Mesh(armGeometry, armMaterial)
      rightArm.position.set(0.35, 1, 0)
      rightArm.rotation.z = -0.3
      character.add(rightArm)

      // Legs
      const legGeometry = new THREE.CylinderGeometry(0.08, 0.1, 0.8, 16)
      const legMaterial = new THREE.MeshLambertMaterial({ color: 0xffd6cc })
      
      const leftLeg = new THREE.Mesh(legGeometry, legMaterial)
      leftLeg.position.set(-0.15, 0, 0)
      character.add(leftLeg)
      
      const rightLeg = new THREE.Mesh(legGeometry, legMaterial)
      rightLeg.position.set(0.15, 0, 0)
      character.add(rightLeg)

      model = character
      scene.add(model)

      console.log('Simple 3D character created')
    }

    // Setup animations
    const setupAnimations = () => {
      // Create basic animations using Three.js
      const clock = new THREE.Clock()
      
      animationActions.idle = () => {
        const time = clock.getElapsedTime()
        if (model) {
          model.rotation.y = Math.sin(time * 0.5) * 0.1
          model.position.y = Math.sin(time * 2) * 0.02
        }
      }
      
      animationActions.wave = () => {
        const time = clock.getElapsedTime()
        if (model && model.children[6]) { // Right arm
          model.children[6].rotation.z = -0.3 + Math.sin(time * 8) * 0.5
        }
      }
      
      animationActions.dance = () => {
        const time = clock.getElapsedTime()
        if (model) {
          model.rotation.y = Math.sin(time * 2) * 0.3
          model.position.y = Math.sin(time * 4) * 0.1
          model.scale.set(
            1 + Math.sin(time * 3) * 0.05,
            1 + Math.sin(time * 4) * 0.05,
            1 + Math.sin(time * 3) * 0.05
          )
        }
      }

      // Set default animation
      currentAction = animationActions.idle
    }

    // Create fallback model
    const createFallbackModel = () => {
      const geometry = new THREE.BoxGeometry(1, 2, 0.5)
      const material = new THREE.MeshLambertMaterial({ color: 0xff6b9d })
      model = new THREE.Mesh(geometry, material)
      model.position.y = 1
      scene.add(model)
      
      isLoading.value = false
      emit('model-loaded', false)
      animate()
    }

    // Change animation
    const changeAnimation = (animationName) => {
      if (animationActions[animationName]) {
        currentAction = animationActions[animationName]
        console.log(`Changed to ${animationName} animation`)
        emit('animation-complete', animationName)
      }
    }

    // Animation loop
    const animate = () => {
      requestAnimationFrame(animate)
      
      if (currentAction) {
        currentAction()
      }
      
      if (controls) {
        controls.update()
      }
      
      if (renderer && scene && camera) {
        renderer.render(scene, camera)
      }
    }

    // Cleanup
    const cleanup = () => {
      if (renderer) {
        renderer.dispose()
      }
      if (controls) {
        controls.dispose()
      }
    }

    // Lifecycle
    onMounted(async () => {
      console.log('3D Avatar mounted - starting 3D loading...')
      await nextTick()
      await initializeThreeJS()
    })

    onUnmounted(() => {
      cleanup()
    })

    return {
      avatarContainer,
      threeCanvas,
      isLoading,
      loadingProgress,
      loadingStep,
      changeAnimation
    }
  }
}
</script>

<style scoped>
.companion-avatar-3d {
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
  flex-direction: column;
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

.three-canvas {
  width: 400px !important;
  height: 600px !important;
  max-width: 100%;
  max-height: 100%;
  border-radius: 8px;
}

.model-controls {
  display: flex;
  gap: 0.5rem;
  margin-top: 1rem;
  flex-wrap: wrap;
  justify-content: center;
}

.control-btn {
  padding: 0.5rem 1rem;
  background: rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 20px;
  color: white;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
}

.control-btn:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: translateY(-2px);
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
