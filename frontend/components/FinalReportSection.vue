<template>
  <article class="tcf-card">
    <div class="flex flex-wrap items-start justify-between gap-3">
      <div>
        <UiBadge :tone="attempt.isWritten ? 'written' : 'oral'">Task {{ attempt.question.taskNumber }}</UiBadge>
        <h2 class="mt-2 font-semibold text-slate-950">{{ attempt.question.taskTypeFr }}</h2>
      </div>
      <div class="flex flex-wrap items-center justify-end gap-3">
        <ScoreRing v-if="attempt.grade?.status === 'succeeded'" :score="attempt.grade.overallScore20" :level="attempt.grade.estimatedCefrLevel" />
        <UiBadge v-else tone="warning">{{ attempt.grade?.status || 'pending' }}</UiBadge>
        <UiButton class="shrink-0" variant="ghost" :to="`/tests/${sessionUuid}/tasks/${attempt.sequenceOrder}/grade`">View task feedback</UiButton>
      </div>
    </div>
    <p class="mt-4 text-sm text-slate-700">{{ attempt.question.prompt }}</p>
    <div v-if="attempt.grade?.status === 'succeeded'" class="mt-4 grid gap-4 md:grid-cols-2">
      <div>
        <h3 class="text-sm font-semibold text-slate-950">Covered</h3>
        <ul class="mt-2 list-disc space-y-1 pl-5 text-sm text-slate-600">
          <li v-for="item in attempt.grade.parsedResult.elementsCovered || attempt.grade.parsedResult.elements_covered || []" :key="item">{{ item }}</li>
        </ul>
      </div>
      <div>
        <h3 class="text-sm font-semibold text-slate-950">Missing</h3>
        <ul class="mt-2 list-disc space-y-1 pl-5 text-sm text-slate-600">
          <li v-for="item in attempt.grade.parsedResult.elementsMissing || attempt.grade.parsedResult.elements_missing || []" :key="item">{{ item }}</li>
        </ul>
      </div>
    </div>
  </article>
</template>

<script setup lang="ts">
import type { TaskAttempt } from '~/types/api'

defineProps<{ attempt: TaskAttempt; sessionUuid: string }>()
</script>
