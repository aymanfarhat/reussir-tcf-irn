<template>
  <div v-if="detail">
    <ProgressPills :attempts="detail.attempts" :current-order="attempt.sequenceOrder" />
    <form class="grid gap-6 lg:grid-cols-[1fr_340px]" @submit.prevent="submit">
      <section class="tcf-card">
        <div class="flex flex-wrap items-start justify-between gap-3">
          <div>
            <UiBadge :tone="attempt.isWritten ? 'written' : 'oral'">
              {{ attempt.isWritten ? $t('common.written') : $t('common.oral') }} - {{ $t('common.taskNumber', { number: attempt.question.taskNumber }) }}
            </UiBadge>
            <h1 class="mt-3 text-xl font-bold text-slate-950">{{ attempt.question.taskTypeFr }}</h1>
          </div>
          <CountdownTimer :deadline="attempt.deadlineAt" />
        </div>

        <div class="mt-5 rounded-md border-l-4 p-4" :class="attempt.isWritten ? 'border-emerald-500 bg-emerald-50' : 'border-indigo-500 bg-indigo-50'">
          <blockquote class="text-slate-900">{{ attempt.question.prompt }}</blockquote>
          <QuestionAudioPlayer v-if="attempt.isOral" :src="`/api/sessions/${sessionUuid}/attempts/${order}/question-audio`" />
        </div>

        <template v-if="attempt.isWritten">
          <UiTextarea v-model="answerText" class="mt-5 min-h-80" :placeholder="$t('taskPage.writePlaceholder')" />
          <div class="mt-4 flex flex-wrap items-center justify-between gap-3">
            <WordCounter :text="answerText" :min-words="attempt.question.taskDefinition.wordCountMin" :max-words="attempt.question.taskDefinition.wordCountMax" />
            <UiButton type="submit" :disabled="pending">{{ pending ? $t('taskPage.submitting') : $t('taskPage.submit') }}</UiButton>
          </div>
        </template>

        <template v-else>
          <div class="mt-6">
            <AudioRecorder @recorded="recordedFile = $event" />
          </div>
          <UiTextarea v-model="transcriptText" class="mt-5" :label="$t('taskPage.manualTranscriptFallback')" :placeholder="$t('taskPage.manualTranscriptPlaceholder')" />
          <div class="mt-4 flex flex-wrap items-center justify-between gap-3">
            <p class="text-sm text-slate-500">{{ $t('taskPage.recordingNote') }}</p>
            <UiButton type="submit" :disabled="pending">{{ pending ? $t('taskPage.submitting') : $t('taskPage.submit') }}</UiButton>
          </div>
        </template>
      </section>

      <aside class="space-y-4">
        <UiCard>
          <h2 class="font-semibold text-slate-950">{{ $t('taskPage.boundaries') }}</h2>
          <dl class="mt-3 space-y-2 text-sm text-slate-600">
            <div class="flex justify-between">
              <dt>{{ $t('common.time') }}</dt>
              <dd>{{ attempt.question.taskDefinition.durationMinutes || attempt.question.taskDefinition.suggestedDurationMinutes }} min</dd>
            </div>
            <div v-if="attempt.isWritten" class="flex justify-between">
              <dt>{{ $t('common.words') }}</dt>
              <dd>{{ attempt.question.taskDefinition.wordCountMin }}-{{ attempt.question.taskDefinition.wordCountMax }}</dd>
            </div>
            <div v-if="attempt.question.register" class="flex justify-between gap-4">
              <dt>{{ $t('common.register') }}</dt>
              <dd class="text-right">{{ attempt.question.register }}</dd>
            </div>
            <div v-if="attempt.question.examinerRoleFr" class="flex justify-between gap-4">
              <dt>{{ $t('common.examiner') }}</dt>
              <dd class="text-right">{{ attempt.question.examinerRoleFr }}</dd>
            </div>
          </dl>
        </UiCard>
        <UiCard>
          <h2 class="font-semibold text-slate-950">{{ $t('taskPage.expectedStructure') }}</h2>
          <ol class="mt-3 list-decimal space-y-1 pl-5 text-sm text-slate-600">
            <li v-for="item in attempt.question.expectedResponse.structure || []" :key="item">{{ item }}</li>
          </ol>
        </UiCard>
      </aside>
    </form>
  </div>
</template>

<script setup lang="ts">
import type { AttemptDetailResponse, TaskAttempt } from '~/types/api'

definePageMeta({ requires: 'auth' })

const route = useRoute()
const api = useApi()
const { show } = useFlash()
const { t } = useI18n()
const sessionUuid = computed(() => String(route.params.sessionUuid))
const order = computed(() => Number(route.params.order))

const { data: detail } = await useAsyncData(`attempt-${sessionUuid.value}-${order.value}`, () =>
  api.get<AttemptDetailResponse>(`/api/sessions/${sessionUuid.value}/attempts/${order.value}`),
)

const attempt = computed(() => detail.value!.attempt)
const answerText = ref(detail.value?.attempt.answerText || '')
const transcriptText = ref(detail.value?.attempt.transcriptText || '')
const recordedFile = ref<File | null>(null)
const pending = ref(false)

watch(
  () => detail.value?.attempt,
  (value?: TaskAttempt) => {
    answerText.value = value?.answerText || ''
    transcriptText.value = value?.transcriptText || ''
  },
)

async function submit() {
  pending.value = true
  try {
    if (attempt.value.isWritten) {
      await api.post(`/api/sessions/${sessionUuid.value}/attempts/${order.value}/submit`, {
        answerText: answerText.value,
      })
    } else {
      const formData = new FormData()
      formData.append('transcriptText', transcriptText.value)
      if (recordedFile.value) formData.append('audioFile', recordedFile.value)
      await $fetch(`/api/sessions/${sessionUuid.value}/attempts/${order.value}/submit`, {
        method: 'POST',
        body: formData,
      })
    }
    await navigateTo(`/tests/${sessionUuid.value}/tasks/${order.value}/grade`)
  } catch (err: any) {
    show(err?.data?.detail || t('taskPage.submitFailed'), 'error')
  } finally {
    pending.value = false
  }
}
</script>
