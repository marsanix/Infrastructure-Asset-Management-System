<script setup>
import { ref, watch, computed } from 'vue'
import apiClient from '@/services/apiClient'
import { useUiStore } from '@/stores/ui'
import { useI18n } from 'vue-i18n'
import Dialog from '@/components/ui/Dialog.vue'
import Button from '@/components/ui/Button.vue'
import Input from '@/components/ui/Input.vue'
import Label from '@/components/ui/Label.vue'
import Select from '@/components/ui/Select.vue'
import Badge from '@/components/ui/Badge.vue'
import Barcode from '@/components/ui/Barcode.vue'
import { formatDate } from '@/lib/utils'

const { t } = useI18n()
const props = defineProps({
  modelValue: { type: Boolean, default: false },
  asset: { type: Object, default: null },
  locations: { type: Array, default: () => [] },
  models: { type: Array, default: () => [] },
  users: { type: Array, default: () => [] },
})
const emit = defineEmits(['update:modelValue', 'saved'])

const ui = useUiStore()
const isCreate = computed(() => !props.asset)
const loading = ref(false)

const form = ref({
  asset_tag: '',
  serial_number: '',
  po_number: '',
  model_id: '',
  location_id: '',
  user_id: '',
  status: 'Available',
  purchase_date: '',
  warranty_months: '',
  os_license: '',
  ip_address: '',
  mac_address: '',
  hostname: '',
  vlan: '',
  credential: '',
})

watch(() => props.modelValue, (open) => {
  if (!open) return
  fetchStatusLabels()
  if (props.asset) {
    form.value = {
      asset_tag: props.asset.asset_tag || '',
      serial_number: props.asset.serial_number || '',
      po_number: props.asset.po_number || '',
      model_id: props.asset.model_id || '',
      location_id: props.asset.location_id || '',
      user_id: props.asset.user_id || '',
      status: props.asset.status || 'Active',
      purchase_date: props.asset.purchase_date || '',
      warranty_months: props.asset.warranty_months || '',
      os_license: props.asset.os_license || '',
      ip_address: props.asset.ip_address || '',
      mac_address: props.asset.mac_address || '',
      hostname: props.asset.hostname || '',
      vlan: props.asset.vlan || '',
      credential: '',
    }
    fetchCredentials()
    fetchFiles()
    fetchHistory()
  } else {
    form.value = {
      asset_tag: '', serial_number: '', po_number: '', model_id: '', location_id: '', user_id: '',
      status: 'Available', purchase_date: '', warranty_months: '', os_license: '',
      ip_address: '', mac_address: '', hostname: '', vlan: '', credential: '',
    }
    credentials.value = []
  }
})

const statusOpts = ref([
  { label: 'Active', value: 'Active' },
  { label: 'Available', value: 'Available' },
  { label: 'Repair', value: 'Repair' },
  { label: 'Disposed', value: 'Disposed' },
])

async function fetchStatusLabels() {
  try {
    const res = await apiClient.listStatusLabels()
    const custom = (res.data?.data || res.data || []).map(s => ({ label: s.name, value: s.name }))
    statusOpts.value = [
      { label: 'Active', value: 'Active' },
      { label: 'Available', value: 'Available' },
      { label: 'Repair', value: 'Repair' },
      { label: 'Disposed', value: 'Disposed' },
      ...custom,
    ]
  } catch (_) {}
}
const locationOpts = computed(() => props.locations.map((l) => ({ label: l.name, value: String(l.id) })))
const modelOpts = computed(() => props.models.map((m) => ({ label: `${m.brand_name} ${m.name}`, value: String(m.id) })))
const userOpts = computed(() => [{ label: 'IT Inventory / Server', value: '' }, ...props.users.map((u) => ({ label: u.name, value: String(u.id) }))])

const credentials = ref([])
const credForm = ref({ credential_type: 'SSH', username: '', password: '', notes: '' })
const credReveal = ref({})
const editingCredId = ref(null)
const files = ref([])
const fileInput = ref(null)
const uploading = ref(false)
const credTypeOpts = ['SSH', 'Web Console', 'SNMP', 'Telnet', 'RDP', 'API Key', 'Other'].map(s => ({ label: s, value: s }))

