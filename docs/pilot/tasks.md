# Tasks: corridor pilot

Format: `- T-ID | title | reqs | depends | env | exit`

- T-CP-01 | Corridor model: M + A1..A4 geometries, versioned | GEO-001 | - | dev | geometries loaded, feature green
- T-CP-02 | EVSE corridor index with family and cluster tags | GEO-002 | T-CP-01 | dev | index rebuilt nightly
- T-CP-03 | Total-time ranking with three components | NAV-001 | T-CP-01 | dev | corridor-planning green
- T-CP-04 | Charging-time model: curve, sharing, climate load | NAV-002, IDLE-004 | T-CP-10 | dev | MAE report on test trips
- T-CP-05 | Active-trip re-planning and sparse-segment reserve | NAV-003..004 | T-CP-03 | dev | feature green
- T-CP-06 | Ferry and bridge crossing model (A1) | NAV-005 | T-CP-03 | dev | feature green
- T-CP-07 | Queue prediction live/historical + alternative offer | IDLE-001..002 | T-CP-11 | dev | idle-waiting green
- T-CP-08 | End-condition and occupancy-fee notice | IDLE-003 | - | dev | feature green
- T-CP-09 | Peak calendar and peak profiles | PEAK-001..002 | T-CP-11 | dev | feature green
- T-CP-10 | Live status ingest with freshness rule | DATA-001 | - | dev | data-foundation green
- T-CP-11 | Status, fault and occupancy history + profiles | DATA-002..003, IDLE-004 | T-CP-10 | dev | two-week profile built
- T-CP-12 | EPDK list and Şarj@TR weekly reconciliation | DATA-004 | - | dev | first discrepancy report
- T-CP-13 | Plug&Charge attempt log and failure classes | PNC-001..002 | - | dev | pnc-friction green
- T-CP-14 | Bounded Plug&Charge preference in ranking | PNC-003 | T-CP-03 | dev | feature green
- T-CP-15 | Channel selection and display (Hubject, bilateral, guest) | ACCESS-001..002 | - | dev | multi-operator green
- T-CP-16 | Daily K1 evidence count | ACCESS-003 | T-CP-02 | dev | count report before 2026-11-09
- T-CP-17 | Guest price engine per ADR-0006 with caps | PRICE-001..002 | - | dev | guest-pricing green
- T-CP-18 | Weekly direct card price sheet | PRICE-003 | - | ops | sheet in pilot report
- T-CP-19 | KPI jobs, dashboard, control/treatment groups | KPI-001..002, DATA-005 | T-CP-11 | dev | kpi-measurement green
- T-CP-20 | Post-trip waiting question and trace retention | KPI-003..004 | - | dev | feature green
- T-CP-21 | Real trips on M + three families incl. peak | GEO-003 | T-CP-19 | pilot | trip log per family
