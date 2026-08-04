# Backend Schema — Vision-Based Child Wellness Shield

| Field | Value |
|---|---|
| **Document** | Backend Schema Document |
| **Status** | Draft v0.1 — awaiting review |
| **Date** | August 4, 2026 |
| **Author** | Project team (collaboratively drafted) |

---

## 1. Document Control

| Version | Date | Author | Change Summary |
|---|---|---|---|
| 0.1 | 2026-08-04 | Team | Initial draft from discovery interviews |

---

## 2. Executive Summary

This document defines the **data model and storage architecture** for the Vision-Based Child Wellness Shield. It covers the database schema (both cloud and local), the offline sync queue, security rules, and the data flow from capture to cloud storage.

The schema is built on three core design decisions:

1. **Two collections only** — Users (Appwrite Auth) + Screening Documents (flat NoSQL records). Everything about a child lives inside the document; no separate child profiles.
2. **Offline-first** — Documents are created locally with phone-generated UUIDs, stored in a local SQLite table mirroring the cloud schema, and synced to Appwrite when connectivity is available.
3. **Account-sealed** — Each account sees only its own documents. Appwrite's built-in auth rules enforce this automatically. No cross-account visibility exists in v1.

Storage is minimized: **no raw photos are ever stored**, only the final PDF. Cloud copies auto-age out after 6 months.

---

## 3. Data Model Overview

### 3.1 Collections

| Collection | Storage | Managed by | Records |
|---|---|---|---|
| `users` | Appwrite Auth | Appwrite (built-in) | Worker/staff accounts; one per phone |
| `screening_documents` | Appwrite Database + local SQLite | Custom | One record per screening session |

### 3.2 Key design principles

| Principle | Implementation |
|---|---|
| **Flat, not nested** | No sub-collections or child profiles. Every screening is a self-contained document. |
| **Self-auditing** | Consent, model version, and confidence scores travel with the document. No separate audit trail. |
| **Offline-compatible** | All fields are created and written on the phone. The cloud is a passive sync target, never a source of truth. |
| **Storage-light** | Only metadata and PDF file IDs are stored in the database. Raw photos are never persisted. |

---

## 4. The `screening_documents` Collection (Cloud + Local)

This is the **only custom collection** in the system. The same schema is used for both the Appwrite cloud database and the local SQLite table on the phone.

### 4.1 Full field list

#### Block A: Meta & Identification

| Field | Type | Example | Notes |
|---|---|---|---|
| `$id` | string (UUID) | `"a1b2c3d4-e5f6-7890-abcd-ef1234567890"` | **Locally-generated UUID on the phone** (Round 1). Unique across all devices. No server needed. |
| `account_id` | string | `"user_abc123"` | Appwrite User ID. Links the document to its owner. Set automatically by Appwrite on upload. |
| `child_name` | string | `"Aarav"` | Simple name field. Not a unique identifier — name-linking is a convenience search, not a key. |
| `child_age_years` | number | `6` | Age in years (user taps big year buttons per UI/UX Brief). Input is in years. |
| `child_age_months` | number | `72` | Age in months = `child_age_years * 12`. Converted on-device. Stored as number for WHO percentile lookup. Both raw and converted values preserved. |
| `child_sex` | string | `"boy"` | `"boy"` or `"girl"`. Required for WHO BMI-for-age percentile calculation. |
| `village` | string (optional) | `"Rampur"` | Free-text village/area name. Optional. Useful for center-level aggregation in future phases. |
| `consent_given` | boolean | `true` | One-tap consent recorded per document (Round 1). |
| `consent_timestamp` | datetime | `2026-08-04T09:15:30+05:30` | Exact timestamp of consent tap. Timezone-aware. |
| `analysis_timestamp` | datetime | `2026-08-04T09:15:45+05:30` | When the analysis completed. |
| `created_at` | datetime | `2026-08-04T09:15:30+05:30` | When the document was first created (draft start). |
| `updated_at` | datetime | `2026-08-04T09:15:50+05:30` | Last modification time. |

#### Block B: Measurements & BMI

