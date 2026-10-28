# ADR-0005: Asymmetric parallel hub sequencing for the pilot

**Status:** accepted · **Date:** 2026-10-25

**Context.** Almost no Turkish CPO is on a hub: ZES is on Hubject; GIREVE and e-clearing.net have none. Coverage in Didim comes mostly from bilateral OCPI and the guest flow. Hubject onboarding takes about three months (median). GIREVE PNCP offers Plug&Charge without our own PKI. A GIREVE roaming licence would add no Didim coverage.

**Decision.** Run two tracks in parallel, unequally:
- Hubject: commercial talks and the OICP 2.3 adapter (roaming, ZES).
- GIREVE: PNCP pre-production only. The roaming offer (BOOST!) is deferred to Phase 5.
- e-clearing.net: Phase 5 (ADR-0004).
Engineering order: shared layer (canonical OCPI model, 2.3.0 to 2.2.1 conversion, mock hubs, fault injection), then the OICP adapter, then the PNCP client. Contracts are signed only after the go/no-go gate (2026-12-07).

**Fallback (option E).** If neither hub passes the gate (K1 and K2 fail), the pilot runs hub-less: bilateral OCPI in Didim plus the guest flow; hubs move to Phase 5.

**Consequences.** Two test environments and two contract talks in the first six weeks. Capacity split stays small because the shared layer serves both. Whether PNCP can be bought without BOOST! is unknown and is GIREVE question 1.

**Sources.** deliverables/05-kararlar.md (Decision 1), deliverables/07-go-no-go.md, runs/hubject/bizdev.md, runs/gireve/bizdev.md.
