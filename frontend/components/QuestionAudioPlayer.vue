<template>
  <div class="mt-4 flex flex-wrap items-center gap-3">
    <UiButton type="button" variant="ghost" :disabled="loading" @click="play">
      {{ loading ? 'Loading audio...' : 'Play question' }}
    </UiButton>
    <span class="text-xs text-indigo-900">{{ status }}</span>
    <audio ref="audioRef" preload="none" :src="src" @ended="status = defaultStatus" @error="onError" />
  </div>
</template>

<script setup lang="ts">
defineProps<{ src: string }>()
const defaultStatus = 'AI-generated examiner audio.'
const status = ref(defaultStatus)
const loading = ref(false)
const audioRef = ref<HTMLAudioElement | null>(null)

async function play() {
  if (!audioRef.value) {
    status.value = 'Question audio is unavailable right now.'
    return
  }
  loading.value = true
  status.value = 'Loading question audio...'
  try {
    audioRef.value.currentTime = 0
    await audioRef.value.play()
    status.value = 'Playing question audio.'
  } catch {
    status.value = 'Question audio is unavailable right now.'
  } finally {
    loading.value = false
  }
}

function onError() {
  loading.value = false
  status.value = 'Question audio is unavailable right now.'
}
</script>
