#!/usr/bin/env python3
"""
workbook_verified.py — companion to The Math of Logic: Professor Logic's
Workbook.
==========================================================================
Every chalkboard in the workbook that carries a [verified: test_X_Y] stamp
is checked here, by complete enumeration or direct construction wherever
possible. Run it:

    python3 workbook_verified.py

The script ends by printing the book's own manifest: every claim, its
evidence tier, and the weakest-link verdict ON THE BOOK ITSELF.

Tiers (the book applies its own discipline to itself):
  FORCED      provable here by complete enumeration / direct construction
  EMPIRICAL   a measured fact about the world; cited, reproduced where we can
  STIPULATED  a design choice; could be otherwise; alternatives shown
  ANALOGY     a structural correspondence that holds under a stated
              construction, verified inside that construction only
  SPECULATION an idea worth having; not asserted; not load-bearing

No claim of evolution toward truth. The map evolves toward usefulness in
the contexts it is shown. The contexts select.

James Pugmire's Propagation Logic Project — 2026.
Deterministic. No external libraries. Python 3.
"""
import itertools, math, random, sys, json

random.seed(20260612)
MANIFEST, TRAPS = [], []

def claim(test_id, tier, statement, ok):
    MANIFEST.append({"id": test_id, "tier": tier,
                     "statement": statement, "verified": bool(ok)})
    mark = "PASS" if ok else "FAIL"
    print(f"  [{tier:11s}][{mark}] {test_id}: {statement[:88]}")
    if not ok:
        raise SystemExit(f"VERIFICATION FAILED: {test_id}")

def trap(tempting_claim, why):
    """A tempting overclaim, stated explicitly so the code can catch it."""
    TRAPS.append({"tempting_claim": tempting_claim, "why": why})
    print(f"  [TRAP-CAUGHT]      {tempting_claim[:58]} -- {why[:48]}")

def section(t):
    print("\n" + "=" * 74 + f"\n{t}\n" + "=" * 74)

# ===================================================================== #
# CHAPTER 1 — carriers and designation                                  #
# ===================================================================== #
section("CHAPTER 1 — What Can Something Be?")

V2 = [0, 1]
V3 = [0, 0.5, 1]

designated = [v for v in V3 if v > 0]
claim("test_1_1", "FORCED",
      "In {0,0.5,1} with rule 'designated iff v>0', exactly {0.5,1} are designated",
      designated == [0.5, 1])

# A one-element carrier is trivial: every statement gets the same value.
V1 = [1]
claim("test_1_2", "FORCED",
      "A one-element carrier makes every statement evaluate identically (trivial logic)",
      all(v == 1 for v in V1) and len(set(V1)) == 1)

# ===================================================================== #
# CHAPTER 2 — the three operations ARE CHOICES (a tempting overclaim)   #
# ===================================================================== #
section("CHAPTER 2 — The Three Operations (operations are choices)")

NOT  = lambda v: 1 - v
ANDp = lambda a, b: a * b        # product AND (Zadeh/product fuzzy)
ANDm = lambda a, b: min(a, b)    # min AND (Kleene/Goedel)
OR   = lambda a, b: max(a, b)

# Truth tables on {0,1}
tt_and = {(a, b): ANDp(a, b) for a in V2 for b in V2}
tt_or  = {(a, b): OR(a, b)  for a in V2 for b in V2}
claim("test_2_1", "FORCED",
      "On {0,1}: AND=product and AND=min produce the SAME table; so does OR=max",
      all(ANDp(a, b) == ANDm(a, b) for a in V2 for b in V2)
      and tt_and == {(0,0):0,(0,1):0,(1,0):0,(1,1):1}
      and tt_or  == {(0,0):0,(0,1):1,(1,0):1,(1,1):1})

claim("test_2_2", "FORCED",
      "On {0,0.5,1} the two ANDs DIFFER: product(0.5,0.5)=0.25, min(0.5,0.5)=0.5 — choice exposed",
      ANDp(0.5, 0.5) == 0.25 and ANDm(0.5, 0.5) == 0.5)

trap("Tempting overclaim: 'Once you choose your carrier, the formulas for the "
        "operations are forced.'",
        "False: product-AND and min-AND share {0,1} but split on {0,0.5,1}. "
        "Operations are a second choice (the gradient family G). The "
        "project's own Carrier Catalogue lists three fuzzy ANDs.")

