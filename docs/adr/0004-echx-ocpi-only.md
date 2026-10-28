# ADR-0004: Connect to e-clearing.net over OCPI 2.2.1 only

**Status:** proposed · **Date:** 2026-10-24

**Context.** e-clearing.net offers OCPI 2.1.1 and 2.2.1 on ECHX and still offers OCHP 1.3 to 1.4.1 and OCHPdirect. OCHP is SOAP, checks tokens only against the hub's own whitelist (no live authorization at the eMSP), and OCHPdirect needs an OCHP link. ECHX maps between OCHP and OCPI (changelog v3.0).

**Decision.** The eMSP platform connects to ECHX with OCPI 2.2.1 through the existing compatibility layer and never builds an OCHP or OCHPdirect client. The OCHP reference profile stays documentation.

**Consequences.** One protocol family for GIREVE and e-clearing.net. Guest and app tokens (`whitelist=NEVER`) may be refused at CPOs that only speak OCHP until Q-EC-04 is answered. e-clearing.net sits in Phase 5 for the product (no Turkish CPOs), so this ADR only guards the design.

**Sources.** runs/e-clearing/analysis.md §2, §3; changelog https://www.e-clearing.net/changelog-summary-system-update.
