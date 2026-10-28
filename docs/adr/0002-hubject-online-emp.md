# ADR-0002: Connect to Hubject as an online EMP

**Status:** proposed · **Date:** 2026-10-24

**Context.** OICP allows offline EMPs (push authentication data, pull CDRs) and online EMPs (real-time authorize, CDRs pushed). The project requires price and operator policy checks at authorization time.

**Decision.** Run online. Implement authorize start (mandatory), CDR receive (mandatory), remote start/stop (mandatory). Do not push authentication data in the pilot.

**Consequences.** The authorize endpoint must be highly available and fast; an unreachable eMSP is treated as NotAuthorized by Hubject. Offline push stays a fallback option (RH-HUBJECT-AUTH-007).

**Sources.** OICP 2.3 EMP info text (online vs offline EMP), eRoamingAuthorizeStart description.

**Facts added after the deep runs (2026-10-24).** Online and Broadcast requests are off by default in the HBS portal; the authorize answer must arrive within 10 seconds; the HBS never resends failed CDRs, so a daily reconciliation job is part of the design (RH-HUBJECT-CDR-004). Sources: support.hubject.com articles 4403420365585 and 4403421095953.
