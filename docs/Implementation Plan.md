# Implementation Plan — Vision-Based Child Wellness Shield

| Field | Value |
|---|---|
| **Document** | Implementation Plan |
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

This document defines **how the Vision-Based Child Wellness Shield gets built** — the repository structure, the phase-by-phase build order, the environment and tooling, the AI training workflow (on free cloud GPUs, no local GPU required), testing strategy, and the field pilot rollout.

The plan is built on decisions locked across all five interview rounds:

| Decision | Choice |
|---|---|
| Repo layout | Single monorepo — app + web + training scripts + docs |
| Build order | Core app loop first, AI models as plug-ins |
| Git workflow | Simple trunk — main branch, tags for releases |
| Dev machine | Local Flutter + Android Studio; free cloud GPUs for training |
| Milestones | 6 phases: Setup → Core loop → AI → Offline/PDF → Cloud → Polish |
| AI timing | Start training in parallel during Phase 2 |
| Mock phase | Real pipeline, fake results |
| First model | Jaundice classifier |
| Testing | Unit tests for logic + manual field tests |
| CI/CD | Free GitHub Actions: lint + tests + APK build |
| Appwrite setup | Cloud project + local emulator for offline dev |
| Device testing | One low-end Android + one modern phone |
| Timeline | **Milestone-driven** (no fixed calendar deadlines) |
| Done criteria | Core loop works offline end-to-end + models pass accuracy bar |
| Pilot plan | 2–3 sites, ~2 weeks, supervised + monitored |
| Rollout | Pilot data → refine models → expand sites |

**The north star remains:** a villager or health worker captures a single photo of a child on a low-end Android phone and receives a printable PDF document within ~10 seconds — fully offline, at zero cost.

---

## 3. Repository Structure (Single Monorepo)

One git repository containing everything. Proposed layout:

```
vision-based-child-wellness-shield/
├── docs/                      # All documentation (PRD, TRD, App Flow, UI/UX, Schema, this plan)
├── app/                       # Flutter app — Android + Web (one codebase)
│   ├── lib/
│   │   ├── main.dart
│   │   ├── models/            # Document model (mirrors Backend Schema)
│   │   ├── screens/           # All 21 screens from App Flow
│   │   ├── services/          # Camera, quality checks, analysis, PDF, sync, voice
│   │   ├── ai/                # Model loading + inference wrappers (TFLite)
│   │   └── assets/            # Icons, illustrations, voice clips, .tflite models
│   ├── test/                  # Unit tests (BMI math, quality checks, sync)
│   └── pubspec.yaml
├── training/                  # Python training scripts + dataset prep
│   ├── datasets/              # (seeded datasets — see TRD Section 7.3)
│   ├── train_jaundice.py      # First model (jaundice classifier)
│   ├── train_pallor.py
│   ├── train_skin.py
│   ├── train_goitre.py
│   ├── train_malnutrition.py
│   ├── train_bmi.py           # Height/weight estimator
│   └── requirements.txt
├── backend/                   # Appwrite config, schema, functions
│   ├── appwrite.json          # Appwrite CLI project config
│   ├── schema.md              # Collection definitions (mirrors Backend Schema)
│   └── functions/             # Auto-age-out function, etc.
└── README.md
```

**Why monorepo:** the docs describe the code, the training scripts feed the app's models, and the backend config mirrors the schema — keeping them in one repo means one versioned source of truth. Tagging a release captures the whole system at that point.

---

## 4. Git Workflow (Simple Trunk)

| Rule | Detail |
|---|---|
| Branch | Work directly on `main` |
| Commits | Meaningful messages (`feat: add consent screen`, `fix: blur detection threshold`) |
| Releases | Tag milestones: `v0.1-core-loop`, `v0.2-ai`, `v1.0-pilot` |
| CI | GitHub Actions runs on every push to `main` (see Section 7) |
| Rollback | `git revert` — simple and effective at this scale |

No feature branches, no PR ceremony. For a solo/small-team project this keeps momentum while CI still catches breakage.

---

## 5. Development Environment

### 5.1 Local machine (no GPU — by design)

| Tool | Purpose | Cost |
|---|---|---|
| Flutter SDK + Android Studio | Build Android app + Web version | Free |
| Android emulator | Quick UI iterations (not for camera/perf testing) | Free |
| VS Code or Android Studio IDE | Code editing | Free |
| Git + GitHub | Version control + CI | Free |
| Appwrite local emulator (Docker) | Offline backend dev — sync testing without consuming cloud quota | Free |
| Python (for training scripts only) | Prepare/validate datasets locally; training itself runs in cloud | Free |

