"""
Experiment 10 -- Local spectral dimension: does DIFFUSION feel a different
dimension inside dense regions than in voids?

Exp 3 measured one global spectral dimension. Exp 8 showed the GEOMETRIC
dimension of dense regions is morphology-driven and non-monotonic. Here we ask
the DYNAMICAL question separately: seed a random walker inside a dense knot vs in
a void, and measure the return probability  P(t) ~ t^(-d_s/2)  for each
population. d_s is "the dimension the physics of propagation sees."

Method: build the kNN graph of the web, take the symmetric normalized Laplacian
L = I - D^{-1/2} A D^{-1/2}, diagonalize it, and use the heat-kernel diagonal
    K_ii(t) = sum_k exp(-lambda_k t) psi_k(i)^2   (return prob. for node i)
averaged over dense nodes vs void nodes. Then d_s(t) = -2 d ln K / d ln t.
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.spatial import cKDTree
import scipy.sparse as sp
from exp2_cosmicweb import zeldovich_web
from dimension_tools import local_count

rng = np.random.default_rng(10)
OUT = "../figures"


def knn_adjacency(points, k=10, boxsize=None):
    tree = cKDTree(points, boxsize=boxsize)
    _, nbr = tree.query(points, k=k + 1)
    N = len(points)
    rows = np.repeat(np.arange(N), k)
    cols = nbr[:, 1:].ravel()
    A = sp.coo_matrix((np.ones(len(rows)), (rows, cols)), shape=(N, N)).tocsr()
    return ((A + A.T) > 0).astype(float)


print("Building cosmic web and its diffusion operator...")
pts, L = zeldovich_web(N=48, L=1.0, n_index=-2.4, growth=3.2, seed=4)
box = [L, L, L]
dens_full = local_count(pts, 0.045 * L, boxsize=box)

# subsample for a full (eigenvector) diagonalization
nsub = 4000
sub = rng.choice(len(pts), nsub, replace=False)
P = pts[sub]
dens = dens_full[sub]
A = knn_adjacency(P, k=10, boxsize=box)

deg = np.asarray(A.sum(1)).ravel()
dinv = 1.0 / np.sqrt(np.clip(deg, 1e-9, None))
Lap = sp.identity(nsub) - sp.diags(dinv) @ A @ sp.diags(dinv)
Lap = 0.5 * (Lap + Lap.T)
print("  diagonalizing %d x %d Laplacian..." % (nsub, nsub))
evals, evecs = np.linalg.eigh(Lap.toarray())
evals = np.clip(evals, 0, None)

# heat-kernel diagonal per node: K_ii(t) = sum_k exp(-lam_k t) evec[i,k]^2
t_grid = np.logspace(0, 2.3, 36)
V2 = evecs**2                                   # (N, N)
# K[node, t] = V2 @ exp(-lam outer t)
expmat = np.exp(-np.outer(evals, t_grid))       # (N_modes, n_t)
K = V2 @ expmat                                 # (N_nodes, n_t)

dense_mask = dens >= np.percentile(dens, 75)
void_mask = dens <= np.percentile(dens, 25)
K_dense = K[dense_mask].mean(0)
K_void = K[void_mask].mean(0)
ds_dense = -2 * np.gradient(np.log(K_dense), np.log(t_grid))
ds_void = -2 * np.gradient(np.log(K_void), np.log(t_grid))

win = (t_grid > 3) & (t_grid < 40)
print("\n  Spectral (diffusion) dimension by environment:")
print(f"    dense regions (top 25% density):  d_s = {np.median(ds_dense[win]):.2f}")
print(f"    voids        (bottom 25% density): d_s = {np.median(ds_void[win]):.2f}")
print(f"    mean node degree dense/void = "
      f"{deg[dense_mask].mean():.1f} / {deg[void_mask].mean():.1f}")
diff = np.median(ds_dense[win]) - np.median(ds_void[win])
print(f"\n    d_s(dense) - d_s(void) = {diff:+.2f}")
if diff < -0.1:
    print("    => diffusion sees dense regions as LOWER-dimensional.")
elif diff > 0.1:
    print("    => diffusion sees dense regions as HIGHER-dimensional.")
else:
    print("    => no strong split in the dynamical dimension.")
print("""
  Note: the spectral (dynamical) dimension and the geometric dimension (Exp 8)
  need not agree -- that mismatch is itself physics. On fractals d_s < d_geom
  generically (Alexander-Orbach). Here we compare environments head to head.""")

# ---- figure ----
fig, axes = plt.subplots(1, 2, figsize=(13, 5))
ax = axes[0]
ax.plot(t_grid, ds_dense, "o-", color="crimson", ms=3, label="dense (top 25%)")
ax.plot(t_grid, ds_void, "o-", color="navy", ms=3, label="voids (bottom 25%)")
ax.set_xscale("log"); ax.set_ylim(0, 4)
ax.set_xlabel("diffusion time t (~ scale^2)")
ax.set_ylabel("local spectral dimension d_s(t)")
ax.set_title("Does diffusion feel dimension differently\nin dense vs empty space?")
ax.legend(); ax.grid(alpha=0.3)

ax = axes[1]
ax.plot(t_grid, K_dense, "o-", color="crimson", ms=3, label="dense")
ax.plot(t_grid, K_void, "o-", color="navy", ms=3, label="void")
ax.set_xscale("log"); ax.set_yscale("log")
ax.set_xlabel("diffusion time t"); ax.set_ylabel("return probability K(t)")
ax.set_title("Return probability by environment"); ax.legend(); ax.grid(alpha=0.3)

plt.tight_layout()
plt.savefig(f"{OUT}/exp10_local_spectral.png", dpi=130)
print(f"\n  figure saved -> figures/exp10_local_spectral.png")
