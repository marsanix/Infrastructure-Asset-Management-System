<script setup lang="ts">
import { onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()

// ── Theme ─────────────────────────────────────────────────
function applyTheme() {
  const saved       = localStorage.getItem('theme') || 'system'
  const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
  const isDark      = saved === 'dark' || (saved === 'system' && prefersDark)
  document.documentElement.classList.toggle('dark', isDark)
}

onMounted(async () => {
  applyTheme()
  window.matchMedia('(prefers-color-scheme: dark)')
    .addEventListener('change', applyTheme)

  // Auto-restore session dari refresh token di sessionStorage
  // Ini yang mencegah user harus login ulang setiap kali refresh halaman
  await auth.initSession()
})
</script>

<template>
  <RouterView />
</template>
