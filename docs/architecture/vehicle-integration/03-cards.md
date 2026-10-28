# Proposed cards: vehicle integration

**Status:** proposal, **not** added to `kanban/v2/ev_pnc_backlog_v2.csv`. The wartime rule (no new card without dropping one until the gate of 2026-12-07) applies; the product owner picks what to drop or whether these start after the gate. Ids use the prefix VH to avoid the reserved V-01 (invoice issuer).

| Id | Title | Repo | Depends on | Human gate | Points |
|---|---|---|---|---|---|
| VH-01 | Decide Tesla Fleet API route: registration entity, Turkey billing, scopes; counsel reviews L1..L10 | EV_PNC_docs | P0-04, X-01 | yes | 2 |
| VH-02 | `vehicle-core` ports and `vehicle-tesla` read-only adapter on pinned fixtures; token vault; key custody and rotation runbook | EV_PNC_vehicle-gateway | VH-01, X-01 | no | 8 |
| VH-03 | `tesla-edge` (Go): Fleet Telemetry receiver publishing SoC and charge state only, key proxy, field allowlist test (no location) | EV_PNC_vehicle-gateway | VH-02 | no | 5 |
| VH-04 | `VehicleLink` state machine, consent purpose `vehicle.read`, `VehicleBinding.evidence`, topics `ev.vehicle.*` in `topics.csv` | EV_PNC_vehicle-gateway, EV_PNC_plugcharge, EV_PNC_consent_contracts | VH-02, P2-14 | no | 5 |
| VH-05 | App: connect-your-car, my-vehicle and digital-key-help screens (React Native, TR/EN/DE/NL) | EV_PNC_mobile | VH-04, P3-05 | no | 5 |
| VH-06 | Spike: Android Auto energy level on a real Togg and a real BYD; Java native module if it works | EV_PNC_mobile | P3-09 | no | 3 |
| VH-07 | Research: how a Tesla identifies itself at third-party CPOs in Türkiye (VIN, MAC/EVCCID) and what Autocharge-style binding needs | EV_PNC_plugcharge | P0-08 | no | 3 |
| VH-08 | Simulator: fake OEM cloud, CCC Digital Key release 3 test double for app flows | EV_PNC_simulator | VH-05 | no | 5 |

Not a card: partnership requests to Togg and BYD (product owner decision, not sent); a spike on a Trumore or BYD app binary (only after counsel and with a team-owned vehicle; would need its own card and an ADR amendment).

Swap suggestion: VH-01 and VH-07 are small and can replace two off-critical-path I3 cards; VH-02..VH-05 wait for the gate unless the pilot cohort contains Teslas (ask in the pilot recruiting, K-cards).
