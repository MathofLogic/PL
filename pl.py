#!/usr/bin/env python3
"""
pl.py — PROPAGATION LOGIC: reference kernel
============================================================================
                            P / G -> Q

One mechanism. A loaded pattern P propagates through a gradient G to a
pattern Q, inside a context that can refuse it. Everything else in this
file is a parameter setting.

    P      = (v, L)        value in carrier V, load L >= 0
    G      : Pattern -> Pattern   (value rule + load rule)
    theta  = coherence threshold; L > theta  =>  decoherence, not error
    Q      = the propagated pattern, bill attached

THE FIVE COMMITMENTS (each enforced below, none assumed):
  1. MECHANISM FIRST   laws are enumerated from carriers at registration,
                       never looked up. A carrier that fails its audit is
                       not registered.
  2. LOAD IS REAL      AND adds, OR takes min, sequence sums, parallel
                       maxes. The load arithmetic is itself a carrier
                       (tropical) and is registered as one.
  3. DRAS              every quantity carries scope (scale, temperature,
                       method, baseline) and a ledger. Erasing scope is
                       permitted — and priced.
  4. GRADIENTS COMPOSE a scale step from E0 to E2 equals E0->E1->E2 in
                       VALUE (state function); load is path-dependent
                       (process function). Both are property-tested.
  5. HONEST TIERS      FORCED > EMPIRICAL > CONDITIONAL > STIPULATED,
                       weakest link composes. The kernel grades itself
                       and cannot outrank its own stipulations.

This is a late iteration. Prior repairs are absorbed as baseline; the
diff lives in the project's chain, not in comments here. Running this
file IS the audit: it enumerates every registered carrier's laws,
property-tests every continuous claim, seals a hash chain, and writes
pl_manifest.json. Exit 0 means the kernel earned its verdict.

Propagation Logic Project - kernel build 2026.07
"""
import math, json, hashlib, random, itertools, sys, time
from dataclasses import dataclass, field, replace

T0 = time.time()
random.seed(20260702)
LOADCOUNT = 0
def pay(n):
    global LOADCOUNT; LOADCOUNT += n

# ═══════════════════════════════════════════════════════════════════════
# SECTION 0 — VERDICT CALCULUS  (the grading substrate, defined first
# because the kernel is its own first repository)
# ═══════════════════════════════════════════════════════════════════════
TIERS = {"FORCED": 4, "EMPIRICAL": 3, "CONDITIONAL": 2,
         "STIPULATED": 1, "UNPAID": 0}
MANIFEST, FAILED, CHAIN = [], [], []

def claim(tier, statement, ok=True, sec="?"):
    MANIFEST.append({"tier": tier, "statement": statement,
                     "verified": bool(ok), "section": sec})
    if tier != "UNPAID" and not ok:
        FAILED.append(f"[{sec}] {statement}")
    flag = "PASS" if ok else ("----" if tier == "UNPAID" else "FAIL")
    print(f"  [{tier:<11}][{flag}] {statement[:98]}")

def seal(body):
    prev = CHAIN[-1]["sha"] if CHAIN else "GENESIS"
    sha = hashlib.sha256((prev + json.dumps(body, sort_keys=True)
                          ).encode()).hexdigest()[:16]
    CHAIN.append({**body, "sha_prev": prev, "sha": sha})

def S(t): print(f"\n{'='*72}\n{t}\n{'='*72}")

# ═══════════════════════════════════════════════════════════════════════
# SECTION 1 — THE MECHANISM
# ═══════════════════════════════════════════════════════════════════════
@dataclass(frozen=True)
class Pattern:
    """P = (v, L). v: designation in carrier V. L: accumulated cost.
    L = 0 is the seed state — no history, no bill."""
    v: object
    L: float = 0.0
    available: bool = True
    tags: frozenset = field(default_factory=frozenset)
    def coheres(self, theta): return self.L <= theta
    def demand(self, theta):  return max(0.0, self.L - theta)

@dataclass
class Context:
    """C = (theta, T). theta: what the context can absorb. T: temperature
    in kelvin, REQUIRED for any joule-denominated cost (no bare Landauer
    constants — a bare kT ln 2 at hidden T is a reification)."""
    theta: float = math.inf
    T: float = None

def propagate(P, G, ctx, *args):
    """P / G -> Q. The only operator. theta is LIVE: an over-threshold
    result decoheres — it is returned, flagged, and unusable downstream."""
    Q = G(P, *args, ctx=ctx)
    pay(1)
    if not Q.coheres(ctx.theta):
        return replace(Q, available=False,
                       tags=Q.tags | frozenset({"decoherent"}))
    return Q

