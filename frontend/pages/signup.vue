<template>
  <div class="mx-auto max-w-md">
    <UiCard>
      <h1 class="text-xl font-bold text-slate-950">Create your account</h1>
      <form class="mt-6 space-y-4" @submit.prevent="submit">
        <UiInput v-model="username" label="Username" required />
        <UiInput v-model="password" label="Password" type="password" required />
        <UiInput v-model="password2" label="Password confirmation" type="password" required />
        <p v-if="error" class="rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-800">{{ error }}</p>
        <UiButton class="w-full" type="submit" :disabled="pending">{{ pending ? 'Creating account...' : 'Create account' }}</UiButton>
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

async function submit() {
  pending.value = true
  error.value = ''
  try {
    await signup(username.value, password.value, password2.value)
    await navigateTo('/')
  } catch (err: any) {
    const data = err?.data
    error.value = data?.detail || JSON.stringify(data || 'Signup failed.')
  } finally {
    pending.value = false
  }
}
</script>
