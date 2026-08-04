# App Flow — Vision-Based Child Wellness Shield

| Field | Value |
|---|---|
| **Document** | Application Flow Document (App Flow) |
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

This document describes **every screen, step, and transition** a user moves through in
the Vision-Based Child Wellness Shield — from the first time the app is opened, to a
completed screening document, to syncing and viewing records later.

The product is deliberately a **single journey**: *capture a child → get a document*.
Every flow in this document exists only to make that journey work for two kinds of
people:

- a **villager** (possibly low-literacy) who wants a simple document for their child, and
- a **health worker** who runs bulk screening camps of 50–150 children per day.

The flows are built on the core principles already locked in the PRD and TRD:
offline-first (everything works with no internet), voice + visual guidance, ~10-second
results, one-tap consent, and **one account per phone** so no one else can ever see
another person's results.

---

## 3. Actors

| Actor | Who they are | What they do | Role in app |
|---|---|---|---|
| **Villager / parent** | A family member, possibly low literacy | Screens 1–3 children, shares/prints the document | `Family Member` |
| **Health worker** | PHC staff / camp organizer | Runs bulk sessions (50–150/day), uses Manual Mode, sees daily summary | `Health Worker` |
| **Web viewer** | Same person, on a computer | Views/searches/prints their own synced documents | Any account |

**Role selection:** at signup, the app asks **"Who are you?"** with two big buttons
(🧑‍⚕️ Health Worker / Center Staff | 👨‍👩‍👧 Family Member / Other). This one tap is
saved to the account and controls which features are visible. It can be changed later
in the Setup screen.

---

## 4. Flow Map (the whole product at a glance)

