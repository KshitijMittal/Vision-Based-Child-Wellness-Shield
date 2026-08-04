# TRD — Vision-Based Child Wellness Shield

| Field | Value |
|---|---|
| **Document** | Technical Requirements Document (TRD) |
| **Status** | Draft v0.1 — awaiting review |
| **Date** | August 3, 2026 |
| **Author** | Project team (collaboratively drafted) |

---

## 1. Document Control

| Version | Date | Author | Change Summary |
|---|---|---|---|
| 0.1 | 2026-08-03 | Team | Initial draft from discovery interviews |

---

## 2. Executive Summary

This document defines **how** the Vision-Based Child Wellness Shield will be built
technically. It covers architecture, technology stack, the computer-vision pipeline,
model training strategy (including the GPU-free workflow), capture-quality logic,
offline document sync, privacy, and validation.

The technical north star is the same as the product's: **a villager or health worker
captures a single photo of a child on a low-end Android phone and receives a printable
PDF document within ~10 seconds — fully offline, at zero cost.**

Key technical commitments:

| Commitment | Decision |
|---|---|
| Platform | Android app (primary) + Web app (secondary, view/download documents) |
| AI execution | Hybrid — on-device first (MediaPipe + TensorFlow Lite), cloud fallback |
| Backend | Appwrite Cloud (free tier): database + auth + file storage |
| Document | Printable PDF, one page (simple top, technical bottom) |
| Offline | Local-first storage → auto-sync when online (idempotent) |
| Devices | Low-end Android: 2GB RAM, Android 8+ |
| Model training | Free cloud GPUs (Google Colab / Kaggle), transfer learning |
| Cost | Zero monetary cost — free tiers and open-source tooling only |

---

## 3. System Architecture

```
┌────────────────────────────── ANDROID APP (field, offline-first) ──────────────────────────────┐
│                                                                                                │
│  📸 Capture         🧠 Analyze (on-device)         📄 Document          ☁️ Sync                  │
│  ─────────          ───────────────────           ───────────          ────────                 │
│  Camera intent      Quality checks                PDF generator        Local queue (SQLite)     │
│  Consent screen     (brightness, sharpness,       (one page, WHO       → auto-upload when       │
│  Age/sex entry      face, pose, child count)      percentile chart)    online                   │
│  Voice guidance     BMI estimation                Local draft save     Idempotent, unique IDs   │
│                     Symptom classifiers           (crash-safe)         Retry with backoff       │
│                     (TFLite models)                                    No raw photos stored      │
│                                                                                                │
└──────────────────────────────────────┬─────────────────────────────────────────────────────────┘
                                       │ HTTPS (when online)
                                       ▼
                    ┌────────────────────────────────────────────┐
                    │         APPWRITE CLOUD (free tier)          │
                    │  • Database — document records             │
                    │  • Storage — generated PDFs only           │
                    │  • Auth — worker/staff accounts            │
                    └────────────────────────────────────────────┘
                                       ▲
                                       │ (view/download via browser)
                    ┌──────────────────┴──────────────────┐
                    │        WEB APP (secondary)          │
                    │  Browse history, view/share PDFs     │
                    └─────────────────────────────────────┘

┌────────────────────────── MODEL TRAINING (no local GPU needed) ──────────────────────────────┐
│  Local machine                 Free cloud GPU (Colab T4 / Kaggle 30h·wk⁻¹)    Result         │
│  Dataset folders +             Transfer learning on MobileNet/EfficientNet    one .tflite    │
│  training script ──upload──▶   via TFLite Model Maker (minutes–1 hour)   ──▶  file → app     │
│  (via Drive / GitHub)                                                            assets       │
└────────────────────────────────────────────────────────────────────────────────────────────────┘
```

**Design principle:** the phone is a self-contained unit. Analysis, quality checks,
PDF generation, and storage all work with zero connectivity. The cloud is a backup
and access layer, never a dependency for the core loop.

---

## 4. Technology Stack

