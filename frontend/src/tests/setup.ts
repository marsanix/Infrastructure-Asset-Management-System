/**
 * Global test setup untuk Vitest.
 * Dijalankan sebelum setiap test file.
 */
import { vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import { config } from '@vue/test-utils'
import { createI18n } from 'vue-i18n'
import en from '@/locales/en.json'
import id from '@/locales/id.json'

// Mock router untuk semua test
vi.mock('vue-router', async (importOriginal) => {
  const actual = await importOriginal<typeof import('vue-router')>()
  return {
    ...actual,
    useRouter: () => ({
      push: vi.fn(),
      replace: vi.fn(),
      back: vi.fn(),
      go: vi.fn(),
    }),
    useRoute: () => ({
      params: {},
      query:  {},
      path:   '/',
      name:   'test',
    }),
    RouterLink: { template: '<a><slot /></a>' },
    RouterView: { template: '<div />' },
  }
})

// Mock api untuk semua test
vi.mock('@/lib/api', () => ({
  api: {
    get:    vi.fn(),
    post:   vi.fn(),
    put:    vi.fn(),
    delete: vi.fn(),
  },
}))

// Setup global i18n + Pinia sebelum setiap test
beforeEach(() => {
  setActivePinia(createPinia())

  const i18n = createI18n({
    legacy: false,
    locale: 'id',
    fallbackLocale: 'en',
    messages: { en, id },
  })

  config.global.plugins = [i18n, createPinia()]
})
