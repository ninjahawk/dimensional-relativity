"""
Experiment 2 -- The decisive test on REALISTIC structure.

We grow a cosmic web from Gaussian initial conditions using the Zel'dovich
approximation (first-order Lagrangian perturbation theory -- the standard cheap
way to make the real filament/wall/cluster morphology of our universe). Then we
ask, point by point:

        Does effective dimension RISE or FALL with local density?

The naive hypothesis predicts: dense regions -> higher dimension.
The cosmic-web/correlation-function picture predicts the opposite:
matter collapses into 2-D walls, 1-D filaments and ~point-like clusters, so the
DENSE regions are LOWER dimensional, and space looks 3-D only on average.

We let the simulation decide.
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from dimension_tools import local_dimension, local_count, correlation_dimension

rng = np.random.default_rng(7)
OUT = "../figures"


def zeldovich_web(N=64, L=1.0, n_index=-2.4, growth=3.2, seed=7):
    """Grow a cosmic web. Returns particle positions in a periodic box [0,L)^3.

    n_index : slope of the initial power spectrum P(k) ~ k^n_index
    growth  : sets rms displacement in units of the cell size (>1 => shell
              crossing => filaments/clusters form)
    """
    rng = np.random.default_rng(seed)
    k1d = 2 * np.pi * np.fft.fftfreq(N, d=L / N)
    kx, ky, kz = np.meshgrid(k1d, k1d, k1d, indexing="ij")
    k2 = kx**2 + ky**2 + kz**2
    k2[0, 0, 0] = 1.0
    kmag = np.sqrt(k2)

    P = kmag**n_index
    P[0, 0, 0] = 0.0

    white_k = np.fft.fftn(rng.standard_normal((N, N, N)))
    delta_k = white_k * np.sqrt(P)
    delta_k[0, 0, 0] = 0.0

    # displacement Psi: grad^2 phi = delta, Psi = -grad phi => Psi_k = i k delta_k / k^2
    psi_x = np.fft.ifftn(1j * kx * delta_k / k2).real
    psi_y = np.fft.ifftn(1j * ky * delta_k / k2).real
    psi_z = np.fft.ifftn(1j * kz * delta_k / k2).real

    disp_rms = np.sqrt(np.mean(psi_x**2 + psi_y**2 + psi_z**2))
    A = growth * (L / N) / disp_rms          # rms displacement = growth cells

    g = np.arange(N) * (L / N)
    qx, qy, qz = np.meshgrid(g, g, g, indexing="ij")
    x = (qx + A * psi_x).ravel() % L
    y = (qy + A * psi_y).ravel() % L
    z = (qz + A * psi_z).ravel() % L
    return np.column_stack([x, y, z]), L


print("Growing cosmic web (Zel'dovich approximation)...")
pts, L = zeldovich_web(N=64, L=1.0, n_index=-2.4, growth=3.4)
box = [L, L, L]
print(f"  {len(pts)} particles in a periodic box.")

# density proxy: neighbour count in a fixed aperture
r0 = 0.035 * L
dens = local_count(pts, r0, boxsize=box)
print(f"  local density (count within r0={r0:.3f}): "
      f"min={dens.min():.0f}, median={np.median(dens):.0f}, max={dens.max():.0f}")

# per-point effective dimension (subsample query points for speed)
nq = 20000
qidx = rng.choice(len(pts), nq, replace=False)
Dloc = local_dimension(pts, k_min=12, k_max=120, boxsize=box,
                       query_points=pts[qidx])
dens_q = dens[qidx]
good = np.isfinite(Dloc)
Dloc, dens_q = Dloc[good], dens_q[good]

# bin dimension by density percentile
print("\n  Effective dimension vs local density:")
print("  density percentile      mean density      effective D")
edges = np.percentile(dens_q, np.linspace(0, 100, 9))
edges[-1] += 1e-6
binc, meanD, meandens = [], [], []
for i in range(len(edges) - 1):
    m = (dens_q >= edges[i]) & (dens_q < edges[i + 1])
    if m.sum() < 20:
        continue
    lo = int(100 * i / (len(edges) - 1))
    hi = int(100 * (i + 1) / (len(edges) - 1))
    print(f"    {lo:3d}-{hi:3d}%            {dens_q[m].mean():8.1f}        "
          f"{Dloc[m].mean():.3f}")
    binc.append((lo + hi) / 2)
    meanD.append(Dloc[m].mean())
    meandens.append(dens_q[m].mean())

corr = np.corrcoef(dens_q, Dloc)[0, 1]
print(f"\n  Pearson correlation (local density, local D) = {corr:+.3f}")
if corr < -0.05:
    print("  => DENSER regions are LOWER dimensional. Naive hypothesis is")
    print("     contradicted; the cosmic-web/correlation picture holds.")
elif corr > 0.05:
    print("  => DENSER regions are HIGHER dimensional. Supports the hypothesis!")
else:
    print("  => No clear relationship.")

# scale dependence: the transition to homogeneity (dimension that RUNS)
print("\n  Global correlation dimension vs scale (transition to homogeneity):")
D2, err, radii, C, slope_curve = correlation_dimension(
    pts, r_min=0.01 * L, r_max=0.5 * L, n_bins=22, boxsize=box)
for r, s in zip(radii[::3], slope_curve[::3]):
    print(f"    r = {r:5.3f} L   ->  local dimension D(r) = {s:4.2f}")


# ----------------------------------------------------------------- figures
fig = plt.figure(figsize=(15, 5))

# (1) a thin slice of the web, coloured by density
ax1 = fig.add_subplot(1, 3, 1)
sl = pts[:, 2] < 0.06 * L
sc = ax1.scatter(pts[sl, 0], pts[sl, 1], c=np.log10(dens[sl] + 1),
                 s=2, cmap="inferno")
ax1.set_title("Cosmic web (thin slice)\ncolour = log local density")
ax1.set_aspect("equal"); ax1.set_xlabel("x"); ax1.set_ylabel("y")
plt.colorbar(sc, ax=ax1, fraction=0.046)

# (2) the money plot: D vs local density
ax2 = fig.add_subplot(1, 3, 2)
ax2.scatter(dens_q, Dloc, s=2, alpha=0.08, color="steelblue")
ax2.plot(meandens, meanD, "o-", color="crimson", lw=2, ms=7,
         label="binned mean")
ax2.axhline(3, ls="--", color="gray", label="D = 3 (smooth space)")
ax2.set_xscale("log")
ax2.set_xlabel("local density (count within r0)")
ax2.set_ylabel("effective dimension D")
ax2.set_title(f"Dimension vs local density\nPearson r = {corr:+.3f}")
ax2.legend(); ax2.grid(alpha=0.3)

# (3) running dimension with scale
ax3 = fig.add_subplot(1, 3, 3)
ax3.plot(radii / L, slope_curve, "o-", color="darkgreen")
ax3.axhline(3, ls="--", color="gray", label="homogeneous limit D=3")
ax3.set_xscale("log")
ax3.set_xlabel("scale  r / L")
ax3.set_ylabel("dimension D(r)")
ax3.set_title("Dimension RUNS with scale\n(transition to homogeneity)")
ax3.legend(); ax3.grid(alpha=0.3)

plt.tight_layout()
plt.savefig(f"{OUT}/exp2_cosmicweb.png", dpi=130)
print(f"\n  figure saved -> figures/exp2_cosmicweb.png")
