<template>
  <component :is="to ? NuxtLink : 'button'" :to="to || undefined" class="tcf-btn" :class="variantClass" v-bind="$attrs">
    <slot />
  </component>
</template>

<script setup lang="ts">
defineOptions({ inheritAttrs: false })

const NuxtLink = resolveComponent('NuxtLink')
const props = withDefaults(
  defineProps<{
    variant?: 'primary' | 'ghost' | 'danger'
    to?: string
  }>(),
  { variant: 'primary', to: '' },
)

const variantClass = computed(() => {
  if (props.variant === 'ghost') return 'tcf-btn-ghost'
  if (props.variant === 'danger') return 'tcf-btn-danger'
  return 'tcf-btn-primary'
})
</script>
