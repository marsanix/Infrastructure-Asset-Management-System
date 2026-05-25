<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useCrud } from '@/composables/useCrud'
import { useForm } from '@/composables/useForm'
import { ChangeSchema, CHANGE_TYPES, CHANGE_PRIORITIES } from '@/types/itsm'
import type { ChangeForm } from '@/types/itsm'
import ItsmListView    from '@/components/itsm/ItsmListView.vue'
import MasterFormModal from '@/components/master/MasterFormModal.vue'
import CInput  from '@/components/ui/CInput.vue'
import CSelect from '@/components/ui/CSelect.vue'

interface Change { id: number; change_number: string; title: string; status: string; priority: string; change_type: string }

const router  = useRouter()
const { t }   = useI18n()
const crud    = useCrud<Change>('/changes')
const modal   = ref(false)
const listRef = ref<InstanceType<typeof ItsmListView> | null>(null)

const { values, errors, submitting, setField, handleSubmit, reset } = useForm<ChangeForm>(
  ChangeSchema, { priority: 'Medium', change_type: 'Normal', status: 'Draft' }
)

const columns = [
  { key: 'change_number', label: t('common.number'),   width: '140px' },
  { key: 'title',         label: t('common.title') },
  { key: 'change_type',   label: t('common.type'),     width: '100px' },
  { key: 'priority',      label: t('common.priority'), width: '100px' },
  { key: 'status',        label: t('common.status'),   width: '120px' },
]

function openCreate() { reset({ priority: 'Medium', change_type: 'Normal', status: 'Draft' }); modal.value = true }
function openDetail(item: Change) { router.push(`/app/changes/${item.id}`) }

async function onSubmit(data: ChangeForm) {
  const ok = await crud.create(data)
  if (ok) { modal.value = false; listRef.value?.load() }
}
</script>

<template>
  <ItsmListView ref="listRef" :title="t('itsm.changes.title')" endpoint="/changes"
    permission-module="change" :columns="columns"
    :on-create-click="openCreate" :on-row-click="openDetail" />

  <MasterFormModal :open="modal" :title="t('itsm.changes.createTitle')"
    :submitting="submitting || crud.loading.value"
    @close="modal = false" @submit="handleSubmit(onSubmit)">
    <CInput :model-value="values.title || ''" :label="t('common.title')" required :error="errors.title"
      autocomplete="off" @update:model-value="setField('title', $event as string)" />
    <CSelect :model-value="values.change_type || 'Normal'" :label="t('common.type')"
      :options="CHANGE_TYPES.map(t => ({ value: t, label: t }))"
      @update:model-value="setField('change_type', $event as ChangeForm['change_type'])" />
    <CSelect :model-value="values.priority || 'Medium'" :label="t('common.priority')"
      :options="CHANGE_PRIORITIES.map(p => ({ value: p, label: p }))"
      @update:model-value="setField('priority', $event as ChangeForm['priority'])" />
  </MasterFormModal>
</template>
