# What to update in the repos and the kanban

**Version:** 0.2 (audit 2026-10-26) · **Date:** 2026-10-26 · **Status:** list only. Nothing here was applied to the repos or to the board, except the draft pull request that adds the principles, stack and ADRs to `EV_PNC_docs`. The product owner accepts the ADRs on card X-01 first.

## 1. Repositories

| Repo | Change | Driven by |
|---|---|---|
| `EV_PNC_docs` | Add `docs/architecture/` (principles, stack) and ADR-0008 to 0015, which live under `docs/architecture/kafka-backend/adr/` until P0-02 moves the whole ADR series into `docs/adr/`. Add `topics.csv` and `eventflow_check.py` under `tools/`. Add the loyalty and invoicing rows to `components.csv`. Put the relationship labels of stack §2.1 into the context map (P0-16). Rename P0-05 "ADR-001" to ADR-0016 and reserve ADR-0017 for V-01 (invoice issuer). P0-02 then keeps the whole series in `docs/adr/` with an index: 0001 to 0006 from `roaming-hubs/specs/adr/`, 0007 from `consent-boundary-review.md` §8, 0008 to 0015 from here | all ADRs |
| `EV_PNC_infra-modules` | Modules: Strimzi operator, Kafka cluster with node pools, `KafkaTopic` and `KafkaUser` generated from `topics.csv`, Apicurio Registry. `templates/spring-service` and a small Python template. Reusable workflow steps: schema compatibility, topic manifest diff, `eventflow_check --strict`, licence scan, redelivery kit | 0009, 0010, 0014 |
| `EV_PNC_infra` | Kafka environment per stage, `KafkaUser` certificates in the key vault partitions, dashboards and alerts (URP, ISR shrinks, lag SLOs, publish lag, revocation time), restore test, preproduction idle-to-zero | 0009 |
| `EV_PNC_ocpi-model` | Avro event schemas for the 22 topics, `Money` and `EventTime` types, envelope header constants, Java and Python codegen (M-01 already asks for both). Schema changes follow M-02 rules | 0010 |
| `EV_PNC_ocpi-emsp` | README: "Kotlin and Spring Boot 3" becomes "Java and Spring Boot 4.x" (ADR-0012); Kafka via the Modulith publication registry; single writer of six topics including session and CDR for all channels; ingest port for hub CDRs; consumes grant, policy and contract changes so revoked grants and bindings invalidate tokens at CPOs | 0008, 0010, 0011, 0012 |
| `EV_PNC_hub-gateway` | README: local read model from binding, contract, grant and policy topics; publishes status and authorization decisions; hub CDRs go to the ocpi-emsp ingest port | 0011, AP-5 |
| `EV_PNC_telemetry` | Stays Go (ADR-0012 revision 0.2; C-01 is Go in PR #2). README line becomes "Go, PostgreSQL with TimescaleDB and PostGIS, Redis-compatible cache, Kafka"; outbox table, header names and redelivery kit match the JVM template through the shared contract test (X-06). Consumes five topics, owns one | 0012 |
| `EV_PNC_pilot-analytics` | Batch jobs reading 14 topics; union-find for EVSE identity (C-02, C-03) with an oracle test; same inputs give the same KPIs | 0015, DP-7 |
| `EV_PNC_simulator` | Redelivery and failure kit; header-printing debug consumer; hub mocks publish through the same envelope | 0011 |
| `EV_PNC_plugcharge` | Owns `contract-changed` and `vehicle-binding-changed`; no VIN or plate in payloads; recipient resolver API | 0013 |
| `EV_PNC_payments` | Owns `payment-state-changed`; one capture per `paymentId`; idempotent consumer of `cdr-received`; synchronous hold and redeem calls to loyalty | 0011 |
| `EV_PNC_pricing`, `EV_PNC_policy-engine` | Pricing consumes tariffs and publishes price sheets; policy publishes `policy-changed` | 0010 |
| `EV_PNC_planner` | Python outbox and envelope; DP per ADR-0015 with oracle test; consumes availability and price sheets; publishes trip state and arrivals; positions arrive over HTTP only | 0011, 0013, 0015 |
| `EV_PNC_api-gateway` | Spring Cloud Gateway (the one reactive component); push dispatcher is an open item | 0012 |
| `EV_PNC_mobile` | No Kafka. Generated clients only | 0012 |
| `EV_PNC_loyalty`, `EV_PNC_invoicing` | Create (card X-12). Java, template-generated. The customer-profile module lives in `loyalty`. `invoicing` consumes `cdr-received` and `payment-state-changed` | 0011, 0014 |
| `EV_PnC_Consent_*` | `contracts`: Avro for `grant-changed`, `grant-event-logged` and `decision-logged` beside OpenAPI and JSON Schema. `registry` owns grants, keyed by `grantId`; `decision` owns decision logs; `audit` consumes. `edevlet-bridge` becomes the one e-Devlet client for all six consent flows (repo-plan v2 amendment 2, widened) and publishes `ev.edevlet.upstream-grant-changed.v1`. Quotas and ACLs on the shared cluster; `infra` reuses the Kafka modules | 0009, 0010 |
| `EV_PNC_national-data`, `EV_PNC_national-consent` | None. Their stack is for the adopting public bodies to choose | |

## 2. Existing cards to amend (add these acceptance criteria)

| Card | Add |
|---|---|
| P0-05 | Rename "ADR-001" to ADR-0016 |
| P0-16 | Relationship label for every context pair (stack §2.1); aggregate list (stack §2.2); name the owner of the driver account and `driverRef` (ADR-0013 item 4) |
| P1-01 | Schema compatibility gate, topic manifest diff, `eventflow_check --strict`, licence scan |
| P1-02 | Strimzi operator and Apicurio in the environment; Kafka version pinned |
| P1-03 | Kafka JMX metrics, consumer lag against each consumer's SLO, trace context in Kafka headers, runbook per alert |
| P1-05, P1-04, H-03, H-04 | Testcontainers Kafka in the E2E harness; simulators use the envelope |
| P1-07 | Replace "change events on Kafka" with "change events written to the outbox table; the relay to Kafka is switched on after X-02", so P1-07 does not wait for the cluster |
| P1-07, P1-10 | Topic names, keys, outbox; `ocpi-emsp` is the single writer of session and CDR events; hub CDR ingest port |
| M-01, M-02 | Avro schemas in the model, `Money` and `EventTime`; schema changes need an ADR and semver bump |
| C-02, C-03 | EVSE identity by union-find with oracle test and a human sample of merges |
| C-14 | Jobs read topics in batch; replaying yesterday's inputs reproduces yesterday's KPIs |
| H-05 | Authorize answers from a local read model; with Kafka stopped it still answers |
| K-05, K-06, K-07 | Topics `grant-changed`, `grant-event-logged` (audit feed) and `decision-logged`; revocation-to-hub time as a metric (RC-REV-002) |
| P3-02 | ADR-0015: oracle test against brute force, benchmark gate, DP per family (the existing 2 s on 500 km stays) |
| L-04, L-05 | Idempotency key is `ce_id`; consume `payment-state-changed`, `cdr-received`, `trip-state-changed` |
| V-04 | Consume `cdr-received` and `payment-state-changed`; issue once both have arrived for the `paymentId` |
| K-07, K-17 | `grant-changed` keyed by `grantId`; tombstone every grant of an erased driver; K-17 later reads `ev.edevlet.upstream-grant-changed.v1` |
| C-02 | Go stays; the Kafka consumer follows the shared contract test (X-06) |

## 3. New cards (12 cards, 38 points, file `kanban/ev_pnc_backlog_v2_kafka_additions.csv`)

Same columns as the loyalty additions file, epics included.

| Id | Card | Iter. | Pts |
|---|---|---|---|
| X-01 | Accept ADRs and principles; decide telemetry runtime | I3 | 2 |
| X-02 | Spike: Kafka on Strimzi with failure drills | I4 (was I3) | 5 |
| X-03 | Registry and first three schemas for P1-07 | I4 (was I3) | 3 |
| X-04 | Topic catalogue as code and CI checks | later | 3 |
| X-05 | Golden-path Spring service template | later | 5 |
| X-06 | Python template for the planner | later | 3 |
| X-07 | Redelivery and failure kit | later | 3 |
| X-08 | hub-gateway read model and latency budget test | later | 5 |
| X-09 | Event privacy lint and erasure drill with the DPO | later | 3 |
| X-10 | Baseline load test and sizing | later | 3 |
| X-11 | Sustainability proxy metrics | later | 2 |
| X-12 | Create the loyalty and invoicing repos | later | 1 |

## 4. The wartime rule (revised in 0.2)

The board says "no new card without dropping one" until the 7 December gate. I3 (23 Nov to 6 Dec) carries 54 points and five PO-action gates, against a limit of six.

- **Put only X-01 (2 points) in I3.** It makes I3 six PO gates, the limit.
- **Move X-02 and X-03 to I4** (from 7 Dec). No K1 to K9 criterion needs Kafka, and P1-07 can write its change events to the outbox table now and switch the relay on after X-02 (amendment above). Rows written before X-03 fixes the schemas and header names are discarded, not relayed, when the relay starts; P1-07 records that in its acceptance criteria. v0.1 put both spikes in I3.
- **Defer A-01** (contradiction register, 2 points) to keep the rule.
- **Do not defer P0-13.** v0.1 suggested it, but P0-13 checks hub fees against K6 and the guest margin against K8, which the gate decision G-04 needs. B-02 and N-01 also stay; they were only needed to free the 10 points that v0.1 asked for.
- ADR-0008's fallback deadline moves from 7 Dec to the end of I4 (20 Dec) accordingly.

## 5. Open items I could not settle

| Item | Who | Blocks |
|---|---|---|
| Telemetry runtime: keep Go (recommended in 0.2, since C-01 is Go) or move to Java | Product owner (X-01) | C-02 and later telemetry cards |
| Hosting provider in a Turkey region, managed Kafka there | Product owner, DevOps | Cluster sizing, DR |
| Who owns the push-notification dispatcher | Architect | `bonus-earned` and `invoice-state-changed` consumers |
| Invoice issuer model (V-01) and whether bonus is a discount | Product owner, tax adviser | Invoice event payload |
| Whether the consent family shares the cluster or has its own | Architect | Quotas, ACLs, SLO class |
| Date and retention for erasure lag | DPO, counsel | ADR-0013 numbers |
| Who owns the driver account and mints `driverRef` | Architect (P0-16) | ADR-0013 erasure path |
| Widen `edevlet-bridge` to a generic client for all six consent flows (repo-plan v2 amendment 2) | Product owner, Architect | Wave-3 bridge scope, F1 and F3 to F6 |