**The training machine is NOT your local machine.** Your machine runs the app toolchain; training happens on free cloud GPUs (Google Colab T4 / Kaggle 30 GPU-hours/week) — see Section 6.

### 5.2 Appwrite setup

- **Cloud project** (free tier): the real sync target — database, auth, storage.
- **Local emulator** (Docker): identical Appwrite running on your machine for development — test sync flows endlessly without touching free-tier quota.
- Configure once, both from the same `backend/appwrite.json`.

### 5.3 Test devices

| Device | Role |
|---|---|
| **One low-end Android** (2 GB RAM, Android 8+) | The target floor — prove the app runs here |
| **One modern phone** | Baseline comparison + faster iteration |

---

## 6. The Six Phases (Milestone-Driven)

**Timeline philosophy (locked Round 4):** milestone-driven, no fixed calendar deadlines. Each phase below lists its **exit criteria** — the phase is done when the criteria are met, not when a date arrives. Rough effort guides (in parentheses) are estimates to help sequence, not commitments.

### Phase 1 — Setup (foundation)

| Task | Detail |
|---|---|
| Repo scaffold | Create monorepo layout (Section 3), git init, README |
| Flutter init | `flutter create` app skeleton, run on emulator + both phones |
| Appwrite setup | Create cloud project, start local emulator, define collections (per Backend Schema) |
| GitHub Actions | Basic CI: `flutter analyze` + `flutter test` + APK build on push |
| Design tokens | Set up greens/cream palette, typography, illustration placeholders (per UI/UX Brief) |

**Exit criteria:** app builds and runs on the low-end phone; CI green; Appwrite collections created; local emulator syncs a test document.

*Effort guide: ~1–2 weeks.*

### Phase 2 — Core Loop (mock AI)

Build the real pipeline with **fake AI results** (locked Round 2):

| Task | Detail |
|---|---|
| Screens | Welcome → Login → Role → Language → Permissions → Home (App Flow Section 5) |
| Core loop | Child details (~5 taps) → Consent → Capture → Quality checks → Analyzing → Weight confirm → Document Ready (App Flow Section 6) |
| Quality checks | Brightness, sharpness, face, pose, child count — with voice-guided retake + "Save anyway" after 2 fails (TRD Section 8) |
| Mock AI | Real code paths, pre-programmed sample results (BMI, symptoms) — swap layer only |
| PDF (mock) | Generate the one-page PDF with sample data — simple top, technical bottom (UI/UX Brief Section 7) |
| Voice | Phrase bank (~40 clips) generated via free TTS, bundled, stitched summaries (UI/UX Brief Section 5) |
| Local storage | SQLite table mirroring the schema; draft → pending → synced lifecycle (Backend Schema Section 5) |

**Parallel track (starts here):** prepare training scripts + seed datasets; launch the first cloud training run (jaundice — Section 6.1).

**Exit criteria:** a first-time user completes capture → PDF → share **fully offline** on the low-end phone, with mock results, under 10 seconds.

*Effort guide: ~2–3 weeks (parallel training does not block it).*

### Phase 3 — AI Integration (real models)

| Task | Detail |
|---|---|
| Integrate jaundice model | Drop the trained `.tflite` into app assets; swap the mock layer |
| Integrate remaining models | Pallor, skin, goitre, malnutrition (as they finish training) |
| BMI pipeline | Pose landmarks (MediaPipe) → height/weight estimator → BMI → WHO percentile (TRD Section 6.2) |
| Cloud fallback | On-device primary; fallback path for slow/missing models (TRD Section 6.5) |
| Model versioning | `*_model_ver` fields populated (Backend Schema) |

**Exit criteria:** all 5 symptom models + BMI pipeline running on-device with measured accuracy meeting the bar (Section 8); app still under the <10 s budget.

*Effort guide: ~2–3 weeks (overlaps Phase 2 end).*

### Phase 4 — Offline, PDF & Sync (production-ready core)

| Task | Detail |
|---|---|
| PDF finalization | Real data, color band, corrective measures, technical block, "not a diagnosis" footer (UI/UX Brief Section 7) |
| Sync engine | Auto-sync queue (status filter), idempotent UUIDs, retry with backoff (Backend Schema Section 6) |
| Crash safety | Draft auto-save + "Resume unfinished document?" (App Flow Section 10.3) |
| My Documents | Newest-first list, "Same child as before?" name-linking (account-scoped) |

**Exit criteria:** screening works fully offline all day; docs sync automatically when signal returns; crash mid-analysis recovers the draft; no duplicate docs after retries.

*Effort guide: ~2 weeks.*

### Phase 5 — Cloud & Web App