async function fetchCredentials() {
  if (!props.asset?.id) return
  try {
    const res = await apiClient.listCredentials(props.asset.id)
    credentials.value = Array.isArray(res.data) ? res.data : (res.data?.data || [])
  }
  catch (_) { credentials.value = [] }
}

async function addOrUpdateCredential() {
  if (!props.asset?.id) return
  try {
    if (editingCredId.value) {
      const payload = { credential_type: credForm.value.credential_type, username: credForm.value.username || undefined, notes: credForm.value.notes || undefined }
      if (credForm.value.password.trim()) payload.password = credForm.value.password.trim()
      await apiClient.updateCredential(props.asset.id, editingCredId.value, payload)
      ui.pushToast({ title: t('common.success'), description: 'Kredensial diperbarui.', variant: 'success' })
    } else {
      if (!credForm.value.password.trim()) return
      await apiClient.createCredential(props.asset.id, credForm.value)
      ui.pushToast({ title: t('common.success'), description: 'Kredensial ditambahkan.', variant: 'success' })
    }
    credForm.value = { credential_type: 'SSH', username: '', password: '', notes: '' }
    editingCredId.value = null
    fetchCredentials()
  } catch (err) { ui.pushToast({ title: t('common.failed'), description: err.data?.error || t('toast.failed'), variant: 'destructive' }) }
}

function editCredential(cred) {
  credForm.value = { credential_type: cred.credential_type, username: cred.username || '', password: '', notes: cred.notes || '' }
  editingCredId.value = cred.id
}

function cancelEdit() {
  credForm.value = { credential_type: 'SSH', username: '', password: '', notes: '' }
  editingCredId.value = null
}

async function fetchFiles() {
  if (!props.asset?.id) return
  try { const r = await apiClient.listAssetFiles(props.asset.id); files.value = r.data?.data || r.data || [] }
  catch (_) { files.value = [] }
}

async function uploadFile(e) {
  const file = e.target.files?.[0]
  if (!file || !props.asset?.id) return
  uploading.value = true
  try {
    await apiClient.uploadAssetFile(props.asset.id, file)
    fetchFiles()
  } catch (err) { ui.pushToast({ title: t('common.failed'), description: err.data?.error || 'Upload gagal.', variant: 'destructive' }) }
  finally { uploading.value = false }
}

async function deleteFile(fileId) {
  try {
    await apiClient.deleteAssetFile(props.asset.id, fileId)
    files.value = files.value.filter(f => f.id !== fileId)
  } catch (err) { ui.pushToast({ title: t('common.failed'), description: err.data?.error || t('toast.failed'), variant: 'destructive' }) }
}

async function revealCredential(credId) {
  try {
    const r = await apiClient.revealCredential(props.asset.id, credId)
    const pwd = r.data?.password || r.data?.data?.password || '***'
    credReveal.value[credId] = pwd
    ui.pushToast({ title: t('common.success'), description: 'Password ditampilkan (tercatat di audit log).', variant: 'info' })
    setTimeout(() => { delete credReveal.value[credId] }, 5000)
  } catch (err) { ui.pushToast({ title: t('common.failed'), description: err.data?.error || t('toast.failed'), variant: 'destructive' }) }
}

async function deleteCredential(credId) {
  try {
    await apiClient.deleteCredential(props.asset.id, credId)
    ui.pushToast({ title: t('common.success'), description: 'Kredensial dihapus.', variant: 'success' })
    fetchCredentials()
  } catch (err) { ui.pushToast({ title: t('common.failed'), description: err.data?.error || t('toast.failed'), variant: 'destructive' }) }
}

const checkoutOpen = ref(false)
const checkoutForm = ref({ user_id: '', expected_return_date: '', notes: '' })
const checkoutLoading = ref(false)
const history = ref([])
const historyOpen = ref(false)

