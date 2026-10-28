# EV_PNC architecture principles: Data, Application, Technology

**Version:** 0.2 (audit 2026-10-26, changes listed at the end) · **Date:** 2026-10-26 · **Status:** proposed; for acceptance by the product owner on card X-01 · **Scope:** the EV_PNC_ platform and, where they share the Kafka cluster, the EV_PnC_Consent_ services
**Frame:** TOGAF. The squad agents read BDAT as Business, Data, Application, Technology (an assumption, see `squad-agents-ev-pnc-squad`). Principles follow the TOGAF template: **Name, Statement, Rationale, Implications**, plus a **Check** (a fitness function that says where it runs), so a principle that cannot be tested stays a wish.
**Business principles** are not rewritten here. They already exist and these principles assume them: the platform is a neutral eMSP, not a CPO and not a payment institution; it is hub-ready and not hub-dependent; the pilot does not depend on state services (NHS-ADR-05); the guest price is B2B cost plus fixed margin plus VAT (ADR-0006).
**Sources:** apache-kafka, microservices-and-ddd (with evans-ddd), algorithms-data-structures (with the TheAlgorithms-Java and Liang libraries), java-spring-boot (with spring-boot-in-practice security/REST/reactive), aws-waf-sustainability, architecture-review. Tags such as (K 05a) point to the skill chapter.

A good principle is understandable, robust, complete, consistent and stable (TOGAF). Each one below was kept only if a team could break it by accident and a check could notice.

---

## Data principles

### DP-1 Own your data, one writer
- **Statement:** Every dataset has one owning service. Only the owner writes it, in its own schema or topic. Everyone else holds copies derived from events, or calls the owner's API.
- **Rationale:** Shared databases make a distributed monolith. A single writer gives one place for versioning and consistency (MS 08c) and matches the C4 rule "one schema per service, never shared".
- **Implications:** Credentials per service. Reporting reads events, never another service's tables. A topic's WRITE ACL belongs to its owner alone. Session and CDR events have one writer, `ocpi-emsp`, for all three channels (hub CDRs enter through an ingest port).
- **Check:** `eventflow_check` R1 and R2 in CI; ACL test in staging (a non-owner principal cannot produce to the topic); database grants test.

### DP-2 Kafka transports facts; the owner's database is the record
- **Statement:** Events say what happened, in the past tense, in the owning context's language. Kafka keeps them for replay and fan-out. The record of truth stays in the owner's PostgreSQL or audit store. Event sourcing is not the default.
- **Rationale:** Replay and fan-out are what the log is for (K 01a, MS 08a). Erasure, audit and KVKK retention are easier on a store we control, and event sourcing costs snapshots and upcasting that a small team does not need for the pilot (MS 02b, 01b).
- **Implications:** State topics (binding, grant, tariff, policy, availability) are compacted so a new read model can be built from them. Fact topics (CDR, payment, trip) have time retention. Anything needed longer lives in the owner's store.
- **Check:** every topic has cleanup and retention in `topics.csv` (R5); DP-7 rebuild drill.

### DP-3 Translate at the edge, one canonical model inside
- **Statement:** Hub, CPO, PSP, integrator and government shapes stop at an adapter. Internal topics carry the OCPI 2.3.0-shaped model from `ocpi-model` (ADR-0001).
- **Rationale:** Policy, pricing and payments then see one session and CDR shape. An anticorruption layer keeps a foreign model from leaking into ours (Evans ch14).
- **Implications:** No vendor field names in internal schemas. Hub rules live in data (profiles), not code branches.
- **Check:** schema lint for vendor names; adapter contract tests generated from the pinned contracts (H-01).

### DP-4 Contracts are code, change is additive, replay must keep working
- **Statement:** Every topic has an Avro schema in the registry and a version in its name (`.v1`). Changes are additive. A breaking change is a new topic version with a dual-schema window. Compatibility mode is BACKWARD_TRANSITIVE.
- **Rationale:** Schemas are the API of an event-driven service (MS 08d). Replay means new readers must read all old data, which is the transitive rule (my inference from K 01d, which names only BACKWARD and FORWARD).
- **Implications:** A schema change is a pull request that the consumer owners review. Moving or removing a field means cloning and a window, not an edit.
- **Check:** registry compatibility check on every schema pull request; consumer-driven contract tests (MS 01c).

