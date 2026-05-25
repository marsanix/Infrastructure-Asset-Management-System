# Aplikasi Infrastructure Asset Management System (IAMS)

## Teknologi

| Layer | Stack |
|---|---|
| **Frontend** | Vue 3 + Vite + TypeScript + shadcn-vue + Tailwind CSS |
| **Backend** | Python Flask 3.1 + SQLAlchemy ORM + Marshmallow |
| **Database** | PostgreSQL 16 |
| **Cache & Token Store** | Redis 7 (JWT blacklist, rate limiting) |
| **Reverse Proxy** | Nginx 1.27 (TLS 1.3, security headers) |
| **Containerization** | Docker + Docker Compose |
| **UI Design System** | IBM Carbon Design System (IBM Plex Sans, 0px radius, token warna) |
| **Font** | IBM Plex Sans (self-hosted via @fontsource — tidak ada CDN eksternal) |

### Keamanan
- Implementasi **OWASP Top 10:2025** dan **MITRE ATT&CK framework**
- JWT Authentication (access token 15 menit + refresh token 7 hari)
- RBAC (Role-Based Access Control) dengan permission granular per modul
- Rate limiting via Flask-Limiter + Nginx zone
- Brute-force lockout (5 kali gagal login → akun terkunci)
- AES-256 encryption (Fernet) untuk credential perangkat
- bcrypt cost-12 untuk password akun
- Immutable audit log (tidak ada endpoint DELETE/UPDATE)
- Content Security Policy (CSP) ketat via Flask-Talisman
- Non-root Docker container

### UI/UX
- Multiple Language Support: **Bahasa Indonesia** dan **English** (vue-i18n)
- Theme: **Light**, **Dark**, **System** (mengikuti preferensi OS)
- Responsive Design: **Mobile**, **Tablet**, **Desktop**
- Arsitektur komponen modular (Carbon Design tokens, 0px border radius)

---

## Fitur Aplikasi

### Core
- **Dashboard** — ringkasan status aset, ITSM overview, warranty expiry alert
- **User Login / Logout** — JWT-based authentication, session management

### Manajemen Aset
- **Manajemen Aset** — CRUD aset, filter, search, pagination, riwayat perubahan, soft delete
- **Manajemen Jaringan** — IP address, MAC address, VLAN, hostname, subnet per aset
- **Secure Credential Notes** — password perangkat (router, switch, firewall, AP, printer) terenkripsi AES-256, reveal endpoint terpisah + selalu di-audit

### Master Data
- **Manajemen Pengguna (Karyawan)** — data karyawan sebagai pemilik/pengguna aset
- **Manajemen Departemen**
- **Manajemen Lokasi**
- **Manajemen Kategori**
- **Manajemen Merek**
- **Manajemen Model** — spesifikasi perangkat, relasi ke merek & kategori

### Akses & Keamanan
- **Manajemen Akun** — CRUD akun login, reset password, unlock akun
- **Role Management** — Administrator, User
- **Role Based Access Control (RBAC)** — permission granular: `module:action` (contoh: `asset:create`, `audit:read`)

### ITSM (IT Service Management)
- **Incident Management** — pelaporan insiden, state machine workflow, severity & priority
- **Change Management** — permintaan perubahan, approval workflow, rollback plan
- **Problem Management** — analisis root cause, workaround, known error
- **Request Management** — permintaan layanan IT, approval & fulfillment workflow

> Semua modul ITSM menggunakan **state machine validation** di server — transisi status yang tidak valid ditolak (Business Logic Abuse prevention).

### Pelaporan & Audit
- **Report Management** — laporan aset lengkap, filter multi-kriteria, export **CSV** dan **Excel** (dengan formula injection prevention)
- **Audit Log** — riwayat semua aktivitas (CREATE/UPDATE/DELETE/LOGIN/LOGOUT), immutable, filter per modul/aksi

---

## Struktur Database

Lihat file `database.sql` untuk DDL lengkap.

### Ringkasan Tabel (16 tabel, PostgreSQL)

| Grup | Tabel |
|---|---|
| **User & Access** | `accounts`, `roles`, `permissions`, `role_permissions`, `refresh_tokens` |
| **Master Data** | `departments`, `locations`, `categories`, `brands`, `models`, `employees` |
| **Asset Core** | `assets`, `network_details`, `asset_credentials` |
| **ITSM** | `incidents`, `changes`, `problems`, `requests`, `incident_problems` |
| **Governance** | `audit_logs` |

### Fitur Database
- Semua tabel punya `created_at`, `updated_at` (auto-trigger), dan `deleted_at` (soft delete)
- Index pada kolom yang sering di-query (status, asset_tag, serial_number, ip_address)
- 3 database views: `v_asset_report`, `v_asset_status_summary`, `v_asset_by_department`
- `pgcrypto` extension untuk operasi kriptografi di level database

---

## Struktur Project

```
Infrastructure-Asset-Management-System/
├── backend/
│   ├── app/
│   │   ├── api/v1/          # 14 endpoint modules
│   │   ├── models/          # 13 SQLAlchemy models
│   │   └── utils/           # crypto, rbac, audit, token_store, state_machine
│   ├── seed.py              # Database seeder (idempotent)
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/ui/   # Carbon UI components (Button, Input, Table, dll)
│   │   ├── components/master/  # Generic master data components
│   │   ├── components/itsm/    # Generic ITSM list component
│   │   ├── composables/     # useCrud, useAssets, useForm (Zod)
│   │   ├── views/           # Semua halaman per modul
│   │   ├── types/           # Zod schemas + TypeScript types
│   │   ├── stores/          # Pinia (auth store)
│   │   ├── router/          # Vue Router + navigation guard
│   │   └── lib/             # axios instance + interceptor
│   └── Dockerfile
├── nginx/nginx.conf
├── database.sql             # PostgreSQL schema lengkap
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## Cara Menjalankan

```bash
# 1. Setup environment
cp .env.example .env
# Edit .env — isi SECRET_KEY, JWT_SECRET_KEY, POSTGRES_PASSWORD, REDIS_PASSWORD, AES_ENCRYPTION_KEY, ADMIN_PASSWORD

# 2. Jalankan Docker Compose
docker-compose up --build -d

# 3. Migration + Seed
docker exec -it iams_backend bash
flask db upgrade
python seed.py
```

Akses aplikasi di: `https://localhost`
