<template>
  <div class="space-y-8">
    <section class="tcf-card bg-gradient-to-r from-white to-slate-50">
      <div class="flex flex-col gap-6 lg:flex-row lg:items-center lg:justify-between">
        <div class="max-w-3xl">
          <p class="text-xs font-semibold uppercase tracking-[0.18em] text-indigo-700">{{ $t('dashboard.eyebrow') }}</p>
          <h1 class="mt-2 text-3xl font-bold tracking-tight text-slate-950">{{ $t('dashboard.title', { name: userName }) }}</h1>
          <p class="mt-3 text-sm leading-6 text-slate-600">{{ $t('dashboard.subtitle') }}</p>
        </div>

        <div class="grid grid-cols-2 gap-3 sm:grid-cols-4 lg:min-w-96 lg:grid-cols-2">
          <div v-for="stat in heroStats" :key="stat.label" class="rounded-tcf-input border border-tcf-line bg-white p-3 text-center shadow-sm">
            <p class="text-2xl font-bold" :class="stat.class">{{ stat.value }}</p>
            <p class="mt-1 text-[10px] font-semibold uppercase tracking-wider text-slate-500">{{ stat.label }}</p>
          </div>
        </div>
      </div>
    </section>

    <section>
      <div class="mb-4 flex flex-wrap items-end justify-between gap-3">
        <div>
          <h2 class="text-xl font-bold text-slate-950">{{ $t('dashboard.quickStartTitle') }}</h2>
          <p class="mt-1 text-sm text-slate-500">{{ $t('dashboard.quickStartSubtitle') }}</p>
        </div>
      </div>

      <div class="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <TestModeCard v-for="definition in definitions" :key="definition.sourceId" :definition="definition" @start="start" />
        <article class="flex h-full flex-col rounded-tcf-card border border-tcf-line bg-white p-4 transition hover:-translate-y-0.5 hover:border-slate-300 hover:shadow-sm">
          <div class="flex items-center justify-between gap-3">
            <h2 class="text-sm font-bold leading-snug text-slate-950">{{ $t('dashboard.targetedPractice') }}</h2>
            <UiBadge>{{ $t('modes.practice') }}</UiBadge>
          </div>
          <p class="mt-3 min-h-14 flex-1 text-xs leading-5 text-slate-600">{{ $t('dashboard.targetedPracticeDescription') }}</p>
          <UiButton class="mt-4 self-start !px-3 !py-1.5 !text-xs" to="/practice">{{ $t('dashboard.practiceCtaShort') }}</UiButton>
        </article>
        <div v-if="definitions.length === 0" class="rounded-lg border border-amber-200 bg-amber-50 p-5 text-sm text-amber-800">
          {{ $t('dashboard.emptyDefinitions') }}
        </div>
      </div>
    </section>

    <section>
      <div class="mb-4 flex flex-wrap items-end justify-between gap-3">
        <div>
          <h2 class="text-xl font-bold text-slate-950">{{ $t('dashboard.latestTitle') }}</h2>
          <p class="mt-1 text-sm text-slate-500">{{ $t('dashboard.latestSubtitle') }}</p>
        </div>
        <UiButton to="/tests/history" variant="ghost">{{ $t('dashboard.viewAllHistory') }}</UiButton>
      </div>

      <div class="grid gap-4 xl:grid-cols-2">
        <SessionSummaryCard v-for="session in latestSessions" :key="session.uuid" :session="session" />
        <div v-if="latestSessions.length === 0" class="tcf-card text-sm text-slate-500">{{ $t('dashboard.emptySessions') }}</div>
      </div>

      <div v-if="sessions.length > latestSessions.length" class="mt-5 flex justify-center">
        <UiButton to="/tests/history" variant="ghost">{{ $t('dashboard.viewAllHistory') }}</UiButton>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import type { TestDefinition, TestSession } from '~/types/api'

definePageMeta({ requires: 'auth' })

const api = useApi()
const { user } = useSession()
const { show } = useFlash()
const { t } = useI18n()
const { data: definitionsData } = await useAsyncData('test-definitions', () => api.get<TestDefinition[]>('/api/test-definitions'))
const { data: sessionsData } = await useAsyncData('dashboard-sessions', () => api.get<TestSession[]>('/api/sessions'))

const definitions = computed(() => definitionsData.value ?? [])
const sessions = computed(() => sessionsData.value ?? [])
const latestSessions = computed(() => sessions.value.slice(0, 4))
const sessionSummaries = computed(() => sessions.value.map((session) => summarizeSession(session)))
const userName = computed(() => user.value?.displayName || user.value?.username || t('dashboard.defaultLearner'))
const totalCompletedTasks = computed(() => sessionSummaries.value.reduce((total, summary) => total + summary.completedTasks, 0))
const scoredSummaries = computed(() => sessionSummaries.value.filter((summary) => summary.averageScore !== null))
const averageScore = computed(() => {
  if (scoredSummaries.value.length === 0) return '-'
  const total = scoredSummaries.value.reduce((sum, summary) => sum + Number(summary.averageScore), 0)
  return `${formatSessionScore(Math.round((total / scoredSummaries.value.length) * 10) / 10)}/20`
})
const bestScore = computed(() => {
  const scores = sessionSummaries.value.map((summary) => summary.bestScore).filter((score): score is number => typeof score === 'number')
  return scores.length > 0 ? `${formatSessionScore(Math.max(...scores))}/20` : '-'
})
const heroStats = computed(() => [
  { label: t('dashboard.stats.sessions'), value: sessions.value.length, class: 'text-slate-950' },
  { label: t('dashboard.stats.tasks'), value: totalCompletedTasks.value, class: 'text-indigo-700' },
  { label: t('dashboard.stats.average'), value: averageScore.value, class: 'text-lime-700' },
  { label: t('dashboard.stats.best'), value: bestScore.value, class: 'text-amber-700' },
])

async function start(mode: string) {
  try {
    const session = await api.post<TestSession>('/api/sessions/start', { mode })
    await navigateTo(`/tests/${session.uuid}/tasks/1`)
  } catch (err: any) {
    show(err?.data?.detail || t('dashboard.startFailed'), 'error')
  }
}
</script>
