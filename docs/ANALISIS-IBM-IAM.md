# Analisis Keterkaitan: IAMS Project vs IBM Infrastructure Asset Management Framework

**Analis:** Ahli Keamanan Komputer & Jaringan (Cybersecurity) — 20+ tahun pengalaman Industri  
**Sumber Referensi:** https://www.ibm.com/think/topics/infrastructure-asset-management  
**Proyek:** IAMS (Infrastructure Asset Management System)  
**Tanggal:** 23 Juni 2026

---

## Ringkasan Eksekutif

Proyek **IAMS** yang sedang dikembangkan memiliki keterkaitan substansial dengan kerangka kerja *Infrastructure Asset Management* (IAM) dari IBM. Dari 6 elemen kunci IAM IBM, IAMS telah meng-cover **5 elemen** (kecuali *Level of Service* / LOS). Dari 7 *lifecycle stage*, IAMS meng-cover **4 stage** (kecuali *Planning*, *Design & Procurement*, *Long-term Financial Planning*).

Dari perspektif *Cybersecurity*, IAMS memiliki fondasi keamanan yang kokoh (*defense-in-depth*) dengan beberapa fitur (seperti *append-only audit log* + *auto-redaction*) yang melampaui sistem komersial semacam IBM Maximo. Namun terdapat celah signifikan pada tidak adanya *asset criticality scoring*, *vulnerability management*, dan *password strength validation*.

---

## 1. Pemetaan dengan 6 Key Elements IAM (IBM)

| Elemen IBM IAM | Implementasi di IAMS Project | Analisis Cybersecurity |
|---|---|---|
| **Asset Inventory** | ✅ **Lengkap.** CRUD asset (asset_tag, serial_number, PO, lokasi, user FK, status, purchase_date, warranty_months, OS license). Dilengkapi: 1:1 network_detail, 1:N encrypted credentials (AES-256-GCM), file attachments (LargeBinary, 10MB max), check-in/check-out history. | Inventaris IT sudah baik namun belum mencakup *OT/IoT assets* atau *infrastructure as code* (konfigurasi server, container, VM). IBM menekankan pentingnya mencakup *seluruh jenis infrastruktur fisik*. |
| **Condition Assessment** | ✅ **Parsial.** Status asset (Active/Available/Repair/Disposed) + Incident & Problem management sebagai indikator kondisi tidak langsung. | Belum ada *predictive condition scoring* berbasis ML, belum ada *health index* per asset. IBM menyoroti AI/ML untuk *predictive maintenance*. |
| **Level of Service (LOS)** | ❌ **Belum tersentuh.** Tidak ada metrik SLA/SLO, availability target, atau *service level agreements*. | **Rekomendasi prioritas:** Tambahkan SLA tracking per kategori asset. LOS adalah elemen yang menghubungkan *technical condition* dengan *business impact* — sangat relevan untuk *risk management* keamanan. |
| **Life Cycle Costing** | ⚠️ **Parsial.** Ada purchase_date, warranty_months, dan laporan warranty-expiring. | Belum ada TCO (*Total Cost of Ownership*), depresiasi aset, akumulasi biaya maintenance, atau *replacement cost projection*. |
| **Risk Management** | ✅ **Parsial.** Change Management memiliki risk/impact assessment + rollback plan. Problem Management menyediakan root cause analysis. Incident Management sebagai indikator kegagalan. | Belum ada *risk register*, *FMEA scoring* (*Failure Mode & Effects Analysis*), atau *criticality matrix* per asset. Ini adalah celah keamanan *kritis* karena tanpa *risk scoring*, keputusan mitigasi tidak dapat diprioritaskan secara objektif. |
| **Long-term Financial Planning** | ❌ **Belum tersentuh.** Tidak ada budget forecasting, CAPEX/OPEX planning, atau *capital replacement plan*. | |

---

## 2. Pemetaan dengan 7 Stage Lifecycle IAM (IBM)

