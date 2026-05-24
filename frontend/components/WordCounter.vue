<template>
  <p class="text-sm" :class="wordClass(minWords, maxWords)">
    {{ wordCount }} words. Expected {{ minWords }}-{{ maxWords }}.
  </p>
</template>

<script setup lang="ts">
const props = defineProps<{ text: string; minWords?: number | null; maxWords?: number | null }>()
const textRef = computed(() => props.text)
const { wordCount, wordClass } = useWordCount(textRef)
</script>
