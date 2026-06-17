# RESEARCH LOG — dimensional-relativity

This file is the persistent brain of the project. It is written so that an agent
(me) resuming with *no memory of previous turns* can read this top-to-bottom and
continue the research without losing the thread. If you are that agent: read the
PROTOCOL, read STATUS, do the top item in NEXT, then append to the LEDGER.

Repo: https://github.com/ninjahawk/dimensional-relativity
Local: C:\Users\jedin\Desktop\DimensionalRelativity
Owner: ninjahawk (Nathan). Wants brutal honesty, no flattery, real science only.
The mission: falsifiably determine what the dimensionality of space is determined
by — at universal scale, focused on whether net gravity / mass-energy
concentration sets it. The owner believes denser → higher dimension; the evidence
so far says the opposite. Report the truth either way.

## PROTOCOL (how each overnight iteration runs)
1. `cd` to the repo. `git pull` (in case). Read this log.
2. Pick the highest-priority unblocked item in NEXT.
3. Do real work: write a script in `sims/`, run it, generate a figure, get NUMBERS.
4. Be adversarial to my own conclusions. Try to break "denser → lower D", not confirm it.
5. Update STATUS + LEDGER below with what was found (the number, not vibes).
6. `git add -A && git commit` with a clear message, `git push`.
7. Schedule the next wakeup to keep going.
8. Keep iterations atomic: one experiment per commit so the history is a story.

## STATUS (experiments done)
- [x] e01 validation — estimator nails Sierpinski D=1.584 (true 1.585). 16× density → ΔD=+0.003.
- [x] e02 cosmic web — denser → lower D, Pearson r=−0.31. D(r) runs 2.6→2.9. analytic D=3−γ.
- [x] e03 spectral — diffusion dimension. lattices 2.14/3.51 (biased), web d_s≈2.67 < 3D-control.
- [x] e04 stability — orbits bind only at D=3 (Ehrenfest). D≥4 unbound. D=2 over-bound.
- [x] e05 holographic — compactness ζ=2GM/Rc². threshold ζ=1 = horizon. universe exact ζ=1; clusters ~1e-4.
- [x] e06 mass contrast — dimensional spread grows with contrast up to ~10× (dD 0.16→1.13), then Zel'dovich breaks.
- [x] e07 dimension flow — spectral d 2→4 from singularity to today. evolving-dimensions hypothesis, labeled.
- [x] e08 N-body PM gravity — real self-gravity (CIC+FFT+leapfrog). KEY HONEST RESULT:
  dense-region geometric D is NON-MONOTONIC in contrast. Strongest low-D at the
  filament/sheet stage (contrast ~13x: densest 0.1% D~2.0, r=-0.52), then washes
  back to ~3 as halos VIRIALIZE into locally-3D blobs. Geometric dim tracks
  MORPHOLOGY (filament1/sheet2/halo3), not density magnitude. This corrected my
  earlier guess that D just keeps falling. (Caveat: non-expanding box.)
- [x] e09 multifractal — sandbox-estimator generalized dimensions D_q (box-counting
  failed its own uniform validation; sandbox passes after raising inner radius).
  D_q falls with q: dense (q=+6) D~2.1, sparse (q=-6) D~3.2-4, D_2 2.92→2.56 as
  clustering grows. Multifractal width grows from 0.47 (mild) to 2.0 (strong).
  Rigorous single-object confirmation dimension depends on density. Caveat:
  negative-q (sparse) noisy; robust quantities are D_0/D_1/D_2 + the trend.
- [x] e10 local spectral — diffusion (heat-kernel diagonal) seeded by environment.
  d_s(dense)=2.57 vs d_s(void)=3.01, Δ=-0.44. DYNAMICAL dimension also lower in
  dense regions (at filament stage). Void lands exactly on 3 (clean). Independent
  corroboration of the geometric result.
- [x] e11 robustness — swept power-spectrum slope n=-1.5..-3.0. Pearson r stays
  -0.29..-0.34 (all "dense=lower-D"), MF width 0.40..1.41, D_2 2.71..2.91. Sign
  invariant across morphologies; magnitude tracks clustering. Not a tuning artifact.
- [x] e12 connectivity — THE regime where the owner's "dense=higher-D" WINS.
  Spectral d_s set by connectivity: long-range links raise d_s without bound
  (2D lattice 2.14 -> +100% links 6.63). Density-modulated graph: dense core
  d_s=4.56 > sparse edge 4.09 (+0.47). So SIGN depends on mechanism: gravity/
  anisotropy lowers D; long-range connectivity raises it. Owner's intuition is
  right in the connectivity-dominated regime (AdS/CFT, ER=EPR, entanglement).
  Caveat: absolute d_s inflated by estimator bias; relative comparison robust.
- [x] e13 entanglement — emergent dimension from entanglement (AdS/CFT steelman).
  Exact free-fermion S(l); central-charge check PASSES (c=1.004 vs exact 1).
  Entanglement graph: critical d_s=1.94 > gapped 1.34 (+0.60). More entanglement
  (criticality) => higher emergent dimension. "Matter/energy generates a
  dimension" as an actual calculation; owner's intuition realized via
  entanglement/connectivity, not mass density per se.
