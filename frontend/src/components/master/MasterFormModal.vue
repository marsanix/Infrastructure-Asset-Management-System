<script setup lang="ts">
/**
 * MasterFormModal — generic inline form modal untuk master data
 * Slot-based: parent inject form fields, composable handle submit
 * Security: tidak ada v-html, semua input via v-model
 */
import CModal  from '@/components/ui/CModal.vue'
import CButton from '@/components/ui/CButton.vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

defineProps<{
  open:       boolean
  title:      string
  submitting?: boolean
  size?:      'sm' | 'md' | 'lg'
}>()

const emit = defineEmits<{
  close:  []
  submit: []
}>()
</script>

<template>
  <CModal :open="open" :title="title" :size="size || 'md'" @close="emit('close')">
    <form @submit.prevent="emit('submit')" novalidate>
      <div class="space-y-lg">
        <slot />
      </div>
    </form>

    <template #footer>
      <CButton variant="ghost" type="button" @click="emit('close')">
        {{ t('common.cancel') }}
      </CButton>
      <CButton
        variant="primary"
        type="button"
        :loading="submitting"
        @click="emit('submit')"
      >
        {{ t('common.save') }}
      </CButton>
    </template>
  </CModal>
</template>
