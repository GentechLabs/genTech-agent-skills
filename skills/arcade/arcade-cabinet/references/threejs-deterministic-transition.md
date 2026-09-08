# Three.js Deterministic Scene-Transition Pattern — from MengTo complete-shelf

Source: https://github.com/MengTo/complete-shelf (Aug 2026). The reusable mechanism for smooth, frame-rate-independent state transitions between two scene layouts (shelf → detail / overview → inspect / lobby → cabinet).

## Core building blocks (all standard Three.js)

1. **`damp()` = exponential smoothing** — `THREE.MathUtils.damp(current, target, lambda, delta)`. Frame-rate independent spring toward a target. Use for camera/motion follow (never per-frame lerp with a fixed ratio — that breaks at different framerates).

2. **`smoothstep(v)` = cubic ease** — `v*v*(3-2*v)`. Deterministic ease-in-out for 0→1 progress. Use when you need exact, repeatable animation, not spring physics.

3. **Mode state machine** — `hero → opening → detail → closing → hero`. A single `mode` string guards every interaction. `controls.enabled = mode === "detail"` — interactions only work in the right state.

4. **Normalized transition time** — `transitionTime = min(1, transitionTime + delta / DURATION)`; then apply pose as a pure function `applyOpeningPose(transitionTime)` / `applyClosingPose(transitionTime)`. When `transitionTime >= 1`, call `finishOpening()/finishClosing()` to snap the state machine.

## Why it prevents the "last-frame jump"

- Camera, book, shelf, and view-offset transforms **share the same deterministic eased timeline**.
- Because progress is driven by accumulated delta, not by target proximity, two objects reparented between scene graphs never diverge — they hit exact endpoints at the same frame.
- This is the key fix for reparenting a selected object between an overview and a detail scene without a visible snap.

## The 3 constants that make it tunable

```js
const damp = THREE.MathUtils.damp;          // follow motion
const lerp = THREE.MathUtils.lerp;          // linear mix
const smoothstep = (v) => v * v * (3 - 2 * v); // 0→1 cubic ease
const DETAIL_TRANSITION_DURATION = 0.92;    // s
const SHELF_TRANSITION_DURATION = 0.92;     // s
```

## Reuse in GenTech arcade

Apply this exact pattern to:
- **Agent Warfare / Cesium Flight Sim** — overview map → inspect a unit/aircraft, with exact deterministic camera endpoints.
- **King's Gambit** — board overview → piece inspection / move preview.
- **Arcade lobby** — cabinet shelf → enter a game (already has the navigation; this gives buttery deterministic motion).

Rule: every interaction that changes scene layout should go through `mode` + normalized `transitionTime` + `damp`/`smoothstep`, never raw per-frame position writes.
