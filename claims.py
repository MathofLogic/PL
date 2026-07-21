"""
claims.py — the /PL ledger, priced by the Atlas LEDGER plate.
==========================================================================
SECTIONS = [(section, [ {claim, check|cite, tier?} ])]. Checked claims
name entries in pl_checks:CHECKS. Conceptual claims are cited to
PL_SPEC.md and priced as presumptions or stipulations — the kernel
FORCES its models, never the reading of the world through them. The
paid fraction below is whatever it is; targeted, it would cease to
measure.
"""

SECTIONS = [
    ("The instrument", [
        {"claim": "the kernel announces its own identity: "
                  "sha256(pl.py)[:16] recomputed from bytes equals the "
                  "sealed suite sha",
         "check": "kernel_sha_recomputes", "tier": "FORCED"},
        {"claim": "every committed manifest carries a sha-linked chain "
                  "that replays without its writer",
         "check": "all_chains_replay", "tier": "FORCED"},
        {"claim": "the enumeration's cost is on the books: 20,780 "
                  "load checks under a fixed, sealed seed",
         "check": "load_is_priced", "tier": "EMPIRICAL"},
    ]),
    ("Carrier facts (enumerated, not argued)", [
        {"claim": "CL2 is closed: all 15 laws enumerate true",
         "check": "classical_carrier_closed", "tier": "FORCED"},
        {"claim": "K3 drops LEM and keeps LNC and MP: the gap is "
                  "priced where it lives",
         "check": "k3_drops_lem_keeps_lnc", "tier": "FORCED"},
        {"claim": "LP's gluts cost it MP: paraconsistency is paid for "
                  "in detachment, not asserted for free",
         "check": "lp_glut_costs_mp", "tier": "FORCED"},
        {"claim": "FDE drops both LEM and LNC and loses MP with them",
         "check": "fde_drops_both", "tier": "FORCED"},
    ]),
    ("The kernel's self-pricing", [
        {"claim": "no FORCED claim in the sealed ledger is unverified",
         "check": "forced_claims_verified", "tier": "FORCED"},
        {"claim": "the kernel's self-verdict is capped at "
                  "PASS/STIPULATED with its UNPAID entries priced",
         "check": "verdict_capped_stipulated", "tier": "FORCED"},
        {"claim": "the kernel's negative space is sealed into its own "
                  "ledger as NOT-claimed statements at UNPAID",
         "check": "nonclaims_sealed", "tier": "FORCED"},
    ]),
    ("Conceptual commitments (stipulated mappings, never forced)", [
        {"claim": "P / G -> Q: propagation of a pattern through a "
                  "gradient over a value space under a coherence "
                  "threshold, with its cost on the books, is a "
                  "workable primitive for formal systems",
         "cite": "PL_SPEC.md", "tier": "STIPULATED"},
        {"claim": "PL is a process logic: designation and detachment "
                  "are activities with costs, not static properties — "
                  "the frame aims to operate before the subject/"
                  "predicate cut is treated as ontologically prior",
         "cite": "PL_SPEC.md; workbook ch. 1", "tier": "STIPULATED"},
        {"claim": "the tier order (FORCED > EMPIRICAL > ... ) is a "
                  "chosen bookkeeping convention, not a discovery",
         "cite": "pl.py NOT-claimed ledger entries", "tier": "STIPULATED"},
        {"claim": "the registry of seven carriers does not exhaust "
                  "formal systems",
         "cite": "pl.py NOT-claimed ledger entries", "tier": "PRESUMED"},
        {"claim": "load is an accounting device; it equals physical "
                  "energy only under an explicit further mapping that "
                  "is not made here",
         "cite": "pl.py NOT-claimed ledger entries", "tier": "PRESUMED"},
    ]),
]
