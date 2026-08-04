# PRD — Vision-Based Child Wellness Shield

| Field | Value |
|---|---|
| **Document** | Product Requirements Document (PRD) |
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

The **Vision-Based Child Wellness Shield** is an automated computer vision system that
non-invasively estimates BMI and detects visible health symptoms in children from
photos and videos taken on a simple smartphone camera.

The product is intentionally **simple by design**: anyone — a villager with no formal
training, or a health center worker — takes a photo or video of a child, and the system
instantly generates a **document containing the findings and the corrective measures to
be taken**. That document is the core deliverable of the entire product.

It scales health monitoring for rural welfare programs such as the **Mid-Day Meal
Scheme**, replacing irregular manual checkups with real-time, data-driven tracking —
at **zero cost to operate** (free-tier infrastructure), offline-first for remote
villages and coastal areas.

---

## 3. Problem Statement

- In rural villages and coastal areas, children are checked for malnutrition and
  visible health conditions only sporadically, through manual visits by health workers.
- Manual checkups are slow (limited children per day), irregular, and rarely recorded
  in a usable form.
- Welfare programs like the Mid-Day Meal Scheme lack a scalable, low-cost way to
  measure child health outcomes and detect at-risk children early.
- A health worker or even a village member already carries a phone; the missing piece
  is a tool that turns a simple photo/video into actionable health information.

---

## 4. Product Vision

> *Anyone can pick up a phone, photograph a child, and receive an instant,
> easy-to-understand document of the child's health findings and the corrective
> measures to be taken.*

### 4.1 Core Product Loop

```
📸 CAPTURE  →  🧠 ANALYZE  →  📄 DOCUMENT
 photo/video   BMI + symptom    findings + corrective
 of a child     estimation       measures, shared/printed
```

That is the whole product. Everything else (records, sync) exists only to support
this loop.

---

## 5. Goals & Non-Goals

### 5.1 Goals

1. Estimate a child's BMI from a camera capture (hybrid: automatic estimation with
   manual fallback when needed).
2. Detect visible health symptoms: jaundice (yellowing), pallor/anemia cues, visible
   malnutrition cues, skin conditions (rashes/lesions), and thyroid swelling (goitre).
3. Instantly generate a per-child document with **findings** and **corrective
   measures**.
4. Be usable by a person with no training or low literacy (voice prompts, local
   languages, minimal steps).
5. Operate fully offline in the field, syncing documents to a cloud store when
   connectivity is available (daily sync).
6. Operate at **zero cost** using free-tier infrastructure.
7. Support a throughput of 50–150 children per site per day.

### 5.2 Non-Goals (explicitly out of scope for v1)

- ❌ Clinical diagnosis of any condition — this is a **screening and guidance** tool only.
- ❌ Complex dashboards, escalation ladders, and multi-tier admin analytics (may be
  revisited later).
- ❌ State-level rollout infrastructure and government-cloud migration (design must be
  *migration-ready*, but not executed now).
- ❌ Integration with the Mid-Day Meal Scheme's meal-attendance systems (API
  integration points are designed, not wired).
- ❌ Automated referral tracking to health centers (referrals are issued via the
  document; follow-up is manual).

---

## 6. Target Users & Personas

| Persona | Description | Core need | Skill level |
|---|---|---|---|
| **Village User** | A parent or village member, possibly with low literacy | Point phone at a child, capture, receive the document | Very low |
| **Health Center Worker** | Works at a PHC / runs periodic screening camps | Same simple flow, slightly higher volume; may print/share documents | Low–moderate |
| **Parent/Guardian (document recipient)** | Receives the generated document | Understand the findings and follow corrective measures | Very low |

**Design consequence:** the capture flow must be 2–3 taps maximum, guided by voice
prompts and icons, never by written instructions alone.

---

## 7. Functional Requirements

Priorities: **M** = Must have (v1), **S** = Should have (v1.1), **C** = Could have (later).

### 7.1 Capture (📸)