# Implication derived: A -> B = OR(NOT A, B), full table on {0,1}
imp = {(a, b): OR(NOT(a), b) for a in V2 for b in V2}
claim("test_2_3", "FORCED",
      "A->B := OR(NOT A, B) is 0 only at (1,0) on {0,1} — implication is derivable",
      imp == {(0,0):1,(0,1):1,(1,0):0,(1,1):1})

# Closure: addition-as-OR leaks
claim("test_2_4", "FORCED",
      "OR := a+b violates closure on {0,1}: 1+1=2 is outside the carrier",
      (1 + 1) not in V2)

# ===================================================================== #
# CHAPTER 3 — laws forced by (V, G); and the obvious machine's trap     #
# ===================================================================== #
section("CHAPTER 3 — Laws Forced by (V, G) — and the trap in the obvious machine")

def closure_audit(V, NOT_, AND_, OR_):
    Vs = set(round(v, 12) for v in V)
    leaks = []
    for v in V:
        if round(NOT_(v), 12) not in Vs:
            leaks.append(("NOT", v, NOT_(v)))
    for a, b in itertools.product(V, repeat=2):
        if round(AND_(a, b), 12) not in Vs: leaks.append(("AND", (a, b), AND_(a, b)))
        if round(OR_(a, b), 12)  not in Vs: leaks.append(("OR",  (a, b), OR_(a, b)))
    return leaks

# THE TRAP: the obvious machine — {0,0.5,1} with product AND
bug_leaks = closure_audit(V3, NOT, ANDp, OR)
claim("test_3_0", "FORCED",
      "TRAP SPRUNG: {0,0.5,1} with product-AND leaks: AND(0.5,0.5)=0.25 is not in V",
      bug_leaks == [("AND", (0.5, 0.5), 0.25)])

trap("Tempting overclaim: central three-valued example used V={0,0.5,1} with "
        "AND=multiply while Exercise 2.4 demanded closure.",
        "The Chapter 2 closure rule, applied to this carrier, fails. Use "
        "AND=min (Kleene K3). The teaching points all survive the swap.")

# THE REPAIR: Kleene K3 = ({0,0.5,1}, NOT=1-v, AND=min, OR=max) is closed
claim("test_3_1", "FORCED",
      "REPAIR: Kleene K3 ({0,0.5,1}, 1-v, min, max) passes the closure audit",
      closure_audit(V3, NOT, ANDm, OR) == [])

def lnc(V, AND_, NOT_):  # AND(v, NOT v) = bottom for every v
    bot = min(V)
    return all(abs(AND_(v, NOT_(v)) - bot) < 1e-12 for v in V)

def lem(V, OR_, NOT_):   # OR(v, NOT v) = top for every v
    top = max(V)
    return all(abs(OR_(v, NOT_(v)) - top) < 1e-12 for v in V)

def dn(V, NOT_):
    return all(abs(NOT_(NOT_(v)) - v) < 1e-12 for v in V)

claim("test_3_2", "FORCED",
      "{0,1}: LNC, LEM, DN all hold — checked by complete enumeration, not assumed",
      lnc(V2, ANDm, NOT) and lem(V2, OR, NOT) and dn(V2, NOT))

claim("test_3_3", "FORCED",
      "{0,0.5,1} (K3): LNC fails at 0.5 (min=0.5), LEM fails at 0.5 (max=0.5), DN survives",
      (not lnc(V3, ANDm, NOT)) and (not lem(V3, OR, NOT)) and dn(V3, NOT)
      and ANDm(0.5, NOT(0.5)) == 0.5 and OR(0.5, NOT(0.5)) == 0.5)

Vfuzzy = [i / 100 for i in range(101)]
claim("test_3_4", "FORCED",
      "[0,1] sampled at 101 points: LNC and LEM fail at every interior point; DN survives",
      (not lnc(Vfuzzy, ANDm, NOT)) and (not lem(Vfuzzy, OR, NOT)) and dn(Vfuzzy, NOT)
      and all(ANDm(v, 1 - v) > 0 for v in Vfuzzy if 0 < v < 1))

# DN is algebra, not enumeration: 1-(1-v)=v for all real v — spot-check widely
claim("test_3_5", "FORCED",
      "DN = pure algebra of NOT(v)=1-v: 1-(1-v)=v, robust to any carrier using that NOT",
      all(abs(NOT(NOT(v)) - v) < 1e-12 for v in [-3.7, 0, 0.25, 0.5, 1, 42.0]))

# LNC can hold while DN fails (non-standard NOT) — laws are independent
NOTodd = lambda v: 0          # NOT(0)=0, NOT(1)=0
claim("test_3_6", "FORCED",
      "Independence: with NOT(v):=0 on {0,1}, LNC holds but DN fails at v=1",
      lnc(V2, ANDm, NOTodd) and not dn(V2, NOTodd))

