<template>
  <div class="space-y-8 pb-16">
    <UiCard>
      <h1 class="text-2xl font-bold">{{ $t('uiKit.title') }}</h1>
      <p class="mt-2 text-sm text-slate-600">{{ $t('uiKit.subtitle') }}</p>
    </UiCard>

    <UiCard>
      <h2 class="text-xl font-semibold">{{ $t('uiKit.buttons') }}</h2>
      <div class="mt-4 flex flex-wrap gap-3">
        <UiButton>{{ $t('uiKit.primary') }}</UiButton>
        <UiButton variant="ghost">{{ $t('uiKit.secondary') }}</UiButton>
        <UiButton variant="danger">{{ $t('uiKit.delete') }}</UiButton>
      </div>
    </UiCard>

    <UiCard>
      <h2 class="text-xl font-semibold">{{ $t('uiKit.badges') }}</h2>
      <div class="mt-4 flex flex-wrap gap-2">
        <UiBadge>{{ $t('uiKit.defaultBadge') }}</UiBadge>
        <UiBadge tone="oral">{{ $t('common.oral') }}</UiBadge>
        <UiBadge tone="written">{{ $t('common.written') }}</UiBadge>
        <UiBadge tone="success">{{ $t('uiKit.success') }}</UiBadge>
        <UiBadge tone="warning">{{ $t('uiKit.warning') }}</UiBadge>
        <UiBadge tone="error">{{ $t('uiKit.error') }}</UiBadge>
      </div>
    </UiCard>

    <UiCard>
      <h2 class="text-xl font-semibold">{{ $t('uiKit.scoreRings') }}</h2>
      <div class="mt-4 grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
        <ScoreRing :score="17.5" level="B2" />
        <ScoreRing :score="13" level="B1" />
        <ScoreRing :score="9" level="A2" />
        <ScoreRing :score="5" level="A1" />
      </div>
    </UiCard>
  </div>
</template>