async function fetchHistory() {
  if (!props.asset?.id) return
  try { const r = await apiClient.assetHistory(props.asset.id); history.value = r.data?.data || r.data || [] }
  catch (_) { history.value = [] }
}

async function doCheckout() {
  if (!props.asset?.id || !checkoutForm.value.user_id) return
  checkoutLoading.value = true
  try {
    await apiClient.checkoutAsset(props.asset.id, {
      user_id: Number(checkoutForm.value.user_id),
      expected_return_date: checkoutForm.value.expected_return_date || undefined,
      notes: checkoutForm.value.notes.trim() || undefined,
    })
    ui.pushToast({ title: t('common.success'), description: t('checkout.checkoutSuccess'), variant: 'success' })
    checkoutOpen.value = false
    checkoutForm.value = { user_id: '', expected_return_date: '', notes: '' }
    fetchHistory()
    emit('saved')
  } catch (err) {
    ui.pushToast({ title: t('common.failed'), description: err.data?.error || t('toast.failed'), variant: 'destructive' })
  } finally {
    checkoutLoading.value = false
  }
}

async function doCheckin() {
  if (!props.asset?.id) return
  checkoutLoading.value = true
  try {
    await apiClient.checkinAsset(props.asset.id, { notes: checkoutForm.value.notes.trim() || undefined })
    ui.pushToast({ title: t('common.success'), description: t('checkout.checkinSuccess'), variant: 'success' })
    checkoutForm.value = { user_id: '', expected_return_date: '', notes: '' }
    fetchHistory()
    emit('saved')
  } catch (err) {
    ui.pushToast({ title: t('common.failed'), description: err.data?.error || t('toast.failed'), variant: 'destructive' })
  } finally {
    checkoutLoading.value = false
  }
}

