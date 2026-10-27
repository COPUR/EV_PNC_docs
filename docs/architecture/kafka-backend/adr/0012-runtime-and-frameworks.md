# ADR-0012: Runtime: Kotlin on Spring Boot 4, MVC with virtual threads, reactive only at the edge

**Status:** proposed; the telemetry runtime needs the product owner (card X-01) · **Date:** 2026-10-26 · **Revision:** 0.2 (audit 2026-10-26: Spring Boot 4 line and JDK 25; telemetry recommendation changed to keep Go, because C-01 is already written in Go)

**Context.** Repo READMEs say Kotlin and Spring Boot 3 for `ocpi-emsp`, Go for `telemetry`, Python for `planner`, native apps for mobile. The project topic lists Java, Node.js and MySQL as a generic payments-gateway reference. A team of two or three people or agent roles maintains everything, with Kafka clients in every backend service. The books agree that reactive pays only end to end and for cost, not for speed (SB 02d, 03d), and that Spring Data JDBC is lighter and aggregate-oriented while JPA demands care with lazy loading and dirty checking (SB 06b).

**Options for the main runtime.**

| Option | For | Against |
|---|---|---|
| A Kotlin, Spring Boot 4, MVC with virtual threads | Blocking style, simple stack traces, one language for 10+ services | Virtual threads need a check against pinning in client libraries |
| B Same with WebFlux everywhere | High concurrency per node | Everything must be non-blocking (JDBC to R2DBC); one blocking call ties up a core-bound thread |
| C Polyglot per service (Go, Node.js) | Local optimum | More toolchains, more on-call knowledge, shared templates stop working |

**Decision.**
1. Option A for every backend service: Kotlin 2.2 or newer, JDK 25 LTS, Spring Boot 4.x (pin the exact line in `infra-modules`; Spring Boot 3.5, the last 3.x line, left open-source support on 30 Jun 2026, so a new platform does not start on it; X-05 confirms the support window before this ADR is accepted), Spring MVC with virtual threads, Resilience4j for timeouts, retries, circuit breakers and bulkheads (order: time limiter, circuit breaker, retry; rate limit before all).
2. Reactive only in `api-gateway` (Spring Cloud Gateway) where many concurrent I/O-bound connections and aggregation justify it. Nothing downstream of it is reactive.
3. Persistence: PostgreSQL, one schema per service, Flyway migrations written to be compatible with the previous release (rolling deploys run both). Spring Data JDBC for aggregates, one repository per aggregate root. `JdbcClient` or jOOQ for read models and reports. JPA only with a written reason. Never `ddl-auto` in production.
4. **Telemetry: keep Go for now (changed in revision 0.2).** v0.1 proposed moving it to Kotlin for one runtime less. The audit found that card C-01 is already written in Go (open pull request COPUR/EV_PNC_telemetry#2: corridor geometries and the EVSE index, with tests and a Go CI workflow), and C-02 follows in I2. Rewriting reviewed code before the 7 Dec gate breaks the wartime rule. So telemetry stays Go, follows the same outbox table layout, header names and redelivery kit as the planner (a shared contract test, not the JVM template), and is reconsidered at X-10 or when telemetry needs the JVM template's glue in more than one place. The JVM still handles its load (about 4 messages per second at the pilot, about 100 nationally with one status channel per socket, about 200 with two), so moving later stays possible.
5. `planner` stays Python (FastAPI, NumPy; OR-Tools optional). The optimiser is a pure function behind `planner-api`. It publishes Trip events through the same outbox and envelope (ADR-0011).
6. Mobile unchanged: native Swift and Kotlin, generated OpenAPI clients, no Kafka on devices.
7. Observability: Micrometer and OpenTelemetry, trace context in Kafka headers, health probes with readiness separate from liveness (never an external system in liveness).
8. Security: Spring Security 6 `SecurityFilterChain` beans, JWT resource server with the issuer URI, method security with `@PreAuthorize` and `@PostAuthorize` for object ownership, BCrypt or the delegating encoder wherever a password exists.

**Consequences.**
- Three backend languages for now (Kotlin, Go for telemetry, Python for the planner). Go's and Python's Kafka and outbox code are documented exceptions, held to the JVM template by the shared contract test.
- The golden-path template (ADR-0014) is JVM-only. A Python template of about 200 lines covers the planner.
- If a service needs WebFlux later, it needs its own ADR and an end-to-end reactive chain.
- JDK 24 and later no longer pin a virtual thread inside `synchronized` (JEP 491), which removes the main pinning risk of JDBC and Kafka clients; X-10 still checks for native-call pinning.
- Kotlin versus Java: the repo READMEs say Kotlin and I kept it; both are JVM, so switching does not change this ADR.

**Sources.** java-spring-boot (core frameworks 1 to 13, 06b data, 02d and 03d reactive, 06c resilience), spring-boot-in-practice-security-rest-reactive (ch5, ch7, ch8), microservices-and-ddd (09a twelve factor), repo-plan v2 READMEs.
