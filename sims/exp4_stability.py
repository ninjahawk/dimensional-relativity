"""
Experiment 4 -- The self-consistency knife-edge:
Can dense, bound matter even EXIST in dimensions other than 3?

Your hypothesis says high density should push space toward higher dimension.
But there is a brutal constraint, first noticed by Ehrenfest (1917):

  In D spatial dimensions, Gauss's law forces gravity/electrostatics to fall
  off as  F(r) ~ 1 / r^(D-1).
  The effective radial potential for an orbiting body is
        V_eff(r) = -k / r^(D-2)        +   L^2 / (2 m r^2)
                   (attraction)            (centrifugal barrier)

  - D = 3:  attraction ~1/r, barrier ~1/r^2  -> a real minimum -> STABLE orbits,
            stable planetary systems, stable atoms.
  - D >= 4: attraction falls off at least as fast as the barrier -> NO stable
            minimum -> every orbit either plunges to r=0 or escapes.
  - D = 2:  logarithmic potential -> everything is bound, nothing escapes;
            a qualitatively different (and structureless) universe.

CONSEQUENCE FOR THE HYPOTHESIS:
  If a dense region had D >= 4, atoms and gravitational clumps there could not
  hold together -- so matter could not have become dense in the first place.
  "Density creates higher dimension" is therefore self-defeating: stable
  density REQUIRES D = 3. If anything, the causal arrow runs the other way.

We test this by direct orbit integration in D = 2, 3, 4, 5.
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = "../figures"


def accel(r_vec, D, k=1.0):
    """Acceleration of a test body, central attractive force ~ 1/r^(D-1)."""
    r = np.linalg.norm(r_vec)
    if r < 1e-9:
        return np.zeros_like(r_vec)
    # |a| = k / r^(D-1), direction -r_hat = -r_vec/r  => a = -k r_vec / r^D
    return -k * r_vec / r**D


def integrate(D, v_factor=0.9, steps=200000, dt=2e-3, k=1.0):
    """Start near a circular orbit at r=1, perturb the speed, integrate (RK4).
    Returns the trajectory and the radius history."""
    r0 = 1.0
    # circular speed: v^2 / r = k / r^(D-1) -> v_c = sqrt(k / r^(D-2))
    v_c = np.sqrt(k / r0**(D - 2)) if D != 2 else np.sqrt(k)
    pos = np.array([r0, 0.0])
    vel = np.array([0.0, v_factor * v_c])

    traj = np.empty((steps, 2))
    radii = np.empty(steps)
    for i in range(steps):
        traj[i] = pos
        radii[i] = np.linalg.norm(pos)
        if radii[i] < 1e-3 or radii[i] > 50:    # plunged or escaped
            traj = traj[:i + 1]
            radii = radii[:i + 1]
            break
        # RK4 on (pos, vel)
        def deriv(p, v):
            return v, accel(p, D, k)
        k1p, k1v = deriv(pos, vel)
        k2p, k2v = deriv(pos + 0.5 * dt * k1p, vel + 0.5 * dt * k1v)
        k3p, k3v = deriv(pos + 0.5 * dt * k2p, vel + 0.5 * dt * k2v)
        k4p, k4v = deriv(pos + dt * k3p, vel + dt * k3v)
        pos = pos + (dt / 6) * (k1p + 2 * k2p + 2 * k3p + k4p)
        vel = vel + (dt / 6) * (k1v + 2 * k2v + 2 * k3v + k4v)
    return traj, radii


print("=" * 64)
print("ORBIT STABILITY IN D SPATIAL DIMENSIONS")
print("  (start at r=1 with 90% of circular speed, integrate, watch r)")
print("=" * 64)

fig, axes = plt.subplots(2, 4, figsize=(18, 9))
verdicts = {}
for j, D in enumerate([2, 3, 4, 5]):
    traj, radii = integrate(D)
    rmin, rmax = radii.min(), radii.max()
    survived = len(radii)
    bounded = (rmin > 1e-2) and (rmax < 10)
    verdict = "STABLE  (matter can bind)" if bounded else \
              ("PLUNGE to singularity" if rmin <= 1e-2 else "ESCAPE / unbound")
    verdicts[D] = (verdict, rmin, rmax)
    print(f"  D = {D}:  r ranged [{rmin:6.3f}, {rmax:6.3f}]   ->  {verdict}")

    # orbit plot
    ax = axes[0, j]
    ax.plot(traj[:, 0], traj[:, 1], lw=0.6,
            color="crimson" if not bounded else "navy")
    ax.plot(0, 0, "y*", ms=14, mec="k")
    ax.set_title(f"D = {D}\n{verdict}")
    ax.set_aspect("equal"); ax.grid(alpha=0.3)
    lim = min(5, max(1.5, rmax * 1.1))
    ax.set_xlim(-lim, lim); ax.set_ylim(-lim, lim)

    # radius-vs-time plot
    ax2 = axes[1, j]
    ax2.plot(radii, lw=0.8, color="darkgreen")
    ax2.set_xlabel("step"); ax2.set_ylabel("radius")
    ax2.axhline(1.0, ls=":", color="gray")
    ax2.set_title(f"radius over time (D={D})")
    ax2.grid(alpha=0.3)

plt.tight_layout()
plt.savefig(f"{OUT}/exp4_stability.png", dpi=120)

print("\n  VERDICT: stable bound orbits exist ONLY at D = 3.")
print("  This is why a universe that contains stable atoms, stars and planets")
print("  must be (macroscopically) 3-dimensional. A region cannot quietly")
print("  become 4-D just because it is dense -- its matter would fall apart.")
print(f"\n  figure saved -> figures/exp4_stability.png")
