<template>
  <div class="flex flex-col min-h-screen">
    <SmallHeader title="Fullsong Recognizer" />
    <main class="flex-1 p-4 sm:p-6 md:p-8 text-center text-base sm:text-lg md:text-[1.2rem]">
      <Toolbar
        :onUploadAudio="handleAudioUpload"
        :onProcess="handleProcess"
        :onDownload="handleDownload"
        :onUploadArchive="handleArchiveUpload"
      />
      <p class="px-2 break-words">
        {{ audioFile?.name || 'No file selected' }}
      </p>
      <!-- Audio Player -->
      <audio
        ref="audioplayerRef"
        :src="audioSrc"
        controls
        @timeupdate="onTimeupdate"
        class="mt-4 mx-auto w-full max-w-md"
      ></audio>
      <!-- Current Chord -->
      <div class="mt-6 text-2xl sm:text-3xl md:text-4xl font-bold">
        Current: <br />
        {{ currentChord?.chord || '—' }}
      </div>
      <!-- Progress to Next -->
      <div class="w-full max-w-md mx-auto bg-gray-200 rounded-full h-2 mt-2 overflow-hidden">
        <div
          class="bg-blue-600 h-full rounded-full transition-all duration-200"
          :style="{ width: progressPercent + '%' }"
        ></div>
      </div>
      <!-- Next Chord -->
      <div class="mt-2 text-sm sm:text-base text-gray-600">
        Next: <br />
        <span class="font-semibold">{{ nextChord?.chord || '—' }}</span>
      </div>
      <!-- Chord Editor -->
      <ChordEditor class="mt-6 sm:mt-8 md:mt-10" v-model:chords="labFile" />
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
          <div class="flex flex-row items-center space-x-2">
            <label class="block mb-1 font-medium text-sm sm:text-base">Model Choice:</label>
            <i class="fa fa-question-circle text-gray-300"></i>
          </div>
          <select v-model="modelChoice" class="border rounded p-2 w-full text-sm sm:text-base">
            <option v-for="m in modelOptions" :key="m.value" :value="m.value">
              {{ m.label }}
            </option>
          </select>
          <p v-if="selectedModelDescription" class="text-xs sm:text-sm text-gray-600 mt-1 text-left pl-2">
            {{ selectedModelDescription }}
          </p>
        </div>

        <!-- Separation choice -->
        <div title="Select which audio track to filter out">
          <div class="flex flex-row items-center space-x-2">
            <label class="block mb-1 font-medium text-sm sm:text-base">Separation Choice:</label>
            <i class="fa fa-question-circle text-gray-300"></i>
          </div>
          <select v-model="separationChoice" class="border rounded p-2 w-full text-sm sm:text-base">
            <option v-for="s in separationOptions" :key="s.value" :value="s.value">
              {{ s.label }}
            </option>
          </select>
          <p v-if="selectedSeparationDescription" class="text-xs sm:text-sm text-gray-600 mt-1 text-left pb-2 pl-2">
            {{ selectedSeparationDescription }}
          </p>
          <p class="p-2 sm:p-3 text-sm sm:text-base text-white bg-orange-400 rounded">
            <strong>Warning!</strong> Using audio separation will take more time.
          </p>
        </div>
      </div>
    </Modal>
  </div>
</template>

<script setup>
import { ref, onUnmounted, computed } from 'vue'
import { apiService } from '@/utils/api'
import { useLoading } from 'vue-loading-overlay'
import { useToast } from 'vue-toastification'

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

// Processing visuals
const $loading = useLoading()
const toast = useToast()

// Processing state
const currentProcessId = ref(0)
const taskId = ref(null)

// Modal state
const isModalOpen = ref(false)
const modelOptions = [
  { value: 'majmin', label: 'majmin', description: 'Basic major and minor chords only' },
  { value: 'majmin7', label: 'majmin7', description: 'Major, minor, and 7th chords (maj7, min7 and 7)' },
  { value: 'complex', label: 'complex', description: 'All chord types (augmented, diminished, sus, etc.)' }
]

const separationOptions = [
  { value: 'none', label: 'none', description: 'No audio separation' },
  { value: 'guitar', label: 'guitar', description: 'Remove guitar track' },
  { value: 'vocals', label: 'vocals', description: 'Remove vocals, keep instruments' },
  { value: 'both', label: 'both', description: 'Remove both guitar and vocals' }
]
const modelChoice = ref(modelOptions[0].value)
const separationChoice = ref(separationOptions[0].value)

const selectedModelDescription = computed(() => 
  modelOptions.find(m => m.value === modelChoice.value)?.description
)

const selectedSeparationDescription = computed(() => 
  separationOptions.find(s => s.value === separationChoice.value)?.description
)

onUnmounted(() => {
  currentProcessId.value++ // Kill any current processing
  cancelTaskById(taskId.value)
})

