import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import '@/assets/colors.css'
import '@/assets/fonts.css'
import 'font-awesome/css/font-awesome.min.css'
import './assets/tailwind.css'
import { LoadingPlugin } from 'vue-loading-overlay'
import 'vue-loading-overlay/dist/css/index.css'

const app = createApp(App)

app.use(router)
app.use(LoadingPlugin)

app.mount('#app')
