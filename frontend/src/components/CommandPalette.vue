<script setup>
import { ref, computed, watch, nextTick, onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '@/stores/auth'
import { useLocaleStore } from '@/stores/locale'
import { useThemeStore } from '@/stores/theme'
import { navMenu } from '@/lib/menuConfig'

const { t } = useI18n()
const router = useRouter()
const auth = useAuthStore()
const locale = useLocaleStore()
const theme = useThemeStore()

const props = defineProps({
  modelValue: { type: Boolean, default: false },
})
const emit = defineEmits(['update:modelValue'])

const query = ref('')
const activeIndex = ref(0)
const inputRef = ref(null)
const listRef = ref(null)

const icons = {
  search: 'M21 21l-4.3-4.3 M11 19a8 8 0 1 0 0-16 8 8 0 0 0 0 16Z',
  home: 'M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z M9 22V12h6v10',
  box: 'M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z M3.3 7l8.7 5 8.7-5 M12 22V12',
  plus: 'M12 5v14 M5 12h14',
  language: 'M5 8h14 M5 16h14 M12 5v14 M3 12h18',
  moon: 'M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z',
  sun: 'M12 1v2 M12 21v2 M4.22 4.22l1.42 1.42 M18.36 18.36l1.42 1.42 M1 12h2 M21 12h2 M4.22 19.78l1.42-1.42 M18.36 5.64l1.42-1.42 M16 12a4 4 0 1 1-8 0 4 4 0 0 1 8 0Z',
  logout: 'M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4 M16 17l5-5-5-5 M21 12H9',
  corner: 'M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71',
  list: 'M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z M14 2v6h6 M16 13H8 M16 17H8 M10 9H8',
}

function iconFor(item) {
  if (item.icon && icons[item.icon]) return icons[item.icon]
  return icons.box
}

const navCommands = computed(() => {
  const role = auth.role || 'Operator'
  return navMenu
    .filter((m) => m.roles.includes(role))
    .map((m) => ({
      id: `nav-${m.name}`,
      title: t(m.i18nKey),
      description: t('common.navigate') + ': ' + t(m.i18nKey),
      icon: m.icon,
      category: 'navigation',
      keywords: [t(m.i18nKey).toLowerCase(), m.label.toLowerCase(), m.name],
      action: () => { router.push({ name: m.name }) },
    }))
})

const quickCommands = computed(() => {
  const role = auth.role || 'Operator'
  const cmds = []

  const createItems = {
    assets: { title: t('assets.addAsset'), kw: ['tambah aset', 'buat aset', 'create asset', 'new asset', 'aset baru', 'add asset'] },
    incidents: { title: t('incidents.addIncident'), kw: ['tambah insiden', 'buat insiden', 'create incident', 'new incident', 'insiden baru'] },
    problems: { title: t('problems.addProblem'), kw: ['tambah problem', 'buat problem', 'create problem', 'new problem', 'problem baru'] },
    requests: { title: t('requests.addRequest'), kw: ['tambah permintaan', 'buat request', 'create request', 'new request'] },
    changes: { title: t('changes.addChange'), kw: ['tambah perubahan', 'buat change', 'create change', 'new change'] },
  }

  for (const [name, cfg] of Object.entries(createItems)) {
    const menu = navMenu.find((m) => m.name === name)
    if (!menu || !menu.roles.includes(role)) continue
    cmds.push({
      id: `create-${name}`,
      title: cfg.title,
      description: `${t('common.navigate')}: ${t(menu.i18nKey)}`,
      icon: 'plus',
      category: 'action',
      keywords: cfg.kw,
      action: () => { router.push({ name }) },
    })
  }

  if (auth.isAdmin && navMenu.find((m) => m.name === 'users-roles')?.roles.includes(role)) {
    cmds.push({
      id: 'create-user',
      title: t('usersRoles.addUser'),
      description: `${t('common.navigate')}: ${t('navigation.usersRoles')}`,
      icon: 'plus',
      category: 'action',
      keywords: ['tambah user', 'tambah pengguna', 'create user', 'new user', 'add user', 'pengguna baru'],
      action: () => { router.push({ name: 'users-roles' }) },
    })
  }

  return cmds
})

const prefCommands = computed(() => {
  const cmds = [
    {
      id: 'lang-toggle',
      title: locale.current === 'id' ? 'Switch to English' : 'Ganti ke Bahasa Indonesia',
      description: locale.current === 'id' ? 'Bahasa Indonesia → English' : 'English → Bahasa Indonesia',
      icon: 'language',
      category: 'preference',
      keywords: ['ganti bahasa', 'switch language', 'english', 'indonesia', 'id', 'en', 'bahasa'],
      action: () => { locale.setLocale(locale.current === 'id' ? 'en' : 'id') },
    },
    {
      id: 'theme-toggle',
      title: theme.resolved === 'dark' ? t('navigation.light') : t('navigation.dark'),
      description: theme.resolved === 'dark' ? t('navigation.switchLight') : t('navigation.switchDark'),
      icon: theme.resolved === 'dark' ? 'sun' : 'moon',
      category: 'preference',
      keywords: ['tema', 'theme', 'dark', 'light', 'gelap', 'terang', 'mode'],
      action: () => { theme.setMode(theme.resolved === 'dark' ? 'light' : 'dark', window.innerWidth / 2, window.innerHeight / 2) },
    },
    {
      id: 'logout',
      title: t('common.logout'),
      description: t('auth.logoutDesc') || 'Keluar dari sesi',
      icon: 'logout',
      category: 'preference',
      keywords: ['keluar', 'logout', 'sign out', 'signout', 'exit'],
      action: async () => { await auth.logout(); router.push({ name: 'login' }) },
    },
  ]
  return cmds
})

const allCommands = computed(() => [...navCommands.value, ...quickCommands.value, ...prefCommands.value])

const filtered = computed(() => {
  const q = query.value.trim().toLowerCase()
  if (!q) {
    // default: dashboard, assets, incidents, plus reports if admin
    const defaults = ['nav-dashboard', 'nav-assets', 'nav-incidents']
    const all = allCommands.value
    const result = []
    for (const id of defaults) {
      const c = all.find((x) => x.id === id)
      if (c) result.push(c)
    }
    if (auth.isAdmin) {
      const r = all.find((x) => x.id === 'nav-reports')
      if (r) result.push(r)
    }
    return result
  }
  return allCommands.value.filter((c) => {
    const haystack = [c.title, c.description, ...c.keywords].join(' ').toLowerCase()
    return haystack.includes(q)
  })
})

const grouped = computed(() => {
  const labels = { navigation: t('common.navigate'), action: t('common.create'), preference: t('common.preference') }
  const groups = {}
  for (const c of filtered.value) {
    const key = c.category
    if (!groups[key]) groups[key] = { label: labels[key] || key, items: [] }
    groups[key].items.push(c)
  }
  return Object.values(groups)
})

const activeCommand = computed(() => {
  const flat = filtered.value
  if (!flat.length) return null
  return flat[Math.min(activeIndex.value, flat.length - 1)]
})

function selectCommand(cmd) {
  cmd.action()
  close()
}

function close() {
  emit('update:modelValue', false)
}

function onKeydown(e) {
  if (!props.modelValue) return
  if (e.key === 'Escape') { e.preventDefault(); close() }
  else if (e.key === 'ArrowDown') { e.preventDefault(); activeIndex.value = Math.min(activeIndex.value + 1, filtered.value.length - 1) }
  else if (e.key === 'ArrowUp') { e.preventDefault(); activeIndex.value = Math.max(activeIndex.value - 1, 0) }
  else if (e.key === 'Enter') {
    e.preventDefault()
    if (activeCommand.value) selectCommand(activeCommand.value)
  }
}

function scrollActiveIntoView() {
  nextTick(() => {
    const el = listRef.value?.querySelector('[data-active]')
    el?.scrollIntoView({ block: 'nearest' })
  })
}

watch(activeIndex, scrollActiveIntoView)
watch(query, () => { activeIndex.value = 0 })

watch(() => props.modelValue, (open) => {
  if (open) {
    query.value = ''
    activeIndex.value = 0
    nextTick(() => inputRef.value?.focus())
  }
})

function onBackdropClick(e) {
  if (e.target === e.currentTarget) close()
}
</script>

<template>
  <teleport to="body">
    <div
      v-if="modelValue"
      class="fixed inset-0 z-[60] flex items-start justify-center pt-[15vh] sm:pt-[20vh] px-4"
      @click="onBackdropClick"
    >
      <div class="absolute inset-0 bg-black/50 backdrop-blur-[2px]" />
      <div
        class="relative w-full max-w-[580px] bg-card border border-border rounded-xl shadow-2xl overflow-hidden animate-fade-in"
        role="dialog"
        aria-modal="true"
        aria-label="Command Palette"
        @keydown="onKeydown"
      >
        <!-- Search -->
        <div class="flex items-center gap-2.5 px-4 py-3 border-b border-border">
          <svg class="h-4 w-4 shrink-0 text-muted-foreground" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path :d="icons.search"/></svg>
          <input
            ref="inputRef"
            v-model="query"
            type="text"
            class="flex-1 bg-transparent text-sm outline-none placeholder:text-muted-foreground/60"
            :placeholder="t('common.search') + '...'"
            autocomplete="off"
            spellcheck="false"
          />
          <kbd class="hidden sm:inline-flex items-center gap-0.5 rounded-md border border-border bg-muted px-1.5 py-0.5 text-[10px] font-mono text-muted-foreground">Esc</kbd>
        </div>

        <!-- Results -->
        <div ref="listRef" class="max-h-72 sm:max-h-80 overflow-y-auto p-2">
          <template v-if="filtered.length">
            <div v-for="group in grouped" :key="group.label" class="mb-1">
              <p class="text-[10px] font-semibold uppercase tracking-wide text-muted-foreground px-3 py-1.5">{{ group.label }}</p>
              <button
                v-for="cmd in group.items"
                :key="cmd.id"
                :data-active="cmd.id === activeCommand?.id ? '' : undefined"
                :class="[
                  'w-full flex items-center gap-3 px-3 py-2 rounded-lg text-left transition-colors duration-75',
                  cmd.id === activeCommand?.id
                    ? 'bg-primary/10 text-primary'
                    : 'text-foreground/80 hover:bg-secondary/60',
                ]"
                @click="selectCommand(cmd)"
                @mouseenter="activeIndex = filtered.indexOf(cmd)"
              >
                <div :class="['h-7 w-7 rounded-md grid place-items-center shrink-0', cmd.id === activeCommand?.id ? 'bg-primary/15 text-primary' : 'bg-muted text-muted-foreground']">
                  <svg class="h-3.5 w-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path :d="iconFor(cmd)"/></svg>
                </div>
                <div class="flex-1 min-w-0">
                  <p class="text-[13px] font-medium leading-tight truncate">{{ cmd.title }}</p>
                  <p class="text-[11px] text-muted-foreground leading-tight truncate">{{ cmd.description }}</p>
                </div>
                <span :class="['text-[9px] font-medium uppercase tracking-wide rounded-full border px-1.5 py-0.5 shrink-0', cmd.category === 'navigation' ? 'bg-primary/8 text-primary/80 border-primary/15' : cmd.category === 'action' ? 'bg-warning/10 text-warning/80 border-warning/20' : 'bg-muted text-muted-foreground border-border']">
                  {{ cmd.category === 'navigation' ? t('common.navigate') : cmd.category === 'action' ? t('common.create') : t('common.preference') }}
                </span>
              </button>
            </div>
          </template>
          <div v-else class="py-10 text-center">
            <svg class="h-8 w-8 mx-auto text-muted-foreground/30" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path :d="icons.search"/></svg>
            <p class="text-sm text-muted-foreground mt-2">{{ t('common.noResults') || 'Tidak ditemukan' }}</p>
          </div>
        </div>

        <!-- Footer hint -->
        <div class="flex items-center gap-4 px-4 py-2 border-t border-border text-[10px] text-muted-foreground">
          <span class="flex items-center gap-1"><kbd class="rounded bg-muted px-1 py-0.5 font-mono">↑↓</kbd> Navigasi</span>
          <span class="flex items-center gap-1"><kbd class="rounded bg-muted px-1 py-0.5 font-mono">↵</kbd> Pilih</span>
          <span class="flex items-center gap-1"><kbd class="rounded bg-muted px-1 py-0.5 font-mono">Esc</kbd> Tutup</span>
        </div>
      </div>
    </div>
  </teleport>
</template>