// Backend communication
async function confirmProcess() {
  /**
   * All of processing
   */
  if (!audioFile.value) {
    console.error('No audio file selected!')
    return
  }

  // Processing state
  const myProcessId = ++currentProcessId.value
  cancelTaskById(taskId.value)

  // Display
  isModalOpen.value = false
  const loader = $loading.show()

  // Annotation request
  // Build form data
  const annotData = new FormData()
  annotData.append('audio', audioFile.value)
  annotData.append('model_choice', modelChoice.value)

  // Request processing
  try {
    const annotationTask = await apiService.post('fullsong/annotate', annotData, {
      responseType: 'json',
    })
    taskId.value = annotationTask.task_id
  } catch (error) {
    console.error('Annotation start failed:', error.message)
    toast.error('Failed to start annotation!')
    return
  }
  console.log('Annotation task sent!')

  // Querying
  const annotToastId = toast.info('Annotation in progress!', {
    timeout: false,
    closeOnClick: false,
    closeButton: false,
    draggable: false,
  })
  await queryAnnotation(taskId.value, annotToastId, myProcessId)

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
  try {
    const separationTask = await apiService.post('separation/filter', sepData, {
      responseType: 'json',
    })
    taskId.value = separationTask.task_id
  } catch (error) {
    console.error('Separation start failed:', error.message)
    toast.error('Failed to start separation!')
    return
  }
  console.log('Task sent!')
  loader.hide()

  // Querying
  const sepToastId = toast.info('Separation in progress!', {
    timeout: false,
    closeOnClick: false,
    closeButton: false,
    draggable: false,
  })
  querySeparation(taskId.value, sepToastId, myProcessId)
}

async function queryAnnotation(annotationId, toastId, processId) {
  let labContent = null
  while (true) {
    if (processId !== currentProcessId.value) {
      toast.dismiss(toastId)
      return
    }
    try {
      // Querry
      const data = await apiService.get(`fullsong/annotate/${annotationId}`)

      // Check status
      if (data.status === 'COMPLETED') {
        labContent = data.result
        console.log('Task completed!')
        labFile.value = labContent
        console.log('Lab file loaded.')
        toast.update(toastId, {
          content: 'Annotation finished',
          options: {
            type: 'success',
            timeout: 5000,
            closeOnClick: true,
          },
        })
        taskId.value = null
        break
      }

      if (data.status === 'PROCESSING') {
        await new Promise((resolve) => setTimeout(resolve, 2000)) // non blocking wait
        console.log('Task processing!')
        continue
      }
    } catch (err) {
      console.error('Polling failed:', err)
      toast.update(toastId, {
        content: 'Checking for annotation result failed!',
        options: {
          type: 'error',
          timeout: 5000,
          closeOnClick: true,
        },
      })
      taskId.value = null
      break
    }
  }
}

// Query for separation result
async function querySeparation(separationId, toastId, processId) {
  while (true) {
    if (processId !== currentProcessId.value) {
      toast.dismiss(toastId)
      return
    }
    try {
      const response = await apiService.get(
        `separation/filter/${separationId}`,
        {},
        { responseType: 'blob' },
      )

      // Check if JSON for status
      if (response.type === 'application/json') {
        const text = await response.text()
        const statusData = JSON.parse(text)

        if (statusData.status === 'PROCESSING') {
          console.log('Task processing!')
          // 2 second query pause
          await new Promise((resolve) => setTimeout(resolve, 2000))
          continue
        }
      }

      // Parse audio blob
      const originalName = audioFile.value?.name || 'audio.mp3'
      audioFile.value = new File([response], originalName, { type: 'audio/mpeg' })
      audioSrc.value = URL.createObjectURL(audioFile.value)

      console.log('Task completed!')
      toast.update(toastId, {
        content: 'Separation finished',
        options: {
          type: 'success',
          timeout: 5000,
          closeOnClick: true,
        },
      })
      taskId.value = null
      break
    } catch (err) {
      console.error('Polling failed:', err)
      toast.update(toastId, {
        content: 'Checking for separation result failed!',
        options: {
          type: 'error',
          timeout: 5000,
          closeOnClick: true,
        },
      })
      taskId.value = null
      break
    }
  }
}

// Handlers
function handleProcess() {
  /**
   * Display modal for processing selection
   */
  if (!audioFile.value) {
    console.error('No audio file selected!')
    alert('Select audio')
    return
  }
  isModalOpen.value = true
}

async function handleDownload(event) {
  /**
   * Download processed files
   */
  try {
    downloadArchive(audioFile.value, labFile.value)
  } catch (err) {
    alert(err.message)
    console.log(err.message)
  }
}

async function handleArchiveUpload(event) {
  /**
   * Upload previously processed files
   */
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

async function cancelTaskById(CancelId) {
  /**
   * Cancel task by its ID
   */
  if (!CancelId) return
  taskId.value = null

  try {
    const response = await apiService.post(`tasks/${CancelId}/cancel`)
    console.log('Task cancelled')
    toast.info(`Task cancelled`)
  } catch (err) {
    console.error('Failed to cancel task:', err)
    toast.error(`Failed to cancel task`)
  }
}
</script>
