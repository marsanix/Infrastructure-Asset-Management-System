<script setup lang="ts">
/**
 * SparklesCore — Inspira UI (ported from Aceternity UI)
 * Canvas-based sparkle particle effect
 */
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { cn } from '@/lib/utils'

const props = withDefaults(defineProps<{
  id?:            string
  background?:    string
  minSize?:       number
  maxSize?:       number
  speed?:         number
  particleColor?: string
  particleDensity?: number
  class?:         string
}>(), {
  background:      'transparent',
  minSize:         0.4,
  maxSize:         1,
  speed:           1,
  particleColor:   '#ffffff',
  particleDensity: 100,
})

const canvasRef = ref<HTMLCanvasElement | null>(null)
let animFrame: number
let particles: { x: number; y: number; size: number; speedX: number; speedY: number; opacity: number; opacityDir: number }[] = []

function init() {
  const canvas = canvasRef.value
  if (!canvas) return
  const ctx = canvas.getContext('2d')
  if (!ctx) return

  canvas.width  = canvas.offsetWidth
  canvas.height = canvas.offsetHeight

  particles = Array.from({ length: props.particleDensity }, () => ({
    x:          Math.random() * canvas.width,
    y:          Math.random() * canvas.height,
    size:       Math.random() * (props.maxSize - props.minSize) + props.minSize,
    speedX:     (Math.random() - 0.5) * props.speed * 0.3,
    speedY:     (Math.random() - 0.5) * props.speed * 0.3,
    opacity:    Math.random(),
    opacityDir: Math.random() > 0.5 ? 1 : -1,
  }))

  function draw() {
    if (!canvas || !ctx) return
    ctx.clearRect(0, 0, canvas.width, canvas.height)

    for (const p of particles) {
      p.x += p.speedX
      p.y += p.speedY
      p.opacity += p.opacityDir * 0.005

      if (p.opacity >= 1 || p.opacity <= 0) p.opacityDir *= -1

      if (p.x < 0) p.x = canvas.width
      if (p.x > canvas.width) p.x = 0
      if (p.y < 0) p.y = canvas.height
      if (p.y > canvas.height) p.y = 0

      ctx.beginPath()
      ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2)
      ctx.fillStyle = props.particleColor
      ctx.globalAlpha = Math.max(0, Math.min(1, p.opacity))
      ctx.fill()
    }

    ctx.globalAlpha = 1
    animFrame = requestAnimationFrame(draw)
  }

  draw()
}

onMounted(() => { init() })
onUnmounted(() => { cancelAnimationFrame(animFrame) })
</script>

<template>
  <canvas
    ref="canvasRef"
    :id="id"
    :class="cn('h-full w-full', $props.class)"
    :style="{ background }"
    aria-hidden="true"
  />
</template>
