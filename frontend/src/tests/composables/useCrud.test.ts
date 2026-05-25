/**
 * Unit tests: useCrud composable
 * Test fetchAll, create, update, remove, fetchOptions dengan mock API.
 */
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { useCrud } from '@/composables/useCrud'
import { api } from '@/lib/api'

// api sudah di-mock di setup.ts
const mockApi = api as { get: ReturnType<typeof vi.fn>; post: ReturnType<typeof vi.fn>; put: ReturnType<typeof vi.fn>; delete: ReturnType<typeof vi.fn> }

interface TestItem { id: number; name: string }

const mockPaginatedResponse = (data: TestItem[]) => ({
  data: {
    data,
    total:    data.length,
    page:     1,
    per_page: 50,
    pages:    1,
  },
})

describe('useCrud', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('fetchAll', () => {
    it('populates items on success', async () => {
      const items = [{ id: 1, name: 'Item 1' }, { id: 2, name: 'Item 2' }]
      mockApi.get.mockResolvedValue(mockPaginatedResponse(items))

      const { fetchAll, items: result, loading, error } = useCrud<TestItem>('/test')
      await fetchAll()

      expect(result.value).toEqual(items)
      expect(loading.value).toBe(false)
      expect(error.value).toBeNull()
    })

    it('sets error on failure', async () => {
      mockApi.get.mockRejectedValue(new Error('Network error'))
      const { fetchAll, error } = useCrud<TestItem>('/test')
      await fetchAll()
      expect(error.value).toBe('Network error')
    })

    it('sets loading true during fetch', async () => {
      let resolvePromise!: () => void
      mockApi.get.mockReturnValue(new Promise((r) => { resolvePromise = () => r(mockPaginatedResponse([])) }))

      const { fetchAll, loading } = useCrud<TestItem>('/test')
      const fetchPromise = fetchAll()
      expect(loading.value).toBe(true)
      resolvePromise()
      await fetchPromise
      expect(loading.value).toBe(false)
    })

    it('applies search filter to URL params', async () => {
      mockApi.get.mockResolvedValue(mockPaginatedResponse([]))
      const { fetchAll } = useCrud<TestItem>('/test')
      await fetchAll({ search: 'keyword' })
      const callUrl = mockApi.get.mock.calls[0][0] as string
      expect(callUrl).toContain('search=keyword')
    })

    it('truncates search to 100 chars', async () => {
      mockApi.get.mockResolvedValue(mockPaginatedResponse([]))
      const { fetchAll } = useCrud<TestItem>('/test')
      await fetchAll({ search: 'x'.repeat(200) })
      const callUrl = mockApi.get.mock.calls[0][0] as string
      const searchParam = new URL(`http://localhost${callUrl}`).searchParams.get('search')
      expect(searchParam!.length).toBeLessThanOrEqual(100)
    })

    it('updates pagination state from response', async () => {
      mockApi.get.mockResolvedValue({
        data: { data: [], total: 100, page: 2, per_page: 20, pages: 5 },
      })
      const { fetchAll, pagination } = useCrud<TestItem>('/test')
      await fetchAll({ page: 2, perPage: 20 })
      expect(pagination.total).toBe(100)
      expect(pagination.pages).toBe(5)
      expect(pagination.page).toBe(2)
    })
  })

  describe('create', () => {
    it('returns created item on success', async () => {
      const newItem = { id: 3, name: 'New Item' }
      mockApi.post.mockResolvedValue({ data: newItem })
      const { create } = useCrud<TestItem>('/test')
      const result = await create({ name: 'New Item' })
      expect(result).toEqual(newItem)
    })

    it('returns null on failure', async () => {
      mockApi.post.mockRejectedValue(new Error('Server error'))
      const { create, error } = useCrud<TestItem>('/test')
      const result = await create({ name: 'Bad' })
      expect(result).toBeNull()
      expect(error.value).toBeTruthy()
    })
  })

  describe('update', () => {
    it('returns updated item on success', async () => {
      const updated = { id: 1, name: 'Updated' }
      mockApi.put.mockResolvedValue({ data: updated })
      const { update } = useCrud<TestItem>('/test')
      const result = await update(1, { name: 'Updated' })
      expect(result).toEqual(updated)
    })

    it('calls correct URL', async () => {
      mockApi.put.mockResolvedValue({ data: { id: 5, name: 'x' } })
      const { update } = useCrud<TestItem>('/departments')
      await update(5, { name: 'IT' })
      expect(mockApi.put).toHaveBeenCalledWith('/departments/5', { name: 'IT' })
    })
  })

  describe('remove', () => {
    it('returns true on success', async () => {
      mockApi.delete.mockResolvedValue({ data: {} })
      const { remove } = useCrud<TestItem>('/test')
      const result = await remove(1)
      expect(result).toBe(true)
    })

    it('returns false on failure', async () => {
      mockApi.delete.mockRejectedValue(new Error('Not found'))
      const { remove } = useCrud<TestItem>('/test')
      const result = await remove(999)
      expect(result).toBe(false)
    })

    it('calls correct URL', async () => {
      mockApi.delete.mockResolvedValue({})
      const { remove } = useCrud<TestItem>('/assets')
      await remove(42)
      expect(mockApi.delete).toHaveBeenCalledWith('/assets/42')
    })
  })

  describe('fetchOptions', () => {
    it('returns items on success', async () => {
      const items = [{ id: 1, name: 'Opt 1' }]
      mockApi.get.mockResolvedValue(mockPaginatedResponse(items))
      const { fetchOptions } = useCrud<TestItem>('/test')
      const result = await fetchOptions()
      expect(result).toEqual(items)
    })

    it('returns empty array on failure', async () => {
      mockApi.get.mockRejectedValue(new Error('fail'))
      const { fetchOptions } = useCrud<TestItem>('/test')
      const result = await fetchOptions()
      expect(result).toEqual([])
    })
  })
})
