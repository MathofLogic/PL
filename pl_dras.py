#!/usr/bin/env python3
"""
pl_dras.py  —  DRAS: De-Reification Axiom Standard
====================================================
Standalone implementation of the DRAS framework from
The Math of Logic, Chapter 5.

DRAS is the principle that every quantity in a formal system
should carry its full load history — not just its current value.

When a constant changes with scale, context, or history,
treating it as a context-free number is a carrier mismatch.

This module provides:
    LoadedHistory  — a value that carries its full parameter history
    G_scale        — the scale-change gradient (P/G→Q in scale carrier)
    zero_point_five_test — the DRAS diagnostic for reification

Physical grounding: the Landauer limit
    kB * T * ln(2) ≈ 2.87e-21 joules per erased bit at 300K
    Proved by Landauer (1961). Verified to within 2% by Berut et al. (2012).

Key demonstrations:
    Fine structure constant: 1/137 at low energy → 1/128 at Z mass
    QCD asymptotic freedom: coupling decreases at high energy
    The 0.5 test applied to everyday claims

P / G → Q.  Every quantity is a loaded history at scale E.

James Pugmire · Propagation Logic Project · 2026
github.com/ApplePiesFromScratch/propagation-logic
"""

import math
import sys
from dataclasses import dataclass, field
from typing import Any, Callable, Optional

# ── Physical constants ─────────────────────────────────────────────────────
kB       = 1.380649e-23   # Boltzmann constant (J/K)
ln2      = math.log(2)
T_300    = 300.0          # room temperature (K)
LANDAUER = kB * T_300 * ln2   # ≈ 2.87e-21 J per bit erased

UNDEF    = float('nan')   # undefined: gradient pole

# ──────────────────────────────────────────────────────────────────────────
# PATTERN  (re-exported for convenience)
# ──────────────────────────────────────────────────────────────────────────

@dataclass
class Pattern:
    """
    A loaded pattern P = (v, L).

    v: the designation — value in the carrier.
    L: load — accumulated thermodynamic cost.

    In the scale carrier:
        v = coupling value at the current energy scale
        L = accumulated load from all scale steps taken
    """
    v: float
    L: float = 0.0
    available: bool = True
    tags: frozenset = field(default_factory=frozenset)

    def coheres(self, theta: float) -> bool:
        return self.L <= theta

    def demand(self, theta: float) -> float:
        return max(0.0, self.L - theta)

    def __repr__(self):
        return f"P(v={self.v:.6g}, L={self.L:.4f})"


@dataclass
class Context:
    """
    A context C = (theta, E_current).
    theta: coherence threshold (load capacity)
    E_current: current energy scale in the scale carrier
    """
    theta: float = 100.0
    E_current: float = 1.0


# ──────────────────────────────────────────────────────────────────────────
# LOADED HISTORY
# The DRAS quantity type — carries its full parameter history
# ──────────────────────────────────────────────────────────────────────────

