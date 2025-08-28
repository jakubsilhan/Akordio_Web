import { createRouter, createWebHistory } from 'vue-router'
import FullSongRecognizer from '@/views/FullSongRecognizer.vue'
import OnlineRecognizer from '@/views/OnlineRecognizer.vue'
import Home from '@/views/Home.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', component: Home },
    { path: '/online', component: OnlineRecognizer },
    { path: '/fullsong', component: FullSongRecognizer },
  ],
})

export default router
