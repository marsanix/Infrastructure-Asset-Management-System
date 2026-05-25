<script setup lang="ts">
/**
 * AssetDetailView — detail aset + credentials + history
 * Security: semua data render via {{ }}, tidak ada v-html
 */
import { onMounted, ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '@/stores/auth'
import { useAssets } from '@/composables/useAssets'
import { api } from '@/lib/api'
import { STATUS_BADGE_MAP } from '@/types/asset'
import CButton       from '@/components/ui/CButton.vue'
import CCard         from '@/components/ui/CCard.vue'
import CBadge        from '@/components/ui/CBadge.vue'
import CModal        from '@/components/ui/CModal.vue'
import CInput        from '@/components/ui/CInput.vue'
import CSelect       from '@/components/ui/CSelect.vue'
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

// ── Credentials state ─────────────────────────────────────────
interface Credential {
  id: number
  asset_id: number
  credential_type: string
  username: string | null
  notes: string | null
  created_at: string
  password?: string  // hanya ada setelah reveal
}

const credentials     = ref<Credential[]>([])
const credLoading     = ref(false)
const credError       = ref('')
const revealedPasswords = ref<Record<number, string>>({})

// Add credential modal
const credModal       = ref(false)
const credSubmitting  = ref(false)
const newCred = ref({ credential_type: 'SSH', username: '', password: '', notes: '' })

const CREDENTIAL_TYPES = [
  { value: 'SSH',         label: 'SSH' },
  { value: 'Web Console', label: 'Web Console' },
  { value: 'SNMP',        label: 'SNMP' },
  { value: 'Telnet',      label: 'Telnet' },
  { value: 'RDP',         label: 'RDP' },
  { value: 'API Key',     label: 'API Key' },
  { value: 'Other',       label: 'Other' },
]

// Delete credential
const credDeleteModal  = ref(false)
const credDeleteTarget = ref<Credential | null>(null)
const credDeleteLoading = ref(false)

async function loadCredentials() {
  if (!auth.hasPermission('credential:read')) return
  credLoading.value = true
  credError.value   = ''
  try {
    const res = await api.get(`/assets/${assetId.value}/credentials`)
    credentials.value = res.data.data
  } catch (err: unknown) {
    credError.value = err instanceof Error ? err.message : 'Gagal memuat kredensial'
  } finally {
    credLoading.value = false
  }
}

async function revealPassword(cred: Credential) {
  if (revealedPasswords.value[cred.id]) {
    // Toggle hide
    delete revealedPasswords.value[cred.id]
    return
  }
  try {
    const res = await api.get(`/assets/${assetId.value}/credentials/${cred.id}/reveal`)
    revealedPasswords.value[cred.id] = res.data.password || '(empty)'
  } catch (err: unknown) {
    credError.value = err instanceof Error ? err.message : 'Gagal reveal password'
  }
}

function openAddCredential() {
  newCred.value = { credential_type: 'SSH', username: '', password: '', notes: '' }
  credModal.value = true
}

async function submitCredential() {
  credSubmitting.value = true
  credError.value = ''
  try {
    await api.post(`/assets/${assetId.value}/credentials`, {
      credential_type: newCred.value.credential_type,
      username:        newCred.value.username || null,
      password:        newCred.value.password,
      notes:           newCred.value.notes || null,
    })
    credModal.value = false
    newCred.value.password = ''  // clear dari memory
    await loadCredentials()
  } catch (err: unknown) {
    credError.value = err instanceof Error ? err.message : 'Gagal menambah kredensial'
  } finally {
    credSubmitting.value = false
  }
}

function confirmDeleteCred(cred: Credential) {
  credDeleteTarget.value = cred
  credDeleteModal.value  = true
}

async function handleDeleteCred() {
  if (!credDeleteTarget.value) return
  credDeleteLoading.value = true
  try {
    await api.delete(`/assets/${assetId.value}/credentials/${credDeleteTarget.value.id}`)
    credDeleteModal.value = false
    credDeleteTarget.value = null
    await loadCredentials()
  } catch (err: unknown) {
    credError.value = err instanceof Error ? err.message : 'Gagal menghapus kredensial'
  } finally {
    credDeleteLoading.value = false
  }
}

onMounted(async () => {
  await fetchAsset(assetId.value)
  history.value = await fetchHistory(assetId.value)
  await loadCredentials()
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

          <!-- ── Credentials Section (AES-256 Encrypted) ──────── -->
          <CCard v-if="auth.hasPermission('credential:read')" variant="feature">
            <div class="flex items-center justify-between mb-md">
              <h2 class="type-body-emphasis text-ink">Kredensial Perangkat</h2>
              <CButton
                v-if="auth.hasPermission('credential:create')"
                variant="primary"
                size="sm"
                @click="openAddCredential"
              >
                + Tambah
              </CButton>
            </div>

            <p class="type-caption text-ink-muted mb-md">
              Password disimpan terenkripsi AES-256. Setiap akses reveal tercatat di audit log.
            </p>

            <CNotification v-if="credError" kind="error" :message="credError" class="mb-md" @close="credError = ''" />

            <!-- Loading -->
            <div v-if="credLoading" class="flex items-center gap-xs text-ink-muted py-md">
              <span class="w-4 h-4 border-2 border-primary border-t-transparent rounded-full animate-spin" aria-hidden="true" />
              {{ t('common.loading') }}
            </div>

            <!-- Empty state -->
            <div v-else-if="!credentials.length" class="py-md text-center">
              <p class="type-body-sm text-ink-muted">Belum ada kredensial untuk aset ini.</p>
            </div>

            <!-- Credential list -->
            <div v-else class="space-y-xs">
              <div
                v-for="cred in credentials"
                :key="cred.id"
                class="border border-hairline p-sm"
              >
                <div class="flex items-start justify-between gap-sm">
                  <div class="flex-1 min-w-0">
                    <div class="flex items-center gap-xs mb-xxs">
                      <CBadge variant="info">{{ cred.credential_type }}</CBadge>
                      <span v-if="cred.username" class="type-body-sm text-ink font-medium">{{ cred.username }}</span>
                    </div>

                    <!-- Password field -->
                    <div class="flex items-center gap-xs mt-xs">
                      <span class="type-caption text-ink-muted">Password:</span>
                      <code v-if="revealedPasswords[cred.id]" class="type-body-sm text-ink bg-surface-1 px-xs py-xxs font-mono break-all">
                        {{ revealedPasswords[cred.id] }}
                      </code>
                      <span v-else class="type-body-sm text-ink-muted">••••••••••</span>
                    </div>

                    <!-- Notes -->
                    <p v-if="cred.notes" class="type-caption text-ink-subtle mt-xs">{{ cred.notes }}</p>
                  </div>

                  <!-- Actions -->
                  <div class="flex items-center gap-xxs flex-shrink-0">
                    <CButton
                      variant="ghost"
                      size="sm"
                      @click="revealPassword(cred)"
                    >
                      {{ revealedPasswords[cred.id] ? 'Sembunyikan' : 'Reveal' }}
                    </CButton>
                    <CButton
                      v-if="auth.hasPermission('credential:delete')"
                      variant="danger"
                      size="sm"
                      @click="confirmDeleteCred(cred)"
                    >
                      Hapus
                    </CButton>
                  </div>
                </div>
              </div>
            </div>
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

    <!-- Delete asset modal -->
    <CModal :open="deleteModal" :title="t('common.deleteConfirmTitle')" size="sm" @close="deleteModal = false">
      <p class="type-body-sm text-ink">
        {{ t('assetDetail.deleteConfirmMessage', { tag: asset?.asset_tag }) }}
      </p>
      <template #footer>
        <CButton variant="ghost" @click="deleteModal = false">{{ t('common.cancel') }}</CButton>
        <CButton variant="danger" :loading="deleteLoading" @click="handleDelete">
          {{ t('common.delete') }}
        </CButton>
      </template>
    </CModal>

    <!-- Add credential modal -->
    <CModal :open="credModal" title="Tambah Kredensial" size="md" @close="credModal = false">
      <form class="space-y-md" @submit.prevent="submitCredential" novalidate>
        <CSelect
          v-model="newCred.credential_type"
          label="Tipe Credential"
          :options="CREDENTIAL_TYPES"
        />
        <CInput
          v-model="newCred.username"
          label="Username"
          placeholder="admin / root / ..."
          autocomplete="off"
        />
        <CInput
          v-model="newCred.password"
          label="Password"
          type="password"
          required
          placeholder="Password perangkat"
          autocomplete="new-password"
        />
        <CInput
          v-model="newCred.notes"
          label="Catatan (opsional)"
          placeholder="Contoh: Password router lantai 3"
          autocomplete="off"
        />
      </form>
      <template #footer>
        <CButton variant="ghost" @click="credModal = false">{{ t('common.cancel') }}</CButton>
        <CButton variant="primary" :loading="credSubmitting" @click="submitCredential">
          Simpan (Terenkripsi)
        </CButton>
      </template>
    </CModal>

    <!-- Delete credential modal -->
    <CModal :open="credDeleteModal" title="Hapus Kredensial" size="sm" @close="credDeleteModal = false">
      <p class="type-body-sm text-ink">
        Hapus kredensial <strong>{{ credDeleteTarget?.credential_type }}</strong>
        ({{ credDeleteTarget?.username || 'no username' }})? Tindakan ini tidak dapat dibatalkan.
      </p>
      <template #footer>
        <CButton variant="ghost" @click="credDeleteModal = false">{{ t('common.cancel') }}</CButton>
        <CButton variant="danger" :loading="credDeleteLoading" @click="handleDeleteCred">
          {{ t('common.delete') }}
        </CButton>
      </template>
    </CModal>

  </div>
</template>
