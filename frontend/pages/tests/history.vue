<template>
  <div>
    <div class="mb-6 flex flex-wrap items-start justify-between gap-4">
      <div>
        <h1 class="text-2xl font-bold text-slate-950">Test history</h1>
        <p class="mt-1 text-sm text-slate-500">Review previous simulations, task feedback, and reports.</p>
      </div>
      <UiButton to="/" variant="ghost">Dashboard</UiButton>
    </div>

    <div class="space-y-4">
      <HistorySessionCard v-for="session in sessions" :key="session.uuid" :session="session" @delete="deleteSession" />
      <div v-if="sessions.length === 0" class="tcf-card text-sm text-slate-500">No sessions yet.</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { TestSession } from '~/types/api'

definePageMeta({ requires: 'auth' })

const api = useApi()
const { show } = useFlash()
const { data, refresh } = await useAsyncData('history', () => api.get<TestSession[]>('/api/sessions'))
const sessions = computed(() => data.value ?? [])

async function deleteSession(uuid: string) {
  if (!window.confirm('Delete this history item? This cannot be undone.')) return
  await api.del(`/api/sessions/${uuid}`)
  show('History item deleted.', 'success')
  await refresh()
}
</script>