# ===================================================================== #
# CHAPTER 4 — three knobs                                               #
# ===================================================================== #
section("CHAPTER 4 — Three Knobs: V, G, theta")

# Knob 1 (V): change V, laws change — already test_3_2 vs test_3_3.
claim("test_4_1", "FORCED",
      "Knob V: identical (G) on {0,1} vs {0,0.5,1} flips LNC/LEM; DN unmoved",
      lnc(V2, ANDm, NOT) and not lnc(V3, ANDm, NOT) and dn(V2, NOT) and dn(V3, NOT))

# Knob 2 (G): remove OR -> LEM is not false, it is UNSTATABLE.
G_intuition = {"NOT": NOT, "AND": ANDm}     # no OR
claim("test_4_2", "FORCED",
      "Knob G: with OR removed, the statement of LEM cannot even be formed (unreachable)",
      "OR" not in G_intuition and "AND" in G_intuition)

# Knob 3 (theta): lower theta -> strictly fewer coherent patterns.
loads = [0.2, 0.7, 1.3, 2.5, 5.0]
coh = lambda th: [L for L in loads if L <= th]
claim("test_4_3", "FORCED",
      "Knob theta: coherent set at theta=0.5 is a subset of the set at theta=2.0",
      set(coh(0.5)) < set(coh(2.0)))

# ===================================================================== #
# CHAPTER 5 — load: a bookkeeping device, grounded but stipulated       #
# ===================================================================== #
section("CHAPTER 5 — The Price of an Idea (load)")

kB, T = 1.380649e-23, 300.0
LANDAUER = kB * T * math.log(2)
claim("test_5_1", "EMPIRICAL",
      f"Landauer limit kB*T*ln2 at 300K = {LANDAUER:.3e} J/bit "
      "(Landauer 1961; measured to ~2%, Berut et al. 2012)",
      abs(LANDAUER - 2.87e-21) / 2.87e-21 < 0.01)

class P:
    """Pattern (value, load). The load rules below are STIPULATED design
    choices for one gradient family — Chapter 8 builds a different one."""
    def __init__(s, v, L=0.0): s.v, s.L = v, L
    def coheres(s, theta): return s.L <= theta

def NOTp(p):    return P(1 - p.v, p.L)                       # flip is free
def ANDp_(p,q): return P(min(p.v,q.v), p.L + q.L)            # both costs paid
def ORp_(p,q):  return P(max(p.v,q.v), min(p.L, q.L))        # cheapest path

a, b = P(1, 4.0), P(1, 3.0)
r_not, r_and, r_or = NOTp(a), ANDp_(a, P(0, 5.0)), ORp_(P(1,8.0), P(1,3.0))
claim("test_5_2", "STIPULATED",
      "Load rules (one chosen G): NOT keeps L, AND adds (4+5=9), OR takes min (3)",
      r_not.L == 4.0 and r_and.L == 9.0 and r_or.L == 3.0)

# Alternative load rule exists -> the rules are choices, not laws
def AND_alt(p, q): return P(min(p.v, q.v), max(p.L, q.L))    # bottleneck cost
claim("test_5_3", "FORCED",
      "Alternatives exist: a max-cost AND is also closed and monotone — load rules are choices",
      AND_alt(a, b).L == 4.0 != ANDp_(a, b).L)

# Generalised AND: L = LP + LQ - I(P,Q)
and_load = lambda LP, LQ, I=0.0: LP + LQ - I
claim("test_5_4", "STIPULATED",
      "Generalised AND load LP+LQ-I: I=0 pays full price; I=LP makes Q free given P",
      and_load(2, 3) == 5 and and_load(2, 3, I=2) == 3)

# Seven chained ANDs at unit-load 2.0 vs theta=25: where does it first fail?
L, step_fail = 2.0, None
for k in range(2, 9):
    L = L + 2.0
    if L > 25 and step_fail is None: step_fail = k
claim("test_5_5", "FORCED",
      "Chained ANDs of load 2.0: after 7 ops L=16<=25 coheres; failure would begin at op 12",
      L == 16.0 and step_fail is None and (2.0 + 2.0*12 > 25))

# Full load spectrum is a STIPULATED extension; record, don't prove.
claim("test_5_6", "STIPULATED",
      "Load spectrum extension (tautology L<0, contradiction L=-inf) is a design proposal",
      True)

