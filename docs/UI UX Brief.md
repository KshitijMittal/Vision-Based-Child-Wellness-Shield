# UI/UX Brief — Vision-Based Child Wellness Shield

| Field | Value |
|---|---|
| **Document** | UI/UX Brief |
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

This brief defines **how the product looks, sounds, and feels**. It translates the
flows from **App Flow.md** into concrete design decisions: colors, typography,
illustrations, voice, screen layouts, and the design of the PDF document itself.

The design north star is simple:

> *A person who cannot read, has never used the app, and is standing in bright
> sunlight should be able to open it and produce a document for their child without
> anyone's help — guided by pictures and a warm voice.*

Everything in this brief serves that goal, on the lowest-end Android phone (2 GB RAM,
Android 8+) with the app's offline-first behavior.

---

## 3. Design Principles

| # | Principle | What it means in practice |
|---|---|---|
| 1 | **Pictures over words** | Guidance is stick-figure illustrations + voice first; text is a supporting label, never the primary channel |
| 2 | **One giant action per screen** | Every screen has exactly one big, unmissable primary button; nothing competes with it |
| 3 | **Never blame the user** | Retakes and errors are gentle and encouraging — a moving child is normal, not a mistake |
| 4 | **Readable in sunlight** | Light theme, very high contrast, large type — designed for outdoor field use |
| 5 | **Reassurance over alarm** | Results use calm colors and simple words; the document always says "screening, not a diagnosis" |
| 6 | **Offline is invisible** | Sync, saving, and queuing happen silently; the user only ever sees a small counter |
| 7 | **Warmth and trust** | Greens + cream, soft sounds, a calm female voice — the app feels like a helpful health worker, not a machine |
| 8 | **One language at a time** | The entire app (text, voice, PDF) speaks the language chosen at setup; switching changes everything together |

---

## 4. Visual Identity

### 4.1 Color palette (locked Round 1: warm + trustworthy — greens & cream)

| Token | Hex | Usage |
|---|---|---|
| **Leaf Green** (primary) | `#1B7A43` | Primary buttons, headers, active states |
| **Soft Green** (accent) | `#4CAF50` | Success, "Yes" buttons, check marks |
| **Cream** (background) | `#FAF6EC` | Screen backgrounds, document paper feel |
| **White** | `#FFFFFF` | Cards, button text on green |
| **Ink** (text) | `#1F2A24` | Near-black green for body text (high contrast on cream) |
| **Stone Grey** (secondary text) | `#5C6B63` | Captions, secondary labels |

**Semantic result colors** (used on the PDF and result screens):

| Level | Color | Meaning |
|---|---|---|
| **GREEN** — Normal | `#2E7D32` | BMI-for-age in normal range, nothing flagged |
| **AMBER** — Watch | `#C77800` | Near-normal or mild finding — monitor, follow advice |
| **RED** — See a health center | `#C62828` | Flagged finding — the document says to visit a health center |

Contrast: every text-on-background pair meets WCAG AA (≥ 4.5:1). Primary button text
(white on Leaf Green) is ~5.8:1.

### 4.2 Typography (locked Round 1: very large, simple, high-contrast)

- **Family:** Noto Sans (Latin + **Devanagari**) — free, open-source, and renders
  Hindi perfectly alongside English.
- **Body:** 22–24 sp on phones (≈ 50% larger than a typical app) — readable in
  sunlight and by older eyes.
- **Primary buttons:** 28–32 sp, bold.
- **Titles:** 32–36 sp, bold.
- **Rules:** no italic, no thin weights, no decorative fonts; sentence case; strong
  letter spacing only for numbers.
- **Numbers** (age, BMI, percentiles) use tabular figures and large size — never
  cramped.

### 4.3 Icons & illustrations (locked Round 1: simple illustrations / stick figures)

- **Style:** consistent, friendly **line-drawn stick figures** with soft rounded
  strokes in Leaf Green / Ink — readable at a glance, timeless, cheap to produce.
- **Never real photos of children in the UI** — protects privacy and keeps storage
  tiny (locked in App Flow discussions).
- Every icon is paired with a label in the active language, but must be
  **understandable with the label hidden**.
- The full illustration inventory is in Section 12.

### 4.4 Touch targets & spacing

| Element | Minimum size |
|---|---|
| Any tappable target | ≥ 48 × 48 dp |
| Primary action button | ≥ 96 dp tall, full width |
| Camera shutter | ≥ 120 dp circle |
| Age/sex buttons | ≥ 80 dp tall |
| Spacing between targets | ≥ 16 dp (prevents mis-taps) |

### 4.5 Language (locked Round 1: one language at a time)

- One active language; **all text, voice, and the PDF switch together**.
- The language picker (हिन्दी / English) appears only in **Setup** (per App Flow
  Section 12) — never cluttering the main flow.
- Right-to-left scripts, if ever added, get full mirroring (not v1).

---

## 5. Voice & Audio Design

### 5.1 Voice character (locked Round 3)

- **Warm, calm female voice** — familiar, reassuring, consistent with how rural
  health guidance is delivered.