```
┌────────────────────────────── FIRST-RUN (one time only) ──────────────────────────────┐
│  Welcome ──▶ Login/Signup ──▶ Role (one tap) ──▶ Language ──▶ Permissions ──▶ Home    │
└──────────────────────────────────────────────┬────────────────────────────────────────┘
                                               ▼
┌────────────────────────────── CORE LOOP (repeated per child) ─────────────────────────┐
│                                                                                        │
│   Home ("New Screening")                                                                │
│        │                                                                            │
│        ▼                                                                            │
│   Child details (name, age, boy/girl) ~5 taps                                       │
│        │                                                                            │
│        ▼                                                                            │
│   Consent (one tap YES, timestamped)                                                │
│        │                                                                            │
│        ▼                                                                            │
│   Capture (voice-guided, single photo) ──quality fail──▶ voice retake loop ──▶ "Save│
│        │                                                       (×2)         anyway" │
│        ▼                                                                            │
│   Analyze (on-device, <10 s) ──▶ weight confirm (hybrid) ──▶ Document Ready         │
│        │                                                                            │
│        ▼                                                                            │
│   Spoken summary + Share / Next Child / My Documents                                │
│        │                                                                            │
│        ▼                                                                            │
│   Document saved locally (✓) ──▶ sync queue counter ──▶ auto-sync to cloud          │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

Everything else in this document is a detail of one of these boxes.

---

## 5. First-Run / Onboarding Flow

The very first time the app opens, the user completes a one-time setup. **All of it
needs internet once** (account creation); after this, the phone works fully offline.

| Step | Screen | What happens | Notes |
|---|---|---|---|
| 1 | **Welcome** | App name + simple picture (child + phone + document) + big **"Start"** button | Icon-driven, no text required to understand |
| 2 | **Login / Signup** | Existing user: phone + password. New user: name + phone + create password | One account **per phone**. Needs internet (only time it's mandatory) |
| 3 | **Role** | One-tap question: 🧑‍⚕️ **Health Worker / Center Staff** or 👨‍👩‍👧 **Family Member / Other** | Saved to the account. No typing. Changeable later in Setup |
| 4 | **Language** | Two big buttons: **हिन्दी** and **English** (+ regional languages when added) | Selected once here; changeable later only in Setup |
| 5 | **Permissions** | Camera access — big **"Allow"** button | No other permission is needed in v1 |
| 6 | **Setup complete** | Brief voice welcome: *"Your app is ready."* → auto-advances | Straight to Home / camera |

**State notes**
- First login offline → clear message: *"Please connect to the internet once to set up
  your account."* Retry later; nothing else is blocked forever.
- Wrong role/language picked → both are changeable anytime in **Setup** (see Section 12).

---

## 6. Core Screening Flow (happy path)

This is the journey for every child, every time. **Villager and worker walk the exact
same path** — the worker only has extras *outside* this loop (Section 11).

### 6.1 Step-by-step

| # | Screen | What the user does | What the app does |
|---|---|---|---|
| 1 | **Home** | Taps the big **"New Screening"** button | Opens child details form. (Home = camera-first; see Section 6.2) |
| 2 | **Child details** | Types child **name**, taps **age** (big year/month buttons), taps **boy/girl** — ~5 taps total | Saves details for this screening only |
| 3 | **Consent** | One-tap **"Yes, I agree"** on a simple statement | Records consent **timestamp** with the document (per PRD/TRD) |
| 4 | **Capture** | Follows voice guidance, taps the big shutter button | Takes a **single photo**, then instantly runs quality checks (Section 7) |
| 5 | **Analyzing** | Waits (progress animation + voice: *"Checking…"*) | On-device analysis: pose → height/weight → BMI-for-age, symptom classifiers. Target **< 10 s** |
| 6 | **Weight confirm** *(hybrid)* | Taps **"Correct"** on the estimated weight, or adjusts it | Recomputes BMI with the confirmed value (locked in TRD Round 2) |
| 7 | **Document Ready** | Hears spoken summary, then taps **Share / Next Child / My Documents** | Generates the one-page PDF, speaks the summary (Section 8) |

### 6.2 Home screen (after setup)

```
┌─────────────────────────────┐
│  📸  NEW SCREENING          │  ← one big button (the whole app)
├─────────────────────────────┤
│  📄  My Documents   [⬆ 3]   │  ← newest-first list + sync counter
├─────────────────────────────┤
│        [Setup]              │  ← small gear icon, bottom corner
└─────────────────────────────┘
```

- After setup, the home is **camera-first**: one big "New Screening" button.
- The **sync counter** (`⬆ 3`) shows how many documents are waiting to upload.
- "My Documents" and "Setup" are secondary — never required to complete a screening.

### 6.3 Multiple children in a row

After a document is ready, tapping **"Next Child"** clears the form and reopens the
camera — the previous child's details do not leak into the next screening.

---

## 7. Capture Quality & Retake Loop

The captured photo passes **5 instant on-device checks** (milliseconds, offline).
Each failure maps to a pre-recorded voice line + the same message on screen:

| Check | What the voice says |
|---|---|
| Photo too dark | *"The photo is dark — please move to a brighter place."* |
| Child moved (blurry) | *"The child moved — let's take it again."* |
| Face not visible | *"Please ask the child to look at the camera."* |
| Body cut off / too far | *"Please step back so the full body is visible."* |
| More than one child | *"Only one child in the frame, please."* |

### 7.1 Retake state machine

```
                capture
                   │
                   ▼
            quality checks ──all pass──▶ analysis (Section 6)
                   │
            one or more fail
                   │
                   ▼
     voice + message ("The photo is dark…")
                   │
          user retakes (2nd attempt)
                   │
            quality checks ──pass──▶ analysis
                   │
                  fail
                   │
                   ▼
   ┌──────────────────────────────┐
   │  [Retake]        [Save anyway]│   ← "Save anyway" now appears
   └──────────────────────────────┘
        │                    │
     retake (3rd+)     proceed with analysis anyway
        │                    │
        ▼                    ▼
   (loop repeats)   PDF marked "Low quality capture"
