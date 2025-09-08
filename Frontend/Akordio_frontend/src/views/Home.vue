<template>
  <div class="flex flex-col h-screen">
    <!-- Header / Title Section -->
    <header class="h-1/3 flex items-center justify-center bg-blue-600 text-white text-center">
      <h1 class="text-9xl font-bold">Akordio</h1>
    </header>

    <!-- Content Section -->
    <main class="flex-1 flex flex-col items-center justify-start p-4 bg-gray-100">
      <nav class="flex space-x-4 mt-2">
        <NavButton to="/online">Online</NavButton>
        <NavButton to="/fullsong">Fullsong</NavButton>
      </nav>

      <p class="text-gray-800 text-xl mt-2 text-center">
        Welcome to Akordio - A chord recognition website
      </p>
    </main>
  </div>
</template>

<script setup>
import NavButton from '@/components/NavButton.vue'
</script>
