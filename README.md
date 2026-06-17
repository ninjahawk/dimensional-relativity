# dimensional-relativity

A from-scratch numerical attack on one question I've been chewing on since I was about 15:

**is the dimensionality of space a fixed backdrop, or is it set by matter?**

The intuition: nobody hands "3D" down from above. Maybe dimension is *caused* by
something physical — maybe where you pile up an absurd amount of mass-energy,
space organizes itself differently than where it's nearly empty. That's the
hypothesis. This repo is me actually testing it with code instead of just
staring at the ceiling about it.

No frameworks, no magic, ~1k lines of python, just numpy/scipy/matplotlib. Every
claim below has a script next to it you can run. Where the idea is right I say
so; where it's wrong I say that too, with the number that killed it.

## tl;dr (what the code actually shows)

| claim | verdict | the number |
|---|---|---|
| dimension is a fixed integer | **wrong** | the estimator reads the Sierpinski fractal at D=1.584 (true 1.585) |
| *amount* of matter sets dimension | **wrong** | 16× more uniform density → ΔD = +0.003 (nothing) |
| *arrangement* of matter sets dimension | **right** | cosmic web: denser → lower D, Pearson r = −0.31 |
| denser regions are higher-dimensional | **backwards** | dense filaments measure D→1–2; voids → 3 |
| dimension runs with scale | **right** | D(r): ~2.6 small-scale → ~3 large-scale; spectral d_s flows 2→4 |
| net gravity sets the *fundamental* dimension | **right, with a threshold** | holographic dof go 3→2 at ζ = R_s/R = 1 |
| a supercluster's gravity is enough to do it | **no** | clusters sit at ζ ~ 1e-4, ~10⁴× too diffuse |
| the whole universe is enough | **yes, exactly** | flat universe ⇒ ζ = 1 identically (R_s = R_H) |
| only D=3 can hold matter together | **right** | orbits bind only at D=3 (Ehrenfest); D≥4 plunges/escapes |

Short version: **the hypothesis is half right in a deep way.** Dimension really
is a non-integer, local, scale-dependent thing set by matter — that part is real
physics. But every way I measure it, cramming in mass-energy pushes the effective
dimension *down* toward 2 (holography, the cosmic web, quantum-gravity spectral
flow all agree), not up. And the force-law dimension you actually walk around in
stays pinned at 3 because nothing else can hold an atom together.

## the question, made precise

"Dimension" is overloaded. Four different things wear the same word, and the
answer is different for each:

1. **topological / force-law** — number of directions; sets `F ∝ 1/r^(D−1)`. pinned at 3.
2. **geometric / fractal** — how matter fills space. non-integer, varies. *measurable.*
3. **spectral** — how diffusion/fields propagate. runs with scale. *the quantum-gravity one.*
4. **holographic** — count of fundamental degrees of freedom. gravity controls it.

The whole trick is to stop arguing about #1 and actually measure #2–#4, which are
allowed to move. So the first thing the repo does is build estimators that can
see a non-integer dimension and *prove* they work on a known fractal before
trusting them on anything subtle.

## experiments

run them in order, each prints its result and drops a figure in `figures/`.

- `sims/dimension_tools.py` — the estimators (correlation dim, local dim, box-counting). self-tests on a sheet.
- `sims/exp1_validation.py` — recovers 1D/2D/3D + the Sierpinski fractal. then shows 16× density does nothing.
- `sims/exp2_cosmicweb.py` — grows a cosmic web (Zel'dovich), measures D vs local density. **the money plot.**
- `sims/exp3_spectral.py` — spectral dimension from diffusion. validates on lattices, then the web.
- `sims/exp4_stability.py` — integrates orbits in D=2,3,4,5. only D=3 survives.
- `sims/exp5_holographic.py` — compactness ζ for everything from a human to the observable universe. finds the threshold.
- `sims/exp6_masscontrast.py` — does the effect grow with mass piled up? (yes, until my sim method breaks — see caveats.)
- `sims/exp7_dimension_flow.py` — dimension as a flow: ~2 near the Big Bang → 3+1 today. frontier hypothesis, labeled as such.

## running it

```bash
pip install -r requirements.txt
cd sims
python exp1_validation.py    # ... through exp7
```

nothing here needs a GPU or more than a couple minutes. the heaviest is the
cosmic-web run (262k particles) at ~1–2 min.

## what I actually believe now

- dimension is **not** fundamental-and-fixed. it's a field-like quantity set by
  matter/energy. my 15-year-old instinct was pointing at something real.
- the sign is the opposite of what I guessed: **concentration lowers effective
  dimension toward 2.** holography, the cosmic web, and four separate
  quantum-gravity programs all say this. I've stopped fighting it.
- there *is* a real threshold, and it's the one place the universe's own gravity
  reaches it: the horizon, ζ=1. not clusters. not superclusters. the whole thing.
- the only place "more matter → *more* dimension" survives is (a) large extra
  dimensions, which the LHC has been quietly strangling, and (b) AdS/CFT, where
  matter genuinely *generates* an extra dimension — but it's the energy-scale
  direction, not a new way to walk.

## todos / roadmap

this is under active, nightly development. next up, roughly in order:

- [ ] **real data.** SDSS/DESI galaxy catalog → measure D(r) and D-vs-density on the actual sky. the experiment that makes this empirical instead of simulated.
- [ ] **full N-body.** Zel'dovich breaks after shell-crossing (see caveats), so push mass contrast into the deeply nonlinear regime with a real particle-mesh gravity solver.
- [ ] **multifractal spectrum** f(α) / generalized dimensions D_q of the web. the cosmic web isn't mono-fractal; characterize the whole spectrum.
- [ ] **local spectral dimension** — diffusion seeded inside dense vs empty regions, not just globally.
- [ ] **the dimension field.** write D(x,r) as an actual field with an action and see what equation it wants to satisfy. speculative, labeled.
- [ ] **GW cutoff.** work out the predicted high-frequency cutoff in the primordial gravitational-wave background from exp7's flow.

## caveats (read these)

- the Zel'dovich approximation in exp2/exp6 is first-order and only trustworthy
  up to shell-crossing. past mass-contrast ~10× the structures wash out and the
  curves bend back — that's the *method* dying, not physics. the N-body todo
  fixes it.
- the spectral-dimension estimator (exp3) has a +0.1–0.5 bias from finite size;
  treat it as a *relative* probe, not a precise number.
- exp7 (evolving dimensions) is a frontier hypothesis, not established. the UV
  reduction d_s→2 is robust across programs; the cosmological story is not.
- nothing here is peer-reviewed. it's a serious hobby investigation that tries
  very hard to be honest, including about itself.

## notes

longer writeups with the derivations live in `notes/`:
- `notes/FINDINGS.md` — the full argument, the D = 3 − γ derivation, references.
- `notes/THRESHOLDS.md` — what determines dimension, every threshold, every constraint, how to falsify each.

---

*started from a question, kept honest by the code. if a result here is wrong,
the script is right there — go break it.*