| Stage IBM | Coverage IAMS | Detail |
|---|---|---|
| **1. Planning** | ❌ Tidak di-cover | Di luar lingkup teknis sistem saat ini. IBM: *identifikasi kebutuhan aset, cost-benefit analysis, feasibility study*. |
| **2. Design & Procurement** | ❌ Tidak di-cover | IBM: *detailed design, material procurement, cost estimation*. Tidak ada *vendor management* atau *procurement workflow*. |
| **3. Construction/Acquisition** | ✅ Parsial | Check-in asset baru ke sistem. Tidak ada *acceptance testing* atau *quality assurance* workflow. |
| **4. Operation** | ✅ Dashboard & Monitoring | KPI cards (total assets, open incidents, critical incidents, active problems), distribusi kategori, breakdown status, real-time refresh. Operasional sudah terpantau dengan baik. |
| **5. Maintenance & Upgrades** | ✅ **Area paling solid** | Incident Management (ticketing ITSM), Problem Management (RCA), Change Management (approve/reject, risk/impact, rollback). Ini area paling matang dan paling relevan dengan *Cybersecurity* — terutama *Change Management* yang mencegah *unauthorized changes*. |
| **6. Renewal/Replacement** | ✅ Parsial | Check-in/check-out, warranty tracking via laporan warranty-expiring. Belum ada EOL (*End-of-Life*) dan EOS (*End-of-Support*) tracking untuk asset IT — sangat penting dari sisi keamanan (software/support yang habis masa berlakunya adalah vektor serangan). |
| **7. Review & Audit** | ✅ **Sangat kuat** | Append-only audit logs, 24 event types, auto-redaction metadata, immutable. Sesuai standar ISO 55000 clause 7.5 dan regulatory compliance. |

---

## 3. Keterkaitan Teknologi Masa Depan (IBM: AI, ML, IoT, GIS)

IBM menyoroti peran **Industry 4.0** dalam masa depan IAM:

| Teknologi | Status di IAMS | Analisis & Rekomendasi Keamanan |
|---|---|---|
| **AI/ML** (*Predictive Maintenance*) | ❌ Belum ada | **Rekomendasi:** Model *failure prediction* berdasarkan data historis incident + problem. **Catatan keamanan:** Model ML rentan *adversarial attacks* → perlu *input validation, model monitoring, adversarial retraining*. |
| **Internet of Things (IoT)** | ❌ Belum ada | IAMS fokus pada IT asset management. IBM juga mencakup *physical infrastructure* (roads, bridges, utilities). **Rekomendasi:** Jika diperluas ke OT (Operational Technology) — perlu mengadopsi standar **ISA/IEC 62443** untuk *network segmentation*, *secure remote access*, dan *patching* untuk perangkat OT/IoT. |
| **GIS** (*Geospatial Data*) | ❌ Belum ada | Untuk IT infra, *network topology mapping* (L2/L3 topology graph) bisa menjadi alternatif yang lebih relevan daripada GIS geografis. |
| **ISO 55000 Series** | ⚠️ Parsial | IAMS sudah memiliki: *audit trail* (klausa 7.5), *risk management* parsial (klausa 6.1), *asset lifecycle* parsial (klausa 6.2). **Rekomendasi:** Mapping fitur eksplisit ke klausa ISO 55001 untuk menambah kredibilitas dan *compliance readiness*. |

---

## 4. Analisis Cybersecurity Mendalam

### 4.1. Kekuatan Keamanan IAMS (selaras dengan best practice IBM)