# ═══════════════════════════════════════════════════════════════════════
# SECTION 2 — LOAD RULES  (stipulated; then registered as a carrier)
# ═══════════════════════════════════════════════════════════════════════
def L_and(a, b): return a + b            # both maintained simultaneously
def L_or(a, b):  return min(a, b)        # cheapest alternative suffices
def L_seq(ls):   return sum(ls)          # every step on one worldline
def L_par(ls):   return max(ls)          # walltime of the widest branch

kB = 1.380649e-23
def landauer(bits, T):
    """Minimum cost of irreversibly erasing `bits` at temperature T (K).
    T is a required argument. There is no module-level constant."""
    if T is None:
        raise ValueError("Landauer cost requires an explicit temperature")
    return kB * T * math.log(2) * bits

# ═══════════════════════════════════════════════════════════════════════
# SECTION 3 — THE LAW ENGINE  (laws are outputs, never inputs)
# ═══════════════════════════════════════════════════════════════════════
LAWS = ["LNC","LEM","DN","NoGlut","MP","ANDcomm","ANDassoc","ANDidem",
        "ORcomm","ORassoc","ORidem","DeM1","DeM2","Distrib","Absorb"]

def enumerate_laws(V, neg, AND, OR, D):
    """Complete enumeration over finite V. Every law is decided, none
    assumed. Cost is paid to the global load counter."""
    Dset = set(D); law = {}
    law["LNC"]    = all(AND(a, neg(a)) not in Dset for a in V)
    law["LEM"]    = all(OR(a, neg(a)) in Dset for a in V)
    law["DN"]     = all(neg(neg(a)) == a for a in V)
    law["NoGlut"] = not any(a in Dset and neg(a) in Dset for a in V)
    law["MP"]     = all(not (a in Dset and OR(neg(a), b) in Dset)
                        or b in Dset for a in V for b in V)
    law["ANDcomm"]= all(AND(a,b) == AND(b,a) for a in V for b in V)
    law["ORcomm"] = all(OR(a,b)  == OR(b,a)  for a in V for b in V)
    law["ANDassoc"]=all(AND(AND(a,b),c) == AND(a,AND(b,c))
                        for a in V for b in V for c in V)
    law["ORassoc"]= all(OR(OR(a,b),c) == OR(a,OR(b,c))
                        for a in V for b in V for c in V)
    law["ANDidem"]= all(AND(a,a) == a for a in V)
    law["ORidem"] = all(OR(a,a)  == a for a in V)
    law["DeM1"]   = all(neg(AND(a,b)) == OR(neg(a),neg(b))
                        for a in V for b in V)
    law["DeM2"]   = all(neg(OR(a,b)) == AND(neg(a),neg(b))
                        for a in V for b in V)
    law["Distrib"]= all(AND(a,OR(b,c)) == OR(AND(a,b),AND(a,c))
                        for a in V for b in V for c in V)
    law["Absorb"] = all(AND(a,OR(a,b)) == a and OR(a,AND(a,b)) == a
                        for a in V for b in V)
    n = len(V); pay(5*n + 5*n*n + 3*n**3 + n*n)
    return law

# ═══════════════════════════════════════════════════════════════════════
# SECTION 4 — THE CARRIER REGISTRY
# A carrier is admitted only if (a) it is closed over V, and (b) its
# enumerated laws match its declared signature. Declaration is a
# falsifiable expectation, not a definition.
# ═══════════════════════════════════════════════════════════════════════
@dataclass
class Carrier:
    name: str; V: tuple; neg: object; AND: object; OR: object
    D: tuple; expect: dict; note: str = ""
    laws: dict = None

REGISTRY = {}

def register(c: Carrier):
    closed = (all(c.neg(a) in c.V for a in c.V) and
              all(c.AND(a,b) in c.V and c.OR(a,b) in c.V
                  for a in c.V for b in c.V))
    pay(len(c.V) + 2*len(c.V)**2)
    if not closed:
        claim("FORCED", f"{c.name}: REFUSED — not closed over V", False, "P2")
        return None
    c.laws = enumerate_laws(c.V, c.neg, c.AND, c.OR, c.D)
    mism = {k: (c.laws[k], want) for k, want in c.expect.items()
            if c.laws[k] != want}
    ok = not mism
    held = sum(c.laws.values())
    sig = " ".join(f"{k}:{'Y' if c.laws[k] else '.'}"
                   for k in ["LNC","LEM","DN","MP"])
    claim("FORCED", f"{c.name}: closed; {held}/15 laws enumerated "
          f"[{sig}]; declared signature {'matches' if ok else 'FAILS: '+str(mism)}",
          ok, "P2")
    if ok: REGISTRY[c.name] = c
    return c