| Layer | Choice | Rationale |
|---|---|---|
| Mobile framework | Flutter (single codebase → Android app + future iOS) | Free, open-source; good TFLite interop; offline-friendly local DB |
| On-device ML runtime | TensorFlow Lite (`.tflite` models) | Runs on 2GB-RAM Android phones, fully offline |
| Pose estimation | MediaPipe (BlazePose / Pose Landmarker) | Free, lightweight, 33-point body landmarks on low-end devices |
| Face detection | MediaPipe Face Detector / Face Mesh | Used for "face visible / facing camera" quality checks |
| Symptom classifiers | Custom TFLite image classifiers (transfer-learned) | One small model per symptom group (or one multi-class model) |
| Local storage | SQLite (e.g., via `sqflite` in Flutter) | Offline document queue + draft recovery |
| Backend | Appwrite Cloud (free tier) | Database + Auth + Storage in one zero-cost platform; open-source → self-hostable later |
| PDF generation | Client-side PDF library (e.g., `pdf` package for Flutter) | Documents generated on-device → works offline |
| Web app | Flutter Web (same codebase) | Secondary view/download layer; free hosting (e.g., Cloudflare Pages / GitHub Pages) |
| Model training | Google Colab free tier + Kaggle notebooks | Free cloud GPUs (see Section 7) |
| Training framework | TensorFlow / TFLite Model Maker | Transfer learning on MobileNet / EfficientNet |

**Note on Appwrite (research-verified):** Appwrite is an authentic, widely used
open-source Backend-as-a-Service (BSD-3 license, funded/maintained since 2019, $27M
in funding). Its free tier comfortably covers the pilot. Key free-tier limits and our
fit are in Section 11.

---

## 5. Platform & Device Requirements

### 5.1 Platforms
- **Primary:** Android app (field capture, on-device analysis, PDF generation, offline sync).
- **Secondary:** Web app (view/download generated documents; same codebase via Flutter Web).

### 5.2 Minimum device floor (field)
| Requirement | Minimum |
|---|---|
| Android version | Android 8.0 (API 26)+ |
| RAM | 2 GB |
| Camera | Standard rear camera ≥ 5 MP (autofocus preferred) |
| Storage free space | ≥ 500 MB |
| Screen | Any (UI is icon/voice-driven, large touch targets) |

**Why this floor:** rural India's common ₹7,000–10,000 phones sit exactly at this
spec. If the app runs here, it runs everywhere — and villagers can use their own
devices, which is what makes the "anyone can use it" vision real.

### 5.3 Future hardware (not v1)
- Fixed camera **kiosk** at larger centers (identical app logic, camera swapped).

---

## 6. AI / Computer Vision Pipeline

### 6.1 Toolkit
- **MediaPipe** for pose + face landmarks (33 body keypoints; face detection/mesh).
- **TensorFlow Lite** for the custom symptom classifiers.
- All inference **on-device** (hybrid with cloud fallback for heavy retries; see Section 6.6).

### 6.2 BMI estimation pipeline
```
Photo → pose landmarks → body-proportion height estimate
                          + weight estimate (AI, then user-confirmed)
      → BMI = weight(kg) / height(m)²
      → WHO BMI-for-age chart (needs AGE + SEX) → percentile & category
```

| Step | Method | Decision |
|---|---|---|
| **Height** | **Body-proportion AI** — estimate height from detected body proportions and typical anthropometric ratios (e.g., total height vs. keypoint segment lengths), calibrated per age band | Locked (Round 2) |
| **Weight** | **Hybrid — AI + confirm** — AI estimates weight from body size/shape; the worker/parent confirms or corrects the value in one simple tap screen | Locked (Round 2) |
| **Age & sex** | **Simple manual entry** — big year/month buttons + one-tap boy/girl screen (~5 s) | Locked (Round 3) |
| **BMI-for-age** | WHO growth charts (WHO LMS data, openly licensed) → percentile + category | Locked (Round 4) |

**Why manual age/sex (not AI):** BMI-for-age is only as accurate as the age fed into
it. Face-based age guessing is ±2–3 years off, which can misclassify a healthy child.
Five seconds of big-button entry eliminates that error class.