### DP-5 Personal data stays off the log
- **Statement:** Topics carry public or pseudonymous data only. No VIN, plate, national ID, phone, e-mail, name, card number, raw location trace or registration-document image. People and cars appear as opaque references (`driverRef`, `vehicleRef`); resolving one goes through the owning service's API under authorization.
- **Rationale:** The log is immutable and replicated three times. Erasure (KVKK Art. 7), security (Art. 12) and cross-border duties (Art. 9) are manageable when personal data lives in few places. **Pseudonymous is still personal data**, so the class limits exposure and does not remove duties.
- **Implications:** Details and the erasure path are in ADR-0013. Keys of topics are never direct personal identifiers (VIN, plate, TCKN, phone, e-mail, name, address, card or account number); pseudonymous refs such as `driverRef` are keys only under ADR-0010 item 5. A compacted topic is keyed by the aggregate whose full state it carries (ADR-0010 item 5), and sets `max.compaction.lag.ms` so erasure has a bound. EMAID and OCPI token uid are linkable outside our systems, so their topics rely on tombstones with that bounded lag for erasure (ADR-0013 item 5a, DPO sign-off on X-09).
- **Check:** `eventflow_check` R3, R6 and R8; the schema linter fails a field tagged `pii`; erasure drill (tombstone, then compaction within the agreed lag); DPO sample review each wave.

### DP-6 Every dataset has a class, an owner and an expiry
- **Statement:** A topic, table, bucket or log stream exists only with a data class, an owner and a retention rule that ends in deletion.
- **Rationale:** Most data cools after a short hot period (AWS SUS04-BP03). Data without an expiry is a leak, in cost, carbon and risk.
- **Implications:** Defaults: raw volume topics 7 days, business-fact topics 30 days, state topics compacted, audit hot 13 months then cold (consent plan), location traces reduced to H3 resolution 8 cells after 90 days (CP-KPI-004). A topic with no consumer is deleted.
- **Check:** R2 (orphan topics) and R5 in CI; monthly storage report per owner.

### DP-7 Derived data is rebuildable
- **Statement:** Read models, caches, KPI tables and dashboards can be rebuilt from the log plus an owner snapshot with one documented command.
- **Rationale:** Views are cheap to throw away and expensive to trust if nobody can recreate them (MS 08c "lean data"). A pilot KPI that cannot be recomputed cannot be defended at the gate.
- **Implications:** Read models keep only the fields they need. A breaking schema change drops and regenerates the view, no migration script.
- **Check:** rebuild drill for each read model before each wave, with the time recorded; the KPI job reproduces yesterday's numbers from the same inputs (CP-KPI-001).

### DP-8 Money, time and identity are typed
- **Statement:** Money is an integer in minor units with an ISO currency (TRY, EUR), never a float. Time is a UTC instant, with the event time kept apart from the publish time. Identifiers are opaque and stable. The idempotency key of an operation is its own id (`paymentId` is the OCPI `authorization_reference`).
- **Rationale:** Rounding and duplicate-charge bugs are the expensive ones. Penny-rounding edge cases are a sign of a missing concept (Evans ch13).
- **Implications:** `Money` and `EventTime` are value objects in `ocpi-model`. FX rates are stored with the amount they converted.
- **Check:** schema lint (no `double` for amounts); property tests on rounding; a replayed CDR produces one capture (payments acceptance test).

---

## Application principles

### AP-1 Boundaries follow the domain; deployables follow load, duty or exposure
- **Statement:** A bounded context owns one model and one team (or agent role). Inside a context, prefer modules of one deployable. Split a deployable only when load profile, separation of duties, audience or exposure differ, or when it must release on its own.
- **Rationale:** Monolith first, a dial and not a switch (MS 01a, 02a). The consent plan already uses this rule, and the squad is small.
- **Implications:** Two services that always release together are merged (the `pricing` and `payments` rule in repo-plan v2 §5). `vehicle-identity` is a module of `plugcharge`, and `energy-profile` a module of `planner`, until a trigger fires.
- **Check:** independent-deploy test in the release pipeline (deploy service A alone against the previous version of all others); release-coupling report each iteration.

