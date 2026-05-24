export function useCountdown(deadline: Ref<string | null | undefined> | string | null | undefined) {
  const now = ref(Date.now())
  let interval: ReturnType<typeof setInterval> | null = null
  const deadlineRef = isRef(deadline) ? deadline : ref(deadline)

  const remainingMs = computed(() => {
    if (!deadlineRef.value) return 0
    return Math.max(0, new Date(deadlineRef.value).getTime() - now.value)
  })
  const expired = computed(() => remainingMs.value <= 0)
  const timeLabel = computed(() => {
    if (!deadlineRef.value) return '--:--'
    if (expired.value) return 'Time expired'
    const minutes = Math.floor(remainingMs.value / 60000)
    const seconds = Math.floor((remainingMs.value % 60000) / 1000)
    return `${minutes}:${seconds.toString().padStart(2, '0')}`
  })

  onMounted(() => {
    interval = setInterval(() => {
      now.value = Date.now()
    }, 1000)
  })
  onBeforeUnmount(() => {
    if (interval) clearInterval(interval)
  })

  return { remainingMs, expired, timeLabel }
}
