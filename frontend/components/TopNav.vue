<template>
  <header class="sticky top-0 z-30 border-b border-slate-200 bg-white/95 backdrop-blur">
    <div class="mx-auto flex max-w-7xl items-center justify-between gap-4 px-4 py-4 sm:px-6 lg:px-8">
      <NuxtLink to="/" class="min-w-0">
        <div class="text-lg font-bold text-slate-950">{{ $t('app.name') }}</div>
        <div class="text-xs text-slate-500">{{ $t('app.tagline') }}</div>
      </NuxtLink>
      <button class="tcf-btn tcf-btn-ghost md:hidden" type="button" @click="open = !open">
        {{ $t('nav.menu') }}
      </button>
      <nav class="hidden items-center gap-2 text-sm md:flex">
        <template v-if="isLoggedIn">
          <NuxtLink class="tcf-btn tcf-btn-ghost" to="/practice">{{ $t('nav.practice') }}</NuxtLink>
          <NuxtLink class="tcf-btn tcf-btn-ghost" to="/tests/history">{{ $t('nav.history') }}</NuxtLink>
          <NuxtLink class="tcf-btn tcf-btn-ghost" to="/settings">{{ $t('nav.settings') }}</NuxtLink>
          <button class="tcf-btn tcf-btn-ghost" type="button" @click="logout">{{ $t('nav.logout') }}</button>
        </template>
        <template v-else>
          <NuxtLink class="tcf-btn tcf-btn-ghost" to="/login">{{ $t('nav.login') }}</NuxtLink>
          <NuxtLink class="tcf-btn tcf-btn-primary" to="/signup">{{ $t('nav.signup') }}</NuxtLink>
        </template>
      </nav>
    </div>
    <nav v-if="open" class="border-t border-slate-200 px-4 py-3 md:hidden">
      <div class="grid gap-2">
        <template v-if="isLoggedIn">
          <NuxtLink class="tcf-btn tcf-btn-ghost" to="/practice" @click="open = false">{{ $t('nav.practice') }}</NuxtLink>
          <NuxtLink class="tcf-btn tcf-btn-ghost" to="/tests/history" @click="open = false">{{ $t('nav.history') }}</NuxtLink>
          <NuxtLink class="tcf-btn tcf-btn-ghost" to="/settings" @click="open = false">{{ $t('nav.settings') }}</NuxtLink>
          <button class="tcf-btn tcf-btn-ghost" type="button" @click="logout">{{ $t('nav.logout') }}</button>
        </template>
        <template v-else>
          <NuxtLink class="tcf-btn tcf-btn-ghost" to="/login" @click="open = false">{{ $t('nav.login') }}</NuxtLink>
          <NuxtLink class="tcf-btn tcf-btn-primary" to="/signup" @click="open = false">{{ $t('nav.signup') }}</NuxtLink>
        </template>
      </div>
    </nav>
  </header>
</template>

<script setup lang="ts">
const open = ref(false)
const { isLoggedIn, logout } = useSession()
</script>