| Field | Type | Example | Notes |
|---|---|---|---|
| `estimated_height_cm` | number | `115.2` | Height estimated from body-proportion AI (Round 2). Raw value preserved. |
| `confirmed_weight_kg` | number | `18.5` | User-confirmed weight from the hybrid AI+confirm screen (Round 2). |
| `bmi` | number | `14.0` | Computed BMI = weight(kg) / height(m)². |
| `who_percentile` | number | `12.5` | WHO BMI-for-age percentile (0–100). Computed on-device at analysis time. |
| `who_category` | string | `"underweight"` | WHO category: `"severely_underweight"`, `"underweight"`, `"normal"`, `"overweight"`, `"obese"`. |
| `who_chart_version` | string | `"who-2006-v1"` | Version of the WHO growth chart data used. Enables future re-calculation if charts are updated. |

#### Block C: Symptom Detection Results (5 symptoms × 3 fields each = 15 fields)

Each of the 5 symptoms stores **3 fields** — status, confidence, and model version (Round 2).

The 5 symptoms are: **Jaundice**, **Pallor**, **Skin conditions**, **Goitre**, and **Malnutrition cues**.

For each symptom, the same 3-field pattern is repeated. Below is the full list:

| Field | Type | Example | Notes |
|---|---|---|---|
| `symptom_jaundice_status` | string | `"detected"` | Status enum: `"not_detected"` / `"low_confidence"` / `"detected"` / `"not_assessed"` |
| `symptom_jaundice_confidence` | number | `0.87` | Model confidence score (0.0–1.0) |
| `symptom_jaundice_model_ver` | string | `"v1.2"` | Model version that made this call |
| `symptom_pallor_status` | string | `"not_detected"` | Same status enum |
| `symptom_pallor_confidence` | number | `0.92` | Confidence score |
| `symptom_pallor_model_ver` | string | `"v1.2"` | Model version |
| `symptom_skin_status` | string | `"not_assessed"` | Same status enum |
| `symptom_skin_confidence` | number | `0.0` | Confidence score |
| `symptom_skin_model_ver` | string | `"v1.0"` | Model version |
| `symptom_goitre_status` | string | `"low_confidence"` | Same status enum |
| `symptom_goitre_confidence` | number | `0.45` | Confidence score |
| `symptom_goitre_model_ver` | string | `"v0.9"` | Model version |
| `symptom_malnutrition_status` | string | `"not_detected"` | Same status enum |
| `symptom_malnutrition_confidence` | number | `0.95` | Confidence score |
| `symptom_malnutrition_model_ver` | string | `"v1.1"` | Model version |

**Note:** The `_status` field uses one of four values:
- `"not_detected"` — model is confident the symptom is absent
- `"low_confidence"` — model couldn't decide (e.g., poor lighting, equivocal signs)
- `"detected"` — model is confident the symptom is present
- `"not_assessed"` — this symptom was not analyzed (e.g., model missing, skipped)

#### Block D: Storage & Sync

| Field | Type | Example | Notes |
|---|---|---|---|
| `pdf_file_id` | string (optional) | `"pdf_abc123"` | Appwrite Storage file ID for the generated PDF. Set after sync. Null until then. |
| `capture_quality` | string | `"good"` | `"good"` or `"low"`. Set by the quality-check pipeline. `"low"` = "Low quality capture" note on PDF. |
| `sync_status` | string | `"synced"` | **Local-only field.** `"draft"` / `"pending"` / `"synced"`. Not uploaded to cloud. |
| `sync_retry_count` | number | `0` | **Local-only field.** Number of failed sync attempts. Resets on success. |
| `sync_last_attempt` | datetime (optional) | `2026-08-04T12:00:00+05:30` | **Local-only field.** Timestamp of last sync attempt. |

### 4.2 Total field count

| Block | Fields |
|---|---|
| Block A: Meta & Identification | 12 |
| Block B: Measurements & BMI | 6 |
| Block C: Symptom Detection (5 × 3) | 15 |
| Block D: Storage & Sync | 5 (2 cloud + 3 local-only) |
| **Total** | **38 fields** |

