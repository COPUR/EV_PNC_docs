# ADR-0011: Delivery guarantees: outbox, idempotent consumers, bounded retries, sagas

**Status:** proposed (accept on card X-01) · **Date:** 2026-10-26 · **Revision:** 0.2 (audit 2026-10-26: invoicing consumes the final CDR)

**Context.** The deck's sequences already say "CDR event via outbox (Kafka, at least once)", "drop if event id already seen" and "one capture per payment id". The money path is session, CDR, capture, ledger and invoice, spread over four services. Exactly-once in Kafka holds only for Kafka-to-Kafka work (K 05a); a PSP call, a database write and a push message can still repeat.

**Options for publishing.**

| Option | For | Against |
|---|---|---|
| A Spring Modulith event publication registry with Kafka externalisation | Off the shelf, stores the event in the transaction, resubmits incomplete publications, fits modules | Needs the Modulith version to match the Boot line (spike X-05) |
| B Debezium outbox event router on Kafka Connect | No polling, scales | Another cluster to run; logical replication on every service database |
| C Hand-written polling relay | Small | We would own a framework |
| D Send after commit | Easy | Loses events on a crash between commit and send (dual write) |

**Decision.**
1. **Publish:** option A in JVM services; the publisher sits behind a port, so B replaces it at national scale or if relay lag becomes a problem, without changing event contracts. The Python planner implements the same outbox table layout and relay in about a hundred lines, covered by a shared contract test. D is forbidden.
2. **Consume:** at-least-once. Offsets commit after processing, never before. Each consumer records (consumer, `ce_id`) in a unique index inside the same transaction as its effect. Cleanup job after the longest retention.
3. **Retries:** bounded, non-blocking retry topics with backoff, then `<topic>.<group>.dlt` with a reason header (`invalid` or `exhausted`) and an alarm. No unbounded in-place retry; no manual resend with idempotence on (a resend gets a new sequence number, K 05a).
4. **Exactly-once:** only inside Kafka-to-Kafka stream jobs (`processing.guarantee`, `read_committed`). It is never a design assumption for a service with a database or an outside call.
5. **Idempotency keys:** one ledger entry per source event id; one PSP capture per `paymentId` (also the PSP idempotency key); one invoice per `paymentId`; one hold per (`paymentId`, kind).
6. **Sagas and ownership:** `payments` orchestrates the payment lifecycle (authorise, session, CDR, capture, refund), compensating by refund or a REVERSE ledger entry; `planner` runs the Trip as a process manager keyed by `tripId`. Fan-out reactions (earn bonus, KPIs, push) are choreographed. Compensations are semantic: a credit CDR becomes a refund, never a second capture.
7. **Ordering:** per key only. Do not rely on order across keys; a consumer needing it uses the state topic.
8. **Expiry:** events with a time limit carry `expires` and a consumer drops expired events (re-plan).

**Consequences.**
- Every service has the same three artefacts: outbox table, idempotency table, DLT handling. The golden-path template (ADR-0014) carries them so nobody writes them twice.
- The redelivery kit in `EV_PNC_simulator` (duplicate, reorder, crash before commit, poison message, slow consumer) is a merge gate for consumers.
- DLT messages are an operations duty: the owner triages within one working day [proposed].
- Relay lag becomes an SLO (publish lag p99 [2 s]); alerts on the outbox backlog.
- A late final CDR or a missing capture holds the invoice on a timer with an alert, as in the loyalty design notes. `invoicing` therefore consumes both `cdr-received` (invoice lines) and `payment-state-changed` (capture), and issues when both have arrived for the same `paymentId`. v0.1 of the catalogue left `invoicing` off the CDR topic.

**Sources.** apache-kafka (01b commit strategy, 05a idempotence and retries, 06a); microservices-and-ddd (02a outbox, 02b sagas, 08d transactions, 07b idempotent receiver); java-spring-boot (06c events, 07c DLQ); `engineering-briefing/loyalty-invoicing/README.md`; `engineering-briefing/review/README.md`.
