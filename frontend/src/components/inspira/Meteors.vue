<script setup lang="ts">
/**
 * Meteors — Inspira UI (ported from Aceternity UI)
 * Animated falling meteor shower effect
 */
import { ref, onMounted } from 'vue'
import { cn } from '@/lib/utils'

const props = withDefaults(defineProps<{
  number?: number
}>(), {
  number: 20,
})

interface Meteor {
  id:     number
  top:    string
  left:   string
  width:  string
  delay:  string
  duration: string
  angle:  string
}

const meteors = ref<Meteor[]>([])

onMounted(() => {
  meteors.value = Array.from({ length: props.number }, (_, i) => ({
    id:       i,
    top:      `${Math.floor(Math.random() * 100)}%`,
    left:     `${Math.floor(Math.random() * 100)}%`,
    width:    `${Math.floor(Math.random() * 80) + 60}px`,
    delay:    `${Math.random() * 0.6}s`,
    duration: `${Math.floor(Math.random() * 8) + 4}s`,
    angle:    '215deg',
  }))
})
</script>

<template>
  <span aria-hidden="true">
    <span
      v-for="meteor in meteors"
      :key="meteor.id"
      class="pointer-events-none absolute h-0.5 rotate-[215deg] rounded-none bg-gradient-to-r from-white to-transparent shadow-[0_0_0_1px_#ffffff10] animate-meteor"
      :style="{
        top:            meteor.top,
        left:           meteor.left,
        width:          meteor.width,
        animationDelay: meteor.delay,
        animationDuration: meteor.duration,
      }"
    />
  </span>
</template>

<style scoped>
@keyframes meteor {
  0%   { transform: rotate(215deg) translateX(0); opacity: 1; }
  70%  { opacity: 1; }
  100% { transform: rotate(215deg) translateX(-800px); opacity: 0; }
}
.animate-meteor {
  animation: meteor 5s linear infinite;
}
</style>
