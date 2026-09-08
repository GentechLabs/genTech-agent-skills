# AKINDO Registration Flow — login, verification code, account setup, join buildathon

AKINDO (app.akindo.io) is the WaveHack platform for the 0G Bridge, Midnight Buildathon, and
other agent-economy buildathons. Every buildathon requires an AKINDO account first. Full flow
verified Aug 13, 2026 (joined 0G Bridge Wave 3 as user `gentech`, code 937985).

## Login flow (email + one-time code)

1. Go to `https://app.akindo.io/login`. Enter the email in the `Email address` box → click `Continue`.
2. AKINDO emails a **one-time verification code**.
3. A `Verification` screen appears with a `Sign in` button. Enter the code → click `Sign in` (or press Enter).

### ⚠️ THE code pitfall (critical — cost two attempts)
- **Re-entering the email on a page reset sends a FRESH code and INVALIDATES the prior one.**
- If the page reloads/resets after you already got a code, the old code is dead. Do NOT reuse it — ask the user for the newest code.
- If a code fails ("Invalid code"), it was almost certainly invalidated by a re-submit. Ask for a fresh one.
- The `Sign in` button may briefly show as `disabled` right after typing the code — it enables while validating; press Enter to submit.

## Account setup (first login — mandatory)

After the code validates, AKINDO requires account setup before you can join anything:
- **Icon** (required — form shows `This field is required` if skipped)
- **User ID** (pick something like `gentech`)
- **Terms checkbox** (must be checked)

### The icon-upload workaround (hidden file input — React quirk)
The icon is a **hidden `<input type="file" accept="image/png, image/jpeg">`** (className `hidden`).
The `<LabelText>` click opens a native file picker the agent CANNOT drive. Workaround:
1. Generate an icon via `image_generate` (any square brand mark), download it, and get its URL.
2. In `browser_console`, inject the file into the hidden input via `DataTransfer`:
```js
(async () => {
  const input = document.querySelector('input[type="file"]');
  const resp = await fetch('<image-url>');           // must be fetch-able from the page
  const blob = await resp.blob();
  const file = new File([blob], 'icon.png', { type: 'image/png' });
  const dt = new DataTransfer(); dt.items.add(file);
  input.files = dt.files;
  input.dispatchEvent(new Event('change', { bubbles: true }));
})();
```
3. This clears the `This field is required` error → click `Continue`.
- After Continue, a "One tap to front-run" / "Follow AKINDO on X" welcome modal appears — dismiss with `Next`.

## Join a buildathon

- Navigate to the buildathon URL (e.g. `https://app.akindo.io/wave-hacks/<id>`).
- Scroll to the bottom → click **`Join Buildathon`**.
- **Verify success:** the `Join Buildathon` button disappears from the page. (A `browser_console` check `document.querySelectorAll('button')` filtered for `/join|register/i` should return only `Join a team`.)
- The user ID appears in the top-right nav (`button "gentech"` + avatar).

## Notes
- `app.akindo.io/dashboard` 404s — don't use it as a post-login check; the nav user button is the sign of a successful session.
- Account email for Jordan: `jordanjones0902@gmail.com`. Account user ID: `gentech`.
- AKINDO has both `/wave-hacks` (buildathons) and `/hackathons` in the top nav.
- Submission requires a GitHub repo + product entry; some builders reported a "New Product" button not appearing — if that happens, the product page may need a fresh GitHub connect before submission.
- **Hidden-file-input injection via `DataTransfer` + `fetch` → `File` → dispatch `change` is a general technique** for any React form that hides its `<input type="file">` behind a `<LabelText>`/camera-button (AKINDO icon, avatar uploads, etc.). The fetch must resolve from the page's origin context (serve the image over HTTP or use a public URL the page can fetch).
