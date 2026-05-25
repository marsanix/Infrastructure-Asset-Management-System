<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useCrud } from '@/composables/useCrud'
import { useForm } from '@/composables/useForm'
import { ProblemSchema, PROBLEM_STATUSES } from '@/types/itsm'
import type { ProblemForm } from '@/types/itsm'
import ItsmListView    from '@/components/itsm/ItsmListView.vue'
import MasterFormModal from '@/components/master/MasterFormModal.vue'
import CInput from '@/components/ui/CInput.vue'

interface Problem { id: number; problem_number: string; title: string; status: string }

const router  = useRouter()
const { t }   = useI18n()
const crud    = useCrud<Problem>('/problems')
const modal   = ref(false)
const listRef = ref<InstanceType<typeof ItsmListView> | null>(null)

const { values, errors, submitting, setField, handleSubmit, reset } = useForm<ProblemForm>(
  ProblemSchema, { status: 'Open' }
)

const columns = [
  { key: 'problem_number', label: t('common.number'), width: '140px' },
  { key: 'title',          label: t('common.title') },
  { key: 'status',         label: t('common.status'), width: '160px' },
]

function openCreate() { reset({ status: 'Open' }); modal.value = true }
function openDetail(item: Problem) { router.push(`/app/problems/${item.id}`) }

async function onSubmit(data: ProblemForm) {
  const ok = await crud.create(data)
  if (ok) { modal.value = false; listRef.value?.load() }
}
</script>

<template>
  <ItsmListView ref="listRef" :title="t('itsm.problems.title')" endpoint="/problems"
    permission-module="problem" :columns="columns"
    :on-create-click="openCreate" :on-row-click="openDetail" />

  <MasterFormModal :open="modal" :title="t('itsm.problems.createTitle')"
    :submitting="submitting || crud.loading.value"
    @close="modal = false" @submit="handleSubmit(onSubmit)">
    <CInput :model-value="values.title || ''" :label="t('common.title')" required :error="errors.title"
      autocomplete="off" @update:model-value="setField('title', $event as string)" />
    <CInput :model-value="values.description || ''" :label="t('common.description')" :error="errors.description"
      autocomplete="off" @update:model-value="setField('description', $event as string)" />
  </MasterFormModal>
</template>
