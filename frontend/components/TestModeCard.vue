<template>
  <form class="group flex h-full flex-col rounded-tcf-card border border-tcf-line bg-white p-4 transition hover:-translate-y-0.5 hover:border-slate-300 hover:shadow-sm" @submit.prevent="emit('start', definition.sourceId)">
    <div class="flex items-center justify-between gap-3">
      <h2 class="text-sm font-bold leading-snug text-slate-950">{{ testDefinitionName(definition) }}</h2>
      <UiBadge>{{ modeLabel(definition.mode) }}</UiBadge>
    </div>
    <p class="mt-3 min-h-14 flex-1 text-xs leading-5 text-slate-600">{{ testDefinitionDescription(definition) }}</p>
    <UiButton class="mt-4 self-start !px-3 !py-1.5 !text-xs" type="submit">{{ $t('common.start') }}</UiButton>
  </form>
</template>

<script setup lang="ts">
import type { TestDefinition } from '~/types/api'

defineProps<{ definition: TestDefinition }>()
const emit = defineEmits<{ start: [mode: string] }>()
const { modeLabel, testDefinitionDescription, testDefinitionName } = useUiLabels()
</script>
