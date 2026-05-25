<script setup lang="ts">
/**
 * ShimmerButton — Inspira UI (ported from Aceternity UI)
 * Button with shimmer sweep animation
 */
import { cn } from '@/lib/utils'

withDefaults(defineProps<{
  shimmerColor?:    string
  shimmerSize?:     string
  borderRadius?:    string
  shimmerDuration?: string
  background?:      string
  class?:           string
  disabled?:        boolean
}>(), {
  shimmerColor:    '#ffffff',
  shimmerSize:     '0.05em',
  borderRadius:    '0px',
  shimmerDuration: '3s',
  background:      'radial-gradient(ellipse at top, #0f62fe, #002d9c)',
  disabled:        false,
})

const emit = defineEmits<{ click: [e: MouseEvent] }>()
</script>

<template>
  <button
    :disabled="disabled"
    :class="cn(
      'group relative z-0 flex cursor-pointer items-center justify-center overflow-hidden whitespace-nowrap px-6 py-3 text-white',
      '[background:var(--bg)]',
      'transition-shadow duration-300 ease-in-out hover:shadow-[0_0_20px_rgba(15,98,254,0.5)]',
      'disabled:opacity-50 disabled:cursor-not-allowed',
      $props.class
    )"
    :style="{
      '--bg':              background,
      'border-radius':     borderRadius,
    }"
    @click="emit('click', $event)"
  >
    <!-- Shimmer sweep -->
    <div
      class="absolute inset-0 overflow-hidden"
      :style="{ 'border-radius': borderRadius }"
      aria-hidden="true"
    >
      <div
        class="absolute inset-0 -top-[20%] left-[-20%] h-[60%] w-[140%] animate-shimmer"
        :style="{
          background: `linear-gradient(90deg, transparent, ${shimmerColor}30, ${shimmerColor}60, ${shimmerColor}30, transparent)`,
          animationDuration: shimmerDuration,
        }"
      />
    </div>

    <!-- Sparkle -->
    <div
      class="absolute inset-0 flex items-center justify-center"
      aria-hidden="true"
    >
      <div
        class="h-full w-full absolute"
        :style="{
          background: `radial-gradient(circle at 50% 0%, ${shimmerColor}20, transparent 50%)`,
        }"
      />
    </div>

    <span class="relative z-10 text-sm font-medium tracking-wide">
      <slot />
    </span>
  </button>
</template>
