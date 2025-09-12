import { ref } from 'vue'

export function useAudio() {
  const audioFile = ref(null)
  const audioSrc = ref(null)
  const audioplayerRef = ref(null)
  const currentTime = ref(0)

  // Parses user input into a usable file and its url
  function handleAudioUpload(event) {
    const file = event.target.files[0]
    if (file) {
      audioFile.value = file
      audioSrc.value = URL.createObjectURL(file)
    }
    console.log('Audio uploaded:', file?.name)
  }

  // Uses audio element reference to get current time
  function onTimeupdate() {
    currentTime.value = audioplayerRef.value.currentTime
  }

  return { audioFile, audioSrc, audioplayerRef, currentTime, handleAudioUpload, onTimeupdate }
}
