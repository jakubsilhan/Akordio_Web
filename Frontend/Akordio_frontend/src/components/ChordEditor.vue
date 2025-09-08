<template>
  <div class="flex flex-col w-1/2 h-[50vh] mx-auto border rounded">
    <textarea class="p-1 h-full" v-model="displayChords" spellcheck="false" />
    <div class="border-t flex">
      <p class="text-red-500 ml-1 my-1">{{ warning }}</p>
      <button
        @click="saveEdits"
        class="ml-auto mr-1 my-1 py-1 px-2 bg-blue-600 text-white rounded hover:bg-blue-500 active:scale-95"
      >
        Save
      </button>
    </div>
  </div>
</template>

<script setup>
import { watch, ref } from 'vue'
const chords = defineModel('chords')
const displayChords = ref('')
const warning = ref('')

watch(chords, (newChords) => {
  displayChords.value = newChords
})

// Check the input and warn if it's wrong
function saveEdits() {
  // TODO consider more complex check
  try {
    warning.value = ''
    const parsed = displayChords.value
      .trim()
      .split('\n')
      .map((line, idx) => {
        const [start, end, chord] = line.trim().split(/\s+/)
        if (!start || !end || !chord) {
          throw new Error(`Invalid format on line ${idx + 1}: "${line}"`)
        }
        return {
          start: parseFloat(start),
          end: parseFloat(end),
          chord,
        }
      })

    chords.value = displayChords.value
  } catch (err) {
    warning.value = 'Cannot parse edited chords!'
  }
}
</script>
