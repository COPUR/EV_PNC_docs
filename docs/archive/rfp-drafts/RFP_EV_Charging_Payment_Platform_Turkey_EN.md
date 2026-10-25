# Request for Proposal (RFP)

## EV Charging & Payment Integration Platform – Turkey Focus

**Document Type:** Draft RFP  
**Date:** 24 October 2026  
**Version:** 0.1  
**Based on:** Project discussion history  

---

## 1. Introduction and Background

This RFP seeks proposals for the design and development of an **intermediary platform** that unifies electric vehicle (EV) charging infrastructure and payment systems in Turkey.

The platform will **not** act as a Charge Point Operator (CPO) or as a licensed payment institution. Instead, it will function as a neutral integration layer that connects existing CPOs, payment providers, and drivers, delivering a seamless Plug&Charge experience.

The core user promise is simple: the driver plugs in the vehicle and charging starts automatically, with payment authorized end-to-end without cards, app memberships, or manual interactions.

### Key Context for Turkey
- Fragmented charging experience across operators (different apps, cards, pricing).
- Growing EV adoption combined with limited seamless Plug&Charge offerings.
- Opportunity to leverage e-Devlet for vehicle ownership data (with explicit consent) and Masterpass for payment.
- Pilot potential in high-season tourist regions (e.g., Didim area) where foreign drivers familiar with European standards encounter friction.

---

## 2. Project Objectives

| Objective | Description |
|-----------|-------------|
| Seamless Plug&Charge | Enable automatic charging start and payment authorization without additional user interaction. |
| Neutral Intermediary | Connect CPOs and payment providers without becoming either. |
| Turkey-first Experience | Design around e-Devlet consent and Masterpass while preparing for future European OCPI roaming. |
| In-vehicle Integration | Deliver CarPlay (and Android Auto) experience with real-time socket availability and intelligent routing. |
| Regulatory Compliance | Full KVKK compliance via explicit, granular consent and data minimization. |
| Pilot Validation | Prove technical and commercial viability in a seasonal tourist market (Didim region). |

---

## 3. Scope of Work

### 3.1 In Scope
- Mobile application (iOS & Android) with CarPlay integration
- OCPI 2.1-based communication layer with CPOs / eMSPs
- ISO 15118 Plug&Charge flow (vehicle identity + automatic authorization)
- e-Devlet consent management and token-based vehicle ownership data retrieval
- Masterpass integration (payment request only — no card data stored or handled)
- Navigation integration: socket availability feed into routing decision trees
- Consent management system compliant with KVKK
- Pilot deployment readiness for Didim / Aegean tourist corridor

### 3.2 Out of Scope
- Operating or owning charging stations (CPO role)
- Acting as a payment institution or holding funds
- Direct plate-to-identity matching without user-initiated consent token
- Building proprietary charging hardware

---

## 4. Functional Requirements

| ID | Requirement | Priority | Notes |
|----|-------------|----------|-------|
| FR-01 | Automatic charging start upon plug-in | Must | Tesla-like Plug&Charge experience |
| FR-02 | End-to-end autonomous payment authorization | Must | Via Masterpass after consent |
| FR-03 | Single-time e-Devlet consent flow | Must | Token-based, revocable |
| FR-04 | Masterpass consent for charging payments | Must | Separate from general card storage |
| FR-05 | CarPlay socket availability in navigation | Must | Real-time or near-real-time |
| FR-06 | Decision-tree routing with charging stops | Should | Consider range, availability, price |
| FR-07 | User dashboard for consent status & history | Must | Transparency & revocation |
| FR-08 | Multi-CPO session support | Must | Via OCPI roaming |
| FR-09 | Invoice / receipt generation | Should | Using e-Devlet-derived billing data |
| FR-10 | Support for foreign vehicles (EU) | Could | Prepare for cross-border OCPI |

---

## 5. Technical Requirements

| Area | Requirement | Standard / Technology |
|------|-------------|-----------------------|
| Roaming Protocol | CPO ↔ Platform communication | OCPI 2.1 (or latest stable) |
| Vehicle Communication | Plug&Charge authentication | ISO 15118 (2 / 20 readiness) |
| In-vehicle UI | Navigation + charging overlay | Apple CarPlay (+ Android Auto) |
| Identity & Consent | Vehicle ownership data | e-Devlet consent token |
| Payment | Authorization & settlement request | Masterpass / Mastercard |
| Privacy | Data minimization & consent | KVKK (Law 6698) |
| Backend | Scalability & security | Cloud-native, API-first |
| Future | European roaming | OCPI network connectivity |

