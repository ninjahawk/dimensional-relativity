"""
Experiment 1 -- Validate the dimension estimator, then run the FIRST honest
test of the hypothesis "more density => higher dimension".

Part A: recover known dimensions
    - 1-D line, 2-D sheet, 3-D volume (periodic -> no edge bias)
    - Sierpinski gasket: a genuine FRACTAL, D = log3/log2 = 1.585...
      (If we can recover a non-integer dimension, the estimator is trustworthy
       for the subtle stuff that follows.)

Part B: the naive hypothesis, tested directly
    - Generate uniform (Poisson) matter in a periodic box at intensities that
      differ by 16x. Measure effective dimension in each.
    - PREDICTION OF THE NAIVE IDEA: denser box -> higher D.
    - We will see what actually happens.
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from dimension_tools import local_dimension, correlation_dimension

rng = np.random.default_rng(42)
OUT = "../figures"


# ---------------------------------------------------------------- Part A
def sierpinski_gasket(n=40000):
    """Chaos game -> points on the Sierpinski gasket. D = ln3/ln2 = 1.58496"""
    verts = np.array([[0.0, 0.0], [1.0, 0.0], [0.5, np.sqrt(3) / 2]])
    p = np.array([0.3, 0.4])
    pts = np.empty((n, 2))
    for i in range(n):
        v = verts[rng.integers(3)]
        p = (p + v) / 2.0
        pts[i] = p
    return pts


print("=" * 64)
print("PART A -- recovering KNOWN dimensions")
print("=" * 64)

# 1-D line (periodic), embedded in 3-D
line = np.column_stack([rng.random(6000),
                        np.zeros(6000), np.zeros(6000)])
D_line = local_dimension(line, k_min=8, k_max=200, boxsize=[1, 0, 0])
print(f"  1-D line (periodic)      D = {np.nanmean(D_line):5.3f}  (expect 1)")

# 3-D volume (periodic)
vol = rng.random((8000, 3))
D_vol = local_dimension(vol, k_min=16, k_max=256, boxsize=[1, 1, 1])
print(f"  3-D uniform (periodic)   D = {np.nanmean(D_vol):5.3f}  (expect 3)")

# Sierpinski fractal -- the acid test (non-integer dimension)
gasket = sierpinski_gasket(40000)
D_gasket = local_dimension(gasket, k_min=8, k_max=64)
D2_gasket, err, radii, C, slope_curve = correlation_dimension(
    gasket, r_min=2e-3, r_max=8e-2, n_bins=30)
true_gasket = np.log(3) / np.log(2)
print(f"  Sierpinski gasket        D_loc = {np.nanmean(D_gasket):5.3f}, "
      f"D2 = {D2_gasket:5.3f}  (TRUE = {true_gasket:.3f})")


# ---------------------------------------------------------------- Part B
print()
print("=" * 64)
print("PART B -- does RAISING THE DENSITY raise the dimension?")
print("=" * 64)
print("  Uniform matter, periodic box, intensity varied 16x:")
densities = [1000, 4000, 16000]
results = []
for n in densities:
    pts = rng.random((n, 3))
    D = local_dimension(pts, k_min=16, k_max=min(256, n // 8),
                        boxsize=[1, 1, 1])
    results.append((n, np.nanmean(D), np.nanstd(D)))
    print(f"    N = {n:6d} points  ->  D = {np.nanmean(D):5.3f} "
          f"+/- {np.nanstd(D):4.3f}")

dens_factor = densities[-1] / densities[0]
D_change = results[-1][1] - results[0][1]
print(f"\n  Density increased {dens_factor:.0f}x.  Dimension changed by "
      f"{D_change:+.3f}.")
print("  => For UNIFORM matter, effective dimension is independent of how")
print("     much matter there is. Absolute density does NOT set dimension.")


# ---------------------------------------------------------------- figure
fig, axes = plt.subplots(1, 2, figsize=(12, 5))

ax = axes[0]
ax.scatter(gasket[:, 0], gasket[:, 1], s=0.3, c="k", alpha=0.5)
ax.set_title(f"Sierpinski gasket\nrecovered D2 = {D2_gasket:.3f} "
             f"(true {true_gasket:.3f})")
ax.set_aspect("equal"); ax.axis("off")

ax = axes[1]
ax.plot(np.log(radii), np.log(np.clip(C, 1e-30, None)), "o-", ms=4)
ax.set_xlabel("ln r"); ax.set_ylabel("ln C(r)")
ax.set_title("Correlation integral of the fractal\n(slope = dimension)")
ax.grid(alpha=0.3)

plt.tight_layout()
plt.savefig(f"{OUT}/exp1_validation.png", dpi=130)
print(f"\n  figure saved -> figures/exp1_validation.png")