| Lapisan Keamanan | Detail | Standar Terkait |
|---|---|---|
| **Authentication** | JWT dalam HttpOnly cookie (8 jam expiry), bcrypt (12 rounds) untuk password. Tidak ada token di localStorage. | OWASP ASVS, NIST SP 800-63B |
| **CSRF Protection** | Double-submit cookie pattern. Token via GET /api/auth/csrf-token + header X-CSRF-Token. | OWASP CSRF Cheatsheet |
| **Encryption at Rest** | AES-256-GCM (*authenticated encryption*) untuk asset credentials. Random 12-byte nonce. | NIST SP 800-38D, FIPS 140-2 |
| **Authorization (RBAC)** | Decorator-based: @admin_only, @admin_or_operator. Proteksi di API + Route level. | OWASP RBAC, NIST AC |
| **Rate Limiting** | Login endpoint: 5 requests/minute. Redis-backed di produksi. | OWASP Rate Limiting |
| **Security Headers** | HSTS (2 tahun), CSP (default-src 'self'), X-Frame-Options DENY, X-Content-Type-Options nosniff, Permissions-Policy ketat. | OWASP Security Headers |
| **Audit Logging** | Append-only, immutable, auto-redaction (password, secret, token, dll.), 24 event types. **Ini unggul dibandingkan IBM Maximo standar.** | ISO 27001 A.12.4, PCI DSS 10, SOX |
| **Fail-fast Config** | Server crash saat startup jika env var tidak valid. Mencegah *misconfiguration* yang tidak terdeteksi. | NIST IR 8320 |
| **HTTPS/TLS** | TLS 1.2/1.3, cipher suite kuat, HTTP-to-HTTPS redirect. Nginx sebagai *reverse proxy*. | OWASP Transport Protection |
| **Error Handling** | Sanitized error messages. Tidak ada stack trace, DB details, atau internal paths yang bocor. | OWASP Info Leakage |

### 4.2. Temuan & Rekomendasi Keamanan (Prioritas)

| # | Area | Temuan | Dampak | Rekomendasi | Prioritas |
|---|---|---|---|---|---|
| 1 | **Asset Criticality & Risk Scoring** | Tidak ada kolom criticality/risk_score per asset. Incident tidak memiliki *impact weighting* berdasarkan aset yang terpengaruh. | Tanpa prioritas risiko, organisasi tidak bisa membedakan mana aset yang *harus* di-protect duluan. Ini adalah *gap fundamental* di sistem IAM. | Tambahkan field `criticality` (Critical/High/Medium/Low) dan `risk_score` pada model Asset. Hubungkan dengan *incident impact analysis* dan dashboard. | 🔴 **Tinggi** |
| 2 | **Vulnerability Management** | Tidak ada integrasi dengan *vulnerability scanner*, tidak ada *patch management tracking*, tidak ada CVE database lookup. | Aset dengan kerentanan kritis yang tidak terpantau menjadi *low-hanging fruit* bagi attacker. | Tambahkan modul *Vulnerability Tracking*: integration API dengan scanner, tracking patch status, CVE mapping ke asset. | 🔴 **Tinggi** |
| 3 | **Password Strength & Rotation** | Tidak ada validasi password strength. Tidak ada *session invalidation* saat password berubah. Tidak ada password history. | Password lemah adalah *attack vector* #1. Session lama yang tetap aktif setelah *password reset* memungkinkan *session hijacking*. | Implementasi: zxcvbn atau custom strength meter, invalidate all sessions on password change, enforce password history (NIST SP 800-63B). | 🟡 **Sedang** |
| 4 | **SOAR / Incident Response** | Incident management manual. Tidak ada *automated playbooks*, *auto-isolation*, atau *notification routing* berbasis severity. | Response time lambat untuk insiden keamanan kritis. | Tambahkan *automation rules*: auto-isolate asset jika critical incident, notifikasi via email/webhook, escalation policy. | 🟡 **Sedang** |
| 5 | **API Security Hardening** | Tidak ada *request schema validation* library (Pydantic/Marshmallow). Rate limiting per-IP bukan per-user. | Input tidak tervalidasi → rentan injection. Rate limit per-IP bisa di-bypass via distributed attack. | Integrasi Pydantic/Marshmallow untuk validasi, rate limiting per-user + per-IP (layered). | 🟡 **Sedang** |
| 6 | **Supply Chain Security** | Tidak ada *vendor management* atau *supplier risk assessment*. | Aset dari vendor dengan *supply chain compromise* tidak terdeteksi. IBM menekankan *end-to-end lifecycle* dari procurement hingga disposal. | Tambahkan *vendor database*, *supplier risk scoring*, *procurement approval workflow*. | 🟢 **Rendah** |
| 7 | **Compliance Mapping** | Audit trail eksisting sangat baik tetapi tidak di-tag ke control framework tertentu. | *Audit readiness* rendah — auditor harus mapping manual. | Tambahkan *compliance tags* ke audit log events. Mapping ke ISO 27001 Annex A, NIST CSF, PCI DSS. | 🟡 **Sedang** |
| 8 | **EOL/EOS Tracking** | Tidak ada *end-of-life* atau *end-of-support* tracking. Software/hardware yang sudah *end-of-life* tidak menerima patch keamanan. | Aset EOL/EOS adalah risiko keamanan tinggi. Kendala IT yang terkenal: Heartbleed, WannaCry mengeksploitasi sistem *legacy/unpatched*. | Tambahkan field `eol_date`, `eos_date` pada model Asset. Notifikasi otomatis saat mendekati EOL/EOS. | 🟡 **Sedang** |
| 9 | **File Upload Security** | File disimpan sebagai LargeBinary di DB (10MB limit). | Tidak disebutkan *virus scanning*, *MIME type validation*, atau *filename sanitization* pada upload. | Tambahkan: *virus scanning* (ClamAV), validasi MIME type (whitelist), *path traversal prevention*, *filename randomization* (UUID sudah ada — baik). | 🟡 **Sedang** |
| 10 | **Session Management** | JWT expiry 8 jam. Tidak ada refresh token. Tidak ada *device fingerprinting*. | Token dicuri → attacker punya akses 8 jam penuh. | Implementasi: *refresh token* (short-lived access token), *device fingerprint* (User-Agent + IP binding), *token rotation*. | 🟡 **Sedang** |

