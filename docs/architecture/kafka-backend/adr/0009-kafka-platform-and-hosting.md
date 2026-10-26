# ADR-0009: Kafka platform: KRaft on Kubernetes with Strimzi, one durability profile, Turkey-hosted

**Status:** proposed (accept on card X-01; hosting provider open) · **Date:** 2026-10-26 · **Revision:** 0.2 (audit 2026-10-26: consumer rebalance protocol and compaction lag added)

**Context.** Consent data and its backups must run in Türkiye (RC-NFR-002), and card P1-02 plans Kubernetes in a Turkey region. No provider is chosen. The consent plan reuses a shared EV_PNC Kafka with its own topics, ACLs and partitions. AWS Well-Architected is a review lens only. The load is small (ADR-0008), so the cluster is sized for durability and operability.

**Options.**

| Option | For | Against |
|---|---|---|
| A Self-run Apache Kafka 4.x (KRaft) with the Strimzi operator on our Kubernetes | Portable, Apache-2.0, topics and users as git-managed resources, residency in our hands | We carry upgrades, on-call and capacity |
| B Managed Kafka abroad (for example MSK or Confluent Cloud) | Less operations, matches SUS05-BP03 | Personal data leaves Türkiye before counsel answers TR-05; hosting lock-in to a region |
| C Kafka-compatible broker (for example Redpanda) | One binary, simple ops | Smaller ecosystem for operators, connectors and schema tooling here; licence terms to check |
| D Managed Kafka in Türkiye | Best of both | Not known to exist for us; check during P1-02 |

**Decision.** Option A, keeping D open. Version: Apache Kafka 4.x in KRaft mode (no ZooKeeper). Three brokers and three dedicated controllers. Combined mode is not used because Kafka's own guidance advises against it for critical deployments (I, from memory; confirm in the spike). Settings, for all topics: replication factor 3, `min.insync.replicas` 2, producers `acks=all` and idempotent, unclean leader election off, topic auto-creation off, `broker.rack` per failure domain, internal topics at RF 3, encrypted volumes, TLS and mTLS identities per service. One durability profile; only batching and retention differ by class (`02-tech-stack.md` §3). The operator creates topics and users from `topics.csv` in git. Pilot node sizes are in the stack document, §3.1 and §6.

**Consequences.**
- Single DC in the pilot with tested backups, a deliberate trade of availability for cost, as the consent plan does. Security and operations are not traded. RF 3 across racks survives one broker loss.
- National scale: second Turkey DC with MirrorMaker 2 (active-passive), offsets synced, RPO ≤ 5 min and RTO ≤ 1 h (NHS HLD). Trigger: consent or payments leaves the pilot.
- SUS05-BP03 tension recorded: we run a stateful service ourselves for residency and portability. Revisit if D appears.
- Alerts: UnderReplicatedPartitions above 0, ISR shrink thrash, consumer lag against each consumer's SLO, revocation-to-hub time, disk growth. The disk and request-time breakdown (queue, local, remote, response) guide the first diagnosis (K 05a).
- Sharing the cluster with the consent family needs quotas and ACLs so one tenant cannot starve the other. Dedicated cluster if the consent family needs its own SLO class.
- Version pins and the Strimzi, Kafka and client compatibility are verified in spike X-02 before any production claim.
- Consumer groups: Kafka 4.x ships the new consumer rebalance protocol (KIP-848, `group.protocol=consumer`), where the broker assigns partitions and client-side assignors such as cooperative-sticky do not apply. X-02 tests it with static membership and adopts it if the Spring for Apache Kafka line in use supports it; otherwise the classic protocol with cooperative-sticky stays (I, from knowledge; confirm in the spike).
- Compacted topics set `max.compaction.lag.ms` [1 d] as well as `segment.ms` 1 d. Without it the cleaner only runs when the dirty ratio passes `min.cleanable.dirty.ratio` (0.5 by default), so on a quiet topic a tombstone may never take effect and the erasure lag in ADR-0013 has no bound.

**Sources.** apache-kafka (05a durability triad, 06a, 01c, 02c, 07a); aws-waf-sustainability (SUS01-BP01, SUS05-BP03); `repo-plan/consent/README.md` §3, §4; `national-hub-service/02-HLD.md` §6; RC-NFR-002.
