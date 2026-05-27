<template>
  <article class="overflow-hidden rounded-tcf-card border border-tcf-line bg-white shadow-sm transition hover:-translate-y-0.5 hover:border-slate-300 hover:shadow-md">
    <div class="flex flex-col gap-4 border-b border-tcf-line px-4 py-4 sm:flex-row sm:items-center sm:justify-between" :class="bannerClass">
      <div class="flex min-w-0 items-center gap-4">
        <ScoreRing :score="summary.averageScore" :level="summary.scoreLevel" :show-label="false" />
        <div class="min-w-0">
          <div class="flex flex-wrap items-center gap-2">
            <span class="text-xs font-bold uppercase tracking-[0.14em]" :style="{ color: tierColor(summary.averageScore) }">{{ scoreStatus }}</span>
            <UiBadge :tone="modeTone">{{ modeLabel(session.mode) }}</UiBadge>
            <UiBadge :tone="statusTone">{{ statusLabel(session.status) }}</UiBadge>
          </div>
          <h2 class="mt-1 truncate text-base font-bold text-slate-950">{{ testDefinitionName(session.testDefinition) }}</h2>
          <p class="mt-1 text-xs text-slate-500">{{ formatDateTime(session.createdAt) }}</p>
        </div>
      </div>

      <div class="grid grid-cols-3 gap-2 sm:min-w-72">
        <div class="rounded-tcf-input border border-white/70 bg-white/80 p-2 text-center">
          <p class="text-lg font-bold text-slate-950">{{ summary.completedTasks }}/{{ summary.totalTasks }}</p>
          <p class="mt-0.5 text-[10px] font-semibold uppercase tracking-wider text-slate-500">{{ $t('history.summary.tasks') }}</p>
        </div>
        <div class="rounded-tcf-input border border-white/70 bg-white/80 p-2 text-center">
          <p class="text-lg font-bold text-slate-950">{{ displayAverage }}</p>
          <p class="mt-0.5 text-[10px] font-semibold uppercase tracking-wider text-slate-500">{{ $t('history.summary.average') }}</p>
        </div>
        <div class="rounded-tcf-input border border-white/70 bg-white/80 p-2 text-center">
          <p class="text-lg font-bold text-slate-950">{{ sectionLabel }}</p>
          <p class="mt-0.5 text-[10px] font-semibold uppercase tracking-wider text-slate-500">{{ $t('history.summary.sections') }}</p>
        </div>
      </div>
    </div>

    <div class="p-4 sm:p-5">
      <div class="flex flex-wrap gap-2">
        <span class="inline-flex rounded-pill border border-slate-200 bg-slate-50 px-2.5 py-1 text-xs font-semibold text-slate-600">
          {{ $t('history.summary.tasksDone', { completed: summary.completedTasks, total: summary.totalTasks }) }}
        </span>
        <span v-if="summary.oralTasks" class="inline-flex rounded-pill border border-indigo-100 bg-indigo-50 px-2.5 py-1 text-xs font-semibold text-indigo-800">
          {{ $t('history.summary.oralCount', { count: summary.oralTasks }) }}
        </span>
        <span v-if="summary.writtenTasks" class="inline-flex rounded-pill border border-emerald-100 bg-emerald-50 px-2.5 py-1 text-xs font-semibold text-emerald-800">
          {{ $t('history.summary.writtenCount', { count: summary.writtenTasks }) }}
        </span>
        <span v-for="taskNumber in visibleTaskNumbers" :key="taskNumber" class="inline-flex rounded-pill border border-slate-200 bg-white px-2.5 py-1 text-xs font-semibold text-slate-600">
          {{ taskLabel(taskNumber) }}
        </span>
      </div>

      <div class="mt-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <p class="text-sm text-slate-600">
          {{ summaryLine }}
        </p>
        <div class="flex flex-wrap gap-2">
          <UiButton :to="`/tests/${session.uuid}/report`" variant="ghost">
            <svg class="mr-2 h-4 w-4" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M2.25 12s3.75-6.75 9.75-6.75S21.75 12 21.75 12 18 18.75 12 18.75 2.25 12 2.25 12Z" />
              <circle cx="12" cy="12" r="2.75" />
            </svg>
            {{ $t('history.viewExam') }}
          </UiButton>
          <UiButton v-if="deletable" type="button" variant="danger" @click="emit('delete', session.uuid)">{{ $t('common.delete') }}</UiButton>
        </div>
      </div>
    </div>
  </article>
</template>

<script setup lang="ts">
import type { TestSession } from '~/types/api'

const props = withDefaults(
  defineProps<{
    session: TestSession
    deletable?: boolean
  }>(),
  { deletable: false },
)
const emit = defineEmits<{ delete: [uuid: string] }>()

const { t } = useI18n()
const { formatDateTime, modeLabel, statusLabel, taskLabel, testDefinitionName } = useUiLabels()
const { tierColor, tierLabel } = useExamScoring()
const summary = computed(() => summarizeSession(props.session))

const displayAverage = computed(() => {
  const score = formatSessionScore(summary.value.averageScore)
  return summary.value.averageScore === null ? score : `${score}/20`
})
const scoreStatus = computed(() => (summary.value.averageScore === null ? t('history.summary.noScore') : tierLabel(summary.value.averageScore)))
const visibleTaskNumbers = computed(() => summary.value.taskNumbers.slice(0, 6))
const modeTone = computed(() => {
  if (props.session.mode === 'oral') return 'oral'
  if (props.session.mode === 'written') return 'written'
  return 'slate'
})
const statusTone = computed(() => {
  if (props.session.status === 'completed') return 'success'
  if (props.session.status === 'grading_failed') return 'error'
  if (props.session.status === 'in_progress' || props.session.status === 'started') return 'warning'
  return 'slate'
})
const bannerClass = computed(() => {
  const score = summary.value.averageScore
  if (score === null) return 'bg-slate-50'
  if (score >= 16) return 'bg-lime-50'
  if (score >= 12) return 'bg-indigo-50'
  if (score >= 8) return 'bg-amber-50'
  return 'bg-red-50'
})
const sectionLabel = computed(() => {
  if (summary.value.sections.length === 2) return t('history.summary.mixedSections')
  if (summary.value.sections[0] === 'oral') return t('common.oral')
  if (summary.value.sections[0] === 'written') return t('common.written')
  return '-'
})
const summaryLine = computed(() => {
  if (summary.value.gradedTasks === 0) {
    return t('history.summary.pendingSummary')
  }
  return t('history.summary.scoredSummary', {
    graded: summary.value.gradedTasks,
    average: displayAverage.value,
  })
})
</script>
