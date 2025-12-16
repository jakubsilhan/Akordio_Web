<template>
  <div class="flex flex-col min-h-screen">
    <SmallHeader title="Online Recognizer" />

    <main class="flex-1 p-8 text-center text-gray-800">
      <!-- Controls -->
      <div class="mb-4 flex flex-col md:flex-row justify-center items-center gap-4">
        <select v-model="modelChoice" class="border rounded-md px-4 py-2 text-lg">
          <option value="majmin">Maj/Min</option>
          <option value="majmin7">Maj/Min7</option>
          <option value="complex">Complex</option>
        </select>

        <button
          @click="startRecording"
          :disabled="isRecording"
          class="bg-blue-600 text-white px-6 py-2 rounded-md disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Start Recording
        </button>

        <button
          @click="stopRecording"
          :disabled="!isRecording"
          class="bg-red-600 text-white px-6 py-2 rounded-md disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Stop Recording
        </button>
      </div>

      <!-- Result -->
      <div class="mt-8 text-xl">
        <p>
          Recognized Chord: <br /><strong>{{ chord || '—' }}</strong>
        </p>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import SmallHeader from '@/components/SmallHeader.vue'
import { apiService } from '@/utils/api'

const recorder = ref(null)
const stream = ref(null)
const isRecording = ref(false)
const chord = ref(null)
const uploading = ref(false)
const modelChoice = ref('majmin')

async function startRecording() {
  try {
    stream.value = await navigator.mediaDevices.getUserMedia({ audio: true })
    isRecording.value = true
    uploading.value = false

    const recordChunk = async () => {
      if (!isRecording.value) return

      recorder.value = new MediaRecorder(stream.value, { mimeType: 'audio/ogg' })
      const chunks = []

      recorder.value.ondataavailable = (e) => {
        if (e.data.size > 0) chunks.push(e.data)
      }

      recorder.value.onstop = async () => {
        const blob = new Blob(chunks, { type: 'audio/ogg' })
        const formData = new FormData()
        formData.append('audio', blob, 'recording.ogg')
        formData.append('model_choice', modelChoice.value)

        uploading.value = true
        let result = null
        try {
          result = await apiService.post('online/recognize', formData, {
            responseType: 'json',
          })
        } catch (error) {
          console.error('Failed to recognize chord:', error.message)
        }
        if (result && result.chord) chord.value = result.chord
        uploading.value = false

        recordChunk()
      }

      recorder.value.start()
      setTimeout(() => recorder.value.stop(), 500)
    }

    recordChunk()
  } catch (err) {
    console.error('Recording error:', err)
  }
}

function stopRecording() {
  if (recorder.value) recorder.value.stop()
  if (stream.value) stream.value.getTracks().forEach((track) => track.stop())
  isRecording.value = false
}
</script>
