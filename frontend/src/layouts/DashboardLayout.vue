<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { RouterView } from 'vue-router'
import Sidebar from '@/components/layout/Sidebar.vue'
import MobileSidebar from '@/components/layout/MobileSidebar.vue'
import Header from '@/components/layout/Header.vue'
import CommandPalette from '@/components/CommandPalette.vue'

const paletteOpen = ref(false)

function onKeydown(e) {
  if ((e.key === 'k' || e.key === 'K') && (e.ctrlKey || e.metaKey)) {
    // don't open if user is typing in an input/textarea/select
    const tag = document.activeElement?.tagName
    if (tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT') return
    if (document.activeElement?.isContentEditable) return
    e.preventDefault()
    paletteOpen.value = !paletteOpen.value
  }
}

onMounted(() => window.addEventListener('keydown', onKeydown))
onBeforeUnmount(() => window.removeEventListener('keydown', onKeydown))
</script>

<template>
  <div class="h-dvh bg-background text-foreground flex">
    <a href="#main-content" class="sr-only focus:not-sr-only focus:absolute focus:z-50 focus:top-3 focus:left-3 focus:px-4 focus:py-2 focus:bg-primary focus:text-primary-foreground focus:rounded-md focus:shadow-lg">Skip ke konten utama</a>
    <Sidebar />
    <MobileSidebar />

    <div class="flex-1 flex flex-col min-w-0">
      <Header />

      <main id="main-content" class="flex-1 p-3 sm:p-4 lg:p-5 max-w-[1600px] mx-auto w-full overflow-y-auto">
        <RouterView v-slot="{ Component, route: r }">
          <transition name="fade" mode="out-in">
            <component :is="Component" :key="r.fullPath" />
          </transition>
        </RouterView>
      </main>
    </div>

    <CommandPalette v-model="paletteOpen" />
  </div>
</template>
