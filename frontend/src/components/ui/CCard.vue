<script setup lang="ts">
/**
 * CCard — IBM Carbon tile variants
 * - feature: canvas bg, 1px hairline border, 24px padding
 * - elevated: surface-1 bg, 24px padding
 * - product: canvas bg, 32px padding
 * - hero: canvas bg, 48px padding
 * Carbon: 0px radius, no drop shadow — depth via surface change + hairline
 */
type Variant = 'feature' | 'elevated' | 'product' | 'hero'

withDefaults(defineProps<{
  variant?: Variant
  as?:      string
}>(), {
  variant: 'feature',
  as:      'div',
})
</script>

<template>
  <component
    :is="as"
    :class="[
      'rounded-none font-sans',
      variant === 'feature'  && 'bg-canvas border border-hairline p-lg',
      variant === 'elevated' && 'bg-surface-1 p-lg',
      variant === 'product'  && 'bg-canvas border border-hairline p-xl',
      variant === 'hero'     && 'bg-canvas border border-hairline p-xxl',
    ]"
  >
    <slot />
  </component>
</template>
