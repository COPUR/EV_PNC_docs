# EV_PNC_ public repository set, v2 (updated 2026-10-25 with the consent boundary review)

**Date:** 2026-10-25 · **Replaces:** `../README.md` (v1, 13 repos; kept unchanged) · **Status:** plan; repos not created yet (GitHub returns 403 on repo creation from this session, so you run the script)
**Inputs:** v1 plan, hub decisions and gate (`../../roaming-hubs/deliverables/05-kararlar.md`, `07-go-no-go.md`), `../../corridor-pilot/`, `../../national-hub-service/`, `../../roaming-consent/`, the `EV_PnC_Consent_` family (`../consent/README.md`), packaging principles (Martin & Martin, ch. 28: REP, CRP, CCP, ADP, SDP, SAP). Details and metrics: `packaging-analysis.md`.

## 1. What changed and why

19 repos instead of 13: **10 to create now, 7 after the gate, 2 on trigger.** Together with the 12 `EV_PnC_Consent_` repos that is 31, created in waves so no repo sits idle.

1. **Hubs move from phase 5 to now.** Gate criterion K9 (mock hubs green) is due before 2026-12-07, and the Hubject onboarding takes about 3 months. `roaming-hubs` becomes `hub-contracts` (specs and pins) plus `hub-gateway` (adapters).
2. **A stable core appears.** `ocpi-model` is carved out of `ocpi-emsp`; each service publishes a small `*-api` component. In v1 as described, policy, payments, plug&charge and consent all need the model that lives inside `ocpi-emsp`, while `ocpi-emsp` calls them: a five-repo dependency cycle (checked, see `packaging-analysis.md` §3).
3. **`EV_PNC_consent` is retired.** KVKK consent belongs to the `EV_PnC_Consent_` family; vehicle binding by VIN and registration document (e-Devlet is parked) moves into `plugcharge` as a module.
4. **Corridor and hub decisions get a home:** `pilot-analytics` (KPI-1..7, K1 count), `pricing` (ADR-0006 guest formula), `national-data` and `national-consent` (open-source reference implementations for EPDK and for e-Devlet, wave 3, split by who would adopt them; see `consent-boundary-review.md`).
5. **Infra is split in two:** reusable `infra-modules` (public, shared with `EV_PnC_Consent_infra`) and `infra` (private). v1 made the infrastructure public while the consent plan makes it private; this removes the contradiction.

Naming: this set uses `EV_PNC_` as you typed it. The consent family keeps your earlier `EV_PnC_Consent_` casing. GitHub treats names case-insensitively but the full names never collide.

## 2. Rule used to draw the boundaries

Martin's principles apply to **components** (things released and versioned: a library, an API definition, a deployable). A **repo** is a unit of ownership, CI and security. So the plan does it in two steps: (1) group classes into components by CCP, CRP and REP, (2) group components into repos by owner and release cadence. One repo may publish several components with their own tags (`policy-api/v1.2.0`).

| Principle | How it was applied |
|---|---|
| **REP** (release unit = reuse unit) | Every cross-repo dependency is on a tagged component: `ocpi-model`, `*-api`, `hub-contracts`, `consent-contracts`. Nobody copies code. |
| **CRP** (reused together lives together) | Planner needs the price API, not PSP code, so `pricing` is not inside `payments`. Mobile needs only `edge-api`. |
| **CCP** (changes together lives together) | Hub adapters change with each hub's spec, so they live with `hub-core`; vendor specs change on drift, so they live apart in `hub-contracts`. PSP changes and margin rules change for different reasons, so `pricing` and `payments` are separate. |
| **ADP** (no cycles) | Checked by `tools/packaging_check.py --strict`; v2 has none. |
| **SDP** (depend towards stability) | Every deployable depends on `*-api` and `ocpi-model` (I near 0), never on another deployable. |
| **SAP** (stable means abstract) | `*-api`, `ocpi-model`, `hub-contracts` and `nhs-contracts` hold schemas and interfaces; servers hold the concrete code. |

Two extra rules from the Consent plan are kept: split a repo only when the load profile, the separation of duties, the audience or the exposure differ; and consume simulators as images over the wire, never as libraries.

## 3. Repository list

