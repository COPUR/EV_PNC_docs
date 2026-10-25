#!/usr/bin/env python3
"""Component-level package metrics (Martin: ADP, SDP, SAP) for the EV_PNC set.

Usage: python3 packaging_check.py components.csv [--strict]   (--strict exits 1 on a cycle, an SDP violation or D' > 0.5)

Input columns: component, repo, kind, abstractness (design estimate, 0..1), depends_on (; separated).
Prints: cycles (ADP), I, A, D' per component, SDP violations, and a per-repo roll-up.
A is an estimate until real counts exist; replace it from code (e.g. jdeps / ArchUnit) in CI.
I = Ce / (Ca + Ce); D' = |A + I - 1|. Zone of pain: A and I both low. Zone of uselessness: both high.
"""
import csv, sys
from collections import defaultdict

rows = list(csv.DictReader(open(sys.argv[1])))
comp = {r["component"]: r for r in rows}
deps = {c: [d for d in r["depends_on"].split(";") if d] for c, r in comp.items()}
missing = {d for ds in deps.values() for d in ds if d not in comp}
if missing:
    sys.exit(f"unknown components: {sorted(missing)}")

# ADP: find cycles with Tarjan SCC
index, low, stack, on, sccs, n = {}, {}, [], set(), [], [0]
sys.setrecursionlimit(10000)
def strong(v):
    index[v] = low[v] = n[0]; n[0] += 1; stack.append(v); on.add(v)
    for w in deps[v]:
        if w not in index:
            strong(w); low[v] = min(low[v], low[w])
        elif w in on:
            low[v] = min(low[v], index[w])
    if low[v] == index[v]:
        scc = []
        while True:
            w = stack.pop(); on.discard(w); scc.append(w)
            if w == v: break
        if len(scc) > 1: sccs.append(sorted(scc))
for v in comp:
    if v not in index: strong(v)

ca = defaultdict(int)
for c, ds in deps.items():
    for d in ds: ca[d] += 1
met = {}
for c in comp:
    ce = len(deps[c]); a_in = ca[c]
    i = ce / (a_in + ce) if (a_in + ce) else 0.0
    a = float(comp[c]["abstractness"])
    met[c] = (a_in, ce, i, a, abs(a + i - 1))

print(f"{len(comp)} components, {len({r['repo'] for r in rows})} repos")
print("\nADP (cycles):", "none" if not sccs else "")
for s in sccs: print("  CYCLE:", " <-> ".join(s))
print(f"\n{'component':24}{'Ca':>3}{'Ce':>4}{'I':>6}{'A':>6}{'Dp':>6}  flag")
for c, (a_in, ce, i, a, d) in sorted(met.items(), key=lambda kv: kv[1][2]):
    flag = ""
    if d > 0.5 and a < 0.5 and i < 0.5: flag = "zone of pain"
    elif d > 0.5 and a >= 0.5 and i >= 0.5: flag = "zone of uselessness"
    elif d > 0.3: flag = "review"
    print(f"{c:24}{a_in:>3}{ce:>4}{i:>6.2f}{a:>6.2f}{d:>6.2f}  {flag}")
print("\nSDP violations (a component depends on a less stable one, I(dep) > I(self)):")
bad = [(c, d) for c, ds in deps.items() for d in ds if met[d][2] > met[c][2] + 1e-9]
print("  none" if not bad else "")
for c, d in bad: print(f"  {c} (I={met[c][2]:.2f}) -> {d} (I={met[d][2]:.2f})")

problems = bool(sccs) or bool(bad) or any(m[4] > 0.5 for m in met.values())
print("\nRepo roll-up (mean over components; I of a repo from its cross-repo edges):")
repos = defaultdict(list)
for c, r in comp.items(): repos[r["repo"]].append(c)
print(f"{'repo':34}{'comps':>6}{'Ca':>4}{'Ce':>4}{'I':>6}")
for repo, cs in sorted(repos.items()):
    ce = len({d for c in cs for d in deps[c] if comp[d]["repo"] != repo})
    cain = len({c2 for c2 in comp for c in cs if c in deps[c2] and comp[c2]["repo"] != repo and comp[c2]["repo"] != repo})
    i = ce / (ce + cain) if (ce + cain) else 0.0
    print(f"{repo:34}{len(cs):>6}{cain:>4}{ce:>4}{i:>6.2f}")

if "--strict" in sys.argv and problems:
    sys.exit("packaging check failed: cycle, SDP violation or D' > 0.5")