# ── the finite logical carriers ─────────────────────────────────────────
Z, H, U = 0.0, 0.5, 1.0          # zero, half, unit
V3 = (Z, H, U)

def mk(neg_h):                    # conservative 3-valued negation
    return lambda a: {Z:U, U:Z, H:neg_h}[a]

def luk_and(a,b): return max(0.0, a+b-1.0)
def luk_or(a,b):  return min(1.0, a+b)
def wk_and(a,b):  return H if H in (a,b) else min(a,b)   # infectious half
def wk_or(a,b):   return H if H in (a,b) else max(a,b)

# FDE on truth/falsity pairs: T=(1,0) F=(0,1) B=(1,1) N=(0,0)
FT, FF, FB, FN = (1,0), (0,1), (1,1), (0,0)
V4 = (FT, FF, FB, FN)
fde_neg = lambda a: (a[1], a[0])
fde_and = lambda a,b: (a[0]&b[0], a[1]|b[1])
fde_or  = lambda a,b: (a[0]|b[0], a[1]&b[1])

S("P2  CARRIER REGISTRY — every carrier audited at the gate")
register(Carrier("CL2  classical", (Z,U), mk(None) if False else (lambda a: U-a),
    min, max, (U,),
    {"LNC":True,"LEM":True,"DN":True,"MP":True,"Distrib":True,"Absorb":True},
    "the L=0 idealisation; all 15 laws hold"))
register(Carrier("K3   strong Kleene", V3, mk(H), min, max, (U,),
    {"LNC":True,"LEM":False,"DN":True,"MP":True},
    "atlas-extremal: unique 14/15 carrier whose lone sacrifice is LEM"))
register(Carrier("LP   priest", V3, mk(H), min, max, (H,U),
    {"LNC":False,"LEM":True,"DN":True,"MP":False},
    "paraconsistent: glut designated, detachment is the price"))
register(Carrier("L3   lukasiewicz", V3, mk(H), luk_and, luk_or, (U,),
    {"LNC":True,"LEM":True,"DN":True,"ANDidem":False},
    "same V as K3, different G: LEM returns, idempotence pays"))
register(Carrier("G3   goedel", V3, mk(Z), min, max, (U,),
    {"LNC":True,"LEM":False,"DN":False,"MP":True},
    "intuitionistic fragment: DN is the sacrifice"))
register(Carrier("B3   weak Kleene", V3, mk(H), wk_and, wk_or, (U,),
    {"LNC":True,"LEM":False,"DN":True,"MP":True},
    "half is infectious: nonsense propagates"))
register(Carrier("FDE  four-valued", V4, fde_neg, fde_and, fde_or, (FT,FB),
    {"LNC":False,"LEM":False,"DN":True,"MP":False},
    "gluts and gaps distinguished — the distinction K3/LP each collapse"))

# cross-check against the catalogue's central claim
same_V_diff_G = (REGISTRY["K3   strong Kleene"].laws["LEM"] is False and
                 REGISTRY["L3   lukasiewicz"].laws["LEM"] is True)
claim("EMPIRICAL", "Catalogue headline reproduced: K3 and L3 share V={0,1/2,1} "
      "yet LEM fails in one and is forced in the other — the law is a "
      "property of G on V, not a fact to look up", same_V_diff_G, "P2")
seal({"gen": 1, "event": "registry",
      "carriers": {k: v.laws for k, v in REGISTRY.items()}})

# ── continuous carriers: property-tested, counterexamples exhibited ─────
S("P3  CONTINUOUS CARRIERS — property tests and exhibited failures")
def prop(n, f):
    ok = all(f() for _ in range(n)); pay(n); return ok

r = lambda: random.random()
fuzzy_ok = prop(2000, lambda: (lambda a,b,c:
    abs((1-min(a,b)) - max(1-a,1-b)) < 1e-12 and
    abs(min(a,max(b,c)) - max(min(a,b),min(a,c))) < 1e-12 and
    abs(min(a,max(a,b)) - a) < 1e-12)(r(), r(), r()))