class LoadedHistory:
    """
    A quantity that carries its full load history.

    LoadedHistory is the DRAS implementation of a physical coupling constant
    or any quantity that changes with scale, context, or time.

    Components:
        real: value at the reference scale E0
        eps:  first-order gradient (derivative component)
        beta: loading rate (dα/d log E — the beta-function coefficient)
        E0:   reference energy scale

    DRAS Axiom L: q(E) = real / (1 + beta * log(E / E0))

    This is not a correction to a 'true' constant.
    It IS the constant — a stabilised loaded history at a reference scale.

    The beta-function IS the load-combination rule for scale translations.
    It is P/G→Q in the scale carrier, not a separate equation.
    """

    def __init__(self, real: float, eps: float = 0.0,
                 beta: float = 0.0, E0: float = 1.0):
        self.real = float(real)
        self.eps  = float(eps)
        self.beta = float(beta)
        self.E0   = float(E0)

    @property
    def val(self): return self.real     # alias for compatibility

    @property
    def load(self): return self.eps     # alias

    def at_scale(self, E: float) -> float:
        """
        The value at energy scale E.

        This is the only meaningful question for a DRAS quantity.
        The bare value (self.real) is only defined relative to E0.
        """
        if self.beta == 0:
            return self.real
        denom = 1.0 + self.beta * math.log(E / self.E0)
        if abs(denom) < 1e-12:
            return UNDEF
        return self.real / denom

    def as_pattern(self) -> Pattern:
        """Convert to a Pattern for use with P/G→Q machinery."""
        return Pattern(v=self.real, L=abs(self.eps))

    # ── Arithmetic with Leibniz rule (AND load rule in calculus carrier) ──

    def __mul__(self, other):
        """
        Multiplication: AND in the calculus carrier.
        Value: real1 * real2
        Load (eps): eps1*real2 + real1*eps2  (Leibniz = AND load rule)
        Beta: betas add under multiplication
        """
        if not isinstance(other, LoadedHistory):
            other = LoadedHistory(other)
        return LoadedHistory(
            real = self.real * other.real,
            eps  = self.eps  * other.real + self.real * other.eps,
            beta = self.beta + other.beta,
            E0   = self.E0
        )
    __rmul__ = __mul__

    def __add__(self, other):
        if not isinstance(other, LoadedHistory):
            other = LoadedHistory(other)
        return LoadedHistory(
            real = self.real + other.real,
            eps  = self.eps  + other.eps,
            beta = self.beta,   # addition takes the current beta
            E0   = self.E0
        )
    __radd__ = __add__

    def __sub__(self, other):
        if not isinstance(other, LoadedHistory):
            other = LoadedHistory(other)
        return LoadedHistory(
            real = self.real - other.real,
            eps  = self.eps  - other.eps,
            beta = self.beta,
            E0   = self.E0
        )
    __rsub__ = lambda self, o: LoadedHistory(o).__sub__(self)

    def __truediv__(self, other):
        if not isinstance(other, LoadedHistory):
            other = LoadedHistory(other)
        return LoadedHistory(
            real = self.real / other.real,
            eps  = (self.eps * other.real - self.real * other.eps) / other.real**2,
            beta = self.beta - other.beta,
            E0   = self.E0
        )
    __rtruediv__ = lambda self, o: LoadedHistory(o).__truediv__(self)

    def __pow__(self, n):
        result = LoadedHistory(1.0, 0.0, 0.0, self.E0)
        for _ in range(abs(int(n))):
            result = result * self
        return result

    def __neg__(self):
        return LoadedHistory(-self.real, -self.eps, self.beta, self.E0)

    def exp(self):
        ev = math.exp(self.real)
        return LoadedHistory(ev, self.eps * ev, self.beta, self.E0)

    def sin(self):
        return LoadedHistory(
            math.sin(self.real),
            self.eps * math.cos(self.real),
            self.beta, self.E0
        )

    def cos(self):
        return LoadedHistory(
            math.cos(self.real),
            -self.eps * math.sin(self.real),
            self.beta, self.E0
        )

    def log(self):
        return LoadedHistory(
            math.log(self.real),
            self.eps / self.real,
            self.beta, self.E0
        )

    def sqrt(self):
        s = math.sqrt(self.real)
        return LoadedHistory(s, self.eps / (2*s), self.beta, self.E0)

    def __repr__(self):
        return (f"LoadedHistory(val={self.real:.6g}, d={self.eps:.4g}, "
                f"beta={self.beta:.4g}, E0={self.E0:.4g})")


# ── Convenience constructors ──────────────────────────────────────────────

def dras_seed(value: float, E0: float = 1.0, beta: float = 0.0) -> LoadedHistory:
    """Create a seed quantity: zero load, value at E0."""
    return LoadedHistory(real=value, eps=0.0, beta=beta, E0=E0)

