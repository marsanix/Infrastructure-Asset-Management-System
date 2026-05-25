/**
 * Unit tests: auth store (Pinia)
 * Test login, logout, refresh, hasPermission, initSession.
 */
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useAuthStore } from '@/stores/auth'
import { api } from '@/lib/api'

const mockApi = api as { get: ReturnType<typeof vi.fn>; post: ReturnType<typeof vi.fn> }

// Mock sessionStorage
const sessionStorageMock = (() => {
  let store: Record<string, string> = {}
  return {
    getItem:    (k: string) => store[k] ?? null,
    setItem:    (k: string, v: string) => { store[k] = v },
    removeItem: (k: string) => { delete store[k] },
    clear:      () => { store = {} },
  }
})()

Object.defineProperty(globalThis, 'sessionStorage', { value: sessionStorageMock })

const mockUser = {
  id:          1,
  username:    'admin',
  full_name:   'Admin User',
  role:        'Administrator',
  permissions: ['asset:read', 'asset:create', 'asset:update', 'asset:delete', 'account:read'],
}

describe('useAuthStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
    sessionStorageMock.clear()
  })

  describe('initial state', () => {
    it('isAuthenticated false initially', () => {
      const auth = useAuthStore()
      expect(auth.isAuthenticated).toBe(false)
    })

    it('user null initially', () => {
      const auth = useAuthStore()
      expect(auth.user).toBeNull()
    })

    it('accessToken null initially', () => {
      const auth = useAuthStore()
      expect(auth.accessToken).toBeNull()
    })
  })

  describe('login', () => {
    it('sets accessToken and user on success', async () => {
      mockApi.post.mockResolvedValue({
        data: {
          access_token:  'access_123',
          refresh_token: 'refresh_456',
          user:          mockUser,
        },
      })

      const auth = useAuthStore()
      await auth.login('admin', 'password')

      expect(auth.accessToken).toBe('access_123')
      expect(auth.user).toEqual(mockUser)
      expect(auth.isAuthenticated).toBe(true)
    })

    it('stores refresh token in sessionStorage', async () => {
      mockApi.post.mockResolvedValue({
        data: {
          access_token:  'access_123',
          refresh_token: 'refresh_xyz',
          user:          mockUser,
        },
      })

      const auth = useAuthStore()
      await auth.login('admin', 'password')

      expect(sessionStorageMock.getItem('iams_rt')).toBe('refresh_xyz')
    })

    it('throws on API error', async () => {
      mockApi.post.mockRejectedValue(new Error('Invalid credentials'))
      const auth = useAuthStore()
      await expect(auth.login('admin', 'wrong')).rejects.toThrow()
    })

    it('does not store anything on failed login', async () => {
      mockApi.post.mockRejectedValue(new Error('fail'))
      const auth = useAuthStore()
      try { await auth.login('x', 'y') } catch { /* expected */ }
      expect(auth.accessToken).toBeNull()
      expect(auth.user).toBeNull()
      expect(sessionStorageMock.getItem('iams_rt')).toBeNull()
    })
  })

  describe('logout', () => {
    it('clears token and user', async () => {
      // Setup: login dulu
      mockApi.post.mockResolvedValueOnce({
        data: { access_token: 'tok', refresh_token: 'ref', user: mockUser },
      })
      const auth = useAuthStore()
      await auth.login('admin', 'pass')
      expect(auth.isAuthenticated).toBe(true)

      // Logout
      mockApi.post.mockResolvedValueOnce({ data: { message: 'ok' } })
      await auth.logout()

      expect(auth.accessToken).toBeNull()
      expect(auth.user).toBeNull()
      expect(auth.isAuthenticated).toBe(false)
    })

    it('clears sessionStorage on logout', async () => {
      mockApi.post.mockResolvedValueOnce({
        data: { access_token: 'tok', refresh_token: 'ref', user: mockUser },
      })
      const auth = useAuthStore()
      await auth.login('admin', 'pass')
      expect(sessionStorageMock.getItem('iams_rt')).toBeTruthy()

      mockApi.post.mockResolvedValueOnce({ data: {} })
      await auth.logout()
      expect(sessionStorageMock.getItem('iams_rt')).toBeNull()
    })

    it('clears token even if API request fails', async () => {
      mockApi.post.mockResolvedValueOnce({
        data: { access_token: 'tok', refresh_token: 'ref', user: mockUser },
      })
      const auth = useAuthStore()
      await auth.login('admin', 'pass')

      mockApi.post.mockRejectedValueOnce(new Error('Network error'))
      await auth.logout()  // harus tetap logout
      expect(auth.accessToken).toBeNull()
    })
  })

  describe('hasPermission', () => {
    it('returns true for existing permission', async () => {
      mockApi.post.mockResolvedValue({
        data: { access_token: 'tok', refresh_token: 'ref', user: mockUser },
      })
      const auth = useAuthStore()
      await auth.login('admin', 'pass')
      expect(auth.hasPermission('asset:read')).toBe(true)
    })

    it('returns false for missing permission', async () => {
      mockApi.post.mockResolvedValue({
        data: { access_token: 'tok', refresh_token: 'ref', user: mockUser },
      })
      const auth = useAuthStore()
      await auth.login('admin', 'pass')
      expect(auth.hasPermission('nonexistent:action')).toBe(false)
    })

    it('returns false when not logged in', () => {
      const auth = useAuthStore()
      expect(auth.hasPermission('asset:read')).toBe(false)
    })

    it('returns false when user has no permissions array', () => {
      const auth = useAuthStore()
      auth.user = { ...mockUser, permissions: [] }
      expect(auth.hasPermission('asset:read')).toBe(false)
    })
  })

  describe('refreshAccessToken', () => {
    it('returns null when no refresh token in sessionStorage', async () => {
      const auth = useAuthStore()
      const result = await auth.refreshAccessToken()
      expect(result).toBeNull()
    })

    it('updates accessToken on success', async () => {
      sessionStorageMock.setItem('iams_rt', 'stored_refresh_token')
      mockApi.post.mockResolvedValue({ data: { access_token: 'new_access' } })

      const auth = useAuthStore()
      const result = await auth.refreshAccessToken()
      expect(result).toBe('new_access')
      expect(auth.accessToken).toBe('new_access')
    })

    it('clears session on refresh failure', async () => {
      sessionStorageMock.setItem('iams_rt', 'expired_token')
      mockApi.post.mockRejectedValue(new Error('Token expired'))

      const auth = useAuthStore()
      const result = await auth.refreshAccessToken()
      expect(result).toBeNull()
      expect(sessionStorageMock.getItem('iams_rt')).toBeNull()
    })
  })

  describe('initSession', () => {
    it('does nothing when no refresh token', async () => {
      const auth = useAuthStore()
      await auth.initSession()
      expect(auth.isAuthenticated).toBe(false)
    })

    it('restores session when valid refresh token exists', async () => {
      sessionStorageMock.setItem('iams_rt', 'valid_refresh')
      // refreshAccessToken → fetchMe
      mockApi.post.mockResolvedValue({ data: { access_token: 'new_acc' } })
      mockApi.get.mockResolvedValue({ data: mockUser })

      const auth = useAuthStore()
      await auth.initSession()

      expect(auth.accessToken).toBe('new_acc')
      expect(auth.user).toEqual(mockUser)
    })

    it('sets initializing to false after completion', async () => {
      const auth = useAuthStore()
      await auth.initSession()
      expect(auth.initializing).toBe(false)
    })
  })
})
