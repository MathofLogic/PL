"""
demos/plboot.py — boot only on a passing self-audit.
==========================================================================
The kernel (pl.py) is not a library that happens to have tests; running it
IS the audit, and it ends by exiting with its verdict. This loader turns
that discipline into an import gate: executing pl.py in full, in a scratch
working directory, and handing back the live module ONLY if the kernel
earned exit 0. A kernel that failed its own enumeration never gets used.

    from plboot import boot
    pl = boot()          # raises RuntimeError unless the kernel PASSED

Nothing here weakens the kernel: the audit runs completely (all carriers
re-enumerated, all property tests re-run, the chain re-sealed) on every
boot. The cost is the point — it is the price of trusting the machinery.
"""
import contextlib, importlib.util, io, os, pathlib, sys, tempfile

KERNEL = pathlib.Path(__file__).resolve().parent.parent / "pl.py"


def boot(verbose=False):
    """Execute the kernel's full self-audit; return the module on PASS."""
    spec = importlib.util.spec_from_file_location("pl", KERNEL)
    mod = importlib.util.module_from_spec(spec)
    here = os.getcwd()
    code = None
    with tempfile.TemporaryDirectory() as scratch:
        os.chdir(scratch)                    # manifest writes stay scratch
        sink = sys.stdout if verbose else io.StringIO()
        try:
            with contextlib.redirect_stdout(sink):
                spec.loader.exec_module(mod)
            code = 0                          # (kernel always exits; belt+braces)
        except SystemExit as e:
            code = e.code or 0
        finally:
            os.chdir(here)
    if code != 0:
        raise RuntimeError("kernel self-audit FAILED - refusing to boot")
    if getattr(mod, "FAILED", None):
        raise RuntimeError(f"kernel reports failures: {mod.FAILED}")
    return mod