| ID | Requirement | Priority |
|---|---|---|
| FR-1 | User can capture a **photo or video** of a child using the phone camera | M |
| FR-2 | Capture is guided by **voice prompts and icons** (e.g., *"Child, stand straight, face the camera"*) in the selected language | M |
| FR-3 | System detects whether a child's body is adequately framed; prompts re-capture if not (e.g., child too close/far, face not visible) | S |
| FR-4 | Quick form before capture: child's **name, age, gender** — personalizes the document and provides the age/sex required for WHO BMI-for-age | S |
| FR-5 | Capture works **fully offline** | M |

### 7.2 Analysis (🧠)

| ID | Requirement | Priority |
|---|---|---|
| FR-6 | Estimate **BMI** from the capture (body landmarks → height/weight estimation) | M |
| FR-7 | **Hybrid fallback:** if the automatic estimate is uncertain, prompt the user to enter weight (and/or height) manually and recompute | M |
| FR-8 | Detect visible symptoms: **jaundice, pallor/anemia cues, malnutrition cues, skin conditions, goitre (thyroid swelling)** | M |
| FR-9 | Analysis completes within a few seconds per child on-device or near-device | S |
| FR-10 | If no body is detected or capture quality is too low, return a clear, simple retry message (voice + icon) | M |

### 7.3 Document (📄)

| ID | Requirement | Priority |
|---|---|---|
| FR-11 | Generate an **instant per-capture document** containing: (a) **Findings** — estimated BMI, BMI-for-age category, detected symptoms; (b) **Corrective measures** — simple, actionable guidance (nutrition, hydration, hygiene, when to seek a health center) | M |
| FR-12 | Document is understandable at **low literacy levels** — large text, icons, simple language, and the user's local language | M |
| FR-13 | Document can be **shared and printed** (PDF/image; share via WhatsApp, Bluetooth, or print) | M |
| FR-14 | Document clearly states it is a **screening result, not a diagnosis** | M |

### 7.4 Records & Sync (☁️)

| ID | Requirement | Priority |
|---|---|---|
| FR-15 | Every generated document **syncs to a simple cloud store** (free tier) when connectivity is available | M |
| FR-16 | Documents queue locally when offline and **auto-sync in daily batches** | M |
| FR-17 | A simple **history list** of past documents (synced or local) is viewable in the app | S |
| FR-18 | Sync is idempotent and conflict-safe (no duplicate documents after retries) | S |

### 7.5 Language & Accessibility

| ID | Requirement | Priority |
|---|---|---|
| FR-19 | Interface supports **Hindi + English + regional languages** | M |
| FR-20 | **Voice/audio prompts** guide capture and results in the local language | M |
| FR-21 | Interface relies on **icons and large touch targets** over text | M |

---

## 8. Non-Functional Requirements

| Category | Requirement |
|---|---|
| **Cost** | System must operate at **zero monetary cost** (free-tier hosting, open-source models) |
| **Connectivity** | Fully functional offline; daily batch sync when internet returns |
| **Simplicity** | A first-time user with no training completes a capture in **≤ 3 taps** |
| **Performance** | Document generated within **< 10 seconds** per capture (≤ ~30 seconds including re-captures) |
| **Throughput** | Supports **50–150 children per site per day** on a single device |
| **Accuracy** | BMI estimate accuracy validated against manual measurement in pilot (target within acceptable clinical band; exact target defined in TRD) |
| **Privacy** | Guardian **consent** captured before first screening; health data **anonymized** for any aggregate use; no unnecessary PII collected |
| **Compliance** | Designed for minors' data protection; migration-ready for government infrastructure standards |
| **Devices** | Android phones/tablets (primary) + fixed camera kiosks (secondary); modest hardware |
| **Scalability** | Architecture supports growth from a few pilot sites to larger deployments without redesign |

---

## 9. User Stories

**Village user:**
- *"As a villager, I want to take a photo of my child and get an instant document, so I can know if my child needs attention."*
- *"As a villager who can't read well, I want voice instructions in my language, so I can use the app without help."*
- *"As a parent, I want the document to tell me in simple words what to do, so I can act on it."*

