<template>
  <div class="rounded-lg border border-slate-200 bg-slate-50 p-4">
    <div class="flex flex-wrap gap-2">
      <UiButton type="button" :disabled="recording" @click="start">Start recording</UiButton>
      <UiButton type="button" variant="ghost" :disabled="!recording" @click="stop">Stop</UiButton>
      <UiButton type="button" variant="ghost" @click="handleReset">Re-record</UiButton>
    </div>
    <p class="mt-3 text-sm text-slate-600">{{ status }}</p>
    <audio v-if="audioUrl" class="mt-3 w-full" :src="audioUrl" controls />
  </div>
</template>

<script setup lang="ts">
const emit = defineEmits<{ recorded: [file: File | null] }>()
const recorder = useAudioRecorder()
const { recording, audioUrl, status, start, stop, reset, file } = recorder

watch(audioUrl, () => emit('recorded', file()))

function handleReset() {
  reset()
  emit('recorded', null)
}
</script>
