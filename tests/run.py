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

print("\nDEMOS (every claim re-derived on a freshly booted kernel)")
r = subprocess.run([sys.executable, str(ROOT / "demos/diagnostics.py")],
                   capture_output=True, text=True, timeout=600)
check("demos/diagnostics.py all claims hold", r.returncode == 0,
      r.stdout.strip().splitlines()[-3].strip() if r.returncode == 0 else
      (r.stdout + r.stderr)[-200:])

print("\n" + ("BUILD PASSED" if not fails else f"BUILD FAILED: {fails}"))
sys.exit(1 if fails else 0)
