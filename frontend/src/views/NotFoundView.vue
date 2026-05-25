<script setup lang="ts">
import { useI18n } from 'vue-i18n'
const { t } = useI18n()
</script>

<template>
  <div class="flex flex-col items-center justify-center h-screen gap-4 font-sans bg-canvas text-ink">
    <h1 class="type-display-xl font-light text-ink-muted">404</h1>
    <p class="type-body-lg text-ink">{{ t('notFound.message') }}</p>
    <RouterLink to="/app" class="type-body-sm text-primary hover:underline">
      {{ t('notFound.backToDashboard') }}
    </RouterLink>
  </div>
</template>
