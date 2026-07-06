# PL

**Propagation Logic — the MathofLogic core framework. One mechanism, a registry of verified carriers, an atlas of every three-valued logic, and a discipline for numbers that keep their receipts. Everything here is code-verified: running a file IS its audit.**

## The one idea

```
P / G → Q
```

A loaded pattern `P = (v, L)` — a value `v` in some value space `V`, plus a
load `L`: the accumulated cost of maintaining it — propagates through a
gradient `G` to a result `Q`, inside a context `C = (θ, T)` that can refuse
it. When `Q.L > θ`, the result **decoheres**: it comes back flagged
unavailable, unusable downstream. Not an error. A budget, enforced.

Everything in this repo is a setting of the parameters `(V, G, θ)`:

- Classical logic is `V = {0,1}` with the familiar tables — the `L = 0`
  idealisation, where maintaining a distinction is treated as free.
- Three-valued logics (Kleene, Łukasiewicz, Priest, Gödel…) are different
  gradient families on `V = {0, ½, 1}` — and their famous "laws" (excluded
  middle, non-contradiction, detachment) are not axioms to look up but
  **outputs**, enumerated from the tables at registration.
- A CI pipeline's walltime, a latency budget, a running physical constant,
  a probability, a derivative — each is another carrier, same mechanism.

The kernel's central verified headline: **K3 and Ł3 share the exact same
value space; excluded middle fails in one and is forced in the other. The
law is a property of `G` on `V`, not a fact about `V`.** That one result
is why "which logic are you assuming?" is a real engineering question and
not philosophy: the aggregation rule you pick for your telemetry *is* a
choice of `G`, and it *forces* different behaviour.

## Why an engineer should care

Your systems already run on non-classical logic; they just don't declare it.

- A health probe that **times out** did not observe DOWN. It observed
  nothing. Coerce that UNKNOWN to `False` — the common default — and your
  monitor asserts "the primary is down" from a probe that never returned.
  Strong Kleene (K3) handles this correctly *and provably*: it's in the
  registry with its 14/15 laws enumerated, and the demo exhibits the
  coercion bug by evaluation.
- A **NaN** in your metrics pipeline is weak Kleene (B3): one corrupted
  value infects every aggregate. Whether corruption poisons or gets
  rescued is a carrier choice — declare it.
- Your **CI walltime** is tropical arithmetic: sequence sums, parallel
  maxes, redundancy takes the min. The kernel registers its own cost
  accounting as a carrier and verifies it.
- A **latency SLO** is a live θ: chained retries decohere at exactly the
  op the arithmetic forces, and the refused result carries the shortfall
  as a bill (`demand()`), not a stack trace.
- A **dashboard number** ("CPU is 73%") is a reification: a value whose
  scope — window, host, method — was erased. DRAS lets you erase it, and
  prices the erasure on a ledger. You may drop the receipt. Not for free.

All five of those sentences are *asserted, not illustrated* in
`demos/diagnostics.py`, which boots the kernel (it refuses to boot on a
failed self-audit) and re-derives every claim from the kernel's own tables.

## What's in the box

Each suite is standalone, stdlib-only, and self-auditing: it enumerates or
property-tests every claim it makes, seals a tamper-evident hash chain,
writes a manifest, and exits nonzero if anything failed.

| file | what running it proves |
|---|---|
| `pl.py` | **The reference kernel.** The mechanism, the load rules (AND adds, OR takes min, sequence sums, parallel maxes), the law engine (15 laws decided by complete enumeration per carrier), 7 finite carriers registered (CL2, K3, LP, Ł3, G3, B3, FDE) plus property-tested continuous ones (fuzzy, probability, dual-number calculus, running-scale, tropical), DRAS, live θ, Landauer floors with T explicit, and a sealed 5-generation chain. 20,780 checks, ~0.05 s. Verdict: PASS/STIPULATED. |
| `atlas3.py` | **The Atlas.** Complete enumeration of all **354,294** conservative three-valued carriers — the entire space, not samples. Verified: no carrier reaches 15/15; only DN or LEM can ever be the lone sacrifice at the 14/15 frontier; K3 is the *unique* carrier whose lone sacrifice is LEM. 7.9M checks, ~2 s. |
| `carrier_verify.py` | **The independent cross-check.** Re-enumerates the carrier laws from scratch, with none of the kernel's code, and must agree with the library's claims. Exits 1 on any mismatch. |
| `pl_dras.py` | **DRAS demonstrations.** De-reification worked end-to-end: quantities with scope and ledgers, the 0.5 test applied to real claims, running constants as state-vs-process. |
| `workbook_verified.py` | **The verified workbook.** 51 claims from the workbook, each re-derived in code; 5 tempting overclaims declined inline. |
| `pl_guide_audit.py` | **The operating guide, shown not told.** Every behavioural claim in the guide re-derived by running code; the guide grades itself STIPULATED. |
| `demos/diagnostics.py` | **Computing applications**, all asserted: three-valued health checks, infectious telemetry, tropical pipelines, SLOs as live θ, DRAS for metrics, and a sealed demo chain replayed by the kernel's own `replay()`. |

