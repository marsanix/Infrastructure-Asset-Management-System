/**
 * useCrud — generic CRUD composable
 * Digunakan oleh semua modul master data (Department, Location, Category, Brand, Model, Employee)
 * Pattern dari VueUse: return reactive state + async actions
 */
import { ref, reactive } from 'vue'
import { api } from '@/lib/api'
import type { PaginatedResponse } from '@/types/asset'

export interface CrudFilters {
  page?:        number
  perPage?:     number
  search?:      string
  activeOnly?:  boolean
}

export function useCrud<T extends { id: number }>(endpoint: string) {
  const items      = ref<T[]>([])
  const item       = ref<T | null>(null)
  const loading    = ref(false)
  const error      = ref<string | null>(null)
  const pagination = reactive({ page: 1, perPage: 50, total: 0, pages: 0 })

  async function fetchAll(filters: CrudFilters = {}) {
    loading.value = true
    error.value   = null
    try {
      const params = new URLSearchParams()
      params.set('page',     String(filters.page     ?? pagination.page))
      params.set('per_page', String(filters.perPage  ?? pagination.perPage))
      if (filters.search)                    params.set('search',      filters.search.slice(0, 100))
      if (filters.activeOnly !== undefined)  params.set('active_only', String(filters.activeOnly))

      const res = await api.get<PaginatedResponse<T>>(`${endpoint}?${params}`)
      items.value         = res.data.data
      pagination.total    = res.data.total
      pagination.page     = res.data.page
      pagination.perPage  = res.data.per_page
      pagination.pages    = res.data.pages
    } catch (err: unknown) {
      error.value = err instanceof Error ? err.message : 'Failed to load data'
    } finally {
      loading.value = false
    }
  }

  async function fetchOne(id: number) {
    loading.value = true
    error.value   = null
    try {
      const res = await api.get<T>(`${endpoint}/${id}`)
      item.value = res.data
    } catch (err: unknown) {
      error.value = err instanceof Error ? err.message : 'Item not found'
    } finally {
      loading.value = false
    }
  }

  async function create(payload: Partial<T>): Promise<T | null> {
    loading.value = true
    error.value   = null
    try {
      const res = await api.post<T>(endpoint, payload)
      return res.data
    } catch (err: unknown) {
      error.value = err instanceof Error ? err.message : 'Failed to create'
      return null
    } finally {
      loading.value = false
    }
  }

  async function update(id: number, payload: Partial<T>): Promise<T | null> {
    loading.value = true
    error.value   = null
    try {
      const res = await api.put<T>(`${endpoint}/${id}`, payload)
      return res.data
    } catch (err: unknown) {
      error.value = err instanceof Error ? err.message : 'Failed to update'
      return null
    } finally {
      loading.value = false
    }
  }

  async function remove(id: number): Promise<boolean> {
    loading.value = true
    error.value   = null
    try {
      await api.delete(`${endpoint}/${id}`)
      return true
    } catch (err: unknown) {
      error.value = err instanceof Error ? err.message : 'Failed to delete'
      return false
    } finally {
      loading.value = false
    }
  }

  /** Fetch semua tanpa pagination — untuk dropdown options */
  async function fetchOptions(): Promise<T[]> {
    try {
      const res = await api.get<PaginatedResponse<T>>(`${endpoint}?per_page=500&active_only=true`)
      return res.data.data
    } catch {
      return []
    }
  }

  return {
    items, item, loading, error, pagination,
    fetchAll, fetchOne, create, update, remove, fetchOptions,
  }
}
