<template>
  <div class="home-page">
    <!-- Header / Title Section -->
    <header class="header">
      <h1 class="title">Akordio</h1>
    </header>

    <!-- Content Section -->
    <main class="content">
      <nav class="nav">
        <NavButton to="/online">Online</NavButton>
        <NavButton to="/fullsong">Fullsong</NavButton>
      </nav>

      <p class="description">Welcome to Akordio - A chord recognition website</p>
    </main>
  </div>
</template>

<script setup>
import NavButton from '@/components/NavButton.vue'
</script>

<style scoped>
.home-page {
  display: flex;
  flex-direction: column;
  height: 100vh;
}

.header {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, var(--color-primary), var(--color-secondary));
  color: white;
  text-align: center;
}

.title {
  font-size: 8rem;
  font-weight: bold;
}

.content {
  flex: 2;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: start;
  padding: 2rem;
  background-color: #f9f9f9;
}

.nav {
  margin-bottom: 1.5rem;
}

.description {
  font-size: 1.2rem;
  color: #333;
  max-width: 600px;
  text-align: center;
}
</style>
