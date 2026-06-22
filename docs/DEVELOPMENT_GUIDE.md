# 🛠️ Development Guide — IAMS

**Versi:** 1.0  
**Tanggal:** 22 Juni 2026  
**Target pembaca:** Developer yang akan melanjutkan/maintain proyek ini

---

## Daftar Isi

1. [Development Setup (Local tanpa Docker)](#1-development-setup)
2. [Architecture Decision Record (ADR)](#2-architecture-decision-record)
3. [Code Convention & Style Guide](#3-code-convention--style-guide)
4. [Database Migration Guide](#4-database-migration-guide)
5. [Cara Tambah Modul Baru (Step-by-Step)](#5-cara-tambah-modul-baru)
6. [Testing Guide](#6-testing-guide)
7. [API Contract & Response Format](#7-api-contract--response-format)
8. [Security Implementation Guide](#8-security-implementation-guide)
9. [Frontend Development Guide](#9-frontend-development-guide)
10. [Deployment Pipeline](#10-deployment-pipeline)
11. [Known Limitations & Technical Debt](#11-known-limitations--technical-debt)
12. [Troubleshooting Developer Issues](#12-troubleshooting)

---

## 1. Development Setup

### 1.1 Prasyarat

| Tool | Versi | Install |
|------|-------|---------|
| Python | 3.12+ | `winget install Python.Python.3.12` |
| Node.js | 18+ | `winget install OpenJS.NodeJS.LTS` |
| Yarn | 1.22+ | `npm install -g yarn` |
| MariaDB | 10.11+ | `winget install MariaDB.Server` atau Docker |
| Redis | 7+ | `winget install Redis.Redis` atau Docker |
| Git | Latest | `winget install Git.Git` |

### 1.2 Backend Setup (Flask)

```bash
# 1. Clone & masuk ke folder
git clone https://github.com/0xshalah/iams-revisi.git
cd iams-revisi/backend

# 2. Buat virtual environment
python -m venv .venv

# 3. Aktifkan venv
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Copy env dan konfigurasi
cp ../.env.example .env
# Edit .env:
#   DATABASE_URL=mysql+pymysql://iams:password@localhost:3306/iams_db
#   JWT_SECRET=<generate: python -c "import secrets; print(secrets.token_hex(64))">
#   AES_KEY_BASE64=<generate: python -c "import secrets,base64; print(base64.b64encode(secrets.token_bytes(32)).decode())">
#   FRONTEND_ORIGIN=http://localhost:3000
#   FLASK_ENV=development

# 6. Buat database (di MariaDB)
mysql -u root -e "CREATE DATABASE iams_db; CREATE USER 'iams'@'localhost' IDENTIFIED BY 'password'; GRANT ALL ON iams_db.* TO 'iams'@'localhost';"

# 7. Jalankan migration
flask db upgrade

# 8. Seed data
flask seed

# 9. Run development server
flask run --port 5000 --debug
```

📁 **Backend berjalan di:** `http://localhost:5000`

### 1.3 Frontend Setup (Vue 3)

```bash
# 1. Masuk ke folder frontend
cd frontend

# 2. Install dependencies
yarn install

# 3. Buat .env (opsional, default sudah ok)
echo "VITE_API_BASE_URL=http://localhost:5000/api" > .env.local

# 4. Run dev server (hot reload)
yarn dev
```

📁 **Frontend berjalan di:** `http://localhost:3000`

### 1.4 Verifikasi

1. Buka `http://localhost:3000` → Landing page muncul
2. Klik Login → `admin@iams.local` / `admin123`
3. Dashboard muncul dengan data → Setup berhasil ✅

### 1.5 Development dengan Docker (alternatif)

Kalau tidak mau install MariaDB/Redis manual:

```bash
# Jalankan hanya DB & Redis via Docker, backend/frontend manual
docker compose up mysql redis -d

# Lalu jalankan backend & frontend secara manual (seperti di atas)
# DATABASE_URL=mysql+pymysql://iams:iams_secret@localhost:3306/iams_db
```

---

## 2. Architecture Decision Record

### ADR-001: Kenapa Flask (bukan Django/FastAPI)?

| Aspek | Keputusan | Alasan |
|-------|-----------|--------|
| Framework | Flask 3 | Lightweight, explicit routing, cocok untuk REST API tanpa fitur yang tidak dipakai |
| Kenapa bukan Django | Terlalu banyak fitur bawaan (admin panel, ORM migration style) yang tidak sesuai kebutuhan | Kita butuh kontrol penuh atas auth flow (JWT cookie) |
| Kenapa bukan FastAPI | async belum diperlukan, MariaDB driver (PyMySQL) synchronous | Team lebih familiar Flask |

📁 **Bukti:** `backend/app/__init__.py` — application factory pattern

### ADR-002: Kenapa Vue 3 (bukan React/Svelte)?

| Aspek | Keputusan | Alasan |
|-------|-----------|--------|
| Framework | Vue 3 (Composition API) | Template syntax lebih readable, single-file component, learning curve rendah |
| State | Pinia | Official Vue state management, simpler than Vuex |
| Routing | vue-router 4 | Deep integration dengan Vue, supports meta-based auth guards |
| CSS | TailwindCSS 3 | Utility-first, no custom CSS needed, dark mode built-in |

📁 **Bukti:** `frontend/package.json` — dependencies

### ADR-003: Kenapa MariaDB (bukan PostgreSQL)?

| Aspek | Keputusan | Alasan |
|-------|-----------|--------|
| Database | MariaDB 10.11 | MySQL-compatible, schema dari supervisor menggunakan MySQL syntax |
| Driver | PyMySQL | Pure Python, no C compilation needed |
| Kenapa bukan PostgreSQL | Supervisor SQL schema = MySQL, migrasi berisiko compatibility |

📁 **Bukti:** `docker-compose.yml` — `image: mariadb:10.11`

### ADR-004: Kenapa JWT di Cookie (bukan localStorage)?

| Aspek | Keputusan | Alasan |
|-------|-----------|--------|
| Token storage | HttpOnly cookie | Immune terhadap XSS (JavaScript tidak bisa akses) |
| CSRF | Double-submit cookie | Trade-off: butuh CSRF protection, tapi XSS-safe |
| Kenapa bukan localStorage | Rentan XSS — satu vulnerability bisa steal token |

📁 **Bukti:** `backend/app/routes/auth.py` Line 76 — `httponly=True`

### ADR-005: Kenapa AES-256-GCM untuk credential?

| Aspek | Keputusan | Alasan |
|-------|-----------|--------|
| Encryption | AES-256-GCM | Credential harus bisa di-reveal (reversible), bcrypt tidak bisa |
| Mode | GCM (Galois/Counter) | Authenticated encryption — detect tampering |
| Key length | 256-bit (32 bytes) | Industry standard, quantum-resistant threshold |
| Kenapa bukan bcrypt | bcrypt = one-way hash, credential perlu di-decrypt untuk reveal |

📁 **Bukti:** `backend/app/utils/security.py` Line 30-35

---

## 3. Code Convention & Style Guide

### 3.1 Backend (Python/Flask)

| Aspek | Convention | Contoh |
|-------|-----------|--------|
| File naming | snake_case | `audit_logs.py`, `snipe_features.py` |
| Function | snake_case | `def list_assets():` |
| Class | PascalCase | `class ChangeRequest(db.Model):` |
| Blueprint | Satu file per modul | `routes/assets.py`, `routes/incidents.py` |
| URL prefix | `/api/{resource}` | `/api/assets`, `/api/incidents` |
| Route method | REST convention | GET=list, POST=create, PUT=update, DELETE=delete |
| Decorator order | `@bp.route` → `@role` → `@require_csrf` → `@audit_action` | Lihat contoh di bawah |

**Decorator stacking order (dari luar ke dalam):**

```python
@bp.route('/<int:asset_id>', methods=['DELETE'])  # 1. Route
@admin_only                                       # 2. Role check (includes @require_auth)
@require_csrf                                     # 3. CSRF validation
@audit_action('DELETE', 'asset', resource_id_key='asset_id')  # 4. Audit logging
def delete_asset(asset_id):
    ...
```

📁 **Contoh:** `backend/app/routes/assets.py` Line 87-92

### 3.2 Frontend (Vue 3)

| Aspek | Convention | Contoh |
|-------|-----------|--------|
| File naming | PascalCase untuk komponen | `AssetsPage.vue`, `UserFormDialog.vue` |
| Folder | lowercase | `components/ui/`, `pages/`, `stores/` |
| Component | `<script setup>` | Composition API, no Options API |
| State | Pinia store | `stores/auth.js`, `stores/ui.js` |
| API calls | Via `apiClient.js` | Tidak fetch langsung dari komponen |
| i18n keys | dot notation | `navigation.dashboard`, `pages.auditTitle` |
| CSS | Tailwind classes only | Tidak ada custom CSS files |

**Struktur komponen standar:**

```vue
<script setup>
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'  // ← WAJIB kalau pakai {{ t('...') }}
import apiClient from '@/services/apiClient'

const { t } = useI18n()
// ... logic
</script>

<template>
  <!-- template -->
</template>
```

> ⚠️ **PENTING:** Selalu destructure `const { t } = useI18n()` di `<script setup>` kalau template menggunakan `{{ t('key') }}`. Tanpa ini, halaman akan blank tanpa error message.

### 3.3 Git Convention

| Aspek | Format |
|-------|--------|
| Branch | `feature/nama-fitur`, `fix/deskripsi-bug`, `refactor/area` |
| Commit | `feat: add license management module` |
| Commit | `fix: resolve i18n crash on users page` |
| Commit | `refactor: extract pagination utility` |
| Commit | `docs: update user manual screenshots` |

---

## 4. Database Migration Guide

### 4.1 File Lokasi

```
backend/migrations/
├── alembic.ini          # Konfigurasi Alembic
├── env.py               # Migration environment
├── script.py.mako       # Template file baru
└── versions/            # Migration files (sequential)
    ├── 001_mysql_extensions.py
    ├── 002_strict_alignment_status_default_timestamp_nulls.py
    ├── 003_service_requests.py
    ├── 004_change_requests.py
    ├── 005_perf_indexes.py
    ├── 006_multi_credentials.py
    ├── 007_snipe_features.py
    └── 009_list_sort_indexes.py
```

### 4.2 Cara Buat Migration Baru

**Opsi A: Auto-generate dari perubahan model**

```bash
# 1. Edit model di backend/app/models.py
# 2. Generate migration otomatis
flask db migrate -m "add knowledge_base table"
# 3. Review file yang dihasilkan di migrations/versions/
# 4. Apply migration
flask db upgrade
```

**Opsi B: Tulis manual (recommended untuk kontrol penuh)**

```bash
# Buat file migration kosong
flask db revision -m "add knowledge_base table"
```

Lalu edit file yang dibuat:

```python
"""add knowledge_base table

Revision ID: 010_knowledge_base
Revises: 009_list_sort_indexes
Create Date: 2026-06-22
"""
from alembic import op
import sqlalchemy as sa

revision = '010_knowledge_base'
down_revision = '009_list_sort_indexes'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('knowledge_base',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('category', sa.String(100), nullable=True),
        sa.Column('author_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False,
                  server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False,
                  server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
    )


def downgrade():
    op.drop_table('knowledge_base')
```

### 4.3 Perintah Migration

| Perintah | Fungsi |
|----------|--------|
| `flask db upgrade` | Apply semua migration yang belum dijalankan |
| `flask db downgrade` | Rollback 1 step |
| `flask db current` | Lihat revision yang aktif |
| `flask db history` | Lihat semua migration |
| `flask db migrate -m "msg"` | Auto-generate dari diff model |

### 4.4 Di Docker

```bash
docker exec iams_backend flask db upgrade
docker exec iams_backend flask db downgrade
```

---

## 5. Cara Tambah Modul Baru

Contoh: Menambahkan modul **"Knowledge Base"** — tempat simpan artikel/solusi IT.

### Step 1: Buat Model

📁 **File:** `backend/app/models.py` — tambahkan di akhir file:

```python
class KnowledgeArticle(db.Model, TimestampMixin):
    """Knowledge base articles."""
    __tablename__ = 'knowledge_articles'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    author_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)
    is_published: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    author: Mapped['User'] = relationship('User')

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'category': self.category,
            'author_id': self.author_id,
            'author_name': self.author.name if self.author else None,
            'is_published': self.is_published,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
        }
```

### Step 2: Buat Migration

```bash
flask db migrate -m "add knowledge_articles table"
flask db upgrade
```

### Step 3: Buat Route (API Blueprint)

📁 **File baru:** `backend/app/routes/knowledge.py`

```python
"""Knowledge Base blueprint."""
from flask import Blueprint, g, jsonify, request

from app.extensions import db
from app.models import KnowledgeArticle
from app.utils.decorators import admin_or_operator, admin_only, require_csrf
from app.utils.pagination import paginate

bp = Blueprint('knowledge', __name__, url_prefix='/api/knowledge')


@bp.route('', methods=['GET'])
@admin_or_operator
def list_articles():
    query = KnowledgeArticle.query
    search = (request.args.get('search') or '').strip()
    if search:
        query = query.filter(KnowledgeArticle.title.like(f'%{search}%'))
    category = request.args.get('category')
    if category:
        query = query.filter_by(category=category)
    rows = query.order_by(KnowledgeArticle.created_at.desc())
    return jsonify(paginate(rows))


@bp.route('', methods=['POST'])
@admin_or_operator
@require_csrf
def create_article():
    data = request.get_json(silent=True) or {}
    title = (data.get('title') or '').strip()
    content = (data.get('content') or '').strip()
    if not title or not content:
        return jsonify({'error': 'title and content are required'}), 400
    article = KnowledgeArticle(
        title=title,
        content=content,
        category=(data.get('category') or '').strip() or None,
        author_id=g.current_user_id,
        is_published=data.get('is_published', False),
    )
    db.session.add(article)
    db.session.commit()
    return jsonify({'data': article.to_dict()}), 201


@bp.route('/<int:article_id>', methods=['GET'])
@admin_or_operator
def get_article(article_id):
    article = db.session.get(KnowledgeArticle, article_id)
    if not article:
        return jsonify({'error': 'Article not found'}), 404
    return jsonify({'data': article.to_dict()})


@bp.route('/<int:article_id>', methods=['PUT'])
@admin_or_operator
@require_csrf
def update_article(article_id):
    article = db.session.get(KnowledgeArticle, article_id)
    if not article:
        return jsonify({'error': 'Article not found'}), 404
    data = request.get_json(silent=True) or {}
    if 'title' in data:
        article.title = data['title'].strip()
    if 'content' in data:
        article.content = data['content'].strip()
    if 'category' in data:
        article.category = (data['category'] or '').strip() or None
    if 'is_published' in data:
        article.is_published = bool(data['is_published'])
    db.session.commit()
    return jsonify({'data': article.to_dict()})


@bp.route('/<int:article_id>', methods=['DELETE'])
@admin_only
@require_csrf
def delete_article(article_id):
    article = db.session.get(KnowledgeArticle, article_id)
    if not article:
        return jsonify({'error': 'Article not found'}), 404
    db.session.delete(article)
    db.session.commit()
    return jsonify({'message': 'Article deleted'})
```

### Step 4: Register Blueprint

📁 **File:** `backend/app/__init__.py` — tambahkan:

```python
from app.routes.knowledge import bp as knowledge_bp
app.register_blueprint(knowledge_bp)
```

### Step 5: Tambah di Frontend API Client

📁 **File:** `frontend/src/services/apiClient.js` — tambahkan:

```javascript
// Knowledge Base
listArticles: (params = {}) => {
  const query = qs(params, { per_page: 25 })
  return get(`/knowledge${query ? `?${query}` : ''}`)
},
createArticle: (payload) => post('/knowledge', payload),
updateArticle: (id, payload) => put(`/knowledge/${id}`, payload),
deleteArticle: (id) => del(`/knowledge/${id}`),
```

### Step 6: Buat Page Vue

📁 **File baru:** `frontend/src/pages/KnowledgePage.vue`

(Ikuti pattern dari `LicensesPage.vue` — copy dan sesuaikan)

### Step 7: Tambah Route

📁 **File:** `frontend/src/router/index.js` — tambahkan di children:

```javascript
{ path: 'knowledge', name: 'knowledge', component: () => import('@/pages/KnowledgePage.vue') },
```

### Step 8: Tambah di Sidebar Navigation

Edit `DashboardLayout.vue` — tambahkan item menu baru.

### Step 9: Tambah i18n Keys

📁 `frontend/src/i18n/locales/id.js` dan `en.js` — tambahkan translation.

### Step 10: Test

```bash
# Backend test
docker exec iams_backend python -m pytest tests/ -v

# Manual test: buka browser, navigasi ke halaman baru
```

---

## 6. Testing Guide

### 6.1 Lokasi & Struktur Test

```
backend/tests/
└── test_security.py    # 19 integration tests (auth, CSRF, RBAC, CRUD)
```

### 6.2 Menjalankan Test

```bash
# Lokal (venv aktif)
cd backend
RATELIMIT_ENABLED=false python -m pytest tests/ -v

# Docker
docker exec -e RATELIMIT_ENABLED=false iams_backend python -m pytest tests/ -v

# Dengan coverage
docker exec -e RATELIMIT_ENABLED=false iams_backend python -m pytest tests/ -v --cov=app
```

### 6.3 Test Fixture Pattern

```python
@pytest.fixture(scope='module')
def app():
    """Create app with test database (SQLite in-memory)."""
    os.environ['DATABASE_URL'] = 'sqlite:///test.db'
    os.environ['RATELIMIT_ENABLED'] = 'false'
    # ... setup ...
    app = create_app()
    with app.app_context():
        db.create_all()
        # Seed test data
    yield app


@pytest.fixture()
def admin(client):
    """Login as admin and return authenticated client."""
    r = client.get('/api/auth/csrf-token')
    csrf = r.json['csrf_token']
    client.post('/api/auth/login',
                json={'email': 'admin@iams.local', 'password': 'admin123'},
                headers={'X-CSRF-Token': csrf})
    return client
```

📁 **Bukti:** `backend/tests/test_security.py` Line 11-56

### 6.4 Cara Tulis Test Baru

Template untuk test modul baru:

```python
class TestKnowledgeBase:
    def test_create_article(self, admin, client):
        r = client.get('/api/auth/csrf-token')
        csrf = r.json['csrf_token']
        client.post('/api/auth/login',
                    json={'email': 'admin@iams.local', 'password': 'admin123'},
                    headers={'X-CSRF-Token': csrf})
        r = client.post('/api/knowledge', json={
            'title': 'How to restart router',
            'content': 'Step 1: ...',
            'category': 'Network'
        }, headers={'X-CSRF-Token': csrf})
        assert r.status_code == 201
        assert r.json['data']['title'] == 'How to restart router'

    def test_operator_cannot_delete(self, operator, client):
        # ... test RBAC ...
        r = client.delete('/api/knowledge/1')
        assert r.status_code == 403
```

### 6.5 Yang Harus Di-test

| Kategori | Apa yang di-test |
|----------|-----------------|
| Auth | Login success, login failure, session expired |
| CSRF | Missing CSRF rejected, invalid CSRF rejected |
| RBAC | Operator blocked from admin routes, admin allowed |
| CRUD | Create, Read, Update, Delete per modul |
| Validation | Missing required fields → 400, duplicate → 409 |
| Security | No token leak in response body, audit log written |

---

## 7. API Contract & Response Format

### 7.1 Standard Response Format

**Success (single item):**
```json
{
  "data": {
    "id": 1,
    "asset_tag": "AST-RTR-0001",
    "status": "Active",
    "created_at": "2026-06-19T12:00:00"
  }
}
```

**Success (list with pagination):**
```json
{
  "data": [
    {"id": 1, "asset_tag": "AST-RTR-0001", ...},
    {"id": 2, "asset_tag": "AST-SWT-0001", ...}
  ],
  "page": 1,
  "per_page": 25,
  "total": 8,
  "pages": 1
}
```

**Error:**
```json
{
  "error": "Asset tag already exists"
}
```

### 7.2 HTTP Status Codes

| Code | Meaning | Kapan dipakai |
|------|---------|---------------|
| 200 | OK | GET success, PUT success, DELETE success |
| 201 | Created | POST success |
| 400 | Bad Request | Validation error (missing field, invalid enum) |
| 401 | Unauthorized | Not logged in / token expired |
| 403 | Forbidden | Wrong role / CSRF mismatch |
| 404 | Not Found | Resource tidak ada |
| 409 | Conflict | Duplicate (unique constraint) / state conflict |
| 413 | Payload Too Large | File upload > 10MB |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Error | Unexpected server error |

### 7.3 Pagination Query Parameters

| Param | Default | Max | Contoh |
|-------|---------|-----|--------|
| `page` | 1 | - | `?page=2` |
| `per_page` | 25 | 100 (500 for reports) | `?per_page=50` |

📁 **Implementation:** `backend/app/utils/pagination.py`

### 7.4 Authentication Headers

Semua request ke protected endpoint harus menyertakan:

```
Cookie: access_token=<jwt>; csrf_token=<csrf>
```

Untuk state-changing requests (POST/PUT/DELETE):
```
Cookie: access_token=<jwt>; csrf_token=<csrf>
X-CSRF-Token: <csrf_value_same_as_cookie>
Content-Type: application/json
```

---

## 8. Security Implementation Guide

### 8.1 Menambah Role Baru

Saat ini: Administrator, Operator. Kalau mau tambah role "Viewer" (read-only):

**Step 1:** Seed role baru

```python
# backend/app/commands.py
for name in ('Administrator', 'Operator', 'Viewer'):
    ...
```

**Step 2:** Buat decorator baru (opsional)

```python
# backend/app/utils/decorators.py
def viewer_and_above(f):
    return require_role('Administrator', 'Operator', 'Viewer')(f)
```

**Step 3:** Update frontend router meta

```javascript
meta: { roles: ['Administrator', 'Operator', 'Viewer'] }
```

### 8.2 Menambah Audit Action Baru

```python
# Di route handler, panggil:
from app.utils.audit import log_audit

log_audit(
    action='CUSTOM_ACTION',       # Nama aksi
    resource_type='knowledge',    # Tipe resource
    resource_id=article.id,       # ID (opsional)
    status='success',             # success / failure
    metadata={'key': 'value'}     # Auto-redacted
)
```

### 8.3 Menambah Encrypted Field Baru

```python
from app.utils.security import encrypt_secret, decrypt_secret
from flask import current_app

# Encrypt
enc, nonce = encrypt_secret(plaintext, current_app.config['AES_KEY'])

# Decrypt
plaintext = decrypt_secret(enc, nonce, current_app.config['AES_KEY'])
```

---

## 9. Frontend Development Guide

### 9.1 Folder Structure

```
frontend/src/
├── components/
│   ├── ui/              # Reusable UI primitives (Button, Card, Input, Dialog, etc.)
│   ├── assets/          # Asset-specific components
│   ├── incidents/       # Incident-specific components
│   ├── problems/        # Problem-specific components
│   ├── users/           # User-specific components (UserFormDialog)
│   └── layout/          # Sidebar, Navbar, etc.
├── pages/               # Route-level page components (1 per route)
├── router/              # Vue Router config + auth guards
├── stores/              # Pinia stores
│   ├── auth.js          # User session, login/logout
│   ├── locale.js        # Language preference
│   ├── theme.js         # Dark/light mode
│   └── ui.js            # Toast notifications, UI state
├── services/
│   └── apiClient.js     # Centralized HTTP client
├── i18n/
│   ├── index.js         # i18n setup
│   └── locales/
│       ├── id.js        # Bahasa Indonesia (~600 keys)
│       └── en.js        # English (~600 keys)
├── lib/
│   └── utils.js         # Utility functions (formatDate, cn, etc.)
└── data/                # Static data (FAQ items, etc.)
```

### 9.2 Komponen UI yang Tersedia

| Komponen | Lokasi | Fungsi |
|----------|--------|--------|
| `Button` | `ui/Button.vue` | Tombol dengan variant/size/loading |
| `Card` | `ui/Card.vue` | Container card |
| `Input` | `ui/Input.vue` | Text input field |
| `Label` | `ui/Label.vue` | Form label |
| `Select` | `ui/Select.vue` | Dropdown select |
| `Dialog` | `ui/Dialog.vue` | Modal dialog |
| `ConfirmDialog` | `ui/ConfirmDialog.vue` | Confirm delete/action |
| `Badge` | `ui/Badge.vue` | Status badge |
| `StatusBadge` | `ui/StatusBadge.vue` | Colored status indicator |
| `Pagination` | `ui/Pagination.vue` | Page navigation |
| `EmptyState` | `ui/EmptyState.vue` | "No data" placeholder |
| `ErrorState` | `ui/ErrorState.vue` | Error with retry button |
| `TableSkeleton` | `ui/TableSkeleton.vue` | Loading skeleton |

### 9.3 State Management (Pinia)

```javascript
// Mengakses auth store
import { useAuthStore } from '@/stores/auth'
const auth = useAuthStore()

// Cek role
if (auth.isAdmin) { ... }

// Logout
await auth.logout()
```

### 9.4 Menambah Halaman Baru (Checklist)

- [ ] Buat `pages/NamaPage.vue`
- [ ] Import `useI18n` dan destructure `t` jika pakai translation
- [ ] Tambah route di `router/index.js`
- [ ] Tambah menu item di sidebar (`DashboardLayout.vue`)
- [ ] Tambah API methods di `services/apiClient.js`
- [ ] Tambah i18n keys di `i18n/locales/id.js` dan `en.js`
- [ ] Test di browser (light + dark mode, id + en)

---

## 10. Deployment Pipeline

### 10.1 Development Flow

```
Local Dev → Push to Git → Docker Build → Deploy
```

### 10.2 Environment Stages

| Stage | Tujuan | Config |
|-------|--------|--------|
| Development | Local coding, hot reload | `FLASK_ENV=development`, `COOKIE_SECURE=false` |
| Staging | Testing sebelum production | Docker Compose, test data |
| Production | Live | `FLASK_ENV=production`, `COOKIE_SECURE=true`, HTTPS |

### 10.3 Production Checklist

- [ ] Ganti semua default credentials (admin/operator password)
- [ ] Generate fresh `JWT_SECRET` dan `AES_KEY_BASE64`
- [ ] Set `FLASK_ENV=production`
- [ ] Set `COOKIE_SECURE=true`, `COOKIE_SAMESITE=Strict`
- [ ] Set `RATELIMIT_STORAGE_URI=redis://redis:6379/0`
- [ ] Replace self-signed cert dengan real TLS cert
- [ ] Set `MYSQL_ROOT_PASSWORD` yang kuat
- [ ] Backup strategy: automated MariaDB dumps
- [ ] Monitor: Docker health checks + alerting
- [ ] Firewall: hanya port 80/443 exposed

📁 **Detail lengkap:** `docs/PRODUCTION_HARDENING.md`

### 10.4 Build Commands

```bash
# Build semua images
docker compose build

# Build spesifik service
docker compose build frontend --no-cache
docker compose build backend --no-cache

# Deploy (rebuild + restart)
docker compose up --build -d

# Zero-downtime restart (satu service)
docker compose up -d --no-deps --build frontend
```

---

## 11. Known Limitations & Technical Debt

### 11.1 Limitations

| # | Limitation | Impact | Workaround |
|---|-----------|--------|-----------|
| 1 | No email notification | User harus manual cek incident/request | — |
| 2 | No file preview (hanya download) | UX kurang optimal untuk PDF/image | — |
| 3 | No real-time updates | Dashboard harus manual refresh | Polling setiap 60s di frontend |
| 4 | Single-region deployment | No HA/failover | Docker restart policy: unless-stopped |
| 5 | File stored as BLOB | DB size grows dengan attachments | Migrasi ke object storage (S3/MinIO) |
| 6 | No password reset via email | User harus kontak admin | — |
| 7 | Audit log no DELETE endpoint | Data terus bertambah | Archival policy needed |

### 11.2 Technical Debt

| # | Item | Severity | Suggested Fix |
|---|------|----------|---------------|
| 1 | No frontend unit tests | Medium | Add Vitest + Vue Test Utils |
| 2 | `Query.get()` deprecated warnings | Low | Replace with `db.session.get()` (partially done) |
| 3 | CSRF token in JSON body AND cookie | Low | Remove JSON body, rely only on cookie |
| 4 | No input sanitization (XSS) | Medium | Add DOMPurify on frontend |
| 5 | Pagination: no cursor-based option | Low | Add cursor for large datasets |
| 6 | i18n keys hardcoded in some pages | Low | Full i18n audit needed |
| 7 | Docker image size (~800MB backend) | Low | Multi-stage build optimization |

### 11.3 PR Welcome

Contributions welcome untuk:
- Email notification (SMTP integration)
- WebSocket real-time dashboard
- LDAP/AD authentication
- S3/MinIO file storage
- Vitest frontend testing
- Cursor-based pagination

---

## 12. Troubleshooting

### 12.1 Backend Issues

| Problem | Cause | Fix |
|---------|-------|-----|
| `RuntimeError: Missing required environment variable` | `.env` tidak diload | Pastikan file `.env` ada di `backend/` |
| `RuntimeError: JWT_SECRET must be at least 32 bytes` | Secret terlalu pendek | Generate baru: `python -c "import secrets; print(secrets.token_hex(64))"` |
| `RuntimeError: AES key must be exactly 32 bytes` | Key bukan 32 bytes | Generate: `python -c "import secrets,base64; print(base64.b64encode(secrets.token_bytes(32)).decode())"` |
| `sqlalchemy.exc.OperationalError: Can't connect to MySQL` | DB belum ready | Tunggu health check atau cek `DATABASE_URL` |
| `ImportError: No module named 'app'` | Cwd salah | Jalankan dari folder `backend/` |

### 12.2 Frontend Issues

| Problem | Cause | Fix |
|---------|-------|-----|
| Halaman blank setelah login | `useI18n()` tidak di-destructure | Tambahkan `const { t } = useI18n()` |
| CORS error di console | Backend FRONTEND_ORIGIN salah | Set `FRONTEND_ORIGIN=http://localhost:3000` |
| 403 pada POST/PUT/DELETE | CSRF mismatch | Clear cookies, login ulang |
| "Network Error" | Backend down | Cek `docker ps` atau `flask run` |

### 12.3 Docker Issues

| Problem | Cause | Fix |
|---------|-------|-----|
| `service_healthy: no matching containers` | Container belum start | `docker compose up -d` ulang |
| Backend restart loop | DB belum ready | Tunggu mysql healthy, lalu restart backend |
| Port already in use | Service lain pakai port | `docker compose down`, kill process, retry |
| Frontend not updating after code change | Cache | `docker compose build frontend --no-cache` |

---

## Related Documents

| Dokumen | Lokasi | Isi |
|---------|--------|-----|
| **User Manual** | `docs/USER_MANUAL.md` | Panduan pengguna + bukti implementasi (code evidence) |
| Database Documentation | `docs/DATABASE.md` | Schema overview & history |
| Database Mapping | `docs/DATABASE_MAPPING.md` | SQL ↔ MariaDB field mapping |
| Production Hardening | `docs/PRODUCTION_HARDENING.md` | Deploy checklist security |
| README | `README.md` | Quick start & overview |

---

*IAMS Development Guide v1.0 — 22 Juni 2026*
