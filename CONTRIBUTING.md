# Contributing — the registration gate

A contribution to /PL is a **candidate carrier or a candidate claim**, and
it enters the same way everything already here entered: by being computed,
not asserted.

## A new carrier must

1. **Declare its signature.** `V`, negation, AND, OR, designated set `D`,
   and the laws you *expect* to hold. Registration enumerates all 15 laws
   over `V` and refuses the carrier if it is not closed over `V` or if the
   enumerated laws contradict the declared signature. The gate is
   `register()` in `pl.py`; it cannot be talked past.
2. **Continuous carriers property-test.** Declared seed, and any failed
   law is proved by a single exhibited counterexample (the corpus method) —
   see FUZZY's LEM failure at 0.5 and PROB's distributivity failure at
   a=b=c=½ for the pattern.
3. **State the price.** Every signature costs something (K3 pays LEM, LP
   pays detachment, Ł3 pays idempotence/distributivity/absorption). A
   carrier claiming 15/15 on three values contradicts the Atlas's complete
   enumeration and will be refused by arithmetic, not by review.

## A new claim in any suite must

- carry a tier (`FORCED / EMPIRICAL / CONDITIONAL / STIPULATED / UNPAID`)
  and be **computed by the suite**, never transcribed from a document;
- keep the suite's exit code honest: a failed claim fails the build;
- keep the seals honest: editing a suite changes its `suite_sha256_16`,
  so re-run it and commit the regenerated manifest **in the same change**.
  `tests/run.py` enforces byte-parity and will fail any drift.

## Non-negotiables

- **No suite grades itself above STIPULATED.** Every suite contains
  stipulations; the weakest link rules.
- **Non-claims ship with the verdict.** If a contribution narrows a
  non-claim, it must replace it with the computation that pays for it.
- **T explicit.** No joule-denominated cost at a hidden temperature.
- **Documents are maps.** `PL_SPEC.md` and the workbook may not assert
  anything their kernels did not verify.

Run `python tests/run.py` before sending anything.
