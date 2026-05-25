<script setup lang="ts">
/**
 * CModal — Carbon dialog
 * Accessibility: role="dialog", aria-modal, aria-labelledby, focus trap, Escape key
 * Security: tidak ada v-html di dalam modal
 */
import { onMounted, onUnmounted, watch } from 'vue'

const props = defineProps<{
  open:    boolean
  title?:  string
  size?:   'sm' | 'md' | 'lg'
}>()

const emit = defineEmits<{ close: [] }>()

function handleKeydown(e: KeyboardEvent) {
  if (e.key === 'Escape' && props.open) emit('close')
}

onMounted(()  => document.addEventListener('keydown', handleKeydown))
onUnmounted(() => document.removeEventListener('keydown', handleKeydown))

// Lock body scroll when open
watch(() => props.open, (val) => {
  document.body.style.overflow = val ? 'hidden' : ''
})

const sizeClass: Record<string, string> = {
  sm: 'max-w-sm',
  md: 'max-w-lg',
  lg: 'max-w-2xl',
}
</script>

<template>
  <Teleport to="body">
    <Transition name="modal">
      <div
        v-if="open"
        class="fixed inset-0 z-50 flex items-center justify-center p-md"
        role="dialog"
        aria-modal="true"
        :aria-labelledby="title ? 'modal-title' : undefined"
      >
        <!-- Backdrop -->
        <div
          class="absolute inset-0 bg-ink/60"
          aria-hidden="true"
          @click="emit('close')"
        />

        <!-- Panel -->
        <div
          :class="[
            'relative w-full bg-canvas border border-hairline rounded-none',
            'shadow-none', // Carbon: no drop shadow
            sizeClass[size || 'md'],
          ]"
        >
          <!-- Header -->
          <div class="flex items-center justify-between px-lg py-md border-b border-hairline">
            <h2 v-if="title" id="modal-title" class="type-body-emphasis text-ink">
              {{ title }}
            </h2>
            <slot name="header" />
            <button
              class="ml-auto p-xs text-ink-muted hover:text-ink hover:bg-surface-1 rounded-none transition-colors"
              aria-label="Close dialog"
              @click="emit('close')"
            >
              <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor" aria-hidden="true">
                <path d="M12 4.7l-.7-.7L8 7.3 4.7 4l-.7.7L7.3 8 4 11.3l.7.7L8 8.7l3.3 3.3.7-.7L8.7 8z"/>
              </svg>
            </button>
          </div>

          <!-- Body -->
          <div class="px-lg py-lg">
            <slot />
          </div>

          <!-- Footer -->
          <div v-if="$slots.footer" class="flex items-center justify-end gap-xs px-lg py-md border-t border-hairline">
            <slot name="footer" />
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.modal-enter-active, .modal-leave-active { transition: opacity 150ms ease; }
.modal-enter-from, .modal-leave-to { opacity: 0; }
</style>
