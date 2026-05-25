<script setup lang="ts">
/**
 * BorderBeam — Inspira UI (ported from Aceternity UI)
 * Animated glowing border sweep effect
 */
import { cn } from '@/lib/utils'

withDefaults(defineProps<{
  size?:        number
  duration?:    number
  anchor?:      number
  borderWidth?: number
  colorFrom?:   string
  colorTo?:     string
  delay?:       number
  class?:       string
}>(), {
  size:        200,
  duration:    15,
  anchor:      90,
  borderWidth: 1.5,
  colorFrom:   '#0f62fe',
  colorTo:     '#a56eff',
  delay:       0,
})
</script>

<template>
  <div
    :class="cn(
      'pointer-events-none absolute inset-0 rounded-none [border:calc(var(--border-width)*1px)_solid_transparent]',
      '[background:padding-box_linear-gradient(transparent,transparent),border-box_linear-gradient(calc(var(--anchor)*1deg),transparent_calc(var(--anchor)*1%-5%),var(--color-from)_calc(var(--anchor)*1%),var(--color-to)_calc(var(--anchor)*1%+5%),transparent_calc(var(--anchor)*1%+10%))]',
      '[animation:border-beam_var(--duration)s_var(--delay)s_linear_infinite]',
      $props.class
    )"
    :style="{
      '--size':         size,
      '--duration':     duration,
      '--anchor':       anchor,
      '--border-width': borderWidth,
      '--color-from':   colorFrom,
      '--color-to':     colorTo,
      '--delay':        `-${delay}s`,
    }"
    aria-hidden="true"
  />
</template>
