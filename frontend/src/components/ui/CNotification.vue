<script setup lang="ts">
/**
 * CNotification — Carbon inline notification / toast
 * Accessibility: role="alert" untuk error/warning, role="status" untuk info/success
 */
type Kind = 'success' | 'warning' | 'error' | 'info'

withDefaults(defineProps<{
  kind?:    Kind
  title?:   string
  message?: string
  closable?: boolean
}>(), {
  kind:     'info',
  closable: true,
})

const emit = defineEmits<{ close: [] }>()

const styles: Record<Kind, string> = {
  success: 'border-l-4 border-success bg-[#defbe6] text-[#0e6027]',
  warning: 'border-l-4 border-warning bg-[#fdf6dd] text-[#684e00]',
  error:   'border-l-4 border-error   bg-[#fff1f1] text-[#750e13]',
  info:    'border-l-4 border-primary  bg-[#edf5ff] text-[#002d9c]',
}

const icons: Record<Kind, string> = {
  success: '✓',
  warning: '⚠',
  error:   '✕',
  info:    'ℹ',
}
</script>

<template>
  <div
    :role="kind === 'error' || kind === 'warning' ? 'alert' : 'status'"
    :aria-live="kind === 'error' ? 'assertive' : 'polite'"
    :class="['flex items-start gap-sm p-md rounded-none font-sans', styles[kind]]"
  >
    <span class="type-body-sm font-semibold flex-shrink-0" aria-hidden="true">
      {{ icons[kind] }}
    </span>
    <div class="flex-1 min-w-0">
      <p v-if="title" class="type-body-emphasis">{{ title }}</p>
      <p v-if="message" class="type-body-sm mt-xxs">{{ message }}</p>
    </div>
    <button
      v-if="closable"
      class="flex-shrink-0 p-xxs hover:opacity-70 transition-opacity"
      aria-label="Dismiss notification"
      @click="emit('close')"
    >
      ✕
    </button>
  </div>
</template>
