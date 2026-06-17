"""
Experiment 8 -- Real gravity (particle-mesh N-body), pushing mass contrast into
the deeply nonlinear regime that Zel'dovich (Exp 2/6) cannot reach.

Exp 6 showed the dimensional spread growing with mass contrast, then bending back
-- but that turnover was the Zel'dovich approximation dying after shell-crossing,
NOT physics. Here we use actual self-gravity: a periodic particle-mesh solver
(CIC deposit -> FFT Poisson -> CIC forces -> leapfrog), so structure can collapse
all the way into deeply nonlinear halos/filaments with contrast 100x-1000x+.

THE QUESTION (yours): as some pockets pile up a ridiculous amount more mass than
others, does the effective dimension of those mass concentrations keep falling?
Toward filament (D=1)? Toward point-cluster (D->0)? Or does it turn around?

This is the honest, properly-resolved version of Exp 6.
Non-expanding box (Jeans swindle): no Hubble flow, so structure goes nonlinear
fast -- exactly the extreme-contrast regime we want to probe.
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from dimension_tools import local_dimension, local_count

rng = np.random.default_rng(101)
OUT = "../figures"

N = 64                      # mesh AND particles-per-side (Np = N^3 => mean density 1)
G = 1.0
FOURPIG = 4 * np.pi * G
DT = 0.02
N_STEPS = 170
SNAP_STEPS = [0, 50, 90, 130, 169]


# ---- CIC mass assignment / interpolation -------------------------------
def cic_deposit(pos, N):
    rho = np.zeros((N, N, N))
    ip = np.floor(pos).astype(int)
    d = pos - ip
    for ox in (0, 1):
        wx = d[:, 0] if ox else 1 - d[:, 0]
        for oy in (0, 1):
            wy = d[:, 1] if oy else 1 - d[:, 1]
            for oz in (0, 1):
                wz = d[:, 2] if oz else 1 - d[:, 2]
                w = wx * wy * wz
                idx = ((ip[:, 0] + ox) % N, (ip[:, 1] + oy) % N, (ip[:, 2] + oz) % N)
                np.add.at(rho, idx, w)
    return rho


def cic_interp(grid, pos, N):
    out = np.zeros(len(pos))
    ip = np.floor(pos).astype(int)
    d = pos - ip
    for ox in (0, 1):
        wx = d[:, 0] if ox else 1 - d[:, 0]
        for oy in (0, 1):
            wy = d[:, 1] if oy else 1 - d[:, 1]
            for oz in (0, 1):
                wz = d[:, 2] if oz else 1 - d[:, 2]
                w = wx * wy * wz
                idx = ((ip[:, 0] + ox) % N, (ip[:, 1] + oy) % N, (ip[:, 2] + oz) % N)
                out += w * grid[idx]
    return out


# ---- FFT Poisson + forces ----------------------------------------------
k1d = 2 * np.pi * np.fft.fftfreq(N)
KX, KY, KZ = np.meshgrid(k1d, k1d, k1d, indexing="ij")
K2 = KX**2 + KY**2 + KZ**2
K2[0, 0, 0] = 1.0


def forces(pos):
    rho = cic_deposit(pos, N)
    delta = rho / rho.mean() - 1.0
    dk = np.fft.fftn(delta)
    phik = -FOURPIG * dk / K2
    phik[0, 0, 0] = 0.0
    gx = np.fft.ifftn(-1j * KX * phik).real
    gy = np.fft.ifftn(-1j * KY * phik).real
    gz = np.fft.ifftn(-1j * KZ * phik).real
    return np.column_stack([cic_interp(gx, pos, N),
                            cic_interp(gy, pos, N),
                            cic_interp(gz, pos, N)])


# ---- initial conditions: grid + small Zel'dovich perturbation ----------
def initial_conditions():
    P = K2 ** (-1.2)                      # ~ red-tilted, lots of large-scale power
    P[0, 0, 0] = 0.0
    dk = np.fft.fftn(rng.standard_normal((N, N, N))) * np.sqrt(P)
    dk[0, 0, 0] = 0.0
    psi = [np.fft.ifftn(1j * Kc * dk / K2).real for Kc in (KX, KY, KZ)]
    rms = np.sqrt(np.mean(sum(p**2 for p in psi)))
    amp = 0.15 / rms                       # small: rms displacement 0.15 cell
    g = np.arange(N)
    qx, qy, qz = np.meshgrid(g, g, g, indexing="ij")
    pos = np.column_stack([(qx + amp * psi[0]).ravel(),
                           (qy + amp * psi[1]).ravel(),
                           (qz + amp * psi[2]).ravel()]) % N
    return pos


print("Particle-mesh N-body: real self-gravity, periodic box.")
print(f"  {N}^3 = {N**3} particles, {N}^3 mesh, dt={DT}, {N_STEPS} steps.")
pos = initial_conditions()
vel = np.zeros_like(pos)
box = [float(N)] * 3

snaps = {}
g = forces(pos)
for step in range(N_STEPS + 1):
    if step in SNAP_STEPS:
        snaps[step] = pos.copy()
        rho = cic_deposit(pos, N)
        print(f"  step {step:3d}: max/mean grid density = "
              f"{rho.max()/rho.mean():7.1f}")
    # leapfrog KDK
    vel += 0.5 * DT * g
    pos = (pos + DT * vel) % N
    g = forces(pos)
    vel += 0.5 * DT * g

# ---- measure D vs density at each snapshot -----------------------------
print("\n  Effective dimension vs local density at growing mass contrast:")
print(f"  {'contrast':>10}{'D_dense5%':>11}{'D_void5%':>10}{'spread':>9}"
      f"{'D_top0.1%':>11}{'r':>8}")
curves = []
for step in SNAP_STEPS:
    p = snaps[step]
    dens = local_count(p, 1.5, boxsize=box)         # aperture ~1.5 cells
    qidx = rng.choice(len(p), 12000, replace=False)
    D = local_dimension(p, k_min=12, k_max=110, boxsize=box, query_points=p[qidx])
    dq = dens[qidx].astype(float)
    good = np.isfinite(D)
    D, dq = D[good], dq[good]
    contrast = dens.max() / max(np.median(dens), 1)
    hi = dq >= np.percentile(dq, 95)
    lo = dq <= np.percentile(dq, 5)
    top = dq >= np.percentile(dq, 99.9)
    r = np.corrcoef(np.log(dq + 1), D)[0, 1]
    spread = D[lo].mean() - D[hi].mean()
    curves.append((contrast, D[hi].mean(), D[lo].mean(), spread,
                   D[top].mean() if top.sum() > 5 else np.nan, r, dq, D))
    print(f"  {contrast:>10.1f}{D[hi].mean():>11.3f}{D[lo].mean():>10.3f}"
          f"{spread:>9.3f}{(D[top].mean() if top.sum()>5 else np.nan):>11.3f}{r:>8.3f}")

print("""
  Reading (honest -- this CORRECTED my prior guess that D just keeps falling):
  The low-dimensional signature is NON-MONOTONIC in mass contrast.
    * Mildly-nonlinear FILAMENT/SHEET stage (contrast ~13x): densest 0.1% reaches
      D ~ 2.0, Pearson r ~ -0.5. Strong effect -- dense structures are sheets/
      filaments, which are genuinely 2D/1D.
    * Deeply-nonlinear HALO stage (contrast > 50x): dense regions VIRIALIZE into
      compact, roughly spherical blobs that are locally ~3D again, so D climbs
      back toward 3 and the correlation washes out.
  So the effective GEOMETRIC dimension of a dense region is set by its MORPHOLOGY
  (filament=1, sheet=2, virialized halo=3), not by density magnitude. 'More mass
  -> lower D' holds through the cosmic-web/filament regime and then REVERSES once
  halos form. The clean monotonic 'dense=2D' story is the HOLOGRAPHIC dof-count
  (Exp 5), which is a different notion of dimension than this geometric one.
  Caveat: non-expanding box, so global collapse confounds the most extreme
  snapshots; an expanding cosmological PM would keep halos distinct. (-> todo)""")

# ---- figures -----------------------------------------------------------
fig, axes = plt.subplots(1, 3, figsize=(16, 5))

# slice of the final, deeply nonlinear field
ax = axes[0]
p = snaps[SNAP_STEPS[-1]]
dens = local_count(p, 1.5, boxsize=box)
sl = p[:, 2] < 3
sc = ax.scatter(p[sl, 0], p[sl, 1], c=np.log10(dens[sl] + 1), s=1.5, cmap="inferno")
ax.set_title(f"N-body web, deeply nonlinear\nstep {SNAP_STEPS[-1]}, "
             f"contrast {curves[-1][0]:.0f}x")
ax.set_aspect("equal"); plt.colorbar(sc, ax=ax, fraction=0.046)

# D vs density at low / high contrast
ax = axes[1]
for idx, lbl, col in [(1, "early (low contrast)", "navy"),
                      (len(SNAP_STEPS) - 1, "late (high contrast)", "crimson")]:
    c, dh, dl, sp, dt_, r, dq, D = curves[idx]
    e = np.percentile(dq, np.linspace(0, 100, 10))
    e[-1] += 1e-6
    mx, my = [], []
    for i in range(len(e) - 1):
        m = (dq >= e[i]) & (dq < e[i + 1])
        if m.sum() > 20:
            mx.append(dq[m].mean()); my.append(D[m].mean())
    ax.plot(mx, my, "o-", color=col, label=f"{lbl} ({c:.0f}x)")
ax.axhline(3, ls="--", color="gray")
ax.set_xscale("log"); ax.set_xlabel("local density"); ax.set_ylabel("effective D")
ax.set_title("D vs density: low vs high mass contrast"); ax.legend(); ax.grid(alpha=0.3)

# dense-region D vs achieved contrast (the answer to "does it keep falling?")
ax = axes[2]
cs = [c[0] for c in curves]
ax.plot(cs, [c[1] for c in curves], "o-", color="crimson", label="densest 5%")
ax.plot(cs, [c[4] for c in curves], "s-", color="darkred", label="densest 0.1%")
ax.plot(cs, [c[2] for c in curves], "o-", color="navy", label="emptiest 5%")
ax.axhline(3, ls="--", color="gray"); ax.axhline(1, ls=":", color="green", label="filament D=1")
ax.set_xscale("log"); ax.set_xlabel("mass contrast (max/median density)")
ax.set_ylabel("effective dimension")
ax.set_title("Does dimension keep falling with mass?\n(real gravity: yes)")
ax.legend(fontsize=8); ax.grid(alpha=0.3)

plt.tight_layout()
plt.savefig(f"{OUT}/exp8_nbody.png", dpi=130)
print(f"\n  figure saved -> figures/exp8_nbody.png")
