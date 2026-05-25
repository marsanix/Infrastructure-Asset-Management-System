<script setup lang="ts">
/**
 * ReportView — Asset report dengan export CSV/Excel
 * Security:
 * - Export via server-side — tidak ada client-side formula injection risk
 * - Download link menggunakan blob URL yang di-revoke setelah dipakai
 * - Tidak ada v-html
 */
import { ref, reactive, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { api } from '@/lib/api'
import { useCrud } from '@/composables/useCrud'
import { STATUS_BADGE_MAP } from '@/types/asset'
import CButton       from '@/components/ui/CButton.vue'
import CTable        from '@/components/ui/CTable.vue'
import CBadge        from '@/components/ui/CBadge.vue'
import CPagination   from '@/components/ui/CPagination.vue'
import CSelect       from '@/components/ui/CSelect.vue'
import CInput        from '@/components/ui/CInput.vue'
import CCard         from '@/components/ui/CCard.vue'
import CNotification from '@/components/ui/CNotification.vue'

const { t } = useI18n()

interface AssetRow {
  asset_tag: string; serial_number: string; po_number: string
  category: string; brand: string; model: string; status: string
  location: string; employee: string; department: string
  ip_address: string; purchase_date: string; warranty_remaining: string | number
}

interface StatusSummary { status: string; total: number }

const rows       = ref<AssetRow[]>([])
const summary    = ref<StatusSummary[]>([])
const loading    = ref(false)
const exporting  = ref<'csv' | 'excel' | null>(null)
const error      = ref('')
const pagination = reactive({ page: 1, perPage: 50, total: 0, pages: 0 })

const filters = reactive({ status: '', search: '' })

const STATUS_OPTIONS = [
  { value: '', label: t('common.allStatus') },
  { value: 'Active',    label: t('asset.statuses.Active') },
  { value: 'Available', label: t('asset.statuses.Available') },
  { value: 'Repair',    label: t('asset.statuses.Repair') },
  { value: 'Disposed',  label: t('asset.statuses.Disposed') },
]

const columns = [
  { key: 'asset_tag',          label: t('asset.assetTag'),      width: '120px' },
  { key: 'category',           label: t('asset.category'),      width: '100px' },
  { key: 'brand',              label: t('asset.brand'),         width: '100px' },
  { key: 'model',              label: t('asset.model') },
  { key: 'status',             label: t('asset.status'),        width: '110px' },
  { key: 'location',           label: t('asset.location') },
  { key: 'employee',           label: t('asset.employee') },
  { key: 'ip_address',         label: t('asset.ipAddress'),     width: '130px' },
  { key: 'warranty_remaining', label: t('asset.warrantyMonths'), width: '100px' },
]

async function load() {
  loading.value = true
  error.value   = ''
  try {
    const params = new URLSearchParams()
    params.set('page',     String(pagination.page))
    params.set('per_page', String(pagination.perPage))
    if (filters.status) params.set('status', filters.status)
    if (filters.search) params.set('search', filters.search.slice(0, 100))

    const [reportRes, summaryRes] = await Promise.all([
      api.get(`/reports/assets?${params}`),
      api.get('/reports/assets/summary'),
    ])

    rows.value          = reportRes.data.data
    pagination.total    = reportRes.data.total
    pagination.page     = reportRes.data.page
    pagination.pages    = reportRes.data.pages
    summary.value       = summaryRes.data.data
  } catch (err: unknown) {
    error.value = err instanceof Error ? err.message : t('report.failedLoad')
  } finally {
    loading.value = false
  }
}

onMounted(load)

function onPageChange(page: number) { pagination.page = page; load() }

async function exportFile(format: 'csv' | 'excel') {
  exporting.value = format
  try {
    const params = new URLSearchParams()
    if (filters.status) params.set('status', filters.status)
    if (filters.search) params.set('search', filters.search.slice(0, 100))

    const endpoint = format === 'csv'
      ? `/reports/assets/export/csv?${params}`
      : `/reports/assets/export/excel?${params}`

    // Download via axios — blob response
    const res = await api.get(endpoint, { responseType: 'blob' })

    const ext      = format === 'csv' ? 'csv' : 'xlsx'
    const filename = `asset_report_${new Date().toISOString().slice(0, 10)}.${ext}`

    // Buat blob URL, trigger download, lalu revoke — tidak ada data di memory lama
    const url  = URL.createObjectURL(new Blob([res.data]))
    const link = document.createElement('a')
    link.href     = url
    link.download = filename
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)  // cleanup
  } catch (err: unknown) {
    error.value = err instanceof Error ? err.message : t('report.exportFailed')
  } finally {
    exporting.value = null
  }
}
</script>