```

- **After 2 failed attempts**, **"Save anyway"** becomes available — there are **no
  dead ends** in the field.
- Choosing it proceeds with analysis; the PDF carries a **"Low quality capture"** note
  so the health worker/doctor re-verifies manually.
- At any point the user can tap **"Repeat instructions"** to replay the current
  guidance, and if nothing happens for ~15 seconds the voice guidance **auto-replays**.

---

## 8. Document Ready & Delivery

### 8.1 The result screen

```
┌───────────────────────────────────┐
│  ✅  DOCUMENT READY               │
│                                   │
│  (spoken:) "BMI is in the normal  │
│   range. The child looks healthy."│
│                                   │
│  [Share]      [Next Child]        │
│  [My Documents]                   │
└───────────────────────────────────┘
```

- The **spoken summary** states the result in simple words plus basic advice (locked
  Round 4) — never technical jargon.
- The full one-page PDF is generated on-device: **simple top** (for the villager),
  **technical bottom** (WHO percentile + reference ranges, for the worker/doctor),
  plus the *"screening result, not a diagnosis"* disclaimer (per TRD Section 9).

### 8.2 Share sheet

Tapping **Share** opens the phone's normal share sheet → **WhatsApp, email, any print
app**. No extra infrastructure, and it works offline (the PDF already exists locally).

### 8.3 After sharing

| Action | Result |
|---|---|
| **Share** | Share sheet opens; document remains in My Documents |
| **Next Child** | Form clears, camera reopens — next screening |
| **My Documents** | Opens the history list (Section 9) |

---

## 9. My Documents & Follow-up

### 9.1 The list

- **"My Documents"** shows the account's documents, **newest first**.
- Each row: child name, date, result summary, and **Share / Print** buttons.
- Opening a document re-opens the full PDF for viewing, sharing, or printing.

### 9.2 Linking a child's documents (follow-ups)

Because follow-up visits matter, documents are **auto-linked by child name**:

```
New screening entered for name "Aarav" (age 6)
        │
        ▼
  existing document(s) with the same name?
        │
     no ──▶ document is standalone
        │
     yes
        │
        ▼
  "Same child as before?"   [Yes] [No]
        │                     │      │
        ▼                     │      ▼
  linked to child's         │      standalone
  history (viewable         │      (e.g., different
  from My Documents)        │      child with same name)
```

- **Why the confirm tap:** many children in one village share a name; the one-tap
  "Same child as before?" prevents wrongly merging two different children.
- **Strict account scoping:** the "Same child as before?" question is directed
  **solely to the account holder**, and it searches **only that account's own
  documents** (created on this phone/login). It never consults, matches against, or
  shows data from any other account, village, or location — a child from elsewhere
  can never appear in your account.
- Linking is only for convenience of viewing history — every capture still produces
  its own standalone document (the core product promise).

---

## 10. Offline & Sync Flow

### 10.1 Saving a document

```
Document Ready
     │
     ▼
draft saved locally (before analysis even starts — crash-safe, Section 10.3)
     │
     ▼
PDF + record saved to on-device store  ──▶  "✓ Saved" flash on screen
     │
     ▼
sync counter increments (⬆ N)          ──▶  counter shown on Home
```

### 10.2 Syncing

- When the phone has **any** internet, queued documents **auto-upload** silently —
  no user action, no button.
- Each document has a **unique ID** → retries never create duplicates (idempotent).
- In a no-signal village, documents accumulate all day and sync the moment signal
  returns (the daily-batch reality).
- The **sync counter** (`⬆ N`) is the only visible sync UI: it ticks down as uploads
  complete, and the user never has to care about it.

### 10.3 Crash safety

- The moment the user taps **"Yes, I agree"** on the consent screen, a **draft record
  is auto-saved** (child name, age, sex, consent) — before capture even starts.
- If the phone crashes or the battery dies mid-flow, the next open shows:
  **"Resume unfinished document?"** → Yes = continue processing/syncing where it left
  off. No = discard the draft.
- Raw photos are **never stored** — only the final PDF (privacy + storage policy from
  TRD Section 9.4).

---

## 11. Worker Flows (extras visible only to Health Workers)

The worker's daily loop is identical to the villager's (Section 6), plus three extras:

### 11.1 Bulk / camp sessions (50–150 children/day)
- Same screens, driven by the **"Next Child"** button — one tap per child.
- Worker sees a small running count during the session (e.g., *"34 done"*).

### 11.2 Manual Mode (when the camera/AI can't work)
- If a photo simply cannot be captured or analyzed, the worker can open **Manual
  Mode** and **type the findings** (height, weight, observed symptoms) → the same
  document is still generated.
- **Villagers never see this button** — role from signup controls visibility.

### 11.3 Daily summary (bulk sessions only)
- At the end of a bulk session the worker can view a one-screen summary:
  **"Today: 34 screened, 5 at-risk."**
- A normal villager **never sees any summary** — they only ever see their documents
  (locked Round 4).

---

## 12. Setup Screen (change role / language later)

A small gear icon on Home opens **Setup** — the same screen as onboarding steps 3–4:

- **Language:** two big buttons (हिन्दी / English) — instant switch, all voice +
  text change immediately.
- **Role:** re-select worker/family — unlocks/locks Manual Mode and the daily summary.
- Language and role are the *only* post-setup settings in v1.

---

## 13. Web Version Flow (computer at the center)

```
Computer browser ──▶ web app (same account as the phone) ──▶ login
        │
        ▼
  My Documents (newest first) ──▶ search by child name ──▶ open PDF
        │
        ▼
  View / Print / Download (same PDF as on the phone)
