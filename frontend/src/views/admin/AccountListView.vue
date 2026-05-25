<script setup lang="ts">
/**
 * AccountListView — manajemen akun user
 * Security:
 * - Password tidak pernah ditampilkan
 * - Password strength validation via Zod
 * - Tidak bisa hapus/deactivate diri sendiri (dihandle backend, UI juga hide tombol)
 */
import { ref, onMounted } from 'vue'
import { z } from 'zod'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '@/stores/auth'
import { useCrud } from '@/composables/useCrud'
import { useForm } from '@/composables/useForm'
import MasterListView  from '@/components/master/MasterListView.vue'
import MasterFormModal from '@/components/master/MasterFormModal.vue'
import CInput  from '@/components/ui/CInput.vue'
import CSelect from '@/components/ui/CSelect.vue'
import CBadge  from '@/components/ui/CBadge.vue'
import CButton from '@/components/ui/CButton.vue'
import CModal  from '@/components/ui/CModal.vue'
import CNotification from '@/components/ui/CNotification.vue'

interface Account { id: number; username: string; full_name: string; email: string; role_name: string; is_active: boolean; is_locked: boolean }
interface Role    { id: number; name: string }

const auth     = useAuthStore()
const { t }    = useI18n()
const crud     = useCrud<Account>('/accounts')
const roleCrud = useCrud<Role>('/roles')
const listRef  = ref<InstanceType<typeof MasterListView> | null>(null)

const modal      = ref(false)
const editTarget = ref<Account | null>(null)
const roleOptions = ref<{ value: string; label: string }[]>([])

// Password reset modal
const pwModal    = ref(false)
const pwTarget   = ref<Account | null>(null)
const pwError    = ref('')
const pwLoading  = ref(false)

const PasswordSchema = z.object({
  new_password: z.string()
    .min(8, 'Min 8 characters')
    .max(128)
    .regex(/[A-Z]/, 'Must contain uppercase')
    .regex(/\d/, 'Must contain digit')
    .regex(/[^A-Za-z0-9]/, 'Must contain special character'),
})

const CreateSchema = z.object({
  username:  z.string().min(3).max(50).regex(/^[A-Za-z0-9_\.]+$/, 'Invalid characters'),
  email:     z.string().email('Invalid email'),
  full_name: z.string().min(1).max(150),
  role_id:   z.number().int().positive(),
  password:  z.string().min(8).max(128)
    .regex(/[A-Z]/, 'Must contain uppercase')
    .regex(/\d/, 'Must contain digit')
    .regex(/[^A-Za-z0-9]/, 'Must contain special character'),
  is_active: z.boolean().default(true),
})
type CreateForm = z.infer<typeof CreateSchema>
type PwForm     = z.infer<typeof PasswordSchema>

const { values, errors, submitting, setField, handleSubmit, reset } = useForm<CreateForm>(
  CreateSchema, { is_active: true }
)
const pwForm = useForm<PwForm>(PasswordSchema)

const columns = [
  { key: 'username',  label: t('common.username') },
  { key: 'full_name', label: t('common.fullName') },
  { key: 'email',     label: t('common.email') },
  { key: 'role_name', label: t('common.role'),   width: '120px' },
  { key: 'is_active', label: t('common.status'), width: '100px' },
  { key: '_pw',       label: '',                 width: '100px' },
]

onMounted(async () => {
  roleOptions.value = [
    { value: '1', label: t('account.administrator') },
    { value: '2', label: t('account.user') },
  ]
})

function openCreate() { editTarget.value = null; reset({ is_active: true }); modal.value = true }
function openEdit(item: Account) {
  editTarget.value = item
  // Tidak pre-fill password saat edit
  reset({ full_name: item.full_name, email: item.email, is_active: item.is_active })
  modal.value = true
}

async function onSubmit(data: CreateForm) {
  const ok = editTarget.value
    ? await crud.update(editTarget.value.id, { full_name: data.full_name, email: data.email, is_active: data.is_active })
    : await crud.create(data)
  if (ok) { modal.value = false; listRef.value?.load() }
}

