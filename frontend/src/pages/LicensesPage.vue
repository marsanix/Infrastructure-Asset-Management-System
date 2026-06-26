<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import apiClient from '@/services/apiClient'
import { useUiStore } from '@/stores/ui'
import Card from '@/components/ui/Card.vue'
import Button from '@/components/ui/Button.vue'
import Input from '@/components/ui/Input.vue'
import Label from '@/components/ui/Label.vue'
import Dialog from '@/components/ui/Dialog.vue'
import ConfirmDialog from '@/components/ui/ConfirmDialog.vue'
import Pagination from '@/components/ui/Pagination.vue'
import EmptyState from '@/components/ui/EmptyState.vue'
import TableSkeleton from '@/components/ui/TableSkeleton.vue'

const ui = useUiStore()
const data = ref([])
const loading = ref(true)
const formOpen = ref(false)
const formItem = ref(null)
const form = ref({ name: '', product_key: '', seats: 1, licensed_to_email: '', purchase_date: '', expiration_date: '', notes: '' })
const formLoading = ref(false)
const isEdit = computed(() => !!formItem.value)
const page = ref(1)
const pageSize = 10

// Item 5: client-side search
const query = ref('')

// Item 2 & 3: product key masking + per-row reveal toggle
const revealed = ref(new Set())
function toggleReveal(id) {
  const next = new Set(revealed.value)
  next.has(id) ? next.delete(id) : next.add(id)
  revealed.value = next
}
function maskKey(key) {
  return key ? '••••-••••-••••-••••' : '-'
}

// Item 4: delete confirmation dialog state
const confirmDeleteOpen = ref(false)
const pendingDelete = ref(null)
const deleting = ref(false)

async function load() {
  loading.value = true
  try { const r = await apiClient.listLicenses(); data.value = r.data?.data || r.data || [] }
  catch (_) { data.value = [] }
  finally { loading.value = false }
}
onMounted(load)

function openCreate() { formItem.value = null; form.value = { name: '', product_key: '', seats: 1, licensed_to_email: '', purchase_date: '', expiration_date: '', notes: '' }; formOpen.value = true }
function openEdit(item) { formItem.value = item; form.value = { name: item.name, product_key: item.product_key || '', seats: item.seats, licensed_to_email: item.licensed_to_email || '', purchase_date: item.purchase_date || '', expiration_date: item.expiration_date || '', notes: item.notes || '' }; formOpen.value = true }

async function submit() {
  formLoading.value = true
  try {
    const p = { ...form.value, seats: Number(form.value.seats) }
    if (isEdit.value) await apiClient.updateLicense(formItem.value.id, p)
    else await apiClient.createLicense(p)
    formOpen.value = false; load()
    ui.pushToast({ title: 'Berhasil', description: isEdit.value ? 'Lisensi diperbarui.' : 'Lisensi ditambahkan.', variant: 'success' })
  } catch (err) { ui.pushToast({ title: 'Gagal', description: err.data?.error || 'Error.', variant: 'destructive' }) }
  finally { formLoading.value = false }
}

// Item 4: open confirmation instead of deleting directly
function askDelete(item) { pendingDelete.value = item; confirmDeleteOpen.value = true }

async function confirmDelete() {
  deleting.value = true
  try {
    await apiClient.deleteLicense(pendingDelete.value.id)
    ui.pushToast({ title: 'Berhasil', description: 'Lisensi dihapus.', variant: 'success' })
    await load()
  } catch (err) {
    ui.pushToast({ title: 'Gagal', description: err.data?.error || 'Error.', variant: 'destructive' })
  } finally {
    deleting.value = false
    confirmDeleteOpen.value = false
    pendingDelete.value = null
  }
}

// Item 5: filter by name + licensed email (product key excluded to avoid leaking masked data)
const filtered = computed(() => {
  const q = query.value.trim().toLowerCase()
  if (!q) return data.value
  return data.value.filter((l) =>
    (l.name || '').toLowerCase().includes(q) || (l.licensed_to_email || '').toLowerCase().includes(q),
  )
})

// Reset to first page when search changes
watch(query, () => { page.value = 1 })

