<script setup>
import { ref, computed, onMounted } from 'vue'
import apiClient from '@/services/apiClient'
import { useUiStore } from '@/stores/ui'
import Card from '@/components/ui/Card.vue'
import Button from '@/components/ui/Button.vue'
import Input from '@/components/ui/Input.vue'
import Label from '@/components/ui/Label.vue'
import Dialog from '@/components/ui/Dialog.vue'
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

async function deleteLicense(id) {
  try { await apiClient.deleteLicense(id); load(); ui.pushToast({ title: 'Berhasil', description: 'Lisensi dihapus.', variant: 'success' }) }
  catch (err) { ui.pushToast({ title: 'Gagal', description: err.data?.error || 'Error.', variant: 'destructive' }) }
}

const paged = computed(() => { const s = (page.value - 1) * pageSize; return data.value.slice(s, s + pageSize) })
</script>
<template>
  <div class="space-y-4">
    <div class="flex items-center justify-between"><h1 class="text-lg font-bold">Lisensi Software</h1><Button size="sm" @click="openCreate">+ Lisensi</Button></div>
    <Card class="p-4">
      <TableSkeleton v-if="loading" :cols="5" :rows="4" />
      <EmptyState v-else-if="!data.length" title="Belum ada lisensi" />
      <div v-else class="overflow-x-auto">
        <table class="w-full text-xs"><thead><tr class="border-b text-left"><th class="py-2 px-2 font-medium text-muted-foreground">Nama</th><th class="py-2 px-2 font-medium text-muted-foreground">Product Key</th><th class="py-2 px-2 font-medium text-muted-foreground">Seats</th><th class="py-2 px-2 font-medium text-muted-foreground">Kadaluarsa</th><th class="py-2 px-2 font-medium text-muted-foreground w-24">Aksi</th></tr></thead>
        <tbody><tr v-for="l in paged" :key="l.id" class="border-b hover:bg-muted/50"><td class="py-1.5 px-2 font-medium">{{ l.name }}</td><td class="py-1.5 px-2 font-mono text-[11px]">{{ l.product_key || '-' }}</td><td class="py-1.5 px-2">{{ l.seats }}</td><td class="py-1.5 px-2">{{ l.expiration_date || '-' }}</td><td class="py-1.5 px-2"><div class="flex gap-1"><Button variant="ghost" size="xs" @click="openEdit(l)">Edit</Button><Button variant="ghost" size="xs" class="text-destructive" @click="deleteLicense(l.id)">Hapus</Button></div></td></tr></tbody></table>
      </div>
      <Pagination v-if="data.length > pageSize" :model-value="page" :total="data.length" :per-page="pageSize" class="mt-3" @update:model-value="page = $event" />
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
  </div>
</template>
