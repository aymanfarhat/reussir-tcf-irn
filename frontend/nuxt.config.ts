export default defineNuxtConfig({
  compatibilityDate: '2026-05-24',
  buildDir: process.env.NUXT_BUILD_DIR || '.nuxt',
  devtools: { enabled: true },
  modules: ['@nuxtjs/i18n'],
  css: ['~/assets/css/base.css'],
  postcss: {
    plugins: {
      '@tailwindcss/postcss': {},
    },
  },
  app: {
    head: {
      title: 'TCF IRN Practice',
      meta: [
        { charset: 'utf-8' },
        { name: 'viewport', content: 'width=device-width, initial-scale=1' },
      ],
    },
  },
  runtimeConfig: {
    djangoInternalBase: process.env.DJANGO_INTERNAL_BASE || 'http://web:8000',
    public: {
      djangoPublicBase: process.env.DJANGO_PUBLIC_BASE || 'http://localhost:8000',
    },
  },
  i18n: {
    defaultLocale: 'fr',
    strategy: 'no_prefix',
    detectBrowserLanguage: false,
    langDir: 'locales',
    locales: [
      { code: 'fr', name: 'Français', language: 'fr-FR', file: 'fr.json' },
      { code: 'en', name: 'English', language: 'en-US', file: 'en.json' },
    ],
  },
  experimental: {
    appManifest: false,
  },
  typescript: {
    strict: true,
  },
})
