# ADR-0008: Kafka is the event backbone; each owner's PostgreSQL stays the record

**Status:** proposed (accept on card X-01) · **Date:** 2026-10-26 · **Revision:** 0.2 (audit 2026-10-26: fallback deadline moved from the 7 Dec gate to the end of I4, because X-02 moves to I4)

**Context.** The C4 containers already show Kafka, and the product owner asked for Kafka on the backend. The reasons that hold up are the ones that need a log: a new consumer can replay (the `hub-gateway` read model, the KPI jobs), one fact reaches many consumers (CDR to payments, ledger and analytics), and revocation must reach the hub path within 15 minutes for 99% of cases (RC-REV-002). The load does not need Kafka: about 6 messages per second at the pilot and about 127 at national scale (`02-tech-stack.md` §6, estimates). The team is two or three people or agent roles, so operating cost counts.

**Options.** Scores are 1 to 5, my judgement, weights in brackets. Maximum 115.

| Criterion (weight) | A Kafka transport, Postgres record | B Postgres outbox, HTTP and NOTIFY only | C Queue broker (RabbitMQ or SQS-like) | D Kafka as record, event sourcing |
|---|---|---|---|---|
| Correctness of money and consent flows (5) | 4 | 3 | 4 | 3 |
| Privacy and erasure (5) | 4 | 4 | 4 | 1 |
| Operable by a small team (4) | 3 | 4 | 3 | 1 |
| Replay and fan-out (4) | 5 | 2 | 3 | 5 |
| Cost and carbon at pilot load (3) | 3 | 5 | 4 | 2 |
| Headroom to national scale (2) | 5 | 2 | 4 | 5 |
| **Weighted total** | **91** | **78** | **84** | **60** |

**Decision.** Option A. Kafka carries immutable facts and state snapshots (compacted topics). The owning service's PostgreSQL, or the audit store for consent, remains the record. Event sourcing is not the default; a service may adopt it by its own ADR. Kafka stays internal: CPOs and hubs speak OCPI and OICP over HTTP at the adapters, and the mobile app speaks REST.

**Consequences.**
- Gains: replay for read models and KPIs, independent consumers, a clean place for the revocation path, headroom to national scale without re-platforming.
- Costs: a cluster to run (six small pods at the pilot), a schema registry, outbox and idempotency discipline in every service, and Kafka skills on a small team.
- B is close and cheaper. **Fallback:** publishing sits behind a port (ADR-0011). Services write to the outbox table from day one (P1-07 does so in I3). If by the end of I4 (20 Dec 2026) the cluster does not run with the durability profile and green failure drills (card X-02), the pilot keeps publishing through Postgres outbox tables with HTTP delivery, with no change to event contracts. Revisit then. Nothing on the 7 Dec gate depends on Kafka.
- The pilot does not need Kafka's throughput. Do not justify tuning or extra partitions by speed.
- Rejected D because the log is immutable and replicated, which makes KVKK erasure and audit retention harder, and snapshots and upcasting are costs with no pilot benefit.

**Sources.** apache-kafka (01a, 01c, 05a); microservices-and-ddd (08a, 08c, 02b, 01b); architecture-review procedure; `engineering-briefing/uml/02-c4-container.puml`; `roaming-consent/spec.md` RC-REV-002; `national-hub-service/02-HLD.md` §7.
