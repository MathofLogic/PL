#!/usr/bin/env python3
"""
demos/diagnostics.py — Propagation Logic pointed at running systems.
==========================================================================
Six demonstrations, all on the booted kernel (see plboot.py), all
asserted. Nothing below is illustrated by prose alone; every claim is
recomputed from the kernel's own carrier tables and machinery, and the
demo exits nonzero if any assertion fails. The tiers are the kernel's.

  D1  UNKNOWN is a value, not a missing boolean   (K3, health checks)
  D2  corrupted telemetry is infectious            (B3 vs K3, aggregation)
  D3  pipeline walltime is tropical arithmetic     (L_seq / L_par / L_or)
  D4  an SLO is a live theta: budget exhaustion is decoherence, not error
  D5  DRAS for metrics: a dashboard number is a priced reification
  D6  the demo seals its own chain and replays it

Run:  python demos/diagnostics.py        (exit 0 = every claim held)
"""
import json, sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from plboot import boot

pl = boot()                       # the kernel re-audits itself, or we stop
print("  kernel booted on a passing self-audit "
      f"(verdict PASS, {len(pl.REGISTRY)} carriers live)\n")

RESULTS, FAILED = [], []


def claim(tier, statement, ok):
    RESULTS.append({"tier": tier, "statement": statement, "ok": bool(ok)})
    if not ok:
        FAILED.append(statement)
    print(f"  [{tier:<11}][{'PASS' if ok else 'FAIL'}] {statement[:96]}")


def sect(t):
    print(f"\n{'=' * 74}\n{t}\n{'=' * 74}")


Z, H, U = 0.0, 0.5, 1.0           # down, unknown, up
K3 = pl.REGISTRY["K3   strong Kleene"]
B3 = pl.REGISTRY["B3   weak Kleene"]

# ── D1: health checks ────────────────────────────────────────────────────
sect("D1  UNKNOWN is a value, not a missing boolean (K3 health checks)")

# A probe that timed out did not observe DOWN. It observed nothing.
primary, standby = H, U           # primary probe timed out; standby is up
claim("FORCED",
      "service availability = OR(primary=UNKNOWN, standby=UP) = UP: one "
      "live replica settles it even with a timed-out probe (K3 OR table)",
      K3.OR(primary, standby) == U)
claim("FORCED",
      "both-replicas-healthy = AND(UNKNOWN, UP) = UNKNOWN: the pair claim "
      "stays open until the probe answers (K3 AND table)",
      K3.AND(primary, standby) == H)
claim("FORCED",
      "LEM fails at the timeout: OR(x, not-x) at x=UNKNOWN evaluates to "
      "UNKNOWN, not designated - a dashboard asserting 'up or down' about "
      "a timed-out probe asserts what was never checked",
      K3.OR(H, K3.neg(H)) == H and H not in K3.D)

# The classical-coercion bug: mapping UNKNOWN -> DOWN (the common default)
coerce = lambda x: Z if x == H else x
claim("FORCED",
      "the coercion bug, exhibited: forcing UNKNOWN->DOWN makes NOT(probe) "
      "come out TRUE - the monitor now claims 'primary is down' from a "
      "probe that never returned. Divergence from K3 proved by evaluation",
      (lambda cl2: cl2.neg(coerce(primary)) == U and K3.neg(primary) == H)
      (pl.REGISTRY["CL2  classical"]))

# ── D2: telemetry aggregation ───────────────────────────────────────────
sect("D2  Corrupted telemetry is infectious (B3) - choose your carrier")

claim("FORCED",
      "under weak Kleene (B3), one corrupted metric poisons any aggregate: "
      "OR(corrupt, UP) = corrupt and AND(corrupt, UP) = corrupt - the "
      "NaN-propagation your metrics pipeline already has, as a logic",
      B3.OR(H, U) == H and B3.AND(H, U) == H)
claim("FORCED",
      "under strong Kleene (K3) the same aggregate is rescued: OR(corrupt, "
      "UP) = UP. Same V = {0, 1/2, 1}, different G, different forced "
      "behaviour - the aggregation rule is a carrier CHOICE, so declare it",
      K3.OR(H, U) == U)

# ── D3: pipeline walltime is tropical ───────────────────────────────────
sect("D3  CI walltime is the load calculus (sequence sums, parallel maxes)")

fetch, compile_, lint, typecheck, test = 2.0, 8.0, 3.0, 4.0, 6.0
wall = pl.L_seq([fetch, pl.L_par([compile_, lint, typecheck]), test])
claim("FORCED",
      "pipeline fetch(2) -> [compile(8) || lint(3) || typecheck(4)] -> "
      f"test(6): walltime = seq(2, par(8,3,4), 6) = {wall} - the critical "
      "path, computed by the kernel's load rules, equals 16",
      wall == 16.0)
