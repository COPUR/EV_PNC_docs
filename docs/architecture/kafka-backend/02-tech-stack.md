# EV_PNC technology stack with Kafka on the backend

**Version:** 0.1 · **Date:** 2026-10-26 · **Status:** proposed · **Principles:** `01-principles.md` · **Decisions:** `adr/0008` to `adr/0015`
**Inputs:** repo-plan v2 and the consent family, the engineering briefing (C4 containers, sequences, state tables, design review), `corridor-pilot/` (CP-*), `national-hub-service/` (NHS-*), `roaming-consent/` (RC-*), kanban v2.
**Confidence labels:** F = from a project file or a skill chapter, I = my inference or estimate, U = unknown. Numbers in [brackets] are proposals, as in the specs.

## 1. The stack in one table

| Layer | Choice | Why in one line | Not chosen |
|---|---|---|---|
| Event backbone | Apache Kafka 4.x in KRaft mode, run by the Strimzi operator on Kubernetes (ADR-0008, 0009) | The log gives replay, fan-out and a revocation path; no ZooKeeper to run | Postgres-only messaging, RabbitMQ/SQS, Kafka as record with event sourcing |
| Cluster shape | 3 brokers plus 3 dedicated controllers, RF 3, `min.insync.replicas` 2 | Durability needs three copies (K 05a); Kafka's KRaft docs advise against combined controller+broker mode in critical deployments (I, from memory) | Single broker, combined mode |
| Event contracts | Avro schemas in Apicurio Registry, CloudEvents-style envelope in headers, BACKWARD_TRANSITIVE (ADR-0010) | Evolvable, replay-safe, Apache-2.0 | Confluent Schema Registry (Community licence), JSON without a registry |
| Publishing | Transactional outbox: Spring Modulith event publication registry with Kafka externalisation; Debezium outbox later (ADR-0011) | No dual writes, no custom framework | Direct `KafkaTemplate.send` after commit |
| Consuming | Spring for Apache Kafka, manual ack after processing, idempotent by a unique key, retry topics then a per-group dead-letter topic | At-least-once made safe | Auto-commit, blocking retries |
| Stream processing | None at day one. Kafka Streams only for a windowed or stateful join with a written reason | Plain consumers plus Postgres upserts are simpler to run | ksqlDB, Flink |
| Service runtime | Kotlin, a supported JDK LTS, the currently supported Spring Boot line, Spring MVC with virtual threads (ADR-0012) | One paved road | WebFlux everywhere |
| Edge | `api-gateway` on Spring Cloud Gateway (reactive), OIDC/JWT, rate limits | The one place where many concurrent I/O-bound calls justify reactive | Custom servlet gateway |
| Persistence | PostgreSQL, one schema per service, Flyway; Spring Data JDBC for aggregates, `JdbcClient` or jOOQ for read models | Aggregate-oriented, no lazy-loading traps (SB 06b) | JPA by default, MySQL |
| Time series | TimescaleDB on PostgreSQL for telemetry history | Already in the telemetry README; two seasons of history (CP-DATA-002) | A second database engine |
| Geo | PostGIS for corridor geometry and "within 2 km"; H3 resolution 8 for location privacy | Spec asks for both (CP-GEO-002, CP-KPI-004) | Hand-written k-d tree |
| Cache | Redis-compatible cache (Valkey if self-hosted, licence check) plus Caffeine in the process | Only data that can be rebuilt | Cache as a store |
| Planner | Python, FastAPI, NumPy; the optimiser is a layered-DAG dynamic programme (ADR-0015); OR-Tools optional | Fast model iteration; the DP does not need a solver | Rewrite in Kotlin now |
| Mobile | Swift, Kotlin native, CarPlay and Android Auto, generated OpenAPI clients; no Kafka on devices | Unchanged | Cross-platform rewrite |
| Delivery | Layered non-root images (buildpacks), Argo CD GitOps, Terraform and Helm in `infra-modules`, GitHub Actions | Build once, promote | Hand-run deploys |
| Observability | OpenTelemetry to Prometheus, Grafana, Loki, Tempo (or the provider's equivalent); Kafka JMX exporter | Open standard | Vendor agent in code |
| Hosting | Kubernetes in a Turkey region (card P1-02); provider not chosen | Residency of consent and personal data (RC-NFR-002) | Hosting abroad before counsel answers TR-05 |

The project topic lists a payments-gateway reference stack (Java, Node.js, MySQL, AWS, WooCommerce plugins). Where it conflicts with the repo plan (Kotlin, PostgreSQL, Turkey hosting, no merchant plugins) I followed the repo plan. Node.js and MySQL are not used. Its AWS pillars and the 12 factors are used as review lenses.

## 2. Application architecture

### 2.1 Context map (proposal for P0-16)

| From | To | Relationship | Notes |
|---|---|---|---|
| `ocpi-emsp` | CPOs | Open Host Service, Published Language (OCPI 2.2.1 out, 2.3.0 model in) | Conformist to the standard |
| `hub-gateway` | Hubject, GIREVE, e-clearing.net | Anticorruption layer per hub (ADR-0001) | Hub rules as data |
| all services | `ocpi-model` | Published Language with shared-kernel governance | ADR plus semver for any change (M-02) |
| platform | Consent family | Customer-Supplier; decision SDK and events | Consumer-driven tests in the supplier's CI |
| `payments` | PSP, Masterpass | Anticorruption layer | PSP idempotency key = `paymentId` |
| `invoicing` | GİB private integrator | Anticorruption layer | Issuer model open (V-01) |
| `planner` | map, traffic, weather, ferry, flight, tolls | One port and adapter per provider | Open-Meteo free tier is non-commercial |
| `loyalty`, `pilot-analytics` | event producers | Conformist to the published events | Read-only consumers |
| Consent bridge | e-Devlet | Anticorruption layer | Parked |

### 2.2 Aggregates and owners

| Service | Aggregates (one transaction each) | Process manager or saga |
|---|---|---|
| `plugcharge` (incl. vehicle-identity) | VehicleBinding, Contract (EMAID), OwnerRecord | |
| `payments` | Payment, PaymentLink | Payment: authorise, session, CDR, capture, refund (orchestrated) |
| `loyalty` | LedgerAccount (append-only entries), EarnRules | |
| `invoicing` | Invoice | Invoice: waits for capture and final CDR, then issues |
| `planner` | Trip (the process manager itself) | Trip STT |
| `ocpi-emsp` | Token, Session, Cdr | |
| `policy-engine`, `pricing` | DriverPolicy, PriceSheet | |
| Consent family | Grant | Revocation propagation |

Rule: orchestrate where one team owns the flow and failure handling matters (money, trips). Choreograph where consumers are independent (ledger earn, analytics, notifications).

## 3. Kafka design

### 3.1 Cluster and defaults (ADR-0009)

| Item | Value | Source |
|---|---|---|
| Version | Kafka 4.x, KRaft only. Pin the exact version in `infra-modules` | F: ZooKeeper removed in 4.x (apache-kafka skill) |
| Operator | Strimzi: `Kafka`, `KafkaNodePool`, `KafkaTopic`, `KafkaUser` as git-managed resources | I |
| Pilot nodes | 3 brokers [2 vCPU, 8 GB, 100 GB SSD] and 3 controllers [1 vCPU, 2 GB, 20 GB] | I, sized in §6 |
| Racks | `broker.rack` per failure domain (node or zone) | F: K 05a |
| Durability profile (all topics) | RF 3, `min.insync.replicas` 2, `acks=all`, `enable.idempotence=true`, `unclean.leader.election.enable=false`, `auto.create.topics.enable=false` | F: K 05a, 06a |
| Internal topics | RF 3, including `__consumer_offsets` and any Streams changelog | F: K 05a |
| Compression | `lz4` on the producer, same codec on the topic | F: K 05a; Intel measured gzip better on P99 (04a); `zstd` not covered by the sources, benchmark if wanted |
| Batching | `linger.ms` 20 and `batch.size` 128 KB on volume topics only; defaults elsewhere | F: K 05a ranges |
| Consumers | `enable.auto.commit=false`, ack after processing, `max.poll.interval.ms` above the worst-case processing time, static membership (`group.instance.id`), cooperative sticky assignor | F: K 01b, 03c |
| Identity | TLS 1.3 and mTLS client certificates through `KafkaUser`; ACLs: WRITE only for the owner; READ per consumer group | F: K 01d, I |
| Disks | Encrypted volumes (Kafka has no encryption at rest) | F: K 01d |
| Retention defaults | Volume 7 d, business facts 30 d, state topics compacted with `segment.ms` 1 d, `max.compaction.lag.ms` [1 d] and `delete.retention.ms` 1 d so a tombstone takes effect within about [3] days on any traffic | I from K 01c |
| DR at national scale | Second Turkey DC, MirrorMaker 2 active-passive, offsets synced; RPO 5 min and RTO 1 h as in the NHS plan | F: NHS HLD §6, K 02c |

One durability profile for the whole cluster, with only batching and retention differing by class. At this volume the cost of `acks=all` is invisible, and a single profile removes a class of mistakes.

### 3.2 Topic classes

| Class | Goal in order | Topics | Settings beyond the profile |
|---|---|---|---|
| A critical | durability, then latency | payments, CDRs, grants, binding, contract, trips, ledger, invoice, authorization, consent decisions | defaults; the state topics among them (grants, binding, contract) are compacted with a required key |
| B state | durability, rebuildability | location, tariff, token, policy, price sheet, availability | `cleanup.policy=compact`, key required |
| C volume | throughput | EVSE status, session updates, arrivals | lz4, linger 20 ms, retention 7 d |

### 3.3 Naming, keys, partitions, envelope

- **Name:** `ev.<context>.<fact-or-state>.v<N>`, past tense (`cdr-received`, `grant-changed`). The context is the owner's. A breaking change makes `.v2` and keeps `.v1` until the last consumer moves (dual-schema window).
- **Key:** the entity whose events must stay in order. `paymentId` links session, CDR, payment, ledger and invoice, because it is the OCPI `authorization_reference`. Never a personal identifier, never an operator (a few big CPOs would make hot partitions).
- **Partitions:** 6 for low volume, 12 for entity-keyed volume, 24 only at national scale (the consent plan also uses 6 and 24). Partition counts only grow and growth re-maps keys, so scale by a new topic version, not by expansion.
- **Envelope** (headers, so the payload stays the pure fact): `ce_id` (the idempotency key), `ce_type`, `ce_source`, `ce_time`, `ce_subject`, `traceparent`, `correlationid` (`paymentId` or `tripId`), `dataclass` (`public` or `pseudonymous`), `expires` (time after which a consumer drops the event, from the design review's re-plan fix).
- **Dead letters:** `<topic>.<consumer-group>.dlt`, one per consumer group, with headers for the reason (`invalid`, `exhausted`) and the original topic, partition and offset. A DLT message raises an alarm.

### 3.4 Topic catalogue (20 topics, generated from `tools/topics.csv`)

| Topic | Owner (single writer) | Key | Part. | Retention | Class | Data | Consumers |
|---|---|---|---|---|---|---|---|
| `ev.roaming.location-changed.v1` | ocpi-emsp | locationUid | 6 | compacted | B | public | telemetry, pilot-analytics |
| `ev.roaming.tariff-changed.v1` | ocpi-emsp | tariffUid | 6 | compacted | B | public | pricing, pilot-analytics |
| `ev.roaming.evse-status-changed.v1` | ocpi-emsp | evseUid | 12 | 7d | C | public | telemetry |
| `ev.roaming.token-changed.v1` | ocpi-emsp | tokenUid | 6 | compacted | B | pseudonymous | hub-gateway |
| `ev.roaming.session-updated.v1` | ocpi-emsp | paymentId | 12 | 7d | C | pseudonymous | telemetry, pilot-analytics |
| `ev.roaming.cdr-received.v1` | ocpi-emsp | paymentId | 12 | 30d | A | pseudonymous | payments, loyalty, pilot-analytics |
| `ev.hub.evse-status-changed.v1` | hub-gateway | evseUid | 12 | 7d | C | public | telemetry |
| `ev.hub.authorization-decided.v1` | hub-gateway | attemptId | 12 | 30d | A | pseudonymous | pilot-analytics |
| `ev.pnc.contract-changed.v1` | plugcharge | emaid | 6 | compacted | A | pseudonymous | hub-gateway, pilot-analytics |
| `ev.identity.vehicle-binding-changed.v1` | plugcharge | vehicleRef | 6 | compacted | A | pseudonymous | hub-gateway, pilot-analytics |
| `ev.consent.grant-changed.v1` | consent-registry | driverRef | 6 | compacted | A | pseudonymous | consent-decision, ocpi-emsp, hub-gateway, plugcharge, consent-audit |
| `ev.consent.decision-logged.v1` | consent-decision | decisionId | 6 | 30d | A | pseudonymous | consent-audit |
| `ev.policy.policy-changed.v1` | policy-engine | driverRef | 6 | compacted | B | pseudonymous | hub-gateway, ocpi-emsp |
| `ev.payment.payment-state-changed.v1` | payments | paymentId | 12 | 30d | A | pseudonymous | loyalty, invoicing, pilot-analytics |
| `ev.pricing.price-sheet-published.v1` | pricing | priceSheetId | 6 | compacted | B | public | planner, pilot-analytics |
| `ev.trip.trip-state-changed.v1` | planner | tripId | 12 | 30d | A | pseudonymous | loyalty, pilot-analytics |
| `ev.trip.arrival-observed.v1` | planner | evseUid | 12 | 7d | C | pseudonymous | telemetry, pilot-analytics |
| `ev.telemetry.evse-availability-changed.v1` | telemetry | evseUid | 12 | compacted | B | public | planner, pilot-analytics |
| `ev.loyalty.bonus-earned.v1` | loyalty | accountId | 6 | 7d | A | pseudonymous | api-gateway, pilot-analytics |
| `ev.invoice.invoice-state-changed.v1` | invoicing | paymentId | 6 | 30d | A | pseudonymous | api-gateway, pilot-analytics |

Notes on the catalogue:
- It is a draft v0.1 derived from the sequences in the briefing and the specs. The Architect agent confirms owners and consumers on X-04.
- `ev.policy.policy-changed.v1` is new. The deck calls `policy-engine` synchronously from `hub-gateway`; an event-fed lookup keeps that call out of the 10 s authorize window.
- Raw location traces never go on Kafka. The app sends positions to `planner` over HTTP, and only `arrival-observed` and `trip-state-changed` leave it.
- `ev.consent.decision-logged.v1` keeps the 30-day business-fact retention (DP-6) because the audit store is filled from it: a `consent-audit` outage shorter than 30 days loses nothing, and a consumer-lag alert fires after 1 day. `ev.loyalty.bonus-earned.v1` stays at 7 days because it is only a notification; the loyalty ledger is the record.
- `ev.loyalty.bonus-earned.v1` and `ev.invoice.invoice-state-changed.v1` are consumed by `api-gateway` for push messages. Who owns the push dispatcher is open.
- `pilot-analytics` reads 14 topics and writes none. That is intended: it is a sink, and its KPI jobs are batch.

### 3.5 Checks that run today

`tools/eventflow_check.py topics.csv --strict` enforces seven rules (one writer, known consumers, key present and not personal, partition counts, retention, data class, event loops). Result on the catalogue: all rules pass, with one declared loop, `planner` and `telemetry` (arrivals feed occupancy profiles, availability feeds the planner; both sides work without the other's data, so it is a feedback loop and not a startup dependency). A trial run with `plugcharge` also consuming `ev.hub.authorization-decided.v1` fails with an undeclared loop `hub-gateway` <-> `plugcharge`, so the check does catch a real cycle. Output is in `evidence/`.

## 4. Algorithms and data structures by component

Method: pick by the operation that must be cheap, state the input size, and audit any library code. The TheAlgorithms-Java library is teaching code with verified high-severity bugs (k-d tree pruning and delete, Johnson dropping zero-weight edges, `AStar` that enumerates paths); it is not a dependency. Liang's implementations are used to reason about costs, not to ship.

| Component | Problem | Structure and algorithm | Cost (I) | Why not the alternative |
|---|---|---|---|---|
| planner | Choose charging stops: minimise drive + charge + expected queue, with reserve SoC | Layered DAG along the route km, DP over (site, leave-SoC bucket); candidate charge-to levels limited to "needed to reach the next K sites" and a cap; run once per family (M, A1..A4) | about 10⁶ relaxations per family [N≈200 sites, L≈50 buckets, K≈10] | Dijkstra is unnecessary on a DAG; Bellman-Ford has no negative edges; OR-Tools solves a harder problem than this |
| planner | Re-plan mid-trip | Same DP from the current position; A* only if a heuristic is admissible (remaining km / max speed) with a closed set | less than the full plan | The library `AStar` is exponential |
| planner | Queue time is time-dependent | Allow waiting at a site, which keeps the travel-time function FIFO, so label-setting stays valid (I, standard result) | | |
| planner | Prove the DP right | Brute-force enumeration of stop subsets on small corridors as an oracle test | | Green unit tests alone were wrong in the library notes |
| telemetry, planner | EVSEs within 2 km of a corridor, nearest EVSE | PostGIS GiST index; in memory a JTS STRtree | log-time lookup | The library `KDTree` prunes wrongly |
| telemetry, analytics | Location privacy | H3 resolution 8 cells | | |
| pilot-analytics | K1 count: the same EVSE appears in EPDK, Şarj@TR, OCPI and Hubject | Blocking on H3 cell and normalised operator and connector, then union-find (union by rank, path compression) to merge matches | near-linear | Pairwise comparison is quadratic; a wrong merge inflates K1, so keep an oracle test and a human sample |
| all | Idempotent consumer | Unique index on (consumer, event id) with a cleanup job | one indexed insert per event | A Bloom filter only as a pre-check, never as the authority (false positives would drop real events) |
| hub-gateway, consent-decision | Read model and decision cache | Hash map in process (Caffeine, W-TinyLFU) plus Redis-compatible second level, invalidated by grant and policy events | O(1) expected | Load factor and `hashCode`/`equals` on value objects must be right (Liang ch27) |
| loyalty | Spend the earliest-expiring points first | Entries ordered by expiry; a min-heap in the model, an index on (account, expires_at) in the database | O(log n) | A full scan per redemption |
| infra | Event-flow and dependency cycles | Tarjan strongly connected components on the service graph and on the component graph | linear | Manual review |
| infra | State machines (Binding, Link, Trip, Invoice) | Transition table as data; code and diagram checked against it | | Diagram-only specs drift |
| edge | Rate limit | Token bucket in the gateway, state in the cache | O(1) | |

Hash tables and B-trees already sit under PostgreSQL, Kafka's partitioner (murmur2 on the key) and the JDK. The one thing we must get right is the key: it fixes both ordering and the load spread.

Budgets: P3-02 already requires a 500 km route in under 2 s. Proposed addition: p95 re-plan within [1 s] on the five-family corridor, measured by the benchmark gate in ADR-0015.

## 5. Security and API notes

- Edge: the gateway terminates OIDC and passes a short-lived JWT; each owning service authorizes the object, not just the URL (IDOR). Spring Security 6 style, `SecurityFilterChain` bean, `denyAll()` last (SB 02c, 03b).
- Service to service: mTLS plus the JWT of the original caller or a service token. Hubs: mTLS and the key vault partitions in the plan (TR-17, TR-18).
- Kafka: one `KafkaUser` per service; no shared credentials; quotas on the producers that take outside input (`ocpi-emsp`, `hub-gateway`).
- REST error bodies come from a `@ControllerAdvice`; no stack traces; OpenAPI is the contract for mobile (generated clients).
- The consent decision point is not on Kafka for its answer, only for its inputs and its audit log.

## 6. Sizing (all I, derived from stated assumptions)

Assumptions: 1,000 EVSE in scope with two status channels and one change per 8 minutes (the NHS HLD uses the same rate); 500 sessions per day with 40 updates each; 500 trips per day with 33 events each; 5,000 drivers with 20 consent decisions per day; 1 KB per message (0.5 KB for decisions); retention as in the catalogue: status and sessions 7 days, trips and consent decisions 30 days.

| Flow | Messages/s (average) | Retained × RF 3 |
|---|---|---|
| EVSE status, both channels | 4.2 | 7.6 GB |
| Session updates | 0.23 | 0.4 GB |
| CDR, payment, invoice | 0.03 | 0.3 GB |
| Trip events and arrivals | 0.19 | 1.5 GB |
| Consent decisions | 1.2 | 4.5 GB |
| **Pilot total** | about 6 (peak at 10× about 60) | about 14 GB |
| National (50,000 sockets and 2 M decisions per day, from the NHS HLD) | about 127 | about 280 GB (decisions at 30 days add about 70 GB) |

The NHS plan allots 3 brokers of 4 vCPU, 16 GB and 500 GB for the national public side, which covers the national row. The pilot is about 6 messages per second, orders of magnitude below what a small broker serves, so **the cluster is sized for durability and operability, not throughput**. The 100 GB disks leave room for 30-day topics, broker restarts and a rebuild. X-10 replaces these estimates with a measured baseline.

## 7. Well-Architected sustainability review (SUS)

| Question | Finding | Action |
|---|---|---|
| SUS 1 Region | Residency fixes the choice first (Türkiye). Carbon data comes second and is unknown for the candidate providers | Ask each provider for energy and PUE figures on selection (P1-02) |
| SUS 2 Demand | Kafka already buffers: consumers work at their own pace, and KPI jobs run as scheduled batch off peak | Keep the KPI jobs batch; do not add always-on stream jobs without a reason |
| SUS 3 Software | Orphan topics and unused services are retired; async work is queued | `eventflow_check` flags orphans; review at each wave |
| SUS 4 Data | Classification, lifecycle and "fetch, don't copy" are in DP-5 to DP-7. Read models hold only the needed fields | Retention table in §3.1; audit data to cold storage after 13 months; no duplicate archives |
| SUS 5 Hardware | Right-size (pilot nodes small), multi-arch images. **Tension:** SUS05-BP03 prefers managed services, but residency and portability push us to run Kafka ourselves | Revisit if a Turkish provider offers managed Kafka with residency; the Kafka API keeps that open |
| SUS 6 Process | Cost and carbon share a proxy metric | CPU-seconds and GB stored per 1,000 sessions per service on the dashboard (X-11); non-production scales to zero outside test windows |

## 8. Inconsistencies found in the existing plan

1. **Missing repos.** Eight cards (L-04, L-05, L-07, L-12 and V-04 to V-07) point at `EV_PNC_loyalty` and `EV_PNC_invoicing`, which are not in the 19-repo plan or in `components.csv`. The packaging check with both added (`tools/components_v2_1.csv`) still has no cycle, 21 repos in all. Suggested card X-12.
2. **Telemetry runtime.** The README says Go; the rest of the platform is Kotlin. ADR-0012 proposes the JVM for one runtime less. Your decision.
3. **Vehicle identity** is a separate container in the deck and a module of `plugcharge` in the repo plan. This document follows the repo plan.
4. **ADR numbering.** P0-05 is titled "ADR-001" while the series runs ADR-0001 to ADR-0007. Rename it when it is written.
5. **Kafka in the national plan.** The NHS HLD names Kafka for the public side too; that cluster is the public bodies' to run, not ours. This stack covers the EV_PNC_ and Consent services only.

## 9. Limits

- Versions are not pinned. Kafka 4.x, the Spring Boot line and Modulith need a compatibility check in X-02 and X-05, and X-05 must confirm the chosen Spring Boot line is inside its open-source support window before ADR-0012 is accepted; I did not run them here.
- Apicurio's Confluent-compatible API and Spring Modulith's Kafka externalisation are from my knowledge, not from the skills; the spikes confirm them.
- Topic catalogue, sizes and budgets are estimates. Hub behaviour (Hubject's 10 s, GIREVE PNCP 1.2.0) is unconfirmed in the project files.
- I did not benchmark anything. The pilot load figures come from the spec assumptions above.