claim("EMPIRICAL", "FUZZY [0,1] (min/max/1-x): De Morgan, distributivity, "
      "absorption hold on 2000 random triples; LEM fails at the exhibited "
      "point a=0.5 (max(0.5,0.5)=0.5, undesignated)", fuzzy_ok, "P3")

pr_dem = prop(2000, lambda: (lambda a,b:
    abs((1-a*b) - ((1-a)+(1-b)-(1-a)*(1-b))) < 1e-12)(r(), r()))
a=b=c=0.5
lhs = a*(b+c-b*c); rhs = a*b + a*c - (a*b)*(a*c)
claim("EMPIRICAL", f"PROBABILITY (AND=ab under stipulated independence, "
      f"OR=a+b-ab): De Morgan holds on 2000 samples; distributivity FAILS "
      f"by single counterexample a=b=c=1/2: {lhs:.4f} != {rhs:.4f} — "
      f"disproof by exhibition, the corpus method", pr_dem and abs(lhs-rhs) > 1e-3, "P3")
claim("STIPULATED", "The probability AND=ab is the independence stipulation; "
      "dependence needs the joint-distribution carrier. Recorded, not hidden",
      True, "P3")

# calculus carrier: dual numbers, eps SIGNED and distinct from load
@dataclass(frozen=True)
class Dual:
    val: float; eps: float = 0.0
    def __mul__(s, o): return Dual(s.val*o.val, s.eps*o.val + s.val*o.eps)
    def __add__(s, o): return Dual(s.val+o.val, s.eps+o.eps)
    def sin(s): return Dual(math.sin(s.val),  s.eps*math.cos(s.val))
    def exp(s): e = math.exp(s.val); return Dual(e, s.eps*e)

def leib_ok():
    x0 = 0.3 + 2.4*random.random()
    x  = Dual(x0, 1.0)
    h  = (x*x)*x.sin()
    d  = 1e-6
    num = ((x0+d)**2*math.sin(x0+d) - (x0-d)**2*math.sin(x0-d)) / (2*d)
    return abs(h.eps - num) < 1e-5
claim("EMPIRICAL", "CALCULUS (dual numbers): Leibniz propagation matches "
      "central-difference derivative on 500 random points. eps is SIGNED "
      "gradient; load is non-negative cost — related, not identical",
      prop(500, leib_ok), "P3")
claim("STIPULATED", "The eps<->load correspondence (Leibniz ~ AND load rule) "
      "is structural analogy up to |.|, priced as such", True, "P3")
seal({"gen": 2, "event": "continuous-carriers"})

# ═══════════════════════════════════════════════════════════════════════
# SECTION 5 — THE SCALE CARRIER  (running quantities that compose)
# Value propagates additively in the INVERSE — the state variable of
# one-loop running. Value is a state function; load is a path function.
# ═══════════════════════════════════════════════════════════════════════
S("P4  SCALE CARRIER — gradients compose; the bill remembers the path")
@dataclass(frozen=True)
class Running:
    """A quantity that runs with scale. inv = 1/q at scale E.
    step() is P/G->Q in the scale carrier and satisfies the group law:
    value after E0->E1->E2 equals E0->E2 exactly. Load does not — each
    step is a distinction and the ledger keeps all of them."""
    inv: float; E: float; b: float
    L: float = 0.0; steps: int = 0
    @classmethod
    def seed(cls, q0, E0, b): return cls(1.0/q0, E0, b)
    @property
    def q(self): return 1.0/self.inv
    def step(self, E_new):
        d = math.log(E_new/self.E); pay(1)
        return Running(self.inv - self.b*d, E_new, self.b,
                       self.L + abs(self.b*d), self.steps + 1)

# calibration (stipulated one-loop effective coefficient)
inv_me, inv_MZ, me, MZ = 137.036, 128.936, 0.000511, 91.188
b_eff = (inv_me - inv_MZ) / math.log(MZ/me)
alpha = Running.seed(1/inv_me, me, b_eff)
claim("STIPULATED", f"Calibration: b_eff = {b_eff:.5f} fixed so that "
      f"1/alpha runs 137.036 -> 128.936 between m_e and M_Z (one-loop "
      f"effective; not a prediction, an anchor)", True, "P4")

def group_law_ok():
    Es = sorted(10**random.uniform(-3, 4) for _ in range(4))
    direct = alpha.step(Es[-1])
    staged = alpha
    for E in Es: staged = staged.step(E)
    return abs(direct.q - staged.q) / direct.q < 1e-12
