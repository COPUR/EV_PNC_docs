# What to update in the repos and the kanban

**Date:** 2026-10-26 · **Status:** list only. Nothing here was applied to the repos or to the board, except the draft pull request that adds the principles, stack and ADRs to `EV_PNC_docs`. The product owner accepts the ADRs on card X-01 first.

## 1. Repositories

| Repo | Change | Driven by |
|---|---|---|
| `EV_PNC_docs` | Add `docs/architecture/` (principles, stack) and ADR-0008 to 0015, which live under `docs/architecture/kafka-backend/adr/` until P0-02 moves the whole ADR series into one directory. Add `topics.csv` and `eventflow_check.py` under `tools/`. Add the loyalty and invoicing rows to `components.csv`. Put the relationship labels of stack §2.1 into the context map (P0-16). Rename P0-05 "ADR-001" to the next free number | all ADRs |
| `EV_PNC_infra-modules` | Modules: Strimzi operator, Kafka cluster with node pools, `KafkaTopic` and `KafkaUser` generated from `topics.csv`, Apicurio Registry. `templates/spring-service` and a small Python template. Reusable workflow steps: schema compatibility, topic manifest diff, `eventflow_check --strict`, licence scan, redelivery kit | 0009, 0010, 0014 |
| `EV_PNC_infra` | Kafka environment per stage, `KafkaUser` certificates in the key vault partitions, dashboards and alerts (URP, ISR shrinks, lag SLOs, publish lag, revocation time), restore test, preproduction idle-to-zero | 0009 |
| `EV_PNC_ocpi-model` | Avro event schemas for the 21 topics, `Money` and `EventTime` types, envelope header constants, Kotlin and Python codegen (M-01 already asks for both). Schema changes follow M-02 rules | 0010 |
| `EV_PNC_ocpi-emsp` | README: Kafka via the Modulith publication registry; single writer of six topics including session and CDR for all channels; ingest port for hub CDRs | 0008, 0010, 0011 |
| `EV_PNC_hub-gateway` | README: local read model from binding, contract, grant and policy topics; publishes status and authorization decisions; hub CDRs go to the ocpi-emsp ingest port | 0011, AP-5 |
| `EV_PNC_telemetry` | README line "Go, Redis, Kafka, TimescaleDB" becomes "Kotlin, Spring Boot, PostgreSQL with TimescaleDB and PostGIS, Redis-compatible cache, Kafka" if X-01 accepts it. Consumes five topics, owns one | 0012 |
| `EV_PNC_pilot-analytics` | Batch jobs reading 14 topics; union-find for EVSE identity (C-02, C-03) with an oracle test; same inputs give the same KPIs | 0015, DP-7 |
| `EV_PNC_simulator` | Redelivery and failure kit; header-printing debug consumer; hub mocks publish through the same envelope | 0011 |
| `EV_PNC_plugcharge` | Owns `contract-changed` and `vehicle-binding-changed`; no VIN or plate in payloads; recipient resolver API | 0013 |
| `EV_PNC_payments` | Owns `payment-state-changed`; one capture per `paymentId`; idempotent consumer of `cdr-received`; synchronous hold and redeem calls to loyalty | 0011 |
| `EV_PNC_pricing`, `EV_PNC_policy-engine` | Pricing consumes tariffs and publishes price sheets; policy publishes `policy-changed` | 0010 |
| `EV_PNC_planner` | Python outbox and envelope; DP per ADR-0015 with oracle test; consumes availability and price sheets; publishes trip state and arrivals; positions arrive over HTTP only | 0011, 0013, 0015 |
| `EV_PNC_api-gateway` | Spring Cloud Gateway (the one reactive component); push dispatcher is an open item | 0012 |
| `EV_PNC_mobile` | No Kafka. Generated clients only | 0012 |
| `EV_PNC_loyalty`, `EV_PNC_invoicing` | Create (card X-12). Kotlin, template-generated | 0014 |
| `EV_PnC_Consent_*` | `contracts`: Avro for `grant-changed`, `grant-event-logged` and `decision-logged` beside OpenAPI and JSON Schema. `registry` owns grants; `decision` owns decision logs; `audit` consumes. Quotas and ACLs on the shared cluster; `infra` reuses the Kafka modules | 0009, 0010 |
| `EV_PNC_national-data`, `EV_PNC_national-consent` | None. Their stack is for the adopting public bodies to choose | |

