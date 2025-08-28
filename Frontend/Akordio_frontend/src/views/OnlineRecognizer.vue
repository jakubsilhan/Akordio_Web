<template>
  <div class="online-page">
    <SmallHeader title="Online Recognizer" />

    <main class="content">
      <div class="controls">
        <select v-model="modelChoice">
          <option value="majmin">Maj/Min</option>
          <option value="majmin7">Maj/Min7</option>
          <option value="complex">Complex</option>
        </select>

        <button @click="startRecording" :disabled="isRecording">Start Recording</button>
        <button @click="stopRecording" :disabled="!isRecording">Stop Recording</button>
      </div>

      <div v-if="chord" class="result">
        <p>
          Recognized Chord: <strong>{{ chord }}</strong>
        </p>
      </div>
    </main>
  </div>
</template>

<script>
import SmallHeader from '@/components/SmallHeader.vue'

export default {
  components: { SmallHeader },
  data() {
    return {
      recorder: null,
      stream: null,
      isRecording: false,
      modelChoice: 'majmin',
      chord: null,
      uploading: false,
    }
  },
  methods: {
    async startRecording() {
      try {
        // Get mic
        this.stream = await navigator.mediaDevices.getUserMedia({ audio: true })

        // Initialize values
        this.isRecording = true
        this.uploading = false

        const recordChunk = async () => {
          if (!this.isRecording) return
          // Initialize MediaRecorder and chunks
          const recorder = new MediaRecorder(this.stream, { mimeType: 'audio/ogg' })
          const chunks = []

          // Aggregate data for chunk
          recorder.ondataavailable = (e) => {
            if (e.data.size > 0) chunks.push(e.data)
          }

          // Send finalized data upon stopping
          recorder.onstop = async () => {
            const blob = new Blob(chunks, { type: 'audio/ogg' })
            const formData = new FormData()
            formData.append('audio', blob, 'recording.ogg')
            formData.append('model_choice', this.modelChoice)

            this.uploading = true
            try {
              const result = await this.$root.apiCall('online/recognize', formData, 'POST', true)
              if (result && result.chord) {
                this.chord = result.chord
              }
            } catch (err) {
              console.error('API call error:', err)
            } finally {
              this.uploading = false
            }

            // Schedule the next chunk recording
            recordChunk()
          }

          // Start recording
          recorder.start()

          // Stop the recorder to finalize clip
          setTimeout(() => recorder.stop(), 500)
        }

        // Start the first chunk
        recordChunk()
      } catch (err) {
        console.error('Recording error:', err)
      }
    },

    stopRecording() {
      if (this.recorder) {
        this.recorder.stop()
        this.stream.getTracks().forEach((track) => track.stop())
      }
      this.isRecording = false
    },
  },
}
</script>

<style scoped>
.online-page {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.content {
  flex: 1;
  padding: 2rem;
  text-align: center;
  font-size: 1.2rem;
  color: var(--color-text);
}

.controls {
  margin-bottom: 1rem;
}

button {
  margin: 0.5rem;
  padding: 0.7rem 1.5rem;
  font-size: 1rem;
  border: none;
  border-radius: 0.5rem;
  cursor: pointer;
}

.result {
  margin-top: 2rem;
  font-size: 1.4rem;
}
</style>
