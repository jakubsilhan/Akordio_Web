import JSZip from 'jszip'
import { saveAs } from 'file-saver'

export function useDownload() {
  // Archive audio and lab into zip and trigger download
  async function downloadArchive(audioFile, labFile) {
    if (!audioFile || !labFile) {
      throw new Error('Bot audio and lab file must be available!')
    }

    const zip = new JSZip()
    zip.file(audioFile.name, audioFile)
    zip.file(audioFile.name.replace(/\.[^/.]+$/, '') + '.lab', labFile)

    const content = await zip.generateAsync({ type: 'blob' })
    saveAs(content, audioFile.name.split('.')[0] + '.zip')
  }

  return { downloadArchive }
}
