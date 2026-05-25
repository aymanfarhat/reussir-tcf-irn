<template>
  <div class="grid gap-6 lg:grid-cols-[1fr_360px]">
    <section>
      <div class="mb-5">
        <h1 class="text-2xl font-bold text-slate-950">{{ $t('dashboard.title') }}</h1>
        <p class="mt-1 text-sm text-slate-500">{{ $t('dashboard.subtitle') }}</p>
        <UiButton class="mt-3" variant="ghost" to="/practice">{{ $t('dashboard.targetedPractice') }}</UiButton>
      </div>

      <div class="grid gap-4 md:grid-cols-3">
        <TestModeCard v-for="definition in definitions" :key="definition.sourceId" :definition="definition" @start="start" />
        <div v-if="definitions.length === 0" class="rounded-lg border border-amber-200 bg-amber-50 p-5 text-sm text-amber-800">
          {{ $t('dashboard.emptyDefinitions') }}
        </div>
      </div>
    </section>

    <aside class="tcf-card">
      <h2 class="font-semibold text-slate-950">{{ $t('dashboard.recentSessions') }}</h2>
      <div class="mt-4 space-y-3">
        <NuxtLink v-for="session in recentSessions" :key="session.uuid" class="block rounded-md border border-slate-200 p-3 hover:bg-slate-50" :to="`/tests/${session.uuid}/report`">
          <div class="flex items-center justify-between gap-3">
            <span class="text-sm font-medium text-slate-900">{{ session.testDefinition.name }}</span>
            <UiBadge>{{ statusLabel(session.status) }}</UiBadge>
          </div>
          <div class="mt-1 text-xs text-slate-500">{{ formatDateTime(session.createdAt) }}</div>
        </NuxtLink>
        <p v-if="recentSessions.length === 0" class="text-sm text-slate-500">{{ $t('dashboard.emptySessions') }}</p>
      </div>
    </aside>
  </div>
</template>

<script setup lang="ts">
import type { TestDefinition, TestSession } from '~/types/api'

definePageMeta({ requires: 'auth' })

const api = useApi()
const { show } = useFlash()
const { t } = useI18n()
const { formatDateTime, statusLabel } = useUiLabels()
const { data: definitionsData } = await useAsyncData('test-definitions', () => api.get<TestDefinition[]>('/api/test-definitions'))
const { data: sessionsData } = await useAsyncData('dashboard-sessions', () => api.get<TestSession[]>('/api/sessions'))

const definitions = computed(() => definitionsData.value ?? [])
const recentSessions = computed(() => (sessionsData.value ?? []).slice(0, 5))

async function start(mode: string) {
  try {
    const session = await api.post<TestSession>('/api/sessions/start', { mode })
    await navigateTo(`/tests/${session.uuid}/tasks/1`)
  } catch (err: any) {
    show(err?.data?.detail || t('dashboard.startFailed'), 'error')
  }
}
</script>