- Speaking pace: slow (≈ 15% slower than normal conversation), with clear pauses
  between steps.

### 5.2 How the voice is produced (locked Round 3: TTS-generated clips, bundled)

- The developer **types ~40 fixed phrases per language**.
- **Free text-to-speech generates natural clips once** (e.g., Edge TTS / Google Cloud
  TTS free tier) in the same warm female voice for every language.
- Clips are **bundled inside the app** (≈ 2–4 MB per language) — **never in the
  database**, no per-user storage, no cloud dependency at runtime.
- The phone only carries the 1–2 languages it needs; extra languages can be
  downloaded as optional packs (from free static hosting) if ever required.
- No on-device TTS engine in v1 — no robots, no runtime cost, works fully offline.

### 5.3 Dynamic spoken summary (audio stitching)

The result summary is built by **joining pre-recorded segments**:

> *"BMI is in the"* + *"normal range"* + *". The child looks healthy."*

Results only fall into a handful of categories (GREEN / AMBER / RED, plus symptom
names), so every possible sentence is assembled from the phrase bank by the **same
voice with matching tone** — it sounds like one natural sentence.

### 5.4 Sound design

| Moment | Sound |
|---|---|
| Capture taken | Soft camera "click" |
| Analysis complete | **Gentle happy "ding"** + green check (locked Round 3) |
| Document ready | Spoken summary (Section 5.3) |
| Retake needed | Voice line only — no alarming sounds |
| Low quality note | Neutral voice line — no judgment |

---

## 6. Screen-by-Screen Design Specs

All phone screens below map to the Screen Inventory in **App Flow.md Section 15**.
Common rules: cream background, one primary action per screen, voice bubble top,
illustrations matching the active language's culture.

| Screen | Key layout decisions |
|---|---|
| **Welcome** | Full-screen illustration (child + phone + document), app name, one giant **"Start"** button |
| **Login / Signup** | Big phone field + large numeric keyboard; giant **"Continue"**; "New here? Create account" as a full-width button, not a link |
| **Role picker** | Two giant illustrated cards: 🧑‍⚕️ Health Worker / Center Staff · 👨‍👩‍👧 Family Member / Other — one tap, no typing |
| **Language picker** | Two huge buttons: **हिन्दी** and **English**; each button shows its own script so it's self-evident |
| **Permissions** | One illustration (camera), one giant **"Allow"** — voice explains why |
| **Home** | Giant full-width **"New Screening"** button with camera icon — **half the screen height** (locked Round 2); below it: My Documents row with sync counter (⬆ N); small Setup gear, bottom corner |
| **Child details** | Name field (keyboard appears only here) + **giant age buttons** (year/month chips) + **two giant boy/girl buttons**; ~5 taps total |
| **Consent** | Short statement in large text (also spoken) + one **giant green "Yes, I agree"** button; date/time recorded silently (locked Round 2) |
| **Capture** | Full-screen camera + **stick-figure frame overlay** showing where the child stands + **voice bubble at top** + **giant shutter at bottom** (locked Round 2) |
| **Analyzing** | Friendly child illustration + **progress bar filling** + voice *"Checking…"* (locked Round 4) — never a blank wait |
| **Weight confirm** | Shows the AI's estimate big: *"Weight: 18 kg — correct?"* with giant **Correct** / **Change** buttons |
| **Document Ready** | Big green ✅ + **"Document Ready"** + spoken summary + three giant buttons: **Share · Next Child · My Documents** |
| **Share sheet** | Native system share (WhatsApp / email / print) — no custom UI |
| **My Documents** | Newest-first **card list**: child name, date, GREEN/AMBER/RED badge, Share/Print buttons; search by name |
| **"Same child?" prompt** | Simple confirm card: *"Same child as before?"* with two giant **Yes / No** buttons |
| **Resume prompt** | *"Resume unfinished document?"* — **Yes** (continue) / **No** (discard draft) |
| **Retake message** | Voice bubble + illustration of the problem + **Retake** (primary) + **Save anyway** (secondary, appears after 2 fails) |
| **Manual Mode** *(worker only)* | Simple form: height, weight, symptom checkboxes, big Save — produces the same document |
| **Daily summary** *(worker only)* | One screen: *"Today: 34 screened, 5 at-risk"* with a big colored count |
| **Setup** | Language buttons + role picker — the only post-setup settings |

---

## 7. The PDF Document Design (locked Round 3: simple & clean with color band)

One page, two zones, **GREEN / AMBER / RED color band** across the top:

```
┌────────────────────────────────────────────────────────────┐
│  [color band: GREEN · AMBER · RED]                          │
│  ✅ Child Wellness Screening — <child name>, <age>, <sex>   │
│  Result: BMI in normal range · No symptoms detected         │
│                                                            │
│  🍎 Corrective measures (simple, with icons):               │
│  • Eat a variety of foods every day                        │
│  • Drink clean water                                       │
│  • Visit the health center if concerned                    │
│  ─────────────────────────────────────────────             │
│  Technical block (small, for workers/doctors):             │
│  BMI 15.2 · WHO BMI-for-age percentile 42nd · reference    │
│  ranges · confidence notes · screening, not a diagnosis     │
└────────────────────────────────────────────────────────────┘
```

