# Kafka backend: principles, tech stack and ADRs

**Version:** 0.2 (audited 2026-10-26, see the last section) · **Date:** 2026-10-26 · **Status:** proposed, for acceptance on card X-01 · **Requested by:** Steerfocus

## What is here

| File | Content |
|---|---|
| [01-principles.md](01-principles.md) | 26 TOGAF-style principles: 8 Data, 9 Application, 9 Technology. Each has a statement, rationale, implications and a check that runs somewhere |
| [02-tech-stack.md](02-tech-stack.md) | The stack by layer, context map and aggregates, the Kafka design with the 21-topic catalogue, algorithms and data structures by component, sizing, sustainability review, inconsistencies found |
| [adr/](adr/) | ADR-0008 to ADR-0015 (series continues after ADR-0007) |
| [03-repo-and-kanban-updates.md](03-repo-and-kanban-updates.md) | Per-repo changes, 24 cards to amend, 12 new cards, how it fits the wartime rule |
| [kanban/ev_pnc_backlog_v2_kafka_additions.csv](kanban/ev_pnc_backlog_v2_kafka_additions.csv) | The 12 new cards in the board's import format |
| [tools/](tools/) and [evidence/](evidence/) | `topics.csv`, `eventflow_check.py`, `components_v2_1*.csv` and the outputs of both checks |

## The decisions in short

1. **Kafka is the transport and short-term log. Each owner's PostgreSQL is the record.** No event sourcing by default (ADR-0008).
2. **Apache Kafka 4.x in KRaft, run by Strimzi on Kubernetes in a Turkey region.** 3 brokers, 3 controllers, RF 3, min ISR 2, `acks=all`, idempotent, one durability profile (ADR-0009).
3. **Avro in an Apicurio registry, headers envelope, `ev.<context>.<fact>.v<N>` names, one writer per topic enforced by ACL; compacted topics keyed by the aggregate id** (ADR-0010).
4. **Transactional outbox (Spring Modulith), idempotent consumers, bounded retries to per-group dead letters, sagas for money and trips** (ADR-0011).
5. **Kotlin on Spring Boot 4.x and JDK 25, MVC with virtual threads, reactive only at the gateway; Spring Data JDBC; telemetry stays Go for now (C-01 is already Go); planner stays Python** (ADR-0012).
6. **No personal data on topics:** only public or pseudonymous, no raw location, no VIN or plate (ADR-0013).
7. **No shared platform library:** a template plus off-the-shelf libraries. A `platform-kit` fails the packaging check (zone of pain) (ADR-0014).
8. **Planner: DP over stop × SoC bucket on a route-ordered DAG, brute-force oracle, no code from teaching libraries** (ADR-0015).

## Findings you may not expect

- **The pilot does not need Kafka's throughput.** About 6 messages per second on average, about 127 at national scale (estimates). Kafka earns its place through replay, fan-out and the revocation path, and it costs a cluster to run. ADR-0008 keeps a Postgres-outbox fallback behind the same event contracts.
- **Two repos are missing from the plan.** Eight cards point at `EV_PNC_loyalty` and `EV_PNC_invoicing`, which are in neither the 19-repo list nor `components.csv`. With both added the packaging check still passes (21 repos).
- **The event-flow check found one loop by design** (`planner` and `telemetry`) and catches an accidental one (`hub-gateway` with `plugcharge`) when I added it as a test.
- **`policy-engine` should publish its rules** so the Plug&Charge authorize does not call it synchronously inside the 10 s window.

## Decisions I need from you

1. Accept, change or reject the ADRs (card X-01). The two with the biggest cost: ADR-0008 (Kafka at pilot size) and ADR-0012 item 4 (telemetry: keep Go, recommended in 0.2, or move to Kotlin).
2. Which hosting provider in a Turkey region, and is a managed Kafka there acceptable if one exists (ADR-0009).
3. Create `EV_PNC_loyalty` and `EV_PNC_invoicing` (card X-12).
4. Put only X-01 (2 points) in I3, move X-02 and X-03 to I4, and defer A-01. Revised in 0.2, see `03-repo-and-kanban-updates.md` §4.
5. Whether the Consent family shares the cluster with the platform or gets its own.

## How the work was done

- Skills used: apache-kafka, microservices-and-ddd, algorithms-data-structures, java-spring-boot, aws-waf-sustainability, architecture-review. The named skills `evans-ddd`, `thealgorithms-java-trees-graph-structures`, `liang-java-data-structure-implementations` and `spring-boot-in-practice-security-rest-reactive` are installed as library skills that the Skill tool cannot start, so I read their core frameworks and the chapters directly.
- Checked by running: `eventflow_check.py` (v0.2: 21 topics, 8 rules, all pass, one declared loop; a trial with an added edge fails as it should, and the v0.1 catalogue fails the new rule R8) and the existing `packaging_check.py` on the extended component list, with and without a shared kit.
- Not done: no Kafka or Spring versions were installed or tested; no benchmark was run; Apicurio compatibility mode and Modulith's Kafka externalisation are from my knowledge and are the first things spike X-02 and X-03 confirm. Sizes are estimates from the stated assumptions.
- The project topic's generic stack table (Node.js, MySQL, merchant plugins) was not followed where it conflicts with the repo plan.

## Audit 0.2 (2026-10-26)

A second review checked this package against ADR-0007, repo-plan v2, kanban v2, the loyalty and invoicing design and the open pull requests. The full audit, with the consent-flow review beside it, is the doc [Audit: Kafka backend and e-Devlet consent flows](https://claude.ai/artifact/YbUDUfgZMyCL71fhGSYhL3).

| # | Finding | Severity | Fixed in |
|---|---|---|---|
| 1 | `grant-changed` keyed by `driverRef`: compaction keeps one record per key, so only a driver's last per-hub grant survives a rebuild | High | `topics.csv`, ADR-0010 item 5, check R8 |
| 2 | Compacted topics had no `max.compaction.lag.ms`, so the erasure lag had no bound on quiet topics | High | ADR-0009, ADR-0013, stack §3.1 |
| 3 | Spring Boot 3 chosen, but Boot 3.5 left open-source support on 30 Jun 2026 | High | ADR-0012, TP-2, stack §1 |
| 4 | Telemetry "Go to Kotlin" ignored that C-01 is already Go (COPUR/EV_PNC_telemetry#2) | Medium | ADR-0012 item 4 (keep Go), X-01, X-06 |
| 5 | `invoicing` did not consume `cdr-received`, but issues only after the final CDR | Medium | `topics.csv`, ADR-0011 |
| 5a | `ocpi-emsp` did not consume `contract-changed`, so a revoked binding never invalidated the EMAID token at CPOs | High | `topics.csv` |
| 6 | Deferring P0-13 would remove K6 and K8 evidence from the gate; X-02 and X-03 are not gate work | Medium | 03 §4, ADR-0008 fallback date, CSV |
| 7 | No owner for the driver account or `driverRef` | Medium | ADR-0013 item 4, P0-16 |
| 8 | e-Devlet grants had no path into the platform that keeps the registry the single writer | Low | new planned topic, ADR-0010 item 11 |
| 9 | Pilot storage undercounted trip state (7 instead of 30 days) | Low | stack §6 |
| 10 | Consumer rebalance protocol: KIP-848 in Kafka 4.x not considered | Low | ADR-0009, X-02 |
| 11 | JDK 21 virtual threads pin on `synchronized`; JDK 25 does not | Low | ADR-0012, TP-2 |
| 12 | Redis licence note out of date (AGPLv3 option since Redis 8) | Low | TP-1 |
