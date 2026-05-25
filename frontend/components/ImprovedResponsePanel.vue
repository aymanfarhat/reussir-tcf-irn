<template>
  <div v-if="grade?.improvedResponseStatus === 'succeeded' && grade.improvedResponse" class="mt-6 rounded-md border border-emerald-200 bg-emerald-50 p-4">
    <div class="flex flex-wrap items-center justify-between gap-2">
      <h2 class="font-semibold text-emerald-950">{{ $t('improved.title') }}</h2>
      <span class="text-xs font-medium text-emerald-700">{{ $t('improved.subtitle') }}</span>
    </div>
    <pre class="mt-4 whitespace-pre-wrap rounded-md border border-emerald-200 bg-white p-4 text-sm leading-6 text-slate-800">{{ grade.improvedResponse.improved_response_fr || grade.improvedResponse.improvedResponseFr }}</pre>
    <div class="mt-4 grid gap-3 md:grid-cols-3">
      <div class="rounded-md bg-white p-3">
        <h3 class="text-sm font-semibold text-slate-950">{{ $t('improved.whatChanged') }}</h3>
        <ul class="mt-2 list-disc space-y-1 pl-5 text-sm text-slate-600">
          <li v-for="item in grade.improvedResponse.changesMade || grade.improvedResponse.changes_made || []" :key="item">{{ item }}</li>
        </ul>
      </div>
      <div class="rounded-md bg-white p-3">
        <h3 class="text-sm font-semibold text-slate-950">{{ $t('improved.reusablePhrases') }}</h3>
        <ul class="mt-2 list-disc space-y-1 pl-5 text-sm text-slate-600">
          <li v-for="item in grade.improvedResponse.reusablePhrases || grade.improvedResponse.reusable_phrases || []" :key="item">{{ item }}</li>
        </ul>
      </div>
      <div class="rounded-md bg-white p-3">
        <h3 class="text-sm font-semibold text-slate-950">{{ $t('improved.nextFocus') }}</h3>
        <ul class="mt-2 list-disc space-y-1 pl-5 text-sm text-slate-600">
          <li v-for="item in grade.improvedResponse.focusNextTime || grade.improvedResponse.focus_next_time || []" :key="item">{{ item }}</li>
        </ul>
      </div>
    </div>
  </div>
  <div v-else-if="grade?.improvedResponseStatus === 'failed'" class="mt-6 rounded-md border border-amber-200 bg-amber-50 p-4 text-sm text-amber-800">
    {{ $t('improved.failed', { message: grade.improvedResponseError }) }}
  </div>
</template>

<script setup lang="ts">
import type { TaskGrade } from '~/types/api'

defineProps<{ grade: TaskGrade | null }>()
</script>