| Task | Detail |
|---|---|
| Appwrite sync | Wire the sync engine to the cloud project (records + PDFs) |
| Web app | Same Flutter codebase, web build: login → My Documents → search → view/download/print (App Flow Section 13) |
| Auto-age-out | Scheduled Appwrite Function: delete cloud copies > 6 months (Backend Schema Section 8.4) |
| Manual Mode | Worker-only (role from signup): type height/weight/symptoms → same document (App Flow Section 11.2) |
| Daily summary | Worker-only: "Today: 34 screened, 5 at-risk" (App Flow Section 11.3) |

**Exit criteria:** docs sync to cloud and appear in the web app under the same account; age-out function runs correctly; worker features visible only to workers.

*Effort guide: ~2 weeks.*

### Phase 6 — Polish, Testing & Pilot-Ready

| Task | Detail |
|---|---|
| Field hardening | Two-phone testing (low-end + modern), lighting/movement edge cases |
| Usability | Low-literacy walkthrough: can a first-time user complete the loop unaided? |
| Unit tests complete | BMI math, percentile lookup, quality checks, sync idempotency (all green in CI) |
| Accuracy validation | Compare estimated vs manually measured BMI + symptom sensitivity/specificity on field-quality photos (TRD Section 16) |
| Pilot kit | Worker guide PDF, consent forms, sample documents, install APKs |

**Exit criteria — the v1 definition of done (locked Round 4):**
1. A villager with no training completes capture → analyze → PDF → share, **fully offline**, **< 10 s**, on the low-end phone.
2. All 5 symptom models integrated with accuracy passing the bar.
3. Documents sync correctly when online; no data loss on crash.
4. Web app shows the account's documents.

*Effort guide: ~2 weeks.*

**Total:** ~11–14 weeks of effort, milestone-gated (not calendar-gated).

---

## 6.1 The Parallel Training Track

Training runs **in parallel with app development** from Phase 2 onward (locked Round 2). The workflow is the no-GPU cloud loop from the TRD:

```
Local machine                Free cloud GPU (Colab T4 / Kaggle)         Result
────────────                 ────────────────────────────────           ──────
dataset folders    ──upload──▶  training notebook/script      ──download──▶  .tflite
+ one .py script               (transfer learning,            (a few MB)     → app assets
(via Drive/GitHub)             minutes–1 hour)
```

### Training order (first model first — locked Round 2)

| Order | Model | Dataset status | Why this order |
|---|---|---|---|
| 1 | **Jaundice** | ✅ Kaggle ~600+ validated images | Best data; proves the whole train→deploy→phone pipeline end-to-end |
| 2 | Pallor | ⚠️ Small (Hugging Face ~218 + Kaggle) | Augment + supplement |
| 3 | Skin conditions | ✅ DermNet ~19.5K (23 categories) | Big data → easy accuracy |
| 4 | Goitre | ❌ Seeded (Wikimedia ~200) | Seed + field collection |
| 5 | Malnutrition | ❌ Custom field collection | Field data + augmentation |
| 6 | BMI estimator | Synthetic + field | Depends on pose landmarks (MediaPipe) working first |

**Iteration rule:** each model gets a `v1.x` tag. Pilot field photos retrain them into `v2.x` (the pilot is the data engine — Section 9).

---

## 7. Testing & CI/CD

### 7.1 Automated unit tests (run in CI)

| Test area | What it covers |
|---|---|
| BMI math | `weight(kg) / height(m)²`, edge cases (zero/negative, rounding) |
| WHO percentile lookup | Age/sex edge cases, correct percentile + category mapping |
| Quality checks | Brightness/sharpness/face/pose thresholds on labeled test photos |
| Sync idempotency | Simulated retries never duplicate documents |
| Draft lifecycle | draft → pending → synced transitions; crash recovery logic |
| PDF generation | Content, layout, size budget |

### 7.2 Manual field tests (not automatable cheaply)

- Camera behavior in sunlight / low light / movement
- Voice guidance clarity and timing (low-literacy usability)
- Real-device performance on the 2 GB phone (cold start, analysis time)
- Offline day simulation: screen all day with no signal, sync later
- Share sheet: WhatsApp, print app, email

### 7.3 GitHub Actions CI (free)

| Job | Runs on push |
|---|---|
| `flutter analyze` | Static analysis — catches bugs before tests |
| `flutter test` | All unit tests |
| `flutter build apk --release` | Builds the installable APK |
| `flutter build web` | Builds the web version |

Free tier: 2,000 minutes/month for private repos, unlimited for public — far beyond this project's needs. APK artifacts attach to release tags for easy sideloading at pilot sites.

---

