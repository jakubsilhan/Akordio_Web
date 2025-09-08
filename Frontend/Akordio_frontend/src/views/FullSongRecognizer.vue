<template>
  <div class="flex flex-col min-h-screen">
    <SmallHeader title="Fullsong Recognizer" />

    <main class="flex-1 p-8 text-center text-[1.2rem]">
      <Toolbar
        :onUploadAudio="handleAudioUpload"
        :onProcess="handleProcess"
        :onDownload="handleDownload"
        :onUploadArchive="handleArchiveUpload"
      />

      <!-- Audio Player -->
      <audio
        ref="audioRef"
        :src="audioSrc"
        controls
        @timeupdate="onTimeupdate"
        class="mt-4 mx-auto"
      ></audio>

      <!-- Current Chord -->
      <div class="mt-6 text-4xl font-bold">
        Current: <br />
        {{ currentChord?.chord || '—' }}
      </div>

      <!-- Progress to Next -->
      <div class="w-full bg-gray-200 rounded-full h-2 mt-2 overflow-hidden">
        <div
          class="bg-blue-600 h-full rounded-full transition-all duration-200"
          :style="{ width: progressPercent + '%' }"
        ></div>
      </div>

      <!-- Next Chord -->
      <div class="mt-2 text-gray-600">
        Next: <br />
        <span class="font-semibold">{{ nextChord?.chord || '—' }}</span>
      </div>

      <!-- Chord Editor -->
      <ChordEditor class="mt-10" v-model:chords="labFile" />
    </main>

    <!-- Processing Modal -->
    <Modal
      :show="isModalOpen"
      title="Processing Options"
      @close="isModalOpen = false"
      @confirm="confirmProcess"
    >
      <div class="space-y-4">
        <!-- Model choice -->
        <div>
          <label class="block mb-1 font-medium">Model Choice:</label>
          <select v-model="modelChoice" class="border rounded p-2 w-full">
            <option disabled value="">-- Select a model --</option>
            <option v-for="m in models" :key="m" :value="m">{{ m }}</option>
          </select>
        </div>

        <!-- Guitar -->
        <label class="flex items-center space-x-2">
          <input type="checkbox" v-model="includeGuitar" />
          <span>Include Guitar</span>
        </label>

        <!-- Vocals -->
        <label class="flex items-center space-x-2">
          <input type="checkbox" v-model="includeVocals" />
          <span>Include Vocals</span>
        </label>
      </div>
    </Modal>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { apiText } from '@/utils/api'

// Components
import SmallHeader from '@/components/SmallHeader.vue'
import Toolbar from '@/components/Toolbar.vue'
import Modal from '@/components/Modal.vue'
import ChordEditor from '@/components/ChordEditor.vue'

// Composables
import { useAudio } from '@/composables/useAudio'
import { useChords } from '@/composables/useChords'
import { useDownload } from '@/composables/useDownload'
import { useUpload } from '@/composables/useUpload'

const { audioFile, audioSrc, audioRef, currentTime, handleAudioUpload, onTimeupdate } = useAudio()
const labFile = ref('')
const { chords, currentChord, nextChord, progressPercent } = useChords(labFile, currentTime)
const { downloadArchive } = useDownload()
const { uploadArchive } = useUpload()

// Modal state
const isModalOpen = ref(false)
const modelChoice = ref('')
const includeGuitar = ref(false)
const includeVocals = ref(false)
const models = ['majmin', 'sevenths', 'complex'] // example

// Show modal
function handleProcess() {
  if (!audioFile.value) {
    console.error('No audio file selected!')
    alert('Select audio')
    return
  }
  isModalOpen.value = true
}

// Request processing from backend
async function confirmProcess() {
  if (!audioFile.value) {
    console.error('No audio file selected!')
    return
  }
  isModalOpen.value = false

  // Build form data
  const formData = new FormData()
  formData.append('audio', audioFile.value)
  formData.append('model_choice', modelChoice.value)

  // Request processing
  const labContent = await apiText('fullsong/annotate', formData, 'POST', true)

  // Safety check
  if (!labContent) {
    console.error('No lab content received')
    return
  }

  labFile.value = labContent
  console.log('Lab file loaded.')
}

async function handleDownload(event) {
  try {
    downloadArchive(audioFile.value, labFile.value)
  } catch (err) {
    alert(err.message)
    console.log(err.message)
  }
}

async function handleArchiveUpload(event) {
  try {
    const archive = event.target.files[0]
    const files = await uploadArchive(archive)
    audioFile.value = files.audioFile
    labFile.value = files.labFile

    audioSrc.value = URL.createObjectURL(audioFile.value)
  } catch (err) {
    console.log(err.message)
  }
}
</script>