async function submit() {
  const payload = {
    asset_tag: form.value.asset_tag.trim(),
    serial_number: form.value.serial_number.trim() || undefined,
    po_number: form.value.po_number.trim() || undefined,
    model_id: form.value.model_id ? Number(form.value.model_id) : undefined,
    location_id: form.value.location_id ? Number(form.value.location_id) : undefined,
    user_id: form.value.user_id ? Number(form.value.user_id) : undefined,
    status: form.value.status,
    purchase_date: form.value.purchase_date || undefined,
    warranty_months: form.value.warranty_months ? Number(form.value.warranty_months) : undefined,
    os_license: form.value.os_license.trim() || undefined,
  }

  const network = {}
  if (form.value.ip_address.trim()) network.ip_address = form.value.ip_address.trim()
  if (form.value.mac_address.trim()) network.mac_address = form.value.mac_address.trim()
  if (form.value.hostname.trim()) network.hostname = form.value.hostname.trim()
  if (form.value.vlan.trim()) network.vlan = form.value.vlan.trim()
  if (Object.keys(network).length) payload.network_detail = network

  const credential = form.value.credential.trim()

  loading.value = true
  try {
    let assetId = props.asset?.id
    if (isCreate.value) {
      const created = await apiClient.createAsset(payload)
      assetId = created.data?.id
    } else {
      await apiClient.updateAsset(assetId, payload)
    }

    if (credential && assetId) {
      await apiClient.updateCredential(assetId, { credential })
    }

    ui.pushToast({ title: t('common.success'), description: isCreate.value ? `Aset ${t('toast.created')}.` : `Aset ${t('toast.updated')}.`, variant: 'success' })
    emit('saved')
    emit('update:modelValue', false)
  } catch (err) {
    ui.pushToast({ title: t('common.failed'), description: err.data?.error || t('toast.failed'), variant: 'destructive' })
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <Dialog
    :model-value="modelValue"
    :title="isCreate ? 'Tambah Aset' : 'Edit Aset'"
    :description="isCreate ? 'Isi informasi aset baru.' : `Perbarui data ${asset?.asset_tag}.`"
    size="lg"
    compact
    @update:model-value="$emit('update:modelValue', $event)"
  >
    <!-- Barcode display (edit only) -->
    <div v-if="!isCreate && asset?.asset_tag" class="flex justify-center mb-3 p-2 bg-white rounded-md border">
      <Barcode :value="asset.asset_tag" :size="180" class="text-black" />
    </div>
    <div class="mb-3 rounded-lg border border-primary/20 bg-primary/5 px-3 py-2 text-xs text-muted-foreground">
      <span class="font-medium text-foreground">Data wajib:</span> Asset Tag, Serial Number, Model, dan Lokasi. Detail jaringan, file, dan kredensial bisa dilengkapi setelah aset tersimpan.
    </div>
    <div class="grid grid-cols-1 sm:grid-cols-2 gap-2 text-[13px]">
      <div>
        <Label for="af-tag" class="mb-0.5 text-xs">Asset Tag *</Label>
        <Input id="af-tag" v-model="form.asset_tag" placeholder="AST-..." class="h-8 text-[13px] px-2.5" />
      </div>
      <div>
        <Label for="af-serial" class="mb-0.5 text-xs">Serial Number *</Label>
        <Input id="af-serial" v-model="form.serial_number" placeholder="SN..." class="h-8 text-[13px] px-2.5" />
      </div>
      <div>
        <Label for="af-model" class="mb-0.5 text-xs">Model *</Label>
        <Select id="af-model" v-model="form.model_id" :options="modelOpts" placeholder="Pilih model" class="h-8 text-[13px] px-2.5" />
      </div>
      <div>
        <Label for="af-location" class="mb-0.5 text-xs">Lokasi *</Label>
        <Select id="af-location" v-model="form.location_id" :options="locationOpts" placeholder="Pilih lokasi" class="h-8 text-[13px] px-2.5" />
      </div>
      <div>
        <Label for="af-po" class="mb-0.5 text-xs">PO Number</Label>
        <Input id="af-po" v-model="form.po_number" placeholder="PO/..." class="h-8 text-[13px] px-2.5" />
      </div>
      <div>
        <Label for="af-status" class="mb-0.5 text-xs">Status</Label>
        <Select id="af-status" v-model="form.status" :options="statusOpts" placeholder="Pilih status" class="h-8 text-[13px] px-2.5" />
      </div>
      <div>
        <Label for="af-user" class="mb-0.5 text-xs">Pengguna</Label>
        <Select id="af-user" v-model="form.user_id" :options="userOpts" placeholder="Pilih pengguna" class="h-8 text-[13px] px-2.5" />
      </div>
      <div>
        <Label for="af-purchase" class="mb-0.5 text-xs">Tanggal Pembelian</Label>
        <Input id="af-purchase" v-model="form.purchase_date" type="date" class="h-8 text-[13px] px-2.5" />
      </div>
      <div>
        <Label for="af-warranty" class="mb-0.5 text-xs">Garansi (bulan)</Label>
        <Input id="af-warranty" v-model="form.warranty_months" type="number" min="0" placeholder="36" class="h-8 text-[13px] px-2.5" />
      </div>
      <div>
        <Label for="af-os" class="mb-0.5 text-xs">OS/License</Label>
        <Input id="af-os" v-model="form.os_license" placeholder="-" class="h-8 text-[13px] px-2.5" />
      </div>

      <div class="sm:col-span-2 border-t border-border pt-2 mt-0.5">
        <p class="text-[11px] font-semibold uppercase tracking-wider text-muted-foreground mb-1.5">Detail Jaringan <span class="font-normal normal-case tracking-normal">(opsional)</span></p>
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-2">
          <div>
            <Label for="af-ip" class="mb-0.5 text-xs">IP Address</Label>
            <Input id="af-ip" v-model="form.ip_address" placeholder="10.x.x.x" class="h-8 text-[13px] px-2.5" />
          </div>
          <div>
            <Label for="af-mac" class="mb-0.5 text-xs">MAC Address</Label>
            <Input id="af-mac" v-model="form.mac_address" placeholder="00:00:00:00:00:00" class="h-8 text-[13px] px-2.5" />
          </div>
          <div>
            <Label for="af-hostname" class="mb-0.5 text-xs">Hostname</Label>
            <Input id="af-hostname" v-model="form.hostname" placeholder="hostname" class="h-8 text-[13px] px-2.5" />
          </div>
          <div>
            <Label for="af-vlan" class="mb-0.5 text-xs">VLAN</Label>
            <Input id="af-vlan" v-model="form.vlan" placeholder="VLAN" class="h-8 text-[13px] px-2.5" />
          </div>
        </div>
      </div>
    </div>

    <!-- Edit-only sections in scrollable body -->
    <template v-if="!isCreate">

      <!-- Credentials -->
      <div class="border-t border-border pt-3 mt-3">
        <div class="mb-2 flex items-center justify-between gap-2">
          <p class="text-[12px] font-semibold uppercase tracking-wider text-muted-foreground">Kredensial Perangkat</p>
          <Badge variant="muted" class="text-[10px]">Terenkripsi</Badge>
        </div>
        <div v-if="credentials.length" class="space-y-1 mb-2">
          <div v-for="cred in credentials" :key="cred.id" :class="['flex flex-wrap items-center gap-1.5 rounded-md border px-2 py-1 transition-colors', editingCredId === cred.id ? 'border-primary bg-primary/5' : 'border-border bg-muted/30']">
            <span class="text-[11px] font-medium min-w-[60px]">{{ cred.credential_type }}</span>
            <span class="text-[11px] text-muted-foreground min-w-[40px]">{{ cred.username || '-' }}</span>
            <span class="text-[11px] font-mono text-muted-foreground">••••••••</span>
            <input v-if="credReveal[cred.id]" :value="credReveal[cred.id]" readonly class="text-[11px] font-mono bg-transparent w-20" />
            <span class="flex-1 min-w-[20px]"></span>
            <div class="flex items-center gap-0.5 ml-auto">
              <Button variant="ghost" size="xs" class="h-6 w-6 p-0" @click="revealCredential(cred.id)" title="Lihat">👁</Button>
              <Button variant="ghost" size="xs" class="h-6 w-6 p-0" @click="editCredential(cred)" title="Edit">✎</Button>
              <Button variant="ghost" size="xs" class="h-6 w-6 p-0 text-destructive" @click="deleteCredential(cred.id)" title="Hapus">✕</Button>
            </div>
          </div>
        </div>
        <div class="grid grid-cols-1 sm:grid-cols-4 gap-1.5">
          <Select v-model="credForm.credential_type" :options="credTypeOpts" class="h-8 text-[12px] px-1.5" />
          <Input v-model="credForm.username" placeholder="Username" class="h-8 text-[12px] px-1.5" />
          <Input v-model="credForm.password" type="password" placeholder="Password" autocomplete="off" class="h-8 text-[12px] px-1.5" />
          <div class="flex gap-1">
            <Button size="xs" class="h-8 text-[11px] flex-1" :disabled="!editingCredId && !credForm.password.trim()" @click="addOrUpdateCredential">{{ editingCredId ? 'Update' : '+ Tambah' }}</Button>
            <Button v-if="editingCredId" variant="ghost" size="xs" class="h-8 text-[11px]" @click="cancelEdit">Batal</Button>
          </div>
        </div>
      </div>

      <!-- File Upload -->
      <div class="border-t border-border pt-3 mt-3">
        <p class="text-[12px] font-semibold uppercase tracking-wider text-muted-foreground mb-1.5">File Upload</p>
        <p class="mb-1.5 text-[11px] text-muted-foreground">Maksimal 10 MB per file. Simpan dokumen penting saja.</p>
        <div class="flex items-center gap-2">
          <input ref="fileInput" type="file" class="text-[12px] flex-1 min-w-0" @change="uploadFile" />
          <span v-if="uploading" class="text-[11px] text-muted-foreground whitespace-nowrap">Uploading...</span>
        </div>
        <div v-if="files.length" class="space-y-0.5 mt-1.5">
          <div v-for="f in files" :key="f.id" class="flex items-center gap-2 text-[11px] bg-muted/30 rounded px-2 py-1">
            <span class="flex-1 truncate">{{ f.original_name }}</span>
            <a :href="'/api/assets/'+asset?.id+'/files/'+f.id" target="_blank" class="text-primary hover:underline shrink-0">Unduh</a>
            <Button variant="ghost" size="xs" class="h-5 w-5 p-0 shrink-0 text-destructive" @click="deleteFile(f.id)">✕</Button>
          </div>
        </div>
      </div>

      <!-- Checkout / Checkin -->
      <div v-if="asset?.id" class="border-t border-border pt-3 mt-3">
        <button class="flex items-center gap-1 text-[12px] font-semibold uppercase tracking-wider text-muted-foreground hover:text-foreground transition-colors w-full text-left" @click="checkoutOpen = !checkoutOpen; if (checkoutOpen) { fetchHistory() }">
          {{ t('checkout.checkout') }} / {{ t('checkout.checkin') }}
          <svg class="h-3.5 w-3.5 transition-transform shrink-0" :class="checkoutOpen ? 'rotate-180' : ''" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="m6 9 6 6 6-6"/></svg>
        </button>
        <template v-if="checkoutOpen">
          <div class="mt-2 space-y-2">
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-2">
              <div>
                <Label class="mb-0.5 text-[11px]">{{ t('checkout.selectUser') }}</Label>
                <Select v-model="checkoutForm.user_id" :options="userOpts" :placeholder="t('checkout.selectUser')" class="h-8 text-[12px] px-1.5" />
              </div>
              <div>
                <Label class="mb-0.5 text-[11px]">{{ t('checkout.expectedReturn') }}</Label>
                <Input v-model="checkoutForm.expected_return_date" type="date" class="h-8 text-[12px] px-1.5" />
              </div>
            </div>
            <Input v-model="checkoutForm.notes" :placeholder="t('checkout.notes')" class="h-8 text-[12px] px-1.5" />
            <div class="flex gap-1.5">
              <Button size="sm" class="h-8 text-[12px]" :loading="checkoutLoading" :disabled="!checkoutForm.user_id" @click="doCheckout">{{ t('checkout.checkoutAsset') }}</Button>
              <Button size="sm" variant="ghost" class="h-8 text-[12px] text-destructive" :loading="checkoutLoading" @click="doCheckin">{{ t('checkout.checkinAsset') }}</Button>
            </div>
          </div>

          <div v-if="history.length" class="mt-2 space-y-1 max-h-32 overflow-y-auto">
            <p class="text-[11px] font-semibold text-muted-foreground">{{ t('checkout.history') }}</p>
            <div v-for="h in history" :key="h.id" class="flex flex-wrap items-center gap-1.5 text-[11px] bg-muted/30 rounded px-2 py-1">
              <Badge :variant="h.action === 'checkout' ? 'warning' : 'success'" class="text-[10px] !px-1 !py-0 shrink-0">{{ h.action }}</Badge>
              <span v-if="h.user_name" class="text-foreground/80">{{ h.user_name }}</span>
              <span v-if="h.expected_return_date" class="text-muted-foreground ml-auto">{{ h.expected_return_date }}</span>
              <span class="text-muted-foreground">{{ formatDate(h.created_at) }}</span>
            </div>
          </div>
          <p v-else class="text-[11px] text-muted-foreground mt-1.5">{{ t('checkout.noHistory') }}</p>
        </template>
      </div>
    </template>

    <template #footer>
      <Button variant="ghost" size="sm" @click="$emit('update:modelValue', false)">Batal</Button>
      <Button size="sm" :loading="loading" :disabled="!form.asset_tag || !form.serial_number || !form.model_id || !form.location_id" @click="submit">
        {{ isCreate ? 'Simpan Aset' : 'Perbarui' }}
      </Button>
    </template>
  </Dialog>
</template>
