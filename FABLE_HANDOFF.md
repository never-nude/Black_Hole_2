# Black Hole Visualization — Handoff for Fable

**Project folder:** `/Users/michael/Documents/Claude/Projects/Wormhole/`
**Owner:** Mike (GitHub `never-nude`)
**Last worked:** June 2026 (handed off mid-task — see Open Decision below)

---

## TL;DR

We took an existing combined wormhole+black-hole WebGL toy and built it up into a ladder of increasingly physically-real black hole renderers, each one verified against analytic general relativity before shipping. The newest (spinning Kerr) is done and correct, but Mike found it **"a bit jarring visually"** and asked to undo/calm it. **That decision is unresolved — start there (see Open Decision).**

---

## The file ladder

All are single self-contained HTML files, Three.js r160 from CDN, no build step. Open directly in a browser.

| File | What it is |
|---|---|
| `wormhole.html` | The original ancestor (~1177 lines): wormhole **and** black hole in one scene. Untouched. There's a `CODEX_TASK.md` about publishing this to `github.com/never-nude/space1` (public) — push status unknown. |
| `blackhole.html` | **Mesh-based** black hole only. Cloned from wormhole.html, wormhole stripped, recentered at origin. Event horizon (shader sphere + Fresnel rim), photon-sphere torus, ISCO ring, accretion disk (shader ring with fake Doppler), infalling particles, spin axis, **screen-space** lens post-process. Lightweight fallback. |
| `blackhole-lensed.html` | **Schwarzschild, ray-traced.** Full-screen per-pixel geodesic ray-marcher. Photon ring, shadow, disk-wrap, and Doppler beaming all emerge from the physics. Quality toggle + fps readout. Fall-in is physically lensed. |
| `blackhole-kerr.html` | **Kerr (spinning), ray-traced.** Full Kerr null geodesics. Spin slider a/M 0→0.998 with live frame-dragging: lopsided shadow, shrinking horizon, inward ISCO, ergosphere toggle. The most advanced rung, and the subject of the open question. |

Naming a future Kerr-or-better file: keep the `blackhole-*.html` convention so the ladder reads cleanly.

---

## ⚠️ Open Decision (resolve first, with Mike)

Mike opened `blackhole-kerr.html`, said *"can you undo this? it's a bit jarring visually,"* and the clarifying question never got answered before handoff. The three candidate readings:

1. **Revert to Schwarzschild** — treat `blackhole-lensed.html` as the working build again; leave the Kerr file in the folder, set aside.
2. **Keep Kerr but open calm** *(my best guess at what he means)* — it loads at **spin 0.7** with an off-center, lopsided shadow **and auto-rotate on**, which is probably the jarring part. Default it to **spin 0** (centered/symmetric, looks like a "normal" black hole), soften the contrast/tonemapping, and **start with auto-rotate off**, so it opens calm and he dials spin up himself.
3. **Delete `blackhole-kerr.html`** entirely.

Recommend confirming which one before doing anything destructive. If leaning to #2, the relevant knobs in the file: default `bhParams.spin` (set `0`), `controls.autoRotate` (start `false`), and the shader's final exposure/tonemap (`col*=1.15` then ACES — dial exposure down a touch and/or reduce the Doppler `beaming = g*g*g` exponent for less blowout). Note: file deletion in this environment is gated and needs Mike's explicit approval.

---

## Physics & verification method (the important part — preserve this discipline)

**Rule we followed: never write a shader until the physics is verified in Python (numpy) in the sandbox.** Both rungs were validated against closed-form GR before any GLSL was written. Reproduce this for anything new.

### Schwarzschild (`blackhole-lensed.html`)
- Photons obey `d²u/dφ² + u = 3M u²`. Vector form used in the shader: **`a = −1.5·Rs·h²·r̂ / r⁵`** (h = |r × v|, Rs = horizon radius, working in units of Rs).
- Verified: the constant **C = 1.5** reproduces the analytic capture threshold **b_crit = (3√3/2)·Rs = 2.598 Rs** to 4 decimals, and weak-field deflection converges to Einstein's **2Rs/b**.
- Ray march: per pixel integrate the geodesic; r < Rs → black shadow; equatorial-plane crossing in [3Rs, 11Rs] → disk with Doppler; escape → lensed procedural starfield.