## 2. Existing cards to amend (add these acceptance criteria)

| Card | Add |
|---|---|
| P0-05 | Rename "ADR-001" to the next free ADR number |
| P0-16 | Relationship label for every context pair (stack §2.1); aggregate list (stack §2.2) |
| P1-01 | Schema compatibility gate, topic manifest diff, `eventflow_check --strict`, licence scan |
| P1-02 | Strimzi operator and Apicurio in the environment; Kafka version pinned |
| P1-03 | Kafka JMX metrics, consumer lag against each consumer's SLO, trace context in Kafka headers, runbook per alert |
| P1-05, P1-04, H-03, H-04 | Testcontainers Kafka in the E2E harness; simulators use the envelope |
| P1-07, P1-10 | Topic names, keys, outbox; `ocpi-emsp` is the single writer of session and CDR events; hub CDR ingest port |
| M-01, M-02 | Avro schemas in the model, `Money` and `EventTime`; schema changes need an ADR and semver bump |
| C-02, C-03 | EVSE identity by union-find with oracle test and a human sample of merges |
| C-14 | Jobs read topics in batch; replaying yesterday's inputs reproduces yesterday's KPIs |
| H-05 | Authorize answers from a local read model; with Kafka stopped it still answers |
| K-05, K-06, K-07 | Topics `grant-changed`, `grant-event-logged` (audit feed) and `decision-logged`; revocation-to-hub time as a metric (RC-REV-002) |
| P3-02 | ADR-0015: oracle test against brute force, benchmark gate, DP per family (the existing 2 s on 500 km stays) |
| L-04, L-05, V-04 | Idempotency key is `ce_id`; consume `payment-state-changed`, `cdr-received`, `trip-state-changed` |

## 3. New cards (12 cards, 38 points, file `kanban/ev_pnc_backlog_v2_kafka_additions.csv`)

Same columns as the loyalty additions file, epics included.

| Id | Card | Iter. | Pts |
|---|---|---|---|
| X-01 | Accept ADRs and principles; decide telemetry runtime | I3 | 2 |
| X-02 | Spike: Kafka on Strimzi with failure drills | I3 | 5 |
| X-03 | Registry and first three schemas for P1-07 | I3 | 3 |
| X-04 | Topic catalogue as code and CI checks | later | 3 |
| X-05 | Golden-path Spring service template | later | 5 |
| X-06 | Python template for the planner | later | 3 |
| X-07 | Redelivery and failure kit | later | 3 |
| X-08 | hub-gateway read model and latency budget test | later | 5 |
| X-09 | Event privacy lint and erasure drill with the DPO | later | 3 |
| X-10 | Baseline load test and sizing | later | 3 |
| X-11 | Sustainability proxy metrics | later | 2 |
| X-12 | Create the loyalty and invoicing repos | later | 1 |

## 4. The wartime rule

The board says "no new card without dropping one" until the 7 December gate, I2 already carries 93 points against 36 in I1, and I2 and I3 each allow at most six PO gates (I2 has six, I3 has five).

- Put only **X-01, X-02 and X-03 (10 points)** in I3. P1-07 is already in I3 and needs Kafka and schemas, so the work is not extra, only visible. X-01 makes I3 six gates.
- Everything else is `it:later` (after the gate).
- To keep the rule, defer 10 points of I3. My suggestion, your call: A-01 contradiction register (2), B-02 EPDK and e-Devlet one sheet (2), P0-13 business model (3), N-01 EPDK unknowns (3, enabler track capped by N-08).
- None of the Kafka work is needed for K1 to K9 on 7 December. If capacity is short, ADR-0008's fallback keeps the pilot moving without it.

## 5. Open items I could not settle

| Item | Who | Blocks |
|---|---|---|
| Telemetry runtime, Go or Kotlin | Product owner (X-01) | Telemetry code after C-01 |
| Hosting provider in a Turkey region, managed Kafka there | Product owner, DevOps | Cluster sizing, DR |
| Who owns the push-notification dispatcher | Architect | `bonus-earned` and `invoice-state-changed` consumers |
| Invoice issuer model (V-01) and whether bonus is a discount | Product owner, tax adviser | Invoice event payload |
| Whether the consent family shares the cluster or has its own | Architect | Quotas, ACLs, SLO class |
| Date and retention for erasure lag | DPO, counsel | ADR-0013 numbers |
