<template>
  <label class="block">
    <span v-if="label" class="tcf-label">{{ label }}</span>
    <input class="tcf-input" :value="modelValue" v-bind="$attrs" @input="emit('update:modelValue', ($event.target as HTMLInputElement).value)" />
  </label>
</template>

<script setup lang="ts">
defineOptions({ inheritAttrs: false })

defineProps<{ label?: string; modelValue: string }>()
const emit = defineEmits<{ 'update:modelValue': [value: string] }>()
</script>
