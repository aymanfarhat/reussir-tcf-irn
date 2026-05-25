export function useAudioRecorder() {
  type RecorderStatus = 'ready' | 'unsupported' | 'attached' | 'recording' | 'cleared'

  const { t } = useI18n()
  const mediaRecorder = shallowRef<MediaRecorder | null>(null)
  const recording = ref(false)
  const audioBlob = shallowRef<Blob | null>(null)
  const audioUrl = ref('')
  const statusKey = ref<RecorderStatus>('ready')
  const status = computed(() => t(`audioRecorder.status.${statusKey.value}`))
  let chunks: BlobPart[] = []
  let stream: MediaStream | null = null

  async function start() {
    if (!navigator.mediaDevices || !window.MediaRecorder) {
      statusKey.value = 'unsupported'
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
      statusKey.value = 'attached'
    }
    mediaRecorder.value.start()
    recording.value = true
    statusKey.value = 'recording'
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
    statusKey.value = 'cleared'
  }

  function file(): File | null {
    if (!audioBlob.value) return null
    return new File([audioBlob.value], 'oral-answer.webm', { type: 'audio/webm' })
  }

  return { recording, audioBlob, audioUrl, status, start, stop, reset, file }
}
