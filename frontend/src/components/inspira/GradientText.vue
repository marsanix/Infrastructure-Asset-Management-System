<script setup lang="ts">
/**
 * GradientText — Inspira UI
 * Animated gradient text with shimmer sweep
 */
import { cn } from '@/lib/utils'

withDefaults(defineProps<{
  class?:   string
  colors?:  string[]
  animationSpeed?: number
  showBorder?: boolean
}>(), {
  colors:         () => ['#40ffaa', '#4079ff', '#40ffaa', '#4079ff', '#40ffaa'],
  animationSpeed: 8,
  showBorder:     false,
})
</script>

<template>
  <div
    :class="cn(
      'relative mx-auto flex max-w-fit flex-row items-center justify-center font-medium',
      $props.class
    )"
  >
    <div
      v-if="showBorder"
      class="absolute inset-0 block h-full w-full animate-gradient rounded-none bg-gradient-to-r [background-size:200%]"
      :style="{
        background: `linear-gradient(90deg, ${colors.join(', ')})`,
        backgroundSize: '200%',
      }"
      aria-hidden="true"
    />
    <div
      class="inline-block bg-clip-text text-transparent animate-gradient bg-gradient-to-r [background-size:200%]"
      :style="{
        background:     `linear-gradient(90deg, ${colors.join(', ')})`,
        backgroundSize: '200%',
        animationDuration: `${animationSpeed}s`,
        WebkitBackgroundClip: 'text',
        WebkitTextFillColor: 'transparent',
      }"
    >
      <slot />
    </div>
  </div>
</template>

<style scoped>
@keyframes gradient-x {
  0%, 100% { background-position: 0% 50%; }
  50%       { background-position: 100% 50%; }
}
.animate-gradient {
  animation: gradient-x 8s linear infinite;
}
</style>
