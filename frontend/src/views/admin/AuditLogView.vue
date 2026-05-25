<script setup lang="ts">
/**
 * AuditLogView — READ ONLY, tidak ada tombol edit/delete
 * Security: sensitive fields di-mask oleh backend, UI hanya display
 */
import { reactive, onMounted, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useCrud } from '@/composables/useCrud'
import CTable      from '@/components/ui/CTable.vue'
import CPagination from '@/components/ui/CPagination.vue'
import CInput      from '@/components/ui/CInput.vue'
import CSelect     from '@/components/ui/CSelect.vue'
import CBadge      from '@/components/ui/CBadge.vue'
import CNotification from '@/components/ui/CNotification.vue'

interface AuditLog {
  id: number; account_id: number | null; action: string; module: string
  record_id: number | null; ip_address: string | null; created_at: string
}

const { t } = useI18n()
const crud  = useCrud<AuditLog>('/audit-logs')

const filters = reactive({ search: '', module: '', action: '', page: 1, perPage: 50 })

const MODULE_OPTIONS = [
  { value: '', label: t('common.allModules') },
  ...['asset', 'account', 'incident', 'change', 'problem', 'request', 'auth'].map(m => ({ value: m, label: m })),
]

const ACTION_OPTIONS = [
  { value: '', label: t('common.allActions') },
  ...['CREATE', 'UPDATE', 'DELETE', 'LOGIN', 'LOGOUT', 'PASSWORD_RESET', 'UNLOCK'].map(a => ({ value: a, label: a })),
]

const ACTION_BADGE: Record<string, 'success' | 'info' | 'warning' | 'error' | 'neutral'> = {
  CREATE:         'success',
  UPDATE:         'info',
  DELETE:         'error',
  LOGIN:          'neutral',
  LOGOUT:         'neutral',
  PASSWORD_RESET: 'warning',
  UNLOCK:         'warning',
  LOGIN_FAILED:   'error',
}

const columns = [
  { key: 'created_at', label: t('common.time'),     width: '160px' },
  { key: 'action',     label: t('common.action'),   width: '120px' },
  { key: 'module',     label: t('common.module'),   width: '100px' },
  { key: 'record_id',  label: t('common.recordId'), width: '100px' },
  { key: 'account_id', label: t('common.account'),  width: '100px' },
  { key: 'ip_address', label: t('common.ip'),       width: '130px' },
]

async function load() {
  await crud.fetchAll({ page: filters.page, perPage: filters.perPage })
}

onMounted(load)
watch(() => [filters.module, filters.action], () => { filters.page = 1; load() })

function onPageChange(page: number) { filters.page = page; load() }

function formatDate(d: string): string {
  return new Date(d).toLocaleString('id-ID', { dateStyle: 'short', timeStyle: 'medium' })
}
</script>

<template>
  <div class="p-sm tablet:p-lg max-w-carbon font-sans">
    <div class="mb-lg border-b border-hairline pb-md">
      <p class="type-caption text-ink-muted uppercase tracking-wider">{{ t('audit.eyebrow') }}</p>
      <h1 class="type-subhead text-ink mt-xxs">{{ t('nav.auditLogs') }}</h1>
      <p class="type-body-sm text-ink-muted mt-xs">{{ t('audit.readOnly') }}</p>
    </div>

    <CNotification v-if="crud.error.value" kind="error" :message="crud.error.value" class="mb-lg" @close="() => {}" />

    <!-- Filters — stack di mobile -->
    <div class="flex flex-col mobile:flex-row flex-wrap gap-sm tablet:gap-md mb-lg">
      <div class="w-full mobile:w-40">
        <CSelect v-model="filters.module" :label="t('common.module')" :options="MODULE_OPTIONS" />
      </div>
      <div class="w-full mobile:w-48">
        <CSelect v-model="filters.action" :label="t('common.action')" :options="ACTION_OPTIONS" />
      </div>
    </div>

    <CTable
      :columns="columns"
      :rows="(crud.items.value as unknown as Record<string, unknown>[])"
      :loading="crud.loading.value"
      :empty-text="t('common.noData')"
    >
      <template #cell-created_at="{ row }">
        <span class="type-caption text-ink-muted font-mono">
          {{ formatDate((row as AuditLog).created_at) }}
        </span>
      </template>

      <template #cell-action="{ row }">
        <CBadge :variant="ACTION_BADGE[(row as AuditLog).action] || 'neutral'">
          {{ (row as AuditLog).action }}
        </CBadge>
      </template>

      <template #cell-module="{ row }">
        <span class="type-caption text-ink">{{ (row as AuditLog).module }}</span>
      </template>

      <template #cell-ip_address="{ row }">
        <!-- IP di-render sebagai plain text — tidak ada link atau v-html -->
        <span class="type-caption text-ink-muted font-mono">
          {{ (row as AuditLog).ip_address || '—' }}
        </span>
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
