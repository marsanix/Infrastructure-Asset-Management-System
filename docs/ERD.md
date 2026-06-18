# IAMS Entity Relationship Diagram

## Core Tables (13)

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│  roles      │     │ departments  │     │  locations  │
│─────────────│     │──────────────│     │─────────────│
│ id (PK)     │     │ id (PK)      │     │ id (PK)     │
│ name UNIQUE │     │ name UNIQUE  │     │ name        │
│ is_active   │     │ description  │     │ description │
│ created_at  │     │ created_at   │     │ created_at  │
│ updated_at  │     │ updated_at   │     │ updated_at  │
└──────┬──────┘     └──────┬───────┘     └──────┬──────┘
       │ FK                │ FK (dept)          │ FK (loc)
       ▼                   ▼                    ▼
┌─────────────────────────────────────────────────────────────┐
│                           users                              │
│─────────────────────────────────────────────────────────────│
│ id (PK) │ name │ email UNIQUE │ password_hash │ role_id (FK)│
│ department_id (FK) │ is_active │ last_login │ created_at   │
└─────┬─────────────────────────────────────────┬─────────────┘
      │ FK (requester/assignee/approver)        │ FK (user_id)
      ▼                                         ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐
│  categories  │  │   brands     │  │       assets         │
│──────────────│  │──────────────│  │──────────────────────│
│ id (PK)      │  │ id (PK)      │  │ id (PK)              │
│ name UNIQUE  │  │ name UNIQUE  │  │ asset_tag UNIQUE     │
│ description  │  │ description  │  │ serial_number UNIQUE │
│ created_at   │  │ created_at   │  │ po_number           │
│ updated_at   │  │ updated_at   │  │ model_id (FK)       │
└──────┬───────┘  └──────┬───────┘  │ location_id (FK)    │
       │ FK (cat)        │ FK (brand)│ user_id (FK)        │
       ▼                 ▼           │ status ENUM         │
┌────────────────────────────────┐   │ purchase_date       │
│           models               │   │ warranty_months     │
│────────────────────────────────│   │ os_license          │
│ id (PK) │ name │ brand_id (FK)│   │ created_at          │
│ category_id (FK) │ specs      │   │ updated_at          │
└────────────────────────────────┘   └──────────┬─────────┘
                                                │ 1:1
                                    ┌───────────▼───────────┐
                                    │   network_details     │
                                    │───────────────────────│
                                    │ asset_id (PK, FK)     │
                                    │ ip_address │ mac_addr │
                                    │ hostname │ vlan │ notes│
                                    └───────────────────────┘

Extension tables:
  service_requests ── FK: requester_id, assigned_to_id, asset_id, dept_id
  change_requests  ── FK: requester_id, assignee_id, approver_id, asset_id,
                          incident_id, problem_id, request_id
  incidents        ── FK: asset_id, assignee_id
  problems         ── FK: owner_id
  asset_credentials── FK: asset_id (1:1), encrypted_secret, nonce
  audit_logs       ── FK: actor_user_id
```

## Relationships Summary

| Parent | Child | Type |
|--------|-------|------|
| roles | users | 1:N |
| departments | users | 1:N |
| locations | assets | 1:N |
| categories | models | 1:N |
| brands | models | 1:N |
| models | assets | 1:N |
| users | assets (user_id) | 1:N |
| assets | network_details | 1:1 |
| assets | asset_credentials | 1:1 |
| users | service_requests (requester) | 1:N |
| users | change_requests (requester) | 1:N |
| assets | incidents | 1:N |
| users | audit_logs (actor) | 1:N |
