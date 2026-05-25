/**
 * IAMS Frontend — Entry point
 * IBM Plex Sans di-load via @fontsource (self-hosted, tidak ada CDN eksternal)
 * Ini penting untuk CSP ketat — tidak perlu whitelist fonts.googleapis.com
 */
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { createI18n } from 'vue-i18n'

import App from './App.vue'
import router from './router'
import en from './locales/en.json'
import id from './locales/id.json'

// CSS utama — includes @fontsource IBM Plex Sans + Tailwind + Carbon tokens
import './assets/index.css'

const i18n = createI18n({
  legacy: false,
  locale: localStorage.getItem('locale') || 'id',
  fallbackLocale: 'en',
  messages: { en, id },
})

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.use(i18n)

app.mount('#app')