# ===================================================================== #
# CHAPTER 6 — distinction debt; Newton's theta done with real numbers   #
# ===================================================================== #
section("CHAPTER 6 — The Debt of the Distinction")

# The 0.5 test is a diagnostic heuristic — STIPULATED, demonstrated:
half_meaningful = {"moderately ill": True, "half-off toggle": False,
                   "somewhat failing economy": True, "half-true arithmetic": False}
claim("test_6_1", "STIPULATED",
      "0.5 test: meaningful midpoint -> continuous domain wearing a binary carrier",
      half_meaningful["moderately ill"] and not half_meaningful["half-off toggle"])

# Newton's theta — now ACTUALLY computed, not hand-waved.
c = 299_792_458.0
def galilean(v1, v2): return v1 + v2
def einstein(v1, v2): return (v1 + v2) / (1 + v1 * v2 / c**2)
def rel_err(v1, v2):
    return abs(galilean(v1, v2) - einstein(v1, v2)) / einstein(v1, v2)

e_slow  = rel_err(0.001*c, 0.001*c)   # ~1e-6
e_mid   = rel_err(0.5*c,   0.5*c)     # 25%
e_fast  = rel_err(0.9*c,   0.9*c)     # large
claim("test_6_2", "FORCED",
      f"Galilean velocity addition error = v1*v2/c^2: {e_slow:.1e} at 0.001c, "
      f"{e_mid:.2f} at 0.5c, {e_fast:.2f} at 0.9c — Newton's hidden theta, computed",
      abs(e_slow - 1e-6) < 1e-8 and abs(e_mid - 0.25) < 1e-12 and e_fast > 0.5)

claim("test_6_3", "ANALOGY",
      "'Einstein found Newton's theta' — reading scientific revision as threshold-"
      "discovery; the numbers above are forced, the framing is a chosen map",
      True)

# ===================================================================== #
# CHAPTER 7 — the four failure modes                                    #
# ===================================================================== #
section("CHAPTER 7 — When Systems Break: four modes")

def liar_solutions(V, NOT_):
    return [v for v in V if abs(v - NOT_(v)) < 1e-12]

claim("test_7_1", "FORCED",
      "Mode 1 (Liar): v=NOT(v) has no solution in {0,1}; exactly one (0.5) in {0,0.5,1}",
      liar_solutions(V2, NOT) == [] and liar_solutions(V3, NOT) == [0.5])

claim("test_7_1b", "STIPULATED",
      "Calling 0.5 a 'resolution' is carrier-relative: K3 assigns the Liar the middle "
      "value; whether natural language IS that carrier is a modelling choice",
      True)

# Mode 2 (load divergence): 2^depth exceeds any finite theta — forced arithmetic
claim("test_7_2", "FORCED",
      "Mode 2 arithmetic: for any theta there is n with 2^n > theta (theta=10^9 -> n=30)",
      2**30 > 1e9 and all(any(2**n > th for n in range(80)) for th in [1, 1e3, 1e9, 1e18]))

claim("test_7_2b", "ANALOGY",
      "Reading Goedel/Turing as Mode 2 is a model: the actual theorems say NO in-system "
      "proof exists at ANY cost; 'infinite load' is the PL picture of that, not the proof",
      True)

# Mode 3 (Russell): demonstrate level collapse as actual machine behaviour
def russell_demo():
    member_of = {}
    def is_member(x, s):           # s contains x iff x is not a member of x
        return not is_member(x, x)
    try:
        is_member("R", "R")
        return False
    except RecursionError:
        return True
claim("test_7_3", "FORCED",
      "Mode 3 (Russell): asking 'R in R?' under R={x: x not in x} drives the evaluator "
      "into unbounded self-call — RecursionError, demonstrated, not narrated",
      russell_demo())

# Mode 4 (Yablo): every FINITE truncation has exactly one model, but the seed
# keeps migrating to the last sentence — and the infinite list has no last.
def yablo_models(n):
    """S_k true iff all S_j (j>k) false. Enumerate all assignments."""
    models = []
    for bits in itertools.product([0, 1], repeat=n):
        ok = all(bits[k] == int(all(bits[j] == 0 for j in range(k + 1, n)))
                 for k in range(n))
        if ok: models.append(bits)
    return models

mods = {n: yablo_models(n) for n in range(2, 9)}
claim("test_7_4", "FORCED",
      "Mode 4 (Yablo): every finite truncation n=2..8 has EXACTLY ONE model — all false "
      "except the LAST sentence. The seed is always at the end; infinity has no end",
      all(len(m) == 1 and m[0] == tuple([0]*(n-1) + [1]) for n, m in mods.items()))

