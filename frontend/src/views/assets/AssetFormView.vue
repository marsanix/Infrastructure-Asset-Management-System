<script setup lang="ts">
/**
 * AssetFormView — Create & Edit asset
 * Security:
 * - Zod schema validation sebelum submit (runtime type safety)
 * - Tidak ada v-html
 * - Field yang dikirim ke API hanya yang ada di schema (no extra fields)
 * - Edit mode: fetch data fresh dari server, bukan dari client state
 */
import { onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useAssets } from '@/composables/useAssets'
import { useForm } from '@/composables/useForm'
import { AssetSchema, ASSET_STATUS_OPTIONS } from '@/types/asset'
import type { AssetFormData } from '@/types/asset'
import CButton       from '@/components/ui/CButton.vue'
import CInput        from '@/components/ui/CInput.vue'
import CSelect       from '@/components/ui/CSelect.vue'
import CCard         from '@/components/ui/CCard.vue'
import CNotification from '@/components/ui/CNotification.vue'
import { api } from '@/lib/api'
import { ref } from 'vue'

const { t }  = useI18n()
const router = useRouter()
const route  = useRoute()

const { createAsset, updateAsset, fetchAsset, asset, loading, error } = useAssets()

const isEdit  = computed(() => !!route.params.id)
const assetId = computed(() => Number(route.params.id))

// ── Dropdown options (loaded from API) ────────────────────────
const modelOptions    = ref<{ value: number; label: string }[]>([])
const locationOptions = ref<{ value: number; label: string }[]>([])
const employeeOptions = ref<{ value: number; label: string }[]>([])

async function loadOptions() {
  const [models, locations, employees] = await Promise.all([
    api.get('/models?per_page=200'),
    api.get('/locations?per_page=200'),
    api.get('/employees?per_page=200'),
  ])
  modelOptions.value    = (models.data.data    || []).map((m: { id: number; name: string }) => ({ value: m.id, label: m.name }))
  locationOptions.value = (locations.data.data || []).map((l: { id: number; name: string }) => ({ value: l.id, label: l.name }))
  employeeOptions.value = [
    { value: 0, label: 'Unassigned' },
    ...(employees.data.data || []).map((e: { id: number; name: string }) => ({ value: e.id, label: e.name })),
  ]
}

// ── Form ──────────────────────────────────────────────────────
const { values, errors, submitting, setField, handleSubmit, reset } = useForm<AssetFormData>(
  AssetSchema,
  { status: 'Available' }
)

onMounted(async () => {
  await loadOptions()
  if (isEdit.value) {
    await fetchAsset(assetId.value)
    if (asset.value) {
      reset({
        asset_tag:       asset.value.asset_tag,
        serial_number:   asset.value.serial_number,
        po_number:       asset.value.po_number ?? undefined,
        model_id:        asset.value.model_id,
        location_id:     asset.value.location_id,
        employee_id:     asset.value.employee_id ?? undefined,
        status:          asset.value.status,
        purchase_date:   asset.value.purchase_date ?? undefined,
        warranty_months: asset.value.warranty_months ?? undefined,
        os_license:      asset.value.os_license ?? undefined,
        notes:           asset.value.notes ?? undefined,
      })
    }
  }
})

async function onSubmit(data: AssetFormData) {
  // Bersihkan field kosong sebelum kirim
  const payload: Partial<AssetFormData> = Object.fromEntries(
    Object.entries(data).filter(([, v]) => v !== '' && v !== undefined)
  )
  // employee_id = 0 artinya unassigned
  if (payload.employee_id === 0) payload.employee_id = undefined

  let result
  if (isEdit.value) {
    result = await updateAsset(assetId.value, payload)
  } else {
    result = await createAsset(payload)
  }

  if (result) {
    router.push(`/app/assets/${result.id}`)
  }
}
</script>

