<template>
  <div v-if="show" class="fixed inset-0 flex items-center justify-center bg-black/50">
    <div class="bg-white p-6 rounded-lg shadow-lg w-125">
      <header class="flex justify-between items-center mb-4">
        <h2 class="text-lg font-semibold">{{ title }}</h2>
        <button @click="$emit('close')" class="text-gray-500 hover:text-gray-700">&times;</button>
      </header>

      <!-- Slot for dynamic form -->
      <div class="mb-4">
        <slot />
      </div>

      <footer class="flex justify-end space-x-2">
        <button
          @click="$emit('close')"
          class="px-4 py-2 bg-gray-300 rounded hover:bg-gray-200 active:scale-95"
        >
          Cancel
        </button>
        <button
          @click="$emit('confirm')"
          class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-500 active:scale-95"
        >
          Process
        </button>
      </footer>
    </div>
  </div>
</template>

<script setup>
defineProps({
  show: Boolean,
  title: {
    type: String,
    default: 'Process Options',
  },
})
</script>