**Health center worker:**
- *"As a health worker, I want to screen many children quickly in a camp, so I can cover 100+ children in a day."*
- *"As a health worker, I want to work even where there is no internet, so I can screen remote villages and sync later."*
- *"As a health worker, I want to share or print each child's document, so the family and center have a record."*

---

## 10. Success Metrics (KPIs)

| KPI | Definition | Target |
|---|---|---|
| **Screening coverage rate** | % of enrolled children screened per cycle | ≥ 80% |
| **Detection → document turnaround** | Time from capture to document available | ≤ 30 seconds |
| **Referral completion rate** | % of children flagged at-risk whose document is shared with family/center | ≥ 90% |
| *(Secondary)* **BMI accuracy vs manual** | Agreement of estimated vs manually measured BMI | Defined in TRD validation plan |

---

## 11. Out of Scope (Explicit)

- Diagnoses, prescriptions, or clinical advice beyond basic guidance.
- Multi-tier dashboards, state analytics, escalation workflows (deferred).
- Meal-attendance integration with Mid-Day Meal Scheme (designed, not built).
- Government cloud deployment (migration-ready only).
- Automated referral tracking/outcome loops (manual follow-up).

---

## 12. Constraints & Assumptions

**Constraints**
- Zero budget — free-tier services and open-source tooling only.
- Rural/coastal connectivity is unreliable — offline-first is mandatory.
- Users may have low literacy — voice + icons are mandatory.
- Minors' health data — privacy and consent are non-negotiable.

**Assumptions**
- Field devices are Android smartphones (a kiosk variant can come later).
- A child can stand reasonably still, roughly facing the camera, for a few seconds.
- Daylight or basic indoor lighting is available at capture time.
- Corrective-measure guidance content can be sourced from standard public-health
  nutrition guidance (e.g., WHO/ICDS-aligned advice).

---

## 13. Stakeholders

| Stakeholder | Interest |
|---|---|
| **Villagers / parents** | Quick, understandable health feedback for their children |
| **Health center workers** | Simple high-volume screening tool that works offline |
| **Schools / Anganwadi centers** | Better monitoring of children under welfare programs |
| **Welfare programs (e.g., Mid-Day Meal Scheme)** | Scalable health-outcome data for program effectiveness |
| **Health department (future)** | Aggregate, anonymized insights (deferred phase) |

---

## 14. Risks & Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| CV model accuracy insufficient in field conditions | High | Pilot validation vs manual measurement; hybrid manual fallback; capture-quality gating |
| Low adoption by low-literacy users | High | Voice-guided, icon-driven flow; co-design with real users in pilot |
| Privacy concerns for minors' data | High | Consent capture, minimal data, anonymization for aggregate use |
| Offline sync conflicts/duplicates | Medium | Idempotent sync with unique document IDs |
| Poor capture conditions (lighting, movement) | Medium | Re-capture prompts; fallback to manual measurement |
| Zero-cost hosting limits at scale | Medium | Free tiers sized for pilot; govt-migration-ready architecture |

---

## 15. Future Roadmap (Post-v1, Not Committed)

- Longitudinal growth tracking per child (WHO growth charts, risk trajectory).
- Simple center-level summaries for program staff.
- Fixed camera kiosk mode for larger centers.
- Government cloud (NIC/MeghRaj) migration and Mid-Day Meal Scheme API integration.

---

## 16. Open Questions (for follow-up docs)

- Exact corrective-measure content library and its sources (finalize in Implementation Plan).
- Which regional languages first (Hindi → Bengali/Tamil/Telegu/Marathi…)? (UI/UX Brief)
- Device camera requirements and pose-estimation model choice. (TRD)
- Document format preference (PDF/image) and print workflow. (UI/UX Brief)
- Consent capture format (verbal + thumbprint/signature?). (Backend Schema)

---

*End of PRD v0.1 — ready for team review and iteration.*
