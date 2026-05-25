<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { z } from 'zod'
import { useCrud } from '@/composables/useCrud'
import { useForm } from '@/composables/useForm'
import MasterListView  from '@/components/master/MasterListView.vue'
import MasterFormModal from '@/components/master/MasterFormModal.vue'
import CInput  from '@/components/ui/CInput.vue'
import CSelect from '@/components/ui/CSelect.vue'

interface Employee {
  id: number; name: string; email: string | null; phone: string | null
  department_id: number | null; is_active: boolean
  department?: { id: number; name: string } | null
}
interface Department { id: number; name: string }

const Schema = z.object({
  name:          z.string().min(1, 'Name is required').max(150),
  email:         z.string().email('Invalid email').optional().or(z.literal('')),
  phone:         z.string().regex(/^[\d\+\-\s\(\)]{0,20}$/, 'Invalid phone').optional().or(z.literal('')),
  department_id: z.number().int().positive().nullable().optional(),
  is_active:     z.boolean().default(true),
})
type Form = z.infer<typeof Schema>

const crud       = useCrud<Employee>('/employees')
const deptCrud   = useCrud<Department>('/departments')
const modal      = ref(false)
const editTarget = ref<Employee | null>(null)
const listRef    = ref<InstanceType<typeof MasterListView> | null>(null)
const deptOptions = ref<{ value: string; label: string }[]>([])

const { values, errors, submitting, setField, handleSubmit, reset } = useForm<Form>(Schema, { is_active: true })

const columns = [
  { key: 'name',       label: 'Name' },
  { key: 'email',      label: 'Email' },
  { key: 'department', label: 'Department', format: (r: Record<string, unknown>) => (r as Employee).department?.name || '—' },
  { key: 'is_active',  label: 'Status', width: '100px' },
]

onMounted(async () => {
  const depts = await deptCrud.fetchOptions()
  deptOptions.value = [
    { value: '', label: 'No Department' },
    ...depts.map(d => ({ value: String(d.id), label: d.name })),
  ]
})

function openCreate() { editTarget.value = null; reset({ is_active: true }); modal.value = true }
function openEdit(item: Employee) {
  editTarget.value = item
  reset({
    name: item.name, email: item.email ?? '', phone: item.phone ?? '',
    department_id: item.department_id, is_active: item.is_active,
  })
  modal.value = true
}
async function onSubmit(data: Form) {
  // Konversi empty string ke null
  const payload = {
    ...data,
    email:         data.email         || null,
    phone:         data.phone         || null,
    department_id: data.department_id || null,
  }
  const ok = editTarget.value
    ? await crud.update(editTarget.value.id, payload)
    : await crud.create(payload)
  if (ok) { modal.value = false; listRef.value?.load() }
}
</script>

<template>
  <MasterListView ref="listRef" title="Employees" endpoint="/employees"
    permission-module="account" :columns="columns"
    :on-create-click="openCreate" :on-edit-click="openEdit" />

  <MasterFormModal :open="modal" :title="editTarget ? 'Edit Employee' : 'Create Employee'"
    :submitting="submitting || crud.loading.value"
    @close="modal = false" @submit="handleSubmit(onSubmit)">
    <CInput :model-value="values.name || ''" label="Full Name" required :error="errors.name"
      autocomplete="name" @update:model-value="setField('name', $event as string)" />
    <CInput :model-value="values.email || ''" label="Email" type="email" :error="errors.email"
      autocomplete="email" @update:model-value="setField('email', $event as string)" />
    <CInput :model-value="values.phone || ''" label="Phone" type="tel" :error="errors.phone"
      autocomplete="tel" @update:model-value="setField('phone', $event as string)" />
    <CSelect :model-value="String(values.department_id || '')" label="Department"
      :options="deptOptions" :error="String(errors.department_id || '')"
      @update:model-value="setField('department_id', $event ? Number($event) : null)" />
  </MasterFormModal>
</template>
