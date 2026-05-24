<template>
  <span class="tcf-badge" :class="classes">
    <slot />
  </span>
</template>

<script setup lang="ts">
const props = withDefaults(
  defineProps<{
    tone?: 'slate' | 'oral' | 'written' | 'success' | 'warning' | 'error'
  }>(),
  { tone: 'slate' },
)

const classes = computed(() => {
  const tones = {
    slate: 'bg-slate-100 text-slate-700',
    oral: 'bg-indigo-50 text-indigo-800',
    written: 'bg-emerald-50 text-emerald-800',
    success: 'bg-lime-100 text-lime-800',
    warning: 'bg-amber-100 text-amber-800',
    error: 'bg-red-100 text-red-800',
  }
  return tones[props.tone]
})
</script>
