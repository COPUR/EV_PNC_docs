# ADR-0012: Runtime: Kotlin on Spring Boot, MVC with virtual threads, reactive only at the edge

**Status:** proposed; the telemetry runtime change needs the product owner (card X-01) · **Date:** 2026-10-26

**Context.** Repo READMEs say Kotlin and Spring Boot 3 for `ocpi-emsp`, Go for `telemetry`, Python for `planner`, native apps for mobile. The project topic lists Java, Node.js and MySQL as a generic payments-gateway reference. A team of two or three people or agent roles maintains everything, with Kafka clients in every backend service. The books agree that reactive pays only end to end and for cost, not for speed (SB 02d, 03d), and that Spring Data JDBC is lighter and aggregate-oriented while JPA demands care with lazy loading and dirty checking (SB 06b).

**Options for the main runtime.**

| Option | For | Against |
|---|---|---|
| A Kotlin, Spring Boot (supported line), MVC with virtual threads | Blocking style, simple stack traces, one language for 10+ services | Virtual threads need a check against pinning in client libraries |
| B Same with WebFlux everywhere | High concurrency per node | Everything must be non-blocking (JDBC to R2DBC); one blocking call ties up a core-bound thread |
| C Polyglot per service (Go, Node.js) | Local optimum | More toolchains, more on-call knowledge, shared templates stop working |

**Decision.**
1. Option A for every backend service: Kotlin, a supported JDK LTS, the currently supported Spring Boot line (pinned in `infra-modules`; X-05 confirms its open-source support window before this ADR is accepted), Spring MVC with virtual threads, Resilience4j for timeouts, retries, circuit breakers and bulkheads (order: time limiter, circuit breaker, retry; rate limit before all).
2. Reactive only in `api-gateway` (Spring Cloud Gateway) where many concurrent I/O-bound connections and aggregation justify it. Nothing downstream of it is reactive.
3. Persistence: PostgreSQL, one schema per service, Flyway migrations written to be compatible with the previous release (rolling deploys run both). Spring Data JDBC for aggregates, one repository per aggregate root. `JdbcClient` or jOOQ for read models and reports. JPA only with a written reason. Never `ddl-auto` in production.
4. **Telemetry moves from Go to Kotlin** (proposed). Its load is about 4 messages per second at the pilot and about 100 nationally; the JVM handles that, and one runtime lets it share the template and libraries. Keep Go only if the X-10 baseline shows a measured gap. This changes `EV_PNC_telemetry`'s README line "Go, Redis, Kafka, TimescaleDB".
5. `planner` stays Python (FastAPI, NumPy; OR-Tools optional). The optimiser is a pure function behind `planner-api`. It publishes Trip events through the same outbox and envelope (ADR-0011).
6. Mobile unchanged: native Swift and Kotlin, generated OpenAPI clients, no Kafka on devices.
7. Observability: Micrometer and OpenTelemetry, trace context in Kafka headers, health probes with readiness separate from liveness (never an external system in liveness).
8. Security: Spring Security 6 `SecurityFilterChain` beans, JWT resource server with the issuer URI, method security with `@PreAuthorize` and `@PostAuthorize` for object ownership, BCrypt or the delegating encoder wherever a password exists.

**Consequences.**
- Two backend languages (Kotlin, Python), down from three. Python's Kafka and outbox code is a documented exception.
- The golden-path template (ADR-0014) is JVM-only. A Python template of about 200 lines covers the planner.
- If a service needs WebFlux later, it needs its own ADR and an end-to-end reactive chain.
- Check JVM client libraries for virtual-thread pinning in the first load test (X-10).
- Kotlin versus Java: the repo READMEs say Kotlin and I kept it; both are JVM, so switching does not change this ADR.

**Sources.** java-spring-boot (core frameworks 1 to 13, 06b data, 02d and 03d reactive, 06c resilience), spring-boot-in-practice-security-rest-reactive (ch5, ch7, ch8), microservices-and-ddd (09a twelve factor), repo-plan v2 READMEs.
