# Kafka backend: principles, tech stack and ADRs

**Date:** 2026-10-26 · **Status:** proposed, for acceptance on card X-01 · **Requested by:** Steerfocus

## What is here

| File | Content |
|---|---|
| [01-principles.md](01-principles.md) | 26 TOGAF-style principles: 8 Data, 9 Application, 9 Technology. Each has a statement, rationale, implications and a check that runs somewhere |
| [02-tech-stack.md](02-tech-stack.md) | The stack by layer, context map and aggregates, the Kafka design with the 20-topic catalogue, algorithms and data structures by component, sizing, sustainability review, inconsistencies found |
| [adr/](adr/) | ADR-0008 to ADR-0015 (series continues after ADR-0007) |
| [03-repo-and-kanban-updates.md](03-repo-and-kanban-updates.md) | Per-repo changes, 24 cards to amend, 12 new cards, how it fits the wartime rule |
| [kanban/ev_pnc_backlog_v2_kafka_additions.csv](kanban/ev_pnc_backlog_v2_kafka_additions.csv) | The 12 new cards in the board's import format |
| [tools/](tools/) and [evidence/](evidence/) | `topics.csv`, `eventflow_check.py` and its tests (`python3 -m unittest discover -s tools`), `components_v2_1*.csv` and the outputs of both checks |

## The decisions in short

1. **Kafka is the transport and short-term log. Each owner's PostgreSQL is the record.** No event sourcing by default (ADR-0008).
2. **Apache Kafka 4.x in KRaft, run by Strimzi on Kubernetes in a Turkey region.** 3 brokers, 3 controllers, RF 3, min ISR 2, `acks=all`, idempotent, one durability profile (ADR-0009).
3. **Avro in an Apicurio registry, headers envelope, `ev.<context>.<fact>.v<N>` names, one writer per topic enforced by ACL** (ADR-0010).
4. **Transactional outbox (Spring Modulith), idempotent consumers, bounded retries to per-group dead letters, sagas for money and trips** (ADR-0011).
5. **Kotlin on the supported Spring Boot line, MVC with virtual threads, reactive only at the gateway; Spring Data JDBC; telemetry moves from Go to Kotlin (proposed); planner stays Python** (ADR-0012).
6. **No personal data on topics:** only public or pseudonymous, no raw location, no VIN or plate (ADR-0013).
7. **No shared platform library:** a template plus off-the-shelf libraries. A `platform-kit` fails the packaging check (zone of pain) (ADR-0014).
8. **Planner: DP over stop × SoC bucket on a route-ordered DAG, brute-force oracle, no code from teaching libraries** (ADR-0015).

## Findings you may not expect

- **The pilot does not need Kafka's throughput.** About 6 messages per second on average, about 127 at national scale (estimates). Kafka earns its place through replay, fan-out and the revocation path, and it costs a cluster to run. ADR-0008 keeps a Postgres-outbox fallback behind the same event contracts.
- **Two repos are missing from the plan.** Eight cards point at `EV_PNC_loyalty` and `EV_PNC_invoicing`, which are in neither the 19-repo list nor `components.csv`. With both added the packaging check still passes (21 repos).
- **The event-flow check found one loop by design** (`planner` and `telemetry`) and catches an accidental one (`hub-gateway` with `plugcharge`) when I added it as a test.
- **`policy-engine` should publish its rules** so the Plug&Charge authorize does not call it synchronously inside the 10 s window.

## Decisions I need from you

1. Accept, change or reject the ADRs (card X-01). The two with the biggest cost: ADR-0008 (Kafka at pilot size) and ADR-0012 item 4 (telemetry from Go to Kotlin).
2. Which hosting provider in a Turkey region, and is a managed Kafka there acceptable if one exists (ADR-0009).
3. Create `EV_PNC_loyalty` and `EV_PNC_invoicing` (card X-12).
4. Fit X-01 to X-03 (10 points) into I3 and defer 10 points. My suggestion is in `03-repo-and-kanban-updates.md` §4.
5. Whether the Consent family shares the cluster with the platform or gets its own.

## How the work was done

- Skills used: apache-kafka, microservices-and-ddd, algorithms-data-structures, java-spring-boot, aws-waf-sustainability, architecture-review. The named skills `evans-ddd`, `thealgorithms-java-trees-graph-structures`, `liang-java-data-structure-implementations` and `spring-boot-in-practice-security-rest-reactive` are installed as library skills that the Skill tool cannot start, so I read their core frameworks and the chapters directly.
- Checked by running: `eventflow_check.py` (20 topics, 7 rules, all pass, one declared loop; a trial with an added edge fails as it should) and the existing `packaging_check.py` on the extended component list, with and without a shared kit.
- Not done: no Kafka or Spring versions were installed or tested; no benchmark was run; Apicurio compatibility mode and Modulith's Kafka externalisation are from my knowledge and are the first things spike X-02 and X-03 confirm. Sizes are estimates from the stated assumptions.
- The project topic's generic stack table (Node.js, MySQL, merchant plugins) was not followed where it conflicts with the repo plan.