| # | Repository | Vis. | Wave | Owner | Purpose | v1 relation |
|---|---|---|---|---|---|---|
| 1 | `EV_PNC_docs` | public | 1 | Architect agent + Product owner | Platform architecture, ADRs, RFP v2, corridor-pilot and go/no-go specs, KVKK/PCI notes, squad working agreement and kanban. | EV_PNC_docs (kept; absorbs the corridor-pilot and national-hub-service platform-side specs) |
| 2 | `EV_PNC_infra-modules` | public | 1 | DevOps agent | Reusable Terraform modules, Helm library charts and reusable CI workflows for EV_PNC_ and EV_PnC_Consent_ services. | Split out of EV_PNC_infra (v1 mixed reusable modules with environments) |
| 3 | `EV_PNC_infra` | private | 1 | DevOps agent | Environments, cluster wiring, key vault partitions, static egress IPs and hub allow-lists, runbooks for the EV_PNC_ platform. | EV_PNC_infra (v1 was public; now private to match EV_PnC_Consent_infra and EV_PnC_Consent_ops) |
| 4 | `EV_PNC_ocpi-model` | public | 1 | Architect agent | Canonical OCPI 2.3.0-shaped model, domain events and error model shared by all EV_PNC_ services. | New: carved out of EV_PNC_ocpi-emsp so that 19 consumers do not depend on a server release |
| 5 | `EV_PNC_ocpi-emsp` | public | 1 | Backend agent | OCPI eMSP server: Credentials, Versions, Locations, Tariffs, Tokens, Commands, Sessions and CDRs, real-time authorization with policy hook and consent gate. | EV_PNC_ocpi-emsp (kept; model moved to EV_PNC_ocpi-model) |
| 6 | `EV_PNC_hub-contracts` | public | 1 | Architect agent + QA agent | Hub specs and contracts for Hubject, GIREVE and e-clearing.net: requirements, profiles, conversion tables, Gherkin conformance features, pins and drift checks. | New: the spec bundle from roaming-hubs/specs, versioned so adapters and mocks can both depend on it |
| 7 | `EV_PNC_hub-gateway` | public | 1 | Backend agent | Roaming hub adapters behind canonical ports: Hubject (OICP, OPCP), GIREVE (OCPI 2.2.1, PNCP), e-clearing.net (ECHX, phase 5). | EV_PNC_roaming-hubs (renamed; moved from phase 5 to wave 1 because K9 needs mock hubs before the 2026-12-07 gate) |
| 8 | `EV_PNC_simulator` | public | 1 | QA agent | Simulators and end-to-end harness: OCPI CPO, ISO 15118 EV/charger, hub mocks generated from EV_PNC_hub-contracts pins, failure injection, corridor trip replays. | EV_PNC_simulator (kept; hub mocks and corridor scenarios added) |
| 9 | `EV_PNC_telemetry` | public | 1 | Backend agent | Charger data foundation: live status ingest with a 15-minute freshness rule, status/fault/occupancy history, EPDK list reconciliation, corridor EVSE index. | EV_PNC_telemetry (kept; data foundation for the corridor KPIs) |
| 10 | `EV_PNC_pilot-analytics` | public | 1 | Data agent | Corridor pilot measurement: KPI-1 to KPI-7 jobs, control and treatment assignment rule, daily K1 count, price sheet, dashboards. | New: the v1 board had P4-05 only; the corridor needs KPIs from day one |
| 11 | `EV_PNC_policy-engine` | public | 2 | Backend agent | Driver policies: price threshold, operator allow/block lists, minimum power. | EV_PNC_policy-engine (kept; api published as its own component) |
| 12 | `EV_PNC_pricing` | public | 2 | Backend agent + Product owner | Effective price service: normalises OCPI and NGP tariffs, applies the ADR-0006 guest formula (B2B cost + fixed margin + VAT, TL/kWh only), caps and FX. | New: split from payments so the planner and policy engine do not depend on PSP code (SDP) |
| 13 | `EV_PNC_payments` | public | 2 | Backend agent | Payment orchestration: PSP tokens, AD_HOC_USER guest pre-authorisation and capture on CDR, reconciliation. | EV_PNC_payments (kept; pricing moved out) |
| 14 | `EV_PNC_plugcharge` | public | 2 | Backend agent | ISO 15118 Plug&Charge contract lifecycle behind one port: EMAID, PCID binding, renewal, revocation. | EV_PNC_plugcharge (scope reduced) plus the useful part of EV_PNC_consent |
| 15 | `EV_PNC_planner` | public | 2 | Planner agent | Corridor charging-stop planner: total time = drive + charge + expected queue, dynamic programming, incremental re-planning, ferry and bridge model, queue prediction, peak profiles, alternative offers. | EV_PNC_planner (kept; corridor scope) |
| 16 | `EV_PNC_api-gateway` | public | 2 | Backend agent | Edge API for app and in-car clients: JWT/OIDC auth, rate limits, BFF aggregation. | EV_PNC_api-gateway (kept; edge-api split out as a component) |
| 17 | `EV_PNC_mobile` | public | 2 | Mobile agent | iOS and Android apps with CarPlay and Android Auto: map, plan, start/stop, guest pay, Plug&Charge activation, consent screens in TR/EN/DE/NL. | EV_PNC_mobile (kept) |
| 18 | `EV_PNC_national-data` | public | 3 | Architect agent + Backend agent | Open-source reference for the EPDK-side national services: C1 charging data access point (EPDK list to OCPI Locations and Tariffs, pull and push), C2 TR ID registry, C4 hub trust and onboarding. | New (from national-hub-service/; split by adopting organisation: EPDK here, e-Devlet in EV_PNC_national-consent) |
| 19 | `EV_PNC_national-consent` | public | 3 | Architect agent + Backend agent | Open-source reference for the state-side Mobility Consent Service (C3) proposed to e-Devlet: scopes, signed assertions, per-recipient opaque IDs, SSF events, plus a mock for tests. | New (from national-hub-service/ C3; split by adopting organisation) |