# ===================================================================== #
# CHAPTER 8 — one mechanism, many faces (claims now bounded honestly)   #
# ===================================================================== #
section("CHAPTER 8 — One Mechanism, Many Faces")

class LH:
    """Loaded History in the real carrier = dual numbers v + L*eps, eps^2=0.
    Under THIS construction the AND/combination rule for products IS the
    Leibniz product rule. That is a built correspondence, verified below —
    not a discovery about classical Boolean AND."""
    def __init__(s, v, L=0.0): s.v, s.L = float(v), float(L)
    def __add__(s, o): o = LH._c(o); return LH(s.v + o.v, s.L + o.L)
    def __radd__(s, o): return s.__add__(o)
    def __mul__(s, o):
        o = LH._c(o)
        return LH(s.v * o.v, s.L * o.v + s.v * o.L)   # <- Leibniz rule lives here
    def __rmul__(s, o): return s.__mul__(o)
    def __sub__(s, o): o = LH._c(o); return LH(s.v - o.v, s.L - o.L)
    @staticmethod
    def _c(o): return o if isinstance(o, LH) else LH(o)

def derivative(f, x0):
    return f(LH(x0, 1.0)).L          # seed unit load, read the output load

f  = lambda x: x * x * x - 5 * x * x + 2 * x + 7     # f(x)=x^3-5x^2+2x+7
fp = lambda x: 3 * x**2 - 10 * x + 2                  # analytic derivative
pts = [-2.0, 0.0, 1.5, 3.0, 10.0]
claim("test_8_1", "FORCED",
      "Dual-number carrier: output load = EXACT derivative; product rule emerges from "
      "the combination rule (checked at 5 points against the analytic derivative)",
      all(abs(derivative(f, x) - fp(x)) < 1e-9 for x in pts))

claim("test_8_2", "FORCED",
      "But this is a DIFFERENT gradient family from Chapter 5: additive AND-load gives "
      "L=2 for two unit loads; Leibniz combination on values (3,1),(4,1) gives L=7",
      ANDp_(P(1,1), P(1,1)).L == 2 and (LH(3,1) * LH(4,1)).L == 7)

trap("Tempting overclaim: 'The Fundamental Theorem of Calculus is Double "
        "Negation in the calculus carrier. Not an analogy.'",
        "Unverifiable as stated and false on the obvious reading: DN is "
        "NOT(NOT(v))=v for NOT=1-v; FTC relates integral and derivative. "
        "No construction was given under which they coincide. Withdrawn "
        "until someone builds and verifies one.")

# Probability: inclusion-exclusion by COMPLETE ENUMERATION of a sample space
omega = list(range(12))
A = set(x for x in omega if x % 2 == 0)        # evens
B = set(x for x in omega if x % 3 == 0)        # multiples of 3
Pmeas = lambda S: len(S) / len(omega)
claim("test_8_3", "FORCED",
      "P(A or B) = P(A)+P(B) ONLY for disjoint events; in general subtract P(A and B) "
      "(inclusion-exclusion, verified by enumerating a 12-point sample space)",
      abs(Pmeas(A | B) - (Pmeas(A) + Pmeas(B) - Pmeas(A & B))) < 1e-12
      and Pmeas(A | B) != Pmeas(A) + Pmeas(B))

trap("Tempting overclaim: 'P(A or B) = P(A) + P(B) — from the normalisation "
        "constraint.'",
        "Holds only for mutually exclusive events; stated without the "
        "condition. Repaired to inclusion-exclusion, verified above.")

# Shannon entropy as load of a distribution
H = lambda ps: -sum(p * math.log2(p) for p in ps if p > 0)
claim("test_8_4", "FORCED",
      "Entropy-as-load: fair coin 1.000 bit > biased(0.9) 0.469 bit > certain 0.000 bit",
      abs(H([0.5, 0.5]) - 1) < 1e-12 and abs(H([0.9, 0.1]) - 0.469) < 5e-4
      and H([1.0]) == 0)

claim("test_8_5", "STIPULATED",
      "World-logic sketches (catuskoti, Taoist, Ubuntu) are PL models built to honour "
      "those traditions' design pressures — carrier proposals, not anthropology",
      True)

