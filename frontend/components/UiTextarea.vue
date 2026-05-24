<template>
  <label class="block">
    <span v-if="label" class="tcf-label">{{ label }}</span>
    <textarea class="tcf-input min-h-40 leading-7" :value="modelValue" v-bind="$attrs" @input="emit('update:modelValue', ($event.target as HTMLTextAreaElement).value)" />
  </label>
</template>

<script setup lang="ts">
defineOptions({ inheritAttrs: false })

defineProps<{ label?: string; modelValue: string }>()
const emit = defineEmits<{ 'update:modelValue': [value: string] }>()
</script>
