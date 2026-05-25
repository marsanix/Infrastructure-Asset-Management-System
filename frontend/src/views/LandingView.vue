<script setup lang="ts">
import { useRouter } from 'vue-router'
import Meteors        from '@/components/inspira/Meteors.vue'
import SparklesCore   from '@/components/inspira/SparklesCore.vue'
import ShimmerButton  from '@/components/inspira/ShimmerButton.vue'
import NumberTicker   from '@/components/inspira/NumberTicker.vue'
import BorderBeam     from '@/components/inspira/BorderBeam.vue'
import GradientText   from '@/components/inspira/GradientText.vue'
import TextReveal     from '@/components/inspira/TextReveal.vue'

const router = useRouter()
function goLogin() { router.push('/login') }

const stats = [
  { n: 16,   suffix: '',     label: 'Tabel Database' },
  { n: 50,   suffix: '+',    label: 'API Endpoint' },
  { n: 2025, suffix: '',     label: 'OWASP Top 10' },
  { n: 256,  suffix: '-bit', label: 'AES Enkripsi' },
]

const features = [
  { icon: 'DB', accent: '#4589ff', title: 'Inventaris Aset',     desc: 'Server, switch, router, firewall, AP, printer — semua dalam satu tampilan. Lengkap dengan lokasi, penanggung jawab, dan riwayat.' },
  { icon: 'SH', accent: '#a56eff', title: 'Kredensial Aman',     desc: 'Password perangkat dienkripsi AES-256. Setiap akses selalu tercatat di audit log immutable.' },
  { icon: 'IN', accent: '#f1c21b', title: 'Manajemen Insiden',   desc: 'Tangani insiden IT dengan alur terstruktur. State machine mencegah perubahan status yang tidak valid.' },
  { icon: 'CH', accent: '#24a148', title: 'Change & Request',    desc: 'Alur persetujuan yang jelas. Tidak ada perubahan tanpa otorisasi dan jejak audit yang tercatat.' },
  { icon: 'RB', accent: '#da1e28', title: 'RBAC Granular',       desc: '52 permission berbeda. Setiap pengguna hanya bisa melakukan apa yang menjadi wewenangnya.' },
  { icon: 'RP', accent: '#4589ff', title: 'Laporan & Ekspor',    desc: 'Filter multi-kriteria. Ekspor ke CSV dan Excel. Formula injection prevention sudah built-in.' },
]

const steps = [
  { n: '01', t: 'Daftarkan aset',       d: 'Masukkan perangkat IT lengkap dengan lokasi, penanggung jawab, dan spesifikasi.' },
  { n: '02', t: 'Atur akses tim',        d: 'Tetapkan role untuk setiap anggota. Kontrol siapa yang bisa melihat dan melakukan apa.' },
  { n: '03', t: 'Pantau dan laporkan',   d: 'Dashboard real-time. Ekspor laporan kapan saja untuk keperluan audit.' },
]

const securityItems = [
  { abbr: 'AES', t: 'AES-256 Encryption',    d: 'Kredensial perangkat dienkripsi. Password user di-hash bcrypt cost-12.' },
  { abbr: 'BF',  t: 'Proteksi Brute-Force',  d: 'Login dibatasi. Akun terkunci otomatis setelah 5 percobaan gagal.' },
  { abbr: 'JWT', t: 'JWT + Refresh Token',    d: 'Access token 15 menit di memory. Redis blacklist saat logout.' },
  { abbr: 'LOG', t: 'Audit Log Immutable',    d: 'Setiap CREATE/UPDATE/DELETE/LOGIN dicatat permanen, tidak bisa diubah.' },
  { abbr: 'VAL', t: 'Input Validation',       d: 'Setiap input divalidasi. Mass assignment dan SQL injection dicegah.' },
  { abbr: '52P', t: '52 Permissions',         d: 'RBAC granular per modul. @require_permission di setiap endpoint.' },
]

const mockStats = [
  { l: 'Aktif',    v: '142', c: '#24a148' },
  { l: 'Tersedia', v: '38',  c: '#4589ff' },
  { l: 'Perbaikan',v: '7',   c: '#f1c21b' },
  { l: 'Total',    v: '187', c: '#ffffff' },
]

