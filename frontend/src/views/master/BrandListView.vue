<script setup lang="ts">
import { ref } from 'vue'
import { z } from 'zod'
import { useCrud } from '@/composables/useCrud'
import { useForm } from '@/composables/useForm'
import MasterListView  from '@/components/master/MasterListView.vue'
import MasterFormModal from '@/components/master/MasterFormModal.vue'
import CInput from '@/components/ui/CInput.vue'

interface Brand { id: number; name: string; is_active: boolean }

const Schema = z.object({
  name:      z.string().min(1, 'Name is required').max(50).regex(/^[\w\s\-\.]+$/, 'Invalid characters'),
  is_active: z.boolean().default(true),
})
type Form = z.infer<typeof Schema>

const crud       = useCrud<Brand>('/brands')
const modal      = ref(false)
const editTarget = ref<Brand | null>(null)
const listRef    = ref<InstanceType<typeof MasterListView> | null>(null)

const { values, errors, submitting, setField, handleSubmit, reset } = useForm<Form>(Schema, { is_active: true })

const columns = [
  { key: 'name',      label: 'Brand Name' },
  { key: 'is_active', label: 'Status', width: '100px' },
]

function openCreate() { editTarget.value = null; reset({ is_active: true }); modal.value = true }
function openEdit(item: Brand) {
  editTarget.value = item
  reset({ name: item.name, is_active: item.is_active })
  modal.value = true
}
async function onSubmit(data: Form) {
  const ok = editTarget.value
    ? await crud.update(editTarget.value.id, data)
    : await crud.create(data)
  if (ok) { modal.value = false; listRef.value?.load() }
}
</script>

<template>
  <MasterListView ref="listRef" title="Brands" endpoint="/brands"
    permission-module="brand" :columns="columns"
    :on-create-click="openCreate" :on-edit-click="openEdit" />

  <MasterFormModal :open="modal" :title="editTarget ? 'Edit Brand' : 'Create Brand'"
    :submitting="submitting || crud.loading.value"
    @close="modal = false" @submit="handleSubmit(onSubmit)">
    <CInput :model-value="values.name || ''" label="Brand Name" required :error="errors.name"
      autocomplete="off" @update:model-value="setField('name', $event as string)" />
  </MasterFormModal>
</template>
