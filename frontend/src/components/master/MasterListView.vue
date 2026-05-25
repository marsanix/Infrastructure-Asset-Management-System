<script setup lang="ts" generic="T extends { id: number; name: string; is_active?: boolean }">
/**
 * MasterListView — generic list view untuk semua modul master data
 * Dipakai oleh: Department, Location, Category, Brand, Model, Employee
 *
 * Security:
 * - Semua render via {{ }} — tidak ada v-html
 * - Delete memerlukan konfirmasi modal
 * - Permission check sebelum tampilkan tombol aksi
 * - Search dibatasi 100 karakter
 */
import { ref, reactive, onMounted, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '@/stores/auth'
import { useCrud } from '@/composables/useCrud'
import type { Column } from '@/components/ui/CTable.vue'
import CButton       from '@/components/ui/CButton.vue'
import CTable        from '@/components/ui/CTable.vue'
import CBadge        from '@/components/ui/CBadge.vue'
import CPagination   from '@/components/ui/CPagination.vue'
import CModal        from '@/components/ui/CModal.vue'
import CInput        from '@/components/ui/CInput.vue'
import CNotification from '@/components/ui/CNotification.vue'

const props = defineProps<{
  title:           string
  endpoint:        string
  permissionModule: string
  columns:         Column[]
  /** Callback untuk buka form create/edit */
  onCreateClick?:  () => void
  onEditClick?:    (item: T) => void
}>()

const { t }  = useI18n()
const auth   = useAuthStore()
const crud   = useCrud<T>(props.endpoint)

const filters = reactive({ search: '', page: 1, perPage: 50 })
const deleteModal   = ref(false)
const deleteTarget  = ref<T | null>(null)
const deleteLoading = ref(false)
const successMsg    = ref('')

async function load() {
  await crud.fetchAll({
    page:    filters.page,
    perPage: filters.perPage,
    search:  filters.search || undefined,
  })
}

onMounted(load)

let searchTimer: ReturnType<typeof setTimeout>
watch(() => filters.search, () => {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(() => { filters.page = 1; load() }, 400)
})

function onPageChange(page: number) {
  filters.page = page
  load()
}

function confirmDelete(item: T, e: Event) {
  e.stopPropagation()
  deleteTarget.value = item
  deleteModal.value  = true
}

async function handleDelete() {
  if (!deleteTarget.value) return
  deleteLoading.value = true
  const ok = await crud.remove(deleteTarget.value.id)
  deleteLoading.value = false
  deleteModal.value   = false
  if (ok) {
    successMsg.value = t('master.deleteSuccess', { name: deleteTarget.value.name })
    deleteTarget.value = null
    load()
    setTimeout(() => { successMsg.value = '' }, 4000)
  }
}

// Expose untuk parent jika perlu refresh
defineExpose({ load })
</script>

<template>
  <div class="p-sm tablet:p-lg max-w-carbon font-sans">

    <!-- Page header -->
    <div class="flex flex-col mobile:flex-row mobile:items-center mobile:justify-between gap-sm mb-lg border-b border-hairline pb-md">
      <div>
        <p class="type-caption text-ink-muted uppercase tracking-wider">{{ t('master.eyebrow') }}</p>
        <h1 class="type-subhead text-ink mt-xxs">{{ title }}</h1>
      </div>
      <CButton
        v-if="auth.hasPermission(`${permissionModule}:create`) && onCreateClick"
        variant="primary"
        size="md"
        class="w-full mobile:w-auto"
        @click="onCreateClick"
      >
        + {{ t('common.create') }}
      </CButton>
    </div>

    <!-- Notifications -->
    <CNotification v-if="successMsg"        kind="success" :message="successMsg"        class="mb-md" @close="successMsg = ''" />
    <CNotification v-if="crud.error.value"  kind="error"   :message="crud.error.value"  class="mb-md" @close="() => {}" />

    <!-- Search -->
    <div class="mb-md w-full tablet:w-64">
      <CInput
        v-model="filters.search"
        :placeholder="`${t('common.search')} ${title.toLowerCase()}...`"
        :label="t('common.search')"
        autocomplete="off"
      />
    </div>

    <!-- Table -->
    <CTable
      :columns="[
        ...columns,
        { key: '_actions', label: t('common.actions'), width: '140px', align: 'right' },
      ]"
      :rows="(crud.items.value as unknown as Record<string, unknown>[])"
      :loading="crud.loading.value"
      :empty-text="t('common.noData')"
    >
      <!-- Status badge -->
      <template #cell-is_active="{ row }">
        <CBadge :variant="(row as T).is_active ? 'success' : 'neutral'" dot>
          {{ (row as T).is_active ? t('common.active') : t('common.inactive') }}
        </CBadge>
      </template>

      <!-- Pass-through slot untuk kolom custom -->
      <template v-for="col in columns" :key="col.key" #[`cell-${col.key}`]="slotProps">
        <slot :name="`cell-${col.key}`" v-bind="slotProps" />
      </template>

      <!-- Actions -->
      <template #cell-_actions="{ row }">
        <div class="flex items-center justify-end gap-xs" @click.stop>
          <CButton
            v-if="auth.hasPermission(`${permissionModule}:update`) && onEditClick"
            variant="ghost"
            size="sm"
            @click="onEditClick(row as T)"
          >
            {{ t('common.edit') }}
          </CButton>
          <CButton
            v-if="auth.hasPermission(`${permissionModule}:delete`)"
            variant="danger"
            size="sm"
            @click="confirmDelete(row as T, $event)"
          >
            {{ t('common.delete') }}
          </CButton>
        </div>
      </template>
    </CTable>

    <!-- Pagination -->
    <CPagination
      v-if="crud.pagination.pages > 1"
      :page="crud.pagination.page"
      :pages="crud.pagination.pages"
      :total="crud.pagination.total"
      :per-page="crud.pagination.perPage"
      class="mt-md"
      @update:page="onPageChange"
    />

    <!-- Delete confirm modal -->
    <CModal :open="deleteModal" :title="t('common.deleteConfirmTitle')" size="sm" @close="deleteModal = false">
      <p class="type-body-sm text-ink">
        {{ t('master.deleteConfirmMessage', { name: deleteTarget?.name }) }}
      </p>
      <template #footer>
        <CButton variant="ghost" @click="deleteModal = false">{{ t('common.cancel') }}</CButton>
        <CButton variant="danger" :loading="deleteLoading" @click="handleDelete">
          {{ t('common.delete') }}
        </CButton>
      </template>
    </CModal>

  </div>
</template>