def dras_x(value: float, E0: float = 1.0) -> LoadedHistory:
    """Create a variable: unit derivative seed."""
    return LoadedHistory(real=value, eps=1.0, beta=0.0, E0=E0)

def dras_const(value: float) -> LoadedHistory:
    """
    A constant: load = 0, beta = 0, scale-independent.
    In DRAS: this is only an approximation. All physical 'constants' run.
    """
    return LoadedHistory(real=value, eps=0.0, beta=0.0, E0=1.0)

def dras_exp(h: LoadedHistory) -> LoadedHistory:  return h.exp()
def dras_sin(h: LoadedHistory) -> LoadedHistory:  return h.sin()
def dras_cos(h: LoadedHistory) -> LoadedHistory:  return h.cos()
def dras_log(h: LoadedHistory) -> LoadedHistory:  return h.log()


# ──────────────────────────────────────────────────────────────────────────
# G_scale  —  THE SCALE-CHANGE GRADIENT
#
# This is the mechanical demonstration from the conversation.
# G_scale implements P/G→Q where:
#   P = current pattern (v = coupling at current scale, L = history)
#   G = the scale-change gradient with coefficient beta
#   Q = pattern at the new scale
#
# Load combination rule (AND rule in scale carrier):
#   The scale step IS a P/G→Q operation.
#   Each step adds to the accumulated load history.
# ──────────────────────────────────────────────────────────────────────────

def G_scale(p: Pattern, delta_logE: float, beta: float,
            ctx: Context) -> Pattern:
    """
    Mechanical scale-change gradient (DRAS).

    Input:
        p:          current pattern (v = coupling at current scale,
                                     L = accumulated load history)
        delta_logE: log(E_new / E_current) — the scale step size
        beta:       coefficient from Gamma (= dα/d log E)
        ctx:        context (threshold theta, current scale)

    Mechanics (forced by AND + load accounting):
        1. New value:  running coupling formula
                       v_new = v / (1 + beta * delta_logE)
        2. Load:       AND rule — each scale step adds to the load
                       L_new = L + |beta * delta_logE|
        3. Tags:       mark as 'scale' and 'dras'

    This is exactly "the load accounting of the propagation operator
    applied to the coupling carrier."

    The load grows because each scale step IS a distinction: the value
    at E_new is genuinely different from the value at E_old. Maintaining
    both requires work. The AND load rule accounts for it.

    Asymptotic freedom (beta < 0):
        As delta_logE → +∞, v → 0 (coupling approaches seed state L=0).
        The pattern reconfigures toward lower load at high scale.

    Landauer grounding:
        Each scale step costs ≥ LANDAUER joules in physical implementation.
        load_add = |beta * delta_logE| is the dimensionless count.
        Physical cost = load_add * LANDAUER joules.
    """
    if abs(delta_logE) < 1e-12:
        return p   # no step — no cost

    denom = 1.0 + beta * delta_logE
    if abs(denom) < 1e-12:
        # Landau pole: coupling diverges. Pattern undefined.
        return Pattern(v=UNDEF, L=UNDEF,
                       tags=p.tags | frozenset({'scale_pole', 'dras'}))

    v_new    = p.v / denom
    load_add = abs(beta * delta_logE)    # cost of this scale step
    L_new    = p.L + load_add            # AND rule: accumulate history

    return Pattern(
        v         = v_new,
        L         = L_new,
        available = p.available,
        tags      = p.tags | frozenset({'scale', 'dras'})
    )


# ──────────────────────────────────────────────────────────────────────────
# THE 0.5 TEST
# Diagnostic for reification — when a binary carrier is applied to a
# continuous domain, hiding load history in the process.
# ──────────────────────────────────────────────────────────────────────────

