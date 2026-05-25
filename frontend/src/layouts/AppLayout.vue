<script setup lang="ts">
import { ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '@/stores/auth'
import ThemeToggle  from '@/components/ui/ThemeToggle.vue'
import LocaleToggle from '@/components/ui/LocaleToggle.vue'

const { t } = useI18n()
const auth  = useAuthStore()
const route = useRoute()

// Desktop: sidebar terbuka by default
// Mobile: tertutup by default
const sidebarOpen = ref(window.innerWidth >= 672)

// Tutup sidebar saat navigasi di mobile
watch(() => route.path, () => {
  if (window.innerWidth < 672) sidebarOpen.value = false
})

function toggleSidebar() { sidebarOpen.value = !sidebarOpen.value }
function closeSidebar()  { sidebarOpen.value = false }

interface NavItem { label: string; to: string; permission?: string }

const navGroups: { heading?: string; items: NavItem[] }[] = [
  {
    items: [{ label: t('nav.dashboard'), to: '/app' }],
  },
  {
    heading: t('nav.groups.asset'),
    items: [
      { label: t('nav.assets'),      to: '/app/assets' },
      { label: t('nav.employees'),   to: '/app/employees' },
      { label: t('nav.departments'), to: '/app/departments' },
      { label: t('nav.locations'),   to: '/app/locations' },
      { label: t('nav.categories'),  to: '/app/categories' },
      { label: t('nav.brands'),      to: '/app/brands' },
      { label: t('nav.models'),      to: '/app/models' },
    ],
  },
  {
    heading: t('nav.groups.itsm'),
    items: [
      { label: t('nav.incidents'), to: '/app/incidents' },
      { label: t('nav.changes'),   to: '/app/changes' },
      { label: t('nav.problems'),  to: '/app/problems' },
      { label: t('nav.requests'),  to: '/app/requests' },
    ],
  },
  {
    heading: t('nav.groups.reporting'),
    items: [{ label: t('nav.reports'), to: '/app/reports' }],
  },
  {
    heading: t('nav.groups.admin'),
    items: [
      { label: t('nav.accounts'),  to: '/app/accounts',   permission: 'account:read' },
      { label: t('nav.auditLogs'), to: '/app/audit-logs', permission: 'audit:read' },
    ],
  },
]

function visibleItems(items: NavItem[]) {
  return items.filter(i => !i.permission || auth.hasPermission(i.permission))
}
</script>

<template>
  <div class="flex flex-col h-screen overflow-hidden bg-canvas font-sans">

    <!-- ── Top Nav ──────────────────────────────────────────── -->
    <header class="flex items-center gap-sm px-sm tablet:px-lg bg-canvas border-b border-hairline h-[48px] flex-shrink-0 z-20">
      <!-- Hamburger — selalu tampil -->
      <button
        class="p-xs text-ink hover:bg-surface-1 rounded-none transition-colors flex-shrink-0"
        :aria-label="sidebarOpen ? 'Tutup menu' : 'Buka menu'"
        :aria-expanded="sidebarOpen"
        @click="toggleSidebar"
      >
        <!-- Animasi hamburger → X -->
        <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
          <Transition name="icon">
            <template v-if="!sidebarOpen">
              <g>
                <rect y="3" width="20" height="2"/>
                <rect y="9" width="20" height="2"/>
                <rect y="15" width="20" height="2"/>
              </g>
            </template>
            <template v-else>
              <g>
                <rect x="2" y="9" width="16" height="2" transform="rotate(45 10 10)"/>
                <rect x="2" y="9" width="16" height="2" transform="rotate(-45 10 10)"/>
              </g>
            </template>
          </Transition>
        </svg>
      </button>

      <span class="type-body-emphasis text-ink tracking-tight select-none">IAMS</span>

      <!-- User info — tampil di tablet+ -->
      <span class="hidden tablet:block type-caption text-ink-muted ml-xs truncate max-w-[160px]">
        {{ auth.user?.full_name }} · {{ auth.user?.role }}
      </span>

      <div class="flex-1" />

      <ThemeToggle />
      <LocaleToggle class="ml-xs" />

      <button
        class="ml-xs tablet:ml-md type-body-sm text-ink-muted hover:text-ink transition-colors whitespace-nowrap"
        @click="auth.logout"
      >
        {{ t('auth.logout') }}
      </button>
    </header>

    <!-- ── Layout body ──────────────────────────────────────── -->
    <div class="flex flex-1 overflow-hidden relative">

      <!-- ── Mobile backdrop overlay ─────────────────────────── -->
      <Transition name="backdrop">
        <div
          v-if="sidebarOpen"
          class="fixed inset-0 z-30 bg-ink/40 tablet:hidden"
          aria-hidden="true"
          @click="closeSidebar"
        />
      </Transition>

      <!-- ── Sidebar ──────────────────────────────────────────── -->
      <!-- Mobile: fixed drawer dari kiri, overlay di atas konten -->
      <!-- Desktop: inline sidebar yang mengambil space -->
      <Transition name="sidebar">
        <aside
          v-if="sidebarOpen"
          class="
            fixed tablet:relative
            top-[48px] tablet:top-0
            left-0
            h-[calc(100vh-48px)] tablet:h-full
            w-64 tablet:w-60
            z-40 tablet:z-auto
            bg-canvas border-r border-hairline
            overflow-y-auto
            flex-shrink-0
          "
          aria-label="Main navigation"
        >
          <nav class="py-xs">
            <template v-for="group in navGroups" :key="group.heading">
              <div
                v-if="group.heading && visibleItems(group.items).length"
                class="px-md pt-md pb-xs type-caption text-ink-subtle uppercase tracking-wider"
              >
                {{ group.heading }}
              </div>
              <RouterLink
                v-for="item in visibleItems(group.items)"
                :key="item.to"
                :to="item.to"
                class="flex items-center px-md py-xs type-body-sm text-ink-muted hover:bg-surface-1 hover:text-ink border-l-2 border-transparent transition-colors duration-75"
                active-class="bg-surface-1 text-ink border-l-2 border-primary"
                exact-active-class="bg-surface-1 text-ink border-l-2 border-primary"
                @click="() => { if (window.innerWidth < 672) closeSidebar() }"
              >
                {{ item.label }}
              </RouterLink>
            </template>
          </nav>
        </aside>
      </Transition>

      <!-- ── Main content ─────────────────────────────────────── -->
      <main class="flex-1 overflow-y-auto bg-canvas min-w-0">
        <RouterView />
      </main>
    </div>
  </div>
</template>

<style scoped>
/* Backdrop fade */
.backdrop-enter-active, .backdrop-leave-active { transition: opacity 200ms ease; }
.backdrop-enter-from, .backdrop-leave-to       { opacity: 0; }

/* Sidebar slide (mobile only) */
@media (max-width: 671px) {
  .sidebar-enter-active, .sidebar-leave-active { transition: transform 220ms ease; }
  .sidebar-enter-from, .sidebar-leave-to       { transform: translateX(-100%); }
}
</style>