```

**Visibility rule (locked Round 4):** the web login sees **only its own account's
documents** — a villager's web login shows only their family's documents; a center's
login shows only that center's documents. **No cross-account visibility exists in
v1** — no one, including centers, can see anyone else's records. **This same rule
governs every feature in the app, including the "Same child as before?" check** —
information concerning a child from a different village or location never appears in
your account.

---

## 14. Edge Cases & State Transitions

| Scenario | What happens |
|---|---|
| First login with no internet | Clear message + retry; everything else still works once setup is done |
| Photo too dark / blurry / face hidden / body cut off / 2 children | Voice-guided retake; "Save anyway" after 2 fails (Section 7) |
| Camera or AI completely fails | Worker: Manual Mode. Villager: retry guidance; no dead ends |
| Same child name appears again | "Same child as before?" one-tap confirm — searched **only within this account's own documents** (Section 9.2) |
| Phone offline during screening | Everything works; sync counter grows; auto-sync later (Section 10) |
| Phone crashes / battery dies mid-analysis | Auto-saved draft; "Resume unfinished document?" on next open |
| Duplicate upload / retry | Idempotent unique doc IDs — no duplicates (TRD Section 10.2) |
| Wrong language / role selected | Changeable anytime in Setup (Section 12) |
| Storage getting low | PDF-only retention keeps files tiny; low-storage warning if needed |
| A stranger picks up the phone | Account stays logged in per phone, but documents are behind the account; login required on fresh installs |

---

## 15. Screen Inventory (v1)

| Screen | Who sees it | Purpose |
|---|---|---|
| Welcome | First run only | Intro + Start |
| Login / Signup | First run (+ fresh installs) | Account creation (one per phone) |
| Role picker | First run + Setup | Worker vs Family (one tap) |
| Language picker | First run + Setup | हिन्दी / English |
| Permissions | First run | Camera access |
| Home | Always | New Screening (primary) + My Documents + Setup |
| Child details | Per screening | Name, age, boy/girl (~5 taps) |
| Consent | Per screening | One-tap YES, timestamped |
| Capture | Per screening | Voice-guided single photo + quality checks |
| Retake message | Per screening | Quality-check failure → voice + illustration, Retake / "Save anyway" after 2 fails |
| Analyzing | Per screening | Progress animation (<10 s) |
| Weight confirm | Per screening | Hybrid AI estimate → confirm/correct |
| Document Ready | Per screening | Spoken summary + Share / Next Child / My Documents |
| Share sheet | On demand | System share (WhatsApp / email / print) |
| My Documents | On demand | Newest-first list, Share/Print, child history |
| "Same child?" prompt | On demand | Confirm name-linking to a previous document (account-scoped) |
| Resume prompt | After crash | Recover unfinished document |
| Manual Mode | Workers only | Type findings when capture fails |
| Daily summary | Workers only | "Today: 34 screened, 5 at-risk" |
| Setup | On demand | Change language / role |
| Web: login + documents | Web only | View/search/print own documents |

---

## 16. Open Questions (for other docs)

- Exact copy for the consent statement and the welcome voice line (UI/UX Brief).
- How "child history" is visually presented after name-linking — timeline vs. list
  (UI/UX Brief).
- Whether the sync counter should also appear on the web version (minor).
- Manual Mode's exact input fields and validation rules (Backend Schema / UI-UX Brief).

---

*End of App Flow v0.1 — ready for team review and iteration.*