- [x] e14 dimension field — fractional/Levy diffusion. Validated d_s=2/alpha
  (alpha=1.5→1.34, 1.0→1.98, 0.7→2.82). Built a 3-zone medium with a literal
  position-dependent d_s(x)=2/alpha(x) (0.90/1.52/2.47). The "new equations":
  d_s(x)=2 d_geom/alpha(rho(x)). Honest: alpha(rho) is a modeling choice; the
  derived parts are d_s=2/alpha and long-range→higher-D.
- [x] e15 expanding N-body — comoving EdS particle-mesh. INTEGRITY GATE PASSED:
  mode growth tracks linear theory delta∝a to 2-3% over a=0.02→2 (a-factors
  correct). Fair test (proper expansion) gives a CLEANER, STRONGER result than
  e08: dense regions stay low-D (D~2.3-2.7) through all of cosmic evolution,
  r(density,D) = -0.46..-0.64 (stronger than e02's -0.31). Web keeps a PERSISTENT
  low-D filament skeleton; only mild recovery (2.32→2.68) at late times from
  partial halo virialization. CORRECTS e08's "dense bounces back to 3" — that was
  largely a non-expanding-box runaway-collapse artifact.
- [x] e16 GW cutoff — turned e07 into a falsifiable prediction. GW background cut
  off above f0(T*)=1.65e-7 Hz·(T*/GeV) since GWs need 3+1 D. Electroweak/TeV
  reduction → LISA (mHz); QCD → PTA (nHz); both testable now. A smooth spectrum
  through f0 kills it. Caveats: T*↔"d→3" model-dependent; assumes a detectable
  primordial background exists.

## NEXT (priority order — do the top unblocked one)
1. **e17 entanglement vs geometry crux** — order-of-magnitude: at cosmological
   scale, can ER=EPR/entanglement connectivity (raises D) ever compete with
   geometric anisotropy (lowers D)? Estimate the entanglement entropy budget vs
   the geometric clustering signal. This is THE open physical question from SYNTHESIS.
4. **e18 better spectral estimator** — validate spectral-dim pipeline on the
   Sierpinski gasket (known d_s=2 ln3/ln5≈1.365) and de-bias e03/e10/e12 absolute
   numbers.
5. **real data (BLOCKED on owner)** — SDSS/DESI D-vs-density on the real sky.
   Needs care with survey mask/selection; do WITH owner input, not solo overnight.
   A naive mask-ignoring analysis would be misleading — explicitly do not fake it.

## LEDGER (append-only; newest at bottom)
- 2026-06-16 — e01–e07 built and run. Core finding stable across 4 independent
  methods: mass-energy concentration lowers effective dimension toward 2, not up.
  Force-law dim pinned at 3 by stability. Threshold for holographic reduction is
  the horizon (ζ=1), reached only by black holes and the whole universe. Repo
  initialized and pushed. README written in Karpathy voice. Owner away overnight;
  autonomous iteration begins.
- 2026-06-16 — e12 connectivity. IMPORTANT for honesty/balance: found the real
  regime where the owner's "denser=higher dimension" is TRUE. Spectral dimension
  rises with long-range connectivity, unbounded; a density-modulated graph makes
  dense regions higher-D. So the sign is mechanism-dependent, not a flat "no".
  Gravity (anisotropy) lowers; connectivity (shortcuts) raises. The physical
  question becomes: does universal-scale concentration create long-range links?
  That is the AdS/CFT / ER=EPR / entanglement question -> e13.
- 2026-06-16 — e09 multifractal + e10 local spectral. Two independent methods both
  confirm dimension depends on density at the web/filament stage: D_q spectrum
  width grows with clustering (geometric), and diffusion d_s splits 2.57(dense)
  vs 3.01(void) (dynamical). Caught and fixed a box-counting estimator artifact
  via uniform validation (switched to sandbox method). Honest-estimator hygiene
  is paying off. Reconciling with e08: at the filament stage all measures say
  dense=lower-D; the e08 "returns to 3" is specifically the deeply-VIRIALIZED
  halo regime. So the full picture: dense filaments/sheets are low-D; once they
  collapse to virialized halos the GEOMETRIC dim recovers to 3 while holographic
  dof-count (e05) stays the dense=2D carrier. Two notions, different behavior.
- 2026-06-16 — e08 N-body run. SURPRISE that corrected a prior claim: dense-region
  geometric dimension is non-monotonic in mass contrast — low (~2) at the filament
  stage, back to ~3 once halos virialize. Lesson: the *geometric* dimension tracks
  morphology, so it is NOT the clean "dense→2D" carrier; that role belongs to the
  *holographic* dof-count (e05). Two distinct notions of dimension behaving
  differently is itself a real result. Committed honestly.

## STANDING CONVENTIONS
- effective dimension default estimator: local kNN slope, k=12..120, periodic box.
- density proxy: raw neighbour count in a fixed aperture (no volume → no baked-in D).
- always validate a new estimator on a known object (line/sheet/fractal) first.
- keep figures reproducible; matplotlib Agg; dpi 130.
- one finding = one number + one figure + one commit.
