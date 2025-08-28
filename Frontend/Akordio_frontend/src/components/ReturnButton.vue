<template>
  <button class="return-btn" @click="$emit('click')">
    <i class="fa fa-arrow-left fa-2x"></i>
  </button>
</template>

<script setup></script>

<style scoped>
.return-btn {
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border: none;
  padding: 1rem 1rem;
  border-radius: 8px;
  cursor: pointer;
  font-weight: bold;
  transition: background 0.2s;
}

.return-btn:hover {
  background: rgba(255, 255, 255, 0.35);
}
</style>