### Kerr (`blackhole-kerr.html`)
- **Canonical Hamiltonian** integration in **Boyer-Lindquist** coords. Conserved **E** and **Lz** (set E=1); integrate (r, θ, φ, p_r, p_θ) with **RK4**. Forces = **central finite differences of the super-Hamiltonian 2H** (i.e. `dp_r = −(2H(r+ε) − 2H(r−ε))/(4ε)`), which is exactly what ships in GLSL — no hand-derived Christoffels.
- Inverse metric (M=1): `Σ=r²+a²cos²θ`, `Δ=r²−2r+a²`, `A=(r²+a²)²−a²Δsin²θ`; `g^tt=−A/(ΣΔ)`, `g^tφ=−2ar/(ΣΔ)`, `g^φφ=(Δ−a²sin²θ)/(ΣΔsin²θ)`, `g^rr=Δ/Σ`, `g^θθ=1/Σ`.
- **Camera-ray initial conditions** (the part that differs from the idealized Python test, so it was verified separately): map the world-space pixel ray → BL coordinate velocities via the **oblate-spheroidal Jacobian**, fix the time component by **null normalization** (future-directed root), lower indices to get p_r, p_θ, and E, L, then divide through by E.
- Verified three ways:
  - **a→0** reproduces the Schwarzschild capture threshold (2.598 Rs).
  - **Shadow boundary** matches the exact analytic **Bardeen critical curve** — at a=0.9, i=85° the marched edges were −2.850 / +6.820 vs analytic −2.851 / +6.825 (within a pixel).
  - **CPU-port of the actual shader `main()`** (Jacobian ICs included) rendered a spin sweep: a=0 gives a centered symmetric shadow (centroid −0.5px), a=0.95 shifts it to −8.7px — frame-dragging.
- Spin-dependent radii (M=1), computed live in the UI readout and used for ISCO/horizon:
  - horizon `r₊ = M + √(M²−a²)`; prograde photon `2(1+cos(⅔·acos(−a)))`; ISCO via Bardeen Z1/Z2.
- Disk brightness uses the **real Kerr redshift+Doppler factor** `g = √(1 − 3/r + 2a/r^{3/2}) / (1 − Ω·b)`, with `Ω = 1/(r^{3/2}+a)` and `b = Lz/E` the photon's conserved axial impact parameter. Brightness ∝ g³.
- **Orientation convention:** spin axis = world **+Y**, disk in the world **XZ** (equatorial) plane. The shader permutes world(x,y,z)→BL(z,x,y) at the top of `main()`. Inclination is changed by orbiting the camera, **not** a tilt slider (a disk can't tilt independent of spin in Kerr — that slider was removed).

### Verification tooling notes
- **headless-gl won't build** in this sandbox (no system GL libs), so we can't render the actual WebGL offscreen. Instead we **CPU-port the fragment shader's `main()` to vectorized numpy** and render a low-res frame to PNG to eyeball. Proof images were written to the outputs scratchpad (`bh_verify.png`, `kerr_shadow_proof.png`, `kerr_sweep.png`) — those are session-temporary and may be gone; regenerate from `/tmp/*.py` logic if needed.
- **Can't screenshot the live page from here:** the Chrome extension lacks local-file permission and the navigate tool forces `https://`, so `file://` loads fail. Mike opens the files himself to view.

---

## GLSL / implementation gotchas

- `THREE.ShaderMaterial` defaults to **GLSL ES 1.00**: no `inverse()` builtin (we hand-code a 3×3 inverse via cross products), loops need **constant bounds** (`const int MAX_STEPS`, then `if (float(i) >= uSteps) break;`), and output is `gl_FragColor`.
- The whole BH is drawn on a **full-screen quad** (ortho cam + plane), not meshes. Mesh objects remain only as **invisible raycast proxies** so hover/click labels still work; their world matrices are updated each frame.
- **Units:** internal math is M=1. `uM = Rs/2` where the "Mass (Rs)" slider = Rs in world units. Convert world↔internal by dividing positions by `uM`.
- **Performance:** Kerr is heavy — RK4 × finite-diff ≈ ~20 inverse-metric evals per step. Adaptive stepping makes empty space cheap; the **Quality** toggle drops resolution + step count. Render pixel ratio is capped to 1 (or 0.6 on Low). There's a live fps readout.

---

## Roadmap that was on the table (Mike's call which, if any)

1. **Performance pass** — replace finite-diff forces with **analytic Kerr forces** (~4× fewer metric evals) + **adaptive step count** to hold 60fps so "High" always works. *(I'd recommended this next so everything downstream runs smoothly.)*
2. **Observer instruments** — a fall-in HUD: time-dilation clock (you vs. distant observer), gravitational redshift, tidal/spaghettification meter, orbital velocity. The Kerr metric already exposes everything needed.
3. **Deeper Kerr** — inner horizon, ergosphere Penrose-process visualization, photon-ring **subrings** (n=1,2 light echoes, the next-gen EHT target).

---

## Working with Mike (preferences)

Direct but conversational; lead with the deliverable, not a plan. **Build the thing, don't describe it.** He delegates aesthetic/visual judgment but **retains tight control over structural/functional requirements — confirm before changing architecture, data models, or core behavior.** Progressive output over big dumps. He's an artist/sculptor (the "sculpting curved spacetime" framing lands). Comfortable with the stack; no need to over-explain code. He routes work deliberately across tools — this is being handed to Fable on purpose.
