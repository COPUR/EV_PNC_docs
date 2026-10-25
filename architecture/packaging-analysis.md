# Packaging analysis for the EV_PNC_ set

**Date:** 2026-10-25 · **Method:** Martin & Martin, *Agile Principles, Patterns, and Practices in C#*, ch. 28 and 30 (via the `book-skills:agile-ppp-packaging-principles` skill). The skill name you gave exists; it can only be run by the user, so its content was read from the skill files and applied by hand.

## 1. Method in one paragraph

Components are the unit of release; the graph of components is a map of buildability and it evolves. Cohesion decides what goes into a component (REP, CRP, CCP). Coupling decides how components may depend on each other (ADP, SDP, SAP). Then components are grouped into repos by ownership and cadence. The check is mechanical: `tools/packaging_check.py` reads `components.csv` (33 components, 19 repos), finds cycles, computes I = Ce/(Ca+Ce), A, D' = |A+I-1|, and lists SDP violations. `--strict` exits 1 on a cycle, an SDP violation or D' > 0.5, so it can gate CI.

## 2. Cohesion decisions

| Question | Decision | Principle |
|---|---|---|
| Should the canonical model live in `ocpi-emsp`? | No. 19 components depend on it and it changes on OCPI upgrades, not on server logic. Own repo, schema first. | CRP, SAP |
| One repo for all hubs? | Specs and pins apart (`hub-contracts`, data, drift-driven), adapters together (`hub-gateway`, one Gradle module per hub, one deployable per hub). | CCP, ADP |
| Pricing inside payments? | No. Planner, policy engine and the app need prices, not PSP code. | CRP, SDP |
| Policy, payments, plug&charge, telemetry: publish what? | A small `*-api` component each (OpenAPI/AsyncAPI plus client interfaces). Servers are never dependencies. | REP, SAP |
| Where do the hub ports live? | Interfaces belong to clients (ABSTRACT SERVER): the plug&charge port is in `plugcharge-api`; adapters in `hub-gateway` implement it. | Interfaces belong to clients |
| Mock hubs inside the adapters? | No. Mocks are generated from `hub-contracts` pins and live in `simulator`, consumed as container images. A library dependency would put a concrete component under four consumers (zone of pain). | SAP |
| Shared contracts mega-repo? | Rejected. Everyone would revalidate on every change. Only `ocpi-model` and per-service `*-api` are shared. | CRP |
| Two infra repos? | Reusable modules (public, shared with the consent family) apart from environments (private). | REP, exposure |

The REP/CRP versus CCP tension is real: early on, CCP wins (few repos, fast change), later reuse wins. That is why wave 1 is 10 repos, the lean variant is 6, and the triggers table in the README says when to split.

## 3. Coupling results

### v2 (this plan)

```
33 components, 19 repos

ADP (cycles): none

component                Ca  Ce     I     A    Dp  flag
hub-contracts             5   0  0.00  1.00  0.00  
ocpi-model               19   0  0.00  0.85  0.15  
edge-api                  3   0  0.00  1.00  0.00  
consent-contracts         8   0  0.00  0.90  0.10  
data-contracts            1   0  0.00  1.00  0.00  
trust-contracts           2   0  0.00  1.00  0.00  
mcs-contracts             2   0  0.00  1.00  0.00  
policy-api                7   1  0.12  1.00  0.12  
pricing-api               6   1  0.14  1.00  0.14  
plugcharge-api            4   1  0.20  1.00  0.20  
telemetry-api             4   1  0.20  1.00  0.20  
payments-api              3   1  0.25  1.00  0.25  
planner-api               3   1  0.25  1.00  0.25  
hub-core                  3   2  0.40  0.30  0.30  review
ocpi-emsp-server          0   3  1.00  0.05  0.05  
policy-server             0   3  1.00  0.05  0.05  
pricing-server            0   2  1.00  0.05  0.05  
payments-server           0   3  1.00  0.05  0.05  
plugcharge-server         0   3  1.00  0.05  0.05  
telemetry-server          0   2  1.00  0.05  0.05  
planner-server            0   5  1.00  0.05  0.05  
hub-hubject               0   6  1.00  0.05  0.05  
hub-gireve                0   6  1.00  0.05  0.05  
hub-echx                  0   5  1.00  0.05  0.05  
simulator                 0   2  1.00  0.05  0.05  
pilot-analytics           0   5  1.00  0.02  0.02  
api-gateway-server        0   8  1.00  0.05  0.05  
mobile-ios                0   1  1.00  0.05  0.05  
mobile-android            0   1  1.00  0.05  0.05  
consent-edevlet-bridge    0   2  1.00  0.05  0.05  
consent-testkit           0   1  1.00  0.02  0.02  
data-reference            0   2  1.00  0.10  0.10  
mcs-reference             0   2  1.00  0.10  0.10  

SDP violations (a component depends on a less stable one, I(dep) > I(self)):
  none
```

