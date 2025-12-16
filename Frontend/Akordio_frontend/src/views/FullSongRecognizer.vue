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

      <p>
        {{ audioFile?.name || 'No file selected' }}
      </p>

      <!-- Audio Player -->
      <audio
        ref="audioplayerRef"
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
        <div title="Select the complexity of desired chords">
          <div class="flex flex-row space-x-2">
            <label class="block mb-1 font-medium">Model Choice:</label>
            <i class="fa fa-question-circle text-gray-300"></i>
          </div>
          <select v-model="modelChoice" class="border rounded p-2 w-full">
            <option v-for="m in models" :key="m" :value="m">{{ m }}</option>
          </select>
        </div>

        <!-- Guitar -->
        <div title="Select wich audio track to filter out">
          <div class="flex flex-row space-x-2">
            <label class="block mb-1 font-medium">Separation Choice:</label>
            <i class="fa fa-question-circle text-gray-300"></i>
          </div>
          <select v-model="separationChoice" class="border rounded p-2 w-full">
            <option v-for="m in separations" :key="m" :value="m">{{ m }}</option>
          </select>
        </div>
        <p class="p-1 text-white bg-orange-400 rounded">
          <strong>Warning!</strong> Using audio separation will take more time.
        </p>
      </div>
    </Modal>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { apiService } from '@/utils/api'
import { useLoading } from 'vue-loading-overlay'

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

const { audioFile, audioSrc, audioplayerRef, currentTime, handleAudioUpload, onTimeupdate } =
  useAudio()
const labFile = ref('')
const { chords, currentChord, nextChord, progressPercent } = useChords(labFile, currentTime)
const { downloadArchive } = useDownload()
const { uploadArchive } = useUpload()

// Loading screen
const $loading = useLoading()

// Modal state
const isModalOpen = ref(false)
const includeGuitar = ref(false)
const includeVocals = ref(false)
const models = ['majmin', 'majmin7', 'complex']
const separations = ['none', 'guitar', 'vocals', 'both']
const modelChoice = ref(models[0])
const separationChoice = ref(separations[0])

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

  const loader = $loading.show()

  // Annotation request
  // Build form data
  const annotData = new FormData()
  annotData.append('audio', audioFile.value)
  annotData.append('model_choice', modelChoice.value)

  // Request processing
  let labContent = null
  try {
    labContent = await apiService.post('fullsong/annotate', annotData, {
      responseType: 'text',
    })
  } catch (error) {
    console.error('No lab content received:', error.message)
    alert('Failed to annotate song!')
    return
  }

  labFile.value = labContent
  console.log('Lab file loaded.')

  // Separation request
  // Build form data
  if (separationChoice.value == 'none') {
    loader.hide()
    return
  }
  const sepData = new FormData()
  sepData.append('audio', audioFile.value)
  sepData.append('separation_choice', separationChoice.value)

  // Request separation
  let separatedAudio = null
  try {
    separatedAudio = await apiService.post('separation/filter', sepData, {
      responseType: 'blob',
    })
  } catch (error) {
    console.error('No audio received:', error.message)
    alert('Failed to separate instruments!')
    loader.hide()
    return
  }

  const originalName = audioFile.value.name || 'audio.wav'
  audioFile.value = new File([separatedAudio], originalName, { type: separatedAudio.type })
  audioSrc.value = URL.createObjectURL(audioFile.value)
  console.log('Audio separated')

  loader.hide()
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
