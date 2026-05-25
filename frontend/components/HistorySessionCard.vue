<template>
  <article class="tcf-card">
    <div class="flex flex-wrap items-start justify-between gap-4">
      <div>
        <div class="flex flex-wrap items-center gap-2">
          <h2 class="font-semibold text-slate-950">{{ session.testDefinition.name }}</h2>
          <UiBadge>{{ modeLabel(session.mode) }}</UiBadge>
          <UiBadge>{{ statusLabel(session.status) }}</UiBadge>
        </div>
        <div class="mt-2 text-sm text-slate-500">{{ formatDateTime(session.createdAt) }}</div>
      </div>
      <div class="flex flex-wrap items-center gap-2">
        <UiButton :to="`/tests/${session.uuid}/report`">{{ $t('history.fullReport') }}</UiButton>
        <UiButton type="button" variant="danger" @click="emit('delete', session.uuid)">{{ $t('common.delete') }}</UiButton>
      </div>
    </div>
    <div class="mt-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
      <div class="rounded-md border border-indigo-100 bg-indigo-50 p-3">
        <div class="text-xs font-medium uppercase text-indigo-700">{{ $t('common.oral') }}</div>
        <div class="mt-1 font-semibold text-indigo-950">{{ session.oralScore ?? '-' }}/20 {{ session.oralLevel }}</div>
      </div>
      <div class="rounded-md border border-emerald-100 bg-emerald-50 p-3">
        <div class="text-xs font-medium uppercase text-emerald-700">{{ $t('common.written') }}</div>
        <div class="mt-1 font-semibold text-emerald-950">{{ session.writtenScore ?? '-' }}/20 {{ session.writtenLevel }}</div>
      </div>
    </div>
    <div class="mt-4 overflow-hidden rounded-md border border-slate-200">
      <table class="w-full text-left text-sm">
        <thead class="bg-slate-50 text-slate-600">
          <tr><th class="px-3 py-2">{{ $t('common.task') }}</th><th class="px-3 py-2">{{ $t('common.status') }}</th><th class="px-3 py-2">{{ $t('common.score') }}</th><th class="px-3 py-2 text-right">{{ $t('common.result') }}</th></tr>
        </thead>
        <tbody class="divide-y divide-slate-200">
          <tr v-for="attempt in session.attempts" :key="attempt.uuid">
            <td class="px-3 py-2">
              <div class="font-medium text-slate-950">{{ taskLabel(attempt.question.taskNumber) }}</div>
              <div class="mt-0.5 text-xs text-slate-500">{{ attempt.question.taskTypeFr }}</div>
            </td>
            <td class="px-3 py-2 text-slate-600">{{ statusLabel(attempt.status) }}</td>
            <td class="px-3 py-2">
              <span v-if="attempt.grade?.status === 'succeeded'" class="font-medium text-slate-950">{{ attempt.grade.overallScore20 }}/20 {{ attempt.grade.estimatedCefrLevel }}</span>
              <span v-else class="text-slate-500">-</span>
            </td>
            <td class="px-3 py-2 text-right">
              <NuxtLink v-if="attempt.status === 'graded' || attempt.status === 'grading_failed'" class="font-medium text-indigo-700 hover:text-indigo-900" :to="`/tests/${session.uuid}/tasks/${attempt.sequenceOrder}/grade`">{{ $t('history.taskFeedback') }}</NuxtLink>
              <NuxtLink v-else class="font-medium text-slate-600 hover:text-slate-900" :to="`/tests/${session.uuid}/tasks/${attempt.sequenceOrder}`">{{ $t('common.continue') }}</NuxtLink>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </article>
</template>

<script setup lang="ts">
import type { TestSession } from '~/types/api'

defineProps<{ session: TestSession }>()
const emit = defineEmits<{ delete: [uuid: string] }>()
const { formatDateTime, modeLabel, statusLabel, taskLabel } = useUiLabels()
</script>
