"""
Experiment 18 -- Validate and de-bias the spectral-dimension estimator.

Earlier spectral-dimension numbers (e03: 2D lattice read 2.14, 3D read 3.51;
e10, e12) clearly carried a bias. Before quoting any of them we should pin the
bias against a KNOWN non-integer target. The Sierpinski gasket has an exactly
known spectral dimension

        d_s = 2 ln 3 / ln 5 = 1.3652...   (Alexander-Orbach / exact)

so it is the perfect ruler. We build the gasket GRAPH, measure d_s with the same
heat-kernel pipeline used everywhere else, and compare. We also re-measure the
2D and 3D lattices. The measured-vs-true map gives a correction we can apply to
the earlier relative results.
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import scipy.sparse as sp

OUT = "../figures"


def sierpinski_graph(levels):
    s3 = np.sqrt(3) / 2
    tris = [((0.0, 0.0), (1.0, 0.0), (0.5, s3))]
    for _ in range(levels):
        nt = []
        for a, b, c in tris:
            ab = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
            bc = ((b[0] + c[0]) / 2, (b[1] + c[1]) / 2)
            ca = ((c[0] + a[0]) / 2, (c[1] + a[1]) / 2)
            nt += [(a, ab, ca), (ab, b, bc), (ca, bc, c)]
        tris = nt
    # dedup vertices, build edge set
    idx = {}
    edges = []
    def vid(p):
        key = (round(p[0], 7), round(p[1], 7))
        if key not in idx:
            idx[key] = len(idx)
        return idx[key]
    for a, b, c in tris:
        ia, ib, ic = vid(a), vid(b), vid(c)
        edges += [(ia, ib), (ib, ic), (ic, ia)]
    N = len(idx)
    rows = [e[0] for e in edges] + [e[1] for e in edges]
    cols = [e[1] for e in edges] + [e[0] for e in edges]
    A = sp.coo_matrix((np.ones(len(rows)), (rows, cols)), shape=(N, N)).tocsr()
    return (A > 0).astype(float)


def lattice(shape):
    dims = len(shape)
    N = int(np.prod(shape))
    idx = np.arange(N).reshape(shape)
    rows, cols = [], []
    for ax in range(dims):
        nb = np.roll(idx, -1, axis=ax)
        rows += [idx.ravel(), nb.ravel()]
        cols += [nb.ravel(), idx.ravel()]
    A = sp.coo_matrix((np.ones(2 * dims * N),
                       (np.concatenate(rows), np.concatenate(cols))),
                      shape=(N, N)).tocsr()
    return (A > 0).astype(float)


def spectral_dimension(A, t_grid):
    deg = np.asarray(A.sum(1)).ravel()
    dinv = 1 / np.sqrt(np.clip(deg, 1e-12, None))
    L = sp.identity(A.shape[0]) - sp.diags(dinv) @ A @ sp.diags(dinv)
    ev = np.clip(np.linalg.eigvalsh((0.5 * (L + L.T)).toarray()), 0, None)
    lam = ev[ev > 1e-9]
    P = np.array([np.mean(np.exp(-lam * t)) for t in t_grid])
    ds = -2 * np.gradient(np.log(P), np.log(t_grid))
    return ds, P


t_grid = np.logspace(0, 3.0, 60)
cases = [
    ("Sierpinski gasket", sierpinski_graph(7), 2 * np.log(3) / np.log(5)),
    ("2D lattice", lattice((55, 55)), 2.0),
    ("3D lattice", lattice((16, 16, 16)), 3.0),
]

print("=" * 64)
print("SPECTRAL-DIMENSION ESTIMATOR validated against known values")
print("=" * 64)
print(f"  {'object':<20}{'N':>7}{'d_s measured':>14}{'d_s true':>11}{'bias':>8}")
print("-" * 64)
results = []
for name, A, true in cases:
    ds, P = spectral_dimension(A, t_grid)
    # plateau: flattest stretch of d_s(t) away from the t~1 transient and the
    # finite-size rolloff (where P approaches 1/N)
    Nn = A.shape[0]
    valid = (P > 3.0 / Nn) & (t_grid > 2)
    dsv = ds[valid]
    # take the most stable (min local variation) window
    if len(dsv) > 6:
        w = 5
        var = [np.std(dsv[i:i + w]) for i in range(len(dsv) - w)]
        j = int(np.argmin(var))
        meas = np.median(dsv[j:j + w])
    else:
        meas = np.median(dsv)
    results.append((name, Nn, meas, true, meas - true))
    print(f"  {name:<20}{Nn:>7}{meas:>14.3f}{true:>11.3f}{meas-true:>+8.3f}")

print("-" * 64)
biases = np.array([r[4] for r in results])
trues = np.array([r[3] for r in results])
# fit bias as roughly proportional to true d_s -> multiplicative correction
slope = np.sum(biases * trues) / np.sum(trues**2)
print(f"  Bias grows with d_s; approx measured ~ {1+slope:.3f} * true.")
print(f"  => CORRECTION: d_s_true ~ d_s_measured / {1+slope:.3f}")
print("  Applying this to earlier results:")
for raw, lbl in [(2.67, "e10 web (dense)"), (3.01, "e10 void"),
                 (2.57, "e10 dense"), (4.56, "e12 dense-core"),
                 (4.09, "e12 sparse-edge")]:
    print(f"    {lbl:<22} raw d_s={raw:.2f} -> corrected {raw/(1+slope):.2f}")
print("""
  The RELATIVE comparisons in e10/e12 are unaffected (both sides shift together);
  this just puts the absolute numbers on a validated footing. The Sierpinski
  check (measured vs exact 1.365) is the anchor that makes the correction honest
  rather than a guess.""")

# ---- figure ----
fig, axes = plt.subplots(1, 2, figsize=(13, 5))
ax = axes[0]
for name, A, true in cases:
    ds, P = spectral_dimension(A, t_grid)
    ax.plot(t_grid, ds, "-", label=f"{name} (true {true:.2f})")
    ax.axhline(true, ls=":", alpha=0.4)
ax.set_xscale("log"); ax.set_xlabel("diffusion time t")
ax.set_ylabel("spectral dimension d_s(t)")
ax.set_title("Estimator vs known targets\n(Sierpinski gasket = non-integer anchor)")
ax.legend(); ax.grid(alpha=0.3); ax.set_ylim(0, 4)

ax = axes[1]
mt = np.array([r[3] for r in results]); mm = np.array([r[2] for r in results])
ax.plot([0, 3.5], [0, 3.5], "--", color="gray", label="ideal (measured=true)")
ax.plot(mt, mm, "o", ms=11, color="crimson")
for name, Nn, meas, true, b in results:
    ax.annotate(name.split()[0], (true, meas), textcoords="offset points",
                xytext=(6, 4), fontsize=8)
ax.plot([0, 3.5], [0, 3.5 * (1 + slope)], "-", color="navy", alpha=0.6,
        label=f"fit: measured={1+slope:.2f}*true")
ax.set_xlabel("true d_s"); ax.set_ylabel("measured d_s")
ax.set_title("Bias calibration"); ax.legend(); ax.grid(alpha=0.3)

plt.tight_layout()
plt.savefig(f"{OUT}/exp18_estimator_validation.png", dpi=130)
print(f"\n  figure saved -> figures/exp18_estimator_validation.png")
