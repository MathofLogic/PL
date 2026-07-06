# Propagation Logic — Specification, kernel build 2026.07

**Status:** map of a verified territory. Every table below is drawn from a
sealed run of `pl.py` (suite sha256[:16] `bfddc7d82986ba9b`, seed 20260702,
verdict **PASS/STIPULATED**, chain length 5, 20,780 enumeration checks).
Nothing in this document is asserted that the kernel did not verify. Where
the kernel stipulates, this document says so. A spec that outranked its own
kernel would be lying.

---

## 1. The Mechanism

One operator, constant across all systems:

```
P / G → Q
```

| Object | Definition |
|---|---|
| **P = (v, L)** | a loaded pattern: designation `v ∈ V`, load `L ∈ [0, ∞)`. `L = 0` is the seed state — no history, no bill. |
| **G** | a gradient: `Pattern → Pattern`, decomposing into a value rule (what happens to `v`) and a load rule (what it costs). |
| **C = (θ, T)** | context: coherence threshold θ and, when joules are quoted, an explicit temperature T. |
| **Q** | the propagated pattern, bill attached. |

**θ is live, not decorative.** `propagate` checks `Q.L ≤ θ`; an
over-threshold result *decoheres* — it is returned, flagged unavailable, and
unusable downstream. Verified: chaining AND at load 2.0 under θ = 25
decoheres at exactly op 12 (L = 26), where the arithmetic forces it.

Every formal system is a setting of the parameters **(V, G, θ)**. The laws
of the system are not axioms. They are outputs of the law engine, enumerated
at registration — a carrier whose enumerated laws contradict its declared
signature is refused at the gate.

## 2. Load Rules (stipulated; then self-registered)

| Operation | Load rule | Reading |
|---|---|---|
| AND | `L(P∧Q) = L(P) + L(Q)` | both maintained simultaneously |
| OR | `L(P∨Q) = min(L(P), L(Q))` | the cheapest alternative suffices |
| NOT | carrier-dependent | history is not erased by flipping |
| sequence | `Σ Lᵢ` | one worldline pays every step |
| parallel | `max Lᵢ` | walltime of the widest branch |
| erasure | `≥ kB·T·ln 2` per bit, **T explicit** | Landauer floor; the kernel has no bare constant at a hidden temperature |

**Self-description (CONDITIONAL):** the load arithmetic `(AND=+, OR=min)`
on `[0, ∞)` is the tropical semiring — the kernel's accounting layer is
itself a carrier in its own registry. Given the stipulated rules, the
correspondence is exact.

## 3. The Law Engine

Fifteen laws, each decided by complete enumeration over finite V (never
assumed, never looked up): LNC, LEM, DN, NoGlut, MP (material detachment),
commutativity / associativity / idempotence of AND and OR, both De Morgan
directions, distributivity, absorption. Continuous carriers are
property-tested under a declared seed, and failures are proved by a single
exhibited counterexample — the corpus method.

## 4. The Carrier Registry (as enumerated by the sealed run)

| Carrier | V | ¬(½) / gluts | D | LNC | LEM | DN | MP | laws | signature price |
|---|---|---|---|---|---|---|---|---|---|
| **CL2** classical | {0,1} | — | {1} | Y | Y | Y | Y | 15/15 | the L = 0 idealisation |
| **K3** strong Kleene | {0,½,1} | ¬½ = ½ | {1} | Y | **.** | Y | Y | 14/15 | LEM — the unique atlas-extremal lone sacrifice |
| **LP** Priest | {0,½,1} | ¬½ = ½ | {½,1} | **.** | Y | Y | **.** | 12/15 | glut designated; detachment is the price |
| **Ł3** Łukasiewicz | {0,½,1} | ¬½ = ½ | {1} | Y | Y | Y | Y | 11/15 | LEM returns; idempotence, distributivity, absorption pay |
| **G3** Gödel | {0,½,1} | ¬½ = 0 | {1} | Y | **.** | **.** | Y | 13/15 | intuitionistic fragment; DN is the sacrifice |
| **B3** weak Kleene | {0,½,1} | ¬½ = ½, ½ infectious | {1} | Y | **.** | Y | Y | 13/15 | nonsense propagates; absorption fails |
| **FDE** four-valued | {T,F,B,N} | ¬ swaps t/f | {T,B} | **.** | **.** | Y | **.** | 11/15 | gluts and gaps distinguished — the distinction K3 and LP each collapse |
| **FUZZY** | [0,1] | 1−x, min/max | graded | — | fails at 0.5 (exhibited) | Y | — | property-tested | De Morgan, distributivity, absorption hold |
| **PROB** | [0,1] | 1−x, AND=ab, OR=a+b−ab | — | — | — | Y | — | property-tested | independence **stipulated**; distributivity fails at a=b=c=½: 0.375 ≠ 0.4375 |
| **CALC** dual numbers | ℝ×ℝ | — | — | — | — | — | — | property-tested | Leibniz propagation ≡ derivative to 1e−5 vs central difference; **eps is signed gradient, load is non-negative cost — related by analogy, not identity** |
| **SCALE** running | 1/q additive | — | θ live | — | — | — | — | property-tested | see §5 |
| **TROP** load itself | [0,∞) | — | — | — | — | — | — | exact | the accounting, registered |

