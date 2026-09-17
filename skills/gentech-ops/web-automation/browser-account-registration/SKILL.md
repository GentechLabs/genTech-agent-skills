---
name: browser-account-registration
description: "Register accounts on JS-rendered platforms via email codes."
tags: [registration, browser, email-code, signup, akindo, hackathon]
trigger: "When the user asks to register/sign up for an account on a JS-rendered web platform (buildathon dashboards like AKINDO, hackathon portals, marketplace signups) that uses email-verification-code auth, or when a listing page returns no data via curl/web_extract."
version: 1.0.0
author: Gentech
---

# Browser Account Registration (Email-Code Platforms)

Registering accounts on modern web platforms that use **email-verification-code
sign-in** (no password, no OAuth). Proven on AKINDO (akindo.io) Aug 2026, but the
pattern generalizes to any JS-rendered dashboard with email-code auth.

## When to use
- User asks "are you able to register us / sign us up" on a buildathon or
  marketplace platform.
- A listing/registration page returns empty content via `web_extract` or curl —
  it's JS-rendered and needs the browser.

## Core pattern
1. **Listing pages are JS-rendered.** If `web_extract`/curl returns a shell with
   no card data, use `browser_navigate` + `browser_snapshot` to see the actual
   content (buildathon cards: name, grant, wave, deadline, builder count).
2. **Grab the registration URL** by clicking a card and reading
   `window.location.href` via `browser_console`. URL pattern is usually
   `{platform}/wave-hacks/{id}` or similar.
3. **Sign-in is email-only.** Enter the user's email → platform emails a
   verification code → enter code → done. No password, no OAuth, no wallet.
4. **The verification code is the ONE step the agent cannot do solo** — the
   agent cannot read the user's email inbox. Ask the user for the code
   explicitly and wait for it.

## Verified sign-in steps (AKINDO example)
1. `browser_navigate` to `https://app.akindo.io/login`
2. `browser_type` the email into `input[name=email]`, click **Continue**.
3. Page shows **Verification** — "We have sent a verification code to your email
   address." Code input is `input[name=code]`.
4. `browser_type` the code, click **Sign in**.

## Pitfalls (learned the hard way)
- **React form quirk — MUST use `browser_type`, not console value-setting.**
  Setting `input.value` via `browser_console` (even with
  `dispatchEvent(new Event('input'))`) does NOT register with React. The field
  shows the text but the form still reports "code is required" / "email is
  required". Real keystrokes via `browser_type` are required. This applies to
  the email field too.
- **Code invalidation on page reset.** If the page resets (navigate away and
  back, or session drops) and you re-enter the email, the platform sends a FRESH
  code and the old one is invalidated. If you get "Invalid code", ask the user
  for the newest code — do not retry the stale one.
- **Codes are single-use and time-limited** — enter promptly once received.
- **Don't burn the user's time with a stale code.** If the flow reset, tell the
  user a fresh code was sent and ask for the newest one.

## After sign-in
- Join the target program from its dashboard (JOIN button).
- Many platforms (AKINDO WaveHack) accept both new and existing projects; you can
  join any wave and resubmit improved versions. Grants paid on-chain, no equity.

## Reference
- `references/akindo-registration-flow.md` — full AKINDO-specific detail
  (URLs, field names, verified steps).
