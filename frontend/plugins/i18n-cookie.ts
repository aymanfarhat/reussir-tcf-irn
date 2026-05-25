type SupportedLocale = 'fr' | 'en'

const SUPPORTED_LOCALES = new Set(['fr', 'en'])

function normalizedLocale(value: string | null | undefined): SupportedLocale {
  return SUPPORTED_LOCALES.has(value || '') ? (value as SupportedLocale) : 'fr'
}

export default defineNuxtPlugin(async (nuxtApp) => {
  const localeCookie = useCookie<SupportedLocale>('tcf_locale', {
    sameSite: 'lax',
    default: () => 'fr',
  })
  const requestedLocale = normalizedLocale(localeCookie.value)
  localeCookie.value = requestedLocale

  const i18n = nuxtApp.$i18n
  if (i18n.locale.value !== requestedLocale) {
    await nuxtApp.runWithContext(() => i18n.setLocale(requestedLocale))
  }
})
