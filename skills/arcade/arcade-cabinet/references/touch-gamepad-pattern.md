# Touch Controls & Gamepad Pattern

## Overview

Adding mobile touch controls and Bluetooth gamepad support to Three.js arcade cabinet games. The pattern preserves the existing keyboard/mouse input while layering on touch and controller support.

## Architecture

The game's `Input` class (`src/core/input.js`) is the central input aggregator. Touch controls and gamepad polling both feed into this system by dispatching synthetic events.

## Gamepad Button Mapping

Standard Xbox controller layout mapped to game actions:

| Button | Index | Action | Implementation |
|--------|-------|--------|----------------|
| A | 0 | Jump | `_gpAction('jump')` |
| B | 1 | Crouch | `_gpAction('crouch')` |
| X | 2 | Reload | `_gpActionPressed('reload')` (press, not hold) |
| Y | 3 | Swap weapon | `_gpActionPressed('swapWeapon')` |
| LB | 4 | Lean left | `_gpAction('leanLeft')` |
| RB | 5 | Lean right | `_gpAction('leanRight')` |
| LT | Axis 2 | ADS (aim down sights) | `_gpAction('_ads')` — axis ≥ 0.3 threshold |
| RT | Axis 3 | Fire | `_gpAction('_fire')` — axis ≥ 0.3 threshold |
| L3 | 10 | Sprint | `_gpAction('sprint')` — threshold 0.5 (push-to-sprint) |
| R3 | 11 | Melee | `_gpAction('melee')` |
| Back | 8 | (unused) | — |
| Start | 9 | Pause | `_gpAction('pause')` |

**Key implementation details:**
- Triggers (LT/RT) are `axes[2]` and `axes[3]`, not buttons. They return float 0-1 when pulled.
- Button state tracking uses a bitmask (`_prevGpBtns`) and `reduce` to track transitions between frames.
- `_gpAction()` checks both button presses and axis thresholds.
- `_gpActionPressed()` only returns true on the frame the button was first pressed (not held).

## Touch Controls Overlay

### When to Activate

Only on touch-capable, small-screen devices:
```js
const isMobile = () =>
  ('ontouchstart' in window || navigator.maxTouchPoints > 0) &&
  (window.innerWidth < 1024 || window.innerHeight < 768);
```

### Layout

```
┌──────────────────────────┐
│       [JUMP]  [RELOAD]   │  ← top-right
│                          │
│  ┌───┐          ┌───┐    │
│  │ M │  LOOK    │ F │    │
│  │ O │  (drag   │ I │    │
│  │ V │  right   │ R │    │
│  │ E │  half)   │ E │    │
│  └───┘          └───┘    │
│  [CROUCH] [SPRINT] [ADS] │  ← bottom
└──────────────────────────┘
```

### Components

**Virtual Joystick** (left half):
- On `touchstart` in left 40% of screen → show joystick at touch point
- On `touchmove` → calculate direction/distance from origin, map to -1..1
- Clamp to unit circle (prevent faster diagonals)
- Synthesize `KeyW/A/S/D` keyboard events based on direction
- On `touchend` → hide joystick, release all keys

**Look Drag** (right half):
- On `touchstart` in right 60% (not over buttons) → record origin
- On `touchmove` → calculate delta from previous position
- Dispatch synthetic `MouseEvent('mousemove', { movementX, movementY })`
- Polled at ~60fps via `setInterval(16ms)` to flush accumulated deltas

**Action Buttons:**
- DOM elements with `position: fixed`, circular, touch/mouse event handlers
- Each button dispatches `KeyboardEvent` or `MouseEvent` on touch down/up
- Fire (pink, bottom-right, 80px) → `Mouse0` down/up
- ADS (blue, above fire, 52px) → `Mouse2` down/up
- Jump (cyan, top-right, 56px) → `Space` down/up
- Crouch (gray, bottom-left, 56px) → `ControlLeft` down/up
- Sprint (orange, above crouch, 48px) → `ShiftLeft` down/up
- Reload (gray, top, 44px) → `KeyR` down/up

### Initialization Order (Critical)

Touch controls must init BEFORE `engine.start()`:
```js
const touchControls = new TouchControls(engine.input);
touchControls.init();  // Creates DOM overlay immediately
window.__TOUCH__ = touchControls;
engine.start();        // Engine may fail on mobile — overlay is already visible
```

### Caveats

- **Button overlap detection:** The look drag touch handler checks if the touch point overlaps any button's bounding rect. Prevents accidental camera movement when pressing buttons.
- **Continuous key states:** Joystick movement uses `_synthesizeContinuous()` which tracks current key state and only dispatches on transitions. Prevents spamming events every frame.
- **Splash screen:** Show a loading/startup splash before JS loads so mobile users see something immediately:
  ```html
  <div id="mobile-splash" style="position:fixed;inset:0;z-index:9997;...">
    Title + spinner + "grab a controller or use touch"
  </div>
  ```
  JS hides it once loaded: `document.getElementById('mobile-splash')?.style.opacity = '0'`.

## Testing

On desktop: connect a Bluetooth controller, verify all buttons map correctly. Open DevTools → Sensors → toggle touch emulation to test mobile overlay without a real device.

On mobile: visit the arcade URL, verify:
1. Splash screen appears while loading
2. Touch overlay is visible after load
3. Virtual joystick works for movement
4. Look drag works for camera
5. All action buttons respond
6. Bluetooth controller connects and maps correctly
