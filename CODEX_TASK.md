# Codex Publish Task

**Goal:** Push this project to `github.com/never-nude/space1` (or, if `space1` is intended as a subdirectory within an existing repo, place these files under `/space1/` in that repo).

## Repo metadata

- **Owner:** never-nude
- **Suggested repo name:** `space1`
- **Visibility:** public
- **Description:** Interactive, single-file WebGL educational visualization of a wormhole (Einstein–Rosen bridge) and a black hole, with first-person black hole fall, gravitational lensing, and click-to-explain physics labels.
- **Topics:** `webgl`, `threejs`, `educational`, `physics`, `general-relativity`, `wormhole`, `black-hole`, `interactive`

## Files to publish

- `wormhole.html` — the entire app (single file, no build step)
- `README.md` — project overview
- `CODEX_TASK.md` — this file (optional to include)

## Suggested commit message

```
Initial release: interactive wormhole + black hole visualization

- Catenoid wormhole embedding diagram with adjustable throat/length/flare
- Black hole with event horizon, photon sphere, ISCO, accretion disk
  (Doppler beaming), infalling particles, spin axis
- First-person "fall into the black hole" with EffectComposer
  gravitational lensing shader, blueshift, chromatic aberration,
  vignette, and phase-by-phase narration
- Hover any 3D feature for tooltips; click for plain-English popovers
- Mouse orbit/pan/zoom + WASD/QE keyboard flight
```

## Repo URL after publish

`https://github.com/never-nude/space1`

## Notes

The project is fully self-contained — `wormhole.html` runs by being opened directly in a browser. Three.js r160 is loaded via CDN (`cdnjs` + `jsdelivr`). No build step, no package.json, no dependencies to install.
