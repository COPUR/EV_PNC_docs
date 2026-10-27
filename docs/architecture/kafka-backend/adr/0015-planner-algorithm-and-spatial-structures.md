# ADR-0015: Planner algorithm: layered-DAG dynamic programme; spatial lookups from libraries, not from teaching code

**Status:** proposed (accept on card X-01; benchmark gate on P3-02) · **Date:** 2026-10-26

**Context.** The planner ranks plans by total time = driving + charging + expected queue (CP-NAV-001), keeps a reserve SoC on sparse segments (CP-NAV-004, A1), re-plans when a better plan beats the current one by [5] minutes or the next EVSE fails (CP-NAV-003), and runs on the main route plus four alternative families (CP-GEO-001). The deck says "stops by DP". Card P3-02 (8 points) is the stop optimiser; its criteria already say "state = stop × SOC bucket" and "500 km route in under 2 s", which this ADR confirms and tightens. EVSEs near a corridor are tagged within 2 km (CP-GEO-002). The TheAlgorithms-Java notes list verified high-severity bugs in the tree and graph code (k-d tree, Johnson, A*), so none of it is a dependency.

**Problem shape.** A corridor is ordered by route kilometre, so the graph of candidate stops is a DAG as long as the planner only moves forward (an assumption; a backtrack to a better charger needs a second pass). Costs are non-negative. Queue time depends on the arrival time, which makes edge cost time-dependent; allowing the driver to wait at a site keeps the travel-time function FIFO, so label-setting methods stay valid (I, standard result).

**Options.**

| Option | For | Against |
|---|---|---|
| A DP over (site, leave-SoC bucket) on the DAG, min time per state | Simple, fast, easy to test with an oracle | SoC discretisation error |
| B Pareto label-setting on (time, SoC) | Exact in both dimensions | More code, labels can grow |
| C OR-Tools routing or CP-SAT | Handles side constraints | Heavier than the problem; slow to explain |
| D Dijkstra on the full graph | Familiar | Needless on a DAG |

**Decision.**
1. Start with A. Buckets of [2]% SoC. Candidate "charge-to" levels are those needed to reach each of the next K sites plus a cap [80]%. Run once per family. Estimated cost is about 10⁶ relaxations per family (N≈200 sites, L≈50 buckets, K≈10; an estimate to be measured).
2. Move to B only if replaying recorded trips shows A's error above [2] minutes. C stays optional for ferry timetables or multi-vehicle cases.
3. Re-planning runs the same DP from the current position and SoC. If A* is ever used it needs an admissible heuristic (remaining km over maximum speed) and a closed set.
4. **Oracle test:** brute-force enumeration of stop subsets on small corridors must equal the DP; property tests on reserve SoC and on FIFO.
5. **Budget:** card P3-02 already requires a 500 km route in under 2 s; apply that to each family. Proposed addition: p95 re-plan server time within [1 s] on the five-family corridor graph. A failing benchmark blocks the merge.
6. **Spatial:** PostGIS GiST for the corridor and EVSE tags; JTS STRtree in memory; H3 resolution 8 for privacy cells. No k-d tree from teaching libraries.
7. **Entity identity across feeds** (K1 count): union-find with union by rank and path compression, after blocking on H3 cell, normalised operator and connector, with a human sample of merges. Oracle: connected components by BFS.
8. **Queue baseline:** historical profile by weekday, hour and peak flag, blended with live occupancy and labelled live or historical (CP-IDLE-001). A learned model is a later extraction (repo-plan trigger).
9. **Library policy:** JDK collections, Caffeine and a Redis-compatible cache for general structures; own code only for the DP, union-find and the STT conformance checks. Audit any algorithm taken from a teaching library, and write the oracle test before first use.

**Consequences.**
- OR-Tools is not needed for the pilot. If the Planner agent wants it for ferry timetabling, it is a bounded add-on.
- The energy model and weather inputs are separate inputs to the DP (`tb_energy_model.py` supplies fitted factors; mean cross-validation error 5.6%).
- The DP is a pure function, so it is testable without Kafka and can move to Kotlin later with the same oracle.

**Sources.** algorithms-data-structures (DP four steps, shortest paths by weight sign and graph shape, union-find, hashing); thealgorithms-java-trees-graph-structures (review findings, SCC, Kahn); liang-java-data-structure-implementations (hashing, graphs); `corridor-pilot/spec.md`; `engineering-briefing/mobile-app/README.md`.
