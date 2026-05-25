<script setup lang="ts">
/**
 * NumberTicker — Inspira UI (ported from Aceternity UI)
 * Animated count-up number with spring easing
 */
import { ref, watch, onMounted } from 'vue'

const props = withDefaults(defineProps<{
  value:      number
  direction?: 'up' | 'down'
  delay?:     number
  decimalPlaces?: number
}>(), {
  direction:     'up',
  delay:         0,
  decimalPlaces: 0,
})

const displayValue = ref(props.direction === 'up' ? 0 : props.value)
let animFrame: number

function animate(from: number, to: number) {
  cancelAnimationFrame(animFrame)
  const start    = performance.now()
  const duration = 1200

  function step(now: number) {
    const elapsed = now - start
    const progress = Math.min(elapsed / duration, 1)
    // Ease out cubic
    const eased = 1 - Math.pow(1 - progress, 3)
    displayValue.value = from + (to - from) * eased

    if (progress < 1) {
      animFrame = requestAnimationFrame(step)
    } else {
      displayValue.value = to
    }
  }

  animFrame = requestAnimationFrame(step)
}

onMounted(() => {
  setTimeout(() => {
    animate(
      props.direction === 'up' ? 0 : props.value,
      props.direction === 'up' ? props.value : 0,
    )
  }, props.delay * 1000)
})

watch(() => props.value, (newVal) => {
  animate(displayValue.value, newVal)
})
</script>

<template>
  <span class="tabular-nums slashed-zero inline-block" aria-live="polite">
    {{ displayValue.toFixed(decimalPlaces) }}
  </span>
</template>
