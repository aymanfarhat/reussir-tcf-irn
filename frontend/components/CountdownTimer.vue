<template>
  <div class="rounded-md bg-slate-100 px-3 py-2 text-sm font-semibold text-slate-800">
    {{ timeLabel }}
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{ deadline?: string | null }>()
const deadline = computed(() => props.deadline)
const { timeLabel } = useCountdown(deadline)
</script>
