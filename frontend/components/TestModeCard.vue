<template>
  <form class="tcf-card" @submit.prevent="emit('start', definition.sourceId)">
    <div class="flex items-center justify-between gap-3">
      <h2 class="font-semibold text-slate-950">{{ definition.name }}</h2>
      <UiBadge>{{ definition.mode }}</UiBadge>
    </div>
    <p class="mt-3 min-h-12 text-sm text-slate-600">{{ definition.description }}</p>
    <UiButton class="mt-5 w-full" type="submit">Start</UiButton>
  </form>
</template>

<script setup lang="ts">
import type { TestDefinition } from '~/types/api'

defineProps<{ definition: TestDefinition }>()
const emit = defineEmits<{ start: [mode: string] }>()
</script>
