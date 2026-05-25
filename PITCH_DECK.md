# IAMS — Technical Proposal Deck
## Infrastructure Asset Management System
**Draft Slide Content · 16:9 · 1920×1080px**

---

---

## SLIDE 1 — COVER

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│   [LOGO / IKON SERVER + SHIELD]                             │
│                                                             │
│   Infrastructure Asset                                      │
│   Management System                                         │
│   ─────────────────────────────────────────────────────     │
│   Web-Based IT Asset & Infrastructure Management Platform   │
│                                                             │
│   Shalahuddin · IT Support & Operation Intern               │
│   Stack: Vue 3 · Flask · PostgreSQL · Docker                │
│   2026                                                      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Visual:** Background gelap (IBM Carbon #161616), teks putih, aksen biru IBM (#0F62FE).
Tambahkan ikon server rack / network topology di sisi kanan.

---

---

## SLIDE 2 — LATAR BELAKANG

**Judul:** Tantangan Pengelolaan Aset Infrastruktur IT

**Konten (3 kolom):**

```
📋 Data Tersebar          🔒 Keamanan Lemah         📊 Pelaporan Manual
─────────────────         ─────────────────         ─────────────────
Aset dicatat di           Kredensial perangkat       Laporan dibuat
spreadsheet,              (router, switch,            manual dari
email, atau               firewall) disimpan          berbagai sumber,
catatan fisik             di catatan biasa,           tidak real-time,
yang tidak                tanpa enkripsi,             sulit diaudit
terpusat                  mudah bocor                 dan diverifikasi
```

**Kalimat bawah (bold):**
> Organisasi membutuhkan satu platform terpusat yang aman, terdokumentasi, dan mudah diaudit.

---

---

## SLIDE 3 — PROBLEM STATEMENT

**Judul:** 5 Masalah Utama yang Ingin Diselesaikan

**Format: numbered list dengan ikon**

```
01  📦  Tidak ada inventaris aset yang terpusat dan real-time
        → Sulit tahu jumlah, lokasi, dan status perangkat

02  🔑  Kredensial perangkat jaringan tidak tersimpan aman
        → Password router/switch/firewall berisiko bocor

03  👤  Hak akses pengguna tidak terkontrol
        → Semua orang bisa akses semua data

04  📝  Tidak ada riwayat perubahan yang bisa diaudit
        → Siapa mengubah apa, kapan, tidak tercatat

05  🔄  Proses ITSM (Incident, Change, Request) masih manual
        → Tidak ada alur kerja yang terstandarisasi
```

---

---

## SLIDE 4 — PROPOSED SOLUTION

**Judul:** IAMS — Satu Platform untuk Semua Kebutuhan

**Layout: center dengan 4 poin melingkar di sekitar logo IAMS**

```
                    ┌─────────┐
         Terpusat ──│         │── Aman
                    │  IAMS   │
         Teraudit ──│         │── Terstandarisasi
                    └─────────┘
```

**Deskripsi:**
> IAMS adalah aplikasi web responsive untuk mengelola aset infrastruktur IT secara **terpusat**, **aman**, dan **terdokumentasi** — mulai dari inventaris perangkat, manajemen akses, hingga proses ITSM.

**3 value utama (card):**
```
┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│  Centralized     │  │  Secure Access   │  │  Traceable IT    │
│  Asset Data      │  │  & Credentials   │  │  Operations      │
└──────────────────┘  └──────────────────┘  └──────────────────┘
```

---

---

## SLIDE 5 — FITUR UTAMA

**Judul:** Modul & Fitur Aplikasi

**Format: tabel 2 kolom**

| Modul | Fitur |
|---|---|
| 🖥️ **Dashboard** | Ringkasan status aset, ITSM overview, warranty alert |
| 📦 **Asset Management** | CRUD aset, riwayat perubahan, filter & export |
| 🗂️ **Master Data** | Department, Lokasi, Kategori, Merek, Model |
| 🌐 **Network Management** | IP Address, MAC, VLAN, Hostname per aset |
| 🔐 **Secure Credentials** | Password perangkat terenkripsi AES-256 |
| 👥 **User & Role** | Login/Logout, RBAC, manajemen akun |
| 🔄 **ITSM** | Incident, Change, Problem, Request Management |
| 📊 **Reports** | Laporan aset, export CSV & Excel |
| 📋 **Audit Log** | Riwayat semua aktivitas, immutable |
| 🌍 **Multi-language** | Bahasa Indonesia & English |
| 🎨 **Theme** | Light / Dark / System |

---

---

## SLIDE 6 — ARSITEKTUR SISTEM

**Judul:** System Architecture

**Diagram (buat sebagai visual di Canva/PPT):**

```
┌─────────────────────────────────────────────────────────────┐
│                        USER BROWSER                         │
│                    (Desktop / Tablet / Mobile)              │
└──────────────────────────┬──────────────────────────────────┘
                           │ HTTPS
┌──────────────────────────▼──────────────────────────────────┐
│                     NGINX (Reverse Proxy)                   │
│              TLS 1.3 · Rate Limiting · Security Headers     │
└──────────┬────────────────────────────────┬─────────────────┘
           │                                │
┌──────────▼──────────┐          ┌──────────▼──────────┐
│   FRONTEND          │          │   BACKEND           │
│   Vue 3 + Vite      │  REST    │   Python Flask      │
│   shadcn-vue        │◄────────►│   SQLAlchemy ORM    │
│   Tailwind CSS      │   API    │   JWT Auth          │
│   IBM Plex Sans     │          │   RBAC              │
└─────────────────────┘          └──────────┬──────────┘
                                            │
                          ┌─────────────────┼─────────────────┐
                          │                 │                 │
               ┌──────────▼──────┐ ┌────────▼────────┐       │
               │   PostgreSQL    │ │     Redis       │       │
               │   Database      │ │  Token Blacklist│       │
               │   (16 tables)   │ │  Rate Limiting  │       │
               └─────────────────┘ └─────────────────┘       │
                                                              │
                          ┌───────────────────────────────────┘
                          │
               ┌──────────▼──────────────────────────────────┐
               │           DOCKER COMPOSE                     │
               │   db · backend · frontend · nginx · redis    │
               └─────────────────────────────────────────────┘
```

---

---

## SLIDE 7 — TECHNOLOGY STACK

**Judul:** Technology Stack

**Format: 3 kolom dengan ikon**

```
┌─────────────────────┐  ┌─────────────────────┐  ┌─────────────────────┐
│     FRONTEND        │  │      BACKEND        │  │   INFRASTRUCTURE    │
│─────────────────────│  │─────────────────────│  │─────────────────────│
│ Vue 3 + Vite        │  │ Python Flask 3.1    │  │ Docker + Compose    │
│ TypeScript          │  │ SQLAlchemy ORM      │  │ Nginx 1.27          │
│ Tailwind CSS        │  │ Flask-JWT-Extended  │  │ PostgreSQL 16       │
│ shadcn-vue          │  │ Flask-Limiter       │  │ Redis 7             │
│ IBM Plex Sans       │  │ Flask-Talisman      │  │                     │
│ Zod (validation)    │  │ Marshmallow         │  │                     │
│ Pinia (state)       │  │ bcrypt + Fernet     │  │                     │
│ Vue Router          │  │ openpyxl            │  │                     │
│ vue-i18n            │  │ gunicorn            │  │                     │
└─────────────────────┘  └─────────────────────┘  └─────────────────────┘
```

**Catatan bawah:**
> IBM Plex Sans di-host secara lokal (self-hosted via @fontsource) — tidak ada request ke CDN eksternal, mendukung Content Security Policy yang ketat.

---

---

## SLIDE 8 — SECURITY DESIGN

**Judul:** Security as a Core Design Principle

**Quote besar di atas:**
> *"Security is implemented as a core design principle, not as an afterthought."*

**Format: 2 kolom**

```
OWASP Top 10:2025                    Implementasi
─────────────────────────────────    ─────────────────────────────────
A01 Broken Access Control        →   RBAC + @require_permission decorator
A02 Cryptographic Failures       →   TLS 1.3, AES-256 (Fernet), bcrypt-12
A03 Injection                    →   SQLAlchemy ORM, Marshmallow EXCLUDE
A05 Security Misconfiguration    →   Flask-Talisman, Nginx hardening
A07 Authentication Failures      →   Rate limiting, brute-force lockout
A09 Logging Failures             →   Immutable audit log + IP tracking
```

```
Tambahan Security Layer
─────────────────────────────────────────────────────────────
✓ JWT blacklist via Redis (logout invalidation)
✓ State machine validation untuk ITSM workflow
✓ CSV formula injection prevention (export)
✓ Credential reveal endpoint terpisah + selalu di-audit
✓ Soft delete — data tidak hilang permanen
✓ Non-root Docker container
✓ IBM Plex Sans self-hosted (no external font CDN)
```

---

---

## SLIDE 9 — DATABASE OVERVIEW

**Judul:** Database Schema — 16 Tables, PostgreSQL

**Format: grouped diagram**

```
┌─────────────────────────────────────────────────────────────┐
│  USER & ACCESS          │  MASTER DATA                      │
│  ─────────────────      │  ─────────────────                │
│  accounts               │  departments                      │
│  roles                  │  locations                        │
│  permissions            │  categories                       │
│  role_permissions       │  brands                           │
│  refresh_tokens         │  models (device)                  │
│                         │  employees                        │
├─────────────────────────┼───────────────────────────────────┤
│  ASSET CORE             │  ITSM                             │
│  ─────────────────      │  ─────────────────                │
│  assets                 │  incidents                        │
│  network_details        │  changes                          │
│  asset_credentials      │  problems                         │
│  (AES-256 encrypted)    │  requests                         │
│                         │  incident_problems                │
├─────────────────────────┴───────────────────────────────────┤
│  GOVERNANCE                                                 │
│  ─────────────────                                          │
│  audit_logs  (immutable — no UPDATE/DELETE endpoint)        │
└─────────────────────────────────────────────────────────────┘
```

**Highlight:**
> Semua tabel punya `updated_at` auto-trigger dan soft delete (`deleted_at`) — data tidak pernah hilang permanen.

---

---

## SLIDE 10 — DEVELOPMENT ROADMAP

**Judul:** Development Roadmap

**Format: timeline horizontal**

```
Phase 1          Phase 2          Phase 3          Phase 4          Phase 5          Phase 6
────────         ────────         ────────         ────────         ────────         ────────
Project          Master           Asset            Security &       ITSM             Reports &
Setup            Data             Management       RBAC             Modules          Finalisasi

• Docker         • Department     • Asset CRUD     • JWT Auth       • Incident       • Report CSV
• PostgreSQL     • Location       • Network        • RBAC           • Change         • Report Excel
• Database       • Category       • Credentials    • Audit Log      • Problem        • Dashboard
  Schema         • Brand          • History        • Brute-force    • Request        • Testing
• Auth           • Model            tracking         lockout                         • Dokumentasi
  Module         • Employee                        • AES-256
                                                     encryption

✅ DONE          ✅ DONE          ✅ DONE          ✅ DONE          ✅ DONE          🔄 IN PROGRESS
```

---

---

## SLIDE 11 — EXPECTED OUTPUT

**Judul:** Deliverables

**Format: 2 kolom checklist**

```
Aplikasi                              Dokumentasi & Deployment
─────────────────────────────────     ─────────────────────────────────
✓ Web app responsive (mobile,         ✓ README instalasi lengkap
  tablet, desktop)                    ✓ .env.example dengan semua
✓ Login/logout dengan JWT               variabel terdokumentasi
✓ Dashboard dengan summary aset       ✓ Docker Compose siap deploy
✓ CRUD master data (6 modul)          ✓ Database schema (PostgreSQL)
✓ Asset management lengkap            ✓ Seed script untuk data awal
✓ Network detail per aset             ✓ Security implementation notes
✓ Encrypted device credentials
✓ ITSM (Incident, Change,
  Problem, Request)
✓ Audit log immutable
✓ Report + export CSV & Excel
✓ Multi-language (ID/EN)
✓ Light/Dark/System theme
```

---

---

## SLIDE 12 — CLOSING

**Judul:** Value Proposition

**Layout: 3 card besar di tengah**

```
┌─────────────────────┐  ┌─────────────────────┐  ┌─────────────────────┐
│                     │  │                     │  │                     │
│  📦 Centralized     │  │  🔐 Secure          │  │  📋 Traceable       │
│     Asset Data      │  │     Operations      │  │     IT Ops          │
│                     │  │                     │  │                     │
│  Semua aset         │  │  Kredensial         │  │  Setiap perubahan   │
│  infrastruktur IT   │  │  perangkat          │  │  tercatat di        │
│  terpusat dalam     │  │  terenkripsi,       │  │  audit log yang     │
│  satu platform      │  │  akses terkontrol   │  │  tidak bisa        │
│                     │  │  via RBAC           │  │  dimanipulasi       │
└─────────────────────┘  └─────────────────────┘  └─────────────────────┘
```

**Kalimat penutup (besar, center):**
> IAMS membantu organisasi mengelola aset infrastruktur IT secara lebih **terpusat**, **aman**, **terdokumentasi**, dan **mudah diaudit**.

**Bawah:**
```
Shalahuddin · IT Support & Operation Intern · 2026
Vue 3 · Flask · PostgreSQL · Docker · IBM Carbon Design
```

---

---

## CATATAN DESAIN

### Warna (IBM Carbon)
| Elemen | Warna |
|---|---|
| Background slide | `#161616` (dark) atau `#FFFFFF` (light) |
| Aksen utama | `#0F62FE` (IBM Blue) |
| Teks utama | `#F4F4F4` (di dark) / `#161616` (di light) |
| Teks sekunder | `#C6C6C6` (di dark) / `#525252` (di light) |
| Card/border | `#262626` (di dark) / `#E0E0E0` (di light) |
| Success | `#24A148` |
| Warning | `#F1C21B` |
| Error | `#DA1E28` |

### Typography
| Elemen | Font | Weight | Size |
|---|---|---|---|
| Judul slide | IBM Plex Sans | 300 (Light) | 42–60px |
| Subjudul | IBM Plex Sans | 400 | 24–32px |
| Body | IBM Plex Sans | 400 | 16–18px |
| Caption/label | IBM Plex Sans | 400 | 12–14px |

### Tips Canva/PowerPoint
- Gunakan template **dark corporate** atau buat dari blank
- Semua sudut elemen: **0px (square)** — sesuai IBM Carbon
- Tidak perlu drop shadow — gunakan border tipis 1px
- Ikon: gunakan **Lucide Icons** atau **Carbon Icons** (IBM)
- Diagram arsitektur bisa dibuat dengan **draw.io** lalu di-screenshot

---

## VERSI RINGKAS (untuk presentasi cepat — 5 slide)

Kalau waktu presentasi terbatas, ambil slide ini saja:

1. **Cover** (Slide 1)
2. **Problem + Solution** (gabung Slide 3 & 4)
3. **Fitur + Stack** (gabung Slide 5 & 7)
4. **Security + Architecture** (gabung Slide 6 & 8)
5. **Roadmap + Closing** (gabung Slide 10 & 12)