<template>
  <div class="p-sm tablet:p-lg max-w-carbon font-sans">

    <!-- Page header -->
    <div class="flex items-center gap-sm mb-lg border-b border-hairline pb-md">
      <button class="type-body-sm text-primary hover:underline flex-shrink-0" @click="router.push('/app/assets')">
        {{ t('assetForm.backToAssets') }}
      </button>
      <span class="text-hairline">|</span>
      <h1 class="type-subhead text-ink truncate">
        {{ isEdit ? t('assetForm.editTitle') : t('assetForm.createTitle') }}
      </h1>
    </div>

    <!-- Error -->
    <CNotification v-if="error" kind="error" :message="error" class="mb-lg" @close="() => {}" />

    <form @submit.prevent="handleSubmit(onSubmit)" novalidate>
      <!-- Desktop: 2/3 + 1/3, Mobile: stack (notes di bawah) -->
      <div class="grid grid-cols-1 desktop:grid-cols-3 gap-lg">

        <!-- Main fields -->
        <div class="desktop:col-span-2 space-y-lg">
          <CCard variant="feature">
            <h2 class="type-body-emphasis text-ink mb-md">{{ t('assetForm.assetInfo') }}</h2>
            <div class="grid grid-cols-1 mobile:grid-cols-2 gap-md tablet:gap-lg">
              <CInput :model-value="values.asset_tag || ''" :label="t('asset.assetTag')"
                required :error="errors.asset_tag" autocomplete="off"
                @update:model-value="setField('asset_tag', $event as string)" />
              <CInput :model-value="values.serial_number || ''" :label="t('asset.serialNumber')"
                required :error="errors.serial_number" autocomplete="off"
                @update:model-value="setField('serial_number', $event as string)" />
              <CInput :model-value="values.po_number || ''" :label="t('asset.poNumber')"
                :error="errors.po_number" autocomplete="off"
                @update:model-value="setField('po_number', $event as string)" />
              <CSelect :model-value="String(values.status || 'Available')" :label="t('asset.status')"
                required :options="ASSET_STATUS_OPTIONS.map(o => ({ value: o.value, label: o.label }))"
                :error="errors.status"
                @update:model-value="setField('status', $event as AssetFormData['status'])" />
              <CSelect :model-value="String(values.model_id || '')" :label="t('asset.model')"
                required :placeholder="t('assetForm.selectModel')"
                :options="modelOptions.map(o => ({ value: String(o.value), label: o.label }))"
                :error="errors.model_id"
                @update:model-value="setField('model_id', Number($event))" />
              <CSelect :model-value="String(values.location_id || '')" :label="t('asset.location')"
                required :placeholder="t('assetForm.selectLocation')"
                :options="locationOptions.map(o => ({ value: String(o.value), label: o.label }))"
                :error="errors.location_id"
                @update:model-value="setField('location_id', Number($event))" />
              <CSelect :model-value="String(values.employee_id || 0)" :label="t('asset.assignedTo')"
                :options="employeeOptions.map(o => ({ value: String(o.value), label: o.label }))"
                :error="errors.employee_id"
                @update:model-value="setField('employee_id', Number($event))" />
            </div>
          </CCard>

          <CCard variant="feature">
            <h2 class="type-body-emphasis text-ink mb-md">{{ t('assetForm.purchaseWarranty') }}</h2>
            <div class="grid grid-cols-1 mobile:grid-cols-2 gap-md tablet:gap-lg">
              <CInput :model-value="values.purchase_date || ''" :label="t('asset.purchaseDate')"
                type="date" :error="errors.purchase_date"
                @update:model-value="setField('purchase_date', $event as string)" />
              <CInput :model-value="String(values.warranty_months || '')" :label="t('asset.warrantyMonths')"
                type="number" :error="errors.warranty_months"
                @update:model-value="setField('warranty_months', $event ? Number($event) : undefined)" />
              <CInput :model-value="values.os_license || ''" :label="t('asset.osLicense')"
                :error="errors.os_license" autocomplete="off"
                @update:model-value="setField('os_license', $event as string)" />
            </div>
          </CCard>
        </div>

        <!-- Notes + Actions -->
        <div class="space-y-lg">
          <CCard variant="elevated">
            <h2 class="type-body-emphasis text-ink mb-md">{{ t('assetForm.notes') }}</h2>
            <div class="flex flex-col gap-xs">
              <label class="type-body-sm text-ink font-medium">{{ t('assetForm.notes') }}</label>
              <textarea
                :value="values.notes || ''"
                rows="5"
                maxlength="2000"
                class="w-full bg-canvas text-ink type-body-sm px-sm py-xs rounded-none border border-hairline focus:border-primary focus:border-2 outline-none resize-y transition-colors duration-100"
                @input="setField('notes', ($event.target as HTMLTextAreaElement).value)"
              />
              <p v-if="errors.notes" class="type-caption text-error">{{ errors.notes }}</p>
            </div>
          </CCard>

          <!-- Sticky actions pada mobile — tempel di bawah layar -->
          <div class="flex flex-col gap-sm sticky bottom-0 bg-canvas border-t border-hairline pt-sm pb-sm desktop:static desktop:border-t-0 desktop:pt-0 desktop:pb-0">
            <CButton type="submit" variant="primary" size="md" :loading="submitting || loading" class="w-full">
              {{ isEdit ? t('common.save') : t('assetForm.createButton') }}
            </CButton>
            <CButton type="button" variant="ghost" size="md" class="w-full" @click="router.push('/app/assets')">
              {{ t('common.cancel') }}
            </CButton>
          </div>
        </div>

      </div>
    </form>
  </div>
</template>
