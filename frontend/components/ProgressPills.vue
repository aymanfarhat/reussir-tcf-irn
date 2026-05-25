<template>
  <div class="mb-5 flex flex-wrap items-center gap-2">
    <UiBadge
      v-for="item in attempts"
      :key="item.uuid"
      :tone="item.sequenceOrder === currentOrder ? 'oral' : item.status === 'graded' ? 'success' : item.status === 'grading_failed' ? 'error' : 'slate'"
      :class="item.sequenceOrder === currentOrder ? '!bg-indigo-600 !text-white' : ''"
    >
      {{ taskLabel(item.question.taskNumber) }}
    </UiBadge>
  </div>
</template>

<script setup lang="ts">
import type { TaskAttempt } from '~/types/api'

defineProps<{ attempts: TaskAttempt[]; currentOrder: number }>()
const { taskLabel } = useUiLabels()
</script>
