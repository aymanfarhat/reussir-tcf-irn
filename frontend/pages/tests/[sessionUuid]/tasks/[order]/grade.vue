<template>
  <div v-if="feedback" class="grid gap-6 lg:grid-cols-[1fr_340px]">
    <section class="tcf-card">
      <TaskFeedbackPanel :attempt="feedback.attempt" :grade="feedback.grade" />
      <form v-if="canRegrade" class="mt-4" @submit.prevent="retry">
        <UiButton type="submit" :disabled="pending">
          {{ pending ? 'Regrading...' : regradeLabel }}
        </UiButton>
        <p v-if="retryError" class="mt-2 text-sm text-red-700">{{ retryError }}</p>
      </form>
      <ExampleResponses :responses="feedback.exampleResponses" />
      <ImprovedResponsePanel :grade="feedback.grade" />
    </section>

    <aside class="tcf-card">
      <h2 class="font-semibold text-slate-950">Next step</h2>
      <UiButton v-if="feedback.nextAttempt" class="mt-4 w-full" :to="`/tests/${sessionUuid}/tasks/${feedback.nextAttempt.sequenceOrder}`">
        Continue to task {{ feedback.nextAttempt.question.taskNumber }}
      </UiButton>
      <UiButton v-else class="mt-4 w-full" :to="`/tests/${sessionUuid}/report`">View final report</UiButton>

      <div class="mt-5 border-t border-slate-200 pt-5">
        <h2 class="font-semibold text-slate-950">Same prompt best</h2>
        <div v-if="feedback.personalBestAttempt" class="mt-3 rounded-md border border-lime-200 bg-lime-50 p-3">
          <div class="text-xl font-bold text-lime-900">{{ feedback.personalBestAttempt.grade?.overallScore20 }}/20</div>
          <div class="mt-1 text-sm font-medium text-lime-800">{{ feedback.personalBestAttempt.grade?.estimatedCefrLevel }}</div>
          <NuxtLink class="mt-3 inline-flex text-sm font-medium text-lime-900 underline" :to="`/tests/${feedback.personalBestAttempt.testSessionUuid}/tasks/${feedback.personalBestAttempt.sequenceOrder}/grade`">
            Review that attempt
          </NuxtLink>
        </div>
        <p v-else class="mt-3 text-sm text-slate-500">No earlier graded attempt for this exact prompt.</p>
      </div>
    </aside>
  </div>
</template>

<script setup lang="ts">
import type { TaskFeedbackResponse } from '~/types/api'

definePageMeta({ requires: 'auth' })

const route = useRoute()
const api = useApi()
const sessionUuid = computed(() => String(route.params.sessionUuid))
const order = computed(() => Number(route.params.order))
const pending = ref(false)
const retryError = ref('')

const { data: feedback, refresh } = await useAsyncData(`feedback-${sessionUuid.value}-${order.value}`, () =>
  api.get<TaskFeedbackResponse>(`/api/sessions/${sessionUuid.value}/attempts/${order.value}/grade`),
)

const canRegrade = computed(() => {
  const attempt = feedback.value?.attempt
  if (!attempt?.candidateText?.trim()) return false
  return ['submitted', 'graded', 'grading_failed'].includes(attempt.status)
})

const regradeLabel = computed(() =>
  feedback.value?.grade?.status === 'failed' ? 'Retry grading' : 'Regrade answer',
)

async function retry() {
  pending.value = true
  retryError.value = ''
  try {
    await api.post(`/api/sessions/${sessionUuid.value}/attempts/${order.value}/retry-grade`)
    await refresh()
  } catch (error: any) {
    retryError.value = error?.data?.detail || 'Regrade failed.'
  } finally {
    pending.value = false
  }
}
</script>
