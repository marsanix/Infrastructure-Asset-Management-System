<script setup lang="ts">
/**
 * AuroraBackground — Inspira UI (ported from Aceternity UI)
 * Animated aurora gradient background
 */
import { cn } from '@/lib/utils'

withDefaults(defineProps<{
  class?: string
  showRadialGradient?: boolean
}>(), {
  showRadialGradient: true,
})
</script>

<template>
  <div
    :class="cn(
      'relative flex flex-col items-center justify-center transition-bg',
      $props.class
    )"
  >
    <div
      class="absolute inset-0 overflow-hidden"
      aria-hidden="true"
    >
      <!-- Aurora animated gradient -->
      <div
        :class="cn(
          '[--aurora:repeating-linear-gradient(100deg,var(--blue-500)_10%,var(--indigo-300)_15%,var(--blue-300)_20%,var(--violet-200)_25%,var(--blue-400)_30%)]',
          '[background-image:var(--aurora)]',
          '[background-size:300%_200%]',
          '[background-position:50%_50%,50%_50%]',
          'filter blur-[10px] invert dark:invert-0',
          'after:content-[\"\"] after:absolute after:inset-0',
          'after:[background-image:var(--aurora)]',
          'after:animate-aurora',
          'after:[background-size:200%,200%]',
          'after:mix-blend-difference',
          'pointer-events-none absolute -inset-[10px] opacity-50',
          showRadialGradient
            ? '[mask-image:radial-gradient(ellipse_at_100%_0%,black_10%,transparent_70%)]'
            : '',
        )"
        style="
          --blue-300: #93c5fd;
          --blue-400: #60a5fa;
          --blue-500: #3b82f6;
          --indigo-300: #a5b4fc;
          --violet-200: #ddd6fe;
        "
      />
    </div>
    <slot />
  </div>
</template>
