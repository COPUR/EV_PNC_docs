# ADR-0010: Event contracts: Avro in Apicurio, headers envelope, naming, keys, single-writer ACLs

**Status:** proposed (accept on card X-01) · **Date:** 2026-10-26 · **Revision:** 0.2 (audit 2026-10-26: key rule for compacted topics, grant key, upstream e-Devlet topic)

**Context.** Events are the API between services and between agents building them. `ocpi-model` already holds "the canonical model, domain events and the error model". Consent contracts use OpenAPI, AsyncAPI and JSON Schema (receipts follow ISO/IEC TS 27560). Replay is a design goal, so new readers must read old data. The design review asked for correlation ids, expiry on re-plan events and invalid and dead-letter topics.

**Options for the payload format.**

| Option | For | Against |
|---|---|---|
| A Avro with a registry | Compact, strong evolution rules, the Kafka books' default, generated Kotlin classes | No native Swift/Kotlin story, but devices never read Kafka |
| B Protobuf with a registry | One IDL with gRPC; good codegen | Adds a second IDL because REST stays OpenAPI; evolution rules need more care |
| C JSON Schema | Already used for receipts | Larger, weaker enforcement, easy to drift |

**Decision.**
1. **Format:** Avro (option A) for Kafka events, defined in `ocpi-model`. OpenAPI stays the REST contract. JSON Schema stays for consent receipts. gRPC is used only where the consent HLD names it (the decision point), without making Protobuf the event format.
2. **Registry:** Apicurio Registry (Apache-2.0), with the Confluent-compatible API enabled so the standard serializers work. Confluent Schema Registry is not used because of its Community licence.
3. **Compatibility:** BACKWARD_TRANSITIVE on every subject. Breaking change: new topic `.v2`, both live until the last consumer moves, then `.v1` is archived.
4. **Naming:** `ev.<context>.<fact-or-state>.v<N>`, past tense. Dead letters: `<topic>.<consumer-group>.dlt`.
5. **Keys:** the entity whose order matters. `paymentId` (equal to the OCPI `authorization_reference`) links session, CDR, payment, ledger and invoice. Never a personal identifier or an operator. **On a compacted topic the key is the id of the aggregate whose full state the value carries.** Compaction keeps one record per key, so a parent id with many children loses all but the last child: `ev.consent.grant-changed.v1` is keyed by `grantId` (one grant per driver, hub and purpose), not by `driverRef`. A topic may use a person-level key only when the value is that person's full state (`policy-changed`), and the checker's rule R8 enforces that.
6. **Envelope in headers:** `ce_id` (idempotency key), `ce_type`, `ce_source`, `ce_time`, `ce_subject`, `traceparent`, `correlationid`, `dataclass`, `expires`.
7. **Partitions:** 6, 12 or 24; scale by a new topic version, never in place.
8. **Single writer:** the topic catalogue (`tools/topics.csv`) names one owner per topic; the operator grants WRITE only to that owner. Session and CDR events have one writer, `ocpi-emsp`, for all three channels.
9. **Catalogue as code:** `topics.csv` generates `KafkaTopic` and `KafkaUser` resources, and `eventflow_check.py --strict` runs in CI (eight rules, including undeclared event loops and person-level keys on compacted topics).
10. **Declared loop:** `planner` and `telemetry` form an event loop by design (arrivals in, availability out). Each side works without the other's events.
11. **Upstream e-Devlet grants** (planned, wave 3): `edevlet-bridge` alone talks to the state Mobility Consent Service (ADR-0007) and publishes `ev.edevlet.upstream-grant-changed.v1` with our own references. `consent-registry` turns roaming grants into registry grants through the ConsentSource port (K-17) and stays the single writer of `ev.consent.*`; `plugcharge` takes ownership and delegation grants. When the two sources disagree, the more restrictive wins.

**Consequences.**
- Schema changes are pull requests reviewed by consumer owners. A consumer-driven contract test per consumer runs in the producer's CI.
- Avro codegen is part of the `ocpi-model` build; its version bump rules (M-02) apply to schemas.
- The planner (Python) uses the same schemas through an Avro library and the same header names.
- Compatibility mode and Apicurio behaviour are checked in spike X-03 against a replay of recorded simulator traffic.
- Header-based envelope keeps payloads as pure facts; the cost is that tools must show headers when debugging. A debug consumer in the simulator prints them.

**Sources.** apache-kafka (01a, 01d, 03a); microservices-and-ddd (08d, 08c, 01b); `engineering-briefing/review/README.md`; `eventflow_check.py` and its output.
