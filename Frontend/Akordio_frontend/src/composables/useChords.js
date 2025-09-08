import { ref, computed, watch } from 'vue'

export function useChords(labFile, currentTime) {
  const chords = ref([])

  // Calculate current chord based on current time
  const currentChord = computed(() =>
    chords.value.find((c) => currentTime.value >= c.start && currentTime.value < c.end),
  )

  // Calculate next chord based on current chord
  const nextChord = computed(() => {
    if (!currentChord.value) return null
    const idx = chords.value.indexOf(currentChord.value)
    return chords.value[idx + 1] || null
  })

  // Calculate progress percentage for chord
  const progressPercent = computed(() => {
    if (!currentChord.value) return 0
    const { start, end } = currentChord.value
    return ((currentTime.value - start) / (end - start)) * 100
  })

  // Watch for new lab file
  watch(labFile, (newLab) => {
    chords.value = newLab
      .trim()
      .split('\n')
      .map((line) => {
        const [start, end, chord] = line.split(' ')
        return { start: parseFloat(start), end: parseFloat(end), chord }
      })
  })

  return { chords, currentChord, nextChord, progressPercent }
}
