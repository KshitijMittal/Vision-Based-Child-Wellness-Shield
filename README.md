# Vision-Based Child Wellness Shield

Offline-first child wellness screening for low-resource settings. A health worker
or parent captures a single photo of a child on a low-end Android phone and
receives a printable PDF document with an estimated BMI, WHO BMI-for-age
percentile, and symptom flags — fully offline, in under ten seconds, at zero cost.

The north star (Implementation Plan §2): *a villager or health worker captures a
single photo of a child on a low-end Android phone and receives a printable PDF
document within ~10 seconds — fully offline, at zero cost.*

## Repository layout

```
├── docs/          # PRD, TRD, App Flow, UI/UX Brief, Backend Schema, Implementation Plan
├── app/           # Flutter app — Android + Web (one codebase)
│   ├── lib/theme/ # Design tokens: greens/cream palette, typography
│   ├── lib/       # models/, screens/, services/, ai/ (populated from Phase 2)
│   └── test/      # Unit tests (BMI math, quality checks, sync)
├── training/      # Python training scripts + dataset prep (Phase 2 parallel track)
├── backend/       # Appwrite config, schema, provisioning scripts
│   ├── schema.md  # Deployable schema (mirrors docs/Backend Schema.md)
│   ├── scripts/   # setup_appwrite.py — idempotent cloud provisioning
│   └── functions/ # Scheduled functions (auto-age-out, Phase 5)
└── .github/       # GitHub Actions CI
```

## Prerequisites

- Flutter SDK (stable) + Android Studio (Android SDK)
- Python 3.10+ (for backend provisioning scripts)
- Docker Desktop (Appwrite local emulator — optional for Phase 1)
- Appwrite Cloud project (free tier)

## Quickstart

### Backend (Appwrite cloud schema)

```bash
python -m venv .venv
.venv/Scripts/python.exe -m pip install -r backend/requirements.txt
cp backend/.env.example backend/.env   # fill in your Appwrite credentials
.venv/Scripts/python.exe backend/scripts/setup_appwrite.py
```

The script is idempotent: it creates the `main` database, the
`screening_documents` table with all 35 cloud fields, the 3 indexes, and
verifies the result — safe to re-run.

### App (Flutter)

```bash
cd app
flutter pub get
flutter run        # or: flutter run -d chrome
```

## CI

GitHub Actions runs on every push to `main`: `flutter analyze`, `flutter test`,
APK release build, and web build. Artifacts (APK) attach to workflow runs.

## Milestones

Phase 1 (Setup) is in progress. See `docs/Implementation Plan.md` for the full
six-phase, milestone-driven plan.
