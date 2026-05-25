/**
 * useAssets — composable untuk Asset CRUD
 * - Semua API call lewat axios instance yang sudah ada auth interceptor
 * - Error handling terpusat
 * - Tidak ada data sensitif di-log ke console di production
 */
import { ref, reactive } from 'vue'
import { api } from '@/lib/api'
import type { Asset, AssetFilters, PaginatedResponse } from '@/types/asset'

export function useAssets() {
  const assets    = ref<Asset[]>([])
  const asset     = ref<Asset | null>(null)
  const loading   = ref(false)
  const error     = ref<string | null>(null)
  const pagination = reactive({ page: 1, perPage: 20, total: 0, pages: 0 })

  async function fetchAssets(filters: AssetFilters = {}) {
    loading.value = true
    error.value   = null
    try {
      const params = new URLSearchParams()
      params.set('page',     String(filters.page     || pagination.page))
      params.set('per_page', String(filters.perPage  || pagination.perPage))
      if (filters.status)     params.set('status',      filters.status)
      if (filters.search)     params.set('search',      filters.search.slice(0, 100))
      if (filters.locationId) params.set('location_id', String(filters.locationId))
      if (filters.categoryId) params.set('category_id', String(filters.categoryId))

      const res = await api.get<PaginatedResponse<Asset>>(`/assets?${params}`)
      assets.value        = res.data.data
      pagination.total    = res.data.total
      pagination.page     = res.data.page
      pagination.perPage  = res.data.per_page
      pagination.pages    = res.data.pages
    } catch (err: unknown) {
      error.value = err instanceof Error ? err.message : 'Failed to load assets'
    } finally {
      loading.value = false
    }
  }

  async function fetchAsset(id: number) {
    loading.value = true
    error.value   = null
    try {
      const res  = await api.get<Asset>(`/assets/${id}`)
      asset.value = res.data
    } catch (err: unknown) {
      error.value = err instanceof Error ? err.message : 'Asset not found'
    } finally {
      loading.value = false
    }
  }

  async function createAsset(payload: Partial<Asset>): Promise<Asset | null> {
    loading.value = true
    error.value   = null
    try {
      const res = await api.post<Asset>('/assets', payload)
      return res.data
    } catch (err: unknown) {
      error.value = err instanceof Error ? err.message : 'Failed to create asset'
      return null
    } finally {
      loading.value = false
    }
  }

  async function updateAsset(id: number, payload: Partial<Asset>): Promise<Asset | null> {
    loading.value = true
    error.value   = null
    try {
      const res = await api.put<Asset>(`/assets/${id}`, payload)
      return res.data
    } catch (err: unknown) {
      error.value = err instanceof Error ? err.message : 'Failed to update asset'
      return null
    } finally {
      loading.value = false
    }
  }

  async function deleteAsset(id: number): Promise<boolean> {
    loading.value = true
    error.value   = null
    try {
      await api.delete(`/assets/${id}`)
      return true
    } catch (err: unknown) {
      error.value = err instanceof Error ? err.message : 'Failed to delete asset'
      return false
    } finally {
      loading.value = false
    }
  }

  async function fetchHistory(id: number) {
    const res = await api.get(`/assets/${id}/history`)
    return res.data.data
  }

  return {
    assets, asset, loading, error, pagination,
    fetchAssets, fetchAsset, createAsset, updateAsset, deleteAsset, fetchHistory,
  }
}