## 8. Acceptance Criteria (v1 Definition of Done)

Beyond the Phase 6 exit criteria, two formal gates:

### Gate 1: Functional readiness (app)

| Criterion | Target |
|---|---|
| Capture → PDF → share, offline | Works with zero connectivity |
| Turnaround | < 10 s on 2 GB RAM / Android 8+ |
| Quality-check retake loop | Correct voice guidance for all 5 failure modes |
| Crash recovery | Draft survives a mid-analysis crash |
| Sync | No duplicates after retries; auto-sync on connectivity |
| Account privacy | No cross-account visibility (tested) |

### Gate 2: Model readiness (AI)

| Criterion | Target |
|---|---|
| Symptom detection | ≥ 80% sensitivity at acceptable specificity on field-quality photos (TRD Section 6.6) |
| BMI vs manual measurement | Within acceptable clinical band (final target set from pilot data — TRD Section 16.2) |
| False "at-risk" flags | Minimized — no over-alarming parents |

**Both gates must pass before the pilot starts.** If Gate 2 is short, options: (a) more training data + augmentation, (b) tighter capture-quality gating, (c) ship the pilot with fewer symptoms and add the rest when ready — decided at the gate review.

---

## 9. Field Pilot (2–3 Sites, ~2 Weeks)

### 9.1 Pre-pilot checklist

- [ ] APK installed on site phones; models validated (Gate 2)
- [ ] Worker guide printed (with screenshots of every screen)
- [ ] Consent forms printed (and consent flow verified in-app)
- [ ] Offline test passed: full screening day with no signal
- [ ] Sample documents printed to confirm printer compatibility (A5/A4)

### 9.2 Operating rhythm (supervised + monitored — locked Round 4)

| Stage | What happens |
|---|---|
| **Worker training** | 30 min per site: role tap, language, capture, retake, share. Worker does 5 practice screenings. |
| **Day 1 — supervised** | You're physically at Site 1. Watch real usage, note every stumble, fix critical bugs same evening. |
| **Daily rhythm** | Workers screen daily on their own. You monitor remotely: documents appearing in Appwrite, sync counts, no stuck queues. Fix bugs remotely; send updated APKs over WhatsApp. |
| **Data collection** | Every ~50 children, manually measure a sample (tape + scale) and compare with app estimates — the BMI accuracy validation. Collect field photos (with consent) for model retraining. |
| **Week 1 review** | Consolidate issues: patch app, adjust thresholds. |
| **Week 2** | Run Sites 2–3 with Site 1 lessons baked in. |

### 9.3 Pilot success signals

- Documents produced and synced daily at all sites
- Workers use it without your help by Day 3
- BMI estimates within the clinical band on the manual-measurement sample
- Goitre + malnutrition field photos collected (the missing datasets!)
- At least one usability bug found that no lab test caught (if none, you didn't test hard enough)

---

## 10. Post-Pilot Rollout (Pilot Data → Refine → Expand)

| Step | Detail |
|---|---|
| 1. Retrain | Feed pilot field photos + measurements into training → models v2.0 (goitre/malnutrition get their real data) |
| 2. Fix UX | Address every usability issue logged during the pilot |
| 3. Re-validate | Re-run Gate 2 accuracy checks with the improved models |
| 4. Expand | Roll out to more sites gradually — one new site at a time, monitored like the pilot |
| 5. (Later) | Government/welfare integration (Mid-Day Meal Scheme), kiosk hardware — per PRD roadmap, not v1 |

---

## 11. Risk Watchlist (from all docs)

| Risk | Where handled |
|---|---|
| Models inaccurate in field conditions | TRD Section 18; Gate 2; capture-quality gating; pilot validation |
| No local GPU | Solved — cloud training (TRD Section 7) |
| Goitre/malnutrition lack data | Seeded datasets + pilot field collection (TRD Section 7.3) |
| Appwrite 2 GB cap | 6-month auto-age-out (Backend Schema Section 8.4) |
| Low-end device performance | < 50 MB model budget, resolution tuning, 10 s budget (TRD Section 14) |
| Offline sync duplicates | Idempotent UUIDs (Backend Schema Section 6.3) |
| Low-literacy adoption | Voice + illustration-driven UX, usability gate in pilot (UI/UX Brief) |

---

## 12. Open Questions

- Exact wording of the consent statement and welcome voice line (copy review).
- Whether the pilot uses the health worker's own phones or provided devices.
- Whether regional languages beyond Hindi/English ship before or after the pilot.
- Whether "ship with fewer symptoms if Gate 2 is short" is acceptable for the pilot.

---

*End of Implementation Plan v0.1 — ready for team review and iteration.*