def zero_point_five_test(claim: str, explanation: str,
                         verdict: str = None) -> dict:
    """
    Apply the 0.5 test to a claim.

    The test: for any claim using a binary value (true/false, safe/unsafe,
    guilty/not-guilty), ask what the value 0.5 would mean.

    If the answer is clear ('somewhat safe', 'partially true'):
        — domain is continuous
        — binary carrier is a reification
        — load history has been suppressed

    If the answer is incoherent:
        — binary carrier may be appropriate
        — check whether boundary cases matter for the problem

    Returns a dict with the test result.
    """
    return {
        'claim':       claim,
        'explanation': explanation,
        'verdict':     verdict,
    }


ZERO_POINT_FIVE_EXAMPLES = [
    zero_point_five_test(
        claim       = "'This city is safe.'",
        explanation = "'Somewhat safe' is clearly meaningful. Safety is continuous. "
                      "The binary claim suppresses: safe for whom, by what measure "
                      "(crime rate? road deaths? air quality?), at what time, "
                      "compared to what baseline. Binary carrier = reification.",
        verdict     = "REIFICATION — domain is continuous"
    ),
    zero_point_five_test(
        claim       = "'The patient is ill.'",
        explanation = "'Moderately ill' is clinically meaningful. Severity drives treatment. "
                      "Binary classification loses information the domain requires. "
                      "Use four-valued carrier: absent/mild/moderate/severe.",
        verdict     = "REIFICATION — use graduated carrier"
    ),
    zero_point_five_test(
        claim       = "'The vote passed.'",
        explanation = "'The vote half-passed' has no legal meaning in a binary voting system. "
                      "However: 'the motion received 50% support' IS meaningful in a "
                      "continuous preference model. Two different carriers, two different "
                      "systems. The 0.5 test forces you to choose which system you are in.",
        verdict     = "CONTEXT-DEPENDENT — depends on the system"
    ),
    zero_point_five_test(
        claim       = "'The circuit is open.'",
        explanation = "'Half-open' is physically meaningful under fault conditions and during "
                      "switching transients. In standard operation binary is appropriate. "
                      "Whether 0.5 matters depends on the problem, not the domain alone.",
        verdict     = "BINARY MAY BE APPROPRIATE — check boundary conditions"
    ),
    zero_point_five_test(
        claim       = "'The fine structure constant is 1/137.'",
        explanation = "'The fine structure constant at 0.5 of the Z boson energy' "
                      "is perfectly well-defined (approximately 1/130). The constant runs "
                      "with scale. The bare value 1/137 is the value at the reference scale "
                      "E0 = m_e = 0.511 MeV. DRAS version: alpha(E) = 1/137 at E = 0.511 MeV.",
        verdict     = "REIFICATION — classic physics example, load history suppressed"
    ),
]


# ──────────────────────────────────────────────────────────────────────────
# RUNNING COUPLING DEMONSTRATIONS
# ──────────────────────────────────────────────────────────────────────────

