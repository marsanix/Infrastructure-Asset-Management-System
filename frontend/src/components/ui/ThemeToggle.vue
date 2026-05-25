<script setup lang="ts">
function toggle() {
  const html   = document.documentElement
  const isDark = html.classList.contains('dark')
  html.classList.toggle('dark', !isDark)
  localStorage.setItem('theme', isDark ? 'light' : 'dark')
}
</script>

<template>
  <button
    class="p-xs text-ink-muted hover:text-ink hover:bg-surface-1 rounded-none transition-colors type-caption"
    aria-label="Toggle theme"
    @click="toggle"
  >
    ◑
  </button>
</template>
