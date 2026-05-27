<template>
  <div>
    <header class="mb-6 flex flex-wrap items-end justify-between gap-4">
      <div>
        <p class="text-xs font-semibold uppercase tracking-[0.18em] text-indigo-700">{{ $t('history.eyebrow') }}</p>
        <h1 class="mt-2 text-2xl font-bold text-slate-950 sm:text-3xl">{{ $t('history.title') }}</h1>
        <p class="mt-2 max-w-2xl text-sm text-slate-500">{{ $t('history.subtitle') }}</p>
      </div>
      <UiButton to="/" variant="ghost">{{ $t('common.dashboard') }}</UiButton>
    </header>

    <div v-if="sessions.length" class="mb-5 grid grid-cols-2 gap-3 rounded-tcf-card border border-tcf-line bg-white p-3 shadow-sm sm:grid-cols-4">
      <div v-for="stat in historyStats" :key="stat.label" class="p-2 text-center">
        <p class="text-2xl font-bold" :class="stat.class">{{ stat.value }}</p>
        <p class="mt-1 text-[10px] font-semibold uppercase tracking-wider text-slate-500">{{ stat.label }}</p>
      </div>
    </div>

    <div class="space-y-4">
      <SessionSummaryCard v-for="session in paginatedSessions" :key="session.uuid" :session="session" deletable @delete="deleteSession" />
      <div v-if="sessions.length === 0" class="tcf-card text-sm text-slate-500">{{ $t('history.empty') }}</div>
    </div>

    <nav v-if="totalPages > 1" class="mt-6 flex flex-col gap-3 rounded-tcf-card border border-tcf-line bg-white p-3 shadow-sm sm:flex-row sm:items-center sm:justify-between">
      <p class="text-sm text-slate-500">
        {{ $t('history.pagination.range', { start: visibleStart, end: visibleEnd, total: sessions.length }) }}
      </p>
      <div class="flex items-center justify-between gap-2 sm:justify-end">
        <UiButton type="button" variant="ghost" :disabled="currentPage === 1" @click="setPage(currentPage - 1)">{{ $t('history.pagination.previous') }}</UiButton>
        <span class="px-2 text-sm font-semibold text-slate-600">{{ $t('history.pagination.page', { page: currentPage, total: totalPages }) }}</span>
        <UiButton type="button" variant="ghost" :disabled="currentPage === totalPages" @click="setPage(currentPage + 1)">{{ $t('history.pagination.next') }}</UiButton>
      </div>
    </nav>
  </div>
</template>

<script setup lang="ts">
import type { TestSession } from '~/types/api'

definePageMeta({ requires: 'auth' })

const api = useApi()
const route = useRoute()
const router = useRouter()
const { show } = useFlash()
const { t } = useI18n()
const { data, refresh } = await useAsyncData('history', () => api.get<TestSession[]>('/api/sessions'))
const sessions = computed(() => data.value ?? [])
const pageSize = 8
const currentPage = ref(parsePage(route.query.page))
const summaries = computed(() => sessions.value.map((session) => summarizeSession(session)))
const totalPages = computed(() => Math.max(1, Math.ceil(sessions.value.length / pageSize)))
const paginatedSessions = computed(() => {
  const start = (currentPage.value - 1) * pageSize
  return sessions.value.slice(start, start + pageSize)
})
const visibleStart = computed(() => (sessions.value.length === 0 ? 0 : (currentPage.value - 1) * pageSize + 1))
const visibleEnd = computed(() => Math.min(currentPage.value * pageSize, sessions.value.length))
const gradedSummaries = computed(() => summaries.value.filter((summary) => summary.averageScore !== null))
const historyAverage = computed(() => {
  if (gradedSummaries.value.length === 0) return '-'
  const total = gradedSummaries.value.reduce((sum, summary) => sum + Number(summary.averageScore), 0)
  return `${formatSessionScore(Math.round((total / gradedSummaries.value.length) * 10) / 10)}/20`
})
const historyStats = computed(() => [
  { label: t('dashboard.stats.sessions'), value: sessions.value.length, class: 'text-slate-950' },
  { label: t('dashboard.stats.tasks'), value: summaries.value.reduce((total, summary) => total + summary.completedTasks, 0), class: 'text-indigo-700' },
  { label: t('dashboard.stats.average'), value: historyAverage.value, class: 'text-lime-700' },
  { label: t('history.summary.gradedTasks'), value: summaries.value.reduce((total, summary) => total + summary.gradedTasks, 0), class: 'text-amber-700' },
])

watch(
  () => route.query.page,
  (page) => {
    currentPage.value = clampPage(parsePage(page))
  },
)

watch(totalPages, () => {
  if (currentPage.value > totalPages.value) setPage(totalPages.value)
})

function parsePage(value: unknown): number {
  const page = Number(Array.isArray(value) ? value[0] : value)
  return Number.isFinite(page) && page > 0 ? Math.floor(page) : 1
}

function clampPage(page: number): number {
  return Math.min(Math.max(page, 1), totalPages.value)
}

async function setPage(page: number) {
  const nextPage = clampPage(page)
  currentPage.value = nextPage
  await router.replace({
    query: {
      ...route.query,
      page: nextPage > 1 ? String(nextPage) : undefined,
    },
  })
}

async function deleteSession(uuid: string) {
  if (!window.confirm(t('history.confirmDelete'))) return
  await api.del(`/api/sessions/${uuid}`)
  show(t('history.deleted'), 'success')
  await refresh()
  if (currentPage.value > totalPages.value) await setPage(totalPages.value)
}
</script>