def demo_qed_running():
    """
    QED: fine structure constant running with energy scale.

    alpha(E) = alpha_0 / (1 + (alpha_0 / 3pi) * sum_fermions * log(E^2/m_f^2))

    At E0 = 0.511 MeV (electron mass):  alpha ≈ 1/137.036
    At E  = 91.2 GeV  (Z boson mass):   alpha ≈ 1/128.9

    Mechanically: G_scale applied iteratively in the energy carrier.
    """
    BAR = "─" * 52

    print(f"\n{'═'*52}")
    print("  QED: Fine Structure Constant Running")
    print("  P / G_scale → Q in the energy carrier")
    print(f"{'═'*52}")
    print(f"\n  Physical grounding:")
    print(f"    Landauer limit at 300K: {LANDAUER:.3e} J per bit")
    print(f"    Each scale step costs at minimum this much energy")
    print()

    # Seed pattern: alpha at E0 = 0.511 MeV (electron mass)
    alpha_E0  = 1/137.036
    E0_MeV    = 0.511
    # QED effective beta coefficient (absorbing the sum over charged fermions)
    # Full treatment: Δ(1/alpha) ≈ 7.8 from E0 to M_Z
    # Effective beta for G_scale: beta_eff * log(E_Z/E0) = 7.8 * alpha_E0
    E_Z_MeV   = 91_200.0
    log_ratio = math.log(E_Z_MeV / E0_MeV)   # ≈ 12.1
    beta_eff  = (7.8 * alpha_E0) / log_ratio  # ≈ 0.000466

    # Build seed pattern
    p = Pattern(v=alpha_E0, L=0.0)
    ctx = Context(theta=100.0, E_current=E0_MeV)

    print(f"  Seed: alpha({E0_MeV} MeV) = 1/{1/alpha_E0:.3f} = {alpha_E0:.7f}")
    print(f"  beta_eff = {beta_eff:.6f}")
    print()
    print(f"  {'E':>12}  {'1/alpha(E)':>12}  {'L (load)':>10}  {'Note'}")
    print(f"  {BAR}")

    # Propagate through scales
    E_current = E0_MeV
    for E_target_MeV in [1.0, 10.0, 100.0, 1000.0, E_Z_MeV]:
        delta_logE = math.log(E_target_MeV / E_current)
        p = G_scale(p, delta_logE, beta_eff, ctx)
        E_current = E_target_MeV

        if math.isnan(p.v):
            print(f"  {E_target_MeV:>12.1f}  {'POLE':>12}  {p.L:>10.4f}")
            break

        note = ""
        if abs(E_target_MeV - E_Z_MeV) < 1.0:
            note = "← Z boson mass"
            alpha_measured = 1/128.9
            error_pct = abs(1/p.v - 1/alpha_measured) / (1/alpha_measured) * 100
            note += f"  (measured: 1/{1/alpha_measured:.1f}, error: {error_pct:.1f}%)"
        elif E_target_MeV >= 1000.0:
            note = "← TeV scale"

        unit = "GeV" if E_target_MeV >= 1000 else "MeV"
        E_show = E_target_MeV/1000 if E_target_MeV >= 1000 else E_target_MeV
        print(f"  {E_show:>9.1f} {unit}  {1/p.v:>12.3f}  {p.L:>10.4f}  {note}")

    print()
    print(f"  Final accumulated load: {p.L:.4f}")
    print(f"  Physical cost: {p.L * LANDAUER:.3e} J")
    print()
    print("  The 'constant' was always a scale-dependent loaded history.")
    print("  1/137 is the value at E0 = 0.511 MeV, not a universal truth.")


