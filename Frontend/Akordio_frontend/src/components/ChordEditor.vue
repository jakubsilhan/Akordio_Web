<template>
  <div class="flex flex-col w-full sm:w-3/4 lg:w-1/2 h-[50vh] mx-auto border rounded">
    <textarea class="p-2 sm:p-3 flex-1 text-sm sm:text-base resize-none" v-model="displayChords" spellcheck="false" />
    <div class="border-t flex flex-wrap sm:flex-nowrap items-center gap-2 p-2 h-12 sm:h-14">
      <p class="text-red-500 text-sm sm:text-base break-words flex-1 min-w-0">{{ warning }}</p>
      <button
        @click="saveEdits"
        class="py-1 px-3 sm:px-4 bg-blue-600 text-white text-sm sm:text-base rounded hover:bg-blue-500 active:scale-95 whitespace-nowrap"
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