claim("EMPIRICAL", "GROUP LAW: 1000 random multi-step paths — staged and "
      "direct propagation agree in VALUE to 1e-12 relative. The gradient "
      "composes; the scale map is a state function", prop(1000, group_law_ok), "P4")

def path_load_ok():
    Es = [10**random.uniform(-3, 4) for _ in range(5)]
    direct = alpha.step(max(Es))
    wander = alpha
    for E in Es: wander = wander.step(E)
    wander = wander.step(max(Es))
    return wander.L >= direct.L - 1e-15
claim("EMPIRICAL", "PATH DEPENDENCE OF LOAD: on 1000 wandering paths the "
      "accumulated load never undercuts the direct path (triangle "
      "inequality on |b dlog|). Value forgets the route; the bill does not. "
      "State function vs process function, shipped as code",
      prop(1000, path_load_ok), "P4")
aZ = alpha.step(MZ)
claim("FORCED", f"alpha(M_Z) = 1/{1/aZ.q:.3f} with L = {aZ.L:.4f} paid in "
      f"one step; theta-live check: pattern coheres in Context(theta=1) "
      f"= {Pattern(aZ.q, aZ.L).coheres(1.0)}", abs(1/aZ.q - 128.936) < 1e-9, "P4")
seal({"gen": 3, "event": "scale-carrier", "b_eff": b_eff})

# ── tropical self-description: the load rules ARE a carrier ─────────────
trop_ok = prop(1000, lambda: (lambda x,y:
    L_and(x,y) == x+y and L_or(x,y) == min(x,y))(10*r(), 10*r()))
claim("CONDITIONAL", "SELF-DESCRIPTION: the kernel's load arithmetic "
      "(AND=+, OR=min on [0,inf)) is the tropical semiring — the "
      "accounting layer is itself a registered carrier. Given the "
      "stipulated load rules, the correspondence is exact", trop_ok, "P4")

# theta live: decoherence fires exactly where arithmetic says
ctx = Context(theta=25.0)
G_AND = lambda P, Q2, ctx: Pattern(min(P.v, Q2.v), L_and(P.L, Q2.L))
p = Pattern(U, 2.0); k = 0; fired_at = None
while k < 20:
    k += 1
    p = propagate(p, G_AND, ctx, Pattern(U, 2.0))
    if not p.available: fired_at = k; break
claim("FORCED", f"THETA IS LIVE: chaining AND(load 2.0) under theta=25 "
      f"decoheres at op {fired_at} (L = {2.0 + 2.0*fired_at:.0f} > 25), "
      f"exactly where the load arithmetic forces it — thresholds enforce, "
      f"not decorate", fired_at == 12, "P4")
claim("CONDITIONAL", f"Joule floor of this run's {LOADCOUNT:,} distinctions "
      f"IF erased irreversibly at T=300 K (stated, not hidden): "
      f"{landauer(LOADCOUNT, 300):.2e} J", True, "P4")
seal({"gen": 4, "event": "tropical+theta", "decohered_at": fired_at})

# ═══════════════════════════════════════════════════════════════════════
# SECTION 6 — DRAS  (De-Reification Axiom Standard)
# ═══════════════════════════════════════════════════════════════════════
S("P5  DRAS — every quantity carries its scope; erasure is priced")
@dataclass(frozen=True)
class LQ:
    """A DRAS quantity: value + signed gradient + load + scope + ledger.
    scope: the history a bare number erases (scale, T, method, baseline).
    reify() hands you the bare float — and adds the erasure to the bill."""
    value: float; eps: float = 0.0; L: float = 0.0
    scope: tuple = (); ledger: tuple = ()
    def __mul__(s, o):
        return LQ(s.value*o.value, s.eps*o.value + s.value*o.eps,
                  L_and(s.L, o.L), s.scope + o.scope,
                  s.ledger + o.ledger + ("AND-combine",))
    def reify(s):
        return s.value, replace(s, L=s.L + 1.0,
                                ledger=s.ledger + ("REIFIED: scope erased",))
    def bill(s):
        return {"value": s.value, "L": s.L, "scope": dict(s.scope),
                "ledger": list(s.ledger)}

aq = LQ(aZ.q, eps=0.0, L=aZ.L,
        scope=(("E","91.188 GeV"), ("method","one-loop effective"),
               ("baseline","1/alpha=137.036 at m_e"), ("run-T","n/a")),
        ledger=("seeded from Running carrier",))
