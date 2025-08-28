<template>
  <div class="fullsong-page">
    <SmallHeader title="Fullsong Recognizer" />
    <main class="content">
      <p>
        Visit
        <a href="https://vuejs.org/" target="_blank" rel="noopener"> vuejs.org </a>
        to read the documentation.
      </p>
    </main>
  </div>
</template>

<script setup>
import SmallHeader from '@/components/SmallHeader.vue'
</script>

<style scoped>
.fullsong_page {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.content {
  flex: 1;
  padding: 2rem;
  text-align: center;
  font-size: 1.2 rem;
  color: var(--color-text);
}
</style>
