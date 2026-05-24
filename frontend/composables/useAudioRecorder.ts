export function useAudioRecorder() {
  const mediaRecorder = shallowRef<MediaRecorder | null>(null)
  const recording = ref(false)
  const audioBlob = shallowRef<Blob | null>(null)
  const audioUrl = ref('')
  const status = ref('Recorder ready. You can also type a manual transcript.')
  let chunks: BlobPart[] = []
  let stream: MediaStream | null = null

  async function start() {
    if (!navigator.mediaDevices || !window.MediaRecorder) {
      status.value = 'Recording is not supported in this browser. Use the manual transcript.'
      return
    }
    stream = await navigator.mediaDevices.getUserMedia({ audio: true })
    chunks = []
    mediaRecorder.value = new MediaRecorder(stream)
    mediaRecorder.value.ondataavailable = (event) => chunks.push(event.data)
    mediaRecorder.value.onstop = () => {
      audioBlob.value = new Blob(chunks, { type: 'audio/webm' })
      audioUrl.value = URL.createObjectURL(audioBlob.value)
      stream?.getTracks().forEach((track) => track.stop())
      status.value = 'Recording attached. Submit when ready.'
    }
    mediaRecorder.value.start()
    recording.value = true
    status.value = 'Recording...'
  }

  function stop() {
    if (mediaRecorder.value && recording.value) {
      mediaRecorder.value.stop()
      recording.value = false
    }
  }

  function reset() {
    chunks = []
    audioBlob.value = null
    audioUrl.value = ''
    status.value = 'Recording cleared. Start again or type a manual transcript.'
  }

  function file(): File | null {
    if (!audioBlob.value) return null
    return new File([audioBlob.value], 'oral-answer.webm', { type: 'audio/webm' })
  }

  return { recording, audioBlob, audioUrl, status, start, stop, reset, file }
}
