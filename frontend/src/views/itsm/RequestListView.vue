<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useCrud } from '@/composables/useCrud'
import { useForm } from '@/composables/useForm'
import { RequestSchema, REQUEST_TYPES, REQUEST_PRIORITIES } from '@/types/itsm'
import type { RequestForm } from '@/types/itsm'
import ItsmListView    from '@/components/itsm/ItsmListView.vue'
import MasterFormModal from '@/components/master/MasterFormModal.vue'
import CInput  from '@/components/ui/CInput.vue'
import CSelect from '@/components/ui/CSelect.vue'

interface ServiceRequest { id: number; request_number: string; title: string; status: string; priority: string; request_type: string }

const router  = useRouter()
const { t }   = useI18n()
const crud    = useCrud<ServiceRequest>('/requests')
const modal   = ref(false)
const listRef = ref<InstanceType<typeof ItsmListView> | null>(null)

const { values, errors, submitting, setField, handleSubmit, reset } = useForm<RequestForm>(
  RequestSchema, { priority: 'Medium', request_type: 'Other', status: 'Draft' }
)

const columns = [
  { key: 'request_number', label: t('common.number'),   width: '140px' },
  { key: 'title',          label: t('common.title') },
  { key: 'request_type',   label: t('common.type'),     width: '120px' },
  { key: 'priority',       label: t('common.priority'), width: '100px' },
  { key: 'status',         label: t('common.status'),   width: '120px' },
]

function openCreate() { reset({ priority: 'Medium', request_type: 'Other', status: 'Draft' }); modal.value = true }
function openDetail(item: ServiceRequest) { router.push(`/app/requests/${item.id}`) }

async function onSubmit(data: RequestForm) {
  const ok = await crud.create(data)
  if (ok) { modal.value = false; listRef.value?.load() }
}
</script>

<template>
  <ItsmListView ref="listRef" :title="t('itsm.requests.title')" endpoint="/requests"
    permission-module="request" :columns="columns"
    :on-create-click="openCreate" :on-row-click="openDetail" />

  <MasterFormModal :open="modal" :title="t('itsm.requests.createTitle')"
    :submitting="submitting || crud.loading.value"
    @close="modal = false" @submit="handleSubmit(onSubmit)">
    <CInput :model-value="values.title || ''" :label="t('common.title')" required :error="errors.title"
      autocomplete="off" @update:model-value="setField('title', $event as string)" />
    <CSelect :model-value="values.request_type || 'Other'" :label="t('common.type')"
      :options="REQUEST_TYPES.map(t => ({ value: t, label: t }))"
      @update:model-value="setField('request_type', $event as RequestForm['request_type'])" />
    <CSelect :model-value="values.priority || 'Medium'" :label="t('common.priority')"
      :options="REQUEST_PRIORITIES.map(p => ({ value: p, label: p }))"
      @update:model-value="setField('priority', $event as RequestForm['priority'])" />
    <CInput :model-value="values.description || ''" :label="t('common.description')" :error="errors.description"
      autocomplete="off" @update:model-value="setField('description', $event as string)" />
  </MasterFormModal>
</template>
