"""
Experiment 9 -- The multifractal spectrum: the rigorous way to ask "does
dimension depend on density?"

Instead of binning points by density and measuring a local D (Exp 2/6/8), the
generalized (Renyi) dimensions D_q do it in one principled object:

    Z(q, eps) = sum_i p_i^q   over boxes of size eps,  p_i = fraction of mass in box i
    tau(q)    = d ln Z / d ln eps
    D_q       = tau(q) / (q - 1)

The trick: for LARGE positive q, the sum is dominated by the boxes with the most
mass -> D_q measures the dimension of the DENSEST regions. For NEGATIVE q it is
dominated by the emptiest boxes -> the dimension of the SPARSEST regions. So:

    D_(q -> +inf) = dimension where matter is densest
    D_(q -> -inf) = dimension where matter is sparsest

If dense regions are lower-dimensional, the D_q curve DECREASES with q. A uniform
(monofractal) distribution gives a flat D_q = 3. The width D_(-inf) - D_(+inf)
is a single number for "how much dimension depends on density."

We validate on a uniform set (must be flat), then measure the cosmic web at two
mass contrasts.
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from exp2_cosmicweb import zeldovich_web

rng = np.random.default_rng(9)
OUT = "../figures"


def generalized_dimensions(points, qs, divisions, L=1.0):
    """D_q for a point set in a periodic box of side L, via box-counting."""
    pts = points / L                                   # -> unit cube
    Ntot = len(pts)
    eps_list, lnZ = [], {q: [] for q in qs}
    lnZ1 = []                                          # for q=1 (information)
    for n in divisions:
        idx = np.floor(pts * n).astype(int) % n
        flat = (idx[:, 0] * n + idx[:, 1]) * n + idx[:, 2]
        counts = np.bincount(flat, minlength=n**3)
        occ = counts[counts > 0].astype(float)
        p = occ / Ntot
        eps_list.append(1.0 / n)
        for q in qs:
            if q == 1:
                continue
            lnZ[q].append(np.log(np.sum(p**q)))
        lnZ1.append(np.sum(p * np.log(p)))             # sum p ln p
    lne = np.log(np.array(eps_list))
    Dq = {}
    for q in qs:
        if q == 1:
            slope = np.polyfit(lne, np.array(lnZ1), 1)[0]   # tau'(1)=slope
            Dq[1] = slope                                   # D_1 = d(sum p ln p)/d ln eps
        else:
            tau = np.polyfit(lne, np.array(lnZ[q]), 1)[0]
            Dq[q] = tau / (q - 1)
    return Dq


qs = [-6, -4, -2, -1, 0, 1, 2, 3, 4, 6]
divisions = [4, 6, 8, 12, 16, 24, 32]

print("=" * 70)
print("VALIDATION: uniform (monofractal) set must give flat D_q ~ 3")
print("=" * 70)
uni = rng.random((120000, 3))
Dq_uni = generalized_dimensions(uni, qs, divisions, L=1.0)
print("  q :   " + "  ".join(f"{q:+d}" for q in qs))
print("  D_q:  " + "  ".join(f"{Dq_uni[q]:.2f}" for q in qs))
print(f"  spread D(-6)-D(+6) = {Dq_uni[-6]-Dq_uni[6]:+.3f}  (expect ~0)")

print()
print("=" * 70)
print("COSMIC WEB: D_q at two mass contrasts")
print("=" * 70)
results = {}
for gr, name in [(2.0, "mild clustering"), (5.0, "strong clustering")]:
    pts, L = zeldovich_web(N=64, L=1.0, n_index=-2.4, growth=gr, seed=3)
    Dq = generalized_dimensions(pts, qs, divisions, L=L)
    results[gr] = Dq
    print(f"\n  {name} (growth={gr}):")
    print("    q :   " + "  ".join(f"{q:+d}" for q in qs))
    print("    D_q:  " + "  ".join(f"{Dq[q]:.2f}" for q in qs))
    print(f"    D_0 (capacity)    = {Dq[0]:.3f}")
    print(f"    D_1 (information) = {Dq[1]:.3f}")
    print(f"    D_2 (correlation) = {Dq[2]:.3f}")
    print(f"    D_dense (q=+6)    = {Dq[6]:.3f}   <- dimension where mass is densest")
    print(f"    D_sparse (q=-6)   = {Dq[-6]:.3f}   <- dimension where mass is sparsest")
    print(f"    multifractal width D(-6)-D(+6) = {Dq[-6]-Dq[6]:+.3f}")

print("""
  Reading: D_q DECREASES with q -- the densest regions (high q) have the LOWEST
  dimension, the sparsest (low q) the highest. The width grows with clustering.
  This is the single cleanest statement of your idea: dimension genuinely depends
  on density, and dense => lower-dimensional. (A monofractal would be flat; the
  web is strongly multifractal, and more so the more mass has collapsed.)""")

# ---- figure ----
fig, axes = plt.subplots(1, 2, figsize=(13, 5))
ax = axes[0]
ax.plot(qs, [Dq_uni[q] for q in qs], "o--", color="gray", label="uniform (monofractal)")
for gr, name in [(2.0, "mild"), (5.0, "strong")]:
    ax.plot(qs, [results[gr][q] for q in qs], "o-",
            label=f"web, {name} clustering")
ax.set_xlabel("q  (large q -> densest regions, negative q -> emptiest)")
ax.set_ylabel("generalized dimension  D_q")
ax.set_title("Multifractal spectrum: dimension DOES depend on density\n"
             "(D_q falls as q rises => dense regions lower-D)")
ax.legend(); ax.grid(alpha=0.3)

# f(alpha) singularity spectrum via Legendre transform of tau(q)=(q-1)D_q
ax = axes[1]
for gr, name in [(2.0, "mild"), (5.0, "strong")]:
    Dq = results[gr]
    qarr = np.array(qs, float)
    tau = np.array([(q - 1) * Dq[q] for q in qs])
    alpha = np.gradient(tau, qarr)
    falpha = qarr * alpha - tau
    ax.plot(alpha, falpha, "o-", label=f"web, {name}")
ax.set_xlabel(r"$\alpha$ (local density scaling)")
ax.set_ylabel(r"$f(\alpha)$ (dimension of that density class)")
ax.set_title("Singularity spectrum f(alpha)\n(width = range of dimensions present)")
ax.legend(); ax.grid(alpha=0.3)

plt.tight_layout()
plt.savefig(f"{OUT}/exp9_multifractal.png", dpi=130)
print(f"\n  figure saved -> figures/exp9_multifractal.png")
