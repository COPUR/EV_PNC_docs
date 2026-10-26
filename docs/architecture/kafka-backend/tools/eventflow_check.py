#!/usr/bin/env python3
"""Event-flow checks for the EV_PNC Kafka topic catalogue (fitness functions for ADR-0008, 0010, 0013).

Usage: python3 eventflow_check.py topics.csv [--strict]   (--strict exits 1 on a rule failure or an undeclared cycle)

Rules checked:
  R1 one writer per topic and the owner is a known service (Single Writer)
  R2 every consumer is a known service and is not the owner
  R3 compacted topics have a key; no key is a personal identifier (VIN, plate, national ID, phone, email, name)
  R4 partitions are 6, 12 or 24 (growth by new topic version, not in-place expansion)
  R5 delete topics have a retention; compacted topics have none
  R6 personal data class never appears on a topic: only public or pseudonymous
  R7 event-flow graph (owner -> consumer): strongly connected components must be declared feedback loops
  R8 a compacted topic keyed by a person-level reference (driverRef, accountId) keeps one record per person,
     so its note must say the value is the full state of that person; otherwise key by the aggregate id
     (v0.2: added after the audit found grant-changed keyed by driverRef, which compaction would collapse
     to the last grant per driver)
"""
import csv, sys
from collections import defaultdict

SERVICES = {"ocpi-emsp", "hub-gateway", "plugcharge", "consent-registry", "consent-decision", "consent-audit", "edevlet-bridge",
            "policy-engine", "pricing", "payments", "planner", "telemetry", "loyalty", "invoicing",
            "pilot-analytics", "api-gateway"}
PII_KEYS = {"vin", "plate", "tckn", "vkn", "phone", "email", "name", "pan", "iban"}
PERSON_LEVEL_KEYS = {"driverref", "accountid"}
DECLARED_LOOPS = [frozenset({"planner", "telemetry"})]  # arrivals feed occupancy profiles, availability feeds planning

rows = list(csv.DictReader(open(sys.argv[1])))
fail = []
g = defaultdict(set)
for r in rows:
    t, o = r["topic"], r["owner"]
    cons = [c for c in r["consumers"].split(";") if c]
    if o not in SERVICES: fail.append(f"R1 {t}: unknown owner {o}")
    for c in cons:
        if c not in SERVICES: fail.append(f"R2 {t}: unknown consumer {c}")
        if c == o: fail.append(f"R2 {t}: owner consumes its own topic")
        g[o].add(c)
    if r["cleanup"] == "compact" and not r["key"]: fail.append(f"R3 {t}: compacted without key")
    if r["key"].lower() in PII_KEYS: fail.append(f"R3 {t}: personal identifier as key")
    if r["cleanup"] == "compact" and r["key"].lower() in PERSON_LEVEL_KEYS and "full" not in r["note"].lower():
        fail.append(f"R8 {t}: compacted on person-level key {r['key']} without a full-state value; key by the aggregate id")
    if int(r["partitions"]) not in (6, 12, 24): fail.append(f"R4 {t}: partitions {r['partitions']}")
    if (r["cleanup"] == "delete") == (not r["retention"]): fail.append(f"R5 {t}: cleanup {r['cleanup']} with retention '{r['retention']}'")
    if r["data_class"] not in ("public", "pseudonymous"): fail.append(f"R6 {t}: data class {r['data_class']}")
    if not cons: fail.append(f"R2 {t}: no consumer (orphan)")
topics_by_owner = defaultdict(list)
for r in rows: topics_by_owner[r["owner"]].append(r["topic"])

# R7 Tarjan SCC over service graph
idx, low, st, on, sccs, n = {}, {}, [], set(), [], [0]
def strong(v):
    idx[v] = low[v] = n[0]; n[0] += 1; st.append(v); on.add(v)
    for w in g[v]:
        if w not in idx: strong(w); low[v] = min(low[v], low[w])
        elif w in on: low[v] = min(low[v], idx[w])
    if low[v] == idx[v]:
        s = []
        while True:
            w = st.pop(); on.discard(w); s.append(w)
            if w == v: break
        if len(s) > 1: sccs.append(frozenset(s))
for v in sorted(set(g) | {c for cs in g.values() for c in cs}):
    if v not in idx: strong(v)
undeclared = [s for s in sccs if s not in DECLARED_LOOPS]
for s in undeclared: fail.append("R7 undeclared event loop: " + " <-> ".join(sorted(s)))

parts = sum(int(r["partitions"]) for r in rows)
print(f"{len(rows)} topics, {parts} partitions, {parts*3} replicas at RF 3 ({parts*3/3:.0f} per broker on 3 brokers)")
print("owners:", ", ".join(f"{o} ({len(t)})" for o, t in sorted(topics_by_owner.items())))
print("services with no topic as owner:", ", ".join(sorted(SERVICES - set(topics_by_owner))))
fan_in = defaultdict(int)
for r in rows:
    for c in r["consumers"].split(";"):
        if c: fan_in[c] += 1
print("topics consumed per service:", ", ".join(f"{s} {k}" for s, k in sorted(fan_in.items(), key=lambda x: -x[1])))
print("event loops (SCC):", [sorted(s) for s in sccs] or "none", "| declared:", [sorted(s) for s in DECLARED_LOOPS])
print("RULE FAILURES:" if fail else "all rules pass")
for f in fail: print("  ", f)
if "--strict" in sys.argv and fail: sys.exit(1)
