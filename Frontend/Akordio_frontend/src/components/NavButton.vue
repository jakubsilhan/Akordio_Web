<template>
  <router-link
    v-if="to"
    :to="to"
    class="py-4 px-8 rounded bg-blue-600 text-white font-bold text-5xl hover:bg-blue-500 active:scale-95"
  >
    <slot />
  </router-link>

  <button
    v-else
    class="py-4 px-8 rounded bg-blue-600 text-white font-bold text-5xl hover:bg-blue-500 active:scale-95"
    @click="$emit('click')"
  >
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
