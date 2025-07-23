import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5173,
    host: 'localhost',
    cors: true,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '')
      },
      '/ws': {
        target: 'ws://localhost:8000',
        ws: true,
        changeOrigin: true
      }
    }
  },
  build: {
    outDir: 'dist',
    sourcemap: true,
    rollupOptions: {
      output: {
        manualChunks: {
          'live2d': ['pixi-live2d-display', 'pixi.js']
        }
      }
    }
  },
  resolve: {
    alias: {
      '@': '/src'
    }
  },
  define: {
    global: 'globalThis'
  },
  optimizeDeps: {
    include: ['pixi.js', 'pixi-live2d-display', 'vue']
  },
  assetsInclude: ['**/*.moc3', '**/*.model3.json', '**/*.cdi3.json', '**/*.physics3.json']
})
