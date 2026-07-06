# Source notes — provenance of /PL

Refined out of the flat MathofLogic project dump on 2026-07-06. Everything
was executed before inclusion; every statement below names its check.

## Included byte-identical (sha-sealed — do not edit casually)

| file | sha256[:16] | verified by |
|---|---|---|
| `pl.py` | `bfddc7d82986ba9b` | runs to exit 0; regenerated `pl_manifest.json` is byte-identical to the manifest shipped in the dump |
| `atlas3.py` | `ab59172abd6618cb` | same discipline; 354,294-carrier enumeration reproduces, ~2 s |
| `pl_guide_audit.py` | `318db3aa0606a917` | same; manifest byte-identical to shipped |
| `workbook_verified.py` | — | runs to exit 0, 51 claims PASS; its manifest was **not** in the dump, so the seal committed in `manifests/` was cut here and confirmed deterministic (two independent runs, byte-identical) |
| `pl_dras.py`, `carrier_verify.py` | — | run to exit 0; carrier_verify's independent enumeration matches the library claims |
| `PL_SPEC.md` | — | its quoted verdicts, chain lengths, check counts, and `bfddc7d82986ba9b` sha were all confirmed against the live run |

Determinism was tested explicitly: each suite was run twice in separate
scratch directories and every manifest compared byte-for-byte. All four
are deterministic, which is what lets `tests/run.py` enforce seal parity.

## Added in this refinement (new code, itself gated)

- `demos/plboot.py` — the boot gate. The kernel is a run-only suite ending
  in `sys.exit(verdict)`; this loader executes it in full in a scratch cwd
  and returns the live module only on exit 0. Fails closed.
- `demos/diagnostics.py` — the computing/system-diagnostics application
  layer: 15 claims (12 FORCED, 2 CONDITIONAL, 1 STIPULATED), every one
  asserted against the booted kernel's own carrier tables and machinery;
  exits 1 on any failure. One authoring error was caught by its own gate
  during development (the tropical self-description lives in the kernel's
  manifest, not its finite-carrier REGISTRY) and fixed before sealing.
- `tests/run.py`, CI workflow, `CONTRIBUTING.md`, `README.md`,
  `pyproject.toml`, this file.

## Deliberately excluded

- The audit toolbox, resistance/delta/testimpact carriers, and the Rigor
  Suite instrument — they live in **/rigor**, which stands alone.
- The large PDFs (`propagation_logic_150_complete.pdf`, the carrier
  library, the mapping guide, the workbook PDF, the codebase paper,
  ~20 MB combined). The verified, executable form of their content is
  this repo; the PDFs are typeset presentations of the same sealed runs
  and can be attached as release assets rather than repo weight. Note
  the discipline this preserves: the documents are maps of the code's
  territory, so the code is the canonical artifact.

## Known non-claims of this repo (inherited from the suites)

The registry does not exhaust formal systems; load does not equal physical
energy without an implementation map; the tier order is a stipulation the
kernel cannot outrank; law-signatures do not individuate logics (RM3 and
LP share one in the Atlas); the Atlas space excludes non-conservative
negations. These are printed, tier UNPAID, in every relevant run.