### 6.3 Symptom detection (5 targets)
| Symptom | Detection approach | Public training data | v1 status |
|---|---|---|---|
| **Jaundice** (yellowing of skin/sclerae) | Image classifier (skin/face region) | ✅ Kaggle *Jaundice Image Data* (~600+ validated images) | Trainable now |
| **Pallor / anemia cues** | Image classifier (palpebral conjunctiva / skin tone) | ⚠️ Small — Hugging Face *Anemia-Eyes* (~218) + Kaggle conjunctiva set | Trainable, needs supplementation |
| **Skin conditions** (rashes, lesions) | Image classifier (region classification) | ✅ DermNet via Kaggle (~19,500 photos, 23 categories) | Trainable now |
| **Thyroid swelling (Goitre)** | Image classifier (neck region) | ❌ No public photo dataset (only ultrasound images exist) | Seed from ~200 Wikimedia Commons images + field collection |
| **Visual malnutrition cues** | Image classifier (full body: wasting/thinness cues) | ❌ No public photo dataset (UNICEF/WHO data is tabular) | Custom field collection + augmentation |

### 6.4 Model output policy (screening, not diagnosis)
- Every model outputs a **confidence score**. Below a threshold → the symptom is
  reported as *"could not be assessed"* rather than a false positive.
- The PDF always carries: **"This is a screening result, not a diagnosis."**

### 6.5 Cloud fallback (hybrid AI)
- On-device inference is primary. If a low-end device is too slow (>10 s budget) or
  a model is missing locally, analysis can fall back to a cloud worker — but the
  product must never *require* the cloud.

### 6.6 Accuracy targets (to validate in pilot)
| Metric | Target |
|---|---|
| BMI estimate vs manual measurement | Within acceptable clinical band (final target set in Section 16, Validation Plan) |
| Symptom detection | ≥ 80% sensitivity at acceptable specificity on field photos (pilot-measured) |
| False "at-risk" flags | Minimized — screening tool must not over-alarm parents |

---

## 7. Model Training Strategy (No Local GPU Required)

The user's machine has **no GPU** — this is fully solved by free cloud GPUs. The
critical insight: **training and the app are separate worlds that touch at exactly
one point — the model file.**

### 7.1 The workflow
1. **Local machine** keeps the entire project. Only two things ever go to the cloud:
   the **dataset folders** and **one training script/notebook** (~100 lines).
2. **Transfer to cloud** via Google Drive (mount in Colab) or GitHub (`git clone` in
   Colab/Kaggle), or upload directly on kaggle.com.
3. **Train on free cloud GPU** — transfer learning on MobileNet / EfficientNet via
   **TFLite Model Maker**: minutes to ~1 hour, typically 90%+ accuracy for image
   classifiers of this type.
4. **Download the result** — one small `.tflite` file (a few MB).
5. **Drop it into app assets** — the phone loads it at runtime; it runs offline forever.

### 7.2 Free cloud GPU options (current)
| Platform | Free GPU | Practical limits |
|---|---|---|
| Google Colab | NVIDIA T4 | ~12-hour sessions; free tier with usage caps |
| Kaggle notebooks | NVIDIA P100/T4 | **30 GPU-hours per week** — enough for weekly retraining |
| Hugging Face Spaces | Limited free CPU/GPU | Secondary option |

**Transfer learning is the key enabler:** we never train from scratch. Pre-trained
MobileNet/EfficientNet weights + a small custom head reach usable accuracy in
minutes–1 hour on these free GPUs.

### 7.3 Dataset strategy (honest picture)
| Source | Use |
|---|---|
| Kaggle *Jaundice Image Data* | Jaundice training seed |
| DermNet (Kaggle) | Skin conditions seed |
| Hugging Face *Anemia-Eyes* + Kaggle conjunctiva | Pallor seed (small — augment + supplement) |
| Wikimedia Commons (open-license, ~200 images) | Goitre seed |
| **Field pilot collection** (with consent) | Goitre + malnutrition real-world data — the missing piece; this is how real medical-AI projects are built |
| **Data augmentation** (rotation, color shift, crop, flip) | Multiply every labeled image; stretch small datasets |

