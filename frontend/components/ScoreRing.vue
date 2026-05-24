<template>
  <div class="flex items-center gap-3">
    <svg class="h-16 w-16 flex-shrink-0" viewBox="0 0 64 64">
      <circle cx="32" cy="32" r="26" fill="none" :stroke="color" stroke-opacity="0.16" stroke-width="5" />
      <circle
        cx="32"
        cy="32"
        r="26"
        fill="none"
        :stroke="color"
        stroke-width="5"
        stroke-linecap="square"
        :stroke-dasharray="arcDash(score)"
        transform="rotate(-90 32 32)"
        class="transition-all duration-700 ease-out"
      />
      <text x="32" y="32" text-anchor="middle" dominant-baseline="central" :fill="color" font-size="18" font-weight="700">
        {{ displayScore }}
      </text>
    </svg>
    <div v-if="showLabel">
      <p class="text-xs font-bold uppercase tracking-wider" :style="{ color }">{{ tierLabel(score) }}</p>
      <p class="text-sm font-semibold text-slate-950">{{ displayScore }}/20</p>
      <p v-if="level" class="text-xs text-slate-500">{{ level }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
const props = withDefaults(
  defineProps<{
    score?: number | null
    level?: string
    showLabel?: boolean
  }>(),
  { score: null, level: '', showLabel: true },
)

const { arcDash, tierColor, tierLabel } = useExamScoring()
const color = computed(() => tierColor(props.score))
const displayScore = computed(() => (props.score === null || props.score === undefined ? '-' : Number(props.score).toFixed(1).replace('.0', '')))
</script>