## Quick start

Python ≥ 3.11. No dependencies. No install.

```bash
python pl.py                     # the kernel audits itself (~0.05 s)
python atlas3.py                 # enumerate all 354,294 carriers (~2 s)
python demos/diagnostics.py      # PL applied to running systems
python tests/run.py              # the whole gate: suites + seals + demos
```

Using the kernel from your own code goes through the boot gate:

```python
from demos.plboot import boot
pl = boot()                      # full self-audit runs; raises on failure

K3 = pl.REGISTRY["K3   strong Kleene"]
K3.OR(0.5, 1.0)                  # -> 1.0  (standby up settles it)

wall = pl.L_seq([2, pl.L_par([8, 3, 4]), 6])   # -> 16, the critical path

req = pl.propagate(pl.Pattern("rq", 0), retry_step, pl.Context(theta=300))
req.available                    # False once the budget is exhausted
```

A kernel that failed its own enumeration never gets used — that is the
whole point of the boot gate.

## The verdict discipline

Every claim in every suite carries a tier from a strict ladder:

```
FORCED > EMPIRICAL > CONDITIONAL > STIPULATED > UNPAID
```

FORCED means complete enumeration on the artifact; STIPULATED means a
declared convention; UNPAID means asserted with no evidence and priced at
zero. Composite verdicts take the **weakest link**, and every suite here
verdicts **PASS/STIPULATED** — never higher — because each contains
stipulations (the load rules, the tier order, the 0.5 test) and a map
that graded itself FORCED would be lying. Each suite also prints its
**non-claims**: what it does *not* assert (that the registry exhausts
formal systems, that load equals energy without an implementation map,
that the tier order is forced).

## The seals

Every suite hashes its own source (`suite_sha256_16`) and writes a
deterministic manifest with a replayable hash chain. The committed seals
live in `manifests/`; `tests/run.py` regenerates each one in a scratch
directory and requires **byte-identical** parity:

| suite | sealed sha256[:16] | verdict |
|---|---|---|
| `pl.py` | `bfddc7d82986ba9b` | PASS/STIPULATED, chain 5, 20,780 checks |
| `atlas3.py` | `ab59172abd6618cb` | PASS/STIPULATED, chain 4, 7,923,327 checks |
| `pl_guide_audit.py` | `318db3aa0606a917` | PASS, guide tier STIPULATED, chain 5 |
| `workbook_verified.py` | (manifest committed) | PASS/STIPULATED, 51 claims |

Edit one character of a suite and the sha changes: a modified instrument
must announce itself as a new instrument and re-cut its seal on purpose.
That is what "everything code verified" means here — not that tests exist,
but that the *documents* (`PL_SPEC.md`, the workbook, the guide) are maps
of sealed runs, asserting nothing their kernels did not compute.

## Repository map

```
pl.py                    the reference kernel (sha-sealed; do not edit casually)
atlas3.py                the three-valued atlas
carrier_verify.py        independent cross-check of the carrier laws
pl_dras.py               DRAS demonstrations
workbook_verified.py     the workbook, claim by claim, in code
pl_guide_audit.py        the operating guide's audit
PL_SPEC.md               the spec — a map of the sealed kernel run
manifests/               committed seals; the gate enforces byte-parity
demos/                   plboot.py (boot gate) + diagnostics.py (computing)
tests/run.py             suites + seals + cross-check + demos
docs/SOURCE_NOTES.md     provenance: what was verified, what was added
.github/workflows/       CI runs the full gate on every push and PR
```

## Relation to the other MathofLogic repos

/PL is the core: the mechanism, the carriers, the atlas, the verification
discipline. The **/rigor** repo applies the same vocabulary to auditing —
code architecture (`audit arch`, resistance, delta, testimpact) and
scientific papers (the Rigor Suite) — and depends on /PL only for its
concepts, not its code. Each repo stands alone and passes its own gate.

## License

MIT. Trust infrastructure should not be paywalled.
