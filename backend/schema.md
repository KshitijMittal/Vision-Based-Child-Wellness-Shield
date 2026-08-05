# Appwrite Cloud Schema — Deployable Definitions

This file mirrors `docs/Backend Schema.md` into the concrete resources created on
Appwrite Cloud (new-generation API: databases → **tables** → **columns**).
String-valued columns are created as **text** columns — the current Appwrite API
(the legacy `string` column type is deprecated since 1.9.0).

Provision with:

```bash
.venv/Scripts/python.exe backend/scripts/setup_appwrite.py
```

The script is **idempotent** — safe to run repeatedly.

---

## Resources

| Resource | ID | Notes |
|---|---|---|
| Database | `main` | Single database for the whole project |
| Table | `screening_documents` | One row per screening session |
| Auth | `users` (built-in) | Managed by Appwrite Auth — never created manually |

## Table: `screening_documents`

- **row_security:** enabled — every row is sealed to its owner account.
- **Table permissions:** `create` for role `member` only. No table-level read/update/delete —
  rows are accessed exclusively through their own `user:{account_id}` permissions
  (Backend Schema §8.1). No admin role exists in v1.

### Columns (35 cloud fields; `$id` is auto-generated)

#### Block A — Meta & Identification

| Column | Type | Required |
|---|---|---|
| `account_id` | text | yes |
| `child_name` | text | yes |
| `child_age_years` | integer | yes |
| `child_age_months` | integer | yes |
| `child_sex` | enum `["boy","girl"]` | yes |
| `village` | text | no |
| `consent_given` | boolean | yes |
| `consent_timestamp` | datetime | yes |
| `analysis_timestamp` | datetime | yes |
| `created_at` | datetime | yes |
| `updated_at` | datetime | yes |

#### Block B — Measurements & BMI

| Column | Type | Required |
|---|---|---|
| `estimated_height_cm` | float | yes |
| `confirmed_weight_kg` | float | yes |
| `bmi` | float | yes |
| `who_percentile` | float | yes |
| `who_category` | enum `["severely_underweight","underweight","normal","overweight","obese"]` | yes |
| `who_chart_version` | text | yes |

#### Block C — Symptom Detection (5 symptoms × 3 fields)

Symptoms: `jaundice`, `pallor`, `skin`, `goitre`, `malnutrition`.

For each symptom `S`:

| Column | Type | Required |
|---|---|---|
| `symptom_S_status` | enum `["not_detected","low_confidence","detected","not_assessed"]` | yes |
| `symptom_S_confidence` | float | yes |
| `symptom_S_model_ver` | text | yes |

#### Block D — Storage & Sync (cloud fields only)

| Column | Type | Required |
|---|---|---|
| `pdf_file_id` | text | no |
| `capture_quality` | enum `["good","low"]` | yes |

> The three local-only fields (`sync_status`, `sync_retry_count`, `sync_last_attempt`)
> exist only in the phone's SQLite mirror and are **never** uploaded (Backend Schema §5.1).

### Indexes

| Key | Columns | Order | Purpose (Backend Schema §10.1) |
|---|---|---|---|
| `by_account` | `account_id`, `created_at` | ASC, DESC | "My Documents" list |
| `by_account_name` | `account_id`, `child_name`, `created_at` | ASC, ASC, DESC | "Same child as before?" lookup |
| `by_created_at` | `created_at` | ASC | auto-age-out query |

---

## Storage bucket (Phase 5)

PDFs land in an Appwrite Storage bucket (`screening_pdfs`) when the sync engine is
built (Phase 5). Not created in Phase 1 — the collection schema is the only Phase 1
backend deliverable.
