<template>
  <div class="space-y-8 pb-16">
    <UiCard>
      <h1 class="text-2xl font-bold">UI Kit</h1>
      <p class="mt-2 text-sm text-slate-600">TCF IRN components, tokens, and score treatments.</p>
    </UiCard>

    <UiCard>
      <h2 class="text-xl font-semibold">Buttons</h2>
      <div class="mt-4 flex flex-wrap gap-3">
        <UiButton>Primary action</UiButton>
        <UiButton variant="ghost">Secondary action</UiButton>
        <UiButton variant="danger">Delete</UiButton>
      </div>
    </UiCard>

    <UiCard>
      <h2 class="text-xl font-semibold">Badges</h2>
      <div class="mt-4 flex flex-wrap gap-2">
        <UiBadge>Default</UiBadge>
        <UiBadge tone="oral">Oral</UiBadge>
        <UiBadge tone="written">Written</UiBadge>
        <UiBadge tone="success">Success</UiBadge>
        <UiBadge tone="warning">Warning</UiBadge>
        <UiBadge tone="error">Error</UiBadge>
      </div>
    </UiCard>

    <UiCard>
      <h2 class="text-xl font-semibold">Score rings</h2>
      <div class="mt-4 grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
        <ScoreRing :score="17.5" level="B2" />
        <ScoreRing :score="13" level="B1" />
        <ScoreRing :score="9" level="A2" />
        <ScoreRing :score="5" level="A1" />
      </div>
    </UiCard>
  </div>
</template>