Components per repo, dependencies and metrics: `components.csv` and `packaging-check-output.txt`.

### Waves

| Wave | When | Repos | Why now |
|---|---|---|---|
| **1** | 26 Oct 2026 onward, before the 7 Dec gate | docs, infra-modules, infra, ocpi-model, ocpi-emsp, hub-contracts, hub-gateway, simulator, telemetry, pilot-analytics | K9 mock hubs, K1 count by 9 Nov, bilateral OCPI, data foundation for KPI-1/2/7 |
| **2** | Gate day (7 Dec) or earlier if a first card is pulled | policy-engine, pricing, payments, plugcharge, planner, api-gateway, mobile | Needs gate outcomes: K2/K3 decide whether `plugcharge` is built at all in the pilot; K8 and TR-01 shape `pricing` |
| **3** | When EPDK PoT-1 starts or a workshop is scheduled | national-data, national-consent | Pilot does not depend on it; it is the enabler track |

### Build order inside wave 1

`docs`, `infra-modules` → `ocpi-model`, `hub-contracts` → `simulator`, `ocpi-emsp`, `hub-gateway` (mock-first) → `telemetry`, `pilot-analytics` → `infra` (when the first environment is needed; static IPs and CSRs for Hubject, TR-17)

## 4. Alignment with the `EV_PnC_Consent_` family

Dependency direction is one way: EV_PNC_ services depend on `EV_PnC_Consent_contracts` (decision SDK, events). The consent family depends on EV_PNC only for shared infra modules, and consumes the simulator as an image. No cycle (checked).

| Concern | Owner | EV_PNC_ side |
|---|---|---|
| Purposes, recipients, grants, receipts, safeguards, rights, tenancy | `Consent_registry` | None. The app reaches it through `api-gateway`. |
| Roaming allow/deny at call time | `Consent_decision` | `ocpi-emsp` and `hub-gateway` call it before any token or data leaves; fail closed. |
| Revocation propagation | `Consent_registry` (propagation worker) | `ocpi-emsp` invalidates tokens, `hub-gateway` calls the hub, `plugcharge` removes the contract from the pool (RC-REV-003). |
| Notice texts TR/EN/DE/NL | `Consent_notices` | `mobile` renders and verifies the hash. |
| Audit trail | `Consent_audit` | Services keep operational logs only. |
| Legal-basis matrix, DPO material | `Consent_docs` | `EV_PNC_docs` keeps only the platform data inventory (P0-17). |
| e-Devlet client | `Consent_edevlet-bridge` | `plugcharge` uses it later for vehicle ownership (parked). |
| Infrastructure | `Consent_infra` (private) | Reuses `EV_PNC_infra-modules`; own key vault partition. |
| Hub mocks | `Consent_testkit` | Pulls `EV_PNC_simulator` images. |

