<template>
  <div class="mx-auto max-w-md">
    <UiCard>
      <h1 class="text-xl font-bold text-slate-950">Log in</h1>
      <form class="mt-6 space-y-4" @submit.prevent="submit">
        <UiInput v-model="username" label="Username" required />
        <UiInput v-model="password" label="Password" type="password" required />
        <p v-if="error" class="rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-800">{{ error }}</p>
        <UiButton class="w-full" type="submit" :disabled="pending">{{ pending ? 'Logging in...' : 'Log in' }}</UiButton>
      </form>
      <p class="mt-4 text-sm text-slate-600">
        No account yet?
        <NuxtLink class="font-medium text-indigo-700 hover:text-indigo-900" to="/signup">Create one</NuxtLink>.
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

async function submit() {
  pending.value = true
  error.value = ''
  try {
    await login(username.value, password.value)
    await navigateTo((route.query.returnTo as string) || '/')
  } catch (err: any) {
    error.value = err?.data?.detail || 'Login failed.'
  } finally {
    pending.value = false
  }
}
</script>
