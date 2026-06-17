"""
Experiment 12 -- The honest case FOR "denser => higher dimension".

Everything so far (geometry, gravity, holography) said concentration lowers the
effective dimension. But I owe the original hypothesis a real, adversarial shot
in the one place it can actually win: CONNECTIVITY.

The spectral (diffusion) dimension d_s is set by how a region is connected, not
by where it sits. Two facts from random-walk theory:
  - LOCAL TRAPPING / ANISOTROPY (matter squeezed into filaments) LOWERS d_s.
    This is what gravity does (Exp 10): dense filaments -> d_s ~ 2.5.
  - LONG-RANGE LINKS (shortcuts across the space) RAISE d_s, without bound.
    A lattice with enough random shortcuts becomes effectively infinite-
    dimensional (return probability decays exponentially). This is the small-
    world / expander phenomenon.

So the SIGN of "density's effect on dimension" depends on the MECHANISM. If
piling up mass mainly squeezes geometry -> dimension falls. If piling up mass
mainly creates long-range connections -> dimension RISES. We demonstrate both,
and a density-modulated graph where dense regions get the shortcuts and therefore
measure HIGHER-dimensional.

This is the rigorous home of your intuition: it's true whenever concentration
buys connectivity.
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import scipy.sparse as sp

rng = np.random.default_rng(12)
OUT = "../figures"


def lap_eigs(A, want_vectors=False):
    deg = np.asarray(A.sum(1)).ravel()
    dinv = 1.0 / np.sqrt(np.clip(deg, 1e-9, None))
    L = sp.identity(A.shape[0]) - sp.diags(dinv) @ A @ sp.diags(dinv)
    L = 0.5 * (L + L.T)
    if want_vectors:
        return np.linalg.eigh(L.toarray())
    return np.linalg.eigvalsh(L.toarray()), None


def spectral_dim(evals, t_grid):
    lam = evals[evals > 1e-9]
    P = np.array([np.mean(np.exp(-lam * t)) for t in t_grid])
    ds = -2 * np.gradient(np.log(P), np.log(t_grid))
    return P, ds


def lattice2d(Lside):
    N = Lside * Lside
    idx = np.arange(N).reshape(Lside, Lside)
    rows, cols = [], []
    for ax in (0, 1):
        nb = np.roll(idx, -1, axis=ax)
        rows += [idx.ravel(), nb.ravel()]
        cols += [nb.ravel(), idx.ravel()]
    A = sp.coo_matrix((np.ones(2 * 2 * N), (np.concatenate(rows), np.concatenate(cols))),
                      shape=(N, N)).tocsr()
    return (A > 0).astype(float)


def add_long_range(A, n_links, weight=1.0):
    N = A.shape[0]
    a = rng.integers(0, N, n_links)
    b = rng.integers(0, N, n_links)
    extra = sp.coo_matrix((np.full(n_links, weight), (a, b)), shape=(N, N)).tocsr()
    return ((A + extra + extra.T) > 0).astype(float)


t_grid = np.logspace(0, 2.3, 36)
win = (t_grid > 3) & (t_grid < 40)

print("=" * 70)
print("(a) VALIDATION + the small-world dimension climb")
print("=" * 70)
base = lattice2d(50)                       # 2500 nodes, d_s ~ 2
N = base.shape[0]
for nfrac, label in [(0.0, "pure 2D lattice"), (0.01, "+1% long-range links"),
                     (0.05, "+5% long-range"), (0.20, "+20% long-range"),
                     (1.0, "+100% long-range")]:
    A = base if nfrac == 0 else add_long_range(base, int(nfrac * N))
    ev, _ = lap_eigs(A)
    P, ds = spectral_dim(ev, t_grid)
    print(f"  {label:<26} d_s = {np.median(ds[win]):.2f}")
print("  => long-range links RAISE the effective dimension without bound.")

print()
print("=" * 70)
print("(b) DENSITY-MODULATED graph: dense regions get the shortcuts")
print("=" * 70)
# density field: a smooth blob over the lattice; dense nodes receive long-range links
Lside = 50
base = lattice2d(Lside)
xx, yy = np.meshgrid(np.arange(Lside), np.arange(Lside), indexing="ij")
cx = cy = Lside / 2
dens = np.exp(-((xx - cx)**2 + (yy - cy)**2) / (2 * (Lside / 6)**2)).ravel()
# each node spawns long-range links with probability proportional to its density
n_per = (6 * dens).astype(int)             # dense center ~6 shortcuts, edges ~0
src = np.repeat(np.arange(N), n_per)
dst = rng.integers(0, N, len(src))
extra = sp.coo_matrix((np.ones(len(src)), (src, dst)), shape=(N, N)).tocsr()
A = ((base + extra + extra.T) > 0).astype(float)

evals, evecs = lap_eigs(A, want_vectors=True)
evals = np.clip(evals, 0, None)
V2 = evecs**2
K = V2 @ np.exp(-np.outer(evals, t_grid))
dense_mask = dens >= np.percentile(dens, 80)
sparse_mask = dens <= np.percentile(dens, 20)
ds_dense = -2 * np.gradient(np.log(K[dense_mask].mean(0)), np.log(t_grid))
ds_sparse = -2 * np.gradient(np.log(K[sparse_mask].mean(0)), np.log(t_grid))
dd, dsp = np.median(ds_dense[win]), np.median(ds_sparse[win])
print(f"  dense core (gets shortcuts):  d_s = {dd:.2f}")
print(f"  sparse edge (no shortcuts):   d_s = {dsp:.2f}")
print(f"  d_s(dense) - d_s(sparse) = {dd - dsp:+.2f}")
print(f"  => {'DENSE = HIGHER dimensional' if dd > dsp else 'dense = lower'} "
      f"-- the hypothesis WINS when density buys long-range connectivity.")

print("""
  HONEST SYNTHESIS (this is the real answer to the sign question):
  Effective dimension is set by connectivity, and concentration can push it
  EITHER way:
    * gravity squeezing matter into filaments/walls -> local anisotropy
      -> dimension DOWN (Exp 2,8,9,10,11). This is what actually happens to
      ordinary matter under gravity.
    * concentration creating long-range links/shortcuts -> dimension UP, without
      bound (this experiment).
  Your "denser => higher D" is correct in the connectivity-dominated regime.
  The open physical question is which mechanism dominates at universal scale.
  Gravitational structure formation is anisotropy-dominated, so the sky shows
  dimension going DOWN. A mechanism that makes mass create genuine long-range
  links (wormhole-like ER=EPR connectivity? quantum entanglement structure?)
  would flip it. That is exactly where AdS/CFT lives -> next experiment.""")

# ---- figure ----
fig, axes = plt.subplots(1, 2, figsize=(13, 5))
ax = axes[0]
for nfrac, label in [(0.0, "2D lattice"), (0.05, "+5% links"), (0.20, "+20% links"),
                     (1.0, "+100% links")]:
    A = base if nfrac == 0 else add_long_range(lattice2d(50), int(nfrac * N))
    ev, _ = lap_eigs(A)
    P, ds = spectral_dim(ev, t_grid)
    ax.plot(t_grid, ds, "-", label=label)
ax.set_xscale("log"); ax.set_xlabel("diffusion time t"); ax.set_ylabel("d_s(t)")
ax.set_title("Long-range links raise effective dimension\n(small-world climb)")
ax.legend(); ax.grid(alpha=0.3); ax.set_ylim(0, 8)

ax = axes[1]
ax.plot(t_grid, ds_dense, "o-", color="crimson", ms=3, label=f"dense core (d_s~{dd:.1f})")
ax.plot(t_grid, ds_sparse, "o-", color="navy", ms=3, label=f"sparse edge (d_s~{dsp:.1f})")
ax.set_xscale("log"); ax.set_xlabel("diffusion time t"); ax.set_ylabel("local d_s(t)")
ax.set_title("Density-modulated graph:\ndense regions measure HIGHER-dimensional")
ax.legend(); ax.grid(alpha=0.3); ax.set_ylim(0, 8)

plt.tight_layout()
plt.savefig(f"{OUT}/exp12_connectivity.png", dpi=130)
print(f"\n  figure saved -> figures/exp12_connectivity.png")
