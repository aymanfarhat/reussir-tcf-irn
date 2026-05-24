<template>
  <label class="block">
    <span v-if="label" class="tcf-label">{{ label }}</span>
    <select class="tcf-input" :value="modelValue" v-bind="$attrs" @change="emit('update:modelValue', ($event.target as HTMLSelectElement).value)">
      <slot />
    </select>
  </label>
</template>

<script setup lang="ts">
defineOptions({ inheritAttrs: false })

defineProps<{ label?: string; modelValue: string | number | null }>()
const emit = defineEmits<{ 'update:modelValue': [value: string] }>()
</script>
