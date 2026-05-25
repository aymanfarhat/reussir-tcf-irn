<template>
  <div class="mt-4 flex flex-wrap items-center gap-3">
    <UiButton type="button" variant="ghost" :disabled="loading" @click="play">
      {{ loading ? $t('questionAudio.loading') : $t('questionAudio.play') }}
    </UiButton>
    <span class="text-xs text-indigo-900">{{ status }}</span>
    <audio ref="audioRef" preload="none" :src="src" @ended="statusKey = 'default'" @error="onError" />
  </div>
</template>

<script setup lang="ts">
defineProps<{ src: string }>()
type QuestionAudioStatus = 'default' | 'loadingStatus' | 'playing' | 'unavailable'

const { t } = useI18n()
const statusKey = ref<QuestionAudioStatus>('default')
const status = computed(() => t(`questionAudio.${statusKey.value}`))
const loading = ref(false)
const audioRef = ref<HTMLAudioElement | null>(null)

async function play() {
  if (!audioRef.value) {
    statusKey.value = 'unavailable'
    return
  }
  loading.value = true
  statusKey.value = 'loadingStatus'
  try {
    audioRef.value.currentTime = 0
    await audioRef.value.play()
    statusKey.value = 'playing'
  } catch {
    statusKey.value = 'unavailable'
  } finally {
    loading.value = false
  }
}

function onError() {
  loading.value = false
  statusKey.value = 'unavailable'
}
</script>
