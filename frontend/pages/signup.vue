<template>
  <div class="mx-auto max-w-md">
    <UiCard>
      <h1 class="text-xl font-bold text-slate-950">{{ $t('auth.createAccount') }}</h1>
      <form class="mt-6 space-y-4" @submit.prevent="submit">
        <UiInput v-model="username" :label="$t('auth.username')" required />
        <UiInput v-model="password" :label="$t('auth.password')" type="password" required />
        <UiInput v-model="password2" :label="$t('auth.passwordConfirmation')" type="password" required />
        <p v-if="error" class="rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-800">{{ error }}</p>
        <UiButton class="w-full" type="submit" :disabled="pending">{{ pending ? $t('auth.creatingAccount') : $t('auth.createAccount') }}</UiButton>
      </form>
    </UiCard>
  </div>
</template>

<script setup lang="ts">
const username = ref('')
const password = ref('')
const password2 = ref('')
const pending = ref(false)
const error = ref('')
const { signup } = useSession()
const { t } = useI18n()

async function submit() {
  pending.value = true
  error.value = ''
  try {
    await signup(username.value, password.value, password2.value)
    await navigateTo('/')
  } catch (err: any) {
    const data = err?.data
    error.value = data?.detail || JSON.stringify(data || t('auth.signupFailed'))
  } finally {
    pending.value = false
  }
}
</script>