<template>
  <div class="p-sm tablet:p-lg max-w-carbon font-sans">

    <!-- Header -->
    <div class="flex flex-col mobile:flex-row mobile:items-center mobile:justify-between gap-sm mb-lg border-b border-hairline pb-md">
      <div>
        <p class="type-caption text-ink-muted uppercase tracking-wider">{{ t('report.eyebrow') }}</p>
        <h1 class="type-subhead text-ink mt-xxs">{{ t('nav.reports') }}</h1>
      </div>
      <!-- Export buttons — stack di mobile, row di desktop -->
      <div class="flex gap-xs">
        <CButton variant="secondary" size="sm" :loading="exporting === 'csv'" class="flex-1 mobile:flex-none"
          @click="exportFile('csv')">
          {{ t('common.exportCsv') }}
        </CButton>
        <CButton variant="primary" size="sm" :loading="exporting === 'excel'" class="flex-1 mobile:flex-none"
          @click="exportFile('excel')">
          {{ t('common.exportExcel') }}
        </CButton>
      </div>
    </div>

    <!-- Error -->
    <CNotification v-if="error" kind="error" :message="error" class="mb-lg" @close="error = ''" />

    <!-- Summary cards — 2 kolom mobile, 4 desktop -->
    <div class="grid grid-cols-2 desktop:grid-cols-4 gap-sm tablet:gap-md mb-lg">
      <CCard v-for="s in summary" :key="s.status" variant="feature">
        <CBadge :variant="STATUS_BADGE_MAP[s.status] || 'neutral'" dot class="mb-xs">
          {{ s.status }}
        </CBadge>
        <p class="text-2xl tablet:type-card-title text-ink font-light">{{ s.total }}</p>
        <p class="type-caption text-ink-muted">{{ t('common.units') }}</p>
      </CCard>
    </div>

    <!-- Filters — stack di mobile -->
    <div class="flex flex-col tablet:flex-row flex-wrap gap-sm tablet:gap-md mb-lg">
      <div class="w-full tablet:w-64">
        <CInput v-model="filters.search" :placeholder="t('report.searchPlaceholder')"
          :label="t('common.search')" autocomplete="off" @keyup.enter="load" />
      </div>
      <div class="w-full tablet:w-48">
        <CSelect v-model="filters.status" :label="t('asset.status')" :options="STATUS_OPTIONS"
          @update:model-value="() => { pagination.page = 1; load() }" />
      </div>
      <div class="flex items-end">
        <CButton variant="secondary" size="md" class="w-full tablet:w-auto" @click="() => { pagination.page = 1; load() }">
          {{ t('common.apply') }}
        </CButton>
      </div>
    </div>

    <!-- Table -->
    <CTable
      :columns="columns"
      :rows="(rows as unknown as Record<string, unknown>[])"
      :loading="loading"
      :empty-text="t('common.noData')"
    >
      <template #cell-status="{ row }">
        <CBadge :variant="STATUS_BADGE_MAP[(row as AssetRow).status] || 'neutral'" dot>
          {{ (row as AssetRow).status }}
        </CBadge>
      </template>

      <template #cell-ip_address="{ row }">
        <!-- IP di-render sebagai plain text — tidak ada link -->
        <span class="type-caption font-mono text-ink-muted">
          {{ (row as AssetRow).ip_address || '—' }}
        </span>
      </template>

      <template #cell-warranty_remaining="{ row }">
        <span :class="[
          'type-caption',
          Number((row as AssetRow).warranty_remaining) === 0 ? 'text-error' :
          Number((row as AssetRow).warranty_remaining) <= 3  ? 'text-warning' : 'text-ink-muted'
        ]">
          {{ (row as AssetRow).warranty_remaining !== '' ? `${(row as AssetRow).warranty_remaining} mo` : '—' }}
        </span>
      </template>
    </CTable>

    <!-- Pagination -->
    <CPagination
      v-if="pagination.pages > 1"
      :page="pagination.page"
      :pages="pagination.pages"
      :total="pagination.total"
      :per-page="pagination.perPage"
      class="mt-md"
      @update:page="onPageChange"
    />

  </div>
</template>
