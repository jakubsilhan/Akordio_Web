<template>
  <header class="flex items-center justify-between bg-blue-600 text-white px-4 py-8">
    <ReturnButton @click="goBack" />
    <h1 class="text-3xl font-bold">{{ title }}</h1>
  </header>
</template>

<script setup>
import { useRouter } from 'vue-router'
import ReturnButton from '@/components/ReturnButton.vue'

const props = defineProps({
  title: {
    type: String,
    default: 'Page Title',
  },
})

const router = useRouter()

function goBack() {
  router.back()
}
</script>
