import js from '@eslint/js'
import vue from 'eslint-plugin-vue'
import vueParser from 'vue-eslint-parser'
import tsParser from '@typescript-eslint/parser'
import tsPlugin from '@typescript-eslint/eslint-plugin'
import prettier from 'eslint-config-prettier'

const globals = {
  AbortController: 'readonly',
  Blob: 'readonly',
  BlobPart: 'readonly',
  BodyInit: 'readonly',
  Buffer: 'readonly',
  clearInterval: 'readonly',
  clearTimeout: 'readonly',
  console: 'readonly',
  document: 'readonly',
  DOMException: 'readonly',
  Element: 'readonly',
  fetch: 'readonly',
  File: 'readonly',
  FormData: 'readonly',
  Headers: 'readonly',
  HeadersInit: 'readonly',
  HTMLElementEventMap: 'readonly',
  IntersectionObserver: 'readonly',
  IntersectionObserverInit: 'readonly',
  MathMLElement: 'readonly',
  MediaRecorder: 'readonly',
  MediaStream: 'readonly',
  MutationObserver: 'readonly',
  navigator: 'readonly',
  process: 'readonly',
  Ref: 'readonly',
  requestAnimationFrame: 'readonly',
  Response: 'readonly',
  self: 'readonly',
  setInterval: 'readonly',
  setTimeout: 'readonly',
  shallowRef: 'readonly',
  SVGElement: 'readonly',
  URL: 'readonly',
  window: 'readonly',
  $fetch: 'readonly',
  computed: 'readonly',
  defineEmits: 'readonly',
  defineEventHandler: 'readonly',
  defineNuxtConfig: 'readonly',
  defineNuxtPlugin: 'readonly',
  defineNuxtRouteMiddleware: 'readonly',
  definePageMeta: 'readonly',
  defineProps: 'readonly',
  isRef: 'readonly',
  navigateTo: 'readonly',
  onBeforeUnmount: 'readonly',
  onMounted: 'readonly',
  ref: 'readonly',
  useApi: 'readonly',
  useSession: 'readonly',
  useState: 'readonly',
  withDefaults: 'readonly',
}

export default [
  {
    ignores: ['.nuxt/**', '.nuxt-build/**', '.output/**', 'node_modules/**', 'dist/**'],
  },
  js.configs.recommended,
  ...vue.configs['flat/recommended'],
  prettier,
  {
    files: ['**/*.vue'],
    languageOptions: {
      parser: vueParser,
      parserOptions: {
        ecmaVersion: 'latest',
        parser: tsParser,
        sourceType: 'module',
      },
      globals,
    },
    plugins: {
      '@typescript-eslint': tsPlugin,
    },
    rules: {
      'no-undef': 'off',
      'vue/multi-word-component-names': 'off',
      '@typescript-eslint/no-explicit-any': 'off',
    },
  },
  {
    files: ['**/*.ts'],
    languageOptions: {
      parser: tsParser,
      parserOptions: {
        ecmaVersion: 'latest',
        sourceType: 'module',
      },
      globals,
    },
    plugins: {
      '@typescript-eslint': tsPlugin,
    },
    rules: {
      'no-undef': 'off',
      'vue/multi-word-component-names': 'off',
      '@typescript-eslint/no-explicit-any': 'off',
    },
  },
]
