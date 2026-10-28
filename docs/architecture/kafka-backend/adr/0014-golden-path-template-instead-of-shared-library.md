# ADR-0014: A golden-path template and off-the-shelf libraries, not a shared platform library

**Status:** proposed (accept on card X-01) · **Date:** 2026-10-26

**Context.** Every JVM service needs the same outbox, idempotent consumer, retry and dead-letter handling, tracing headers and security defaults. The obvious move is a shared `platform-kit` library. The repo plan applies Martin's package principles and checks them with `tools/packaging_check.py`. Code sharing between services is also a named antipattern (MS 03a).

**Evidence.** I added a `platform-kit` component to the component graph (library, estimated abstractness 0.40, used by 10 components: 9 deployables and the `hub-core` library) and ran the check (`evidence/packaging-check-v2_1-with-kit-output.txt`): no cycle, but `platform-kit` has instability 0.09 and distance D' 0.51, which the tool flags as the **zone of pain**: stable and concrete, hard to change, and everything depends on it. Without the kit (`evidence/packaging-check-v2_1-output.txt`, which also adds the missing `loyalty` and `invoicing` repos) the check passes with no cycle, no SDP violation and nothing in the zone of pain. Abstractness is an estimate until code exists.

**Options.**

| Option | For | Against |
|---|---|---|
| A `platform-kit` library in `ocpi-model` | No new repo | Puts Spring and Kafka dependencies into the model that 23 components depend on (CRP and SAP broken) |
| B New repo `EV_PNC_platform-kit` | Clean separation | Zone of pain; a breaking change forces all services to move; one more repo to own |
| C Off-the-shelf libraries plus a copy-once template in `EV_PNC_infra-modules/templates/` | No shared compile-time dependency; each service owns its code | About 300 lines duplicated per service; improvements need re-applying |

**Decision.** Option C.
1. Use maintained libraries for the hard parts: Spring Modulith (event publication registry and Kafka externalisation), Spring for Apache Kafka (retry topics, dead letters), Micrometer and OpenTelemetry, Spring Security, Resilience4j, Flyway.
2. The template `templates/spring-service` in `infra-modules` carries the glue: Kafka property profiles per topic class, the idempotency table and consumer wrapper, DLT handlers with the reason header, security filter chain with `denyAll()`, probes, logging with correlation id, a sample consumer test using Testcontainers Kafka.
3. Conformance is tested, not shared: the redelivery kit in `EV_PNC_simulator` and the envelope tests run against every service in its own CI.
4. When the template changes, a script opens pull requests on the repos that were generated from it. That keeps duplication cheap.
5. Revisit B when the same glue has needed the same fix in three services within two months, or when a measured abstractness shows the kit would sit outside the zone of pain.

**Consequences.**
- No new repo and no packaging violation. The 19-repo plan gains only the two repos already implied by cards (`loyalty`, `invoicing`; card X-12).
- Divergence is possible; the conformance tests and template-update pull requests are the guard.
- The Go services (planner, telemetry) have their own small template.

**Sources.** `repo-plan/v2/tools/packaging_check.py` (run twice, outputs in `evidence/`); agile-ppp-packaging-principles via `repo-plan/v2/README.md` §2; microservices-and-ddd (03a code sharing, 02a).
