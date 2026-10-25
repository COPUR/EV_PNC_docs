# ADR-0006: Guest (AD_HOC_USER) price = B2B cost + fixed margin + VAT, TL/kWh only

**Status:** accepted, conditional on TR-01 · **Date:** 2026-10-25

**Context.** Hubs pass only B2B tariffs to eMSPs (GIREVE B2B Regular; Hubject NGP, tax excluded, may contain time, parking and session fees). Secondary sources say Turkish B2C prices must be TL/kWh only, with no start or connection fee, and that price tiers may differ by about 25%. Most Didim sessions will be at CPOs reached bilaterally, not through hubs. Primary legal texts were not read.

**Decision.** For every channel (bilateral OCPI, Hubject NGP, GIREVE B2B Regular):

```
guest_price_TL_kWh = (B2B_energy_TL_kWh + non_energy_components_TL / reference_session_kWh) × (1 + margin) × (1 + VAT)
```

- Non-energy components are folded into kWh using one reference session profile per CPO ([__ kWh, __ min]) until pilot data exists.
- EUR tariffs are converted at a daily rate fixed at session start (source to confirm: TCMB or payment provider).
- Margin [%__] is set at the gate and must respect the tier limit (to verify). VAT is confirmed by accounting.
- The price shown to the driver and the CDR total use the same TL/kWh value.

**Condition and fallback (option E, agency model).** If the legal opinion (TR-01) says a non-CPO eMSP may not resell charging at its own price, the app shows the CPO's own B2C TL/kWh price and earns a commission from the CPO.

**Consequences.** One tariff-conversion component in the eMSP; the hub adapters only deliver B2B tariffs into the canonical model. Dynamic margins and flat list prices are out of the pilot.

**Sources.** deliverables/05-kararlar.md (Decision 3), deliverables/03-turkiye-todo.md (TR-01, TR-06, TR-07), deliverables/07-go-no-go.md (K4, K8).
