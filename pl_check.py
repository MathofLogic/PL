"""
pl_checks.py — the /PL check registry.
==========================================================================
Named, executable checks backing the root claims.py ledger. Each check
recomputes something INDEPENDENTLY of the suite that wrote it: the
kernel sha from the kernel's bytes, the chains from seal arithmetic,
the carrier facts from the committed manifest whose bytes the gate
holds to parity and whose chain must replay. The checks FORCE the
sealed record's internal consistency — they do not, and cannot, force
the mapping from the record to the world (that rider is standing).
"""
from __future__ import annotations
import hashlib, json, pathlib

ROOT = pathlib.Path(__file__).resolve().parent


def _manifest(name="pl_manifest.json"):
    return json.loads((ROOT / "manifests" / name).read_text())


def _replay(chain):
    if not isinstance(chain, list) or not all(
            isinstance(g, dict) and "sha" in g and "sha_prev" in g
            for g in chain):
        return None
    prev = "GENESIS"
    for g in chain:
        body = {k: v for k, v in g.items()
                if k not in ("sha", "sha_prev")}
        want = hashlib.sha256((prev + json.dumps(body, sort_keys=True))
                              .encode()).hexdigest()[:16]
        if g["sha_prev"] != prev or g["sha"] != want:
            return False
        prev = g["sha"]
    return True


def chk_kernel_sha_recomputes():
    """sha256(pl.py)[:16] recomputed from the kernel's own bytes
    equals the sealed suite_sha256_16 — a one-character edit to the
    instrument announces itself as a new instrument."""
    real = hashlib.sha256((ROOT / "pl.py").read_bytes()).hexdigest()[:16]
    return real == _manifest()["suite_sha256_16"]


def chk_all_chains_replay():
    """Every committed manifest carries a sha-linked chain that
    replays by seal arithmetic alone — no writer consulted."""
    for mf in sorted((ROOT / "manifests").glob("*.json")):
        doc = json.loads(mf.read_text())
        chain = doc.get("chain") if isinstance(doc, dict) else doc
        if _replay(chain) is not True:
            return False
    return True


def chk_classical_carrier_closed():
    """CL2 enumerates closed: all 15 laws hold, including LEM, LNC,
    NoGlut, and MP."""
    c = _manifest()["carriers"]["CL2  classical"]
    return len(c) == 15 and all(c.values())


def chk_k3_drops_lem_keeps_lnc():
    """K3 (strong Kleene): LEM fails, LNC holds, MP holds — the gap
    carrier, priced exactly."""
    c = _manifest()["carriers"]["K3   strong Kleene"]
    return (c["LEM"] is False and c["LNC"] is True
            and c["MP"] is True)


def chk_lp_glut_costs_mp():
    """LP (Priest): LNC and NoGlut fail and MP fails with them — the
    glut carrier pays for its gluts in detachment."""
    c = _manifest()["carriers"]["LP   priest"]
    return (c["LNC"] is False and c["NoGlut"] is False
            and c["MP"] is False and c["LEM"] is True)


def chk_fde_drops_both():
    """FDE: both LEM and LNC fail, MP fails — the four-valued floor."""
    c = _manifest()["carriers"]["FDE  four-valued"]
    return (c["LEM"] is False and c["LNC"] is False
            and c["MP"] is False)


def chk_load_is_priced():
    """The enumeration's cost is on the books: 20,780 load checks
    under a fixed seed, sealed with the verdict they earned."""
    m = _manifest()
    return m["load_checks"] == 20780 and m["seed"] == 20260702


def chk_forced_claims_verified():
    """Every claim sealed at FORCED carries verified=True — no tier is
    asserted above its evidence in the kernel's own ledger."""
    return all(c.get("verified") is True
               for c in _manifest()["claims"]
               if c.get("tier") == "FORCED")


def chk_verdict_capped_stipulated():
    """The kernel's self-verdict is PASS/STIPULATED with UNPAID
    entries priced — a map that graded itself FORCED would be lying."""
    m = _manifest()
    return (m["verdict"] == "PASS/STIPULATED"
            and m["summary"].get("UNPAID", 0) >= 1)


def chk_nonclaims_sealed():
    """The kernel's negative space is in the sealed ledger itself: at
    least three NOT-claimed statements, priced UNPAID."""
    ncs = [c for c in _manifest()["claims"]
           if str(c.get("statement", "")).startswith("NOT claimed")]
    return len(ncs) >= 3 and all(c.get("tier") == "UNPAID" for c in ncs)


CHECKS = {
    "kernel_sha_recomputes": chk_kernel_sha_recomputes,
    "all_chains_replay": chk_all_chains_replay,
    "classical_carrier_closed": chk_classical_carrier_closed,
    "k3_drops_lem_keeps_lnc": chk_k3_drops_lem_keeps_lnc,
    "lp_glut_costs_mp": chk_lp_glut_costs_mp,
    "fde_drops_both": chk_fde_drops_both,
    "load_is_priced": chk_load_is_priced,
    "forced_claims_verified": chk_forced_claims_verified,
    "verdict_capped_stipulated": chk_verdict_capped_stipulated,
    "nonclaims_sealed": chk_nonclaims_sealed,
}