---

## 5. Matriks Keterkaitan Langsung: IAMS Feature → IBM IAM → ISO 55000

| Fitur IAMS | IBM IAM Element | IBM Lifecycle Stage | ISO 55000 Clause Potensial |
|---|---|---|---|
| Asset CRUD (+ network, credentials, files, checkout) | Asset Inventory | Acquisition, Operation | 6.2.2 (*Asset lifecycle planning*), 7.5 (*Information requirements*) |
| Incident Management (auto-code INC-YYYY-NNNN, severity, status) | Condition Assessment | Maintenance | 6.1 (*Risk management*), 8.2 (*Incident management*) |
| Problem Management / RCA (auto-code PRB-YYYY-NNNN, priority) | Risk Management | Review & Audit | 6.1, 10.2 (*Root cause analysis*) |
| Change Management (approve/reject, risk/impact, rollback) | Risk Management | Maintenance, Upgrades | 6.1, 8.1 (*Change control*) |
| Service Request Management (7 types, auto-code REQ-YYYY-NNNN) | Level of Service (LOS) | Operation | 8.2 (*Service request management*) |
| Audit Logs (append-only, 24 event types, auto-redaction) | — | Review & Audit | 7.5, 9.2 (*Internal audit*), 10.1 (*Nonconformity*) |
| Dashboard (KPI cards, status breakdown, distribution) | Level of Service (LOS) | Operation | 9.1 (*Performance evaluation*) |
| Reports (full report, status summary, warranty-expiring, by-PO) | Life Cycle Costing | Review & Audit | 7.5, 9.2 |
| Software Licenses Management (seat count, expiry) | Asset Inventory | Operation | 6.2.2 (*Asset lifecycle planning*) |
| RBAC (Administrator / Operator) | — | — | ISO 27001 A.9 (*Access control*) |

---

## 6. Kesenjangan Strategis (Gap Analysis)

### 6.1. Gap terhadap IBM IAM Framework

| Gap | Dampak | Rekomendasi Penanganan |
|---|---|---|
| **Level of Service (LOS) tidak ada** | Tidak bisa mengukur *apakah aset memberikan layanan sesuai harapan*. Metrik bisnis tidak terdefinisi. | Implementasi SLA framework per kategori asset. Integrasi dengan dashboard (actual vs target availability). |
| **Long-term financial planning tidak ada** | Tidak ada proyeksi biaya jangka panjang. Organisasi buta terhadap *future budget requirement*. | Tambahkan: depresiasi, TCO, *replacement cost forecasting*, *budget planning module*. |
| **Predictive maintenance (AI/ML) tidak ada** | *Reactive* bukan *predictive*. Biaya maintenance lebih tinggi, downtime tidak terduga. | Integrasi model ML sederhana: regression analysis untuk *failure prediction* berdasarkan data historis incident. |
| **Planning & Procurement stage tidak di-cover** | *Lifecycle* tidak lengkap. Aset dicatat setelah dibeli, bukan sejak perencanaan. | Tambahkan *request for purchase* workflow, *vendor management*, *procurement approval*. |

