# ðŸ“˜ User Manual â€” IAMS (Infrastructure Asset Management System)

**Versi:** 3.0 (Hybrid Edition)  
**Tanggal:** 22 Juni 2026  
**Penulis:** [Nama Mahasiswa Magang]  
**Pembimbing:** [Nama Pembimbing]

---

> **Cara baca dokumen ini:**
>
> - ðŸŽ¯ = Penjelasan simpel (untuk semua orang)
> - ðŸ“‹ = Langkah-langkah pakai fiturnya (step-by-step)
> - ðŸ”§ = Detail teknis (untuk pembimbing / developer)
>
> Kalau kamu **pengguna biasa**, cukup baca bagian ðŸŽ¯ dan ðŸ“‹ saja.

---

## Daftar Isi

**Bagian I â€” Panduan Pengguna**

1. [Apa itu IAMS?](#1-apa-itu-iams)
2. [Cara Masuk (Login)](#2-cara-masuk-login)
3. [Dashboard â€” Lihat Ringkasan](#3-dashboard--lihat-ringkasan)
4. [Kelola Aset IT](#4-kelola-aset-it)
5. [Laporkan Gangguan (Incident)](#5-laporkan-gangguan-incident)
6. [Catat Akar Masalah (Problem)](#6-catat-akar-masalah-problem)
7. [Buat Permintaan (Request)](#7-buat-permintaan-request)
8. [Ajukan Perubahan (Change)](#8-ajukan-perubahan-change)
9. [Lisensi Software](#9-lisensi-software)
10. [Data Master](#10-data-master)
11. [Kelola Pengguna](#11-kelola-pengguna)
12. [Audit Log â€” Siapa Ngapain](#12-audit-log--siapa-ngapain)
13. [Laporan & Export](#13-laporan--export)
14. [Ganti Bahasa & Dark Mode](#14-ganti-bahasa--dark-mode)
15. [FAQ â€” Pertanyaan Umum](#15-faq--pertanyaan-umum)

**Bagian II â€” Dokumentasi Teknis**

16. [Arsitektur Sistem](#16-arsitektur-sistem)
17. [Database & ERD](#17-database--erd)
18. [Keamanan Sistem](#18-keamanan-sistem)
19. [Instalasi & Deployment](#19-instalasi--deployment)
20. [API Reference](#20-api-reference)
21. [Use Case Scenario (End-to-End)](#21-use-case-scenario-end-to-end)
22. [Kontribusi Selama Magang](#22-kontribusi-selama-magang)
23. [Kendala & Solusi](#23-kendala--solusi)
24. [Kesimpulan & Saran](#24-kesimpulan--saran)
25. [Glossary](#25-glossary)
26. [Lampiran](#26-lampiran)
27. [Bukti Implementasi (Code Evidence)](#27-bukti-implementasi-code-evidence)

---

# BAGIAN I â€” PANDUAN PENGGUNA

---

## 1. Apa itu IAMS?

### ðŸŽ¯ Penjelasan Simpel

IAMS adalah **website internal kantor** untuk tim IT. Fungsinya kayak "buku besar digital" yang mencatat:

- **Semua perangkat IT** kantor (router, switch, laptop, printer, dll) â€” di mana letaknya, siapa yang pakai
- **Kalau ada gangguan** â€” dicatat, ditugaskan ke orang, dilacak sampai selesai
- **Kalau mau ganti/upgrade perangkat** â€” harus diajukan dulu, disetujui atasan
- **Password perangkat** â€” disimpan aman (terenkripsi), cuma admin yang bisa lihat
- **Siapa ngapain** â€” semua aktivitas tercatat otomatis, tidak bisa dihapus

### ðŸŽ¯ Siapa yang Pakai?

| Kamu adalah... | Di IAMS kamu bisa... |
|---|---|
| **Administrator** (IT Manager) | Semua hal â€” approve perubahan, lihat audit, hapus data, kelola user |
| **Operator** (IT Staff) | Kelola aset, catat gangguan, buat permintaan â€” tapi TIDAK bisa hapus data penting |

### ðŸŽ¯ Cara Akses

Buka browser (Chrome/Firefox/Edge), ketik:
```
https://localhost
```

> ðŸ’¡ **Tips:** Kalau di kantor, tanya admin alamat lengkapnya (mungkin `https://iams.kantorkamu.co.id`)

---

## 2. Cara Masuk (Login)

### ðŸŽ¯ Apa Fungsinya?

Halaman login â€” tempat kamu masukkan email dan password supaya bisa akses dashboard.

### ðŸ“‹ Langkah-langkah

**Step 1:** Buka halaman login

![Halaman Login](screenshots/annotated/02-login-page.png)

**Step 2:** Isi email dan password kamu

- **Email:** email kantor kamu (contoh: `admin@iams.local`)
- **Password:** password yang diberikan IT admin

**Step 3:** Klik tombol **"Masuk"**

![Login Terisi](screenshots/annotated/02b-login-filled.png)

**Step 4:** Kalau berhasil, kamu langsung masuk ke Dashboard âœ…

### ðŸ“‹ Kalau Gagal Login?

| Masalah | Solusi |
|---------|--------|
| "Invalid credentials" | Email atau password salah. Cek huruf besar/kecil. |
| Tidak bisa klik Masuk | Pastikan email dan password sudah diisi |
| Halaman blank / error | Refresh browser (Ctrl+F5), atau hubungi IT admin |
| Terkunci (5x salah) | Tunggu 1 menit, baru coba lagi |

### ðŸ“‹ Akun Demo (untuk testing)

| Role | Email | Password |
|------|-------|----------|
| Admin | `admin@iams.local` | `admin123` |
| Operator | `operator@iams.local` | `operator123` |

> âš¡ **Shortcut:** Di halaman login ada tombol "Administrator" dan "Operator" â€” klik langsung untuk isi otomatis.

### ðŸ”§ Detail Teknis

- Autentikasi: JWT disimpan di HttpOnly cookie (tidak bisa diakses JavaScript)
- CSRF: Double-submit cookie pattern
- Rate limit: Maksimal 5 percobaan login per menit
- Session expire: 8 jam
- API: `POST /api/auth/login` â†’ Set-Cookie access_token

---

## 3. Dashboard â€” Lihat Ringkasan

### ðŸŽ¯ Apa Fungsinya?

Halaman pertama setelah login. Menampilkan **ringkasan cepat** kondisi IT kantor â€” berapa aset, ada gangguan apa, masalah apa yang lagi ditangani.

### ðŸ“‹ Yang Kamu Lihat di Dashboard

![Dashboard](screenshots/annotated/03-dashboard.png)

| Kotak | Artinya |
|-------|---------|
| **Total Aset: 8** | Ada 8 perangkat IT tercatat di sistem |
| **5 aktif Â· 1 tersedia** | 5 sedang dipakai, 1 belum dipakai |
| **Insiden Terbuka: 3** | Ada 3 gangguan yang belum selesai |
| **1 critical** | 1 gangguan serius yang perlu ditangani segera |
| **Problem Aktif: 2** | 2 akar masalah sedang diinvestigasi |
| **Status Jaringan: Degraded** | Jaringan tidak 100% normal |

### ðŸ“‹ Grafik di Dashboard

- **Distribusi Aset** â€” berapa Router, Switch, Firewall, dll
- **Status Aset** â€” berapa yang Active, Available, Repair, Disposed

### ðŸ“‹ Mau ke Halaman Lain?

Klik menu di **sidebar kiri**:
- Aset â†’ kelola perangkat
- Insiden â†’ catat gangguan
- Problem â†’ akar masalah
- dst.

### ðŸ”§ Detail Teknis

- API: `GET /api/dashboard/summary`
- Data real-time dari database (tidak di-cache)
- Aggregasi: `GROUP BY status`, `GROUP BY category`

---

## 4. Kelola Aset IT

### ðŸŽ¯ Apa Fungsinya?

Tempat mencatat semua perangkat IT kantor â€” router, switch, firewall, printer, laptop, dll. Setiap perangkat punya:
- Kode unik (Asset Tag)
- Nomor seri dari pabrik
- Lokasi penempatan
- Siapa yang pakai
- Password/credential (terenkripsi aman)

### ðŸ“‹ Melihat Daftar Aset

**Step 1:** Klik **"Aset"** di sidebar kiri

![Daftar Aset](screenshots/annotated/04-assets-list.png)

**Step 2:** Kamu bisa:
- **Cari** â€” ketik di kolom pencarian (bisa cari pakai kode, serial number, atau model)
- **Filter** â€” pilih kategori (Router/Switch/dll), status (Active/Repair/dll), atau lokasi

![Filter Status Active](screenshots/annotated/04d-assets-filter-active.png)

### ðŸ“‹ Menambah Aset Baru

**Step 1:** Klik tombol **"Tambah Aset"** (pojok kanan atas)

**Step 2:** Isi form:

![Form Tambah Aset](screenshots/annotated/04b-assets-add-form.png)

| Yang harus diisi | Contoh | Keterangan |
|---|---|---|
| Asset Tag | `AST-RTR-003` | Kode unik buatan kamu |
| Serial Number | `FDO2234A5B6` | Dari label di perangkat |
| Model | Cisco ISR 4331 | Pilih dari dropdown |
| Lokasi | HQ Jakarta â€” DC Room | Pilih dari dropdown |

| Opsional | Contoh |
|---|---|
| User | Siapa yang pakai |
| Status | Active / Available / Repair |
| Tanggal Beli | 2024-01-15 |
| Garansi | 36 bulan |

**Step 3:** Klik **"Simpan"** âœ…

### ðŸ“‹ Mengedit Aset

Klik ikon pensil âœï¸ di baris aset yang mau diedit.

![Form Edit Aset](screenshots/annotated/04c-assets-edit-form.png)

### ðŸ“‹ Melihat Riwayat Pemakaian (Checkout History)

Klik ikon jam ðŸ• di baris aset â€” muncul siapa saja yang pernah pakai perangkat ini.

![Checkout History](screenshots/annotated/04e-assets-checkout-history.png)

### ðŸ“‹ Password Perangkat (Credential)

- Tersimpan **terenkripsi** â€” tidak bisa dibaca langsung dari database
- Hanya **Administrator** yang bisa klik "Reveal" untuk lihat password
- Setiap kali password dilihat, **tercatat di Audit Log**

### ðŸ”§ Detail Teknis

- Model: `Asset` (19 field) + `NetworkDetail` (1:1) + `AssetCredential` (1:N) + `AssetFile` (1:N)
- Enkripsi credential: AES-256-GCM (32-byte key, 12-byte nonce)
- File upload: max 10MB, stored as BLOB
- API: `GET/POST /api/assets`, `PUT/DELETE /api/assets/:id`
- Validasi: asset_tag + serial_number harus unique
- Status enum: Active, Available, Repair, Disposed

---

## 5. Laporkan Gangguan (Incident)

### ðŸŽ¯ Apa Fungsinya?

**Kapan pakai fitur ini?**
- Jaringan mati / lambat
- Perangkat error / tidak bisa diakses
- Printer offline
- Server down
- Apapun yang ganggu kerja orang lain

### ðŸ“‹ Cara Buat Laporan Gangguan

**Step 1:** Klik **"Insiden"** di sidebar

![Daftar Insiden](screenshots/annotated/05-incidents-list.png)

**Step 2:** Klik **"Insiden Baru"**

**Step 3:** Isi form:

![Form Insiden Baru](screenshots/annotated/05b-incidents-add-form.png)

| Yang diisi | Contoh |
|---|---|
| Judul | "Router lantai 3 mati" |
| Deskripsi | "Sejak jam 8 pagi, semua user lantai 3 tidak bisa internet" |
| Severity (seberapa parah) | Critical / High / Medium / Low |
| Aset terkait | Pilih perangkat yang bermasalah |
| Ditugaskan ke | Pilih teknisi yang akan handle |

**Step 4:** Klik **"Simpan"** â†’ otomatis dapat kode `INC-2026-0001`

### ðŸ“‹ Arti Severity (Tingkat Keparahan)

| Severity | Kapan dipilih? |
|----------|---------------|
| ðŸ”´ **Critical** | Banyak orang kena dampak, layanan utama mati |
| ðŸŸ  **High** | Sebagian orang terganggu, ada workaround |
| ðŸŸ¡ **Medium** | Gangguan kecil, tidak urgent |
| ðŸŸ¢ **Low** | Nyaman tapi bukan masalah besar |

### ðŸ“‹ Alur Status Insiden

```
Dibuat (Open) â†’ Sedang ditangani (In Progress) â†’ Selesai (Resolved) â†’ Ditutup (Closed)
```

### ðŸ”§ Detail Teknis

- Auto-code: `INC-{YEAR}-{SEQ:4}` (e.g. INC-2026-0001)
- Model: `Incident` â†’ FK ke `assets`, `users` (assignee)
- API: `GET/POST /api/incidents`, `PUT/DELETE /api/incidents/:id`
- Filter: status, severity, search (title + code)
- Delete: Administrator only

---

## 6. Catat Akar Masalah (Problem)

### ðŸŽ¯ Apa Fungsinya?

**Kapan pakai fitur ini?**
- Gangguan yang **berulang** (misal: router sering restart sendiri)
- Mau catat **kenapa** masalahnya terjadi (root cause)
- Sudah selesai investigasi dan mau dokumentasikan

Bedanya dengan Incident: **Incident = gejalanya, Problem = penyebabnya**

### ðŸ“‹ Cara Buat Problem

**Step 1:** Klik **"Problem"** di sidebar

![Daftar Problem](screenshots/annotated/06-problems-list.png)

**Step 2:** Klik **"Problem Baru"**

![Form Problem](screenshots/annotated/06b-problems-add-form.png)

**Step 3:** Isi:
- **Judul:** "Link utama sering flapping"
- **Root Cause:** "Firmware bug pada router versi 15.x"
- **Priority:** High
- **Owner:** Siapa yang investigasi

### ðŸ“‹ Alur Status

```
Open â†’ Investigating â†’ Known Error â†’ Closed
```

- **Known Error** = sudah tahu penyebabnya tapi belum fix

### ðŸ”§ Detail Teknis

- Auto-code: `PRB-{YEAR}-{SEQ:4}`
- Model: `Problem` â†’ FK ke `users` (owner)
- API: `GET/POST /api/problems`, `PUT/DELETE /api/problems/:id`
- Delete: Administrator only

---

## 7. Buat Permintaan (Request)

### ðŸŽ¯ Apa Fungsinya?

**Kapan pakai fitur ini?**
- Mau minta laptop baru
- Mau minta perbaikan perangkat
- Mau minta akses VPN / WiFi
- Mau pindahkan printer ke ruangan lain
- Mau minta apapun ke tim IT

### ðŸ“‹ Jenis Permintaan

| Tipe | Contoh |
|------|--------|
| ðŸ†• Aset | "Minta laptop baru untuk karyawan baru" |
| ðŸ”§ Perbaikan | "Tolong perbaiki router cabang Surabaya" |
| ðŸ”„ Penggantian | "Ganti switch yang sudah tua" |
| ðŸ“¦ Pemindahan | "Pindahkan printer ke lantai 3" |
| ðŸ”‘ Akses | "Minta akses VPN untuk remote working" |
| ðŸŒ Jaringan | "Tambah port network di ruang meeting" |
| â“ Lainnya | Yang tidak masuk kategori di atas |

### ðŸ“‹ Cara Buat Request

**Step 1:** Klik **"Permintaan"** di sidebar

![Daftar Request](screenshots/annotated/07-requests-list.png)

**Step 2:** Klik **"+ Buat Request"**

![Form Request](screenshots/annotated/07b-requests-add-form.png)

**Step 3:** Isi judul, pilih tipe, set prioritas, deadline

**Step 4:** Klik **"Simpan"** â†’ dapat kode `REQ-2026-0001`

### ðŸ“‹ Alur Status

```
Open â†’ In Progress â†’ Waiting Approval â†’ Approved â†’ Fulfilled â†’ Closed
                                       â†˜ Rejected
```

### ðŸ”§ Detail Teknis

- Auto-code: `REQ-{YEAR}-{SEQ:4}`
- 7 request types enum
- Model: `ServiceRequest` â†’ FK ke requester, assigned_to, asset, department
- Status transitions: 8 possible states
- API: `GET/POST /api/requests`, `PUT/DELETE /api/requests/:id`

---

## 8. Ajukan Perubahan (Change)

### ðŸŽ¯ Apa Fungsinya?

**Kapan pakai fitur ini?**
- Mau upgrade firmware router
- Mau ganti firewall ke model baru
- Mau tambah VLAN baru
- Mau patching keamanan
- **Intinya: semua perubahan pada infrastruktur harus diajukan dan disetujui dulu!**

Kenapa harus lewat sini? Supaya ada **rencana cadangan (rollback plan)** kalau gagal, dan ada yang **approve** sebelum dikerjakan.

### ðŸ“‹ Cara Ajukan Perubahan

**Step 1:** Klik **"Perubahan"** di sidebar

![Daftar Change](screenshots/annotated/08-changes-list.png)

**Step 2:** Klik **"+ Buat Perubahan"**

![Form Change](screenshots/annotated/08b-changes-add-form.png)

**Step 3:** Isi:
- **Judul:** "Upgrade firmware router core HQ"
- **Tipe:** Maintenance / Replacement / Emergency / dll
- **Risk Level:** seberapa berisiko (Low/Medium/High/Critical)
- **Impact:** seberapa besar dampak kalau gagal
- **Rollback Plan:** "Kalau gagal, downgrade ke versi lama"
- **Jadwal:** kapan mulai dan selesai

**Step 4:** Klik **"Simpan"** â†’ dapat kode `CHG-2026-0001`

### ðŸ“‹ Proses Approval

| Langkah | Siapa | Apa yang terjadi |
|---------|-------|-----------------|
| 1. Buat & Submit | Kamu (operator/admin) | Status: Submitted |
| 2. Review | Admin lain | Baca detail + rollback plan |
| 3. Approve âœ… | Admin lain | Status: Approved â†’ bisa dikerjakan |
| 3. Reject âŒ | Admin lain | Status: Rejected â†’ harus revisi |

> âš ï¸ **Aturan:** Kamu TIDAK bisa approve perubahan yang kamu sendiri ajukan (harus admin lain)

### ðŸ”§ Detail Teknis

- Auto-code: `CHG-{YEAR}-{SEQ:4}`
- 8 change types, 4 risk levels, 4 impact levels, 11 status states
- Self-approval blocked (requester_id â‰  approver_id)
- Model: `ChangeRequest` â†’ FK ke requester, assignee, approver, asset, incident, problem, request
- API: `GET/POST /api/changes`, `POST /api/changes/:id/approve|reject`

---

## 9. Lisensi Software

### ðŸŽ¯ Apa Fungsinya?

Tempat catat semua lisensi software yang dibeli kantor â€” biar tahu kapan expired dan berapa sisa seat.

### ðŸ“‹ Cara Pakai

**Step 1:** Klik **"Lisensi"** di sidebar

![Daftar Lisensi](screenshots/annotated/09-licenses-list.png)

**Step 2:** Klik **"+ Lisensi"** untuk tambah baru

**Step 3:** Isi nama software, product key, jumlah seat, tanggal kadaluarsa

### ðŸ“‹ Kapan Harus Cek?

- Sebelum beli lisensi baru â†’ cek dulu sudah punya belum
- Tiap awal bulan â†’ cek mana yang mau expired
- Mau deploy software â†’ cek masih ada seat kosong tidak

### ðŸ”§ Detail Teknis

- Model: `SoftwareLicense` (name, product_key, seats, expiration_date)
- API: `GET/POST /api/licenses`, `PUT/DELETE /api/licenses/:id`
- Delete: Administrator only

---

## 10. Data Master

### ðŸŽ¯ Apa Fungsinya?

Data referensi yang dipakai di seluruh sistem. Ibaratnya "daftar pilihan" yang muncul di dropdown form lain.

**Hanya Administrator** yang bisa tambah/edit/hapus.

### ðŸ“‹ Apa Saja Data Master?

| Tab | Isinya | Contoh |
|-----|--------|--------|
| Departemen | Divisi kantor | Infrastructure, Network Ops, IT Service Desk |
| Lokasi | Tempat fisik | HQ Jakarta DC Room, Branch Surabaya |
| Kategori | Jenis perangkat | Router, Switch, Firewall, Printer |
| Merek | Brand | Cisco, MikroTik, HP, Fortinet |
| Model | Tipe perangkat | ISR 4331, Catalyst 9300, FortiGate 100F |

### ðŸ“‹ Cara Tambah

**Step 1:** Klik **"Data Master"** di sidebar

![Master Data](screenshots/annotated/10-master-data.png)

**Step 2:** Pilih tab yang mau ditambah (Departemen/Lokasi/dll)

**Step 3:** Klik **"+ Department"** (atau + Location, dll)

![Form Master Data](screenshots/annotated/10b-master-data-add-form.png)

**Step 4:** Isi nama dan keterangan â†’ **"Simpan"**

### ðŸ“‹ Kenapa Tidak Bisa Hapus?

Kalau kamu coba hapus tapi muncul error **"Cannot delete, still in use"** â€” artinya data itu masih dipakai di tempat lain. Contoh: tidak bisa hapus departemen "Infrastructure" kalau masih ada user yang terdaftar di departemen itu.

### ðŸ”§ Detail Teknis

- 5 entitas: Department, Location, Category, Brand, DeviceModel
- Delete safety: cek FK references sebelum delete (409 Conflict)
- API: `GET/POST/PUT/DELETE /api/{departments|locations|categories|brands|models}[/:id]`
- Read: Admin + Operator; Write: Admin only

---

## 11. Kelola Pengguna

### ðŸŽ¯ Apa Fungsinya?

Tempat admin menambah user baru, ganti role, atau nonaktifkan akun.

> ðŸ”’ **Halaman ini hanya bisa diakses Administrator**

### ðŸ“‹ Cara Tambah User Baru

**Step 1:** Klik **"Pengguna / Role"** di sidebar

![Users & Roles](screenshots/annotated/11-users-roles.png)

**Step 2:** Klik **"Tambah User"**

![Form Tambah User](screenshots/annotated/11b-users-add-form.png)

**Step 3:** Isi:
- Nama lengkap
- Email (untuk login)
- Password
- Role: Administrator atau Operator
- Departemen

### ðŸ“‹ Menonaktifkan User

Klik **"Nonaktifkan"** di baris user â†’ user tersebut tidak bisa login lagi, tapi datanya tetap tersimpan (bisa diaktifkan kembali nanti).

### ðŸ“‹ Menghapus User

Klik **"Hapus"** â†’ data user dihapus **permanen** (tidak bisa dikembalikan!)

### ðŸ”§ Detail Teknis

- Model: `User` â†’ FK ke Role, Department
- Password: bcrypt hash (12 rounds), never stored plaintext
- Deactivate: soft-delete (is_active=false)
- API: `GET/POST /api/users`, `PUT/DELETE /api/users/:id`
- Only Administrator can access

---

## 12. Audit Log â€” Siapa Ngapain

### ðŸŽ¯ Apa Fungsinya?

Catatan otomatis **semua aktivitas** di sistem. Tidak bisa diedit, tidak bisa dihapus. Kayak CCTV digital.

Contoh yang tercatat:
- Siapa login jam berapa
- Siapa tambah/edit/hapus aset
- Siapa lihat password perangkat
- Siapa approve/reject perubahan
- Siapa gagal login (salah password)

> ðŸ”’ **Hanya Administrator** yang bisa lihat halaman ini

### ðŸ“‹ Cara Lihat

**Step 1:** Klik **"Audit Log"** di sidebar

![Audit Logs](screenshots/annotated/12-audit-logs.png)

**Step 2:** Bisa filter:
- **Action:** LOGIN, CREATE, UPDATE, DELETE, REVEAL, APPROVE
- **Status:** success / failure
- **Search:** cari berdasarkan email atau resource

### ðŸ“‹ Contoh Isi Log

| Waktu | Siapa | Aksi | Apa | Status |
|-------|-------|------|-----|--------|
| 22 Jun, 05:04 | admin@iams.local | LOGIN | session | âœ… success |
| 22 Jun, 05:03 | ??? | ACCESS_DENIED | auth | âŒ failure |

### ðŸ”§ Detail Teknis

- Model: `AuditLog` (append-only, no update/delete endpoint)
- Fields: actor_user_id, action, resource_type, resource_id, status, ip_address, metadata_redacted
- Metadata di-redact (sensitive keys di-mask otomatis)
- API: `GET /api/audit-logs` (Admin only)
- Pagination: 10 per page, sortable by timestamp

---

## 13. Laporan & Export

### ðŸŽ¯ Apa Fungsinya?

Halaman untuk bikin laporan â€” terutama:
- Mau lihat semua aset sekaligus
- Mau cek perangkat yang garansinya mau habis
- Mau download data ke Excel/CSV

> ðŸ”’ **Hanya Administrator**

### ðŸ“‹ Cara Pakai

**Step 1:** Klik **"Laporan"** di sidebar

![Reports](screenshots/annotated/13-reports.png)

**Step 2:** Pilih jenis laporan:

| Jenis | Fungsi |
|-------|--------|
| **Export CSV** | Download semua data aset ke file CSV (bisa buka di Excel) |
| **Warranty Watch** | Lihat perangkat yang garansinya mau habis |

### ðŸ“‹ Indikator Garansi

| Warna | Artinya |
|-------|---------|
| ðŸ”´ Critical (0 hari) | Garansi sudah habis! |
| ðŸŸ¡ High (< 90 hari) | Segera perpanjang/siapkan budget |
| ðŸŸ¢ OK | Masih aman |

### ðŸ”§ Detail Teknis

- API: `GET /api/reports/assets/full`, `/assets/status-summary`, `/assets/warranty-expiring?months=3`
- Warranty calculation: `purchase_date + (warranty_months Ã— 30 days)`
- CSV export: client-side generation dari paginated data
- Max 500 rows per page

---

## 14. Ganti Bahasa & Dark Mode

### ðŸŽ¯ Apa Fungsinya?

- **Ganti bahasa:** switch antara Bahasa Indonesia dan English
- **Dark mode:** ganti tampilan gelap (enak buat mata di malam hari)

### ðŸ“‹ Cara Ganti Bahasa

Klik tombol **"id"** atau **"en"** di pojok kanan atas (sebelah ikon notifikasi)

![English Mode](screenshots/annotated/15-dashboard-english.png)

### ðŸ“‹ Cara Aktifkan Dark Mode

Klik ikon **ðŸŒ™ bulan** di pojok kanan atas

![Dark Mode](screenshots/annotated/14-dashboard-dark-mode.png)

> ðŸ’¡ Preferensi kamu disimpan otomatis â€” next time buka, tetap pakai setting terakhir.

### ðŸ”§ Detail Teknis

- i18n: vue-i18n v9, 2 locale files (id.js, en.js), ~600 keys each
- Theme: TailwindCSS `dark:` prefix, View Transitions API (120fps)
- Persistence: localStorage (`iams-locale`, `iams-theme`)

---

## 15. FAQ â€” Pertanyaan Umum

### â“ "Saya lupa password, gimana?"

Hubungi Administrator untuk reset password kamu. Belum ada fitur "Lupa Password" via email.

### â“ "Tombol Hapus tidak ada di halaman saya?"

Kamu login sebagai **Operator**. Hanya Administrator yang bisa menghapus data.

### â“ "Data tidak muncul / halaman kosong?"

1. Coba refresh (Ctrl+F5)
2. Cek koneksi internet
3. Coba logout dan login ulang
4. Kalau masih kosong, hubungi Admin

### â“ "Saya tidak bisa akses halaman Master Data / Audit Log / Reports?"

Halaman tersebut hanya untuk **Administrator**. Kalau kamu Operator, memang tidak bisa akses.

### â“ "Saya mau approve Change tapi tidak bisa?"

Aturannya: kamu **tidak bisa approve perubahan yang kamu sendiri buat**. Harus admin lain yang approve.

### â“ "Muncul error 'Cannot delete, still in use'?"

Data yang mau kamu hapus masih dipakai di tempat lain. Misalnya:
- Hapus departemen â†’ masih ada user di departemen itu
- Hapus model â†’ masih ada aset pakai model itu
- Solusi: pindahkan dulu data yang terkait, baru hapus

### â“ "Credential/password perangkat aman tidak?"

Aman. Password perangkat disimpan **terenkripsi** (AES-256-GCM). Bahkan admin database tidak bisa baca tanpa key. Hanya Administrator yang bisa "Reveal" dan setiap reveal tercatat di Audit Log.

### â“ "Gimana cara export data ke Excel?"

Buka halaman **Laporan** â†’ klik tombol **"Export CSV Aset"**. File CSV bisa dibuka di Excel / Google Sheets.

---

# BAGIAN II â€” DOKUMENTASI TEKNIS

---

## 16. Arsitektur Sistem

### 16.1 Diagram Arsitektur

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚                        CLIENT (Browser)                          â”‚
â”‚                    Vue 3 SPA + TailwindCSS                       â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                               â”‚ HTTPS (TLS 1.2/1.3)
                               â–¼
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚                     NGINX (Reverse Proxy)                        â”‚
â”‚          SSL Termination â”‚ Gzip â”‚ Security Headers              â”‚
â”‚              Port 80/443 â†’ Frontend + Backend                   â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
               â”‚ / (static)                        â”‚ /api/*
               â–¼                                   â–¼
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”           â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚  Frontend Container  â”‚           â”‚      Backend Container       â”‚
â”‚   Nginx + Vue build  â”‚           â”‚   Flask 3 + Gunicorn         â”‚
â”‚   Port 3000          â”‚           â”‚   SQLAlchemy 2.0 ORM         â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜           â”‚   Port 5000                  â”‚
                                   â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                                              â”‚          â”‚
                                              â–¼          â–¼
                               â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â” â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
                               â”‚   MariaDB 10.11  â”‚ â”‚  Redis 7    â”‚
                               â”‚   19 tables      â”‚ â”‚ Rate Limit  â”‚
                               â”‚   Port 3306      â”‚ â”‚ Port 6379   â”‚
                               â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜ â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

### 16.2 Tech Stack Detail

| Layer | Teknologi | Versi |
|-------|-----------|-------|
| Frontend | Vue 3 + Vite + Pinia + TailwindCSS + vue-i18n + motion-v | Vue 3.4, Vite 8 |
| Backend | Flask + SQLAlchemy + Alembic + Gunicorn | Flask 3.0.3, SQLAlchemy 2.0.51 |
| Database | MariaDB | 10.11 |
| Cache | Redis | 7 (Alpine) |
| Proxy | Nginx | Alpine |
| Container | Docker Compose | v2 |
| Security | JWT (PyJWT) + bcrypt + cryptography (AES-GCM) | PyJWT 2.10, bcrypt 4.1 |

### 16.3 Folder Structure

```
â”œâ”€â”€ frontend/src/
â”‚   â”œâ”€â”€ components/         # 50+ reusable UI components
â”‚   â”œâ”€â”€ pages/              # 14 page views
â”‚   â”œâ”€â”€ router/             # Auth guard + RBAC meta
â”‚   â”œâ”€â”€ stores/             # Pinia (auth, locale, theme, ui)
â”‚   â”œâ”€â”€ services/           # apiClient.js (CSRF + retry)
â”‚   â””â”€â”€ i18n/locales/       # id.js, en.js (~600 keys)
â”œâ”€â”€ backend/app/
â”‚   â”œâ”€â”€ routes/             # 14 blueprints
â”‚   â”œâ”€â”€ utils/              # security, audit, decorators, pagination
â”‚   â”œâ”€â”€ models.py           # 19 SQLAlchemy models
â”‚   â””â”€â”€ commands.py         # flask seed CLI
â””â”€â”€ docker-compose.yml      # 5 services
```

---

## 17. Database & ERD

### 17.1 Entity Relationship Diagram

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”    â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”    â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚  roles   â”‚â—„â”€â”€â”€â”‚    users     â”‚â”€â”€â”€â–ºâ”‚departmentsâ”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜    â””â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”˜    â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                       â”‚ 1:N
                       â–¼
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”    â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”    â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚  brands  â”‚â”€â”€â”€â–ºâ”‚   models     â”‚â—„â”€â”€â”€â”‚categories â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜    â””â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”˜    â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                       â”‚ 1:N
                       â–¼
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”    â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”    â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚locations â”‚â—„â”€â”€â”€â”‚    assets     â”‚â”€â”€â”€â–ºâ”‚ network_details  â”‚ (1:1)
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜    â””â”€â”€â”¬â”€â”€â”€â”¬â”€â”€â”€â”¬â”€â”€â”€â”˜    â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                   â”‚   â”‚   â”‚
         â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜   â”‚   â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
         â–¼             â–¼                 â–¼
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â” â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â” â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚asset_credentialsâ”‚ â”‚asset_files â”‚ â”‚checkout_history  â”‚
â”‚(AES-256-GCM)  â”‚ â”‚(BLOB â‰¤10MB)â”‚ â”‚(check-in/out log)â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜ â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜ â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜

â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”    â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”    â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚  incidents   â”‚    â”‚   problems   â”‚    â”‚  change_requests â”‚
â”‚(INC-YYYY-N)  â”‚    â”‚(PRB-YYYY-N)  â”‚    â”‚(CHG-YYYY-N)      â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜    â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜    â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜

â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”    â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”    â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚service_requests  â”‚    â”‚  audit_logs  â”‚    â”‚software_     â”‚
â”‚(REQ-YYYY-N)      â”‚    â”‚(append-only) â”‚    â”‚licenses      â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜    â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜    â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜

                        â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
                        â”‚status_labels â”‚
                        â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

### 17.2 Tabel Detail (19 tabel)

| # | Tabel | PK | Fields | Relasi |
|---|-------|----|--------|--------|
| 1 | roles | id | name, is_active | â†’ users |
| 2 | departments | id | name, description | â†’ users |
| 3 | locations | id | name, description | â†’ assets |
| 4 | categories | id | name, description | â†’ models |
| 5 | brands | id | name, description | â†’ models |
| 6 | models | id | name, brand_id, category_id, specifications | â†’ assets |
| 7 | users | id | name, email, password_hash, role_id, department_id, is_active, last_login | â†’ assets, incidents, etc |
| 8 | assets | id | asset_tag(U), serial_number(U), po_number, model_id, location_id, user_id, status, purchase_date, warranty_months, os_license | Core entity |
| 9 | network_details | asset_id | ip_address, mac_address, hostname, vlan, notes | â†’ asset (1:1) |
| 10 | asset_credentials | id | asset_id, credential_type, username, encrypted_secret, nonce, notes | â†’ asset (1:N) |
| 11 | asset_files | id | asset_id, filename, original_name, mime_type, size, data(BLOB) | â†’ asset (1:N) |
| 12 | incidents | id | code(U), title, description, asset_id, severity, status, assignee_id | ITSM |
| 13 | problems | id | code(U), title, root_cause_summary, priority, status, owner_id | ITSM |
| 14 | service_requests | id | request_number(U), title, request_type, priority, status, requester_id, assigned_to_id, asset_id, department_id, due_date, resolution_notes, closed_at | ITSM |
| 15 | change_requests | id | change_number(U), title, change_type, risk_level, impact, status, requester_id, assignee_id, approver_id, asset_id, incident_id, problem_id, request_id, planned_start/end, implementation_notes, rollback_plan, approval_notes, closed_at | ITSM |
| 16 | audit_logs | id | actor_user_id, action, resource_type, resource_id, status, ip_address, user_agent, metadata_redacted | Compliance |
| 17 | status_labels | id | name, deployable | Config |
| 18 | software_licenses | id | name, product_key, seats, licensed_to_email, purchase_date, expiration_date, notes | Asset mgmt |
| 19 | checkout_history | id | asset_id, user_id, action, expected_return_date, notes, checked_out_by | Tracking |

---

## 18. Keamanan Sistem

### 18.1 Security Layers

| # | Aspek | Implementasi |
|---|-------|-------------|
| 1 | Autentikasi | JWT in HttpOnly cookie (8h expiry) |
| 2 | CSRF | Double-submit cookie (header vs cookie) |
| 3 | Password | bcrypt 12 rounds |
| 4 | Credential Storage | AES-256-GCM (32-byte key, 12-byte nonce) |
| 5 | CORS | Explicit origin whitelist |
| 6 | Rate Limiting | 5 login/min (Redis-backed) |
| 7 | RBAC | Decorator: @admin_only, @admin_or_operator |
| 8 | Headers | HSTS, X-Frame-Options DENY, CSP, X-Content-Type-Options |
| 9 | TLS | 1.2/1.3 via Nginx |
| 10 | Audit | Append-only, auto-redact sensitive metadata |
| 11 | Startup | Fail-fast: reject weak JWT_SECRET / invalid AES key |
| 12 | Error | Sanitize paths/stacktraces from responses |
| 13 | Validation | Server-side per endpoint |
| 14 | Delete Safety | FK reference check before delete |

### 18.2 AES-256-GCM Flow

```
ENCRYPT:
  plaintext + key(32B) + nonce(12B random)
  â†’ AESGCM.encrypt(nonce, plaintext, None)
  â†’ store: base64(ciphertext), base64(nonce)

DECRYPT (admin only, audited):
  base64_decode(ciphertext) + base64_decode(nonce) + key
  â†’ AESGCM.decrypt(nonce, ciphertext, None)
  â†’ plaintext
```

### 18.3 CSRF Double-Submit

```
1. GET /api/auth/csrf-token â†’ Set-Cookie: csrf_token=abc (readable)
2. POST /api/assets â†’ Header: X-CSRF-Token: abc + Cookie: csrf_token=abc
3. Backend: if header â‰  cookie â†’ 403 + audit log
```

---

## 19. Instalasi & Deployment

### 19.1 Prasyarat

- Docker & Docker Compose v2
- Port 80, 443, 3000, 5000 tersedia
- RAM â‰¥ 2GB

### 19.2 Quick Start

```bash
git clone https://github.com/0xshalah/iams-revisi.git && cd iams-revisi
cp .env.example .env
# Edit .env: generate JWT_SECRET & AES_KEY_BASE64
docker compose up --build -d
docker exec iams_backend flask seed
# Open: https://localhost
```

### 19.3 Generate Secrets

```bash
# JWT_SECRET (min 32 chars):
python -c "import secrets; print(secrets.token_hex(64))"

# AES_KEY_BASE64 (32 bytes, base64):
python -c "import secrets,base64; print(base64.b64encode(secrets.token_bytes(32)).decode())"
```

### 19.4 Environment Variables

| Variable | Required | Contoh |
|----------|----------|--------|
| DATABASE_URL | âœ… | mysql+pymysql://iams:pass@mysql:3306/iams_db |
| JWT_SECRET | âœ… | (min 32 chars hex) |
| AES_KEY_BASE64 | âœ… | (32 bytes base64) |
| FRONTEND_ORIGIN | âœ… | http://localhost:3000 |
| FLASK_ENV | | development / production |
| COOKIE_SECURE | | false (dev) / true (prod) |
| COOKIE_SAMESITE | | Lax (dev) / Strict (prod) |
| RATELIMIT_ENABLED | | true |
| RATELIMIT_STORAGE_URI | | memory:// / redis://redis:6379/0 |

### 19.5 Run Tests

```bash
docker exec -e RATELIMIT_ENABLED=false iams_backend python -m pytest tests/ -v
# Expected: 19 passed
```

---

## 20. API Reference

### 20.1 Authentication (4 endpoints)

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | /api/auth/csrf-token | - | Get CSRF token |
| POST | /api/auth/login | - | Login (5/min rate limit) |
| POST | /api/auth/logout | Auth+CSRF | Logout |
| GET | /api/auth/me | Auth | Current user |

### 20.2 Assets (19 endpoints)

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET/POST | /api/assets | A/O | List / Create |
| GET/PUT/DELETE | /api/assets/:id | A/O (DEL: Admin) | Get / Update / Delete |
| GET/PUT | /api/assets/:id/network-details | A/O | Network info |
| GET/POST | /api/assets/:id/credentials | A/O | Credentials |
| PUT/DELETE | /api/assets/:id/credentials/:cid | A/O (DEL: Admin) | Credential ops |
| GET | /api/assets/:id/credentials/:cid/reveal | Admin | Reveal (audited) |
| GET/POST/DELETE | /api/assets/:id/files[/:fid] | A/O (DEL: Admin) | File attachments |
| POST | /api/assets/:id/checkout | A/O | Checkout |
| POST | /api/assets/:id/checkin | A/O | Checkin |
| GET | /api/assets/:id/history | A/O | History |

### 20.3 ITSM (22 endpoints)

| Module | Methods | Path | Auth |
|--------|---------|------|------|
| Incidents | GET/POST/PUT/DELETE | /api/incidents[/:id] | A/O (DEL: Admin) |
| Problems | GET/POST/PUT/DELETE | /api/problems[/:id] | A/O (DEL: Admin) |
| Requests | GET/POST/PUT/DELETE | /api/requests[/:id] | A/O (DEL: Admin) |
| Changes | GET/POST/PUT/DELETE | /api/changes[/:id] | A/O (DEL: Admin) |
| Changes | POST | /api/changes/:id/approve | Admin |
| Changes | POST | /api/changes/:id/reject | Admin |

### 20.4 Master Data, Users, Reports, Other (30+ endpoints)

| Module | Path Pattern | Auth |
|--------|-------------|------|
| Departments | /api/departments[/:id] | Read: All, Write: Admin |
| Locations | /api/locations[/:id] | Read: All, Write: Admin |
| Categories | /api/categories[/:id] | Read: All, Write: Admin |
| Brands | /api/brands[/:id] | Read: All, Write: Admin |
| Models | /api/models[/:id] | Read: All, Write: Admin |
| Users | /api/users[/:id] | Admin |
| Roles | /api/roles | Admin |
| Audit Logs | /api/audit-logs | Admin |
| Reports | /api/reports/assets/* | Admin |
| Dashboard | /api/dashboard/summary | A/O |
| Licenses | /api/licenses[/:id] | A/O (DEL: Admin) |
| Status Labels | /api/status-labels[/:id] | A/O (Write: Admin) |

---

## 21. Use Case Scenario (End-to-End)

### 21.1 Skenario: Router Kantor Mati

| Step | Siapa | Aksi di IAMS | Modul |
|------|-------|-------------|-------|
| 1 | Operator | Buat Incident: "Router lantai 3 mati", severity=Critical | Incident |
| 2 | Admin | Assign ke teknisi, status â†’ In Progress | Incident |
| 3 | Teknisi | Investigasi: masalah berulang (flapping) | - |
| 4 | Teknisi | Buat Problem: "Firmware bug versi 15.x" | Problem |
| 5 | Teknisi | Status problem â†’ Known Error | Problem |
| 6 | Admin | Buat Change: "Upgrade firmware", rollback plan siap | Change |
| 7 | Admin lain | Approve change request | Change |
| 8 | Teknisi | Eksekusi upgrade, status â†’ Completed | Change |
| 9 | Teknisi | Close incident + close problem | Incident, Problem |
| 10 | Otomatis | Semua tercatat di Audit Log | Audit |

### 21.2 Skenario: Karyawan Baru Butuh Laptop

| Step | Siapa | Aksi | Modul |
|------|-------|------|-------|
| 1 | Operator | Buat Request: "Laptop baru tim finance" type=Asset Request | Request |
| 2 | Admin | Approve request | Request |
| 3 | Admin | Checkout laptop dari inventory â†’ assign ke user baru | Asset |
| 4 | Admin | Status request â†’ Fulfilled â†’ Closed | Request |

---

## 22. Kontribusi Selama Magang

| # | Kontribusi | Detail |
|---|-----------|--------|
| 1 | Database design | 19 tabel relasional dari schema supervisor |
| 2 | Backend API | 86 endpoint Flask + security decorators |
| 3 | Frontend SPA | 14 halaman Vue 3 + 50+ komponen |
| 4 | Credential encryption | AES-256-GCM implementation |
| 5 | Audit system | Append-only trail + metadata redaction |
| 6 | ITSM modules | Incident, Problem, Request, Change + interlinking |
| 7 | Approval workflow | Multi-level with self-approval blocking |
| 8 | i18n | 2 bahasa, ~600 translation keys |
| 9 | Docker deployment | 5-service orchestration |
| 10 | Security | JWT, CSRF, CORS, rate limiting, security headers |
| 11 | Testing | 19 integration tests (pytest) |
| 12 | Documentation | User manual, DB docs, production checklist |

---

## 23. Kendala & Solusi

| # | Kendala | Solusi |
|---|---------|--------|
| 1 | Schema PostgreSQL â†’ target MariaDB | Tulis mapping document, adaptasi tipe data |
| 2 | Credential harus aman tapi bisa di-reveal | AES-256-GCM + audit setiap reveal |
| 3 | Vue i18n `t()` undefined â†’ halaman blank | Tambahkan `const { t } = useI18n()` di setiap page |
| 4 | Container restart loop (DB belum ready) | depends_on + condition: service_healthy |
| 5 | CSRF mismatch saat request pertama | Auto-refresh token + retry logic |
| 6 | Rate limiter reset saat restart | Redis sebagai persistent storage |
| 7 | Halaman Licenses kosong saat demo | Tambahkan seed data di flask seed command |

---

## 24. Kesimpulan & Saran

### 24.1 Kesimpulan

1. IAMS berhasil dibangun sebagai platform terpusat manajemen aset IT (13 modul)
2. ITSM terintegrasi: incident â†’ problem â†’ change saling terhubung
3. Keamanan: AES-256-GCM credential, JWT HttpOnly, audit append-only
4. Deployment: satu command `docker compose up` untuk full stack
5. UX: multi-language, dark mode, responsive

### 24.2 Saran Pengembangan

| # | Saran | Prioritas |
|---|-------|-----------|
| 1 | Notifikasi email (incident assigned, change approved) | High |
| 2 | LDAP/Active Directory integration | High |
| 3 | Backup otomatis + disaster recovery | High |
| 4 | Dashboard real-time (WebSocket) | Medium |
| 5 | SLA tracking per incident | Medium |
| 6 | Barcode/QR code asset tagging | Medium |
| 7 | Network topology visualization | Medium |
| 8 | Mobile app | Low |
| 9 | Knowledge Base module | Low |
| 10 | Multi-tenant support | Low |

---

## 25. Glossary

| Istilah | Arti Simpel | Definisi Teknis |
|---------|-------------|-----------------|
| **Aset** | Perangkat IT kantor | Entitas di tabel `assets` dengan identitas unik |
| **Incident** | Gangguan / masalah mendadak | Unplanned interruption to IT service |
| **Problem** | Akar penyebab gangguan | Root cause of one or more incidents |
| **Change** | Perubahan yang direncanakan | Planned modification to IT infrastructure |
| **Request** | Permintaan ke tim IT | Formal request for IT services |
| **RBAC** | Hak akses berdasarkan jabatan | Role-Based Access Control |
| **Credential** | Password perangkat (terenkripsi) | AES-256-GCM encrypted secret |
| **Audit Log** | Catatan aktivitas (tidak bisa dihapus) | Append-only activity record |
| **CSRF** | Perlindungan dari serangan web | Cross-Site Request Forgery prevention |
| **JWT** | Token login (tersimpan aman) | JSON Web Token in HttpOnly cookie |
| **Seed** | Data contoh awal | Sample data injected via CLI command |
| **Docker** | "Kotak" untuk jalankan aplikasi | Container orchestration platform |
| **API** | Jembatan frontend â†” backend | REST Application Programming Interface |
| **VLAN** | Pembagian jaringan virtual | Virtual Local Area Network |
| **EOL** | Perangkat sudah pensiun | End of Life |

---

## 26. Lampiran

### Lampiran A: Daftar Screenshot (26 file)

| # | File | Keterangan |
|---|------|------------|
| 1 | 01-landing-page.png | Landing page (full scroll) |
| 2 | 02-login-page.png | Login form kosong |
| 3 | 02b-login-filled.png | Login form terisi |
| 4 | 03-dashboard.png | Dashboard KPI |
| 5 | 04-assets-list.png | Daftar aset |
| 6 | 04b-assets-add-form.png | Form tambah aset |
| 7 | 04c-assets-edit-form.png | Form edit aset |
| 8 | 04d-assets-filter-active.png | Filter status=Active |
| 9 | 04e-assets-checkout-history.png | Checkout history |
| 10 | 05-incidents-list.png | Daftar insiden |
| 11 | 05b-incidents-add-form.png | Form tambah insiden |
| 12 | 06-problems-list.png | Daftar problem |
| 13 | 06b-problems-add-form.png | Form tambah problem |
| 14 | 07-requests-list.png | Daftar request |
| 15 | 07b-requests-add-form.png | Form buat request |
| 16 | 08-changes-list.png | Daftar change |
| 17 | 08b-changes-add-form.png | Form buat change |
| 18 | 09-licenses-list.png | Daftar lisensi |
| 19 | 10-master-data.png | Master data |
| 20 | 10b-master-data-add-form.png | Form master data |
| 21 | 11-users-roles.png | Users & roles |
| 22 | 11b-users-add-form.png | Form tambah user |
| 23 | 12-audit-logs.png | Audit logs |
| 24 | 13-reports.png | Reports |
| 25 | 14-dashboard-dark-mode.png | Dark mode |
| 26 | 15-dashboard-english.png | English language |

### Lampiran B: Cara Generate Secret

```bash
# JWT Secret (copy output ke .env)
python -c "import secrets; print(secrets.token_hex(64))"

# AES Key (copy output ke .env)
python -c "import secrets,base64; print(base64.b64encode(secrets.token_bytes(32)).decode())"
```

### Lampiran C: Docker Commands

```bash
# Start semua
docker compose up -d

# Rebuild setelah code change
docker compose up --build -d

# Lihat logs
docker logs iams_backend -f

# Seed data
docker exec iams_backend flask seed

# Run tests
docker exec -e RATELIMIT_ENABLED=false iams_backend python -m pytest tests/ -v

# Stop semua
docker compose down

# Stop + hapus data
docker compose down -v
```

### Lampiran D: Bukti Test Results (29 Passed)

```
============================= test session starts ==============================
platform linux -- Python 3.13.14, pytest-8.3.5, pluggy-1.6.0
rootdir: /app
plugins: flask-1.3.0
collected 29 items

tests/test_security.py::TestAuth::test_admin_login_success PASSED        [  3%]
tests/test_security.py::TestAuth::test_operator_login_success PASSED     [  6%]
tests/test_security.py::TestAuth::test_login_failure_generic PASSED      [ 10%]
tests/test_security.py::TestAuth::test_jwt_not_in_response_body PASSED   [ 13%]
tests/test_security.py::TestAuth::test_failed_login_audited_no_secret PASSED [ 17%]
tests/test_security.py::TestCsrf::test_missing_csrf_rejected PASSED      [ 20%]
tests/test_security.py::TestCsrf::test_auth_without_csrf_is_rejected PASSED [ 24%]
tests/test_security.py::TestRbac::test_operator_cannot_access_users PASSED [ 27%]
tests/test_security.py::TestRbac::test_operator_cannot_access_roles PASSED [ 31%]
tests/test_security.py::TestRbac::test_operator_cannot_access_audit_logs PASSED [ 34%]
tests/test_security.py::TestRbac::test_operator_cannot_delete_asset PASSED [ 37%]
tests/test_security.py::TestRbac::test_operator_can_list_assets PASSED   [ 41%]
tests/test_security.py::TestRbac::test_admin_can_access_users PASSED     [ 44%]
tests/test_security.py::TestRbac::test_admin_can_access_audit_logs PASSED [ 48%]
tests/test_security.py::TestCredentialSecurity::test_credential_status_no_leak PASSED [ 51%]
tests/test_security.py::TestAssetValidation::test_create_requires_serial_number PASSED [ 55%]
tests/test_security.py::TestAssetValidation::test_serial_number_must_be_unique PASSED [ 58%]
tests/test_security.py::TestAssetValidation::test_create_asset_default_status_available PASSED [ 62%]
tests/test_security.py::TestAuditLog::test_no_public_mutating_endpoint PASSED [ 65%]
tests/test_security.py::TestAssetCrud::test_create_and_get_asset PASSED  [ 68%]
tests/test_security.py::TestAssetCrud::test_update_asset PASSED          [ 72%]
tests/test_security.py::TestAssetCrud::test_delete_asset PASSED          [ 75%]
tests/test_security.py::TestRequestCrud::test_create_and_get_request PASSED [ 79%]
tests/test_security.py::TestRequestCrud::test_update_request_status PASSED [ 82%]
tests/test_security.py::TestRequestCrud::test_delete_request_admin_only PASSED [ 86%]
tests/test_security.py::TestMasterDataCrud::test_department_crud PASSED  [ 89%]
tests/test_security.py::TestMasterDataCrud::test_location_crud PASSED    [ 93%]
tests/test_security.py::TestMasterDataCrud::test_category_crud PASSED    [ 96%]
tests/test_security.py::TestMasterDataCrud::test_brand_crud PASSED       [100%]

============================= 29 passed in 21.98s ==============================
```

> âœ… **29 integration tests passed** â€” mencakup: Auth (5), CSRF (2), RBAC (7), Credential Security (1), Asset Validation (3), Audit Log (1), CRUD Assets (3), CRUD Requests (3), CRUD Master Data (4)

### Lampiran E: Bukti Docker Deployment (All Healthy)

```
CONTAINER         STATUS                     PORTS
iams_frontend     Up 57 minutes (healthy)    0.0.0.0:3000->80/tcp
iams_backend      Up 2 hours (healthy)       0.0.0.0:5000->5000/tcp
iams_nginx        Up 2 hours                 0.0.0.0:80->80/tcp, 443->443/tcp
iams_redis        Up 2 hours (healthy)       6379/tcp
iams_mysql        Up 2 hours (healthy)       3306/tcp
```

> âœ… **5 containers running** â€” semua service dengan health check menunjukkan status `(healthy)`

### Lampiran F: Git Commit History (Development Evidence)

```
f3be041 fix: remove duplicate licenses menu entry
46db826 chore: update landing/login stats â€” 22 features, 86 endpoints, 42 tests
1056b25 feat: all 5 Snipe-IT features complete
a9b2f80 feat: barcode visible in Edit Asset dialog
b892a0d feat: 5 Snipe-IT features â€” file upload, status labels, licenses, checkout
693a2e2 feat: language toggle â€” direct click IDâ†”EN
9ce630b feat: login page premium â€” AnimatedGradient + real stats
9fdcf6f feat: all scores 10/10 â€” 42 tests, CI/CD pipeline
28c181a feat: all pages 10/10 â€” i18n titles, toasts
9d02f0b feat: i18n polish â€” incidents page
0692598 feat: i18n foundation for all remaining pages
77c524b feat: assets page 10/10
162b0f7 fix: dashboard action buttons
04a0949 feat: dashboard 10/10
504ae47 feat: landing page ALL 10/10
98966e8 feat: landing page 10/10 â€” trust badges, security section
79e1b33 refactor: ponytail audit â€” remove 17 dead items
5e84d71 refactor: remove role CRUD UI
944346c fix: credential edit
```

> âœ… Commit messages mengikuti **Conventional Commits** format (`feat:`, `fix:`, `refactor:`, `chore:`)

### Lampiran G: Cross-Reference Dokumen

| Dokumen | Lokasi | Isi |
|---------|--------|-----|
| User Manual (ini) | `docs/USER_MANUAL.md` | Panduan pengguna + bukti implementasi |
| Development Guide | `docs/DEVELOPMENT_GUIDE.md` | Panduan developer + cara extend |
| Database Documentation | `docs/DATABASE.md` | Schema overview & history |
| Database Mapping | `docs/DATABASE_MAPPING.md` | SQL â†” MariaDB field mapping |
| Production Hardening | `docs/PRODUCTION_HARDENING.md` | Deploy checklist security |
| README | `README.md` | Quick start & overview |

---

## 27. Bukti Implementasi (Code Evidence)

> Section ini berisi **cuplikan kode sumber aktual** sebagai bukti dari setiap klaim teknis di dokumen ini. Setiap snippet mencantumkan path file lengkap dan nomor baris.

---

### 27.1 Password Hashing â€” bcrypt 12 Rounds

**Klaim:** Password user di-hash menggunakan bcrypt dengan 12 rounds.

ðŸ“ **File:** `backend/app/utils/security.py` â€” **Line 18-20**

```python
def hash_password(password: str) -> str:
    """Hash a plaintext password using bcrypt."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(rounds=12)).decode('utf-8')
```

ðŸ“ **File:** `backend/app/utils/security.py` â€” **Line 23-27**

```python
def verify_password(password: str, password_hash: str) -> bool:
    """Verify a plaintext password against a bcrypt hash."""
    try:
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
    except Exception:
        return False
```

âœ… **Bukti:** `bcrypt.gensalt(rounds=12)` â€” 12 rounds dikonfigurasi secara eksplisit.

---

### 27.2 Credential Encryption â€” AES-256-GCM

**Klaim:** Credential perangkat dienkripsi dengan AES-256-GCM, 12-byte nonce random.

ðŸ“ **File:** `backend/app/utils/security.py` â€” **Line 30-35**

```python
def encrypt_secret(plaintext: str, key: bytes) -> tuple[str, str]:
    """Encrypt plaintext with AES-256-GCM; return (ciphertext_b64, nonce_b64)."""
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)  # 96-bit IV/nonce for GCM
    ciphertext = aesgcm.encrypt(nonce, plaintext.encode('utf-8'), None)
    return base64.b64encode(ciphertext).decode('utf-8'), base64.b64encode(nonce).decode('utf-8')
```

ðŸ“ **File:** `backend/app/utils/security.py` â€” **Line 38-46**

```python
def decrypt_secret(ciphertext_b64: str, nonce_b64: str, key: bytes) -> str:
    """Decrypt AES-256-GCM ciphertext; raise ValueError on failure."""
    aesgcm = AESGCM(key)
    try:
        plaintext = aesgcm.decrypt(
            base64.b64decode(nonce_b64),
            base64.b64decode(ciphertext_b64),
            None,
        )
    except InvalidTag as exc:
        raise ValueError('Credential decryption failed') from exc
    return plaintext.decode('utf-8')
```

âœ… **Bukti:** Library `cryptography.hazmat.primitives.ciphers.aead.AESGCM`, nonce 12 bytes (`os.urandom(12)`), output base64 encoded.

---

### 27.3 JWT di HttpOnly Cookie

**Klaim:** Token JWT disimpan di HttpOnly cookie, tidak bisa diakses JavaScript.

ðŸ“ **File:** `backend/app/routes/auth.py` â€” **Line 17-26**

```python
def _set_cookie(response, name: str, value: str, max_age: int, httponly: bool):
    response.set_cookie(
        name,
        value,
        max_age=max_age,
        httponly=httponly,
        secure=current_app.config['COOKIE_SECURE'],
        samesite=current_app.config['COOKIE_SAMESITE'],
        path='/',
    )
    return response
```

ðŸ“ **File:** `backend/app/routes/auth.py` â€” **Line 75-77**

```python
response = jsonify({'message': 'Login successful', 'user': user.to_dict()})
_set_cookie(response, current_app.config['JWT_COOKIE_NAME'], token,
            max_age=current_app.config['JWT_ACCESS_TOKEN_EXPIRES_SECONDS'], httponly=True)
```

âœ… **Bukti:** `httponly=True` â€” browser tidak bisa akses via `document.cookie` atau JavaScript.

---

### 27.4 Rate Limiting â€” 5 Login Per Menit

**Klaim:** Endpoint login dibatasi 5 percobaan per menit.

ðŸ“ **File:** `backend/app/routes/auth.py` â€” **Line 42-43**

```python
@bp.route('/login', methods=['POST'])
@limiter.limit('5 per minute')
def login():
    """Authenticate user and set HttpOnly JWT cookie."""
```

âœ… **Bukti:** Decorator `@limiter.limit('5 per minute')` dari Flask-Limiter.

---

### 27.5 CSRF Double-Submit Cookie

**Klaim:** Setiap state-changing request divalidasi CSRF token (header harus = cookie).

ðŸ“ **File:** `backend/app/utils/decorators.py` â€” **Line 55-67**

```python
def require_csrf(f):
    """Validate CSRF token header against readable cookie for state-changing methods."""
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        if request.method in ('GET', 'HEAD', 'OPTIONS'):
            return f(*args, **kwargs)
        csrf_cookie = request.cookies.get(current_app.config['CSRF_COOKIE_NAME'])
        csrf_header = request.headers.get('X-CSRF-Token') or request.headers.get('X-Csrf-Token')
        if not csrf_cookie or not csrf_header or csrf_cookie != csrf_header:
            log_audit('ACCESS_DENIED', 'csrf', status='failure',
                      metadata={'reason': 'csrf_mismatch', 'ip': get_client_ip()})
            return _set_auth_error(403, 'Invalid CSRF token')
        return f(*args, **kwargs)
    return decorated
```

âœ… **Bukti:** `csrf_cookie != csrf_header` â†’ jika tidak cocok, return 403 + audit log.

---

### 27.6 RBAC â€” Role-Based Access Control

**Klaim:** Akses endpoint diatur berdasarkan role (Administrator/Operator).

ðŸ“ **File:** `backend/app/utils/decorators.py` â€” **Line 70-83**

```python
def require_role(*allowed_roles: str):
    """Restrict endpoint to users with one of the allowed roles."""
    def decorator(f):
        @functools.wraps(f)
        @require_auth
        def decorated(*args, **kwargs):
            role = getattr(g, 'current_role', None)
            if role not in allowed_roles:
                log_audit('ACCESS_DENIED', 'rbac', status='failure',
                          metadata={'required_roles': list(allowed_roles), 'actual_role': role})
                return _set_auth_error(403, 'Forbidden')
            return f(*args, **kwargs)
        return decorated
    return decorator
```

ðŸ“ **File:** `backend/app/utils/decorators.py` â€” **Line 86-90**

```python
def admin_only(f):
    return require_role('Administrator')(f)

def admin_or_operator(f):
    return require_role('Administrator', 'Operator')(f)
```

âœ… **Bukti:** `@admin_only` = hanya Administrator, `@admin_or_operator` = kedua role.

---

### 27.7 Self-Approval Blocking

**Klaim:** Administrator tidak bisa approve change request miliknya sendiri.

ðŸ“ **File:** `backend/app/routes/changes.py` â€” **Line 179-188**

```python
@bp.route('/<int:chg_id>/approve', methods=['POST'])
@admin_only
@require_csrf
def approve_change(chg_id):
    c = db.session.get(ChangeRequest, chg_id)
    if not c:
        return jsonify({'error': 'Change not found'}), 404
    if c.status not in ('Submitted', 'Under Review'):
        return jsonify({'error': f'Cannot approve a change that is {c.status}'}), 409
    if c.requester_id == g.current_user_id:
        return jsonify({'error': 'Cannot approve your own change request'}), 409
```

âœ… **Bukti:** `if c.requester_id == g.current_user_id` â†’ return 409 Conflict.

---

### 27.8 Delete Safety â€” FK Reference Check

**Klaim:** Data master tidak bisa dihapus jika masih direferensi tabel lain.

ðŸ“ **File:** `backend/app/routes/master.py` â€” **Line 98-107**

```python
@bp.route('/departments/<int:dep_id>', methods=['DELETE'])
@admin_only
@require_csrf
def delete_department(dep_id):
    dep = db.session.get(Department, dep_id)
    if not dep:
        return jsonify({'error': 'Department not found'}), 404
    if User.query.filter_by(department_id=dep_id).first():
        return jsonify({'error': 'Cannot delete resource because it is still in use.'}), 409
    db.session.delete(dep)
    db.session.commit()
```

âœ… **Bukti:** `User.query.filter_by(department_id=dep_id).first()` â€” cek apakah masih ada user di dept itu sebelum delete.

---

### 27.9 Audit Log â€” Append-Only (No DELETE/UPDATE Endpoint)

**Klaim:** Audit log bersifat append-only â€” tidak ada endpoint untuk edit atau hapus.

ðŸ“ **File:** `backend/app/routes/audit_logs.py` â€” **SELURUH FILE (26 baris)**

```python
"""Audit logs blueprint (Administrator read-only)."""
from flask import Blueprint, jsonify, request
from app.models import AuditLog
from sqlalchemy import or_
from app.utils.decorators import admin_only
from app.utils.pagination import paginate

bp = Blueprint('audit_logs', __name__, url_prefix='/api/audit-logs')

@bp.route('', methods=['GET'])
@admin_only
def list_audit_logs():
    query = AuditLog.query
    if request.args.get('action'):
        query = query.filter_by(action=request.args.get('action'))
    if request.args.get('status'):
        query = query.filter_by(status=request.args.get('status'))
    search = (request.args.get('search') or '').strip()
    if search:
        pattern = f'%{search}%'
        query = query.filter(or_(AuditLog.action.like(pattern),
            AuditLog.resource_type.like(pattern), AuditLog.resource_id.like(pattern)))
    rows = query.order_by(AuditLog.created_at.desc())
    return jsonify(paginate(rows, max_per_page=100))
```

âœ… **Bukti:** File hanya punya `GET` route. **Tidak ada** `POST`, `PUT`, atau `DELETE` endpoint. Data hanya bisa dibuat oleh `log_audit()` helper dari server-side.

---

### 27.10 Audit Helper â€” Auto-Redact Sensitive Data

**Klaim:** Metadata di audit log otomatis di-redact (password/token tidak tersimpan plain).

ðŸ“ **File:** `backend/app/utils/audit.py` â€” **Line 18-36**

```python
def log_audit(action: str, resource_type: str, resource_id: str | None = None,
              status: str = 'success', metadata: dict | None = None):
    """Append-only audit log creation. Never stores plaintext secrets."""
    try:
        actor_id = getattr(g, 'current_user_id', None)
        redacted_metadata = None
        if metadata is not None:
            redacted_metadata = str(redact(metadata))[:2000]
        entry = AuditLog(
            actor_user_id=actor_id,
            action=action,
            resource_type=resource_type,
            resource_id=str(resource_id)[:255] if resource_id else None,
            status=status,
            ip_address=get_client_ip(),
            user_agent=(request.headers.get('User-Agent') or '')[:500],
            metadata_redacted=redacted_metadata,
        )
        db.session.add(entry)
        db.session.commit()
    except Exception:
        db.session.rollback()
```

ðŸ“ **File:** `backend/app/utils/security.py` â€” **Line 50-57** (redact function)

```python
SENSITIVE_KEYS = (
    'password', 'password_hash', 'secret', 'token', 'access_token', 'refresh_token',
    'aes_key', 'jwt_secret', 'encrypted_secret', 'nonce', 'authorization',
)

def redact(value: dict | list | str | None) -> dict | list | str | None:
    """Recursively redact sensitive-looking keys from structures."""
    if isinstance(value, dict):
        return {
            k: '***REDACTED***' if any(s in str(k).lower() for s in SENSITIVE_KEYS) else redact(v)
            for k, v in value.items()
        }
```

âœ… **Bukti:** `redact(metadata)` mengganti value dari key sensitif (password, token, dll) dengan `***REDACTED***`.

---

### 27.11 Security Headers

**Klaim:** Response headers mencakup HSTS, X-Frame-Options, CSP, X-Content-Type-Options.

ðŸ“ **File:** `backend/app/__init__.py` â€” **Line 31-36**

```python
@app.after_request
def add_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['Strict-Transport-Security'] = 'max-age=63072000; includeSubDomains'
    response.headers['Content-Security-Policy'] = "default-src 'self'"
    return response
```

âœ… **Bukti:** 4 security headers ditambahkan di `@app.after_request` â€” berlaku untuk SEMUA response.

---

### 27.12 CORS â€” Explicit Origin Only

**Klaim:** CORS hanya mengizinkan origin frontend yang terdaftar.

ðŸ“ **File:** `backend/app/__init__.py` â€” **Line 22-28**

```python
CORS(
    app,
    resources={r'/api/*': {'origins': [app.config['FRONTEND_ORIGIN']]}},
    supports_credentials=True,
    allow_headers=['Content-Type', 'X-CSRF-Token'],
    methods=['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS'],
)
```

âœ… **Bukti:** `origins: [app.config['FRONTEND_ORIGIN']]` â€” hanya satu origin yang diizinkan, bukan `*` (wildcard).

---

### 27.13 Fail-Fast Secret Validation

**Klaim:** Aplikasi menolak start jika JWT_SECRET terlalu pendek atau AES key bukan 32 bytes.

ðŸ“ **File:** `backend/config.py` â€” **Line 20-26**

```python
def _validate_aes_key(key_b64: str) -> bytes:
    try:
        key = base64.b64decode(key_b64, validate=True)
    except Exception as exc:
        raise RuntimeError('AES_KEY_BASE64 is not valid base64') from exc
    if len(key) != 32:
        raise RuntimeError(f'AES key must be exactly 32 bytes, got {len(key)} bytes')
    return key

def _validate_jwt_secret(secret: str) -> str:
    if len(secret.encode()) < 32:
        raise RuntimeError('JWT_SECRET must be at least 32 bytes')
    return secret
```

ðŸ“ **File:** `backend/config.py` â€” **Line 42-43**

```python
# Secrets (validated at import time -> fail fast)
JWT_SECRET = _validate_jwt_secret(_load_env('JWT_SECRET'))
AES_KEY = _validate_aes_key(_load_env('AES_KEY_BASE64'))
```

âœ… **Bukti:** Validasi dilakukan saat import config (sebelum app start). Jika tidak valid â†’ `RuntimeError` â†’ app crash.

---

### 27.14 Error Sanitization â€” Never Leak Internals

**Klaim:** Error response tidak pernah menampilkan path internal atau stack trace.

ðŸ“ **File:** `backend/app/__init__.py` â€” **Line 46-50**

```python
@app.errorhandler(Exception)
def handle_exception(exc):
    app.logger.exception('Unhandled exception')
    return jsonify({'error': 'Internal server error'}), 500
```

ðŸ“ **File:** `backend/app/utils/security.py` â€” **Line 60-66**

```python
def sanitize_error_message(message: str) -> str:
    """Remove paths, query hints, and stack traces from error messages."""
    if not isinstance(message, str):
        return 'An error occurred'
    # Remove filesystem paths
    message = re.sub(r'[A-Za-z]:\\[^\s]+|/[^\s]*', '[path]', message)
    # Remove SQLAlchemy internal markers
    message = re.sub(r'\(.*\)', '', message)
    return message.strip() or 'An error occurred'
```

âœ… **Bukti:** Generic "Internal server error" response + `sanitize_error_message()` yang strip paths/SQL markers.

---

### 27.15 JWT Token Verification â€” Cookie-Based Auth

**Klaim:** Setiap request ke protected endpoint, JWT diverifikasi dari cookie.

ðŸ“ **File:** `backend/app/utils/decorators.py` â€” **Line 20-44**

```python
def require_auth(f):
    """Verify JWT from HttpOnly cookie and load current user."""
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        token = request.cookies.get(current_app.config['JWT_COOKIE_NAME'])
        if not token:
            log_audit('ACCESS_DENIED', 'auth', status='failure',
                      metadata={'reason': 'missing_token', 'ip': get_client_ip()})
            return _set_auth_error(401, 'Unauthorized')
        try:
            payload = jwt.decode(
                token,
                current_app.config['JWT_SECRET'],
                algorithms=[current_app.config['JWT_ALGORITHM']],
            )
            user_id = payload.get('sub')
            if not user_id:
                raise jwt.InvalidTokenError('missing sub')
            user = db.session.get(User, int(str(user_id)))
            if not user or not user.is_active:
                raise jwt.InvalidTokenError('user inactive')
            g.current_user = user
            g.current_user_id = user.id
            g.current_role = user.role.name if user.role else None
        except jwt.ExpiredSignatureError:
            return _set_auth_error(401, 'Unauthorized')
```

âœ… **Bukti:** `request.cookies.get(...)` â†’ JWT dari cookie, `jwt.decode(...)` â†’ verifikasi signature + expiry, load user dari DB.

---

### 27.16 Credential Reveal â€” Always Audited

**Klaim:** Setiap kali credential di-reveal, tercatat di audit log.

ðŸ“ **File:** `backend/app/routes/assets.py` â€” **Line 192-203**

```python
@bp.route('/<int:asset_id>/credentials/<int:cred_id>/reveal', methods=['GET'])
@admin_only
def reveal_credential(asset_id, cred_id):
    """Reveal decrypted password â€” always audited."""
    cred = AssetCredential.query.filter_by(id=cred_id, asset_id=asset_id).first()
    if not cred:
        return jsonify({'error': 'Credential not found'}), 404
    try:
        plaintext = decrypt_secret(cred.encrypted_secret, cred.nonce, current_app.config['AES_KEY'])
    except ValueError:
        return jsonify({'error': 'Credential decryption failed'}), 500
    log_audit('REVEAL', 'asset_credential', resource_id=asset_id, status='success',
              metadata={'credential_id': cred_id, 'type': cred.credential_type, 'by_user': g.current_user_id})
    return jsonify({'data': {'password': plaintext}})
```

âœ… **Bukti:** `@admin_only` + `log_audit('REVEAL', ...)` â€” hanya admin bisa, dan SELALU dicatat siapa yang reveal.

---

### 27.17 Auto-Generated Codes (INC/PRB/REQ/CHG)

**Klaim:** Setiap incident/problem/request/change mendapat kode unik otomatis.

ðŸ“ **File:** `backend/app/routes/incidents.py` â€” **Line 30-37**

```python
def _next_code() -> str:
    year = datetime.now(timezone.utc).year
    last = Incident.query.filter(Incident.code.like(f'INC-{year}-%')).order_by(Incident.code.desc()).first()
    n = 1
    if last:
        try:
            n = int(last.code.split('-')[-1]) + 1
        except Exception:
            pass
    return f'INC-{year}-{n:04d}'
```

ðŸ“ **File:** `backend/app/routes/changes.py` â€” **Line 23-26**

```python
def _next_number() -> str:
    year = datetime.now(timezone.utc).year
    last = ChangeRequest.query.order_by(ChangeRequest.id.desc()).first()
    n = (last.id + 1) if last else 1
    return f'CHG-{year}-{n:04d}'
```

âœ… **Bukti:** Format `{PREFIX}-{YEAR}-{SEQ:04d}` â€” sequence auto-increment per tahun.

---

### 27.18 Frontend CSRF Handling â€” Auto-Retry

**Klaim:** Frontend otomatis refresh CSRF token jika expired dan retry request.

ðŸ“ **File:** `frontend/src/services/apiClient.js` â€” **Line 72-82**

```javascript
// If CSRF was rejected, refresh token once and retry.
if (res.status === 403 && isStateChanging(method)) {
  const data = await parseJson(res)
  const msg = (data?.error || '').toLowerCase()
  if (msg.includes('csrf')) {
    csrfToken = null
    await fetchCsrfToken()
    Object.assign(headers, csrfHeaders())
    const retryRes = await fetch(`${BASE}${path}`, fetchOptions)
    return parseResponse(retryRes, options)
  }
}
```

âœ… **Bukti:** Deteksi 403 + "csrf" di error message â†’ refresh token â†’ retry 1x otomatis.

---

### 27.19 Docker Health Checks

**Klaim:** Semua container memiliki health check.

ðŸ“ **File:** `docker-compose.yml` â€” Backend health check:

```yaml
backend:
  healthcheck:
    test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:5000/api/auth/csrf-token')"]
    interval: 30s
    timeout: 5s
    retries: 3
```

ðŸ“ **File:** `docker-compose.yml` â€” MySQL health check:

```yaml
mysql:
  healthcheck:
    test: ["CMD", "healthcheck.sh", "--connect", "--innodb_initialized"]
    interval: 10s
    timeout: 5s
    retries: 5
```

ðŸ“ **File:** `docker-compose.yml` â€” Redis health check:

```yaml
redis:
  healthcheck:
    test: ["CMD", "redis-cli", "ping"]
    interval: 10s
    timeout: 5s
    retries: 5
```

âœ… **Bukti:** 3 service punya health check aktif. Frontend depends_on backend (healthy), backend depends_on mysql + redis (healthy).

---

### 27.20 Vue Router Auth Guard â€” RBAC Frontend

**Klaim:** Frontend memblokir navigasi ke halaman tertentu berdasarkan role.

ðŸ“ **File:** `frontend/src/router/index.js` â€” **Line 55-68**

```javascript
router.beforeEach(async (to) => {
  const auth = useAuthStore()
  if (!auth.initialized) {
    await auth.initSession()
  }
  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    return { name: 'login', query: { next: to.fullPath } }
  }
  if (to.meta.roles && Array.isArray(to.meta.roles)) {
    if (!auth.user || !to.meta.roles.includes(auth.user.role_name)) {
      return { name: 'dashboard' }
    }
  }
})
```

ðŸ“ **File:** `frontend/src/router/index.js` â€” Route meta contoh:

```javascript
{
  path: 'audit-logs',
  name: 'audit-logs',
  component: () => import('@/pages/AuditLogsPage.vue'),
  meta: { roles: ['Administrator'] },
},
```

âœ… **Bukti:** `meta: { roles: ['Administrator'] }` + `beforeEach` guard â†’ Operator redirect ke dashboard jika coba akses audit-logs.

---

*Section ini membuktikan bahwa setiap klaim teknis dalam dokumen didukung oleh kode sumber aktual yang dapat diverifikasi.*

---

*IAMS â€” Infrastructure Asset Management System v3.0*  
*Hybrid User Manual: Panduan Pengguna + Dokumentasi Teknis*  
*Â© 2026*

