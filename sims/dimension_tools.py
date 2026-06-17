"""
dimension_tools.py
==================
Operational, assumption-light estimators of *effective dimension* for point
distributions and fields.

The whole project hinges on replacing the vague word "dimension" with something
you can actually MEASURE and that is allowed to (a) be non-integer and (b) vary
from place to place and scale to scale. We use three independent notions:

1. Correlation dimension  D2  (Grassberger-Procaccia, 1983)
       C(r) = (#pairs closer than r) ~ r^{D2}
       => D2 = d ln C / d ln r
   This is a GLOBAL geometric measure of how mass fills space.

2. Local scaling dimension  D_loc(x)
       Using the m-th nearest-neighbour distance d_m(x):  m ~ d_m^{D}
       => D_loc = d ln m / d ln d_m  (fit per point)
   This is dimension measured *at a point*, so it can vary in space.

3. Spectral dimension  d_s  (from diffusion / random walks)
       Return probability P(t) ~ t^{-d_s/2}
   This is how quantum-gravity programs define a *running* dimension.
   (Implemented in a separate module.)

Density is measured model-independently as a raw neighbour count inside a fixed
aperture r0 (no volume formula => no hidden assumption about dimension).

Author: research session for "dimensional relativity" hypothesis.
"""

from __future__ import annotations
import numpy as np
from scipy.spatial import cKDTree


# ---------------------------------------------------------------------------
# Density proxy (assumption-free: just a count, no volume => no dimension baked in)
# ---------------------------------------------------------------------------
def local_count(points: np.ndarray, r0: float, boxsize=None) -> np.ndarray:
    """Number of OTHER points within radius r0 of each point.

    This is our density proxy. We deliberately do NOT divide by a volume r0^D,
    because choosing D would presuppose the very thing we are trying to measure.
    Relative comparisons (which point sits in a denser neighbourhood) are all we
    need, and a raw count gives that cleanly.
    """
    tree = cKDTree(points, boxsize=boxsize)
    # count_neighbors of a tree against itself counts self-pairs => subtract 1
    counts = tree.query_ball_point(points, r0, return_length=True) - 1
    return counts.astype(float)


# ---------------------------------------------------------------------------
# Global correlation dimension
# ---------------------------------------------------------------------------
def correlation_dimension(points: np.ndarray,
                          r_min: float, r_max: float,
                          n_bins: int = 24, boxsize=None):
    """Grassberger-Procaccia correlation dimension over [r_min, r_max].

    Returns (D2, D2_err, radii, C, slope_curve) where slope_curve is the LOCAL
    logarithmic slope d ln C / d ln r at each radius (this reveals scale
    dependence -- the 'running' of dimension).
    """
    tree = cKDTree(points, boxsize=boxsize)
    radii = np.logspace(np.log10(r_min), np.log10(r_max), n_bins)
    # cumulative pair counts (includes N self-pairs at r>=0; subtract them)
    C = tree.count_neighbors(tree, radii).astype(float)
    N = len(points)
    C = (C - N) / 2.0                       # unordered pairs, excluding self
    C = C / (N * (N - 1) / 2.0)             # normalise to pair fraction

    logr, logC = np.log(radii), np.log(np.clip(C, 1e-30, None))
    # global slope via least squares over the whole window
    good = np.isfinite(logC) & (C > 0)
    A = np.vstack([logr[good], np.ones(good.sum())]).T
    slope, _ = np.linalg.lstsq(A, logC[good], rcond=None)[0]
    # local slope curve (central differences)
    slope_curve = np.gradient(logC, logr)
    # crude error = scatter of local slopes in the window
    D2_err = np.nanstd(slope_curve[good])
    return slope, D2_err, radii, C, slope_curve


# ---------------------------------------------------------------------------
# Local (per-point) scaling dimension via nearest-neighbour growth
# ---------------------------------------------------------------------------
def local_dimension(points: np.ndarray,
                    k_min: int = 8, k_max: int = 128,
                    boxsize=None, query_points: np.ndarray | None = None):
    """Per-point effective dimension from the law  m ~ d_m^{D_loc}.

    For each query point we take its sorted distances to neighbours number
    k_min..k_max and fit ln(m) vs ln(d_m); the slope is the local dimension.
    Using a RANGE of k (not r) makes the estimate adaptive to local density,
    which is exactly what we want when density varies wildly.
    """
    tree = cKDTree(points, boxsize=boxsize)
    q = points if query_points is None else query_points
    # +1 because the nearest neighbour of a point in its own set is itself (d=0)
    dists, _ = tree.query(q, k=k_max + 1)
    dists = dists[:, 1:]                     # drop self (distance 0)

    ms = np.arange(1, k_max + 1, dtype=float)
    log_m = np.log(ms[k_min - 1:k_max])
    D = np.full(len(q), np.nan)
    for i in range(len(q)):
        d = dists[i, k_min - 1:k_max]
        good = d > 0
        if good.sum() < 4:
            continue
        ld = np.log(d[good])
        lm = log_m[good]
        # slope of ln m vs ln d  => dimension
        A = np.vstack([ld, np.ones(good.sum())]).T
        slope, _ = np.linalg.lstsq(A, lm, rcond=None)[0]
        D[i] = slope
    return D


# ---------------------------------------------------------------------------
# Box-counting dimension for a binary occupancy field (sanity / grids)
# ---------------------------------------------------------------------------
def box_counting_dimension(points: np.ndarray, n_scales: int = 12,
                           extent=None):
    """Minkowski-Bouligand (box-counting) dimension of a point set."""
    pts = np.asarray(points, float)
    if extent is None:
        lo = pts.min(0)
        hi = pts.max(0)
    else:
        lo, hi = extent
    span = (hi - lo).max()
    pts = (pts - lo) / span                  # normalise into unit cube
    dim = pts.shape[1]
    sizes = np.floor(np.logspace(0.3, np.log10(2 ** n_scales), n_scales)).astype(int)
    sizes = np.unique(sizes)
    counts = []
    for s in sizes:
        idx = np.floor(pts * s).astype(int)
        idx = np.clip(idx, 0, s - 1)
        occupied = len(np.unique(idx.dot(s ** np.arange(dim)), axis=0))
        counts.append(occupied)
    counts = np.array(counts, float)
    logS, logN = np.log(sizes), np.log(counts)
    A = np.vstack([logS, np.ones(len(logS))]).T
    slope, _ = np.linalg.lstsq(A, logN, rcond=None)[0]
    return slope, sizes, counts


if __name__ == "__main__":
    # quick self-test on a known object: a 2-D sheet embedded in 3-D
    rng = np.random.default_rng(0)
    sheet = np.column_stack([rng.random(4000), rng.random(4000),
                             np.zeros(4000)])
    D = local_dimension(sheet, k_min=8, k_max=128)
    print(f"2-D sheet in 3-D space -> local dimension = "
          f"{np.nanmean(D):.3f} +/- {np.nanstd(D):.3f}  (expect ~2)")