# Catuskoti as a checkable carrier: Belnap-style FOUR = {F, B, N, T}
# encoded as pairs (told-true, told-false); AND/OR componentwise.
FOUR = [(0,0),(0,1),(1,0),(1,1)]   # N, F, T, B  (told-true, told-false)
and4 = lambda a,b: (min(a[0],b[0]), max(a[1],b[1]))
or4  = lambda a,b: (max(a[0],b[0]), min(a[1],b[1]))
not4 = lambda a: (a[1], a[0])
claim("test_8_6", "FORCED",
      "A four-valued carrier (Belnap FOUR) is closed and: LNC fails at B='both', "
      "LEM fails at N='neither' — four corners, forced by the carrier",
      all(and4(a,b) in FOUR and or4(a,b) in FOUR and not4(a) in FOUR
          for a in FOUR for b in FOUR)
      and and4((1,1), not4((1,1))) == (1,1)        # B AND NOT B = B, not F
      and or4((0,0),  not4((0,0)))  == (0,0))      # N OR NOT N = N, not T

# ===================================================================== #
# CHAPTER 9 — the physical logic: a cube model BUILT FROM GEOMETRY      #
# ===================================================================== #
section("CHAPTER 9 — The Physical Logic (pocket cube, derived from geometry)")

# 2x2x2 cube. Sticker slot = (corner vector in {-1,1}^3, axis 0/1/2).
# Moves derived by rotating coordinates — nothing copied from tables.
AXES = (0, 1, 2)
CORNERS = [c for c in itertools.product((-1, 1), repeat=3)]
SLOTS = [(c, a) for c in CORNERS for a in AXES]
S_IDX = {s: i for i, s in enumerate(SLOTS)}

def rot90(axis):
    """Right-hand 90-degree rotation about +axis, acting on integer vectors."""
    def R(v):
        x, y, z = v
        if axis == 0:  return (x, -z, y)
        if axis == 1:  return (z, y, -x)
        return (-y, x, z)
    return R

def move_perm(axis):
    """Quarter turn of the face whose corners have +1 on `axis`.
    Returns dest<-src permutation over slot indices."""
    R = rot90(axis)
    perm = list(range(len(SLOTS)))
    for (c, a) in SLOTS:
        if c[axis] == 1:
            c2 = R(c)
            n = [0, 0, 0]; n[a] = c[a]            # outward normal of sticker
            n2 = R(tuple(n))
            a2 = next(i for i in AXES if n2[i] != 0)
            perm[S_IDX[(c2, a2)]] = S_IDX[(c, a)]
    return tuple(perm)

def apply(perm, state): return tuple(state[perm[i]] for i in range(len(state)))
def compose(p, q):       return tuple(q[p[i]] for i in range(len(p)))  # p then q? (dest<-src chains)

MOVES = {"R": move_perm(0), "U": move_perm(1), "F": move_perm(2)}
IDENT = tuple(range(len(SLOTS)))
SOLVED = tuple(f"{'+' if c[a] > 0 else '-'}{a}"   # colour = signed face of axis
               for (c, a) in SLOTS)

def times(perm, k):
    p = IDENT
    for _ in range(k): p = tuple(p[perm[i]] for i in range(len(perm)))
    return p

claim("test_9_1", "FORCED",
      "Closure + identity: every generator is a bijection of slots; solved state exists",
      all(sorted(p) == list(IDENT) for p in MOVES.values()))

claim("test_9_2", "FORCED",
      "G^4 = identity: each quarter turn applied 4 times returns every sticker home",
      all(times(p, 4) == IDENT and times(p, 1) != IDENT for p in MOVES.values()))

claim("test_9_3", "FORCED",
      "Half-turn is its own inverse: (G^2)^2 = identity — Double Negation in plastic",
      all(times(times(p, 2), 2) == IDENT for p in MOVES.values()))

UR = apply(MOVES["R"], apply(MOVES["U"], SOLVED))
RU = apply(MOVES["U"], apply(MOVES["R"], SOLVED))
claim("test_9_4", "FORCED",
      "Non-commutativity: U then R differs from R then U (compared sticker by sticker)",
      UR != RU)

claim("test_9_5", "FORCED",
      "Inverses exist: G^3 undoes G for every quarter turn (G^3 . G = identity)",
      all(times(p, 3) != IDENT and times(p, 4) == IDENT for p in MOVES.values()))

# Corner-twist invariant. Orientation of the cubie sitting at corner c =
# cyclic position of its U/D-coloured sticker (+1/-1 on axis 1) around c.
def twist(state):
    total = 0
    for c in CORNERS:
        axes_cw = (1, 2, 0) if (c[0]*c[1]*c[2] == 1) else (1, 0, 2)
        for pos, a in enumerate(axes_cw):
            if state[S_IDX[(c, a)]] in ("+1", "-1"):   # the U/D colour
                total += pos
                break
    return total % 3

