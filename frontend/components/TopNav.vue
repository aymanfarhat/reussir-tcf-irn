<template>
  <header class="sticky top-0 z-30 border-b border-slate-200 bg-white/95 backdrop-blur">
    <div class="mx-auto flex max-w-7xl items-center justify-between gap-4 px-4 py-4 sm:px-6 lg:px-8">
      <NuxtLink to="/" class="min-w-0">
        <div class="text-lg font-bold text-slate-950">TCF IRN Practice</div>
        <div class="text-xs text-slate-500">Timed simulations for oral and written production</div>
      </NuxtLink>
      <button class="tcf-btn tcf-btn-ghost md:hidden" type="button" @click="open = !open">
        Menu
      </button>
      <nav class="hidden items-center gap-2 text-sm md:flex">
        <template v-if="isLoggedIn">
          <NuxtLink class="tcf-btn tcf-btn-ghost" to="/practice">Practice</NuxtLink>
          <NuxtLink class="tcf-btn tcf-btn-ghost" to="/tests/history">History</NuxtLink>
          <a class="tcf-btn tcf-btn-ghost" href="/admin/">Admin</a>
          <button class="tcf-btn tcf-btn-ghost" type="button" @click="logout">Log out</button>
        </template>
        <template v-else>
          <NuxtLink class="tcf-btn tcf-btn-ghost" to="/login">Log in</NuxtLink>
          <NuxtLink class="tcf-btn tcf-btn-primary" to="/signup">Sign up</NuxtLink>
        </template>
      </nav>
    </div>
    <nav v-if="open" class="border-t border-slate-200 px-4 py-3 md:hidden">
      <div class="grid gap-2">
        <template v-if="isLoggedIn">
          <NuxtLink class="tcf-btn tcf-btn-ghost" to="/practice" @click="open = false">Practice</NuxtLink>
          <NuxtLink class="tcf-btn tcf-btn-ghost" to="/tests/history" @click="open = false">History</NuxtLink>
          <a class="tcf-btn tcf-btn-ghost" href="/admin/">Admin</a>
          <button class="tcf-btn tcf-btn-ghost" type="button" @click="logout">Log out</button>
        </template>
        <template v-else>
          <NuxtLink class="tcf-btn tcf-btn-ghost" to="/login" @click="open = false">Log in</NuxtLink>
          <NuxtLink class="tcf-btn tcf-btn-primary" to="/signup" @click="open = false">Sign up</NuxtLink>
        </template>
      </div>
    </nav>
  </header>
</template>

<script setup lang="ts">
const open = ref(false)
const { isLoggedIn, logout } = useSession()
</script>
