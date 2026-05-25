/**
 * Auth store — Pinia
 *
 * Token storage strategy (sesuai best practice 2025):
 * - Access token  → memory only (tidak persist, hilang saat refresh — by design)
 * - Refresh token → sessionStorage (persist dalam satu browser session/tab)
 *   - Lebih aman dari localStorage: tidak shared antar tab, hilang saat browser ditutup
 *   - Idealnya: HttpOnly cookie via backend (butuh perubahan backend lebih besar)
 *
 * Auto-restore: saat app mount, coba refresh access token dari refresh token
 * yang tersimpan di sessionStorage → user tidak perlu login ulang saat refresh halaman.
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { api } from '@/lib/api'
import router from '@/router'

interface User {
  id:          number
  username:    string
  full_name:   string
  role:        string
  permissions: string[]
}

const REFRESH_TOKEN_KEY = 'iams_rt'  // key di sessionStorage

export const useAuthStore = defineStore('auth', () => {
  // Access token di memory — tidak persist ke storage (XSS protection)
  const accessToken = ref<string | null>(null)
  const user        = ref<User | null>(null)
  const initializing = ref(false)

  const isAuthenticated = computed(() => !!accessToken.value && !!user.value)

  function hasPermission(permission: string): boolean {
    return user.value?.permissions?.includes(permission) ?? false
  }

  // ── Login ─────────────────────────────────────────────────
  async function login(username: string, password: string) {
    const res = await api.post('/auth/login', { username, password })

    accessToken.value = res.data.access_token
    user.value        = res.data.user

    // Simpan refresh token di sessionStorage
    // sessionStorage: hilang saat tab/browser ditutup, tidak shared antar tab
    sessionStorage.setItem(REFRESH_TOKEN_KEY, res.data.refresh_token)

    return res.data
  }

  // ── Logout ────────────────────────────────────────────────
  async function logout() {
    try {
      if (accessToken.value) {
        await api.post('/auth/logout')
      }
    } catch {
      // Tetap logout meski request gagal
    } finally {
      accessToken.value = null
      user.value        = null
      sessionStorage.removeItem(REFRESH_TOKEN_KEY)
      router.push({ name: 'Landing' })
    }
  }

  // ── Refresh access token ──────────────────────────────────
  async function refreshAccessToken(): Promise<string | null> {
    const refreshToken = sessionStorage.getItem(REFRESH_TOKEN_KEY)
    if (!refreshToken) return null

    try {
      const res = await api.post(
        '/auth/refresh',
        {},
        { headers: { Authorization: `Bearer ${refreshToken}` } }
      )
      accessToken.value = res.data.access_token
      return accessToken.value
    } catch {
      // Refresh token expired atau invalid — paksa logout
      accessToken.value = null
      user.value        = null
      sessionStorage.removeItem(REFRESH_TOKEN_KEY)
      return null
    }
  }

  // ── Fetch user data ───────────────────────────────────────
  async function fetchMe(): Promise<boolean> {
    try {
      const res = await api.get('/auth/me')
      user.value = res.data
      return true
    } catch {
      return false
    }
  }

  // ── Auto-restore session saat page refresh ────────────────
  // Dipanggil dari App.vue saat mount
  async function initSession(): Promise<void> {
    const refreshToken = sessionStorage.getItem(REFRESH_TOKEN_KEY)
    if (!refreshToken) return  // Tidak ada session tersimpan

    initializing.value = true
    try {
      // Coba dapatkan access token baru dari refresh token
      const newToken = await refreshAccessToken()
      if (newToken) {
        // Berhasil — ambil data user
        await fetchMe()
      }
    } finally {
      initializing.value = false
    }
  }

  return {
    accessToken,
    user,
    isAuthenticated,
    initializing,
    hasPermission,
    login,
    logout,
    refreshAccessToken,
    fetchMe,
    initSession,
  }
})
