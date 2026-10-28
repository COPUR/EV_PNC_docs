# RFP v2: corrections (card P0-22)

Version 2.1 of [rfp-v2.md](rfp-v2.md) corrects four errors found in 2.0. Each was checked against the OCPI 2.3.0 spec at commit `efdf2c5` (tag v2.3.0) of the OCPI mirror pinned in EV_PNC_ocpi-model.

| # | Error in 2.0 | Fix in 2.1 | Spec evidence |
|---|---|---|---|
| 1 | Listed a Bookings module as new in OCPI 2.3.0 | Removed. States that reservations use the `ReserveNow` / `CancelReservation` commands and that anything more is a proprietary extension | The spec has no Bookings module (no `mod_bookings`; the word does not appear in the module files) |
| 2 | Treated the Payments module as part of the eMSP's 2.3.0 upgrade path and as a platform "path" for AFIR | The Payments module belongs to payment terminal providers: exchanged between PTP and CPO, eMSP not a party. The platform's ad-hoc path is the app and AD_HOC_USER flow. Phase 5 now names Parking objects and AFIR fields | `mod_payments`: "Data owner: `PTP`"; the Terminal object is "owned and created by the PTP" |
| 3 | Diagram 6.2 had the CPO sending StartSession to the platform | StartSession is a command from the eMSP to the CPO. The diagram now shows the app start request, the command, the CommandResponse, the CommandResult POST to `response_url`, then Session updates and the CDR | `mod_commands`: "The Token provided by the eMSP for the `StartSession` SHALL be authorized by the eMSP before sending it to the CPO" |
| 4 | Listed EMAID next to the other token types without saying that the eMSP must not push it and that the CPO authorizes it in real time | The eMSP should not push EMAID tokens. The CPO learns the issuer from the charge point and asks the eMSP for real-time authorization, so the platform must implement `POST /tokens/{uid}/authorize` | `mod_tokens`: "The eMSP is RECOMMENDED to not push Tokens with type `EMAID` at all" |

## Noticed, not changed (these are decisions, not errors)

- **Hubject is described as having "OCPI support"** (sections 1, 5, 7 Phase 5, 11). The hub analysis found that Hubject speaks OICP 2.3 (and OPCP for Plug&Charge); GIREVE speaks OCPI 2.2.1. See [ADR-0001](../adr/0001-translate-at-the-edge.md) and [ADR-0002](../adr/0002-hubject-online-emp.md). The wording should change, but the RFP is the product owner's document, so the change is queued for review (card R-02).
- **Didim and e-Devlet vehicle ownership**: the pilot is now the Istanbul-Bodrum corridor ([scope](../pilot/scope.md)) and the e-Devlet vehicle-data integration is parked in favour of a VIN or registration document. Sections 1, 3.1, FR-03 and FR-11 still describe the earlier scope.
- **ISO 15118-20** appears next to -2 in sections 3.1 and 5. The pilot accepts ISO 15118-2 only ([ADR-0003](../adr/0003-plugcharge-port.md)).

The original 2.0 text is in the project files; the diff to 2.1 is the git history of `rfp-v2.md`.
