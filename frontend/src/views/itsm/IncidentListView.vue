<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useCrud } from '@/composables/useCrud'
import { useForm } from '@/composables/useForm'
import { IncidentSchema, INCIDENT_STATUSES, INCIDENT_PRIORITIES, INCIDENT_SEVERITIES } from '@/types/itsm'
import type { IncidentForm } from '@/types/itsm'
import ItsmListView    from '@/components/itsm/ItsmListView.vue'
import MasterFormModal from '@/components/master/MasterFormModal.vue'
import CInput  from '@/components/ui/CInput.vue'
import CSelect from '@/components/ui/CSelect.vue'

interface Incident { id: number; incident_number: string; title: string; status: string; priority: string; severity: string }

const router = useRouter()
const { t }  = useI18n()
const crud   = useCrud<Incident>('/incidents')
const modal  = ref(false)
const listRef = ref<InstanceType<typeof ItsmListView> | null>(null)

const { values, errors, submitting, setField, handleSubmit, reset } = useForm<IncidentForm>(
  IncidentSchema, { priority: 'Medium', severity: 'S3', status: 'Open' }
)

const columns = [
  { key: 'incident_number', label: t('common.number'),   width: '140px' },
  { key: 'title',           label: t('common.title') },
  { key: 'priority',        label: t('common.priority'), width: '100px' },
  { key: 'severity',        label: t('common.severity'), width: '80px' },
  { key: 'status',          label: t('common.status'),   width: '120px' },
]

function openCreate() { reset({ priority: 'Medium', severity: 'S3', status: 'Open' }); modal.value = true }
function openDetail(item: Incident) { router.push(`/app/incidents/${item.id}`) }

async function onSubmit(data: IncidentForm) {
  const ok = await crud.create(data)
  if (ok) { modal.value = false; listRef.value?.load() }
}
</script>

<template>
  <ItsmListView ref="listRef" :title="t('itsm.incidents.title')" endpoint="/incidents"
    permission-module="incident" :columns="columns"
    :on-create-click="openCreate" :on-row-click="openDetail" />

  <MasterFormModal :open="modal" :title="t('itsm.incidents.createTitle')"
    :submitting="submitting || crud.loading.value"
    @close="modal = false" @submit="handleSubmit(onSubmit)">
    <CInput :model-value="values.title || ''" :label="t('common.title')" required :error="errors.title"
      autocomplete="off" @update:model-value="setField('title', $event as string)" />
    <CSelect :model-value="values.priority || 'Medium'" :label="t('common.priority')"
      :options="INCIDENT_PRIORITIES.map(p => ({ value: p, label: p }))"
      @update:model-value="setField('priority', $event as IncidentForm['priority'])" />
    <CSelect :model-value="values.severity || 'S3'" :label="t('common.severity')"
      :options="INCIDENT_SEVERITIES.map(s => ({ value: s, label: s }))"
      @update:model-value="setField('severity', $event as IncidentForm['severity'])" />
  </MasterFormModal>
</template>
