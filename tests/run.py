#!/usr/bin/env python3
"""tests/run.py — the /PL build gate.

Four disciplines, enforced in order:
  1. SUITES PASS      every suite runs to exit 0 (running IS the audit).
  2. SEALS MATCH      each regenerated manifest is byte-identical to the
                      committed seal in manifests/. The manifests are
                      deterministic by construction; any drift means the
                      source changed and the seal must be re-cut on purpose.
  3. CROSS-CHECK      carrier_verify.py independently re-enumerates the
                      carrier laws and must agree with the library claims.
  4. DEMOS HOLD       demos/diagnostics.py re-derives every one of its
                      claims on a freshly booted kernel.

Byte-parity is deliberately strict: the suite sha is the sha256 of the
suite's own source, so a one-character edit to pl.py is a new instrument
and must announce itself as one.
"""
import filecmp, pathlib, subprocess, sys, tempfile, shutil

ROOT = pathlib.Path(__file__).resolve().parent.parent
SUITES = {                      # suite file -> manifest it seals (or None)
    "pl.py": "pl_manifest.json",
    "atlas3.py": "atlas_manifest.json",
    "pl_guide_audit.py": "pl_guide_audit_manifest.json",
    "workbook_verified.py": "workbook_manifest.json",
    "pl_dras.py": None,
    "carrier_verify.py": None,
}

fails = []


def check(name, ok, detail=""):
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}"
          + (f" — {detail}" if detail else ""))
    if not ok:
        fails.append(name)


def replay(chain):
    """Independent chain verification: no suite, no writer, just the
    seal arithmetic. Validating regenerated output alone validates the
    writer; the committed HISTORY must also replay on its own."""
    import hashlib, json as _j
    if not isinstance(chain, list) or not all(
            isinstance(g, dict) and "sha" in g and "sha_prev" in g
            for g in chain):
        return None
    prev = "GENESIS"
    for g in chain:
        body = {k: v for k, v in g.items()
                if k not in ("sha", "sha_prev")}
        want = hashlib.sha256((prev + _j.dumps(body, sort_keys=True))
                              .encode()).hexdigest()[:16]
        if g["sha_prev"] != prev or g["sha"] != want:
            return False
        prev = g["sha"]
    return True


print("HISTORY (committed seal chains replay WITHOUT their writers —")
print("tampering with a shipped manifest must be visible before any")
print("suite regenerates anything)")
import json as _json
for _mf in sorted((ROOT / "manifests").glob("*.json")):
    _doc = _json.loads(_mf.read_text())
    _chain = _doc.get("chain") if isinstance(_doc, dict) else _doc
    _r = replay(_chain)
    check(f"{_mf.name} chain replays independently", _r is True,
          "no sha-linked chain found" if _r is None else
          ("" if _r else "chain broken — possible tampering"))


print("SUITES + SEALS (run in scratch cwd; regenerated manifests must be")
print("byte-identical to the committed seals in manifests/)")
with tempfile.TemporaryDirectory() as scratch:
    scratch = pathlib.Path(scratch)
    for suite, manifest in SUITES.items():
        shutil.copy(ROOT / suite, scratch / suite)
        r = subprocess.run([sys.executable, suite], cwd=scratch,
                           capture_output=True, text=True, timeout=600)
        check(f"{suite} exits 0", r.returncode == 0,
              (r.stdout + r.stderr).strip().splitlines()[-1][:70]
              if r.returncode else "")
        if manifest:
            same = filecmp.cmp(scratch / manifest,
                               ROOT / "manifests" / manifest, shallow=False)
            check(f"{manifest} == committed seal (byte-identical)", same)

print("\nLEDGER (root claims.py is backed by pl_checks.py; every check "
      "runs here)")
sys.path.insert(0, str(ROOT))
import claims as _claims
import pl_checks as _plc
for _name, _fn in _plc.CHECKS.items():
    try:
        check(_name, _fn() is True)
    except Exception as _e:
        check(_name, False, f"{type(_e).__name__}: {_e}")
_ledgered = {c["check"] for _, cs in _claims.SECTIONS
             for c in cs if c.get("check")}
check("no ledgered check dangles; no registry check is orphaned",
      _ledgered == set(_plc.CHECKS))

print("\nDEMOS (every claim re-derived on a freshly booted kernel)")
r = subprocess.run([sys.executable, str(ROOT / "demos/diagnostics.py")],
                   capture_output=True, text=True, timeout=600)
check("demos/diagnostics.py all claims hold", r.returncode == 0,
      r.stdout.strip().splitlines()[-3].strip() if r.returncode == 0 else
      (r.stdout + r.stderr)[-200:])

# the kernel states its non-claims on every run; the gate must not
# swallow that voice — negative space is part of the verdict
print("\nNON-CLAIMS (the kernel's own, surfaced from the sealed ledger)")
_pl = _json.loads((ROOT / "manifests" / "pl_manifest.json").read_text())
_nc = [c["statement"] for c in _pl.get("claims", [])
       if str(c.get("statement", "")).startswith("NOT claimed")]
for _s in _nc:
    print("  " + _s)
check("kernel non-claims present in the sealed ledger", len(_nc) >= 3)
print("  NOT claimed: that byte-parity seals + replayed chains are "
      "tamper-proof —\n      they are tamper-EVIDENT under this gate's "
      "finite probes, nothing more.")

print("\n" + ("BUILD PASSED" if not fails else f"BUILD FAILED: {fails}"))
sys.exit(1 if fails else 0)