**Three layers, answered in `consent-boundary-review.md`:** (1) our own `EV_PnC_Consent_` family is the system of record and decision point for our controller duties (neutral, multi-tenant); (2) a state-hosted Mobility Consent Service (C3, e-Devlet) is an optional upstream source, reached only through `Consent_edevlet-bridge`; the reference for it lives in `EV_PNC_national-consent`, owned by whoever adopts it, never by us; (3) EPDK has no consent role: C1 and C2 are data and ID services (`EV_PNC_national-data`).

**Proposed amendments to the consent plan (not applied; consent files are unchanged):**

1. **Catalogue gets platform purposes.** The registry is built to be central and neutral, but its catalogue only has the roaming purposes RP-1..5. The pilot also needs a lawful basis and notice for location traces used for planning and KPIs (pseudonymised, cell level after 90 days) and for push notifications. With `EV_PNC_consent` retired, no one owns these. Recommended: add them to the catalogue as purposes outside roaming. Needs the DPO.
2. **`edevlet-bridge` becomes a generic Mobility Consent Service client** with scopes `roaming.share` and `vehicle.ownership`, so one FAPI 2.0 client exists, not two.
3. Wording only: "reuses EV_PNC_infra modules" becomes "reuses `EV_PNC_infra-modules`".

## 5. Triggers to split or merge later

| Trigger | Action |
|---|---|
| e-clearing.net work starts with its own certification | `hub-echx` moves to `EV_PNC_hub-eclearing` |
| Second on-call rotation | Create `EV_PNC_ops` (SLOs, game days), mirroring `Consent_ops` |
| e-Devlet ownership scope goes live | Extract `vehicle-binding` from `plugcharge` |
| Own PKI is built | Extract `own-pki` from `plugcharge` |
| Queue prediction becomes a learned model | Extract `queue-model` from `planner` |
| Separate iOS and Android teams | Split `mobile` |
| EPDK and e-Devlet both adopt the trust layer (C4) | Extract `EV_PNC_national-trust` from `national-data` |
| `pricing` and `payments` always release together for 3 releases | Merge them (CCP evidence) |

Lean variant if capacity is short: start with 6 repos (`docs`, `ocpi-model`, `ocpi-emsp`, `hub-contracts`, `hub-gateway`, `simulator`) and put `telemetry`, `pilot-analytics` and `infra-modules` into folders of `ocpi-emsp` and `docs` until the first card needs them. The component boundaries stay, so the split costs a repo move, not a redesign.

## 6. Open points

- **Vendor contracts in a public repo.** The pinned Hubject OICP/OPCP files are CC BY-SA 4.0. `hub-contracts` keeps hashes and the fetch script and attributes the licence; if you prefer not to redistribute them, keep `_sources/` out of git.
- **Packaging metrics use estimated abstractness.** Replace with measured values from code once repos have code.
- **Case of the prefix** (`EV_PNC_` vs `EV_PnC_Consent_`). Say if you want one casing across both.

## 7. How to create them

```bash
cd repo-plan/v2
gh auth login                       # once
WAVE=1 ./create_repos_v2.sh         # 10 repos now (infra is private)
WAVE=2 ./create_repos_v2.sh         # at the gate
WAVE=3 ./create_repos_v2.sh         # on trigger
python3 tools/packaging_check.py components.csv --strict   # rerun when dependencies change
```

The script skips repos that already exist, creates public repos with Apache-2.0 and the private one without a licence, and pushes the starter READMEs from `readmes/`. Tested with a stand-in `gh` (19 creates, one private). It does not touch the v1 script. On macOS the `base64` fallback is built in.

After creating, attach each repo to the project (`add_repo`, access: push) so agents can push scaffolds.
