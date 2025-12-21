import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import '@/assets/colors.css'
import '@/assets/fonts.css'
import 'font-awesome/css/font-awesome.min.css'
import './assets/tailwind.css'
import { LoadingPlugin } from 'vue-loading-overlay'
import 'vue-loading-overlay/dist/css/index.css'
import Toast from 'vue-toastification'
import 'vue-toastification/dist/index.css'

const app = createApp(App)

app.use(router)

// Loading screen
app.use(LoadingPlugin)

// Toasts
const options = {
  position: 'bottom-left',
}
app.use(Toast, options)

app.mount('#app')
