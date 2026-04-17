<template>
  <div class="flex flex-col h-screen">
    <!-- Header / Title Section -->
    <header class="h-1/3 flex items-center justify-center bg-blue-600 text-white text-center px-4">
      <h1 class="text-5xl sm:text-7xl md:text-8xl lg:text-9xl font-bold">Akordio</h1>
    </header>
    <!-- Content Section -->
    <main class="flex-1 flex flex-col items-center justify-start p-4 bg-gray-100">
      <nav class="flex flex-wrap justify-center gap-3 sm:gap-4 mt-2">
        <NavButton to="/online">Online</NavButton>
        <NavButton to="/fullsong">Fullsong</NavButton>
      </nav>
      <p class="text-gray-800 text-base sm:text-lg md:text-xl mt-2 text-center px-2">
        Welcome to Akordio - A chord recognition website
      </p>
    </main>
  </div>
</template>

<script setup>
import NavButton from '@/components/NavButton.vue'
</script>