Reproduced catalogue headline (EMPIRICAL): K3 and Ł3 share V = {0, ½, 1};
LEM fails in one and is forced in the other. **The law is a property of G
on V, not a fact to look up.**

Atlas context (project chain): in the exhaustively enumerated space of all
354,294 conservative three-valued carriers, no carrier reaches 15/15; only
DN or LEM can ever be the lone sacrifice at the 14/15 frontier, and K3 is
the unique carrier whose lone sacrifice is LEM.

## 5. The Scale Carrier — gradients compose

A running quantity is stored in its **state variable**: the inverse.

```
Running(inv, E, b):    inv = 1/q at scale E
step(E'):  inv ← inv − b·log(E'/E)      value rule  (additive in 1/q)
           L   ← L + |b·log(E'/E)|      load rule   (AND: each step pays)
```

**Group law (EMPIRICAL, 1000 random paths):** staged and direct propagation
agree in value to 1e−12 relative. The scale map is a gradient because it
composes.

**State vs process (EMPIRICAL, 1000 wandering paths):** value is a state
function — it forgets the route. Load is a process function — the wandering
path never undercuts the direct one (triangle inequality on |b·Δlog E|).
The value tells you where you are; the bill tells you how you got there.

Calibration is a **stipulation**, stated as such: b_eff = 0.66986 anchors
1/α from 137.036 at m_e to 128.936 at M_Z (one-loop effective). An anchor,
not a prediction.

## 6. DRAS — De-Reification Axiom Standard

Every quantity carries its full scope: scale, temperature, method, baseline
— plus a ledger of every operation that produced it.

```
LQ = (value, eps, L, scope, ledger)
```

**Reification is permitted — and priced (FORCED):** `reify()` returns the
bare float and appends `REIFIED: scope erased` to the ledger, raising L by
one distinction. You may drop the scope. You may not drop it for free.

**The 0.5 test (STIPULATED heuristic):** for any binary claim, ask what the
value 0.5 would mean. A sensible answer means the domain is continuous and
the binary carrier is suppressing load history. An incoherent answer means
binary may fit — check the boundaries.

## 7. Verdict Calculus

Five tiers, strictly ordered:

```
FORCED > EMPIRICAL > CONDITIONAL > STIPULATED > UNPAID
```

FORCED means proved by complete enumeration or exact construction within a
stated scope. EMPIRICAL means property-tested under a declared seed or
cross-checked against independent computation. CONDITIONAL means exact
given a named stipulation. STIPULATED means a design choice, recorded.
UNPAID means explicitly not claimed.

**Weakest-link composition:** a composite verdict never outranks its
weakest component. The kernel applies this to itself: it contains
stipulations (the load rules, the tier order, the 0.5 test, its own scope),
so its honest verdict is **PASS/STIPULATED** — and that is what it reports.

## 8. The Chain

Every section of the audit seals a generation: `sha = H(sha_prev ‖ body)`.
The run verifies that its own five-generation chain replays intact and that
mutating any sealed generation breaks replay at that link. The kernel's
history is a verifiable structure, not a log. "Earlier" and "later" are
positions in accumulated seals.

## 9. What Is Not Claimed (UNPAID, listed on the bill)

- That the registry exhausts formal systems. Substructural proof theory,
  non-matrix semantics, and non-material conditionals enter through the
  same gate when built.
- That load equals physical energy without an implementation map.
  `landauer(bits, T)` is a floor for irreversible erasure, quoted only with
  T explicit.
- That the tier order is forced. It is the kernel's constitution — a
  stipulation the kernel cannot outrank.

---

**Reproduce:** `python3 pl.py` — exits 0 on a passing self-audit, writes
`pl_manifest.json` with every claim, every carrier's full law table, and
the sealed chain.

*P / G → Q. Calculemus — and check the receipt.*
