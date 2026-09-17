# AKINDO Buildathon Registration — Verified Flow (Aug 2026)

AKINDO (akindo.io) is the "world's first Buildathon platform" running WaveHack
buildathons (0G, Midnight, SoSoValue, IoTeX, Fhenix, etc.). Registering a team
is a browser task — the app is JS-rendered and email-gated.

## Key facts
- **Sign-in is email-only** (no password). Enter email → AKINDO emails a
  verification code → enter code → you're in. No OAuth, no wallet connect.
- **Listing page is JS-rendered.** `app.akindo.io/wave-hacks` returns a shell
  via curl/web_extract (no card data). Use `browser_navigate` + snapshot to see
  the buildathon cards (name, grant total, wave, deadline, builder count).
- **Registration URL pattern:** `app.akindo.io/wave-hacks/{id}` (e.g. 0G Wave 3
  = `Z4MlX4vreI72ol6pd`, Midnight = `jaMZjqPOBsLXvjdG`). Grab the id by clicking
  a card and reading `window.location.href`.
- **One account covers all buildathons** — sign in once, join any wave-hack.

## Verified sign-in steps (browser)
1. `browser_navigate` to `https://app.akindo.io/login`
2. `browser_type` the email into the `input[name=email]` field, then click
   **Continue** (button text "Continue").
3. Page shows **Verification** — "We have sent a verification code to your email
   address." The code input is `input[name=code]`.
4. `browser_type` the code, click **Sign in**.

## Pitfalls (learned the hard way)
- **React form quirk:** setting `input.value` via `browser_console` (with
  `dispatchEvent(new Event('input'))`) does NOT register with React — the field
  shows the text but the form still reports "code is required" / "email is
  required". You MUST use the `browser_type` tool (real keystrokes) to fill
  AKINDO fields. Same for the email field.
- **Code invalidation:** if the page resets (e.g. you navigate away and back to
  `/login`, or the session drops) and you re-enter the email, AKINDO sends a
  FRESH verification code and the old one is invalidated. If you get "Invalid
  code", ask the user for the newest code from their inbox — do not retry the
  stale one.
- **Code is single-use and time-limited** — enter it promptly.
- **The agent cannot read the user's email inbox.** The verification code is the
  one step that requires the user. Ask for it explicitly and wait.

## After sign-in
- Join the target buildathon from its wave-hack page (JOIN button).
- AKINDO accepts both new and existing projects; you can join any wave and
  resubmit improved versions across waves. Grants paid on-chain, no equity/IP.
