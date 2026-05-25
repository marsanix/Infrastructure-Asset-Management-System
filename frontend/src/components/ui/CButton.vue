<script setup lang="ts">
/**
 * CButton — IBM Carbon button variants
 * Security: tidak ada v-html, tidak ada dynamic event binding dari props
 * Accessibility: role, aria-disabled, focus-visible ring
 */
import { computed } from 'vue'

type Variant = 'primary' | 'secondary' | 'tertiary' | 'ghost' | 'danger'
type Size    = 'sm' | 'md' | 'lg'

const props = withDefaults(defineProps<{
  variant?:  Variant
  size?:     Size
  disabled?: boolean
  loading?:  boolean
  type?:     'button' | 'submit' | 'reset'
}>(), {
  variant:  'primary',
  size:     'md',
  disabled: false,
  loading:  false,
  type:     'button',
})

const emit = defineEmits<{ click: [e: MouseEvent] }>()

function handleClick(e: MouseEvent) {
  if (props.disabled || props.loading) {
    e.preventDefault()
    return
  }
  emit('click', e)
}

const base = [
  'inline-flex items-center justify-center gap-xs',
  'type-button font-sans',
  'border border-transparent',
  'transition-colors duration-100',
  'focus-visible:outline focus-visible:outline-2 focus-visible:outline-primary focus-visible:outline-offset-0',
  'disabled:opacity-40 disabled:cursor-not-allowed',
  'rounded-none', // Carbon: 0px corners always
].join(' ')

const variants: Record<Variant, string> = {
  primary:   'bg-primary text-on-primary hover:bg-blue-hover active:bg-blue-80',
  secondary: 'bg-ink text-inverse-ink hover:bg-[#393939] active:bg-[#262626]',
  tertiary:  'bg-canvas text-primary border border-primary hover:bg-surface-1 active:bg-surface-2',
  ghost:     'bg-transparent text-primary hover:bg-surface-1 active:bg-surface-2',
  danger:    'bg-error text-on-primary hover:bg-[#ba1b23] active:bg-[#750e13]',
}

const sizes: Record<Size, string> = {
  sm: 'h-8 px-sm text-body-sm',
  md: 'h-9 px-md text-body-sm',  // shadcn default: h-9 = 36px
  lg: 'h-10 px-lg text-body-sm',
}

const classes = computed(() =>
  [base, variants[props.variant], sizes[props.size]].join(' ')
)
</script>

<template>
  <button
    :type="type"
    :disabled="disabled || loading"
    :aria-disabled="disabled || loading"
    :aria-busy="loading"
    :class="classes"
    @click="handleClick"
  >
    <!-- Loading spinner -->
    <span
      v-if="loading"
      class="inline-block w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin"
      aria-hidden="true"
    />
    <slot />
  </button>
</template>