**Note:** bulk-scraping Google Images is not viable (ToS violations, blocking,
unverified content) and is excluded by design.

### 7.4 Model inventory (v1)
| Model | Input | Output | Size budget |
|---|---|---|---|
| Pose Landmarker (MediaPipe) | photo | 33 body keypoints | ~4–10 MB |
| Face Detector (MediaPipe) | photo | face boxes | ~1–2 MB |
| BMI height/weight estimator (custom TFLite) | keypoints + age band | height, weight | ~1–3 MB |
| Jaundice classifier | face/skin crop | confidence | ~1–5 MB |
| Pallor classifier | conjunctiva/eye crop | confidence | ~1–5 MB |
| Skin condition classifier | region crop | confidence | ~1–5 MB |
| Goitre classifier | neck crop | confidence | ~1–5 MB |
| Malnutrition classifier | full-body crop | confidence | ~1–5 MB |

All models packaged into the app; total footprint target < 50 MB.

---

## 8. Capture Quality Checks (Voice-Guided Retake)

Single-photo capture (locked in Round 3) is backed by instant on-device quality
checks. Each check is a cheap algorithm (milliseconds, no internet, no big AI) with a
pre-recorded local-language voice line mapped to it:

| Check | Detection method | Voice prompt |
|---|---|---|
| Too dark | Grayscale average brightness below threshold | *"The photo is dark — please move to a brighter place."* |
| Blurry / child moved | Laplacian variance (sharpness) below threshold | *"The child moved — let's take it again."* |
| Face not visible / not facing camera | MediaPipe face detection; head-pose check | *"Please ask the child to look at the camera."* |
| Body cut off / wrong distance | Pose landmarks outside frame | *"Please step back so the full body is visible."* |
| Multiple children in frame | Face count > 1 | *"Only one child in the frame, please."* |

**Retake policy (locked in Round 5):**
1. All checks pass → straight to analysis.
2. Any check fails → voice + on-screen message, user retakes.
3. After **2 failed retakes** → **"Save anyway"** becomes available; the PDF carries a
   *"Low quality capture"* note so the health worker re-verifies manually.

---

## 9. Document Generation (PDF)

### 9.1 Content (locked in Round 4)
One page, two zones:
- **Top (for the villager/parent):** simple language, icons, large text — child info,
  BMI result, detected findings, corrective measures (nutrition, hydration, hygiene,
  when to visit a health center).
- **Bottom (for health worker/doctor):** technical block — BMI value, WHO
  BMI-for-age **percentile**, reference ranges, confidence notes, *"screening result,
  not a diagnosis"* disclaimer.

### 9.2 Generation
- Generated **on-device** by a client-side PDF library → works offline, no server needed.
- Also shareable (WhatsApp / Bluetooth) and printable (A5/A4).

### 9.3 Size & storage math
| Item | Size |
|---|---|
| One-page PDF with chart (no photo) | ~50–150 KB |
| Storage at 150 docs/day | ~15 MB/day |
| Appwrite 2GB free storage | ≈ 4–5 months at max usage (months to a year in practice) |
| PDF + embedded photo (rejected) | ~300 KB–2 MB — the storage hog we avoid |

### 9.4 Photo retention policy (locked in Round 4)
- **Raw captured photos are never stored** — neither on-device long-term nor in the cloud.
- Only the final PDF is kept. This protects the 2GB free storage *and* minimizes
  minors' identifiable data (privacy win).

---

## 10. Offline Sync & Data Flow

### 10.1 Sync model (locked in Round 4)
- **Local-first:** document PDF + record saved instantly to on-device SQLite.
- **Auto-sync:** when the phone has any connectivity, the queue uploads
  (document record + PDF) to Appwrite silently — no user action.