### AP-2 Invest in the core, buy or borrow the rest
- **Statement:** Name the core domain and put the strongest people on it. Generic subdomains use off-the-shelf software or a thin adapter.
- **Rationale:** Evans ch15. The table below is my proposal for the Architect to confirm.
- **Check:** each card names its subdomain class; no custom code for a generic subdomain without an ADR.

| Class | Contexts | Build or buy |
|---|---|---|
| **Core** | Corridor planning (planner, energy-profile, queue prediction); access orchestration (channel choice and guest price across hub, OCPI and guest) | Build, best people |
| **Supporting** | policy-engine, pricing, payments orchestration, plugcharge and vehicle-identity, loyalty, telemetry, pilot-analytics | Build, keep simple |
| **Generic** | OIDC provider, PSP, e-invoice integrator (GİB), maps, weather and traffic data, consent registry mechanics, Kafka itself | Buy, borrow or use a standard |

### AP-3 Translate at every outside boundary and name each relationship
- **Statement:** One adapter per external party (each hub, each CPO profile, PSP, integrator, e-Devlet, each data provider). Every context pair has a labelled relationship.
- **Rationale:** Evans ch14, Vernon context mapping (MS 07b).
- **Implications:** `hub-gateway`, the PSP port, the integrator adapter and `edevlet-bridge` are anticorruption layers. `ocpi-model` is a Published Language with shared-kernel governance (a change needs an ADR and a semver bump, M-02). The consent family is a supplier with consumer-driven contracts. OCPI 2.3.0 is a standard we conform to.
- **Check:** `P0-16` context map lists a relationship for each pair; a CI rule forbids importing vendor client classes outside an adapter package.

### AP-4 One aggregate per transaction; across aggregates use events
- **Statement:** An aggregate root guards its invariants and is the unit of one database transaction. Aggregates refer to each other by id. A rule across aggregates is eventually consistent, through an event or a saga.
- **Rationale:** Evans ch6, MS 07c and 02b. Draw boundaries tight where invariants are strict and loose where contention is high.
- **Implications:** Aggregates: VehicleBinding, Contract (EMAID), Payment, PaymentLink, LedgerAccount, Invoice, Trip (a process manager), Grant, DriverPolicy, PriceSheet. State machines come from the text tables in `engineering-briefing/uml/README.md`; when table and diagram disagree, the table wins.
- **Check:** architecture test that a repository exists only for aggregate roots; STT conformance test generated from the tables.

### AP-5 The user's hot path is local and short; everything else is asynchronous
- **Statement:** A request a person is waiting for may use only local state and bounded synchronous calls. It never waits on Kafka and never chains blocking calls across services.
- **Rationale:** Availability multiplies along synchronous chains (MS 07b, 02a). The Plug&Charge budget is 40 s end to end with a hub answer in about 10 s (Hubject SUP-2.6, unconfirmed in the spec), and the consent decision point must answer in 50 ms at p95 (RC-NFR-001).
- **Implications:** `hub-gateway` answers authorize from a local read model fed by binding, contract, grant and policy topics. The policy call becomes an event-fed lookup (topic `ev.policy.policy-changed.v1` is proposed for this). Kafka feeds the read model; it is not in the request.
- **Check:** latency budget test in the E2E harness (P1-05) with failure injection: with Kafka stopped, authorize still answers; p95 internal budget [0.5 s] of the hub's 10 s (proposed number).

### AP-6 Reliable messaging by default
- **Statement:** A state change and its event commit together (transactional outbox). Delivery is at least once. Every consumer is idempotent. Failures retry a bounded number of times and then go to a dead-letter topic with an alarm.
- **Rationale:** Dual writes lose events; manual deduplication everywhere does not scale (MS 08d, 02a). Exactly-once holds only inside Kafka (K 05a), so it is not a design assumption.
- **Implications:** Idempotency keys: one ledger entry per source event id, one capture per `paymentId`, one invoice per `paymentId`. Details in ADR-0011.
- **Check:** the redelivery kit in `EV_PNC_simulator` (duplicate, reorder, crash before commit, poison message) runs for every consumer in CI.

