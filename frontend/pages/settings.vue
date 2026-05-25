<template>
  <div class="mx-auto max-w-3xl">
    <div class="mb-6">
      <h1 class="text-2xl font-bold text-slate-950">{{ $t('settings.title') }}</h1>
      <p class="mt-1 text-sm text-slate-500">{{ $t('settings.subtitle') }}</p>
    </div>

    <section class="tcf-card">
      <div class="grid gap-5 md:grid-cols-[1fr_auto] md:items-end">
        <UiSelect v-model="selectedLocale" :label="$t('settings.language')">
          <option value="fr">{{ $t('settings.french') }}</option>
          <option value="en">{{ $t('settings.english') }}</option>
        </UiSelect>
        <div class="rounded-md border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-700">
          <span class="font-medium text-slate-950">{{ $t('settings.current') }}:</span>
          {{ currentLocaleLabel }}
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
type SupportedLocale = 'fr' | 'en'

definePageMeta({ requires: 'auth' })

const { locale, setLocale, t } = useI18n()
const { show } = useFlash()
const localeCookie = useCookie<SupportedLocale>('tcf_locale', {
  sameSite: 'lax',
  default: () => 'fr',
})
const selectedLocale = ref<SupportedLocale>(locale.value === 'en' ? 'en' : 'fr')
const currentLocaleLabel = computed(() =>
  locale.value === 'en' ? t('settings.english') : t('settings.french'),
)

watch(
  () => locale.value,
  (value) => {
    selectedLocale.value = value === 'en' ? 'en' : 'fr'
  },
)

watch(selectedLocale, async (value) => {
  localeCookie.value = value
  await setLocale(value)
  show(t('settings.saved'), 'success')
})
</script>