In NoSQL terms, this is a single document with 35 fields that reach the cloud (the 3 local-only sync fields never leave the phone; the 15 symptom fields are grouped by naming convention but are simple key-value pairs). No sub-collections, no joins, no complex queries.

---

## 5. Local SQLite Schema (Phone)

The phone maintains a **single local table** that mirrors the cloud schema (Round 3). The same fields, same types, same structure.

### 5.1 Local-only fields

Three fields exist **only on the phone** and are never uploaded to Appwrite:

| Field | Purpose |
|---|---|
| `sync_status` | `"draft"` → `"pending"` → `"synced"`. Tracks the document's lifecycle. |
| `sync_retry_count` | Incremented on each failed sync attempt. Reset on success. |
| `sync_last_attempt` | Timestamp of the most recent sync attempt. Used for backoff logic. |

### 5.2 Document lifecycle in local storage

```
User starts capture
        │
        ▼
Record created: sync_status = "draft"
(only child_name, age, sex, consent filled)
        │
        ▼
Analysis completes → BMI + symptoms added
        │
        ▼
Record updated: sync_status = "pending"
PDF generated and saved locally
        │
        ▼
Phone online? ──yes──▶ Upload to Appwrite → sync_status = "synced"
        │
        no
        ▼
Record stays "pending" → sync counter (⬆ N) shown on Home
        │
        ▼
Phone later gets signal → auto-sync (idempotent, retry with backoff)
```

### 5.3 Crash safety (draft recovery)

- The record is created with `sync_status = "draft"` the moment the user taps **"Yes, I agree"** on consent.
- If the phone crashes mid-analysis, the next open shows a **"Resume unfinished document?"** prompt.
- If the user taps **Yes**, the draft record is loaded and analysis can restart.
- If the user taps **No**, the draft is deleted (SQLite `DELETE`).
- Drafts older than 24 hours are auto-cleaned on app startup.

---

## 6. Sync Queue & Data Flow

### 6.1 The sync queue is a status filter (Round 3)

There is **no separate queue table**. The sync queue is simply:

```sql
SELECT * FROM screening_documents WHERE sync_status = 'pending' ORDER BY created_at ASC;
```

The queue is a **view** of the documents table — every document with a pending status is waiting to be uploaded.

### 6.2 Sync flow

```
Phone detects connectivity (WiFi / mobile data)
        │
        ▼
Loop through pending documents (oldest first)
        │
        ▼
Upload document record (JSON) → Appwrite Database
Upload PDF file → Appwrite Storage
        │
        ▼
Both succeed? ──yes──▶ Update sync_status = "synced"
        │
        no
        ▼
Increment sync_retry_count
Apply exponential backoff (e.g., 30s, 2min, 10min, 30min, 1hr cap)
Retry on next connectivity event
```

### 6.3 Idempotency

- Each document's `$id` is a UUID generated on the phone. The same UUID is used for the local record and the cloud record.
- If a sync is interrupted (half-uploaded, timeout) and retried, the UUID ensures the same document is **upserted** (inserted or updated), never duplicated.
- PDF files are uploaded with the same UUID as the filename — Appwrite Storage's `updateFile` behavior on the same ID prevents duplicates.

### 6.4 Sync status visibility