claim("FORCED",
      "a warm artifact cache is an OR: L(rebuild=8 v cache-hit=1) = "
      f"{pl.L_or(8.0, 1.0)} - the cheapest alternative suffices; "
      "redundancy lowers the bill exactly min-wise",
      pl.L_or(8.0, 1.0) == 1.0)
claim("CONDITIONAL",
      "this accounting (AND=+, OR=min on [0,inf)) is the tropical "
      "semiring - the kernel verifies this as its own self-description "
      "claim: the cost model your scheduler uses is itself audited",
      any("tropical semiring" in c["statement"] and c["verified"]
          for c in pl.MANIFEST))

# ── D4: theta is an SLO ─────────────────────────────────────────────────
sect("D4  An SLO is a live theta - budget exhaustion is decoherence")

budget = pl.Context(theta=300.0)          # 300 ms latency budget
retry = lambda P, ctx=None: pl.Pattern(P.v, P.L + 45.0)   # each retry: 45 ms
P = pl.Pattern("request", 0.0)
fired_at = None
for op in range(1, 20):
    P = pl.propagate(P, retry, budget)
    if not P.available:
        fired_at = op
        break
claim("FORCED",
      "chaining 45 ms retries under theta = 300 ms decoheres at exactly "
      f"op {fired_at} (L = {P.L:.0f} > 300), where the arithmetic forces "
      "it - the timeout is not an error code, it is the context refusing "
      "the pattern; demand() prices the shortfall at "
      f"{P.demand(budget.theta):.0f} ms",
      fired_at == 7 and P.L == 315.0 and P.demand(budget.theta) == 15.0)
claim("FORCED",
      "the decohered pattern is flagged unusable downstream (available="
      "False, tagged 'decoherent') - you cannot silently keep computing "
      "on a result the budget already refused",
      P.available is False and "decoherent" in P.tags)

# ── D5: DRAS for metrics ────────────────────────────────────────────────
sect("D5  A dashboard number is a priced reification (DRAS)")

cpu = pl.LQ(0.73, L=0.0,
            scope=(("window", "60 s"), ("host", "web-3"),
                   ("method", "ewma"), ("sampled-T", "container cgroup")),
            ledger=("seeded from node exporter",))
bare, priced = cpu.reify()
claim("FORCED",
      f"'CPU is 73%': reify() hands the dashboard its bare {bare} and "
      "appends 'REIFIED: scope erased' to the ledger; L rises "
      f"{cpu.L:.0f} -> {priced.L:.0f}. You may drop the window, host and "
      "method. You may not drop them for free",
      priced.L == cpu.L + 1.0 and "REIFIED: scope erased" in priced.ledger)
claim("STIPULATED",
      "the 0.5 test on ops claims: 'the deploy is safe' -> " +
      pl.half_test("deploy safe", True)[:11] + " (safety is graded; a "
      "binary badge suppresses load history). 'the feature flag is on' "
      "-> binary may fit (check the boundaries: propagation delay)",
      pl.half_test("deploy safe", True).startswith("REIFICATION")
      and pl.half_test("flag on", False).startswith("binary"))
claim("CONDITIONAL",
      "log retention has a physical floor: erasing 1 GiB of audit log "
      "irreversibly at T = 300 K costs at least "
      f"{pl.landauer(8 * 2**30, 300):.2e} J (Landauer, T stated - the "
      "kernel quotes no joule at a hidden temperature)",
      pl.landauer(8 * 2**30, 300) > 0)

# ── D6: the demo seals its own history ──────────────────────────────────
sect("D6  The demo's chain, sealed and replayed")

import hashlib
CHAIN = []


def seal(body):
    prev = CHAIN[-1]["sha"] if CHAIN else "GENESIS"
    sha = hashlib.sha256((prev + json.dumps(body, sort_keys=True))
                         .encode()).hexdigest()[:16]
    CHAIN.append({**body, "sha_prev": prev, "sha": sha})


for i, r in enumerate(RESULTS):
    seal({"gen": i, "claim": r["statement"][:60], "ok": r["ok"]})
tampered = json.loads(json.dumps(CHAIN))
tampered[2]["ok"] = not tampered[2]["ok"]
claim("FORCED",
      f"chain of {len(CHAIN)} demo claims replays intact under the "
      "kernel's own replay(); flipping one sealed verdict breaks replay "
      "at that link - the demo's history is a verifiable structure",
      pl.replay(CHAIN) and not pl.replay(tampered))

# ── verdict ─────────────────────────────────────────────────────────────
counts = {}
for r in RESULTS:
    counts[r["tier"]] = counts.get(r["tier"], 0) + 1
print(f"\n{'=' * 74}")
print(f"  DIAGNOSTICS DEMO {'PASSED' if not FAILED else 'FAILED'}   "
      + "  ".join(f"{k}:{v}" for k, v in sorted(counts.items())))
print("  weakest link: STIPULATED (the 0.5 test is a heuristic; the demo")
print("  cannot outrank its weakest claim). P / G -> Q - check the receipt.")
print(f"{'=' * 74}")
sys.exit(1 if FAILED else 0)
