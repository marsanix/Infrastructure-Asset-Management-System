/**
 * Axios instance dengan interceptor:
 * - Inject Authorization header otomatis
 * - Auto-refresh token saat 401
 * - Sanitasi response (tidak expose stack trace)
 */
import axios, { type AxiosError } from 'axios'

export const api = axios.create({
  baseURL: '/api/v1',
  timeout: 15000,
  headers: { 'Content-Type': 'application/json' },
  withCredentials: true,
})

// ── Request interceptor — inject access token ─────────────────
// Gunakan dynamic import async untuk hindari circular dependency
api.interceptors.request.use(async (config) => {
  const { useAuthStore } = await import('@/stores/auth')
  const auth = useAuthStore()

  if (auth.accessToken) {
    config.headers.Authorization = `Bearer ${auth.accessToken}`
  }
  return config
})

// ── Response interceptor — handle 401 & refresh ───────────────
let isRefreshing = false
let failedQueue: Array<{ resolve: (v: string) => void; reject: (e: unknown) => void }> = []

function processQueue(error: unknown, token: string | null) {
  failedQueue.forEach((p) => (error ? p.reject(error) : p.resolve(token!)))
  failedQueue = []
}

api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as typeof error.config & { _retry?: boolean }

    if (error.response?.status === 401 && !originalRequest._retry) {
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject })
        }).then((token) => {
          originalRequest.headers!.Authorization = `Bearer ${token}`
          return api(originalRequest)
        })
      }

      originalRequest._retry = true
      isRefreshing = true

      const { useAuthStore } = await import('@/stores/auth')
      const auth = useAuthStore()

      try {
        const newToken = await auth.refreshAccessToken()
        if (newToken) {
          processQueue(null, newToken)
          originalRequest.headers!.Authorization = `Bearer ${newToken}`
          return api(originalRequest)
        }
      } catch (refreshError) {
        processQueue(refreshError, null)
        return Promise.reject(refreshError)
      } finally {
        isRefreshing = false
      }
    }

    // Sanitasi error — jangan expose detail internal ke user
    const message = (error.response?.data as { error?: string })?.error
      || 'An unexpected error occurred'

    return Promise.reject(new Error(message))
  }
)