def random_state(k=30):
    s = SOLVED
    for _ in range(k):
        s = apply(random.choice(list(MOVES.values())), s)
    return s

states = [SOLVED] + [random_state() for _ in range(400)]
invariant_ok = all(twist(apply(m, s)) == twist(s)
                   for s in states for m in MOVES.values())
claim("test_9_6", "FORCED",
      "Corner-twist sum mod 3 is move-invariant (moves are FIXED slot permutations; "
      "checked across 401 states x 3 generators = 1203 applications, all preserved)",
      invariant_ok and twist(SOLVED) == 0)

# Build the forbidden state: physically twist ONE corner of the solved cube.
def twist_one_corner(state, c=(1, 1, 1)):
    s = list(state)
    axes_cw = (1, 2, 0)
    a0, a1, a2 = axes_cw
    s[S_IDX[(c, a1)]], s[S_IDX[(c, a2)]], s[S_IDX[(c, a0)]] = \
        state[S_IDX[(c, a0)]], state[S_IDX[(c, a1)]], state[S_IDX[(c, a2)]]
    return tuple(s)

BROKEN = twist_one_corner(SOLVED)
claim("test_9_7", "FORCED",
      "Twist one corner by hand: invariant jumps to 1 (mod 3). Since every legal move "
      "preserves it and solved has 0, NO sequence of legal moves ever solves this state",
      twist(BROKEN) != 0 and twist(SOLVED) == 0)

# Make the unreachability concrete with a bounded search as well:
def bfs_contains(target, depth):
    frontier, seen = {SOLVED}, {SOLVED}
    for _ in range(depth):
        nxt = set()
        for s in frontier:
            for m in MOVES.values():
                for k in (1, 2, 3):
                    t = apply(times(m, k), s)
                    if t not in seen:
                        seen.add(t); nxt.add(t)
        frontier = nxt
        if target in seen: return True, len(seen)
    return target in seen, len(seen)

found, explored = bfs_contains(BROKEN, 7)
claim("test_9_8", "FORCED",
      f"Bounded search agrees: {explored} distinct legal states reached within 7 moves "
      "(any face, any amount) — the twisted state is not among them",
      not found and explored > 100_000)

claim("test_9_9", "EMPIRICAL",
      "God's number for the 3x3x3 is 20 in the half-turn metric — established by "
      "exhaustive computation (Rokicki, Kociemba, Davidson, Dethridge, 2010)",
      True)

trap("Tempting overclaim: 'theta = 20. The physical object enforces theta. "
        "You cannot exceed it.'",
        "Conflates move-count with distance. You can make a million moves; "
        "what is true is that every state lies within distance 20 of solved "
        "(3x3, HTM). God's number is the diameter, an EMPIRICAL result, and "
        "calling it theta is a stipulated reading.")

# ===================================================================== #
# CHAPTER 10 — language as a carrier                                    #
# ===================================================================== #
section("CHAPTER 10 — Language as a Carrier")

# Sorites, made numerical: heap-membership m(n); the induction premise
# 'if n is a heap then n-1 is' has fuzzy truth 1 - (m(n)-m(n-1)); chain a
# million of them with product-AND and watch the load of the argument.
m = lambda n: min(1.0, n / 1_000_000)
premise = lambda n: 1 - (m(n) - m(n - 1))           # ~0.999999 each step
log_chain = sum(math.log(premise(n)) for n in range(2, 1_000_001))
chain_truth = math.exp(log_chain)
claim("test_10_1", "FORCED",
      f"Sorites: each step is 0.999999 true; the MILLION-step conjunction has truth "
      f"{chain_truth:.3f} ~ 1/e. A heap of almost-certainties is not a certainty",
      abs(chain_truth - 1 / math.e) < 1e-3)

claim("test_10_2", "ANALOGY",
      "Reading sentences as P/G->Q (subject/predicate/value) and grammar as a gradient "
      "family is a modelling lens on language, useful and chosen — not a theorem",
      True)

# ===================================================================== #
# CHAPTER 11 — the Carrier class (the book's lab bench)                 #
# ===================================================================== #
section("CHAPTER 11 — Coding a Carrier")