| Zone | Audience | Content | Design |
|---|---|---|---|
| **Top** | Villager / parent | Child info, result in plain words, corrective measures | Large icons + big simple text; the color band is the first thing seen |
| **Bottom** | Worker / doctor | BMI value, WHO BMI-for-age **percentile**, reference ranges, confidence notes | Small, dense, technical; never the visual focus |
| **Footer** | Everyone | **"This is a screening result, not a diagnosis."** | Always present, always visible |

Print: A5 (village-friendly) and A4; portrait; margins safe for cheap printers.

---

## 8. Feedback & States

| State | Design |
|---|---|
| **Analyzing (<10 s)** | Progress bar + child illustration + *"Checking…"* voice — never a blank screen |
| **Retake needed** | Gentle, encouraging tone: *"It's okay — let's try again."* + illustration of the issue (locked Round 4) |
| **Low quality fallback** | After 2 fails, **"Save anyway"** appears; the PDF carries a *"Low quality capture"* note — neutral, no blame |
| **Offline** | Invisible — only the sync counter (⬆ N) on Home reflects pending uploads |
| **Crash / battery death** | Next open shows the Resume prompt; draft is safe |
| **Success** | Soft "ding" + big green ✅ + spoken summary |

**Tone rule everywhere:** never blame, never alarm. A retake is *"It's okay"*, a
flag is *"Please visit the health center"* — never *"danger"*.

---

## 9. Web Version Design (locked Round 4)

- **Same greens/cream identity** as the phone — the web feels like the same product.
- **Card list** of documents (newest first), each showing child name, date, and the
  GREEN/AMBER/RED badge.
- **Search box by child name**, big **Print** and **Download** buttons.
- **Visibility rule (from App Flow):** the web login sees only its own account's
  documents — never anyone else's.
- Responsive: usable on a 10" tablet and a 22" monitor; no complex dashboards in v1.

---

## 10. Accessibility

| Requirement | Design |
|---|---|
| **Low literacy** | Illustrations + voice carry the meaning; text is always secondary |
| **Bright sunlight** | Light theme, high contrast (WCAG AA+), matte/anti-glare-friendly colors |
| **Low vision** | Very large default type; no reliance on color alone (color band always paired with words + icons) |
| **Touch precision** | Minimum 48 dp targets; ≥ 16 dp gaps |
| **Motor / shaking hands** | No small sliders, no drag gestures — everything is a tap |
| **Hearing** | All voice content also exists as on-screen text |
| **Children** | Warm, non-clinical tone; no scary images or wording |
| **Old devices** | Design assumes 2 GB RAM / Android 8+; no heavy animations, no bloat |

---

## 11. Design System Components

| Component | Spec |
|---|---|
| **Primary button** | Leaf Green, white bold 28–32 sp text, ≥ 96 dp tall, rounded (16 dp), full width |
| **Secondary button** | White card with green border + Ink text, same height |
| **Giant button** (New Screening, shutter) | Illustrates its action (camera icon); fills half the screen |
| **Voice bubble** | Top of screen, cream/white rounded card, speaker icon + the spoken text (so text mirrors voice) |
| **Result badge** | GREEN / AMBER / RED pill with the level word + icon |
| **Card** (documents list) | White card on cream, 16 dp radius, big tap area |
| **Progress bar** | Thick (12 dp), Leaf Green fill on white track |
| **Sync counter** | Small pill "⬆ N" next to My Documents — the only sync UI |
| **Setup gear** | Small icon, bottom corner — never blocks the flow |

---

## 12. Illustration Inventory (v1)

| Illustration | Used on |
|---|---|
| Child standing straight (full body) | Capture frame overlay, guidance |
| Child facing camera (face view) | Retake: "look at the camera" |
| Sun / bright place | Retake: "photo is dark" |
| Camera / shutter | Home button, capture |
| Document with checkmark | Welcome, Document Ready |
| One child (two crossed out) | Retake: "only one child in frame" |
| Heart / healthy child | GREEN result, success |
| Flag / health center building | RED result: "visit health center" |
| Weight scale / height ruler | Weight confirm, Manual Mode |
| Family (adult + child) | Role picker: Family Member |
| Stethoscope / worker | Role picker: Health Worker |
| Two children, same name | "Same child as before?" prompt |

All illustrations share one style: rounded stick figures, Leaf Green + Ink lines,
cream/white fills, no photos, no cultural stereotypes.

---

## 13. Open Questions

- Final exact wording of the consent statement and welcome voice line (copy for
  review in Implementation Plan).
- Whether the language picker should also offer a "listen to a sample" preview
  before committing.
- Exact corrective-measure icon set for the PDF (diet, water, hygiene, visit).
- Whether the daily summary (worker view) needs a shareable version in v1.

---

*End of UI/UX Brief v0.1 — ready for team review and iteration.*
