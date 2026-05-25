<script setup lang="ts">
/**
 * TextReveal — Inspira UI (ported from Aceternity UI)
 * Word-by-word reveal animation on scroll
 */
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { cn } from '@/lib/utils'

const props = withDefaults(defineProps<{
  text:   string
  class?: string
}>(), {})

const containerRef = ref<HTMLElement | null>(null)
const scrollProgress = ref(0)

const words = computed(() => props.text.split(' '))

function handleScroll() {
  if (!containerRef.value) return
  const rect = containerRef.value.getBoundingClientRect()
  const windowH = window.innerHeight
  const progress = 1 - (rect.top / windowH)
  scrollProgress.value = Math.max(0, Math.min(1, progress))
}

onMounted(() => {
  window.addEventListener('scroll', handleScroll, { passive: true })
  handleScroll()
})
onUnmounted(() => window.removeEventListener('scroll', handleScroll))
</script>

<template>
  <div
    ref="containerRef"
    :class="cn('flex flex-wrap gap-x-[0.3em]', $props.class)"
  >
    <span
      v-for="(word, i) in words"
      :key="i"
      class="transition-all duration-500"
      :style="{
        opacity:    scrollProgress > i / words.length ? 1 : 0.15,
        filter:     scrollProgress > i / words.length ? 'blur(0)' : 'blur(4px)',
        transform:  scrollProgress > i / words.length ? 'translateY(0)' : 'translateY(6px)',
        transitionDelay: `${i * 30}ms`,
      }"
    >
      {{ word }}
    </span>
  </div>
</template>
