import { createApp } from 'vue'
import App from './App.vue'
import './style.css'

console.log('Starting Vue app...')

const app = createApp(App)
app.mount('#app')

console.log('Vue app mounted!')
