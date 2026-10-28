# ADR-0001: Translate hub protocols at the edge into one canonical model

**Status:** proposed · **Date:** 2026-10-24

**Context.** Hubject speaks OICP 2.3 (and OPCP for Plug&Charge), GIREVE speaks OCPI 2.2.1 with hub deviations (and PNCP), e-clearing.net is OCPI/OCHP with unknown details. The platform's core is an OCPI 2.3.0 eMSP.

**Decision.** Keep the core model OCPI 2.3.0-shaped. Each hub gets an adapter in `EV_PNC_roaming-hubs` that translates at the boundary: OICP ↔ canonical for Hubject, 2.2.1 profile ↔ 2.3.0 for GIREVE. Hub rules live in data (profile and mapping files), not code branches.

**Consequences.** Policy, pricing and payments see one session and CDR shape. Each adapter carries its own contract tests generated from pinned contracts. Fields with no canonical home (for example OICP signed metering details) need explicit extension slots.

**Sources.** `../hubject/spec.md`, `../gireve/spec.md`, report §6.