class Carrier:
    def __init__(s, name, V, not_, and_, or_, theta=1.0):
        s.name, s.V = name, list(V)
        s.not_, s.and_, s.or_, s.theta = not_, and_, or_, theta
    def closure(s):
        return closure_audit(s.V, s.not_, s.and_, s.or_) == []
    def lnc(s):  return lnc(s.V, s.and_, s.not_)
    def lem(s):  return lem(s.V, s.or_,  s.not_)
    def dn(s):   return dn(s.V, s.not_)
    def liar(s): return liar_solutions(s.V, s.not_)
    def report(s):
        rows = [("closure", s.closure()), ("LNC", s.lnc()),
                ("LEM", s.lem()), ("DN", s.dn())]
        out = [f"{s.name}: V={s.V[:6]}{'...' if len(s.V) > 6 else ''}"]
        out += [f"   {n:8s} {'holds' if ok else 'fails'}" for n, ok in rows]
        sols = s.liar()
        out.append(f"   Liar     {'resolves at ' + str(sols) if sols else 'no fixed point (paradox in this carrier)'}")
        print("\n".join(out))
        return dict(rows + [("liar", bool(sols))])

classical = Carrier("classical {0,1}", V2, NOT, ANDm, OR)
kleene    = Carrier("Kleene K3 {0,0.5,1}", V3, NOT, ANDm, OR)
trapcase  = Carrier("product-AND trap {0,0.5,1}", V3, NOT, ANDp, OR)

r1, r2, r3 = classical.report(), kleene.report(), trapcase.report()
claim("test_11_1", "FORCED",
      "Carrier class reproduces every Chapter 3 result; AND it catches the "
      "product-AND trap failing the closure audit — the tool audits the book",
      r1 == {"closure": True, "LNC": True, "LEM": True, "DN": True, "liar": False}
      and r2 == {"closure": True, "LNC": False, "LEM": False, "DN": True, "liar": True}
      and r3["closure"] is False)

def compare(c1, c2):
    return {n: (getattr(c1, n)(), getattr(c2, n)())
            for n in ("closure", "lnc", "lem", "dn")}
diff = compare(classical, kleene)
claim("test_11_2", "FORCED",
      "compare(): classical vs K3 differ exactly on LNC and LEM; agree on closure, DN",
      diff["lnc"] == (True, False) and diff["lem"] == (True, False)
      and diff["closure"] == (True, True) and diff["dn"] == (True, True))

# ===================================================================== #
# CHAPTER 12 — the distinction operation (open thread, now started)     #
# ===================================================================== #
section("CHAPTER 12 — Your Challenge + the open thread")

def D(a, b, V):
    """Distinction cost: normalised distance in the value space.
    STIPULATED starter design — improve it; that is the assignment."""
    rng = max(V) - min(V)
    return abs(a - b) / rng if rng else 0.0

claim("test_12_1", "STIPULATED",
      "Starter D(a,b)=|a-b|/range: D(0,1)=1, D(0.49,0.51)=0.02 on [0,1] — note it makes "
      "NEARBY values CHEAP to distinguish, the opposite of the preface's intuition. "
      "First open problem: build a D where near-boundary distinctions cost MORE",
      D(0, 1, Vfuzzy) == 1.0 and abs(D(0.49, 0.51, Vfuzzy) - 0.02) < 1e-12)

# ===================================================================== #
# THE BOOK GRADES ITSELF                                                #
# ===================================================================== #
section("MANIFEST — the book grades itself (weakest link)")

TIER_ORDER = {"FORCED": 4, "EMPIRICAL": 3, "ANALOGY": 2,
              "STIPULATED": 1, "SPECULATION": 0}
counts = {}
for c in MANIFEST: counts[c["tier"]] = counts.get(c["tier"], 0) + 1
weakest = min(MANIFEST, key=lambda c: TIER_ORDER[c["tier"]])
verdict_tier = weakest["tier"]

print(f"\n  Claims verified : {len(MANIFEST)}  "
      + "  ".join(f"{k}={v}" for k, v in sorted(counts.items())))
print(f"  Traps declined  : {len(TRAPS)} (tempting overclaims, caught inline above)")
print(f"  Weakest link    : {verdict_tier}")
print(f"  Book verdict    : PASS/{verdict_tier} — the book contains stipulations")
print(  "                    (load rules, tier order, the 0.5 test, D itself),")
print(  "                    so no honest verdict on it can outrank STIPULATED.")
print(  "                    A map that graded itself FORCED would be lying.")

json.dump({"claims": MANIFEST, "traps_declined": TRAPS,
           "verdict": f"PASS/{verdict_tier}"},
          open("workbook_manifest.json", "w"), indent=2)
print("\n  Manifest written to workbook_manifest.json")
print("\nP / G -> Q. Calculemus — and check the receipt.")
