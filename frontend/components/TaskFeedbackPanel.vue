<template>
  <div>
    <div class="flex flex-wrap items-start justify-between gap-4">
      <div>
        <UiBadge :tone="attempt.isWritten ? 'written' : 'oral'">Task {{ attempt.question.taskNumber }}</UiBadge>
        <h1 class="mt-3 text-2xl font-bold text-slate-950">{{ attempt.question.taskTypeFr }}</h1>
        <p class="mt-2 text-sm text-slate-600">{{ attempt.question.prompt }}</p>
      </div>
      <ScoreRing v-if="grade?.status === 'succeeded'" :score="grade.overallScore20" :level="grade.estimatedCefrLevel" />
      <UiBadge v-else :tone="grade?.status === 'failed' ? 'error' : 'warning'">{{ grade?.status || attempt.status }}</UiBadge>
    </div>

    <div class="mt-6 rounded-md border border-slate-200 bg-slate-50 p-4">
      <h2 class="font-semibold text-slate-950">Your response</h2>
      <p class="mt-3 whitespace-pre-wrap text-sm leading-6 text-slate-700">{{ attempt.candidateText || 'No candidate production saved.' }}</p>
    </div>

    <div v-if="grade?.status === 'succeeded'" class="mt-6 space-y-5">
      <div class="grid gap-4 md:grid-cols-2">
        <div class="rounded-md border border-lime-200 bg-lime-50 p-4">
          <h2 class="font-semibold text-lime-950">Strengths</h2>
          <ul class="mt-2 list-disc space-y-1 pl-5 text-sm text-lime-800">
            <li v-for="item in grade.parsedResult.strengths || []" :key="item">{{ item }}</li>
          </ul>
        </div>
        <div class="rounded-md border border-amber-200 bg-amber-50 p-4">
          <h2 class="font-semibold text-amber-950">Improve next</h2>
          <ul class="mt-2 list-disc space-y-1 pl-5 text-sm text-amber-800">
            <li v-for="item in grade.parsedResult.improvementAdviceFr || grade.parsedResult.improvement_advice_fr || []" :key="item">{{ item }}</li>
          </ul>
        </div>
      </div>

      <div class="overflow-hidden rounded-md border border-slate-200">
        <table class="w-full text-left text-sm">
          <thead class="bg-slate-50 text-slate-600">
            <tr><th class="px-3 py-2">Dimension</th><th class="px-3 py-2">Score</th><th class="px-3 py-2">Level</th><th class="px-3 py-2">Justification</th></tr>
          </thead>
          <tbody class="divide-y divide-slate-200 bg-white">
            <tr v-for="value in grade.parsedResult.dimensions || []" :key="value.dimensionId || value.dimension_id">
              <td class="px-3 py-2 font-medium">{{ value.dimensionId || value.dimension_id }}</td>
              <td class="px-3 py-2">{{ value.score20 || value.score_20 }}</td>
              <td class="px-3 py-2">{{ value.level }}</td>
              <td class="px-3 py-2 text-slate-600">{{ value.justification }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <div v-if="grade.audioFeedback && Object.keys(grade.audioFeedback).length" class="rounded-md border border-indigo-200 bg-indigo-50 p-4">
        <div class="flex flex-wrap items-center justify-between gap-2">
          <h2 class="font-semibold text-indigo-950">Audio delivery</h2>
          <span class="text-xs font-medium text-indigo-700">{{ grade.audioFeedback.audioEvidenceUsed || grade.audioFeedback.audio_evidence_used ? 'Audio evidence used' : 'Transcript-only limitation' }}</span>
        </div>
        <div class="mt-3 grid gap-3 md:grid-cols-2">
          <div class="rounded-md bg-white p-3">
            <div class="text-xs font-medium uppercase text-slate-500">Pronunciation</div>
            <div class="mt-1 font-semibold text-slate-950">{{ grade.audioFeedback.pronunciationScore20 || grade.audioFeedback.pronunciation_score_20 || '-' }}/20</div>
          </div>
          <div class="rounded-md bg-white p-3">
            <div class="text-xs font-medium uppercase text-slate-500">Fluency</div>
            <div class="mt-1 font-semibold text-slate-950">{{ grade.audioFeedback.fluencyScore20 || grade.audioFeedback.fluency_score_20 || '-' }}/20</div>
          </div>
        </div>
      </div>
    </div>

    <div v-else-if="grade?.status === 'failed'" class="mt-6 rounded-md border border-red-200 bg-red-50 p-4 text-sm text-red-800">
      {{ grade.errorMessage }}
    </div>
  </div>
</template>

<script setup lang="ts">
import type { TaskAttempt, TaskGrade } from '~/types/api'

defineProps<{ attempt: TaskAttempt; grade: TaskGrade | null }>()
</script>
