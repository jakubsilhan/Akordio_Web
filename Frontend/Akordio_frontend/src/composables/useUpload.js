import JSZip from 'jszip'
import { saveAs } from 'file-saver'

export function useUpload() {
  // Parse archive into audio and lab file
  async function uploadArchive(archive) {
    // Initialization
    const zip = await JSZip.loadAsync(archive)
    let audioFile = null
    let audioName = null
    let labFile = null
    let labName = null

    // Cycle through archive files
    for (const [filename, entry] of Object.entries(zip.files)) {
      if (filename.endsWith('.lab')) {
        labFile = await entry.async('string')
        labName = filename
      } else if (
        filename.endsWith('.mp3') ||
        filename.endsWith('.wav') ||
        filename.endsWith('.m4a') ||
        filename.endsWith('.flac') ||
        filename.endsWith('.aac') ||
        filename.endsWith('.wma') ||
        filename.endsWith('.ogg')
      ) {
        audioFile = await entry.async('blob')
        audioName = filename
      }
    }

    // Safety checks
    if (!audioFile || !labFile) {
      throw new Error('Archive must contain both audio and lab file!')
    }

    if (labName.split('.')[0] != audioName.split('.')[0]) {
      throw new Error('Audio and lab file need to match!')
    }

    return {
      audioFile: new File([audioFile], audioName),
      labFile: labFile,
    }
  }

  return { uploadArchive }
}