- **Home screen:** small sync counter (⬆ N) next to "My Documents" — shows count of pending documents.
- **No other sync UI exists.** No progress bars, no "Sync Now" buttons, no error toasts. Sync is invisible to the user by design (per UI/UX Brief, principle #6: "Offline is invisible").

---

## 7. The `users` Collection (Appwrite Auth)

The `users` collection is managed entirely by Appwrite's built-in authentication system. We do not create a custom `users` table.

### 7.1 User attributes

| Attribute | Type | Notes |
|---|---|---|
| `$id` | string (auto-generated) | Appwrite user ID. Used as `account_id` in screening documents. |
| `name` | string | Full name (from signup). |
| `phone` | string | Primary identifier (phone number). |
| `password` | hashed string | Appwrite handles hashing. |
| `role` | string (custom label) | `"health_worker"` or `"family_member"`. Set at signup, changeable in Setup. |
| `language` | string (custom label) | `"hindi"` or `"english"`. Set at signup, changeable in Setup. |

**Custom labels** (`role`, `language`) are stored as Appwrite user preferences — a built-in key-value store on the user object. No extra database collection needed.

### 7.2 Auth rules

| Action | Rule |
|---|---|
| Signup | Anyone can create an account. Requires internet (only time it's mandatory). |
| Login | One account per phone. Phone number + password. |
| Session | Persistent session — stays logged in until explicitly logged out. |
| Password reset | Optional (v1 supports account deletion + re-creation as fallback). |

---

## 8. Security & Access Control

### 8.1 Access model: user-owns-documents (Round 4)

Appwrite's built-in permission model is used directly:

- **Document read/write:** Only the creator (the `account_id` that matches the logged-in user) can read or write a document.
- **No cross-account access:** No user, including health workers, can see documents from another account.
- **No admin role in v1:** There is no "superuser" who can see all documents. Each account is a sealed world.

This is enforced by Appwrite's **user role** permission:

```json
{
  "read": ["user:{account_id}"],
  "write": ["user:{account_id}"]
}
```

### 8.2 Consent audit

Consent is stored **inside the document record** (Round 4) — not in a separate log. The `consent_given` boolean + `consent_timestamp` datetime inside each document is the sole consent record. Every document is self-auditing.

### 8.3 Encryption

- **In transit:** All Appwrite connections use HTTPS. (Appwrite's default.)
- **At rest:** Appwrite encrypts data at rest using standard AES-256. (Appwrite's default.)
- **No client-side encryption:** The phone does not encrypt documents before upload. The paper PDF is the durable record; the cloud copy is a backup and access layer.

### 8.4 Data retention

| Location | Retention policy | Notes |
|---|---|---|
| **Phone (local)** | Indefinite — until phone storage is low | Users never manually delete. Low-storage warning may prompt cleaning. |
| **Cloud (Appwrite Database)** | **6 months** auto-age-out (Round 3) | Records older than 6 months are automatically deleted from the cloud database. |
| **Cloud (Appwrite Storage / PDFs)** | **6 months** auto-age-out | PDF files older than 6 months are deleted from cloud storage. |
| **Paper (printed PDF)** | Kept by the user indefinitely | The paper document is the durable record. The cloud is a working copy. |

**Auto-age-out mechanism:** A scheduled Appwrite Function runs daily, querying `created_at < 6 months ago` and deleting those documents + their associated PDFs. This keeps the 2 GB free storage comfortable indefinitely.

---

## 9. API Endpoints

Minimal API surface, since the app is offline-first. All endpoints are behind Appwrite Auth.

| Endpoint | Method | Purpose | Request body | Response |
|---|---|---|---|---|
| `/sync/documents` | POST | Batch upload pending document records | Array of JSON document objects (without local-only fields) | `{ "synced": [ids], "failed": [ids] }` |
| `/sync/pdf` | POST | Upload a single PDF file | Multipart: file + document UUID | `{ "file_id": "pdf_abc123" }` |
| `/documents` | GET | List own documents (web app) | Query: `?limit=50&offset=0&search=name` | Array of document summaries (no PDF file) |
| `/documents/:id` | GET | Get a single document + PDF download URL | — | Full document JSON + PDF download URL |
| `/documents/:id/pdf` | GET | Download the PDF file | — | PDF binary |

All endpoints are **read-only for the web app** (except sync). The phone never calls these endpoints for the core capture loop — it only uses them for sync.

---

## 10. Indexes & Queries

### 10.1 Appwrite indexes

| Index | Fields | Purpose |
|---|---|---|
| `by_account` | `account_id` ASC, `created_at` DESC | "My Documents" list — newest first for a given account. |
| `by_account_name` | `account_id` ASC, `child_name` ASC, `created_at` DESC | "Same child as before?" lookup — find documents by name within this account. |
| `by_created_at` | `created_at` ASC | Auto-age-out query — find documents older than 6 months. |

### 10.2 Local SQLite indexes

| Index | Fields | Purpose |
|---|---|---|
| `sync_status_idx` | `sync_status` ASC | Sync queue — find all pending documents. |
| `child_name_idx` | `child_name` ASC | Name-linking — "Same child as before?" search. |
| `created_at_idx` | `created_at` DESC | Document list — newest first. |
| `draft_cleanup_idx` | `sync_status` ASC, `created_at` ASC | Find old drafts for auto-cleanup. |

---

## 11. Storage Budget (Revisited)

With the schema finalized, the real storage math:

| Item | Size per document | 150 docs/day | 30 days | 6 months |
|---|---|---|---|---|
| Document record (JSON) | ~1–2 KB | ~225 KB | ~6.75 MB | ~40.5 MB |
| PDF file (with chart, no photo) | ~50–150 KB | ~15 MB avg | ~450 MB | ~2.7 GB |
| **Total** | **~51–152 KB** | **~15.2 MB** | **~456 MB** | **~2.7 GB** |

**At 6 months, the 2 GB free storage is exceeded.** This is why the **6-month auto-age-out** is critical — it keeps the storage under the free tier limit permanently. At lower volumes (say, 50 docs/day), the 2 GB limit lasts ~18 months.

Mitigations (from TRD Section 11.2):
1. **Auto-age-out at 6 months** keeps storage under 2 GB at any reasonable village volume.
2. **Self-hosting Appwrite** (free, open-source) removes the cap entirely.
3. **PDF compression** can reduce file sizes by 30–50% if needed.

---

## 12. Data Flow Diagram (End-to-End)

```
┌─────────────────────────────────────────────────────────────────────┐
│                         PHONE (offline-first)                       │
│                                                                     │
│  Capture → Draft created (sync_status = "draft")                    │
│      │                                                              │
│      ▼                                                              │
│  Analysis → BMI + symptoms filled → sync_status = "pending"         │
│      │                                                              │
│      ▼                                                              │
│  PDF generated → saved to app storage                               │
│      │                                                              │
│      ▼                                                              │
│  Queue: "pending" documents in SQLite                               │
│  Sync counter (⬆ N) shown on Home                                   │
│                                                                     │
│  ── When online ──────────────────────────────────────────────      │
│      │                                                              │
│      ▼                                                              │
│  POST /sync/documents → Appwrite Database                           │
│  POST /sync/pdf → Appwrite Storage                                  │
│      │                                                              │
│      ▼                                                              │
│  sync_status = "synced"                                             │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      APPWRITE CLOUD                                 │
│                                                                     │
│  Database: screening_documents (one per screening)                  │
│  Storage: PDF files (referenced by file_id)                         │
│  Auth: users (one account per phone)                                │
│                                                                     │
│  ── Auto-age-out (daily Function) ──                                │
│  Documents where created_at > 6 months → delete                     │
└─────────────────────────────────────────────────────────────────────┘
                              ▲
                              │ (web app: view/download own docs)
┌─────────────────────────────┴───────────────────────────────────────┐
│                         WEB APP (secondary)                         │
│                                                                     │
│  Login with same account → view own documents only                  │
│  Search by child name, download PDF, print                          │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 13. Schema Evolution & Migration

### 13.1 Adding a new field

Since Appwrite is a NoSQL document database, adding a new field is schema-less — new documents get the field, old documents don't have it. The app code handles missing fields gracefully (e.g., `?? null` or `?? 0`).

### 13.2 Adding a new symptom

A new symptom (e.g., "dental caries" in a future version) adds 3 fields to the schema:
- `symptom_dental_status`
- `symptom_dental_confidence`
- `symptom_dental_model_ver`

No migration. No schema change. The app reads the new fields if present, ignores them if not.

### 13.3 Model version tracking

The `*_model_ver` fields enable **retrospective analysis**: if a new model version is deployed, old documents can be re-analyzed (or their results compared) because the version that produced each result is recorded.

---

## 14. Open Questions

- Exact phone number format for signup (with/without country code?).
- Whether `village` should be a free-text field or a dropdown (for future center-level grouping).
- Whether the daily summary (worker view) needs a separate lightweight API endpoint or can be computed client-side from the documents list.
- Should the auto-age-out Function send a warning before deleting (e.g., email or in-app notification), or run silently?

---

*End of Backend Schema v0.1 — ready for team review and iteration.*