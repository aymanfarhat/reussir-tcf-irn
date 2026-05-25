<template>
  <div class="mx-auto max-w-md">
    <UiCard>
      <h1 class="text-xl font-bold text-slate-950">{{ $t('auth.login') }}</h1>
      <form class="mt-6 space-y-4" @submit.prevent="submit">
        <UiInput v-model="username" :label="$t('auth.username')" required />
        <UiInput v-model="password" :label="$t('auth.password')" type="password" required />
        <p v-if="error" class="rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-800">{{ error }}</p>
        <UiButton class="w-full" type="submit" :disabled="pending">{{ pending ? $t('auth.loggingIn') : $t('auth.login') }}</UiButton>
      </form>
      <p class="mt-4 text-sm text-slate-600">
        {{ $t('auth.noAccount') }}
        <NuxtLink class="font-medium text-indigo-700 hover:text-indigo-900" to="/signup">{{ $t('auth.createAccount') }}</NuxtLink>.
      </p>
    </UiCard>
  </div>
</template>

<script setup lang="ts">
const username = ref('')
const password = ref('')
const pending = ref(false)
const error = ref('')
const route = useRoute()
const { login } = useSession()
const { t } = useI18n()

async function submit() {
  pending.value = true
  error.value = ''
  try {
    await login(username.value, password.value)
    await navigateTo((route.query.returnTo as string) || '/')
  } catch (err: any) {
    error.value = err?.data?.detail || t('auth.loginFailed')
  } finally {
    pending.value = false
  }
}
</script>
