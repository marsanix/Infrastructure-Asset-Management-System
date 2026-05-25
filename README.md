# Infrastructure Asset Management System (IAMS)

## Tech Stack
- **Frontend**: Vue 3 + Vite + TypeScript + Tailwind CSS (IBM Carbon tokens) + IBM Plex Sans (self-hosted)
- **Backend**: Python Flask + SQLAlchemy + PostgreSQL
- **Cache / Token Store**: Redis (JWT blacklist + rate limiting)
- **Reverse Proxy**: Nginx (TLS 1.2/1.3, security headers)
- **Container**: Docker + Docker Compose

---

## Cara Menjalankan

### 1. Setup Environment
```bash
cp .env.example .env
# Edit .env — isi semua nilai yang diperlukan
# WAJIB: SECRET_KEY, JWT_SECRET_KEY, POSTGRES_PASSWORD, REDIS_PASSWORD, AES_ENCRYPTION_KEY, ADMIN_PASSWORD
```

### 2. Generate AES Key (untuk asset credentials)
```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
# Salin output ke AES_ENCRYPTION_KEY di .env
```

### 3. Jalankan dengan Docker Compose
```bash
docker-compose up --build -d
```

### 4. Jalankan Database Migration + Seed
```bash
# Masuk ke container backend
docker exec -it iams_backend bash

# Jalankan migration
flask db upgrade

# Jalankan seeder (baca ADMIN_PASSWORD dari .env)
python seed.py
```

Aplikasi tersedia di: `https://localhost`

---

### Development (tanpa Docker)

**Backend:**
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
flask db init
flask db migrate -m "initial"
flask db upgrade
python seed.py
python run.py
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

---

## Struktur Project
```
├── backend/
│   ├── app/
│   │   ├── api/v1/
│   │   │   ├── base_crud.py      ← Generic CRUD factory
│   │   │   ├── auth.py           ← Login/Logout/Refresh
│   │   │   ├── assets.py         ← Asset CRUD + history
│   │   │   ├── departments.py    ← Master data
│   │   │   ├── locations.py
│   │   │   ├── categories.py
│   │   │   ├── brands.py
│   │   │   ├── models.py
│   │   │   ├── employees.py
│   │   │   ├── network.py        ← Network details
│   │   │   ├── credentials.py    ← Encrypted device credentials
│   │   │   ├── incidents.py      ← ITSM
│   │   │   ├── changes.py
│   │   │   ├── problems.py
│   │   │   ├── requests_bp.py
│   │   │   ├── accounts.py       ← User management
│   │   │   ├── reports.py        ← JSON + CSV + Excel export
│   │   │   └── audit.py          ← Read-only audit log
│   │   ├── models/               ← SQLAlchemy models (13 tables)
│   │   └── utils/
│   │       ├── crypto.py         ← AES-256 Fernet
│   │       ├── rbac.py           ← Permission decorator
│   │       ├── audit.py          ← Audit log helper
│   │       ├── token_store.py    ← JWT blacklist (Redis)
│   │       └── state_machine.py  ← ITSM workflow validation
│   ├── seed.py                   ← Database seeder
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ui/               ← Carbon components (Button, Input, Table, dll)
│   │   │   ├── master/           ← Generic master data components
│   │   │   └── itsm/             ← Generic ITSM list component
│   │   ├── composables/
│   │   │   ├── useCrud.ts        ← Generic CRUD composable
│   │   │   ├── useAssets.ts      ← Asset-specific composable
│   │   │   └── useForm.ts        ← Form + Zod validation
│   │   ├── views/
│   │   │   ├── auth/             ← Login
│   │   │   ├── assets/           ← List, Form, Detail
│   │   │   ├── master/           ← Department, Location, Category, Brand, Model, Employee
│   │   │   ├── itsm/             ← Incident, Change, Problem, Request
│   │   │   ├── admin/            ← Accounts, Audit Log
│   │   │   └── ReportView.vue    ← Report + Export
│   │   ├── types/                ← Zod schemas + TypeScript types
│   │   ├── stores/               ← Pinia (auth)
│   │   ├── router/               ← Vue Router + navigation guard
│   │   └── lib/                  ← axios instance + interceptor
│   └── Dockerfile
├── nginx/nginx.conf
├── database.sql                  ← PostgreSQL schema lengkap
├── docker-compose.yml
├── .env.example
└── .gitignore
```

---

## Security Implementation (OWASP Top 10:2025 + API Security)

| Ancaman | Implementasi |
|---|---|
| **A01 Broken Access Control** | RBAC `@require_permission` di setiap endpoint |
| **A02 Cryptographic Failures** | TLS 1.2/1.3, AES-256 Fernet (credentials), bcrypt cost 12 (passwords) |
| **A03 Injection** | SQLAlchemy ORM (no raw SQL), Marshmallow EXCLUDE, Zod frontend validation |
| **A05 Security Misconfiguration** | Flask-Talisman (CSP/HSTS/X-Frame), Nginx hardening, non-root Docker user |
| **A07 Auth Failures** | Rate limiting (Flask-Limiter + Nginx), brute-force lockout, JWT blacklist (Redis) |
| **A09 Logging Failures** | Immutable audit log, setiap mutasi tercatat + IP + old/new data |
| **API1 BOLA** | 404 response sama untuk not-found dan no-permission |
| **API3 Mass Assignment** | Explicit `UPDATABLE` allowlist + Marshmallow EXCLUDE |
| **API3 Excessive Data Exposure** | Explicit serializer per model, `password_hash` tidak pernah di-response |
| **API4 Resource Consumption** | Pagination max per endpoint, export limit 10k rows |
| **Business Logic Abuse** | State machine validation untuk ITSM status transitions |
| **CSV Formula Injection** | `_sanitize_cell()` prefix stripping sebelum export |
| **XSS** | Tidak ada `v-html`, IBM Plex Sans self-hosted (no external CDN), CSP strict |
| **Credential Exposure** | Reveal endpoint terpisah + selalu di-audit, list endpoint tanpa password |

---

## Default Credentials (setelah seed)
Username dan password diambil dari `.env`:
- `ADMIN_USERNAME` (default: `admin`)
- `ADMIN_PASSWORD` (wajib diset, tidak ada default)

**Ganti password setelah login pertama.**
