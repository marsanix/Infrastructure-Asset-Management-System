<script setup lang="ts">
/**
 * CBadge — status badge sesuai Carbon semantic colors
 * Light mode: background pastel + teks gelap
 * Dark mode: background gelap + teks terang (kontras tinggi)
 */
type Variant = 'success' | 'warning' | 'error' | 'info' | 'neutral'

withDefaults(defineProps<{
  variant?: Variant
  dot?:     boolean
}>(), {
  variant: 'neutral',
  dot:     false,
})

// Light: bg pastel, teks gelap
// Dark:  bg gelap transparan, teks terang — pakai dark: prefix Tailwind
const styles: Record<string, string> = {
  success: [
    'bg-[#defbe6] text-[#0e6027] border-[#24a148]',
    'dark:bg-[#071908] dark:text-[#6fdc8c] dark:border-[#24a148]',
  ].join(' '),
  warning: [
    'bg-[#fdf6dd] text-[#684e00] border-[#f1c21b]',
    'dark:bg-[#1c1500] dark:text-[#f1c21b] dark:border-[#f1c21b]',
  ].join(' '),
  error: [
    'bg-[#fff1f1] text-[#750e13] border-[#da1e28]',
    'dark:bg-[#2d0709] dark:text-[#ff8389] dark:border-[#da1e28]',
  ].join(' '),
  info: [
    'bg-[#edf5ff] text-[#002d9c] border-[#0f62fe]',
    'dark:bg-[#001141] dark:text-[#78a9ff] dark:border-[#4589ff]',
  ].join(' '),
  neutral: [
    'bg-surface-1 text-ink-muted border-hairline',
    'dark:bg-surface-1 dark:text-ink-muted dark:border-hairline',
  ].join(' '),
}

const dotColors: Record<string, string> = {
  success: 'bg-[#24a148] dark:bg-[#6fdc8c]',
  warning: 'bg-[#f1c21b] dark:bg-[#f1c21b]',
  error:   'bg-[#da1e28] dark:bg-[#ff8389]',
  info:    'bg-[#0f62fe] dark:bg-[#78a9ff]',
  neutral: 'bg-ink-subtle',
}
</script>

<template>
  <span
    :class="[
      'inline-flex items-center gap-xxs',
      'type-caption font-sans',
      'px-[5px] py-[1px]',
      'border rounded-xs',
      styles[variant],
    ]"
  >
    <span
      v-if="dot"
      :class="['w-2 h-2 rounded-full flex-shrink-0', dotColors[variant]]"
      aria-hidden="true"
    />
    <slot />
  </span>
</template>
