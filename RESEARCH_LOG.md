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

## NEXT (priority order — do the top unblocked one)
1. **e09 multifractal** — generalized dimensions D_q and the f(α) spectrum of the
   web. The web is multifractal; a single D hides structure. Compute D_0,D_1,D_2
   and the spectrum vs mass contrast. This is the rigorous upgrade of "the
   dimension depends on density."
3. **e10 local spectral dimension** — seed diffusion *inside* dense knots vs voids
   separately; get d_s(density). Tests whether the dynamical dimension also splits
   by density, not just globally.
4. **e11 real data** — fetch a public galaxy catalog (SDSS DR / 2MRS / a mock if
   offline) and run D(r) + D-vs-density on the actual sky. Empirical, not sim.
   (May need WebFetch/network; if blocked, build a high-fidelity mock and flag it.)
5. **e12 dimension field theory** — write D(x) as a scalar field with an action
   S[D, g, ρ]; derive its EOM; check what sourcing by stress-energy implies and
   whether it can ever give D>3 stably. Speculative, label clearly.
6. **e13 adversarial** — dedicated attempt to FIND a regime/measure where denser →
   higher D. Phase-space dim, AdS/CFT emergent dim, anti-correlated estimators.
   Honest search for the owner's direction. Report whatever is found.
7. Revisit e03 spectral estimator bias (better window / larger graphs / known-fractal validation like Sierpinski d_s=2ln3/ln5≈1.365).

## LEDGER (append-only; newest at bottom)
- 2026-06-16 — e01–e07 built and run. Core finding stable across 4 independent
  methods: mass-energy concentration lowers effective dimension toward 2, not up.
  Force-law dim pinned at 3 by stability. Threshold for holographic reduction is
  the horizon (ζ=1), reached only by black holes and the whole universe. Repo
  initialized and pushed. README written in Karpathy voice. Owner away overnight;
  autonomous iteration begins.
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
