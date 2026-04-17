<template>
  <div
    class="inline-flex flex-col sm:flex-row justify-center items-center gap-2 sm:gap-2 py-4 px-4 sm:px-8 border border-black rounded-xl"
  >
    <!-- Upload Audio -->
    <button
      class="w-full sm:w-auto py-2 px-4 bg-blue-600 text-white rounded hover:bg-blue-500 active:scale-95"
      @click="triggerAudioUpload"
    >
      Upload Audio
    </button>
    <input
      type="file"
      accept="audio/*"
      ref="audioInput"
      class="hidden"
      @change="props.onUploadAudio"
    />
    <!-- Process -->
    <button
      class="w-full sm:w-auto py-2 px-4 bg-blue-600 text-white rounded hover:bg-blue-500 active:scale-95"
      @click="props.onProcess"
    >
      Process
    </button>
    <button
      class="w-full sm:w-auto py-2 px-4 bg-blue-600 text-white rounded hover:bg-blue-500 active:scale-95"
      @click="onDownload"
    >
      Download Processed
    </button>
    <!-- Upload Archive -->
    <button
      class="w-full sm:w-auto py-2 px-4 bg-blue-600 text-white rounded hover:bg-blue-500 active:scale-95"
      @click="triggerArchiveUpload"
    >
      Upload Processed
    </button>
    <input
      type="file"
      accept=".zip,.tar,.rar"
      ref="archiveInput"
      class="hidden"
      @change="props.onUploadArchive"
    />
  </div>
</template>

<script setup>
import { ref } from 'vue'
const props = defineProps({
  onUploadAudio: { type: Function, required: true },
  onProcess: { type: Function, required: true },
  onDownload: { type: Function, required: true },
  onUploadArchive: { type: Function, required: true },
})

// Refs for hidden file inputs
const audioInput = ref(null)
const archiveInput = ref(null)

function triggerAudioUpload() {
  audioInput.value.click()
}
function triggerArchiveUpload() {
  archiveInput.value.click()
}
</script>
