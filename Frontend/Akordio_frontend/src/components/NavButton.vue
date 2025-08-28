<template>
  <router-link v-if="to" :to="to" class="nav-btn">
    <slot />
  </router-link>

  <button v-else class="nav-btn" @click="$emit('click')">
    <slot />
  </button>
</template>

<script setup>
defineProps({
  to: {
    type: String,
    default: null,
  },
})
</script>

<style scoped>
.nav-btn {
  padding: 2rem 10rem;
  margin: 0.25rem;
  border: none;
  border-radius: 8px;
  background-color: var(--color-primary);
  color: white;
  font-weight: bold;
  font-size: larger;
  cursor: pointer;
  text-decoration: none;
  display: inline-block;
}

.nav-btn:hover {
  background-color: var(--color-secondary);
}
</style>
