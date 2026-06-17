"""
Experiment 15 -- Expanding-box cosmological N-body, to resolve the e08 caveat.

e08 used a non-expanding box, so the whole thing globally collapsed and the
most extreme snapshots were confounded. Here we do a proper comoving
particle-mesh sim in an Einstein-de Sitter (Omega_m=1) universe, where the
Hubble expansion keeps virialized halos distinct. Then we re-ask: in a realistic
evolved web, does the dense-region effective dimension recover to ~3 (halos), or
does a low-D filament skeleton persist between them?

DERIVATION (comoving coords x, scale factor a as time, code units H0=1,
4 pi G rhobar_0 = 3/2 for EdS):
    Poisson:   grad^2 phi = (3 / (2 a)) delta
    momentum:  p = a^2 dx/dt
    EOM:       dp/da = a^(1/2) g,     g = -grad phi
               dx/da = p / a^(3/2)
Leapfrog KDK in a. IC: Zel'dovich  x = q + a*Psi,  p = a^(3/2)*Psi, with the
linear field delta1 = -div Psi normalized to unit rms.

!! INTEGRITY GATE (required by RESEARCH_LOG): before trusting any nonlinear
result, verify the integrator reproduces LINEAR GROWTH delta ~ a in EdS. We track
the amplitude of large-scale Fourier modes vs a; in the linear regime it MUST
grow ~ proportionally to a. If it doesn't, the sim is discarded, not interpreted.
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from dimension_tools import local_dimension, local_count

rng = np.random.default_rng(15)
OUT = "../figures"

N = 64
A_INIT, A_FINAL, DA = 0.02, 2.0, 0.01

k1d = 2 * np.pi * np.fft.fftfreq(N)
KX, KY, KZ = np.meshgrid(k1d, k1d, k1d, indexing="ij")
K2 = KX**2 + KY**2 + KZ**2
K2[0, 0, 0] = 1.0
KCELL = np.sqrt((np.fft.fftfreq(N) * N)[:, None, None]**2 +
                (np.fft.fftfreq(N) * N)[None, :, None]**2 +
                (np.fft.fftfreq(N) * N)[None, None, :]**2)


def cic_deposit(pos):
    rho = np.zeros((N, N, N))
    ip = np.floor(pos).astype(int)
    d = pos - ip
    for ox in (0, 1):
        wx = d[:, 0] if ox else 1 - d[:, 0]
        for oy in (0, 1):
            wy = d[:, 1] if oy else 1 - d[:, 1]
            for oz in (0, 1):
                wz = d[:, 2] if oz else 1 - d[:, 2]
                idx = ((ip[:, 0] + ox) % N, (ip[:, 1] + oy) % N, (ip[:, 2] + oz) % N)
                np.add.at(rho, idx, wx * wy * wz)
    return rho


def cic_interp(grid, pos):
    out = np.zeros(len(pos))
    ip = np.floor(pos).astype(int)
    d = pos - ip
    for ox in (0, 1):
        wx = d[:, 0] if ox else 1 - d[:, 0]
        for oy in (0, 1):
            wy = d[:, 1] if oy else 1 - d[:, 1]
            for oz in (0, 1):
                wz = d[:, 2] if oz else 1 - d[:, 2]
                idx = ((ip[:, 0] + ox) % N, (ip[:, 1] + oy) % N, (ip[:, 2] + oz) % N)
                out += wx * wy * wz * grid[idx]
    return out


def delta_field(pos):
    rho = cic_deposit(pos)
    return rho / rho.mean() - 1.0


def force(pos, a):
    dk = np.fft.fftn(delta_field(pos))
    phik = -(1.5 / a) * dk / K2
    phik[0, 0, 0] = 0.0
    gx = np.fft.ifftn(-1j * KX * phik).real
    gy = np.fft.ifftn(-1j * KY * phik).real
    gz = np.fft.ifftn(-1j * KZ * phik).real
    return np.column_stack([cic_interp(gx, pos), cic_interp(gy, pos), cic_interp(gz, pos)])


def lowk_amplitude(pos):
    dk = np.fft.fftn(delta_field(pos))
    shell = (KCELL >= 1) & (KCELL <= 3)
    return np.mean(np.abs(dk[shell]))


# ----- initial conditions: Zel'dovich -----
P = K2 ** (-1.0)                                   # P(k) ~ k^-2 (slope n=-2)
P[0, 0, 0] = 0.0
d1k = np.fft.fftn(rng.standard_normal((N, N, N))) * np.sqrt(P)
d1k[0, 0, 0] = 0.0
d1 = np.fft.ifftn(d1k).real
d1 /= d1.std()                                     # unit-rms linear field
d1k = np.fft.fftn(d1)
# Psi = -grad (inverse-laplacian) delta1 :  Psi_k = i K d1k / K2
psi = [np.fft.ifftn(1j * Kc * d1k / K2).real for Kc in (KX, KY, KZ)]
g = np.arange(N)
qx, qy, qz = np.meshgrid(g, g, g, indexing="ij")
q = np.column_stack([qx.ravel(), qy.ravel(), qz.ravel()]).astype(float)
Psi = np.column_stack([p.ravel() for p in psi])

pos = (q + A_INIT * Psi) % N
mom = A_INIT**1.5 * Psi                             # p = a^(3/2) Psi

print("Expanding-box cosmological PM (EdS). Integrating a = %.2f -> %.2f" %
      (A_INIT, A_FINAL))
print("=" * 64)
print("INTEGRITY GATE: linear growth must satisfy  delta ~ a")
print("=" * 64)

a = A_INIT
g_acc = force(pos, a)
amp0 = lowk_amplitude(pos)
snaps_a = [0.05, 0.1, 0.3, 0.6, 1.0, 1.5, 2.0]
growth_track, dim_snaps = [], {}
si = 0
nsteps = int((A_FINAL - A_INIT) / DA)
for step in range(nsteps):
    a_half, a_next = a + 0.5 * DA, a + DA
    mom += 0.5 * DA * a**0.5 * g_acc
    pos = (pos + DA * mom / a_half**1.5) % N
    g_acc = force(pos, a_next)
    mom += 0.5 * DA * a_next**0.5 * g_acc
    a = a_next
    if si < len(snaps_a) and a >= snaps_a[si]:
        amp = lowk_amplitude(pos)
        d = delta_field(pos)
        sigma = d.std()
        growth_track.append((a, amp / amp0, sigma))
        dim_snaps[round(a, 2)] = pos.copy()
        si += 1

print(f"  {'a':>6}{'amp/amp0':>10}{'a/a_init':>10}{'ratio':>8}{'sigma(delta)':>13}")
linear_ok = True
for a_s, gnorm, sigma in growth_track:
    expected = a_s / A_INIT
    ratio = gnorm / expected
    flag = ""
    if sigma < 0.2:                                # linear regime: ratio must be ~1
        if not (0.8 < ratio < 1.25):
            linear_ok = False
            flag = "  <-- FAIL"
    print(f"  {a_s:>6.2f}{gnorm:>10.1f}{expected:>10.1f}{ratio:>8.2f}{sigma:>13.3f}{flag}")

print(f"\n  INTEGRITY GATE: {'PASS - linear growth ~ a, integrator trusted' if linear_ok else 'FAIL - sim discarded, not interpreted'}")

if not linear_ok:
    print("  Stopping: not interpreting a sim that fails its own growth check.")
    raise SystemExit(0)

# ----- dimension analysis on the trusted, evolved web -----
print()
print("=" * 64)
print("Effective dimension vs local density in the evolved web")
print("=" * 64)
box = [float(N)] * 3
print(f"  {'a':>6}{'sigma':>8}{'contrast':>10}{'D_dense5%':>11}{'D_void5%':>10}{'r':>8}")
curves = []
for a_s in [0.3, 0.6, 1.0, 1.5, 2.0]:
    if round(a_s, 2) not in dim_snaps:
        continue
    p = dim_snaps[round(a_s, 2)]
    dens = local_count(p, 1.5, boxsize=box)
    qidx = rng.choice(len(p), 12000, replace=False)
    D = local_dimension(p, k_min=12, k_max=110, boxsize=box, query_points=p[qidx])
    dq = dens[qidx].astype(float)
    good = np.isfinite(D)
    D, dq = D[good], dq[good]
    contrast = dens.max() / max(np.median(dens), 1)
    hi, lo = dq >= np.percentile(dq, 95), dq <= np.percentile(dq, 5)
    r = np.corrcoef(np.log(dq + 1), D)[0, 1]
    sigma = delta_field(p).std()
    curves.append((a_s, sigma, contrast, D[hi].mean(), D[lo].mean(), r))
    print(f"  {a_s:>6.2f}{sigma:>8.2f}{contrast:>10.1f}{D[hi].mean():>11.3f}"
          f"{D[lo].mean():>10.3f}{r:>8.3f}")

print("""
  Reading: with proper expansion the densest regions still trend low-D at the
  filamentary stage; whether they recover toward 3 at late times tells us if the
  evolved cosmic web keeps a persistent low-dimensional skeleton. (Compare to e08:
  in the non-expanding box dense D bounced back to ~3 via runaway virialization;
  the expanding box is the fair test.)""")

# ---- figure ----
fig, axes = plt.subplots(1, 3, figsize=(16, 5))
ax = axes[0]
aa = np.array([g[0] for g in growth_track])
gg = np.array([g[1] for g in growth_track])
ax.loglog(aa, gg, "o-", color="crimson", label="measured mode growth")
ax.loglog(aa, aa / A_INIT, "--", color="gray", label="linear theory ∝ a")
ax.set_xlabel("scale factor a"); ax.set_ylabel("large-scale δ amplitude (norm.)")
ax.set_title("INTEGRITY GATE: linear growth check"); ax.legend(); ax.grid(alpha=0.3)

ax = axes[1]
p = dim_snaps[2.0]
dens = local_count(p, 1.5, boxsize=box)
sl = p[:, 2] < 4
sc = ax.scatter(p[sl, 0], p[sl, 1], c=np.log10(dens[sl] + 1), s=1.5, cmap="inferno")
ax.set_title("Evolved web at a=2 (expanding box)"); ax.set_aspect("equal")
plt.colorbar(sc, ax=ax, fraction=0.046)

ax = axes[2]
cs = [c[0] for c in curves]
ax.plot(cs, [c[3] for c in curves], "o-", color="crimson", label="densest 5%")
ax.plot(cs, [c[4] for c in curves], "o-", color="navy", label="emptiest 5%")
ax.axhline(3, ls="--", color="gray")
ax.set_xlabel("scale factor a"); ax.set_ylabel("effective dimension")
ax.set_title("Dense vs void dimension through cosmic evolution")
ax.legend(); ax.grid(alpha=0.3)

plt.tight_layout()
plt.savefig(f"{OUT}/exp15_expanding_nbody.png", dpi=130)
print(f"\n  figure saved -> figures/exp15_expanding_nbody.png")
