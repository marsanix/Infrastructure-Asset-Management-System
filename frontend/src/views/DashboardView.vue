<script setup lang="ts">
/**
 * DashboardView — IBM Carbon dashboard
 * Stat cards + placeholder sections
 * Security: semua data dari API via reactive refs, tidak ada v-html
 */
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { api } from '@/lib/api'
import CCard  from '@/components/ui/CCard.vue'
import CBadge from '@/components/ui/CBadge.vue'

const { t } = useI18n()

interface StatusSummary { asset_status: string; total: number }

const summary  = ref<StatusSummary[]>([])
const loading  = ref(true)

onMounted(async () => {
  try {
    // TODO: ganti dengan endpoint report yang sudah diimplementasi
    // const res = await api.get('/reports/assets/summary')
    // summary.value = res.data.data
    // Placeholder data sementara
    summary.value = [
      { asset_status: 'Active',    total: 0 },
      { asset_status: 'Available', total: 0 },
      { asset_status: 'Repair',    total: 0 },
      { asset_status: 'Disposed',  total: 0 },
    ]
  } finally {
    loading.value = false
  }
})

const statusBadge: Record<string, 'success' | 'info' | 'warning' | 'error' | 'neutral'> = {
  Active:    'success',
  Available: 'info',
  Repair:    'warning',
  Disposed:  'neutral',
}
</script>

<template>
  <div class="p-sm tablet:p-lg max-w-carbon">

    <!-- Page header -->
    <div class="mb-lg border-b border-hairline pb-md">
      <p class="type-caption text-ink-muted uppercase tracking-wider">{{ t('dashboard.eyebrow') }}</p>
      <h1 class="type-subhead text-ink mt-xxs">{{ t('nav.dashboard') }}</h1>
    </div>

    <!-- Asset status cards — 2 kolom mobile, 4 desktop -->
    <section aria-labelledby="status-heading">
      <h2 id="status-heading" class="type-body-sm font-semibold text-ink mb-md">{{ t('dashboard.assetStatus') }}</h2>
      <div class="grid grid-cols-2 tablet:grid-cols-2 desktop:grid-cols-4 gap-sm tablet:gap-md">
        <CCard
          v-for="item in summary"
          :key="item.asset_status"
          variant="feature"
        >
          <div class="flex flex-col gap-xs">
            <CBadge :variant="statusBadge[item.asset_status] || 'neutral'" dot>
              {{ item.asset_status }}
            </CBadge>
            <span class="text-2xl tablet:type-card-title text-ink font-light">
              {{ loading ? '—' : item.total }}
            </span>
            <span class="type-caption text-ink-muted">{{ t('common.units') }}</span>
          </div>
        </CCard>
      </div>
    </section>

    <!-- ITSM overview — stack di mobile -->
    <section class="mt-lg tablet:mt-xl" aria-labelledby="itsm-heading">
      <h2 id="itsm-heading" class="type-body-sm font-semibold text-ink mb-md">{{ t('dashboard.itsmOverview') }}</h2>
      <div class="grid grid-cols-1 mobile:grid-cols-3 gap-sm tablet:gap-md">
        <CCard variant="elevated">
          <p class="type-body-sm text-ink mb-xs">{{ t('dashboard.openIncidents') }}</p>
          <p class="text-2xl tablet:type-card-title text-ink font-light">—</p>
        </CCard>
        <CCard variant="elevated">
          <p class="type-body-sm text-ink mb-xs">{{ t('dashboard.pendingChanges') }}</p>
          <p class="text-2xl tablet:type-card-title text-ink font-light">—</p>
        </CCard>
        <CCard variant="elevated">
          <p class="type-body-sm text-ink mb-xs">{{ t('dashboard.openRequests') }}</p>
          <p class="text-2xl tablet:type-card-title text-ink font-light">—</p>
        </CCard>
      </div>
    </section>

    <!-- Warranty -->
    <section class="mt-lg tablet:mt-xl" aria-labelledby="warranty-heading">
      <h2 id="warranty-heading" class="type-body-sm font-semibold text-ink mb-md">{{ t('dashboard.warrantyExpiring') }}</h2>
      <CCard variant="feature">
        <p class="type-body-sm text-ink-muted">{{ t('dashboard.warrantyPlaceholder') }}</p>
      </CCard>
    </section>

  </div>
</template>
