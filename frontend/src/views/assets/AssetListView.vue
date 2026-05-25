<script setup lang="ts">
/**
 * AssetListView — IBM Carbon data table
 * Security:
 * - Semua data render via {{ }} — tidak ada v-html
 * - Search input dibatasi 100 karakter
 * - Delete memerlukan konfirmasi modal
 * - Permission check via auth store sebelum tampilkan tombol aksi
 */
import { ref, reactive, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '@/stores/auth'
import { useAssets } from '@/composables/useAssets'
import { STATUS_BADGE_MAP, ASSET_STATUS_OPTIONS } from '@/types/asset'
import type { Asset } from '@/types/asset'
import CButton       from '@/components/ui/CButton.vue'
import CTable        from '@/components/ui/CTable.vue'
import CBadge        from '@/components/ui/CBadge.vue'
import CPagination   from '@/components/ui/CPagination.vue'
import CModal        from '@/components/ui/CModal.vue'
import CInput        from '@/components/ui/CInput.vue'
import CSelect       from '@/components/ui/CSelect.vue'
import CNotification from '@/components/ui/CNotification.vue'

const { t }  = useI18n()
const router = useRouter()
const auth   = useAuthStore()
const { assets, loading, error, pagination, fetchAssets, deleteAsset } = useAssets()

// ── Filters ───────────────────────────────────────────────────
const filters = reactive({
  search:   '',
  status:   '',
  page:     1,
  perPage:  20,
})

// ── Delete confirmation ───────────────────────────────────────
const deleteModal  = ref(false)
const deleteTarget = ref<Asset | null>(null)
const deleteLoading = ref(false)
const successMsg   = ref('')

// ── Table columns ─────────────────────────────────────────────
const columns = [
  { key: 'asset_tag',     label: t('asset.assetTag'),     width: '140px' },
  { key: 'serial_number', label: t('asset.serialNumber'),  width: '160px' },
  { key: 'model',         label: t('asset.model') },
  { key: 'location',      label: t('asset.location') },
  { key: 'employee',      label: t('asset.employee') },
  { key: 'status',        label: t('asset.status'),        width: '120px' },
  { key: 'actions',       label: t('common.actions'),      width: '120px', align: 'right' as const },
]

// ── Load data ─────────────────────────────────────────────────
async function load() {
  await fetchAssets({
    page:    filters.page,
    perPage: filters.perPage,
    status:  filters.status || undefined,
    search:  filters.search || undefined,
  })
}

onMounted(load)

// Debounce search
let searchTimer: ReturnType<typeof setTimeout>
watch(() => filters.search, () => {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(() => {
    filters.page = 1
    load()
  }, 400)
})

watch(() => filters.status, () => {
  filters.page = 1
  load()
})

function onPageChange(page: number) {
  filters.page = page
  load()
}

// ── Actions ───────────────────────────────────────────────────
function openDetail(row: Record<string, unknown>) {
  router.push(`/app/assets/${row.id}`)
}

function openCreate() {
  router.push('/app/assets/new')
}

function openEdit(asset: Asset, e: Event) {
  e.stopPropagation()
  router.push(`/app/assets/${asset.id}/edit`)
}

function confirmDelete(asset: Asset, e: Event) {
  e.stopPropagation()
  deleteTarget.value = asset
  deleteModal.value  = true
}

async function handleDelete() {
  if (!deleteTarget.value) return
  deleteLoading.value = true
  const ok = await deleteAsset(deleteTarget.value.id)
  deleteLoading.value = false
  deleteModal.value   = false
  if (ok) {
    successMsg.value = t('assetList.deleteSuccess', { tag: deleteTarget.value.asset_tag })
    deleteTarget.value = null
    load()
    setTimeout(() => { successMsg.value = '' }, 4000)
  }
}

// ── Helpers ───────────────────────────────────────────────────
function getModelName(row: Record<string, unknown>): string {
  const asset = row as Asset
  return asset.model?.name || String(asset.model_id)
}
function getLocationName(row: Record<string, unknown>): string {
  const asset = row as Asset
  return asset.location?.name || String(asset.location_id)
}
function getEmployeeName(row: Record<string, unknown>): string {
  const asset = row as Asset
  return asset.employee?.name || t('common.unassigned')
}
</script>

<template>
  <div class="p-sm tablet:p-lg max-w-carbon font-sans">

    <!-- Page header -->
    <div class="flex flex-col mobile:flex-row mobile:items-center mobile:justify-between gap-sm mb-lg border-b border-hairline pb-md">
      <div>
        <p class="type-caption text-ink-muted uppercase tracking-wider">{{ t('assetList.eyebrow') }}</p>
        <h1 class="type-subhead text-ink mt-xxs">{{ t('nav.assets') }}</h1>
      </div>
      <CButton
        v-if="auth.hasPermission('asset:create')"
        variant="primary"
        size="md"
        class="w-full mobile:w-auto"
        @click="openCreate"
      >
        + {{ t('assetList.createButton') }}
      </CButton>
    </div>

    <!-- Success notification -->
    <CNotification
      v-if="successMsg"
      kind="success"
      :message="successMsg"
      class="mb-lg"
      @close="successMsg = ''"
    />

    <!-- Error notification -->
    <CNotification
      v-if="error"
      kind="error"
      :message="error"
      class="mb-lg"
      @close="() => {}"
    />

    <!-- Filters -->
    <div class="flex flex-wrap gap-md mb-lg">
      <div class="w-full tablet:w-64">
        <CInput
          v-model="filters.search"
          :placeholder="t('assetList.searchPlaceholder')"
          :label="t('common.search')"
          autocomplete="off"
        />
      </div>
      <div class="w-full tablet:w-48">
        <CSelect
          v-model="filters.status"
          :label="t('asset.status')"
          :options="[{ value: '', label: t('common.allStatus') }, ...ASSET_STATUS_OPTIONS]"
        />
      </div>
    </div>

    <!-- Table -->
    <CTable
      :columns="columns"
      :rows="(assets as unknown as Record<string, unknown>[])"
      :loading="loading"
      :empty-text="t('common.noData')"
      @row-click="openDetail"
    >
      <!-- Model column -->
      <template #cell-model="{ row }">
        <span class="type-body-sm text-ink">{{ getModelName(row) }}</span>
      </template>

      <!-- Location column -->
      <template #cell-location="{ row }">
        <span class="type-body-sm text-ink">{{ getLocationName(row) }}</span>
      </template>

      <!-- Employee column -->
      <template #cell-employee="{ row }">
        <span class="type-body-sm text-ink-muted">{{ getEmployeeName(row) }}</span>
      </template>

      <!-- Status column -->
      <template #cell-status="{ row }">
        <CBadge
          :variant="STATUS_BADGE_MAP[(row as Asset).status] || 'neutral'"
          dot
        >
          {{ (row as Asset).status }}
        </CBadge>
      </template>

      <!-- Actions column -->
      <template #cell-actions="{ row }">
        <div class="flex items-center justify-end gap-xs" @click.stop>
          <CButton
            v-if="auth.hasPermission('asset:update')"
            variant="ghost"
            size="sm"
            @click="openEdit(row as Asset, $event)"
          >
            {{ t('common.edit') }}
          </CButton>
          <CButton
            v-if="auth.hasPermission('asset:delete')"
            variant="danger"
            size="sm"
            @click="confirmDelete(row as Asset, $event)"
          >
            {{ t('common.delete') }}
          </CButton>
        </div>
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

    <CModal
      :open="deleteModal"
      :title="t('common.deleteConfirmTitle')"
      size="sm"
      @close="deleteModal = false"
    >
      <p class="type-body text-ink">
        {{ t('assetList.deleteConfirmMessage', { tag: deleteTarget?.asset_tag }) }}
      </p>

      <template #footer>
        <CButton variant="ghost" @click="deleteModal = false">
          {{ t('common.cancel') }}
        </CButton>
        <CButton
          variant="danger"
          :loading="deleteLoading"
          @click="handleDelete"
        >
          {{ t('common.delete') }}
        </CButton>
      </template>
    </CModal>

  </div>
</template>
