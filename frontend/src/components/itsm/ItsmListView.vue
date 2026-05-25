<script setup lang="ts">
/**
 * Generic ITSM list view — dipakai Incident, Change, Problem, Request
 * Security: tidak ada v-html, semua render via {{ }}
 * Note: generic type dihapus karena vue-tsc compatibility — pakai unknown + cast
 */
import { reactive, onMounted, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '@/stores/auth'
import { useCrud } from '@/composables/useCrud'
import { STATUS_BADGE, PRIORITY_BADGE } from '@/types/itsm'
import type { Column } from '@/components/ui/CTable.vue'
import CButton       from '@/components/ui/CButton.vue'
import CTable        from '@/components/ui/CTable.vue'
import CBadge        from '@/components/ui/CBadge.vue'
import CPagination   from '@/components/ui/CPagination.vue'
import CInput        from '@/components/ui/CInput.vue'
import CNotification from '@/components/ui/CNotification.vue'

interface ItsmItem {
  id:        number
  title:     string
  status:    string
  priority?: string
}

const props = defineProps<{
  title:            string
  endpoint:         string
  permissionModule: string
  columns:          Column[]
  onCreateClick?:   () => void
  onRowClick?:      (item: ItsmItem) => void
}>()

const { t } = useI18n()
const auth  = useAuthStore()
const crud  = useCrud<ItsmItem>(props.endpoint)

const filters = reactive({ search: '', page: 1, perPage: 20 })

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

function onPageChange(page: number) { filters.page = page; load() }

defineExpose({ load })
</script>

<template>
  <div class="p-sm tablet:p-lg max-w-carbon font-sans">
    <div class="flex flex-col mobile:flex-row mobile:items-center mobile:justify-between gap-sm mb-lg border-b border-hairline pb-md">
      <div>
        <p class="type-caption text-ink-muted uppercase tracking-wider">{{ t('itsm.eyebrow') }}</p>
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

    <CNotification
      v-if="crud.error.value"
      kind="error"
      :message="crud.error.value"
      class="mb-md"
      @close="() => {}"
    />

    <div class="mb-md w-full tablet:w-64">
      <CInput
        v-model="filters.search"
        :placeholder="t('itsm.searchPlaceholder', { module: title.toLowerCase() })"
        :label="t('common.search')"
        autocomplete="off"
      />
    </div>

    <CTable
      :columns="columns"
      :rows="(crud.items.value as unknown as Record<string, unknown>[])"
      :loading="crud.loading.value"
      :empty-text="t('common.noData')"
      @row-click="(row) => onRowClick?.(row as unknown as ItsmItem)"
    >
      <template #cell-status="{ row }">
        <CBadge :variant="STATUS_BADGE[(row as ItsmItem).status] || 'neutral'" dot>
          {{ (row as ItsmItem).status }}
        </CBadge>
      </template>

      <template #cell-priority="{ row }">
        <CBadge :variant="PRIORITY_BADGE[(row as ItsmItem).priority || ''] || 'neutral'">
          {{ (row as ItsmItem).priority || '—' }}
        </CBadge>
      </template>

      <template v-for="col in columns" :key="col.key" #[`cell-${col.key}`]="slotProps">
        <slot :name="`cell-${col.key}`" v-bind="slotProps" />
      </template>
    </CTable>

    <CPagination
      v-if="crud.pagination.pages > 1"
      :page="crud.pagination.page"
      :pages="crud.pagination.pages"
      :total="crud.pagination.total"
      :per-page="crud.pagination.perPage"
      class="mt-md"
      @update:page="onPageChange"
    />
  </div>
</template>
