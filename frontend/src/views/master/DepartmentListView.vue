<script setup lang="ts">
import { ref } from 'vue'
import { z } from 'zod'
import { useCrud } from '@/composables/useCrud'
import { useForm } from '@/composables/useForm'
import MasterListView from '@/components/master/MasterListView.vue'
import MasterFormModal from '@/components/master/MasterFormModal.vue'
import CInput from '@/components/ui/CInput.vue'

interface Department { id: number; name: string; description: string | null; is_active: boolean }

const DeptSchema = z.object({
  name:        z.string().min(1, 'Name is required').max(100).regex(/^[\w\s\-\.]+$/, 'Invalid characters'),
  description: z.string().max(500).optional(),
  is_active:   z.boolean().default(true),
})
type DeptForm = z.infer<typeof DeptSchema>

const crud      = useCrud<Department>('/departments')
const modal     = ref(false)
const editTarget = ref<Department | null>(null)
const listRef   = ref<InstanceType<typeof MasterListView> | null>(null)

const { values, errors, submitting, setField, handleSubmit, reset } = useForm<DeptForm>(
  DeptSchema, { is_active: true }
)

const columns = [
  { key: 'name',        label: 'Name' },
  { key: 'description', label: 'Description' },
  { key: 'is_active',   label: 'Status', width: '100px' },
]

function openCreate() {
  editTarget.value = null
  reset({ is_active: true })
  modal.value = true
}

function openEdit(item: Department) {
  editTarget.value = item
  reset({ name: item.name, description: item.description ?? '', is_active: item.is_active })
  modal.value = true
}

async function onSubmit(data: DeptForm) {
  let ok
  if (editTarget.value) {
    ok = await crud.update(editTarget.value.id, data)
  } else {
    ok = await crud.create(data)
  }
  if (ok) {
    modal.value = false
    listRef.value?.load()
  }
}
</script>

<template>
  <MasterListView
    ref="listRef"
    title="Departments"
    endpoint="/departments"
    permission-module="department"
    :columns="columns"
    :on-create-click="openCreate"
    :on-edit-click="openEdit"
  />

  <MasterFormModal
    :open="modal"
    :title="editTarget ? 'Edit Department' : 'Create Department'"
    :submitting="submitting || crud.loading.value"
    @close="modal = false"
    @submit="handleSubmit(onSubmit)"
  >
    <CInput
      :model-value="values.name || ''"
      label="Name"
      required
      :error="errors.name"
      autocomplete="off"
      @update:model-value="setField('name', $event as string)"
    />
    <CInput
      :model-value="values.description || ''"
      label="Description"
      :error="errors.description"
      autocomplete="off"
      @update:model-value="setField('description', $event as string)"
    />
  </MasterFormModal>
</template>
