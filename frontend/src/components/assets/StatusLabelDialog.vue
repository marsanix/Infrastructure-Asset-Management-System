<script setup>
import { ref, watch, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import apiClient from '@/services/apiClient'
import { useUiStore } from '@/stores/ui'
import Dialog from '@/components/ui/Dialog.vue'
import Button from '@/components/ui/Button.vue'
import Input from '@/components/ui/Input.vue'
import Label from '@/components/ui/Label.vue'

const { t } = useI18n()
const props = defineProps({
  modelValue: { type: Boolean, default: false },
})
const emit = defineEmits(['update:modelValue', 'saved'])

const ui = useUiStore()
const loading = ref(false)
const form = ref({ name: '', deployable: true })

watch(() => props.modelValue, (open) => {
  if (open) {
    form.value = { name: '', deployable: true }
  }
})

async function submit() {
  const name = form.value.name.trim()
  if (!name) return
  loading.value = true
  try {
    await apiClient.createStatusLabel({ name, deployable: form.value.deployable })
    ui.pushToast({ title: t('common.success'), description: t('masterData.createSuccess'), variant: 'success' })
    emit('saved')
    emit('update:modelValue', false)
  } catch (err) {
    ui.pushToast({ title: t('common.failed'), description: err.data?.error || t('toast.failed'), variant: 'destructive' })
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <Dialog
    :model-value="modelValue"
    :title="t('masterData.addStatusLabel')"
    :description="'Buat status label kustom.'"
    size="sm"
    @update:model-value="$emit('update:modelValue', $event)"
  >
    <div class="space-y-4 text-sm">
      <div>
        <Label for="sl-name">{{ t('masterData.name') }} *</Label>
        <Input id="sl-name" v-model="form.name" placeholder="Mis: In Transit, Archived..." />
      </div>
      <div class="flex items-center gap-2">
        <input id="sl-deployable" v-model="form.deployable" type="checkbox" class="h-4 w-4 rounded border-border" />
        <Label for="sl-deployable" class="!mb-0 cursor-pointer">{{ t('masterData.deployable') }}</Label>
      </div>
    </div>

    <template #footer>
      <Button variant="ghost" @click="$emit('update:modelValue', false)">{{ t('common.cancel') }}</Button>
      <Button :loading="loading" :disabled="!form.name.trim()" @click="submit">{{ t('common.save') }}</Button>
    </template>
  </Dialog>
</template>
