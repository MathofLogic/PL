#!/usr/bin/env python3
"""Re-derive library carriers' forced laws by enumeration; check vs claims.
The point: an entry is not authority — it is a spec you can re-run."""

class Carrier:
    def __init__(self, name, V, NOT, AND, OR, bottom, top, designated=None):
        self.name, self.V = name, V
        self.NOT, self.AND, self.OR, self.bottom, self.top = NOT, AND, OR, bottom, top
    def laws(self):
        return {
            "LNC": all(self.AND(v, self.NOT(v)) == self.bottom for v in self.V),
            "LEM": all(self.OR(v, self.NOT(v)) == self.top for v in self.V),
            "DN":  all(self.NOT(self.NOT(v)) == v for v in self.V),
        }

NOT = lambda v: 1 - v
B = 0.5  # 'both' / paradoxical value, self-negating under 1-v

carriers = {
    # name: (Carrier, claimed laws from the library)
    "01 Classical {0,1}":
        (Carrier("classical", [0,1], NOT, lambda a,b: a*b, max, 0, 1),
         {"LNC": True, "LEM": True, "DN": True}),
    "03 Kleene K3 {0,1/2,1}  (min/max)":
        (Carrier("K3", [0,0.5,1], NOT, min, max, 0, 1),
         {"LNC": False, "LEM": False, "DN": True}),
    "02 Lukasiewicz L3 {0,1/2,1}  (strong t-norm)":
        (Carrier("L3", [0,0.5,1], NOT,
                 lambda a,b: max(0, a+b-1), lambda a,b: min(1, a+b), 0, 1),
         {"LNC": True, "LEM": True, "DN": True}),
    "06 Priest LP {0,B,1}  (B designated)":
        (Carrier("LP", [0,B,1], NOT, min, max, 0, 1),
         {"LNC": False, "DN": True}),  # LNC breaks at B; library lists these
}

print("="*78)
print("  LIBRARY CARRIERS RE-DERIVED BY ENUMERATION  (computed vs claimed)")
print("="*78)
allmatch = True
for name, (c, claimed) in carriers.items():
    got = c.laws()
    print(f"\n  {name}")
    for law, claim_v in claimed.items():
        ok = got[law] == claim_v
        allmatch &= ok
        print(f"    {law:4s} computed={str(got[law]):5s} claimed={str(claim_v):5s} "
              f"[{'MATCH' if ok else 'MISMATCH'}]")

print("\n" + "="*78)
print("  HEADLINE: same V={0,1/2,1}, different G -> different forced law")
k3  = carriers["03 Kleene K3 {0,1/2,1}  (min/max)"][0].laws()
l3  = carriers["02 Lukasiewicz L3 {0,1/2,1}  (strong t-norm)"][0].laws()
print(f"    K3 (AND=min,  OR=max)          LEM = {k3['LEM']}")
print(f"    L3 (AND=max(0,a+b-1), OR=min(1,a+b))  LEM = {l3['LEM']}")
print("    -> the law is a property of G on V, not a fact to look up.")
print("="*78)
print(f"  ALL ENUMERATIONS MATCH LIBRARY CLAIMS: {allmatch}")
print("="*78)
import sys; sys.exit(0 if allmatch else 1)