def demo_qcd_asymptotic_freedom():
    """
    QCD: strong coupling constant running (asymptotic freedom).

    Beta-function: beta(g) = -b0 * g^3 / (16*pi^2)
    For N_f=6 quark flavours: b0 = 11 - 2*6/3 = 7
    beta < 0: coupling DECREASES at high energy.

    This is reconfiguration toward lower load at high scale.
    Asymptotic freedom = the pattern approaching its seed state (L=0).
    """
    BAR = "─" * 52

    print(f"\n{'═'*52}")
    print("  QCD: Asymptotic Freedom")
    print("  Beta < 0: coupling reconfigures toward seed state")
    print(f"{'═'*52}")

    # alpha_s at M_Z = 91.2 GeV: experimentally 0.118
    alpha_s_MZ = 0.118
    g_MZ       = math.sqrt(alpha_s_MZ * 4 * math.pi)
    E0_GeV     = 91.2   # reference scale: Z mass

    # G_scale with negative beta (asymptotic freedom)
    # For G_scale: v = alpha_s, beta_eff < 0
    # Effective: alpha_s(E) ≈ alpha_s(MZ) / (1 + beta_eff * log(E/MZ))
    # where beta_eff = b0 * alpha_s(MZ) / (2*pi) ≈ 7 * 0.118 / (2*pi) ≈ 0.132
    b0       = 7.0
    beta_eff = b0 * alpha_s_MZ / (2 * math.pi)   # positive denominator sign
    # Note: for G_scale, asymptotic freedom means denom grows → v decreases
    # We encode this as positive beta in G_scale (denom = 1 + beta*dlogE grows)

    p = Pattern(v=alpha_s_MZ, L=0.0)
    ctx = Context(theta=1000.0, E_current=E0_GeV)

    print(f"\n  Seed: alpha_s({E0_GeV} GeV) = {alpha_s_MZ:.4f}")
    print(f"  beta_eff (QCD) = +{beta_eff:.4f}  [positive → decreasing coupling]")
    print()
    print(f"  {'E (GeV)':>12}  {'alpha_s(E)':>12}  {'L (load)':>10}  {'Note'}")
    print(f"  {BAR}")

    E_current = E0_GeV
    for E_target_GeV in [200.0, 1000.0, 10000.0, 1_000_000.0]:
        delta_logE = math.log(E_target_GeV / E_current)
        p = G_scale(p, delta_logE, beta_eff, ctx)
        E_current = E_target_GeV

        if math.isnan(p.v):
            break

        note = ""
        if E_target_GeV >= 1_000_000:
            note = "← 1 PeV (approaching seed state)"
        elif E_target_GeV >= 10_000:
            note = "← 10 TeV (LHC frontier)"

        print(f"  {E_target_GeV:>12.1f}  {p.v:>12.6f}  {p.L:>10.4f}  {note}")

    print()
    print(f"  Coupling approaches zero as E → ∞.")
    print(f"  This is the pattern reconfiguring toward its seed state (L→0 coupling).")
    print(f"  'Asymptotic freedom' = coherence recovery at high scale.")


def demo_scale_stepping():
    """
    Step-by-step scale evolution using G_scale.
    Directly demonstrates P/G→Q applied to the coupling carrier.
    """
    BAR = "─" * 52

    print(f"\n{'═'*52}")
    print("  Mechanical Scale-Change Demonstration")
    print("  G_scale as P/G→Q: each step is a distinct event")
    print(f"{'═'*52}")
    print()

    # QED-like parameters from the conversation
    alpha0 = Pattern(v=1/137.036, L=0.0)   # seed at reference scale
    beta   = 0.0078                          # from book / simplified QED
    ctx    = Context(theta=100.0, E_current=0.511)

    print(f"  Seed: alpha = {alpha0.v:.7f}  (1/{1/alpha0.v:.2f})")
    print(f"  Beta = {beta}  (screening: positive → coupling increases with E)")
    print()
    print(f"  {'E (MeV)':>10}  {'alpha(E)':>12}  {'1/alpha(E)':>12}  {'acc. load':>10}")
    print(f"  {BAR}")

    E_current = 0.511
    for E_target in [10.0, 91_200.0, 1_000_000.0]:
        dlogE  = math.log(E_target / E_current)
        alpha0 = G_scale(alpha0, dlogE, beta, ctx)
        E_current = E_target

        unit = "GeV" if E_target >= 1000 else "MeV"
        E_show = E_target/1000 if E_target >= 1000 else E_target
        print(f"  {E_show:>7.1f} {unit}  {alpha0.v:>12.7f}  "
              f"{1/alpha0.v:>12.2f}  {alpha0.L:>10.4f}")

    print()
    print(f"  Each step pays load = |beta * delta_logE|")
    print(f"  AND rule: accumulated load = sum of all step costs")
    print(f"  Physical cost of full evolution: {alpha0.L * LANDAUER:.3e} J")


# ──────────────────────────────────────────────────────────────────────────
# 0.5 TEST DEMONSTRATION
# ──────────────────────────────────────────────────────────────────────────

