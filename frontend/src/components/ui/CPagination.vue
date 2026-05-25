<script setup lang="ts">
/**
 * CPagination — Carbon-style pagination
 * Accessibility: aria-label, aria-current
 */
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

const props = defineProps<{
  page:     number
  pages:    number
  total:    number
  perPage:  number
}>()

const emit = defineEmits<{ 'update:page': [page: number] }>()

const visiblePages = computed(() => {
  const range: (number | '...')[] = []
  const delta = 2
  for (let i = 1; i <= props.pages; i++) {
    if (
      i === 1 || i === props.pages ||
      (i >= props.page - delta && i <= props.page + delta)
    ) {
      range.push(i)
    } else if (range[range.length - 1] !== '...') {
      range.push('...')
    }
  }
  return range
})

const from = computed(() => (props.page - 1) * props.perPage + 1)
const to   = computed(() => Math.min(props.page * props.perPage, props.total))
</script>

<template>
  <div class="flex flex-col mobile:flex-row mobile:items-center mobile:justify-between gap-xs py-sm font-sans">
    <!-- Info -->
    <span class="type-body-sm text-ink-muted">
      {{ t('pagination.info', { from, to, total }) }}
    </span>

    <!-- Pages -->
    <nav aria-label="Pagination" class="flex items-center gap-xxs">
      <!-- Prev -->
      <button
        :disabled="page <= 1"
        class="h-8 px-sm type-body-sm text-ink border border-hairline rounded-none hover:bg-surface-1 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
        aria-label="Previous page"
        @click="emit('update:page', page - 1)"
      >
        ‹
      </button>

      <!-- Page numbers -->
      <template v-for="p in visiblePages" :key="p">
        <span v-if="p === '...'" class="px-xs type-body-sm text-ink-muted">…</span>
        <button
          v-else
          :aria-current="p === page ? 'page' : undefined"
          :class="[
            'h-8 px-sm type-body-sm border rounded-none transition-colors',
            p === page
              ? 'bg-primary text-on-primary border-primary'
              : 'text-ink border-hairline hover:bg-surface-1',
          ]"
          @click="emit('update:page', p as number)"
        >
          {{ p }}
        </button>
      </template>

      <!-- Next -->
      <button
        :disabled="page >= pages"
        class="h-8 px-sm type-body-sm text-ink border border-hairline rounded-none hover:bg-surface-1 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
        aria-label="Next page"
        @click="emit('update:page', page + 1)"
      >
        ›
      </button>
    </nav>
  </div>
</template>
