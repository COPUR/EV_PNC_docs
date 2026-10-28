# ADR-0012: Runtime: Java on Spring Boot 4, MVC with virtual threads, reactive only at the edge

**Status:** proposed; the telemetry runtime needs the product owner (card X-01) · **Date:** 2026-10-26 · **Revision:** 0.3 (2026-10-28: backend languages are Java and Go, mobile is React Native, at the product owner's instruction. 0.2, audit 2026-10-26: Spring Boot 4 line and JDK 25; telemetry kept in Go, because C-01 is already written in Go)

**Context.** The product owner's backend stack is Java and Go. The earlier repo READMEs named another JVM language and Spring Boot 3; the planning sessions wrote that, the product owner did not choose it, and revisions 0.1 and 0.2 of this ADR kept it. The READMEs also say Go for `telemetry` and Python for `planner`. The project topic lists Java, Node.js and MySQL as a generic payments-gateway reference. A team of two or three people or agent roles maintains everything, with Kafka clients in every backend service. The books agree that reactive pays only end to end and for cost, not for speed (SB 02d, 03d), and that Spring Data JDBC is lighter and aggregate-oriented while JPA demands care with lazy loading and dirty checking (SB 06b).

**Options for the main runtime.**

| Option | For | Against |
|---|---|---|
| A Java, Spring Boot 4, MVC with virtual threads | Blocking style, simple stack traces, one language for 10+ services | Virtual threads need a check against pinning in client libraries |
| B Same with WebFlux everywhere | High concurrency per node | Everything must be non-blocking (JDBC to R2DBC); one blocking call ties up a core-bound thread |
| C Polyglot per service (Go, Node.js, Python) | Local optimum | More toolchains, more on-call knowledge, shared templates stop working |

**Decision.**
1. Option A for every backend service: Java 25 (LTS; records, sealed types and pattern matching for the domain model), Spring Boot 4.x (pin the exact line in `infra-modules`; Spring Boot 3.5, the last 3.x line, left open-source support on 30 Jun 2026, so a new platform does not start on it; X-01 accepts this ADR on condition that X-02 confirms the support window of the pinned line), Spring MVC with virtual threads, Resilience4j for timeouts, retries, circuit breakers and bulkheads (order: time limiter, circuit breaker, retry; rate limit before all).
2. Reactive only in `api-gateway` (Spring Cloud Gateway) where many concurrent I/O-bound connections and aggregation justify it. Nothing downstream of it is reactive.
3. Persistence: PostgreSQL, one schema per service, Flyway migrations written to be compatible with the previous release (rolling deploys run both). Spring Data JDBC for aggregates, one repository per aggregate root. `JdbcClient` or jOOQ for read models and reports. JPA only with a written reason. Never `ddl-auto` in production.
4. **Telemetry: Go (changed in revision 0.2).** v0.1 proposed moving it to the JVM for one runtime less. The audit found that card C-01 is already written in Go (open pull request COPUR/EV_PNC_telemetry#2: corridor geometries and the EVSE index, with tests and a Go CI workflow), and C-02 follows in I2. Rewriting reviewed code before the 7 Dec gate breaks the wartime rule. So telemetry stays Go, follows the same outbox table layout, header names and redelivery kit as the planner (a shared contract test, not the JVM template), and is reconsidered at X-10 or when telemetry needs the JVM template's glue in more than one place. The JVM still handles its load (about 4 messages per second at the pilot, about 100 nationally with one status channel per socket, about 200 with two), so moving later stays possible.
5. `planner` is Python in the repo plan (FastAPI, NumPy; OR-Tools optional). **Python is outside the Java and Go stack; the product owner decides whether the planner becomes Java or Go.** The optimiser is a pure function behind `planner-api`, so the move is cheap and the oracle test (ADR-0015) carries over. Until then it publishes Trip events through the same outbox and envelope (ADR-0011).
6. Mobile: React Native (TypeScript), Android 9.0+ and iOS 15.5+, one codebase; CarPlay and Android Auto are thin native modules (Android Auto in Java). Generated OpenAPI clients, no Kafka on devices. Payment-provider keys never ship in the app.
7. Observability: Micrometer and OpenTelemetry, trace context in Kafka headers, health probes with readiness separate from liveness (never an external system in liveness).
8. Security: Spring Security 7 (the line Spring Boot 4.x manages) `SecurityFilterChain` beans, JWT resource server with the issuer URI, method security with `@PreAuthorize` and `@PostAuthorize` for object ownership, BCrypt or the delegating encoder wherever a password exists.

**Consequences.**
- Two backend languages, Java and Go (plus Python for the planner until it is decided). Go's (and Python's) Kafka and outbox code are documented exceptions, held to the JVM template by the shared contract test.
- The golden-path template (ADR-0014) is JVM-only. A Python template of about 200 lines covers the planner.
- If a service needs WebFlux later, it needs its own ADR and an end-to-end reactive chain.
- JDK 24 and later no longer pin a virtual thread inside `synchronized` (JEP 491), which removes the main pinning risk of JDBC and Kafka clients; X-10 still checks for native-call pinning.
- Revision 0.3 changed only the language of the Spring services and the generated event classes (Java). The frameworks, Kafka design and template are unchanged.

**Sources.** java-spring-boot (core frameworks 1 to 13, 06b data, 02d and 03d reactive, 06c resilience), spring-boot-in-practice-security-rest-reactive (ch5, ch7, ch8), microservices-and-ddd (09a twelve factor), repo-plan v2 READMEs.
