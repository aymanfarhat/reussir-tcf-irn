export function useWordCount(text: Ref<string>) {
  const wordCount = computed(() => (text.value.match(/[^\W_]+(?:['-][^\W_]+)*/gu) || []).length)

  function wordClass(minWords?: number | null, maxWords?: number | null) {
    if (minWords && wordCount.value < minWords) return 'text-amber-700'
    if (maxWords && wordCount.value > maxWords) return 'text-red-700'
    return 'text-emerald-700'
  }

  return { wordCount, wordClass }
}
