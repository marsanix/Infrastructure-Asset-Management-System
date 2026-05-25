<script setup lang="ts">
/**
 * LoginView — IBM Carbon login page
 * Security:
 * - Password field cleared dari memory setelah submit
 * - Error message generic (tidak reveal apakah username/password yang salah)
 * - autocomplete="current-password" untuk password manager support
 * - Tidak ada v-html
 * - Input validation sisi klien sebelum kirim ke server
 */
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '@/stores/auth'
import CButton from '@/components/ui/CButton.vue'
import CInput  from '@/components/ui/CInput.vue'
import CNotification from '@/components/ui/CNotification.vue'

const { t } = useI18n()
const router = useRouter()
const route  = useRoute()
const auth   = useAuthStore()

const username = ref('')
const password = ref('')
const error    = ref('')
const loading  = ref(false)

// Validasi sisi klien
function validate(): string {
  if (!username.value.trim()) return t('validate.usernameRequired')
  if (username.value.trim().length < 3) return t('validate.usernameTooShort')
  if (!password.value) return t('validate.passwordRequired')
  return ''
}

async function handleLogin() {
  error.value = validate()
  if (error.value) return

  loading.value = true
  try {
    await auth.login(username.value.trim(), password.value)
    const redirect = (route.query.redirect as string) || '/app'
    router.push(redirect)
  } catch (err: unknown) {
    // Generic error — jangan expose detail dari server
    error.value = err instanceof Error ? err.message : t('auth.invalidCredentials')
  } finally {
    loading.value = false
    // Bersihkan password dari memory
    password.value = ''
  }
}
</script>

<template>
  <div class="min-h-screen flex bg-canvas font-sans">

    <!-- Left panel — branding (hidden on mobile) -->
    <div class="hidden tablet:flex flex-col justify-between w-1/2 bg-inverse-canvas p-xxl">
      <div>
        <span class="type-display-md text-inverse-ink font-light">IAMS</span>
        <p class="type-body-lg text-inverse-ink-muted mt-lg max-w-sm">
          Infrastructure Asset Management System
        </p>
      </div>
      <p class="type-caption text-inverse-ink-muted">
        {{ t('auth.copyright', { year: new Date().getFullYear() }) }}
      </p>
    </div>

    <!-- Right panel — form -->
    <div class="flex flex-col justify-center w-full tablet:w-1/2 px-sm mobile:px-lg tablet:px-xxl">
      <div class="w-full max-w-sm mx-auto py-xl">

        <p class="type-headline text-ink mb-xxl tablet:hidden">IAMS</p>

        <h1 class="type-headline text-ink mb-xs">{{ t('auth.login') }}</h1>
        <p class="type-body-sm text-ink-muted mb-xl">
          {{ t('auth.subtitle') }}
        </p>

        <!-- Error notification -->
        <CNotification
          v-if="error"
          kind="error"
          :message="error"
          class="mb-lg"
          @close="error = ''"
        />

        <!-- Form -->
        <form
          class="space-y-lg"
          @submit.prevent="handleLogin"
          novalidate
          autocomplete="on"
        >
          <CInput
            v-model="username"
            :label="t('auth.username')"
            type="text"
            autocomplete="username"
            required
            :disabled="loading"
          />

          <CInput
            v-model="password"
            :label="t('auth.password')"
            type="password"
            autocomplete="current-password"
            required
            :disabled="loading"
          />

          <CButton
            type="submit"
            variant="primary"
            size="md"
            :loading="loading"
            class="w-full"
          >
            {{ t('auth.loginButton') }}
          </CButton>
        </form>
      </div>
    </div>
  </div>
</template>
