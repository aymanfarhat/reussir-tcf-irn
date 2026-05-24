<template>
  <div class="min-h-screen bg-tcf-paper text-slate-800 antialiased">
    <TopNav />
    <main class="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
      <FlashBanner />
      <slot />
    </main>
  </div>
</template>