---

## 6. Pilot Strategy – Turkey (Didim Focus)

**Recommended Pilot Region:** Didim and surrounding Aegean tourist areas.

| Factor | Rationale |
|--------|-----------|
| Demand | High vehicle density in summer (domestic + foreign tourists) |
| Supply Gap | Limited permanent high-quality charging infrastructure |
| User Mix | European drivers already familiar with Plug&Charge / OCPI friction points |
| Seasonality | Clear peak (May–October) allows measurable stress testing |
| Risk | Winter population drop — profitability model must account for seasonality |

Pilot goals: technical proof-of-concept + real user feedback + initial commercial signal.

---

## 7. Proposed Timeline

| Phase | Duration | Key Activities | Deliverables |
|-------|----------|----------------|--------------|
| **Phase 0 – Discovery & Design** | Month 1–2 | Architecture, consent flows, partner mapping, legal review | Architecture document, consent UX, partner shortlist |
| **Phase 1 – Core Backend & Integrations** | Month 3–5 | OCPI layer, e-Devlet token flow, Masterpass integration, consent engine | Working backend APIs, integration test environment |
| **Phase 2 – Mobile & CarPlay MVP** | Month 5–7 | App development, CarPlay navigation overlay, Plug&Charge flow | MVP app + CarPlay prototype |
| **Phase 3 – Pilot Preparation** | Month 7–8 | Partner onboarding (CPO + payment), security & KVKK audit | Pilot-ready system, compliance report |
| **Phase 4 – Didim Pilot** | Month 9–11 | Limited live deployment, user testing, metrics collection | Pilot report, improvement backlog |
| **Phase 5 – Refinement & Scale Readiness** | Month 12 | Bug fixes, UX improvements, European OCPI preparation | Scale-ready roadmap |

**Total estimated duration:** 12 months to pilot conclusion and scale readiness.

---

## 8. Deliverables

| # | Deliverable | Phase |
|---|-------------|-------|
| 1 | Technical architecture & data flow diagrams | Phase 0 |
| 2 | Consent management system (e-Devlet + Masterpass) | Phase 1 |
| 3 | OCPI 2.1 integration layer | Phase 1 |
| 4 | Masterpass payment request integration | Phase 1 |
| 5 | Mobile application (iOS/Android) | Phase 2 |
| 6 | CarPlay integration with navigation overlay | Phase 2 |
| 7 | KVKK compliance documentation & audit report | Phase 3 |
| 8 | Pilot deployment package & operational runbook | Phase 3–4 |
| 9 | Pilot results report & recommendations | Phase 4 |
| 10 | Scale-up and European readiness roadmap | Phase 5 |

---

## 9. Open Issues & Risks

| Issue | Description | Mitigation Suggestion |
|-------|-------------|-----------------------|
| OCPI roaming in Turkey | Limited mature roaming agreements | Start with direct CPO integrations; prepare OCPI abstraction |
| e-Devlet consent mechanics | Exact token lifetime, revocation, and available data fields | Early legal + technical workshop with relevant authorities |
| CarPlay navigation depth | Level of control over decision trees | Define minimal viable overlay first |
| Seasonality | Didim winter demand drop | Design pricing and partnership models accordingly |
| Partner dependency | Need cooperative CPOs and payment provider | Early LOIs in Phase 0 |

---

## 10. Proposal Submission Guidelines

Respondents are requested to include:

- Understanding of the intermediary model and Turkey-specific constraints
- Proposed technical architecture (with diagrams)
- Approach to e-Devlet consent and Masterpass integration
- Timeline and resource plan aligned with the phases above
- Relevant experience with OCPI, ISO 15118, CarPlay, or Turkish payment systems
- Compliance and security approach (KVKK, PCI-related considerations)
- Estimated effort and commercial model (fixed, T&M, or hybrid)

---

**Note:** This is a draft RFP derived from project discussion notes. It should be reviewed and refined with legal, technical, and commercial stakeholders before formal issuance.

---

*End of Document*
