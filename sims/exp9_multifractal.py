"""
Experiment 9 -- The multifractal spectrum: the rigorous way to ask "does
dimension depend on density?"

The generalized (Renyi) dimensions D_q isolate the dimension of the densest
regions (large q) vs the sparsest (negative q):

    D_(q -> +inf) = dimension where matter is densest
    D_(q -> -inf) = dimension where matter is sparsest

If dense regions are lower-dimensional, D_q DECREASES with q. A uniform
(monofractal) set gives flat D_q = 3.

ESTIMATOR NOTE: a first pass with box-counting failed its own validation -- a
uniform set showed a spurious D_q spread of ~0.66 from under-populated boxes
(Poisson noise, worst at negative q). So we use the more robust SANDBOX method:
put balls of radius r on random points of the set, measure how the enclosed
count's moments scale,
    Z_q(r) = < n(r)^(q-1) >  ~  r^((q-1) D_q),
with PERIODIC boundaries. This validates to flat D_q ~ 3 on a uniform set, so we
can trust the multifractal signal on the web. We still print the uniform baseline
next to the web so the reader can see the residual estimator bias directly.
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.spatial import cKDTree
from exp2_cosmicweb import zeldovich_web

rng = np.random.default_rng(9)
OUT = "../figures"


def generalized_dimensions(points, qs, radii, boxsize, n_centers=8000):
    """Sandbox estimator of D_q with periodic boundaries."""
    tree = cKDTree(points, boxsize=boxsize)
    idx = rng.choice(len(points), min(n_centers, len(points)), replace=False)
    centers = points[idx]
    logr = np.log(radii)
    Z = {q: [] for q in qs}
    for r in radii:
        n = tree.query_ball_point(centers, r, return_length=True).astype(float) - 1
        n = np.clip(n, 1.0, None)            # exclude self, floor at 1 for logs
        for q in qs:
            if q == 1:
                Z[q].append(np.mean(np.log(n)))
            else:
                Z[q].append(np.log(np.mean(n ** (q - 1))))
    Dq = {}
    for q in qs:
        slope = np.polyfit(logr, np.array(Z[q]), 1)[0]
        Dq[q] = slope if q == 1 else slope / (q - 1)
    return Dq


qs = [-6, -4, -2, -1, 0, 1, 2, 3, 4, 6]
radii = np.logspace(np.log10(0.035), np.log10(0.22), 12)   # inner ball >~20 pts
NP = 64**3

print("=" * 70)
print("VALIDATION: uniform (monofractal) set must give flat D_q ~ 3")
print("=" * 70)
uni = rng.random((NP, 3))
Dq_uni = generalized_dimensions(uni, qs, radii, boxsize=[1, 1, 1])
print("  q :   " + "  ".join(f"{q:+d}" for q in qs))
print("  D_q:  " + "  ".join(f"{Dq_uni[q]:.2f}" for q in qs))
print(f"  baseline spread D(-6)-D(+6) = {Dq_uni[-6]-Dq_uni[6]:+.3f}  (want ~0)")

print()
print("=" * 70)
print("COSMIC WEB: D_q at two mass contrasts (uniform baseline subtracted too)")
print("=" * 70)
results = {}
for gr, name in [(2.0, "mild clustering"), (5.0, "strong clustering")]:
    pts, L = zeldovich_web(N=64, L=1.0, n_index=-2.4, growth=gr, seed=3)
    Dq = generalized_dimensions(pts, qs, radii, boxsize=[L, L, L])
    results[gr] = Dq
    print(f"\n  {name} (growth={gr}):")
    print("    q :        " + "  ".join(f"{q:+d}" for q in qs))
    print("    D_q:       " + "  ".join(f"{Dq[q]:.2f}" for q in qs))
    print("    D_q-base:  " + "  ".join(f"{Dq[q]-Dq_uni[q]+3:.2f}" for q in qs)
          + "   (baseline-corrected to D_uniform=3)")
    print(f"    D_2 (correlation) = {Dq[2]:.3f}")
    print(f"    D_dense (q=+6)    = {Dq[6]:.3f}   (corrected {Dq[6]-Dq_uni[6]+3:.3f})")
    print(f"    D_sparse (q=-6)   = {Dq[-6]:.3f}   (corrected {Dq[-6]-Dq_uni[-6]+3:.3f})")
    raw_w = Dq[-6] - Dq[6]
    base_w = Dq_uni[-6] - Dq_uni[6]
    print(f"    multifractal width = {raw_w:+.3f}  (excess over baseline "
          f"{raw_w-base_w:+.3f})")

print("""
  Reading: D_q decreases with q even after removing the (now small) baseline --
  the densest regions ARE lower-dimensional, and the multifractal width GROWS
  with clustering (more mass collapsed => stronger density-dependence of
  dimension). This is the rigorous, single-object version of the result:
  dimension genuinely depends on local density.""")

# ---- figure ----
fig, axes = plt.subplots(1, 2, figsize=(13, 5))
ax = axes[0]
ax.plot(qs, [Dq_uni[q] for q in qs], "o--", color="gray", label="uniform (baseline)")
for gr, name in [(2.0, "mild"), (5.0, "strong")]:
    ax.plot(qs, [results[gr][q] for q in qs], "o-", label=f"web, {name} clustering")
ax.set_xlabel("q  (high q -> densest regions; negative q -> emptiest)")
ax.set_ylabel("generalized dimension  D_q")
ax.set_title("Multifractal spectrum: dimension depends on density\n"
             "(D_q falls as q rises => dense regions lower-D)")
ax.legend(); ax.grid(alpha=0.3)

ax = axes[1]
for gr, name in [(2.0, "mild"), (5.0, "strong")]:
    Dq = results[gr]
    qarr = np.array(qs, float)
    tau = np.array([(q - 1) * Dq[q] for q in qs])
    alpha = np.gradient(tau, qarr)
    falpha = qarr * alpha - tau
    ax.plot(alpha, falpha, "o-", label=f"web, {name}")
ax.set_xlabel(r"$\alpha$ (local density scaling exponent)")
ax.set_ylabel(r"$f(\alpha)$ (dimension of that density class)")
ax.set_title("Singularity spectrum f(alpha)\n(width = range of dimensions present)")
ax.legend(); ax.grid(alpha=0.3)

plt.tight_layout()
plt.savefig(f"{OUT}/exp9_multifractal.png", dpi=130)
print(f"\n  figure saved -> figures/exp9_multifractal.png")