bare, priced = aq.reify()
claim("FORCED", f"REIFICATION IS PRICED: alpha(M_Z).reify() returns the "
      f"bare float {bare:.6f} and appends the erasure to the ledger; "
      f"L rises {aq.L:.3f} -> {priced.L:.3f}. You may drop the scope. "
      f"You may not drop it for free",
      priced.L == aq.L + 1.0 and "REIFIED: scope erased" in priced.ledger, "P5")

def half_test(claim_text, half_meaning_clear):
    """The 0.5 test: if 'halfway' is sensible, the domain is continuous
    and a binary carrier on it is a reification."""
    return ("REIFICATION - continuous domain, binary carrier"
            if half_meaning_clear else "binary may fit - check boundaries")
demo = [("'the system is safe'", True), ("'the toggle is off'", False)]
res = [half_test(c, h) for c, h in demo]
claim("STIPULATED", f"THE 0.5 TEST (diagnostic heuristic): "
      f"{demo[0][0]} -> {res[0]}; {demo[1][0]} -> {res[1]}",
      res[0].startswith("REIF") and res[1].startswith("binary"), "P5")
seal({"gen": 5, "event": "dras", "alpha_bill": aq.bill()})

# ═══════════════════════════════════════════════════════════════════════
# SECTION 7 — WHAT IS NOT CLAIMED, THE CHAIN, THE VERDICT
# ═══════════════════════════════════════════════════════════════════════
S("P6  THE BILL — unpaid items, chain replay, weakest link")
claim("UNPAID", "NOT claimed: that the registry exhausts formal systems. "
      "Substructural proof theory, non-matrix semantics, and conditionals "
      "beyond material enter through the same gate when built", False, "P6")
claim("UNPAID", "NOT claimed: that load equals physical energy without an "
      "implementation map. landauer(bits,T) is a floor for irreversible "
      "erasure, quoted only with T explicit", False, "P6")
claim("UNPAID", "NOT claimed: that the tier order is forced. It is the "
      "kernel's constitution — a stipulation the kernel cannot outrank",
      False, "P6")

def replay(chain):
    prev = "GENESIS"
    for g in chain:
        body = {k: v for k, v in g.items() if k not in ("sha","sha_prev")}
        want = hashlib.sha256((prev + json.dumps(body, sort_keys=True)
                               ).encode()).hexdigest()[:16]
        if g["sha_prev"] != prev or g["sha"] != want: return False
        prev = g["sha"]
    return True
tam = json.loads(json.dumps(CHAIN)); tam[0]["event"] = "forged"
claim("FORCED", f"Chain of {len(CHAIN)} generations replays intact; a "
      f"mutated seal breaks replay at its link. The kernel's history is a "
      f"verifiable structure, not a log", replay(CHAIN) and not replay(tam), "P6")

weakest = min((c for c in MANIFEST if c["tier"] != "UNPAID"),
              key=lambda c: TIERS[c["tier"]])
counts = {}
for c in MANIFEST: counts[c["tier"]] = counts.get(c["tier"], 0) + 1
sha = hashlib.sha256(open(__file__, "rb").read()).hexdigest()[:16]
verdict = f"PASS/{weakest['tier']}" if not FAILED else "FAIL"
json.dump({"title": "PL reference kernel - build 2026.07",
           "verdict": verdict, "seed": 20260702,
           "suite_sha256_16": sha, "load_checks": LOADCOUNT,
           "carriers": {k: v.laws for k, v in REGISTRY.items()},
           "summary": counts, "failed": FAILED,
           "claims": MANIFEST, "chain": CHAIN},
          open("pl_manifest.json", "w"), indent=1)

print(f"\n{'='*72}")
print(f"  PL KERNEL {'PASSED' if not FAILED else 'FAILED'}   "
      + "  ".join(f"{k}:{v}" for k, v in sorted(counts.items())))
print(f"  carriers registered: {len(REGISTRY)}   load {LOADCOUNT:,} checks"
      f"   {time.time()-T0:.2f}s")
print(f"  verdict {verdict}   chain {len(CHAIN)}   sha256[:16] = {sha}")
print(f"  The kernel contains stipulations (load rules, tier order, the")
print(f"  0.5 test, its own scope) and therefore cannot honestly grade")
print(f"  itself above STIPULATED. A map that did would be lying.")
print(f"{'='*72}")
print(f"\n  P / G -> Q. Calculemus — and check the receipt.")
sys.exit(1 if FAILED else 0)
