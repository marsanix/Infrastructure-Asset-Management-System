<script setup>
import { ref, onMounted, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import apiClient from '@/services/apiClient'
import Card from '@/components/ui/Card.vue'
import Badge from '@/components/ui/Badge.vue'
import { useRouter } from 'vue-router'

const { t } = useI18n()
const router = useRouter()
const assets = ref([])
const incidents = ref([])
const problems = ref([])
const loading = ref(true)
const lastUpdated = ref(null)

onMounted(async () => {
  try {
    const [a, i, p] = await Promise.all([
      apiClient.listAssets(),
      apiClient.listIncidents(),
      apiClient.listProblems(),
    ])
    assets.value = a?.data?.data || a?.data || []
    incidents.value = i?.data?.data || i?.data || []
    problems.value = p?.data?.data || p?.data || []
    lastUpdated.value = new Date()
  } catch (_) {
    // silently fail — dashboard shows empty state
  } finally {
    loading.value = false
  }
})

const timeAgo = computed(() => {
  if (!lastUpdated.value) return ''
  const sec = Math.floor((Date.now() - lastUpdated.value.getTime()) / 1000)
  if (sec < 5) return t('dashboard.justNow')
  if (sec < 60) return `${sec}s ${t('dashboard.ago')}`
  const min = Math.floor(sec / 60)
  return `${min}m ${t('dashboard.ago')}`
})

// KPIs
const totalAssets = computed(() => assets.value.length)
const activeAssets = computed(() => assets.value.filter((a) => a.status === 'Active').length)
const openIncidents = computed(() => incidents.value.filter((i) => i.status === 'Open' || i.status === 'In Progress').length)
const criticalIncidents = computed(() => incidents.value.filter((i) => i.severity === 'Critical' && i.status !== 'Closed' && i.status !== 'Resolved').length)
const activeProblems = computed(() => problems.value.filter((p) => p.status !== 'Closed').length)

const networkStatus = computed(() => {
  if (criticalIncidents.value > 0) return { label: t('dashboard.degraded'), tone: 'destructive', detail: `${criticalIncidents.value} ${t('dashboard.criticalOpen')}` }
  if (openIncidents.value > 2) return { label: t('dashboard.watch'), tone: 'warning', detail: `${openIncidents.value} ${t('dashboard.activeIncidents')}` }
  return { label: t('dashboard.operational'), tone: 'success', detail: t('dashboard.allNormal') }
})

const distribution = computed(() => {
  const map = {}
  for (const a of assets.value) {
    map[a.category_name] = (map[a.category_name] || 0) + 1
  }
  const total = Object.values(map).reduce((s, n) => s + n, 0) || 1
  const colors = ['bg-primary/50', 'bg-info/50', 'bg-warning/50', 'bg-success/50', 'bg-destructive/40']
  return Object.entries(map)
    .sort((a, b) => b[1] - a[1])
    .map(([name, count], idx) => ({ name, count, pct: Math.round((count / total) * 100), color: colors[idx % colors.length] }))
})

const statusBreakdown = computed(() => {
  const groups = { Active: 0, Available: 0, Repair: 0, Disposed: 0 }
  for (const a of assets.value) groups[a.status] = (groups[a.status] || 0) + 1
  return groups
})

const toneCls = {
  success: 'bg-success/8 text-success/70 border-success/20',
  warning: 'bg-warning/8 text-warning/70 border-warning/20',
  destructive: 'bg-destructive/8 text-destructive/70 border-destructive/20',
}
const toneDot = {
  success: 'bg-success/60',
  warning: 'bg-warning/60',
  destructive: 'bg-destructive/60',
}
</script>

<template>
  <div class="space-y-3" data-testid="dashboard-compact">
    <!-- Compact header row -->
    <div class="flex items-end justify-between gap-3 flex-wrap">
      <div>
        <p class="text-[10px] uppercase tracking-wide text-muted-foreground">{{ t('dashboard.overview') }}</p>
        <h2 class="text-lg md:text-xl font-bold tracking-tight mt-0.5">{{ t('dashboard.summary') }}</h2>
        <p class="text-xs text-muted-foreground mt-0.5">{{ t('dashboard.subtitle') }}</p>
      </div>
      <div class="flex items-center gap-2">
        <div :class="['inline-flex items-center gap-2 rounded-full px-3 py-1.5 border text-xs', toneCls[networkStatus.tone]]" data-testid="network-status-card">
          <span class="relative flex h-2 w-2">
            <span :class="['absolute inset-0 rounded-full opacity-60 animate-ping', toneDot[networkStatus.tone]]"></span>
            <span :class="['relative h-2 w-2 rounded-full', toneDot[networkStatus.tone]]"></span>
          </span>
          <span class="font-semibold uppercase tracking-wide">{{ networkStatus.label }}</span>
          <span class="opacity-80 hidden sm:inline">· {{ networkStatus.detail }}</span>
        </div>
        <div class="flex gap-1.5">
          <button class="inline-flex items-center gap-1 rounded-md border border-border bg-card hover:bg-primary hover:text-primary-foreground hover:border-primary px-2.5 py-1.5 text-[11px] font-medium transition-all duration-150" @click="router.push({name:'assets'})">
            <svg class="h-3 w-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M12 5v14M5 12h14"/></svg>
            {{ t('common.asset') }}
          </button>
          <button class="inline-flex items-center gap-1 rounded-md border border-border bg-card hover:bg-warning hover:text-white hover:border-warning px-2.5 py-1.5 text-[11px] font-medium transition-all duration-150" @click="router.push({name:'incidents'})">
            <svg class="h-3 w-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M12 5v14M5 12h14"/></svg>
            {{ t('common.incident') }}
          </button>
        </div>
      </div>
    </div>

    <!-- Time context -->
    <p v-if="timeAgo" class="text-[10px] text-muted-foreground">{{ t('dashboard.updated') }} {{ timeAgo }}</p>

    <!-- KPI cards -->
    <div class="grid grid-cols-2 xl:grid-cols-4 gap-3" data-testid="kpi-cards">
      <Card class="p-3.5">
        <div class="flex items-start justify-between gap-2">
          <div class="min-w-0">
            <p class="text-[10px] text-muted-foreground uppercase tracking-wide">{{ t('dashboard.totalAssets') }}</p>
            <p class="text-2xl font-bold tracking-tight mt-0.5 leading-none" data-testid="kpi-total-assets">{{ loading ? '—' : totalAssets }}</p>
            <p class="text-[11px] text-muted-foreground mt-1.5">
              <span class="text-success/60 font-medium">{{ activeAssets }}</span> {{ t('dashboard.active') }} ·
              <span class="text-info/60 font-medium">{{ statusBreakdown.Available }}</span> {{ t('dashboard.available') }}
            </p>
          </div>
          <div class="h-8 w-8 rounded-md bg-primary/5 text-primary/60 grid place-items-center shrink-0">
            <svg viewBox="0 0 24 24" class="h-4 w-4" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16Z"/><path d="m3.3 7 8.7 5 8.7-5M12 22V12"/></svg>
          </div>
        </div>
      </Card>

      <Card class="p-3.5">
        <div class="flex items-start justify-between gap-2">
          <div class="min-w-0">
            <p class="text-[10px] text-muted-foreground uppercase tracking-wide">{{ t('dashboard.openIncidents') }}</p>
            <p class="text-2xl font-bold tracking-tight mt-0.5 leading-none" data-testid="kpi-open-incidents">{{ loading ? '—' : openIncidents }}</p>
            <p class="text-[11px] text-muted-foreground mt-1.5">
              <span class="text-destructive/60 font-medium">{{ criticalIncidents }}</span> {{ t('dashboard.criticalNeed') }}
            </p>
          </div>
          <div class="h-8 w-8 rounded-md bg-warning/8 text-warning/60 grid place-items-center shrink-0">
            <svg viewBox="0 0 24 24" class="h-4 w-4" fill="none" stroke="currentColor" stroke-width="2"><path d="M10.29 3.86 1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0Z"/><path d="M12 9v4M12 17h.01"/></svg>
          </div>
        </div>
      </Card>

      <Card class="p-3.5">
        <div class="flex items-start justify-between gap-2">
          <div class="min-w-0">
            <p class="text-[10px] text-muted-foreground uppercase tracking-wide">{{ t('dashboard.activeProblems') }}</p>
            <p class="text-2xl font-bold tracking-tight mt-0.5 leading-none" data-testid="kpi-active-problems">{{ loading ? '—' : activeProblems }}</p>
            <p class="text-[11px] text-muted-foreground mt-1.5">{{ t('dashboard.investigating') }}</p>
          </div>
          <div class="h-8 w-8 rounded-md bg-info/5 text-info/60 grid place-items-center shrink-0">
            <svg viewBox="0 0 24 24" class="h-4 w-4" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>
          </div>
        </div>
      </Card>

      <Card class="p-3.5">
        <div class="flex items-start justify-between gap-2">
          <div class="min-w-0">
            <p class="text-[10px] text-muted-foreground uppercase tracking-wide">{{ t('dashboard.netStatus') }}</p>
            <p class="text-2xl font-bold tracking-tight mt-0.5 leading-none" data-testid="kpi-network-status">{{ networkStatus.label }}</p>
            <p class="text-[11px] text-muted-foreground mt-1.5 line-clamp-1">{{ networkStatus.detail }}</p>
          </div>
          <div :class="['h-8 w-8 rounded-md grid place-items-center shrink-0', toneCls[networkStatus.tone]]">
            <svg viewBox="0 0 24 24" class="h-4 w-4" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="3" width="20" height="14" rx="2" ry="2"/><path d="M8 21h8M12 17v4"/></svg>
          </div>
        </div>
      </Card>
    </div>

    <!-- Bottom row: Distribution + Status Breakdown -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-3">
      <Card class="p-4 lg:col-span-2">
        <div class="flex items-center justify-between mb-3">
          <div>
            <p class="text-[10px] uppercase tracking-wide text-muted-foreground">{{ t('dashboard.assetDist') }}</p>
            <h3 class="text-sm font-semibold tracking-tight">{{ t('dashboard.byCategory') }}</h3>
          </div>
          <Badge variant="muted">{{ totalAssets }} {{ t('dashboard.assets') }}</Badge>
        </div>
        <div v-if="loading" class="space-y-2 animate-pulse">
          <div v-for="i in 5" :key="i" class="h-5 bg-muted rounded" />
        </div>
        <div v-else class="space-y-2" data-testid="distribution-chart">
          <div v-for="row in distribution" :key="row.name">
            <div class="flex items-center justify-between text-xs mb-1">
              <div class="flex items-center gap-1.5">
                <span :class="['h-2 w-2 rounded-full', row.color]"></span>
                <span class="font-medium">{{ row.name }}</span>
              </div>
              <span class="text-muted-foreground">
                <span class="font-medium text-foreground">{{ row.count }}</span> · {{ row.pct }}%
              </span>
            </div>
            <div class="h-1.5 rounded-full bg-secondary overflow-hidden">
              <div :class="['h-full rounded-full transition-all', row.color]" :style="{ width: row.pct + '%' }"></div>
            </div>
          </div>
        </div>
      </Card>

      <Card class="p-4">
        <div class="flex items-center justify-between mb-3">
          <div>
            <p class="text-[10px] uppercase tracking-wide text-muted-foreground">{{ t('dashboard.assetStatus') }}</p>
            <h3 class="text-sm font-semibold tracking-tight">{{ t('dashboard.summary') }}</h3>
          </div>
        </div>
        <div class="grid grid-cols-2 gap-2" data-testid="status-breakdown">
          <div class="rounded-md border border-border p-2.5">
            <p class="text-[10px] text-muted-foreground uppercase tracking-wide">{{ t('status.active') }}</p>
            <p class="text-xl font-bold text-success/60 leading-none mt-1">{{ loading ? '—' : statusBreakdown.Active }}</p>
          </div>
          <div class="rounded-md border border-border p-2.5">
            <p class="text-[10px] text-muted-foreground uppercase tracking-wide">{{ t('status.available') }}</p>
            <p class="text-xl font-bold text-info/60 leading-none mt-1">{{ loading ? '—' : statusBreakdown.Available }}</p>
          </div>
          <div class="rounded-md border border-border p-2.5">
            <p class="text-[10px] text-muted-foreground uppercase tracking-wide">{{ t('status.repair') }}</p>
            <p class="text-xl font-bold text-warning/60 leading-none mt-1">{{ loading ? '—' : statusBreakdown.Repair }}</p>
          </div>
          <div class="rounded-md border border-border p-2.5">
            <p class="text-[10px] text-muted-foreground uppercase tracking-wide">{{ t('status.disposed') }}</p>
            <p class="text-xl font-bold text-muted-foreground leading-none mt-1">{{ loading ? '—' : statusBreakdown.Disposed }}</p>
          </div>
        </div>
      </Card>
    </div>
  </div>
</template>
