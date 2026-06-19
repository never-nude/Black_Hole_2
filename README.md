# Black Hole 2

Interactive, single-file WebGL/Three.js black-hole visualization. An upgrade of the
original mesh-based renderer with a **true volumetric star** and two toggleable
**field layers** (gravitational well + magnetic field). No build step — open the HTML
directly in a modern browser.

## Files

| File | What it is |
|---|---|
| `blackhole.html` | **Main build.** Mesh black hole — event horizon, photon sphere, accretion disk (Doppler-boosted), ISCO, screen-space lensing, fall-in, tidal-disruption event, volumetric star, and the new field layers. |
| `blackhole-lensed.html` | Schwarzschild, fully ray-traced per-pixel geodesic marcher. |
| `blackhole-kerr.html` | Kerr (spinning), ray-traced, with frame-dragging. |
| `wormhole.html` | The original wormhole + black hole ancestor. |
| `FABLE_HANDOFF.md` | Physics, verification method, and architecture notes. |
| `star_proof.py`, `field_proof.py` | NumPy/Matplotlib proofs used to verify the shader/geometry math before shipping to the GPU. |

## What's new in v2

- **Volumetric star** (tidal-disruption event) — a raymarched sphere with 3D-noise
  plasma/granulation, blackbody color (white-hot disk center → orange granule limb),
  limb darkening, and a wispy animated corona. Dissolves into the existing particle
  stream as it's torn apart. Quality toggle caps the raymarch step count.
- **Gravity well** layer — Flamm-paraboloid funnel (the real Schwarzschild embedding
  diagram) with inspiraling tracer bodies and trails, showing how matter wanders in.
- **Magnetic field** layer — dipole poloidal field loops (`r = r_eq·sin²θ`) threading
  the disk, flowing plasma beads, and twin relativistic jets along the spin axis.
- **Mobile-responsive** — viewport-aware layout, slide-up control/info sheets, and
  touch-sized hit targets.

## Physics (verified against GR before shipping)

- Schwarzschild photon geodesic `a = −1.5·Rs·h²·r̂/r⁵` (reproduces `b_crit = 2.598 Rs`).
- Kerr null geodesics via canonical Hamiltonian in Boyer-Lindquist, RK4 (verified
  against the analytic Bardeen shadow curve).
- Tidal disruption: near-parabolic infall under point-mass gravity → spaghettified
  stream; ~25% accretes (the flare), the rest forms tidal tails.

See `FABLE_HANDOFF.md` for the full detail.

## Controls

Drag to orbit · right-drag to pan · scroll to zoom · WASD+QE to fly · Shift to boost ·
R to reset. Click any label for a plain-English explanation. On phones, use the ⚙ and
ℹ buttons to open the control and info sheets.

## Stack

Pure HTML/CSS/vanilla JS modules. Three.js r160 from CDN with `EffectComposer` for the
post-processing lens shader. All shaders are GLSL ES 1.00.
