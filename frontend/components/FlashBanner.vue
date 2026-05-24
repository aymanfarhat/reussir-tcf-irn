<template>
  <div v-if="flash" class="mb-6 flex items-start justify-between gap-3 rounded-md border px-4 py-3 text-sm" :class="classes">
    <span>{{ flash.text }}</span>
    <button type="button" class="text-xs font-semibold uppercase tracking-wider opacity-70 hover:opacity-100" @click="clear">
      Dismiss
    </button>
  </div>
</template>

<script setup lang="ts">
const { flash, clear } = useFlash()
const classes = computed(() => {
  if (!flash.value) return ''
  return {
    info: 'border-indigo-200 bg-indigo-50 text-indigo-900',
    success: 'border-lime-200 bg-lime-50 text-lime-900',
    warning: 'border-amber-200 bg-amber-50 text-amber-900',
    error: 'border-red-200 bg-red-50 text-red-900',
  }[flash.value.kind]
})
</script>
