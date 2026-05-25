<script setup lang="ts">
import { useI18n } from 'vue-i18n'

const { locale } = useI18n()

function toggle() {
  const next   = locale.value === 'id' ? 'en' : 'id'
  locale.value = next
  localStorage.setItem('locale', next)
}
</script>

<template>
  <button
    class="p-xs text-ink-muted hover:text-ink hover:bg-surface-1 rounded-none transition-colors type-caption uppercase"
    aria-label="Toggle language"
    @click="toggle"
  >
    {{ locale === 'id' ? 'EN' : 'ID' }}
  </button>
</template>