const paged = computed(() => { const s = (page.value - 1) * pageSize; return filtered.value.slice(s, s + pageSize) })
</script>
<template>
  <div class="space-y-4">
    <div class="flex items-center justify-between"><h1 class="text-lg font-bold">Lisensi Software</h1><Button size="sm" @click="openCreate">+ Lisensi</Button></div>

    <!-- Item 5: search input -->
    <Card class="p-4">
      <Label for="lic-search" class="text-xs mb-1">Pencarian</Label>
      <div class="relative max-w-md">
        <svg class="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>
        <Input id="lic-search" v-model="query" placeholder="Cari nama atau email lisensi..." class="pl-9" data-testid="licenses-search-input" />
      </div>
    </Card>

    <Card class="p-4">
      <TableSkeleton v-if="loading" :cols="5" :rows="4" />
      <EmptyState v-else-if="!filtered.length" title="Belum ada lisensi" />
      <div v-else class="overflow-x-auto">
        <table class="w-full text-xs"><thead><tr class="border-b text-left"><th class="py-2 px-2 font-medium text-muted-foreground">Nama</th><th class="py-2 px-2 font-medium text-muted-foreground">Product Key</th><th class="py-2 px-2 font-medium text-muted-foreground">Seats</th><th class="py-2 px-2 font-medium text-muted-foreground">Kadaluarsa</th><th class="py-2 px-2 font-medium text-muted-foreground w-24">Aksi</th></tr></thead>
        <tbody><tr v-for="l in paged" :key="l.id" class="border-b hover:bg-muted/50"><td class="py-1.5 px-2 font-medium">{{ l.name }}</td>
          <!-- Item 2 & 3: masked product key with reveal toggle -->
          <td class="py-1.5 px-2 font-mono text-[11px]">
            <div class="flex items-center gap-1.5">
              <span>{{ revealed.has(l.id) ? (l.product_key || '-') : maskKey(l.product_key) }}</span>
              <button v-if="l.product_key" type="button" class="text-muted-foreground hover:text-foreground" :title="revealed.has(l.id) ? 'Sembunyikan' : 'Tampilkan'" :aria-label="revealed.has(l.id) ? 'Sembunyikan product key' : 'Tampilkan product key'" :data-testid="`license-reveal-${l.id}`" @click="toggleReveal(l.id)">
                <svg v-if="!revealed.has(l.id)" class="h-3.5 w-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z"/><circle cx="12" cy="12" r="3"/></svg>
                <svg v-else class="h-3.5 w-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9.88 9.88a3 3 0 1 0 4.24 4.24"/><path d="M10.73 5.08A10.43 10.43 0 0 1 12 5c7 0 10 7 10 7a13.16 13.16 0 0 1-1.67 2.68"/><path d="M6.61 6.61A13.526 13.526 0 0 0 2 12s3 7 10 7a9.74 9.74 0 0 0 5.39-1.61"/><line x1="2" x2="22" y1="2" y2="22"/></svg>
              </button>
            </div>
          </td>
          <td class="py-1.5 px-2">{{ l.seats }}</td><td class="py-1.5 px-2">{{ l.expiration_date || '-' }}</td><td class="py-1.5 px-2"><div class="flex gap-1"><Button variant="ghost" size="xs" @click="openEdit(l)">Edit</Button><Button variant="ghost" size="xs" class="text-destructive" :data-testid="`license-delete-${l.id}`" @click="askDelete(l)">Hapus</Button></div></td></tr></tbody></table>
      </div>
      <Pagination v-if="filtered.length > pageSize" :model-value="page" :total="filtered.length" :per-page="pageSize" class="mt-3" @update:model-value="page = $event" />
    </Card>

    <Dialog :model-value="formOpen" :title="isEdit ? 'Edit Lisensi' : 'Tambah Lisensi'" compact @update:model-value="formOpen=$event">
      <div class="grid gap-2 text-[13px]">
        <div><Label class="text-xs mb-0.5">Nama *</Label><Input v-model="form.name" placeholder="Microsoft 365" class="h-8 text-[13px] px-2.5" /></div>
        <div><Label class="text-xs mb-0.5">Product Key</Label><Input v-model="form.product_key" placeholder="XXXX-XXXX-XXXX" class="h-8 text-[13px] px-2.5" /></div>
        <div><Label class="text-xs mb-0.5">Seats</Label><Input v-model="form.seats" type="number" min="1" class="h-8 text-[13px] px-2.5" /></div>
        <div><Label class="text-xs mb-0.5">Email Lisensi</Label><Input v-model="form.licensed_to_email" placeholder="email@domain.com" class="h-8 text-[13px] px-2.5" /></div>
        <div class="grid grid-cols-2 gap-2"><div><Label class="text-xs mb-0.5">Pembelian</Label><Input v-model="form.purchase_date" type="date" class="h-8 text-[13px] px-2.5" /></div><div><Label class="text-xs mb-0.5">Kadaluarsa</Label><Input v-model="form.expiration_date" type="date" class="h-8 text-[13px] px-2.5" /></div></div>
      </div>
      <template #footer><Button variant="ghost" size="sm" @click="formOpen=false">Batal</Button><Button size="sm" :loading="formLoading" :disabled="!form.name.trim()" @click="submit">{{ isEdit ? 'Perbarui' : 'Simpan' }}</Button></template>
    </Dialog>

    <!-- Item 4: delete confirmation dialog -->
    <ConfirmDialog
      v-model="confirmDeleteOpen"
      title="Hapus lisensi?"
      :description="`Lisensi ${pendingDelete?.name || ''} akan dihapus permanen. Tindakan ini tidak dapat dibatalkan.`"
      confirm-text="Hapus"
      :loading="deleting"
      variant="destructive"
      @confirm="confirmDelete"
    />
  </div>
</template>