### AP-7 Fail closed for consent and money, degrade visibly for navigation
- **Statement:** If consent cannot be decided, deny (RC-GATE-003). If a payment state is unknown, do not capture twice and do not release the car's session blindly. If live data is missing, the planner uses history and says so (CP-IDLE-001).
- **Rationale:** Degrade by business criticality (MS 01c, 09c).
- **Check:** failure-injection scenarios in the simulator for decision timeout, PSP timeout, stale telemetry.

### AP-8 Secure by default
- **Statement:** Deny by default. Tokens on every edge call, object-level authorization on every owned resource, mTLS between services and to hubs, no secrets in code or images, no personal data in logs.
- **Rationale:** URL rules do not stop IDOR; `@PreAuthorize` and `@PostAuthorize` do (SB-practice ch7). Security 6 style: a `SecurityFilterChain` bean ending in `denyAll()`.
- **Implications:** The OBD2 allowlist (0x01, 0x09, 0x22) is enforced in the app, not by convention.
- **Check:** the three-way security test per endpoint (401, 403, allowed); DAST in `Consent_testkit`; secret scan on every pull request.

### AP-9 Choose algorithms by cost model and verify them
- **Statement:** A spec that depends on an algorithm states its input size, complexity and time budget. Library code is audited before use. Each hand-written algorithm has a brute-force oracle test.
- **Rationale:** The TheAlgorithms-Java notes found high-severity bugs in teaching code that has green tests (a k-d tree that prunes wrongly, a Johnson that drops zero edges). Cross-checking against brute force found what the suites missed.
- **Implications:** Production uses JDK collections, Caffeine, JTS and H3 for generic structures. We write only the planner DP, union-find for EVSE identity and the STT checks. See ADR-0015.
- **Check:** oracle tests in CI; the planner benchmark gate (p95 re-plan within the budget in ADR-0015).

---

## Technology principles

### TP-1 Open standards and open source first, portable by construction
- **Statement:** Prefer OCPI, OICP, ISO 15118, OAuth 2.0 and OIDC, the Kafka protocol, OpenTelemetry, SQL. Public repositories are Apache-2.0, so dependencies must be compatible with that.
- **Rationale:** The platform must run in a Turkey region first and may move. Hubs and EPDK expect standards.
- **Implications:** Application code uses the Kafka API only, never a vendor extension. Operators and Helm charts run on any conformant Kubernetes. Check licences when a component changes licence (Redis left the BSD licence in 2024 and added AGPLv3 as an option with Redis 8 in 2025; Valkey stays BSD; verify before choosing).
- **Check:** dependency licence scan in CI; a monthly "can we move" review reading the infra modules.

### TP-2 One paved road: the JVM, with written reasons for anything else
- **Statement:** Backend services are Java 25 (LTS) on Spring Boot 4.x (exact line pinned in `infra-modules`), using Spring MVC with virtual threads. Other runtimes need a one-paragraph reason in an ADR.
- **Rationale:** Two or three people (or agent roles) must maintain everything. Reactive code is chosen only end to end and for cost, not for speed (SB 02d, 03d).
- **Implications:** Exceptions today: planner in Python (OR-Tools and NumPy), mobile apps native, `api-gateway` on Spring Cloud Gateway (reactive, where many concurrent I/O-bound connections justify it). `telemetry` stays Go for now because C-01 is already written in Go (ADR-0012 revision 0.2); Go and Python services meet the same outbox, header and redelivery contract tests as the JVM template.
- **Check:** `docs/stack.md` lists each service's runtime; an ADR link is required for anything else.

### TP-3 Right store for the job
- **Statement:** PostgreSQL is the system of record. Kafka is the transport and short-term log. TimescaleDB (on PostgreSQL) holds time series. PostGIS holds geometry. A Redis-compatible cache holds only data that can be rebuilt. Object storage with WORM lock holds anchors and archives.
- **Rationale:** One operational skill set; no second broker; no cache as a database.
- **Check:** a cache loss drill (flush it and see the service recover); no table holds data that exists nowhere else except in Postgres.

