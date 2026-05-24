<template>
  <div v-if="session">
    <div class="mb-6 flex flex-wrap items-start justify-between gap-4">
      <div>
        <h1 class="text-2xl font-bold text-slate-950">Final report</h1>
        <p class="mt-1 text-sm text-slate-500">Scores are practice estimates. The official TCF IRN aggregation formula is not public.</p>
      </div>
      <UiButton to="/" variant="ghost">Dashboard</UiButton>
    </div>

    <div class="mb-6 grid gap-4 md:grid-cols-2">
      <div class="rounded-lg border border-indigo-200 bg-indigo-50 p-5">
        <div class="text-sm font-medium text-indigo-800">Oral</div>
        <div class="mt-3"><ScoreRing :score="session.oralScore" :level="session.oralLevel" /></div>
      </div>
      <div class="rounded-lg border border-emerald-200 bg-emerald-50 p-5">
        <div class="text-sm font-medium text-emerald-800">Written</div>
        <div class="mt-3"><ScoreRing :score="session.writtenScore" :level="session.writtenLevel" /></div>
      </div>
    </div>

    <div class="space-y-5">
      <FinalReportSection v-for="attempt in session.attempts" :key="attempt.uuid" :attempt="attempt" :session-uuid="session.uuid" />
    </div>
  </div>
</template>

<script setup lang="ts">
import type { TestSession } from '~/types/api'

definePageMeta({ requires: 'auth' })

const route = useRoute()
const api = useApi()
const sessionUuid = computed(() => String(route.params.sessionUuid))
const { data: session } = await useAsyncData(`report-${sessionUuid.value}`, () =>
  api.get<TestSession>(`/api/sessions/${sessionUuid.value}/report`),
)
</script>
