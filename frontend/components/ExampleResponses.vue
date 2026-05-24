<template>
  <div v-if="responses.length" class="mt-6 rounded-md border border-slate-200 bg-slate-50 p-4">
    <div class="flex flex-wrap items-center justify-between gap-2">
      <h2 class="font-semibold text-slate-950">Example B2 responses</h2>
      <span class="text-xs font-medium text-slate-500">For study, not memorization</span>
    </div>
    <div class="mt-4 space-y-3">
      <details v-for="(response, index) in responses" :key="response.label" class="rounded-md border border-slate-200 bg-white p-4" :open="index === 0">
        <summary class="cursor-pointer text-sm font-semibold text-slate-900">{{ response.label }}</summary>
        <p class="mt-3 whitespace-pre-wrap text-sm leading-6 text-slate-700">{{ response.answer }}</p>
      </details>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{ responses: { label: string; answer: string }[] }>()
</script>