Reading it: no cycles; no SDP violations; the stable and abstract core is `ocpi-model` (19 dependents), the `*-api` components, `hub-contracts`, `edge-api`, `mcs-contracts`, `data-contracts`, `trust-contracts` and `consent-contracts`; every deployable sits at I = 1 with A near 0, which is correct for leaves. `hub-core` (D' 0.30) is the one component to watch: it is a library with a concrete core and 3 dependents; if it grows, move its error mapping and profile loader interfaces into `hub-contracts`.

### v1 read literally

v1 gives one README per repo, not a dependency list. The graph below is derived from what those READMEs and the specs say each repo does: the authorize hook sits in OCPI token authorization (ocpi-emsp calls policy-engine), CDRs drive payment capture, EMAID tokens come from plug&charge, consent gates token push, and the model types live in `ocpi-emsp`. This is an inference, not measured code.

```
11 components, 11 repos

ADP (cycles): 
  CYCLE: consent <-> ocpi-emsp <-> payments <-> plugcharge <-> policy-engine

component                Ca  Ce     I     A    Dp  flag
policy-engine             4   1  0.20  0.05  0.75  zone of pain
plugcharge                3   1  0.25  0.05  0.70  zone of pain
payments                  3   1  0.25  0.05  0.70  zone of pain
consent                   2   1  0.33  0.05  0.62  zone of pain
telemetry                 2   1  0.33  0.05  0.62  zone of pain
ocpi-emsp                 7   4  0.36  0.05  0.59  zone of pain
planner                   1   2  0.67  0.05  0.28  
roaming-hubs              1   4  0.80  0.05  0.15  
api-gateway               1   6  0.86  0.05  0.09  
mobile                    0   1  1.00  0.05  0.05  
simulator                 0   2  1.00  0.05  0.05  

SDP violations (a component depends on a less stable one, I(dep) > I(self)):

  policy-engine (I=0.20) -> ocpi-emsp (I=0.36)
  plugcharge (I=0.25) -> ocpi-emsp (I=0.36)
  payments (I=0.25) -> ocpi-emsp (I=0.36)
  consent (I=0.33) -> ocpi-emsp (I=0.36)
  telemetry (I=0.33) -> ocpi-emsp (I=0.36)
```

Reading it: every service needs the model inside `ocpi-emsp` while `ocpi-emsp` calls each of them, so five repos form one cycle, they would release as one unit (the weekly-build problem), and the most depended-on component is concrete (zone of pain). The v2 split removes it by giving the model and each service API their own component.

## 4. What the numbers do not say

- **A is an estimate.** It is set from design intent (APIs and schemas near 1, deployables near 0.05). Replace it with measured abstract/total counts from code once repos exist (jdeps or ArchUnit for Kotlin, import-linter for Python).
- **Test-only edges.** Simulators are consumed as images over the wire and are not in the graph; conformance is guaranteed because both sides are generated from the same `hub-contracts` pin.
- **Infra, docs and specs-only repos** (`infra`, `infra-modules`, `docs`) are left out of the metrics; they have no code dependencies to measure.
- The consent family is modelled only where it touches EV_PNC (`consent-contracts`, `edevlet-bridge`, `testkit`).
- Treat the metrics as a heuristic, as the book does: the standard is arbitrary, the cycle check is not.

## 5. Re-run

```bash
python3 tools/packaging_check.py components.csv            # report
python3 tools/packaging_check.py components.csv --strict   # CI gate
```

Update `components.csv` in the same pull request as any new cross-repo dependency; reviewers read the diff of `packaging-check-output.txt`.