- **Daily batch reality:** in no-signal villages, documents accumulate all day and
  sync the next time internet appears.

### 10.2 Reliability requirements
- **Idempotent sync:** each document has a unique ID; retries never create duplicates.
- **Retry with backoff:** failed uploads retry automatically.
- **Crash safety (locked in Round 5):** the moment the user taps **"Yes, I agree"**
  on consent, a **draft record is auto-saved** locally (child name, age, sex, consent).
  If the phone crashes/dies, the draft is recovered on next open and can finish
  processing/syncing.

### 10.3 Data model overview
Full schema in **Backend Schema.md**. At a high level:
- `documents` — per-capture record (child info, metrics, symptom confidences, PDF
  reference, consent timestamp, sync status).
- `consent_log` — consent record per child/session.
- `users` — worker/staff accounts (Appwrite Auth).
- Raw photos: never stored (see Section 9.4).

---

## 11. Backend — Appwrite Cloud (Free Tier)

### 11.1 Free-tier limits vs our needs (research-verified)
| Limit | Free tier | Our fit |
|---|---|---|
| Database reads / writes | 500K reads / 250K writes per month | ✅ More than enough at 50–150 docs/day |
| **Storage** | **2 GB total** | ⚠️ The real constraint — see Section 9.3 and mitigations |
| Bandwidth | 5 GB/month | ✅ Fine for PDF-sized payloads |
| Users | 75,000 monthly users | ✅ Way beyond pilot needs |
| Projects | 2 | ✅ Fine |

### 11.2 Storage mitigations when 2GB approaches
1. **Retention window** — auto-delete cloud copies older than **6 months** (paper/PDF is
   the durable record anyway).
2. **Self-host Appwrite** — it's open-source; hosting on a free server removes the
   cap with zero code change.
3. **Compression** — PDFs can be compressed further if needed.

### 11.3 Migration readiness
- Schema and API designed to port cleanly to government cloud (NIC/MeghRaj) and to
  wire into Mid-Day Meal Scheme systems later (API-ready, not wired now — per PRD).

---

## 12. API Design Overview

Minimal, since the app is offline-first and self-sufficient:

| Endpoint (Appwrite Functions) | Purpose |
|---|---|
| `POST /sync/documents` | Batch upload of queued document records (idempotent by doc ID) |
| `POST /sync/pdf` | Upload a single PDF file (same UUID as the document) |
| `GET /documents` | List own documents, with name search (web app) |
| `GET /documents/:id` | Fetch a document + PDF download URL (web app) |
| `GET /documents/:id/pdf` | Download the PDF file (web app) |

Consent is recorded **inside the document record** (see Backend Schema §8.2), so there
is no separate consent endpoint.

Auth via Appwrite accounts (worker login). No real-time requirements.

---

## 13. Security & Privacy

| Requirement | Implementation |
|---|---|
| **Consent** | **One-tap consent screen** before first capture (locked Round 5): simple statement + big YES; consent timestamp recorded per document; works for low-literacy users |
| **Data minimization** | No raw photos stored (see Section 9.4); only PDF + metadata kept |
| **Anonymization** | Aggregate use (future) uses anonymized data only |
| **Minors' protection** | Consent + minimal PII + no long-term raw biometric images |
| **Transit** | HTTPS for all sync |
| **Access** | Worker accounts via Appwrite Auth; no public write access |

---

## 14. Performance Requirements

| Requirement | Target |
|---|---|
| Photo → document turnaround | **< 10 seconds** on low-end Android (2GB RAM, Android 8+) — locked Round 5 |
| Capture quality checks | < 1 second (fraction of the budget) |
| On-device analysis budget | 3–8 s (pose + BMI + symptom classifiers) |
| Session throughput | 50–150 children per site per day (one device) |
| App cold start | < 5 s on low-end device |
| Offline capture + PDF | Always works with zero connectivity |

---

## 15. Error Handling & Field Resilience

