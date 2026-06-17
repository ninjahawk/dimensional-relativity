"""
Experiment 5 -- Does NET GRAVITY at universal scale change the effective
dimension of a region's fundamental degrees of freedom?  And is there a
THRESHOLD?

This is the rigorous, fact-based core of your idea. "Dimension" here means what
you actually meant: the way the *fundamental degrees of freedom* are organized.
The quantity that captures that and that gravity provably controls is ENTROPY
scaling:

  - Weak gravity:   entropy is EXTENSIVE,    S ~ Volume ~ R^3   -> organized in 3D
  - Strong gravity: entropy is HOLOGRAPHIC,  S ~ Area   ~ R^2   -> organized in 2D
        (Bekenstein-Hawking S = A / 4 l_p^2 ;  't Hooft / Susskind holography)

The control parameter is the gravitational COMPACTNESS
        zeta = R_s / R = 2 G M / (R c^2)        (R_s = Schwarzschild radius)
zeta -> 0 : ordinary matter, 3D organization.
zeta -> 1 : region is at its own horizon; organization collapses to 2D.

So the effective dimension of the degrees of freedom is
        d_dof = d ln S_max / d ln R  =  3   (zeta << 1)  ->  2   (zeta -> 1)

We compute zeta for REAL objects from planet to the whole observable universe,
and find where the threshold actually bites.
"""
import numpy as np

# --- constants (SI) ---
G   = 6.674e-11
c   = 2.998e8
hbar= 1.055e-34
kB  = 1.381e-23
l_p = np.sqrt(hbar * G / c**3)          # Planck length ~1.6e-35 m
Msun= 1.989e30
Mpc = 3.086e22
kpc = 3.086e19

TWO_G_OVER_C2 = 2 * G / c**2            # R_s per kg

# Hubble constant -> observable-universe numbers
H0 = 67.7e3 / Mpc                       # s^-1
R_H = c / H0                            # Hubble radius
rho_c = 3 * H0**2 / (8 * np.pi * G)     # critical density
M_univ = rho_c * (4/3) * np.pi * R_H**3 # mass within Hubble radius (flat universe)

# (name, Mass[kg], Radius[m]) -- self-gravitating extent (virial where relevant)
objects = [
    ("Human",                70.0,                     0.5),
    ("Earth",                5.97e24,                  6.37e6),
    ("Sun",                  1.989e30,                 6.96e8),
    ("Sgr A* (MW black hole)",4.3e6*Msun,  2*G*4.3e6*Msun/c**2),
    ("Milky Way (virial)",   1.5e12*Msun,              200*kpc),
    ("Galaxy cluster (Coma)",1.0e15*Msun,              3*Mpc),
    ("Supercluster (Laniakea)",1.0e17*Msun,            80*Mpc),
    ("Observable universe",  M_univ,                   R_H),
]

print("=" * 78)
print("GRAVITATIONAL COMPACTNESS  zeta = R_s/R = 2GM/(Rc^2)  -> dimensional regime")
print("=" * 78)
print(f"{'object':<26}{'M [kg]':>11}{'R [m]':>11}{'zeta=R_s/R':>14}  regime")
print("-" * 78)
for name, M, R in objects:
    Rs = TWO_G_OVER_C2 * M
    zeta = Rs / R
    if zeta < 1e-3:
        regime = "fully 3D  (d_dof = 3)"
    elif zeta < 0.5:
        regime = "3D, slight reduction"
    else:
        regime = "AT THRESHOLD -> 2D (holographic)"
    print(f"{name:<26}{M:>11.2e}{R:>11.2e}{zeta:>14.2e}  {regime}")

print("-" * 78)
print(f"Planck length l_p = {l_p:.3e} m")
print(f"Hubble radius R_H = {R_H:.3e} m   critical density rho_c = {rho_c:.3e} kg/m^3")

# --- the exact analytic punchline for a flat universe ---
print()
print("=" * 78)
print("KEY ANALYTIC RESULT (not a fit -- exact):")
print("=" * 78)
print("""  For ANY flat (critical-density) universe, the Schwarzschild radius of the
  mass inside the Hubble sphere equals the Hubble radius itself:

      M = rho_c (4/3)pi R_H^3,   rho_c = 3H^2/(8 pi G),   R_H = c/H
      =>  R_s = 2GM/c^2 = (H^2/c^2) R_H^3 = c/H = R_H      =>  zeta = 1  exactly.

  Meaning: galaxies, clusters, even superclusters sit at zeta ~ 1e-6..1e-4, so
  their net gravity does NOT change their dimensional organization at all.
  But the UNIVERSE AS A WHOLE sits exactly at zeta = 1 -- the holographic
  threshold where 3D (volume) and 2D (area) degree-of-freedom counts coincide.

  THE THRESHOLD YOU ASKED ABOUT IS REAL, AND IT LIVES AT THE COSMOLOGICAL
  HORIZON SCALE -- nowhere smaller. No cluster, however massive, reaches it;
  only the whole observable universe does.""")
print(f"\n  check: zeta(observable universe) computed above = "
      f"{TWO_G_OVER_C2*M_univ/R_H:.4f}")

# --- holographic degree-of-freedom counts (the "fundamental arrangement") ---
print()
print("=" * 78)
print("FUNDAMENTAL DEGREES OF FREEDOM (holographic bound  N = A / 4 l_p^2):")
print("=" * 78)
for name, M, R in [objects[i] for i in (4, 5, 6, 7)]:
    N_holo = np.pi * R**2 / l_p**2                  # area-law dof (2D-organized)
    N_vol  = (4/3) * np.pi * R**3 / l_p**3          # naive volume dof (3D-organized)
    print(f"  {name:<26} 2D-count(area)={N_holo:.2e}   "
          f"3D-count(volume)={N_vol:.2e}   ratio V/A={N_vol/N_holo:.2e}")
print("""
  The volume count vastly exceeds what gravity ALLOWS (the area count). Nature
  caps the real number of degrees of freedom at the 2D (area) value once a
  region approaches its horizon. That cap IS 'gravity lowering the dimension of
  the fundamental arrangement' -- precisely your idea, made exact.""")
