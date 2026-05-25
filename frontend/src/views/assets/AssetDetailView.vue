<script setup lang="ts">
/**
 * AssetDetailView — detail aset + history
 * Security: semua data render via {{ }}, tidak ada v-html
 */
import { onMounted, ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '@/stores/auth'
import { useAssets } from '@/composables/useAssets'
import { STATUS_BADGE_MAP } from '@/types/asset'
import CButton       from '@/components/ui/CButton.vue'
import CCard         from '@/components/ui/CCard.vue'
import CBadge        from '@/components/ui/CBadge.vue'
import CModal        from '@/components/ui/CModal.vue'
import CNotification from '@/components/ui/CNotification.vue'

const { t }  = useI18n()
const route  = useRoute()
const router = useRouter()
const auth   = useAuthStore()

const assetId = computed(() => Number(route.params.id))
const { asset, loading, error, fetchAsset, deleteAsset, fetchHistory } = useAssets()

const history      = ref<Record<string, unknown>[]>([])
const deleteModal  = ref(false)
const deleteLoading = ref(false)

onMounted(async () => {
  await fetchAsset(assetId.value)
  history.value = await fetchHistory(assetId.value)
})

async function handleDelete() {
  deleteLoading.value = true
  const ok = await deleteAsset(assetId.value)
  deleteLoading.value = false
  if (ok) router.push('/app/assets')
}

// Hitung sisa garansi
function warrantyRemaining(purchaseDate: string | null | undefined, months: number | null | undefined): string {
  if (!purchaseDate || !months) return '—'
  const purchase = new Date(purchaseDate)
  const expiry   = new Date(purchase)
  expiry.setMonth(expiry.getMonth() + months)
  const now      = new Date()
  if (expiry <= now) return 'Expired'
  const diffMs   = expiry.getTime() - now.getTime()
  const diffMo   = Math.floor(diffMs / (1000 * 60 * 60 * 24 * 30))
  return `${diffMo} months remaining`
}

function formatDate(d: string | null | undefined): string {
  if (!d) return '—'
  return new Date(d).toLocaleDateString('id-ID', { year: 'numeric', month: 'long', day: 'numeric' })
}
</script>

<template>
  <div class="p-sm tablet:p-lg max-w-carbon font-sans">

    <!-- Breadcrumb + actions — responsive -->
    <div class="flex flex-col mobile:flex-row mobile:items-center gap-sm mb-lg border-b border-hairline pb-md">
      <div class="flex items-center gap-sm flex-1 min-w-0">
        <button class="type-body-sm text-primary hover:underline whitespace-nowrap flex-shrink-0" @click="router.push('/app/assets')">
          {{ t('assetDetail.backToAssets') }}
        </button>
        <span class="text-hairline hidden mobile:block">|</span>
        <h1 class="type-subhead text-ink truncate">
          {{ asset?.asset_tag || t('assetDetail.defaultTitle') }}
        </h1>
      </div>
      <template v-if="asset">
        <div class="flex gap-xs">
          <CButton
            v-if="auth.hasPermission('asset:update')"
            variant="secondary"
            size="sm"
            class="flex-1 mobile:flex-none"
            @click="router.push(`/app/assets/${assetId}/edit`)"
          >
            {{ t('common.edit') }}
          </CButton>
          <CButton
            v-if="auth.hasPermission('asset:delete')"
            variant="danger"
            size="sm"
            class="flex-1 mobile:flex-none"
            @click="deleteModal = true"
          >
            {{ t('common.delete') }}
          </CButton>
        </div>
      </template>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="flex items-center gap-xs text-ink-muted py-xxl">
      <span class="w-4 h-4 border-2 border-primary border-t-transparent rounded-full animate-spin" aria-hidden="true" />
      {{ t('common.loading') }}
    </div>

    <!-- Error -->
    <CNotification v-else-if="error" kind="error" :message="error" @close="() => {}" />

    <!-- Content -->
    <template v-else-if="asset">
      <!-- Desktop: 2/3 + 1/3, Mobile: stack -->
      <div class="grid grid-cols-1 desktop:grid-cols-3 gap-lg">

        <!-- Left: Main info (2 cols desktop) -->
        <div class="desktop:col-span-2 space-y-lg">

          <!-- Identity -->
          <CCard variant="feature">
            <h2 class="type-body-emphasis text-ink mb-md">{{ t('assetDetail.assetInfo') }}</h2>
            <dl class="grid grid-cols-1 mobile:grid-cols-2 tablet:grid-cols-3 gap-md">
              <div>
                <dt class="type-caption text-ink-muted">{{ t('asset.assetTag') }}</dt>
                <dd class="type-body-emphasis text-ink mt-xxs">{{ asset.asset_tag }}</dd>
              </div>
              <div>
                <dt class="type-caption text-ink-muted">{{ t('asset.serialNumber') }}</dt>
                <dd class="type-body-sm text-ink mt-xxs break-all">{{ asset.serial_number }}</dd>
              </div>
              <div>
                <dt class="type-caption text-ink-muted">{{ t('asset.poNumber') }}</dt>
                <dd class="type-body-sm text-ink mt-xxs">{{ asset.po_number || '—' }}</dd>
              </div>
              <div>
                <dt class="type-caption text-ink-muted">{{ t('asset.status') }}</dt>
                <dd class="mt-xxs">
                  <CBadge :variant="STATUS_BADGE_MAP[asset.status] || 'neutral'" dot>
                    {{ asset.status }}
                  </CBadge>
                </dd>
              </div>
              <div>
                <dt class="type-caption text-ink-muted">{{ t('asset.model') }}</dt>
                <dd class="type-body-sm text-ink mt-xxs">{{ asset.model?.name || '—' }}</dd>
              </div>
              <div>
                <dt class="type-caption text-ink-muted">{{ t('asset.brand') }}</dt>
                <dd class="type-body-sm text-ink mt-xxs">{{ asset.model?.brand?.name || '—' }}</dd>
              </div>
              <div>
                <dt class="type-caption text-ink-muted">{{ t('asset.category') }}</dt>
                <dd class="type-body-sm text-ink mt-xxs">{{ asset.model?.category?.name || '—' }}</dd>
              </div>
              <div>
                <dt class="type-caption text-ink-muted">{{ t('asset.location') }}</dt>
                <dd class="type-body-sm text-ink mt-xxs">{{ asset.location?.name || '—' }}</dd>
              </div>
              <div>
                <dt class="type-caption text-ink-muted">{{ t('asset.employee') }}</dt>
                <dd class="type-body-sm text-ink mt-xxs">{{ asset.employee?.name || t('common.unassigned') }}</dd>
              </div>
            </dl>
          </CCard>

          <!-- Purchase & Warranty -->
          <CCard variant="feature">
            <h2 class="type-body-emphasis text-ink mb-md">{{ t('assetDetail.purchaseWarranty') }}</h2>
            <dl class="grid grid-cols-1 mobile:grid-cols-2 tablet:grid-cols-3 gap-md">
              <div>
                <dt class="type-caption text-ink-muted">{{ t('asset.purchaseDate') }}</dt>
                <dd class="type-body-sm text-ink mt-xxs">{{ formatDate(asset.purchase_date) }}</dd>
              </div>
              <div>
                <dt class="type-caption text-ink-muted">{{ t('asset.warrantyMonths') }}</dt>
                <dd class="type-body-sm text-ink mt-xxs">{{ asset.warranty_months ? `${asset.warranty_months} bulan` : '—' }}</dd>
              </div>
              <div>
                <dt class="type-caption text-ink-muted">{{ t('asset.warrantyStatus') }}</dt>
                <dd class="type-body-sm text-ink mt-xxs">
                  {{ warrantyRemaining(asset.purchase_date, asset.warranty_months) }}
                </dd>
              </div>
              <div>
                <dt class="type-caption text-ink-muted">{{ t('asset.osLicense') }}</dt>
                <dd class="type-body-sm text-ink mt-xxs">{{ asset.os_license || '—' }}</dd>
              </div>
            </dl>
          </CCard>

          <!-- Network -->
          <CCard v-if="asset.network" variant="feature">
            <h2 class="type-body-emphasis text-ink mb-md">{{ t('assetDetail.networkDetails') }}</h2>
            <dl class="grid grid-cols-1 mobile:grid-cols-2 gap-md">
              <div>
                <dt class="type-caption text-ink-muted">{{ t('asset.ipAddress') }}</dt>
                <dd class="type-body-sm text-ink mt-xxs font-mono break-all">{{ asset.network.ip_address || '—' }}</dd>
              </div>
              <div>
                <dt class="type-caption text-ink-muted">{{ t('asset.macAddress') }}</dt>
                <dd class="type-body-sm text-ink mt-xxs font-mono break-all">{{ asset.network.mac_address || '—' }}</dd>
              </div>
              <div>
                <dt class="type-caption text-ink-muted">{{ t('asset.hostname') }}</dt>
                <dd class="type-body-sm text-ink mt-xxs">{{ asset.network.hostname || '—' }}</dd>
              </div>
              <div>
                <dt class="type-caption text-ink-muted">{{ t('asset.vlan') }}</dt>
                <dd class="type-body-sm text-ink mt-xxs">{{ asset.network.vlan || '—' }}</dd>
              </div>
            </dl>
          </CCard>

          <!-- Notes -->
          <CCard v-if="asset.notes" variant="elevated">
            <h2 class="type-body-emphasis text-ink mb-sm">{{ t('assetDetail.notes') }}</h2>
            <p class="type-body-sm text-ink whitespace-pre-wrap break-words">{{ asset.notes }}</p>
          </CCard>
        </div>

        <!-- Right: History (full width on mobile, 1/3 on desktop) -->
        <div>
          <CCard variant="elevated">
            <h2 class="type-body-emphasis text-ink mb-md">{{ t('assetDetail.changeHistory') }}</h2>
            <div v-if="!history.length" class="type-body-sm text-ink-muted">{{ t('common.noHistory') }}</div>
            <ol v-else class="space-y-md">
              <li
                v-for="log in history"
                :key="(log.id as number)"
                class="border-l-2 border-hairline pl-md"
              >
                <p class="type-body-emphasis text-ink">{{ log.action }}</p>
                <p class="type-caption text-ink-muted mt-xxs">{{ formatDate(log.created_at as string) }}</p>
                <p class="type-caption text-ink-subtle">IP: {{ log.ip_address || '—' }}</p>
              </li>
            </ol>
          </CCard>
        </div>

      </div>
    </template>

    <!-- Delete modal -->
    <CModal :open="deleteModal" title="Confirm Delete" size="sm" @close="deleteModal = false">
      <p class="type-body text-ink">
        Delete asset <strong>{{ asset?.asset_tag }}</strong>? This action cannot be undone.
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