| Scenario | Behavior |
|---|---|
| Child moved / dark / blurry photo | Quality checks → voice-guided retake (×2) → "Save anyway" fallback with low-quality note (see Section 8) |
| No internet | Full offline operation; queue + auto-sync later (see Section 10) |
| Phone crash / battery death | Draft auto-saved before analysis; recovered on next open (see Section 10.2) |
| Analysis fails on device | Cloud fallback retry; else manual measurement mode (height/weight entry) per PRD hybrid fallback |
| Duplicate sync / retry | Idempotent unique IDs (see Section 10.2) |
| Low-end device slow | Budget-tuned models; reduce resolution to model input size; async UI with progress animation |

---

## 16. Testing & Validation Strategy

### 16.1 Unit / integration (dev machine)
- Quality-check unit tests (brightness/sharpness/face/pose thresholds on labeled test photos).
- BMI math tests (BMI formula, WHO percentile lookup, age/sex edge cases).
- PDF generation tests (content, layout, size budget).
- Sync idempotency tests (simulated retries, duplicate uploads).

### 16.2 Model validation
- Hold-out validation sets (never leaked from training).
- Per-symptom: sensitivity/specificity measured on field-quality photos.
- **BMI accuracy vs manual measurement** — the PRD's secondary KPI: compare estimated
  vs manually measured BMI on a pilot sample; set/confirm the acceptable clinical band
  from results (e.g., within ±1.0 BMI point for the majority).

### 16.3 Field pilot
- 2–3 sites (school/Anganwadi/camp), 50–150 children/day.
- Low-literacy usability test with real users (voice guidance effectiveness).
- Offline simulation: screening day without internet, verify daily sync.

---

## 17. Deployment & Hosting (Zero Cost)

| Component | Hosting |
|---|---|
| Android app | APK distribution (direct install; Play Store optional later) |
| Web app | Cloudflare Pages / GitHub Pages (free static) |
| Backend | Appwrite Cloud free tier |
| Training | Google Colab / Kaggle free GPUs |
| Model storage | In-app assets (no server needed) |

**Cost:** ₹0. All tiers free; no per-scan fees; all models open-source.

---

## 18. Technical Risks & Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| No public data for goitre / malnutrition | Medium-High | Seed datasets (Wikimedia ~200) + field collection + augmentation (see Section 7.3) |
| No local GPU for training | Medium | Free cloud GPUs + transfer learning (see Sections 7.1–7.2) |
| Model accuracy in field conditions | High | Capture-quality gating, hybrid manual fallback, pilot validation (see Sections 8 and 16) |
| Appwrite 2GB storage cap | Medium | PDF-only retention, retention window, self-hosting path (see Section 11.2) |
| Low-end device performance | Medium | Model size budget < 50 MB total, resolution tuning, 10-s budget (see Section 14) |
| Offline sync duplicates | Medium | Idempotent unique doc IDs (see Section 10.2) |
| Cloud dependency creep | Medium | On-device-first architecture; cloud never required (see Section 6.5) |

---

## 19. Open Questions

- Exact BMI accuracy band to commit to (to be set from pilot data; see Section 16.2).
- Which regional languages beyond Hindi + English ship first (UI/UX Brief).
- WHO growth-chart data source integration detail (WHO LMS tables are openly
  licensed; final library choice in Implementation Plan).
- Final PDF library and A5/A4 print layout (UI/UX Brief).
- Whether kiosk hardware mode is Phase 2 or later (Implementation Plan).

---

## 20. References

- Appwrite — open-source backend platform, free tier & limits (docs.appwrite.io)
- MediaPipe — pose estimation & face detection (developers.google.com/mediapipe)
- TensorFlow Lite Model Maker — transfer learning for mobile (tensorflow.org/lite)
- Google Colab free GPU tier & Kaggle notebooks free GPU
- Kaggle: *Jaundice Image Data*; DermNet dataset (23 categories)
- Hugging Face: *Anemia-Eyes* dataset
- WHO Child Growth Standards (BMI-for-age, openly licensed)
- Wikimedia Commons (open-license images for goitre seed set)

---

*End of TRD v0.1 — ready for team review and iteration.*