### 6.2. Gap terhadap Cybersecurity Best Practice

| Gap | Dampak | Severity |
|---|---|---|
| Tidak ada *asset criticality / risk scoring* | Keputusan prioritas tidak objektif | **Critical** |
| Tidak ada *vulnerability management* | Kerentanan tidak terpantau | **Critical** |
| Tidak ada *password strength validation* | Password lemah — *attack vector* #1 | **High** |
| Tidak ada *session invalidation on password change* | Session lama tetap aktif | **Medium** |
| Tidak ada *refresh token* | Token dicuri → akses 8 jam penuh | **Medium** |
| Tidak ada *virus scanning* pada file upload | Potensi malware upload | **Medium** |
| Tidak ada API schema validation library | Rentan injection via parameter | **Medium** |

---

## 7. Matriks Prioritas Rekomendasi

| Prioritas | Rekomendasi | Estimasi Effort | Dampak Bisnis |
|---|---|---|---|
| **P1 — Segera** | Tambahkan *Asset Criticality & Risk Scoring* | 2-3 hari | Memungkinkan prioritasi berbasis risiko — fondasi untuk semua keputusan keamanan |
| **P1 — Segera** | Implementasi *Password Strength & Rotation Policy* | 1-2 hari | Mengurangi risiko *credential compromise* secara langsung |
| **P2 — Jangka Pendek** | Integrasi *Vulnerability Management* (CVE tracking) | 5-7 hari | Menutup celah keamanan kritis pada aset IT |
| **P2 — Jangka Pendek** | Session Management: refresh token + device fingerprint | 3-5 hari | Mengurangi risiko *token theft* |
| **P2 — Jangka Pendek** | API Schema Validation (Pydantic/Marshmallow) | 2-4 hari | Mencegah injection attacks secara sistematis |
| **P2 — Jangka Pendek** | SLA / LOS Framework | 5-7 hari | Menghubungkan teknis dengan bisnis |
| **P3 — Jangka Menengah** | AI/ML Predictive Maintenance | 2-4 minggu | Mengurangi *unplanned downtime* |
| **P3 — Jangka Menengah** | Compliance Mapping (ISO 27001, ISO 55000, NIST) | 1-2 minggu | *Audit readiness*, meningkatkan kepercayaan pelanggan |
| **P3 — Jangka Menengah** | SOAR / Incident Response Automation | 2-3 minggu | Mempercepat *mean time to respond* (MTTR) |
| **P4 — Jangka Panjang** | Supply Chain / Vendor Management | 2-4 minggu | Mengelola *third-party risk* |
| **P4 — Jangka Panjang** | Financial Planning (TCO, CAPEX, Depresiasi) | 3-5 minggu | Perencanaan anggaran aset jangka panjang |

---

## 8. Referensi

1. IBM. *What is Infrastructure Asset Management?* https://www.ibm.com/think/topics/infrastructure-asset-management
2. ISO 55000:2014 — *Asset management — Overview, principles and terminology*
3. ISO 55001:2014 — *Asset management — Management systems — Requirements*
4. ISO 27001:2022 — *Information security, cybersecurity and privacy protection*
5. NIST SP 800-63B — *Digital Identity Guidelines: Authentication and Lifecycle Management*
6. ISA/IEC 62443 — *Security for Industrial Automation and Control Systems*
7. OWASP Application Security Verification Standard (ASVS)
8. IAMS Project Documentation: `docs/` — Infrastructure Asset Management System

---

> **Catatan:** Analisis ini didasarkan pada kode sumber dan dokumentasi proyek IAMS per tanggal 23 Juni 2026, serta publikasi IBM *Think: Infrastructure Asset Management*. Rekomendasi bersifat *advisory* dan harus disesuaikan dengan konteks organisasi, *risk appetite*, dan sumber daya yang tersedia.
