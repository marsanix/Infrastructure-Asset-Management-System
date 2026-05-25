<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { z } from 'zod'
import { useCrud } from '@/composables/useCrud'
import { useForm } from '@/composables/useForm'
import MasterListView  from '@/components/master/MasterListView.vue'
import MasterFormModal from '@/components/master/MasterFormModal.vue'
import CInput  from '@/components/ui/CInput.vue'
import CSelect from '@/components/ui/CSelect.vue'

interface DeviceModel {
  id: number; name: string; specifications: string | null
  brand_id: number; category_id: number; is_active: boolean
  brand?: { id: number; name: string } | null
  category?: { id: number; name: string } | null
}
interface Brand    { id: number; name: string }
interface Category { id: number; name: string }

const Schema = z.object({
  name:           z.string().min(1, 'Name is required').max(100),
  specifications: z.string().max(2000).optional(),
  brand_id:       z.number({ required_error: 'Brand is required' }).int().positive(),
  category_id:    z.number({ required_error: 'Category is required' }).int().positive(),
  is_active:      z.boolean().default(true),
})
type Form = z.infer<typeof Schema>

const crud         = useCrud<DeviceModel>('/models')
const brandCrud    = useCrud<Brand>('/brands')
const categoryCrud = useCrud<Category>('/categories')
const modal        = ref(false)
const editTarget   = ref<DeviceModel | null>(null)
const listRef      = ref<InstanceType<typeof MasterListView> | null>(null)
const brandOptions    = ref<{ value: string; label: string }[]>([])
const categoryOptions = ref<{ value: string; label: string }[]>([])

const { values, errors, submitting, setField, handleSubmit, reset } = useForm<Form>(Schema, { is_active: true })

const columns = [
  { key: 'name',     label: 'Model Name' },
  { key: 'brand',    label: 'Brand',    format: (r: Record<string, unknown>) => (r as DeviceModel).brand?.name || '—' },
  { key: 'category', label: 'Category', format: (r: Record<string, unknown>) => (r as DeviceModel).category?.name || '—' },
  { key: 'is_active', label: 'Status', width: '100px' },
]

onMounted(async () => {
  const [brands, categories] = await Promise.all([
    brandCrud.fetchOptions(),
    categoryCrud.fetchOptions(),
  ])
  brandOptions.value    = brands.map(b => ({ value: String(b.id), label: b.name }))
  categoryOptions.value = categories.map(c => ({ value: String(c.id), label: c.name }))
})

function openCreate() { editTarget.value = null; reset({ is_active: true }); modal.value = true }
function openEdit(item: DeviceModel) {
  editTarget.value = item
  reset({ name: item.name, specifications: item.specifications ?? '', brand_id: item.brand_id, category_id: item.category_id, is_active: item.is_active })
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
  <MasterListView ref="listRef" title="Device Models" endpoint="/models"
    permission-module="model" :columns="columns"
    :on-create-click="openCreate" :on-edit-click="openEdit" />

  <MasterFormModal :open="modal" :title="editTarget ? 'Edit Model' : 'Create Model'"
    :submitting="submitting || crud.loading.value"
    @close="modal = false" @submit="handleSubmit(onSubmit)">
    <CInput :model-value="values.name || ''" label="Model Name" required :error="errors.name"
      autocomplete="off" @update:model-value="setField('name', $event as string)" />
    <CSelect :model-value="String(values.brand_id || '')" label="Brand" required
      placeholder="Select brand..." :options="brandOptions" :error="errors.brand_id"
      @update:model-value="setField('brand_id', Number($event))" />
    <CSelect :model-value="String(values.category_id || '')" label="Category" required
      placeholder="Select category..." :options="categoryOptions" :error="errors.category_id"
      @update:model-value="setField('category_id', Number($event))" />
    <CInput :model-value="values.specifications || ''" label="Specifications" :error="errors.specifications"
      autocomplete="off" @update:model-value="setField('specifications', $event as string)" />
  </MasterFormModal>
</template>