function openPwReset(item: Account, e: Event) {
  e.stopPropagation()
  pwTarget.value = item
  pwForm.reset()
  pwError.value  = ''
  pwModal.value  = true
}

async function handlePwReset(data: PwForm) {
  if (!pwTarget.value) return
  pwLoading.value = true
  try {
    const { api } = await import('@/lib/api')
    await api.post(`/accounts/${pwTarget.value.id}/reset-password`, data)
    pwModal.value = false
  } catch (err: unknown) {
    pwError.value = err instanceof Error ? err.message : t('account.failedReset')
  } finally {
    pwLoading.value = false
    pwForm.values.new_password = '' // clear dari memory
  }
}
</script>

<template>
  <MasterListView ref="listRef" :title="t('account.title')" endpoint="/accounts"
    permission-module="account" :columns="columns"
    :on-create-click="openCreate" :on-edit-click="openEdit">

    <template #cell-is_active="{ row }">
      <div class="flex items-center gap-xs">
        <CBadge :variant="(row as Account).is_active ? 'success' : 'neutral'" dot>
          {{ (row as Account).is_active ? t('common.active') : t('common.inactive') }}
        </CBadge>
        <CBadge v-if="(row as Account).is_locked" variant="error">{{ t('common.locked') }}</CBadge>
      </div>
    </template>

    <template #cell-_pw="{ row }">
      <CButton
        v-if="auth.hasPermission('account:update') && (row as Account).id !== auth.user?.id"
        variant="ghost"
        size="sm"
        @click="openPwReset(row as Account, $event)"
      >
        {{ t('account.resetPw') }}
      </CButton>
    </template>
  </MasterListView>

  <!-- Create/Edit modal -->
  <MasterFormModal :open="modal" :title="editTarget ? t('account.editTitle') : t('account.createTitle')"
    :submitting="submitting || crud.loading.value"
    @close="modal = false" @submit="handleSubmit(onSubmit)">
    <template v-if="!editTarget">
      <CInput :model-value="values.username || ''" :label="t('common.username')" required :error="errors.username"
        autocomplete="username" @update:model-value="setField('username', $event as string)" />
      <CInput :model-value="values.password || ''" :label="t('common.password')" type="password" required :error="errors.password"
        autocomplete="new-password" @update:model-value="setField('password', $event as string)" />
      <CSelect :model-value="String(values.role_id || '')" :label="t('common.role')" required
        :options="roleOptions" :error="String(errors.role_id || '')"
        @update:model-value="setField('role_id', Number($event))" />
    </template>
    <CInput :model-value="values.full_name || ''" :label="t('common.fullName')" required :error="errors.full_name"
      autocomplete="name" @update:model-value="setField('full_name', $event as string)" />
    <CInput :model-value="values.email || ''" :label="t('common.email')" type="email" required :error="errors.email"
      autocomplete="email" @update:model-value="setField('email', $event as string)" />
  </MasterFormModal>

  <!-- Password reset modal -->
  <CModal :open="pwModal" :title="t('account.resetPwTitle')" size="sm" @close="pwModal = false">
    <p class="type-body-sm text-ink-muted mb-lg">
      {{ t('account.resetPwFor', { username: pwTarget?.username }) }}
    </p>
    <CNotification v-if="pwError" kind="error" :message="pwError" class="mb-md" @close="pwError = ''" />
    <CInput
      :model-value="pwForm.values.new_password || ''"
      :label="t('account.newPassword')"
      type="password"
      required
      :error="pwForm.errors.new_password"
      autocomplete="new-password"
      @update:model-value="pwForm.setField('new_password', $event as string)"
    />
    <template #footer>
      <CButton variant="ghost" @click="pwModal = false">{{ t('common.cancel') }}</CButton>
      <CButton variant="primary" :loading="pwLoading"
        @click="pwForm.handleSubmit(handlePwReset)">
        {{ t('account.resetPwTitle') }}
      </CButton>
    </template>
  </CModal>
</template>