### TP-4 Everything is code, declared and reviewed
- **Statement:** Topics, ACLs, schemas, quotas, infrastructure, dashboards and alerts live in git and change by pull request. Topic auto-creation is off.
- **Rationale:** Topic and ACL drift is how single-writer rules and retention rules die. Kafka in Action and the Confluent papers both want auto-create off in production (K 01c, 05a).
- **Implications:** `topics.csv` is the source for `KafkaTopic` and `KafkaUser` manifests in `EV_PNC_infra-modules`.
- **Check:** a nightly diff of cluster against git must be empty.

### TP-5 Build once, promote the same artifact
- **Statement:** One layered, non-root container image per commit, tagged by commit, promoted through environments by configuration only.
- **Rationale:** Twelve-factor, deployment pipeline (SB 06b, 02d).
- **Check:** image digest equality across environments is a release gate.

### TP-6 Observable by default
- **Statement:** Every service ships structured logs with a correlation id (`paymentId`, `tripId`), RED and USE metrics, and OpenTelemetry traces whose context travels in Kafka headers. SLOs are written before launch.
- **Implications:** Kafka alerts: UnderReplicatedPartitions above 0, ISR shrink thrash, consumer lag against the consumer's own SLO (not a fixed number), revocation-to-hub time against RC-REV-002 (15 minutes for 99%). Latency is measured with mergeable histograms, not per-instance percentiles.
- **Check:** a service without a readiness probe, a dashboard and a runbook link fails the release gate.

### TP-7 Residency and least privilege
- **Statement:** Personal data, consent and their backups run in Türkiye (RC-NFR-002). Kafka uses TLS, SASL or mTLS identities per service, and ACLs by topic. Network policy is deny by default.
- **Rationale:** The security layers are TLS, then authentication, then ACLs, then quotas (K 01d). There is no encryption at rest in Kafka, so disks are encrypted by the platform.
- **Implications:** The hosting provider is not yet chosen. AWS Well-Architected is used as a review lens only (consent plan §4), not as a hosting decision.
- **Check:** a quarterly access review of KafkaUser ACLs; a restore test of backups in the Turkey region.

### TP-8 Measure before tuning, and name the service goal
- **Statement:** For each topic class, decide first which of throughput, latency, durability and availability matters most. Benchmark from defaults, change one lever per run, repeat three times, report P99 beside throughput.
- **Rationale:** K 05a, 06a, 04a. The pilot's load (about 6 messages per second) is orders of magnitude below what a small cluster handles (ADR-0008, 02-tech-stack §6), so the decision here is durability and operability, not speed.
- **Check:** the X-10 baseline report exists before any non-default setting is merged.

### TP-9 Spend what the load needs
- **Statement:** Cost and carbon move together. Size to demand, schedule what can wait, tier what cools, scale non-production to zero outside test windows.
- **Rationale:** AWS SUS02, SUS04, SUS05 and the cost-sustainability link (SUS06-BP01). Tension recorded: SUS05-BP03 prefers managed services; residency and portability make us run Kafka ourselves (ADR-0009).
- **Implications:** Proxy metrics: CPU-seconds and GB stored per 1,000 sessions, per service. Multi-arch (amd64 and arm64) images so cheaper or more efficient instances stay possible. Region choice: business requirement first (residency), then provider energy data (SUS01-BP01).
- **Check:** the proxy-metric dashboard exists by the pilot gate; preproduction idle-to-zero job runs.

---

## Changes in 0.2 (audit, 2026-10-26)

| Principle | Change | Why |
|---|---|---|
| DP-5 | Compacted topics keyed by the aggregate id; bounded compaction lag; check R8 added | The v0.1 catalogue keyed grants by `driverRef`, which compaction collapses to one grant per driver; without `max.compaction.lag.ms` erasure had no bound |
| TP-1 | Redis licence note updated (AGPLv3 option since Redis 8) | Accuracy |
| TP-2 | JDK 25 LTS and Spring Boot 4.x named instead of "a supported JDK LTS and the currently supported Spring Boot line"; telemetry stays Go | Boot 3.5 left open-source support on 30 Jun 2026; JDK 24+ removes `synchronized` pinning of virtual threads (JEP 491); C-01 is already Go (COPUR/EV_PNC_telemetry#2) |