const mockRows = [
  { color: 'border-[#24a148]/40 text-[#24a148] bg-[#24a148]/10', status: 'Aktif' },
  { color: 'border-[#4589ff]/40 text-[#4589ff] bg-[#4589ff]/10', status: 'Tersedia' },
  { color: 'border-[#f1c21b]/40 text-[#f1c21b] bg-[#f1c21b]/10', status: 'Perbaikan' },
  { color: 'border-[#24a148]/40 text-[#24a148] bg-[#24a148]/10', status: 'Aktif' },
]

const sidebarWidths = [70, 55, 65, 60, 50, 70, 55]
const rowWidths     = [65, 80, 55, 70]
</script>

<template>
  <div class="min-h-screen bg-[#080808] text-white font-sans overflow-x-hidden">

    <!-- ── Navbar ────────────────────────────────────────── -->
    <header class="relative z-20 flex items-center justify-between px-6 tablet:px-12 h-16 border-b border-white/[0.06] backdrop-blur-sm bg-[#080808]/80">
      <div class="flex items-center gap-2">
        <div class="w-7 h-7 bg-[#0f62fe] flex items-center justify-center">
          <svg width="14" height="14" viewBox="0 0 14 14" fill="none" aria-hidden="true">
            <rect x="1" y="1" width="5" height="5" fill="white"/>
            <rect x="8" y="1" width="5" height="5" fill="white" opacity="0.6"/>
            <rect x="1" y="8" width="5" height="5" fill="white" opacity="0.6"/>
            <rect x="8" y="8" width="5" height="5" fill="white"/>
          </svg>
        </div>
        <span class="text-sm font-semibold tracking-tight">IAMS</span>
      </div>

      <nav class="hidden tablet:flex items-center gap-8 absolute left-1/2 -translate-x-1/2">
        <a href="#features"  class="text-sm text-white/50 hover:text-white transition-colors">Fitur</a>
        <a href="#how"       class="text-sm text-white/50 hover:text-white transition-colors">Cara Kerja</a>
        <a href="#security"  class="text-sm text-white/50 hover:text-white transition-colors">Keamanan</a>
      </nav>

      <ShimmerButton
        shimmer-color="#ffffff"
        shimmer-duration="2.5s"
        background="radial-gradient(ellipse at top, #0f62fe, #002d9c)"
        class="px-4 py-2 text-sm"
        @click="goLogin"
      >
        Masuk →
      </ShimmerButton>
    </header>

    <!-- ── Hero ─────────────────────────────────────────── -->
    <section class="relative z-10 flex flex-col items-center text-center px-6 pt-24 pb-20 tablet:pt-32 tablet:pb-28 overflow-hidden">

      <!-- Sparkles background -->
      <div class="absolute inset-0 pointer-events-none" aria-hidden="true">
        <SparklesCore
          id="hero-sparkles"
          background="transparent"
          :min-size="0.4"
          :max-size="1.2"
          :particle-density="80"
          particle-color="#4589ff"
          class="w-full h-full"
        />
      </div>

      <!-- Meteors -->
      <div class="absolute inset-0 overflow-hidden pointer-events-none" aria-hidden="true">
        <Meteors :number="12" />
      </div>

      <!-- Ambient glow -->
      <div class="absolute top-0 left-1/2 -translate-x-1/2 w-[600px] h-[300px] pointer-events-none opacity-30" aria-hidden="true"
        style="background: radial-gradient(ellipse, #0f62fe 0%, transparent 70%); filter: blur(60px);" />

      <!-- Badge -->
      <div class="relative inline-flex items-center gap-2 px-3 py-1 mb-8 border border-white/10 bg-white/[0.04] text-xs text-white/60 uppercase tracking-widest">
        <span class="w-1.5 h-1.5 rounded-full bg-[#24a148] animate-pulse" aria-hidden="true"/>
        IT Asset Management System
      </div>

      <!-- Main headline -->
      <h1 class="relative max-w-4xl text-4xl tablet:text-6xl desktop:text-7xl font-light leading-[1.08] tracking-tight mb-6">
        Kelola infrastruktur IT kamu
        <br class="hidden tablet:block" />
        <GradientText
          :colors="['#ffffff', '#78a9ff', '#0f62fe', '#a56eff', '#ffffff']"
          :animation-speed="6"
          class="text-4xl tablet:text-6xl desktop:text-7xl font-light"
        >
          dalam satu platform.
        </GradientText>
      </h1>

      <!-- Subhead with text reveal -->
      <TextReveal
        text="Inventaris aset, kredensial perangkat terenkripsi, ITSM workflow, dan audit log — semua terpusat, aman, dan siap diaudit."
        class="max-w-xl text-base tablet:text-lg text-white/50 leading-relaxed mb-10 justify-center"
      />

      <!-- CTA buttons -->
      <div class="relative flex flex-wrap items-center justify-center gap-3">
        <ShimmerButton
          shimmer-color="#ffffff"
          shimmer-duration="3s"
          background="radial-gradient(ellipse at top, #0f62fe, #002d9c)"
          class="px-6 py-3 text-sm font-medium"
          @click="goLogin"
        >
          Mulai sekarang →
        </ShimmerButton>
        <a
          href="#features"
          class="flex items-center gap-2 px-6 py-3 text-sm font-medium text-white/70 hover:text-white border border-white/10 hover:border-white/20 transition-colors"
        >
          Lihat fitur
        </a>
      </div>

      <!-- Dashboard mockup with BorderBeam -->
      <div class="relative mt-20 w-full max-w-5xl mx-auto">
        <div class="absolute -inset-4 opacity-25 pointer-events-none"
          style="background: radial-gradient(ellipse at center bottom, #0f62fe 0%, transparent 70%); filter: blur(40px);" aria-hidden="true"/>

        <div class="relative border border-white/[0.08] bg-[#111111] overflow-hidden">
          <!-- BorderBeam animation on mockup -->
          <BorderBeam :size="300" :duration="12" color-from="#0f62fe" color-to="#a56eff" :border-width="1.5" />

          <!-- Fake browser chrome -->
          <div class="flex items-center gap-1.5 px-4 h-9 border-b border-white/[0.06] bg-[#0d0d0d]">
            <div class="w-2.5 h-2.5 rounded-full bg-[#da1e28]" aria-hidden="true"/>
            <div class="w-2.5 h-2.5 rounded-full bg-[#f1c21b]" aria-hidden="true"/>
            <div class="w-2.5 h-2.5 rounded-full bg-[#24a148]" aria-hidden="true"/>
            <div class="flex-1 mx-4 h-5 bg-white/[0.05] flex items-center justify-center">
              <span class="text-[10px] text-white/30">iams.local — Dashboard</span>
            </div>
          </div>

          <!-- Fake app UI -->
          <div class="flex h-64 tablet:h-72">
            <!-- Sidebar -->
            <div class="hidden tablet:flex flex-col w-44 border-r border-white/[0.06] bg-[#0d0d0d] p-3 gap-1">
              <div class="h-7 bg-[#0f62fe]/80 px-3 flex items-center">
                <div class="h-2 w-20 bg-white/60" aria-hidden="true"/>
              </div>
              <div v-for="(w, i) in sidebarWidths" :key="i" class="h-7 px-3 flex items-center">
                <div class="h-1.5 bg-white/20" :style="`width: ${w}%`" aria-hidden="true"/>
              </div>
            </div>
            <!-- Content -->
            <div class="flex-1 p-4 tablet:p-5 overflow-hidden">
              <div class="grid grid-cols-2 tablet:grid-cols-4 gap-2 mb-4">
                <div v-for="s in mockStats" :key="s.l" class="bg-white/[0.03] border border-white/[0.06] p-2.5">
                  <p class="text-[9px] text-white/40 mb-1">{{ s.l }}</p>
                  <p class="text-xl font-light" :style="`color:${s.c}`">{{ s.v }}</p>
                </div>
              </div>
              <div class="border border-white/[0.06]">
                <div class="flex h-7 border-b border-white/[0.06] bg-white/[0.02]">
                  <div v-for="(wc, j) in ['w-24','flex-1','w-20','w-24']" :key="j" :class="`${wc} px-3 flex items-center`">
                    <div class="h-1.5 bg-white/20 w-3/4" aria-hidden="true"/>
                  </div>
                </div>
                <div v-for="(row, j) in mockRows" :key="j" class="flex h-8 border-b border-white/[0.04] last:border-b-0" :class="j%2===0?'':'bg-white/[0.01]'">
                  <div class="w-24 px-3 flex items-center"><div class="h-1.5 bg-[#4589ff]/60 w-20" aria-hidden="true"/></div>
                  <div class="flex-1 px-3 flex items-center"><div class="h-1.5 bg-white/15" :style="`width:${rowWidths[j]}%`" aria-hidden="true"/></div>
                  <div class="w-20 px-3 flex items-center">
                    <span class="text-[9px] px-1.5 py-0.5 border" :class="row.color">{{ row.status }}</span>
                  </div>
                  <div class="w-24 px-3 flex items-center"><div class="h-1.5 bg-white/10 w-16" aria-hidden="true"/></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ── Stats strip with NumberTicker ──────────────────── -->
    <section class="relative z-10 border-y border-white/[0.06]" aria-label="Key numbers">
      <div class="max-w-4xl mx-auto px-6 grid grid-cols-2 tablet:grid-cols-4 divide-x divide-white/[0.06]">
        <div v-for="s in stats" :key="s.label" class="py-8 text-center">
          <p class="text-3xl font-light text-white mb-1">
            <NumberTicker :value="s.n" :delay="0.2" />{{ s.suffix }}
          </p>
          <p class="text-xs text-white/40 uppercase tracking-wider">{{ s.label }}</p>
        </div>
      </div>
    </section>

    <!-- ── Features ──────────────────────────────────────── -->
    <section id="features" class="relative z-10 px-6 tablet:px-12 py-24 max-w-6xl mx-auto">
      <div class="text-center mb-16">
        <p class="text-xs text-[#4589ff] uppercase tracking-widest mb-3">Fitur</p>
        <h2 class="text-3xl tablet:text-4xl font-light text-white">
          Semua yang tim IT kamu butuhkan.
        </h2>
      </div>

      <div class="grid grid-cols-1 tablet:grid-cols-2 desktop:grid-cols-3 gap-3">
        <div
          v-for="feat in features"
          :key="feat.title"
          class="group relative bg-[#0d0d0d] border border-white/[0.07] p-6 hover:border-white/[0.15] transition-all duration-300 overflow-hidden"
        >
          <BorderBeam
            :size="150"
            :duration="8"
            :color-from="feat.accent"
            color-to="#ffffff"
            :border-width="1"
            class="opacity-0 group-hover:opacity-100 transition-opacity duration-500"
          />
          <!-- Icon badge -->
          <div
            class="inline-flex items-center justify-center w-9 h-9 text-xs font-bold mb-4 border"
            :style="{ borderColor: feat.accent + '40', color: feat.accent, background: feat.accent + '15' }"
            aria-hidden="true"
          >
            {{ feat.icon }}
          </div>
          <h3 class="text-sm font-semibold text-white mb-2">{{ feat.title }}</h3>
          <p class="text-xs text-white/40 leading-relaxed">{{ feat.desc }}</p>
        </div>
      </div>
    </section>

    <!-- ── How it works ───────────────────────────────────── -->
    <section id="how" class="relative z-10 border-t border-white/[0.06] px-6 tablet:px-12 py-24 max-w-6xl mx-auto">
      <div class="text-center mb-16">
        <p class="text-xs text-[#4589ff] uppercase tracking-widest mb-3">Cara Kerja</p>
        <h2 class="text-3xl tablet:text-4xl font-light text-white">Mulai dalam 3 langkah.</h2>
      </div>

      <div class="grid grid-cols-1 tablet:grid-cols-3 gap-px bg-white/[0.06]">
        <div
          v-for="step in steps"
          :key="step.n"
          class="bg-[#080808] p-8 hover:bg-[#0d0d0d] transition-colors"
        >
          <p class="text-5xl font-light text-white/10 mb-6 select-none tabular-nums" aria-hidden="true">{{ step.n }}</p>
          <h3 class="text-sm font-semibold text-white mb-3">{{ step.t }}</h3>
          <p class="text-xs text-white/40 leading-relaxed">{{ step.d }}</p>
        </div>
      </div>
    </section>

    <!-- ── Security ───────────────────────────────────────── -->
    <section id="security" class="relative z-10 border-t border-white/[0.06] px-6 tablet:px-12 py-24 overflow-hidden">
      <div class="absolute inset-0 pointer-events-none" aria-hidden="true">
        <SparklesCore
          id="security-sparkles"
          background="transparent"
          :min-size="0.2"
          :max-size="0.8"
          :particle-density="30"
          particle-color="#0f62fe"
          class="w-full h-full opacity-40"
        />
      </div>

      <div class="relative max-w-6xl mx-auto">
        <div class="text-center mb-16">
          <p class="text-xs text-[#4589ff] uppercase tracking-widest mb-3">Keamanan</p>
          <h2 class="text-3xl tablet:text-4xl font-light text-white mb-4">Keamanan dibangun dari fondasinya.</h2>
          <p class="text-sm text-white/45 max-w-xl mx-auto">
            Setiap endpoint, setiap input, setiap akses — divalidasi, dibatasi, dan dicatat.
            Sesuai standar <span class="text-white/70">OWASP Top 10:2025</span>.
          </p>
        </div>

        <div class="grid grid-cols-1 tablet:grid-cols-2 desktop:grid-cols-3 gap-3">
          <div
            v-for="item in securityItems"
            :key="item.t"
            class="bg-[#0d0d0d]/80 border border-white/[0.07] p-5 backdrop-blur-sm"
          >
            <div class="inline-flex items-center justify-center w-8 h-8 text-xs font-bold text-[#4589ff] border border-[#4589ff]/30 bg-[#4589ff]/10 mb-3" aria-hidden="true">
              {{ item.abbr }}
            </div>
            <h3 class="text-sm font-semibold text-white mb-2">{{ item.t }}</h3>
            <p class="text-xs text-white/40 leading-relaxed">{{ item.d }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- ── CTA ────────────────────────────────────────────── -->
    <section class="relative z-10 border-t border-white/[0.06] px-6 py-24 text-center overflow-hidden">
      <div class="absolute inset-0 pointer-events-none" aria-hidden="true"
        style="background: radial-gradient(ellipse at center, #0f62fe12 0%, transparent 60%);" />

      <!-- Meteors in CTA -->
      <div class="absolute inset-0 overflow-hidden pointer-events-none" aria-hidden="true">
        <Meteors :number="8" />
      </div>

      <p class="relative text-xs text-[#4589ff] uppercase tracking-widest mb-4">Siap mulai?</p>
      <h2 class="relative text-3xl tablet:text-5xl font-light text-white mb-4">
        Ambil kendali atas<br />infrastruktur IT kamu.
      </h2>
      <p class="relative text-sm text-white/45 mb-10 max-w-md mx-auto">
        Mulai kelola aset, kredensial, dan workflow ITSM tim IT kamu hari ini.
      </p>
      <div class="relative flex justify-center">
        <ShimmerButton
          shimmer-color="#ffffff"
          shimmer-duration="2s"
          background="radial-gradient(ellipse at top, #0f62fe, #002d9c)"
          class="px-8 py-4 text-sm font-medium"
          @click="goLogin"
        >
          Masuk ke IAMS →
        </ShimmerButton>
      </div>
    </section>

    <!-- ── Footer ─────────────────────────────────────────── -->
    <footer class="relative z-10 border-t border-white/[0.06] px-6 tablet:px-12 py-8">
      <div class="max-w-6xl mx-auto flex flex-col tablet:flex-row items-center justify-between gap-4">
        <div class="flex items-center gap-2">
          <div class="w-5 h-5 bg-[#0f62fe] flex items-center justify-center">
            <svg width="10" height="10" viewBox="0 0 14 14" fill="none" aria-hidden="true">
              <rect x="1" y="1" width="5" height="5" fill="white"/>
              <rect x="8" y="1" width="5" height="5" fill="white" opacity="0.6"/>
              <rect x="1" y="8" width="5" height="5" fill="white" opacity="0.6"/>
              <rect x="8" y="8" width="5" height="5" fill="white"/>
            </svg>
          </div>
          <span class="text-xs text-white/30">IAMS — Proyek Magang {{ new Date().getFullYear() }}</span>
        </div>
        <div class="flex items-center gap-6">
          <span class="text-xs text-white/20">OWASP Top 10:2025</span>
          <span class="text-xs text-white/20">ITIL ITSM</span>
          <span class="text-xs text-white/20">AES-256 Encrypted</span>
        </div>
      </div>
    </footer>

  </div>
</template>