def demo_zero_point_five():
    print(f"\n{'═'*52}")
    print("  The 0.5 Test: Diagnostic for Reification")
    print(f"{'═'*52}")
    print()
    print("  For each binary claim, ask: what would 0.5 mean?")
    print("  Clear answer → continuous domain → binary is a reification.")
    print()

    for i, ex in enumerate(ZERO_POINT_FIVE_EXAMPLES, 1):
        print(f"  {i}. Claim: {ex['claim']}")
        print(f"     {ex['explanation']}")
        print(f"     Verdict: {ex['verdict']}")
        print()


# ──────────────────────────────────────────────────────────────────────────
# DRAS ARITHMETIC VERIFICATION
# ──────────────────────────────────────────────────────────────────────────

def demo_dras_arithmetic():
    """
    Verify that LoadedHistory arithmetic obeys the AND load rule (Leibniz rule).
    The product rule d/dx[f*g] = f'*g + f*g' IS the AND load rule.
    """
    print(f"\n{'═'*52}")
    print("  DRAS Arithmetic: AND Load Rule = Product Rule")
    print(f"{'═'*52}")
    print()

    # d/dx[x^2 * sin(x)] at x = 1.3
    x_val = 1.3
    x = dras_x(x_val)

    # Compute using LoadedHistory (AND load rule)
    f = x * x          # x^2: val=1.69, load=2*x=2.6
    g = x.sin()        # sin(x): val=sin(1.3), load=cos(1.3)
    h = f * g          # x^2 * sin(x): Leibniz rule

    # Analytical answer
    expected_d = 2*x_val*math.sin(x_val) + x_val**2*math.cos(x_val)
    err = abs(h.eps - expected_d)

    print(f"  d/dx[x² · sin(x)] at x = {x_val}")
    print(f"    Mechanism (AND load rule): {h.eps:.10f}")
    print(f"    Analytical:               {expected_d:.10f}")
    print(f"    Error:                    {err:.2e}")
    print(f"  {'✓ VERIFIED' if err < 1e-10 else '✗ FAILED'}")
    print()
    print(f"  The Leibniz product rule is the AND load rule.")
    print(f"  eps component of (f*g) = eps_f*val_g + val_f*eps_g")
    print(f"  Compare: d/dx[fg] = f'*g + f*g'")
    print(f"  They are the same arithmetic with different names.")

    # Verify product rule as load rule explicitly
    print(f"\n  Explicit verification:")
    print(f"    f = x^2:    val = {f.real:.6f},  eps = {f.eps:.6f}")
    print(f"    g = sin(x): val = {g.real:.6f},  eps = {g.eps:.6f}")
    print(f"    f*g load  = eps_f*val_g + val_f*eps_g")
    print(f"             = {f.eps:.6f}*{g.real:.6f} + {f.real:.6f}*{g.eps:.6f}")
    print(f"             = {f.eps*g.real + f.real*g.eps:.10f}")
    print(f"    h.eps     = {h.eps:.10f}")

    assert err < 1e-10, f"DRAS product rule failed: {err}"
    print(f"  Assertion passed. ✓")


# ──────────────────────────────────────────────────────────────────────────
# ENTRY POINT
# ──────────────────────────────────────────────────────────────────────────

def main():
    args = sys.argv[1:]

    if '--qed' in args:
        demo_qed_running()
    elif '--qcd' in args:
        demo_qcd_asymptotic_freedom()
    elif '--steps' in args:
        demo_scale_stepping()
    elif '--test' in args:
        demo_zero_point_five()
    elif '--arithmetic' in args:
        demo_dras_arithmetic()
    else:
        print(__doc__)
        print("\nRunning all demonstrations...\n")
        demo_scale_stepping()
        demo_qed_running()
        demo_qcd_asymptotic_freedom()
        demo_dras_arithmetic()
        demo_zero_point_five()
        print(f"\n{'═'*52}")
        print("  All demonstrations complete.")
        print(f"  Landauer limit: {LANDAUER:.3e} J per bit at 300K")
        print(f"  P / G → Q. The carrier sets the logic.")
        print(f"{'═'*52}")


if __name__ == "__main__":
    main()
