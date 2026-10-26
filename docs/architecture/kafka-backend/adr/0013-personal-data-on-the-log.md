# ADR-0013: Personal data on the log: classes, what may be published, erasure

**Status:** proposed; the DPO and counsel review it (cards X-09, K-01, TR-05) · **Date:** 2026-10-26

**Context.** Kafka topics are replicated three times and, by design, hard to edit. KVKK sets duties on retention, access and transfer (Art. 9). The corridor spec reduces location traces to H3 resolution 8 after 90 days (CP-KPI-004). Receipts and the audit trail in the consent family are kept [10] years unless counsel says otherwise (RC-NFR-002), and that store is the record, not Kafka. Vehicle identity carries VIN and registration data, owner data and payment links, some of which must never be broadcast.

**Options.** (A) Allow personal data on restricted topics and encrypt. (B) Keep personal data out of events entirely and pass references. (C) Allow it with crypto-shredding for erasure.

**Decision.** Option B by default, C as an exception by ADR.
1. **Classes** for every dataset: `public`, `pseudonymous`, `personal`, `restricted` (payment, ownership, consent evidence). Only `public` and `pseudonymous` may appear on a topic.
2. **Pseudonymous is still personal data** under KVKK and GDPR. It lowers exposure; it does not remove the duty to have a basis, a retention rule and an access rule.
3. **Never on Kafka:** VIN, plate, national ID or tax number, phone, e-mail, name, address, card number, IBAN, registration-document images, raw location traces, OBD2 data, free text typed by a person.
4. **References:** `driverRef` and `vehicleRef` are random identifiers minted by the owning service at registration. They are not derived from a phone number, VIN or plate. Resolving one is an API call under authorization. The invoice recipient is resolved by the recipient resolver at issue time (owner on the session date), never from a plate alone.
5. **Keys** are never personal identifiers; the checker rejects them.
6. **Retention:** volume 7 d, business facts 30 d, state topics compacted. Longer retention lives in the owner's store with its own lifecycle.
7. **Erasure:** delete the mapping (`driverRef` to person) in the owning service; the log then holds unlinkable data. For compacted state topics also publish a tombstone; set `segment.ms` 1 d and `delete.retention.ms` 1 d so compaction removes it in about [3] days. Rehearse in the erasure drill.
8. **Location:** positions go to `planner` over HTTP, are stored there with the 90-day reduction, and never reach a topic. Only `arrival-observed` (pseudonymous trip, EVSE) and trip state do.
9. **Logs and traces:** no personal data; trace ids and `correlationid` only.
10. **Transfers:** hub-bound data leaves through `hub-gateway` after the consent decision (RC-GATE-001..004), under the standard-contract basis counsel confirms (TR-05). Kafka itself stays in Türkiye.

**Consequences.**
- Services need an extra call to resolve references; analytics works on references and pseudonymous trips, which is what the KPIs need.
- The schema linter reads a `pii` tag on fields and fails the build. The catalogue checker fails on a non-allowed class or a personal key.
- If a future payload really needs personal data, write an ADR choosing option C: per-subject keys in the vault, with the key deletion as the erasure.
- The platform data inventory (P0-17) records each topic with its class and expiry.

**Sources.** apache-kafka (01c compaction and tombstones, 01d security); microservices-and-ddd (08d deleting data); aws-waf-sustainability (SUS04-BP01, BP03); `corridor-pilot/spec.md` CP-KPI-004; `roaming-consent/spec.md` RC-NFR-002, RC-GATE-*; `engineering-briefing/loyalty-invoicing/README.md`.
