# Architecture decision records

One numbering for the whole EV_PNC platform. The next free number is **ADR-0007**.

| ADR | Title | Status |
|---|---|---|
| [0001](0001-translate-at-the-edge.md) | Translate hub protocols at the edge into one canonical model | proposed |
| [0002](0002-hubject-online-emp.md) | Connect to Hubject as an online EMP | proposed |
| [0003](0003-plugcharge-port.md) | One Plug&Charge port, two ecosystem adapters | accepted (2026-10-25) |
| [0004](0004-echx-ocpi-only.md) | Connect to e-clearing.net over OCPI 2.2.1 only | proposed |
| [0005](0005-hub-sequencing.md) | Asymmetric parallel hub sequencing for the pilot | accepted |
| [0006](0006-guest-pricing.md) | Guest (AD_HOC_USER) price = B2B cost + fixed margin + VAT, TL/kWh only | accepted, conditional on TR-01 |

ADR-0001 to 0006 come from the roaming hub analysis (`roaming-hubs/specs/adr/`) and are copied here unchanged. From now on they live here only.

## How to add one

1. Copy [template.md](template.md) to `NNNN-short-title.md` with the next number.
2. Add a row to the table above.
3. Open a PR. The decision is accepted when the product owner (or the architect for technical-only decisions) approves it; set the status and date.
4. Never edit an accepted ADR's decision. Supersede it with a new ADR and mark the old one `superseded by ADR-NNNN`.

Decisions that need an ADR: a change to the canonical model (EV_PNC_ocpi-model), a new or changed hub contract pin, a new component or repo boundary, anything that changes a gate criterion.
