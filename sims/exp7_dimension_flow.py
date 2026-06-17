"""
Experiment 7 -- Did dimension itself EVOLVE as the universe expanded from the
initial singularity?  (Your singularity/white-hole framing.)

STATUS: this is a FRONTIER HYPOTHESIS, not established fact. I label it as such.
But it is a real, published research program with FALSIFIABLE predictions:
  - "Spectral dimension" running 4 -> 2 toward the Planck scale
        (Ambjorn-Jurkiewicz-Loll, causal dynamical triangulations, 2005;
         Reuter-Saueressig asymptotic safety; Horava gravity)
  - "Evolving / vanishing dimensions": the very early, ultra-dense universe was
        effectively (1+1)- or (2+1)-dimensional, with full 3+1 D 'unfolding' only
        as it expanded and cooled
        (Stojkovic, Mureika, Anchordoqui et al., 2010-2014)

The mechanism is exactly what you intuited: ENERGY DENSITY (here via the
expansion / temperature of the universe) sets the effective dimension. Near the
singularity, density ~ Planck density and the effective dimension is ~2; as the
universe expanded and density dropped, it grew toward 3+1.

We implement the established CDT spectral-dimension flow and map it onto cosmic
history, then list the predictions that could KILL or CONFIRM it.
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = "../figures"

# --- CDT spectral-dimension flow (Ambjorn-Jurkiewicz-Loll 2005 fit form) ---
# d_s(sigma) = a - b/(c + sigma),  sigma = diffusion time ~ (probe length)^2
a, b, cc = 4.02, 119.0, 54.0
sigma = np.logspace(0.3, 4.0, 400)
d_s = a - b / (cc + sigma)
probe_length = np.sqrt(sigma)            # in Planck units (~ sqrt of diffusion time)

print("=" * 76)
print("EFFECTIVE (SPECTRAL) DIMENSION vs SCALE / COSMIC EPOCH")
print("=" * 76)
print(f"  UV limit (near singularity, Planck-scale probe): d_s -> {a - b/cc:.2f}")
print(f"  IR limit (today, cosmological probe):            d_s -> {a:.2f}")
print()
print("  Mapping probe scale -> cosmic energy density (schematic, order of mag):")
# crude map: probe length in Planck units <-> universe's age/horizon in Planck units
epochs = [
    ("Planck era (t~10^-43 s)",        1.0,        "~2  (effectively 1+1/2+1 D)"),
    ("GUT/inflation (t~10^-36 s)",     10.0,       "~2.5"),
    ("Electroweak (t~10^-12 s)",       1e2,        "~3"),
    ("Nucleosynthesis (t~1 s)",        3e2,        "~3.6"),
    ("Today (t~10^17 s)",              1e4,        "~4  (3+1 D)"),
]
for name, sig, dim in epochs:
    ds = a - b / (cc + sig)
    print(f"    {name:<34} probe^2~{sig:>7.0f} (Planck^2)  d_s={ds:4.2f}  -> {dim}")

print()
print("=" * 76)
print("FALSIFIABLE PREDICTIONS (this is what makes it science, not story):")
print("=" * 76)
print("""  1. PRIMORDIAL GRAVITATIONAL WAVES HAVE A HIGH-FREQUENCY CUTOFF.
        Gravitational waves require >= 3+1 dimensions to exist. If the early
        universe was effectively lower-D, no GWs were produced above the energy
        where 3+1 D 'switched on'. => a sharp cutoff in the stochastic GW
        background. Testable by LISA / pulsar-timing arrays / next-gen detectors.
        A detected smooth spectrum through that band would FALSIFY it.

  2. ULTRA-HIGH-ENERGY COSMIC RAYS BECOME PLANAR (lower-D) above ~ TeV.
        Reported hints of alignment in the highest-energy events; not confirmed.
        Clean isotropy at all energies would FALSIFY it.

  3. RUNNING OF THE SPECTRAL DIMENSION toward 2 in the deep UV.
        Independently 'measured' inside CDT, asymptotic safety, Horava gravity,
        loop quantum gravity -- four unrelated approaches agree d_s -> 2. That
        convergence is the strongest current support.

  HONEST WEIGHT OF EVIDENCE: the UV reduction d_s -> 2 is robust across multiple
  quantum-gravity programs. The cosmological 'evolving dimensions' version is
  speculative and not confirmed. BOTH say high density -> LOWER effective
  dimension (toward 2), consistent with Exp 2, 5, 6. No serious framework gives
  high density -> dimension ABOVE 3 except large-extra-dimension models, which
  the LHC has constrained (no sign up to several TeV).""")

# ----------------------------------------------------------------- figure
fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(probe_length, d_s, lw=2.5, color="darkviolet")
ax.axhline(2, ls=":", color="gray"); ax.axhline(4, ls=":", color="gray")
ax.set_xscale("log")
ax.set_xlabel("probe scale  (Planck lengths)  --  small = early/dense, large = today")
ax.set_ylabel("effective (spectral) dimension  d_s")
ax.set_title("Dimension as a FLOW: ~2 near the singularity -> 3+1 today\n"
             "(causal-dynamical-triangulation flow form; frontier hypothesis)")
for name, sig, dim in epochs:
    ds = a - b / (cc + sig)
    ax.annotate(name.split(" (")[0], (np.sqrt(sig), ds),
                textcoords="offset points", xytext=(6, -4), fontsize=8)
    ax.plot(np.sqrt(sig), ds, "o", color="crimson")
ax.set_ylim(1.5, 4.3); ax.grid(alpha=0.3)
plt.tight_layout()
plt.savefig(f"{OUT}/exp7_dimension_flow.png", dpi=130)
print(f"\n  figure saved -> figures/exp7_dimension_flow.png")
