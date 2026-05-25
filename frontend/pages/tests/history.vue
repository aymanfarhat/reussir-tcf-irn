<template>
  <div>
    <div class="mb-6 flex flex-wrap items-start justify-between gap-4">
      <div>
        <h1 class="text-2xl font-bold text-slate-950">{{ $t('history.title') }}</h1>
        <p class="mt-1 text-sm text-slate-500">{{ $t('history.subtitle') }}</p>
      </div>
      <UiButton to="/" variant="ghost">{{ $t('common.dashboard') }}</UiButton>
    </div>

    <div class="space-y-4">
      <HistorySessionCard v-for="session in sessions" :key="session.uuid" :session="session" @delete="deleteSession" />
      <div v-if="sessions.length === 0" class="tcf-card text-sm text-slate-500">{{ $t('history.empty') }}</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { TestSession } from '~/types/api'

definePageMeta({ requires: 'auth' })

const api = useApi()
const { show } = useFlash()
const { t } = useI18n()
const { data, refresh } = await useAsyncData('history', () => api.get<TestSession[]>('/api/sessions'))
const sessions = computed(() => data.value ?? [])

async function deleteSession(uuid: string) {
  if (!window.confirm(t('history.confirmDelete'))) return
  await api.del(`/api/sessions/${uuid}`)
  show(t('history.deleted'), 'success')
  await refresh()
}
</script>
