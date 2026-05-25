<script setup lang="ts">
/**
 * CTable — responsive data table
 * Desktop: table layout normal
 * Mobile (<672px): setiap row jadi "card" dengan label:value pairs
 * Security: semua data render via {{ }}, bukan v-html
 */
import { useI18n } from 'vue-i18n'

export interface Column<T = Record<string, unknown>> {
  key:        string
  label:      string
  sortable?:  boolean
  width?:     string
  align?:     'left' | 'center' | 'right'
  mobileHide?: boolean  // sembunyikan di mobile card view
  format?:    (row: T) => string
}

const props = withDefaults(defineProps<{
  columns:    Column[]
  rows:       Record<string, unknown>[]
  loading?:   boolean
  emptyText?: string
}>(), {
  loading: false,
})

const { t } = useI18n()

const emit = defineEmits<{
  'row-click': [row: Record<string, unknown>]
}>()

function getCellValue(row: Record<string, unknown>, col: Column): string {
  if (col.format) return col.format(row)
  const val = row[col.key]
  if (val === null || val === undefined) return '—'
  return String(val)
}

// Kolom yang tampil di mobile card (bukan actions)
const mobileColumns = props.columns.filter(c => c.key !== '_actions' && !c.mobileHide)
// Kolom actions
const actionsCol = props.columns.find(c => c.key === '_actions' || c.key === 'actions')
</script>

<template>
  <!-- ── Loading ──────────────────────────────────────────── -->
  <div v-if="loading" class="flex items-center justify-center gap-xs py-xxl text-ink-muted border border-hairline">
    <span class="w-4 h-4 border-2 border-primary border-t-transparent rounded-full animate-spin" aria-hidden="true" />
    <span class="type-body-sm">{{ t('common.loading') }}</span>
  </div>

  <!-- ── Empty ────────────────────────────────────────────── -->
  <div v-else-if="!rows.length" class="py-xxl text-center text-ink-muted type-body-sm border border-hairline">
    {{ emptyText ?? t('common.noData') }}
  </div>

  <template v-else>
    <!-- ══ DESKTOP TABLE (>= 672px) ══════════════════════════ -->
    <div class="hidden tablet:block w-full overflow-x-auto border border-hairline">
      <table role="table" class="w-full border-collapse font-sans type-body-sm text-ink">
        <thead class="bg-surface-1 border-b border-hairline">
          <tr>
            <th
              v-for="col in columns"
              :key="col.key"
              :style="col.width ? `width: ${col.width}` : ''"
              :class="[
                'px-sm py-xs text-left type-body-sm font-semibold text-ink',
                'border-r border-hairline last:border-r-0',
                col.align === 'center' && 'text-center',
                col.align === 'right'  && 'text-right',
              ]"
              scope="col"
            >
              {{ col.label }}
            </th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="(row, idx) in rows"
            :key="idx"
            :class="[
              'border-b border-hairline last:border-b-0',
              'hover:bg-surface-1 cursor-pointer transition-colors duration-75',
              idx % 2 === 1 && 'bg-[#fafafa] dark:bg-[#1e1e1e]',
            ]"
            @click="emit('row-click', row)"
          >
            <td
              v-for="col in columns"
              :key="col.key"
              :class="[
                'px-sm py-xs type-body-sm',
                'border-r border-hairline last:border-r-0',
                col.align === 'center' && 'text-center',
                col.align === 'right'  && 'text-right',
              ]"
            >
              <slot :name="`cell-${col.key}`" :row="row" :value="getCellValue(row, col)">
                {{ getCellValue(row, col) }}
              </slot>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- ══ MOBILE CARDS (< 672px) ═════════════════════════════ -->
    <div class="tablet:hidden space-y-xs">
      <div
        v-for="(row, idx) in rows"
        :key="idx"
        class="border border-hairline bg-canvas p-sm cursor-pointer hover:bg-surface-1 transition-colors active:bg-surface-2"
        role="button"
        :tabindex="0"
        @click="emit('row-click', row)"
        @keydown.enter="emit('row-click', row)"
        @keydown.space.prevent="emit('row-click', row)"
      >
        <!-- Top row: first visible column + status/badge -->
        <div class="flex items-start justify-between gap-sm mb-xs">
          <!-- Primary info (first non-action col) -->
          <div class="flex-1 min-w-0">
            <p class="type-body-emphasis text-ink truncate">
              <slot
                :name="`cell-${mobileColumns[0]?.key}`"
                :row="row"
                :value="getCellValue(row, mobileColumns[0])"
              >
                {{ getCellValue(row, mobileColumns[0]) }}
              </slot>
            </p>
            <!-- Second column as subtitle if exists -->
            <p v-if="mobileColumns[1]" class="type-caption text-ink-muted mt-xxs truncate">
              <slot
                :name="`cell-${mobileColumns[1]?.key}`"
                :row="row"
                :value="getCellValue(row, mobileColumns[1])"
              >
                {{ getCellValue(row, mobileColumns[1]) }}
              </slot>
            </p>
          </div>

          <!-- Status/badge column (biasanya kolom terakhir sebelum actions) -->
          <div class="flex-shrink-0">
            <slot
              v-if="mobileColumns[mobileColumns.length - 1]?.key !== mobileColumns[0]?.key"
              :name="`cell-${mobileColumns[mobileColumns.length - 1]?.key}`"
              :row="row"
              :value="getCellValue(row, mobileColumns[mobileColumns.length - 1])"
            >
              <span class="type-caption text-ink-muted">
                {{ getCellValue(row, mobileColumns[mobileColumns.length - 1]) }}
              </span>
            </slot>
          </div>
        </div>

        <!-- Middle rows: remaining columns as key-value pairs -->
        <dl v-if="mobileColumns.length > 2" class="grid grid-cols-2 gap-x-md gap-y-xxs mt-xs border-t border-hairline pt-xs">
          <template v-for="col in mobileColumns.slice(2, -1)" :key="col.key">
            <div class="min-w-0">
              <dt class="type-caption text-ink-subtle">{{ col.label }}</dt>
              <dd class="type-caption text-ink mt-xxs truncate">
                <slot :name="`cell-${col.key}`" :row="row" :value="getCellValue(row, col)">
                  {{ getCellValue(row, col) }}
                </slot>
              </dd>
            </div>
          </template>
        </dl>

        <!-- Actions row -->
        <div
          v-if="actionsCol"
          class="flex items-center justify-end gap-xs mt-xs pt-xs border-t border-hairline"
          @click.stop
        >
          <slot :name="`cell-${actionsCol.key}`" :row="row" :value="''">
            <!-- fallback -->
          </slot>
        </div>
      </div>
    </div>
  </template>
</template>
