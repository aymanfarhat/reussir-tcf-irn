<template>
  <div class="mx-auto max-w-3xl">
    <div class="mb-6">
      <h1 class="text-2xl font-bold text-slate-950">{{ $t('practice.title') }}</h1>
      <p class="mt-1 text-sm text-slate-500">{{ $t('practice.subtitle') }}</p>
    </div>

    <form class="tcf-card" @submit.prevent="submit">
      <div class="grid gap-5 md:grid-cols-2">
        <UiSelect v-model="taskNumber" :label="$t('practice.taskType')">
          <option value="">{{ $t('practice.anyTask') }}</option>
          <option v-for="task in options?.taskDefinitions || []" :key="task.sourceId" :value="task.taskNumber">
            {{ $t('common.taskNumber', { number: task.taskNumber }) }} - {{ task.nameFr }}
          </option>
        </UiSelect>
        <UiSelect v-model="theme" :label="$t('practice.theme')">
          <option value="">{{ $t('practice.anyTheme') }}</option>
          <option v-for="item in options?.themes || []" :key="item" :value="item">{{ item }}</option>
        </UiSelect>
      </div>
      <UiButton class="mt-6" type="submit" :disabled="pending">{{ pending ? $t('practice.starting') : $t('practice.startButton') }}</UiButton>
    </form>
  </div>
</template>

<script setup lang="ts">
import type { TaskDefinition, TestSession } from '~/types/api'

definePageMeta({ requires: 'auth' })

const api = useApi()
const { show } = useFlash()
const { t } = useI18n()
const { data: options } = await useAsyncData('practice-options', () =>
  api.get<{ taskDefinitions: TaskDefinition[]; themes: string[] }>('/api/practice-options'),
)
const taskNumber = ref<string | number>('')
const theme = ref('')
const pending = ref(false)

async function submit() {
  pending.value = true
  try {
    const session = await api.post<TestSession>('/api/practice/start', {
      taskNumber: taskNumber.value ? Number(taskNumber.value) : null,
      theme: theme.value,
    })
    await navigateTo(`/tests/${session.uuid}/tasks/1`)
  } catch (err: any) {
    show(err?.data?.detail || t('practice.startFailed'), 'error')
  } finally {
    pending.value = false
  }
}
</script>
