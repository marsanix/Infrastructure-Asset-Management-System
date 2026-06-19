<script setup>
defineProps({ class: { type: String, default: '' } })
</script>
<template>
  <div :class="['absolute inset-0 overflow-hidden pointer-events-none', $props.class]">
    <div class="absolute -top-1/2 -left-1/4 h-[150%] w-[150%] animate-gradient-spin opacity-30" style="background:conic-gradient(from 0deg, hsl(var(--primary)/0.3), hsl(var(--primary)/0.05), hsl(270 70% 60% / 0.15), hsl(var(--primary)/0.05), hsl(var(--primary)/0.3))"></div>
  </div>
</template>
<style scoped>
@keyframes gradient-spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
.animate-gradient-spin { animation: gradient-spin 20s linear infinite; }
</style>
