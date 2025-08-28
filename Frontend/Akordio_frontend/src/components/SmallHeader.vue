<template>
  <header class="small-header">
    <ReturnButton @click="goBack" />
    <h1 class="title">{{ title }}</h1>
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

<style scoped>
.small-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding: 1rem 2rem;
  background: linear-gradient(135deg, var(--color-primary), var(--color-secondary));
  color: white;
}

.title {
  font-size: 2.5rem;
  font-weight: bold;
}
</style>
