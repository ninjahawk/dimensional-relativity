"""
Experiment 17 -- The crux, as an honest order-of-magnitude estimate:
can entanglement connectivity (which RAISES dimension, e12/e13) ever beat
geometric anisotropy (which LOWERS it, e02/e08/e15) at large scale?

THIS IS AN ESTIMATE, NOT A MEASUREMENT. It maps a 1-D free-fermion toy onto a
cosmological question; treat the conclusion as a scaling argument with large
uncertainty, not a number. What makes it more than hand-waving: the input (how
mutual information decays with separation) is computed exactly and VALIDATED
against the known result I(r) ~ 1/r^2 for a critical chain.

The logic:
  - e12 showed you need a long-range "link fraction" f ~ 0.1 (links at separation
    d carrying ~10% of the local link strength) to raise the spectral dimension
    appreciably.
  - entanglement supplies links of strength = mutual information I(d). So the
    dimension-raising power at separation d is  f(d) = I(d) / I(local).
  - geometric anisotropy is an order-1, MEASURED effect (e15: dense regions sit at
    D~2.3-2.7, a deficit of ~0.5-0.7 from 3).
  - so: at what separation does entanglement still provide f >~ 0.1? If that
    separation is tiny (a few lattice steps), entanglement is too short-range to
    raise the dimension at large scale, and geometry wins everywhere except where
    entanglement SATURATES its holographic bound (horizons, black holes, the very
    early universe).
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = "../figures"


def correlation_matrix(N, gap=0.0):
    H = np.zeros((N, N))
    for i in range(N):
        H[i, (i + 1) % N] = H[(i + 1) % N, i] = -1.0
    if gap > 0:
        H[np.diag_indices(N)] = gap * (-1.0) ** np.arange(N)
    e, V = np.linalg.eigh(H)
    occ = V[:, :N // 2]
    return (occ @ occ.conj().T).real


def s_of_nu(nu):
    nu = np.clip(nu, 1e-12, 1 - 1e-12)
    return float(-np.sum(nu * np.log(nu) + (1 - nu) * np.log(1 - nu)))


def two_site_S(C, i, j):
    return s_of_nu(np.linalg.eigvalsh(C[np.ix_([i, j], [i, j])]))


def mutual_info_vs_r(C, rs, n_avg=120):
    N = len(C)
    Si = np.array([s_of_nu(np.array([C[i, i]])) for i in range(N)])
    I = []
    for r in rs:
        starts = np.linspace(0, N - r - 1, n_avg).astype(int)
        vals = [Si[i] + Si[i + r] - two_site_S(C, i, i + r) for i in starts]
        I.append(max(np.mean(vals), 1e-30))
    return np.array(I)


N = 400
# half-filled chain: C(r)=sin(pi r/2)/(pi r) vanishes at EVEN r and ~1/r at odd r,
# so the mutual information I(r)~C(r)^2 only lives on odd separations. Use odd r
# (otherwise mixing in the structural zeros corrupts the power-law fit).
_base = np.floor(np.logspace(0, np.log10(N // 6), 24)).astype(int)
rs = np.unique(2 * _base + 1)
C_crit = correlation_matrix(N, gap=0.0)
C_gap = correlation_matrix(N, gap=0.6)
I_crit = mutual_info_vs_r(C_crit, rs)
I_gap = mutual_info_vs_r(C_gap, rs)

print("=" * 70)
print("VALIDATION: critical free-fermion mutual information must decay as 1/r^2")
print("=" * 70)
mask = (rs >= 2) & (rs <= N // 5)
slope = np.polyfit(np.log(rs[mask]), np.log(I_crit[mask]), 1)[0]
print(f"  critical chain: I(r) ~ r^{slope:.2f}   (known result: r^-2.0)")
ok = abs(slope + 2) < 0.4
print(f"  validation: {'PASS' if ok else 'CHECK'}  (power-law, as required)")
# gapped correlation length
lg = np.log(I_gap[mask])
xi = -1.0 / np.polyfit(rs[mask], lg, 1)[0]
print(f"  gapped chain:   I(r) ~ exp(-r/xi), xi = {xi:.1f} sites (short-range)")

print()
print("=" * 70)
print("THE CRUX: where is entanglement still ~10% of the local link strength?")
print("=" * 70)
f_crit = I_crit / I_crit[0]
f_gap = I_gap / I_gap[0]
THR = 0.1


def crossing(rs, f, thr):
    below = np.where(f < thr)[0]
    return rs[below[0]] if len(below) else np.inf


r_crit = crossing(rs, f_crit, THR)
r_gap = crossing(rs, f_gap, THR)
print(f"  critical: entanglement link fraction drops below {THR} at r ~ {r_crit} sites")
print(f"  gapped:   ... at r ~ {r_gap} sites")
print(f"""
  So even for a CRITICAL (maximally long-range ordinary) system, the entanglement
  that could raise the dimension is gone (< 10% of local) within ~{r_crit} lattice
  steps. As a power law I(r)~1/r^2, reaching cosmological separations d/R ~ 1e60
  (horizon / Planck) leaves f ~ 1e-120 -- utterly negligible. Geometric anisotropy
  is an order-1 measured effect (e15) at ALL scales. So:

  ESTIMATE / CONCLUSION: for ordinary matter, geometry wins by ~100+ orders of
  magnitude. Entanglement connectivity can only raise the effective dimension
  where it SATURATES its holographic bound -- i.e. at horizons, black holes, and
  the Planck-density early universe (exactly the e05/e07 regime). The observable,
  classical universe is geometry-dominated, so its dimension goes DOWN where mass
  clumps. The 'denser => higher D' regime exists, but it is hidden at the horizon/
  Planck frontier, not in the cosmic web.

  UNCERTAINTIES (large, stated plainly): (1) a 1-D free-fermion chain is a toy;
  real cosmological entanglement involves gravity and is not computed here. (2)
  ER=EPR is a conjecture; whether entanglement = traversable geometric connection
  is unknown. (3) near saturation the perturbative scaling used here breaks down --
  that regime needs full quantum gravity. This is a scaling argument, not proof.""")

# ---- figure ----
fig, axes = plt.subplots(1, 2, figsize=(13, 5))
ax = axes[0]
ax.loglog(rs, I_crit, "o-", color="crimson", label=f"critical  (I~r^{slope:.2f})")
ax.loglog(rs, I_gap, "s-", color="navy", label=f"gapped (xi={xi:.0f})")
ax.loglog(rs, I_crit[0] * (rs / rs[0])**-2.0, "--", color="gray", label="1/r^2 (theory)")
ax.set_xlabel("separation r (sites)"); ax.set_ylabel("mutual information I(r)")
ax.set_title("Entanglement decays fast with separation\n(validated against 1/r^2)")
ax.legend(); ax.grid(alpha=0.3, which="both")

ax = axes[1]
ax.semilogy(rs, f_crit, "o-", color="crimson", label="critical")
ax.semilogy(rs, f_gap, "s-", color="navy", label="gapped")
ax.axhline(THR, ls="--", color="green", label=f"dimension-raising threshold ~{THR}")
ax.set_xlabel("separation r (sites)")
ax.set_ylabel("link fraction f(r) = I(r)/I(local)")
ax.set_title("Where can entanglement still raise dimension?\n(only at tiny separation)")
ax.legend(); ax.grid(alpha=0.3)

plt.tight_layout()
plt.savefig(f"{OUT}/exp17_crux.png", dpi=130)
print(f"\n  figure saved -> figures/exp17_crux.png")
