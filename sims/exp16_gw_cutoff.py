"""
Experiment 16 -- Turning the dimensional-flow hypothesis into a FALSIFIABLE
gravitational-wave prediction.

e07 (evolving dimensions): the very early, ultra-dense universe was effectively
lower-dimensional, becoming 3+1 D only below some transition scale T*. Key
physical fact: gravitational waves are a property of (3+1)-D spacetime -- there is
no transverse-traceless graviton in 2+1 or 1+1 D. So NO primordial GWs were
produced from epochs hotter than T*. The stochastic GW background must therefore
be CUT OFF above the frequency that corresponds to horizon-crossing at T*.

This is the cleanest falsifiable consequence of the whole idea: measure the
primordial GW spectrum; if it continues smoothly through the predicted cutoff,
the hypothesis is dead. We compute where that cutoff lands for plausible T* and
put it next to real detectors (PTA, LISA, LIGO/ET).

Horizon-crossing -> present-day frequency (standard, e.g. Maggiore):
    f0 = 1.65e-7 Hz * (T*/GeV) * (g*/106.75)^(1/6)
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = "../figures"


def f0_today(T_GeV, gstar=106.75):
    """Present-day frequency of a mode that crossed the horizon at temperature T*."""
    return 1.65e-7 * T_GeV * (gstar / 106.75) ** (1.0 / 6.0)


# candidate dimensional-reduction scales T* (where d -> 3 'switches on')
scales = [
    ("QCD epoch",        0.15,      1e-8),
    ("Electroweak",      100.0,     1e-4),
    ("a few TeV",        3000.0,    1e-3),
    ("intermediate",     1e9,       1e-1),
    ("GUT",              1e16,      1e2),
]

print("=" * 72)
print("GRAVITATIONAL-WAVE CUTOFF from dimensional reduction at T*")
print("=" * 72)
print(f"  {'reduction scale T*':<18}{'T* [GeV]':>12}{'cutoff f0 [Hz]':>16}   best probe")
print("-" * 72)


def best_detector(f):
    if f < 1e-6:
        return "Pulsar Timing Arrays (nHz)"
    if f < 1e-1:
        return "LISA (mHz)"
    if f < 1e4:
        return "LIGO / Einstein Telescope (Hz-kHz)"
    return "above all current detectors"


for name, T, _ in scales:
    f = f0_today(T)
    print(f"  {name:<18}{T:>12.2e}{f:>16.2e}   {best_detector(f)}")

print("-" * 72)
print("""  Interpretation: the cutoff frequency scales LINEARLY with the reduction
  temperature. If dimensional reduction happens at the electroweak / TeV scale,
  the GW cutoff sits squarely in the LISA band (mHz) -- testable this decade. If
  it happens at the QCD scale, pulsar-timing arrays (already running) probe it.
  Only a GUT-scale reduction is out of reach.

  THE FALSIFIER: a detected, smooth, scale-invariant primordial GW spectrum that
  continues through f0(T*) rules out dimensional reduction at that T*. This turns
  a metaphysical-sounding idea into a number a detector can kill.

  Honest caveats: (1) which T* corresponds to 'd -> 3' is model-dependent -- this
  predicts the FORM (a cutoff at f0(T*)), not a unique frequency. (2) it assumes a
  detectable primordial GW background exists at all (inflationary amplitude is
  uncertain). (3) other physics (phase transitions, reheating) also imprint GW
  features; a cutoff alone is suggestive, not proof.""")

# ---- figure: cutoff vs T*, with detector bands ----
fig, ax = plt.subplots(figsize=(11, 6))
Tgrid = np.logspace(-1.5, 17, 200)
ax.loglog(Tgrid, f0_today(Tgrid), "-", color="black", lw=2,
          label="GW cutoff $f_0(T_*)$")

bands = [("PTA", 1e-9, 1e-6, "tab:green"),
         ("LISA", 1e-4, 1e-1, "tab:blue"),
         ("LIGO/ET", 1e1, 1e4, "tab:red")]
for nm, flo, fhi, col in bands:
    ax.axhspan(flo, fhi, alpha=0.15, color=col)
    ax.text(2e-1, np.sqrt(flo * fhi), nm, color=col, fontsize=11, va="center")

for name, T, _ in scales:
    f = f0_today(T)
    ax.plot(T, f, "o", ms=9, color="crimson")
    ax.annotate(name, (T, f), textcoords="offset points", xytext=(6, 6), fontsize=8)

ax.set_xlabel("dimensional-reduction scale  $T_*$  [GeV]")
ax.set_ylabel("present GW cutoff frequency  $f_0$  [Hz]")
ax.set_title("Falsifiable prediction: where the primordial GW spectrum is cut off\n"
             "if spacetime was lower-dimensional above $T_*$")
ax.legend(loc="upper left"); ax.grid(alpha=0.3, which="both")
ax.set_xlim(3e-2, 1e17); ax.set_ylim(1e-10, 1e10)

plt.tight_layout()
plt.savefig(f"{OUT}/exp16_gw_cutoff.png", dpi=130)
print(f"\n  figure saved -> figures/exp16_gw_cutoff.png")
