# Professional Dashboard Preview Pattern

Use when building a preview for a management surface (DeFi treasury, portfolio, agent
operations) where Jordan wants it to "look professional" rather than just display data.
The deliverable is a product-shaped HTML page, not a dashboard.

## Surface distinction

| Surface | User job | Example |
|---|---|---|
| Chat (Telegram) | Talk to the agent, ask questions, get alerts | "Rebalance me now" |
| Hub / dashboard | Manage the system with buttons, inspect state, verify trust | Add funds, withdraw, pause machine, read last chain sync |

If other people will use the product, the hub is the product face. Telegram becomes the
support channel. Build them as separate surfaces with separate jobs.

## Layout checklist

1. **Sticky header**  
   Logo + nav tabs (Overview, Position, Activity, Vault), tenant/user toggle, wallet chip,
   and a live status dot.
2. **Capital hero**  
   Large balance, deployed/idle split, efficiency/badge row, and a progress bar that
   indicates utilization.
3. **Action row**  
   Buttons the user expects: Add funds, Rebalance, Withdraw, Pause the machine. If the
   wiring is not implemented, mark them clearly as `preview · actions are not wired` so
   the UI does not imply functionality that does not exist.
4. **Metric grid**  
   2×2 on mobile, 4 columns on desktop, with subtle vertical dividers.
5. **Earnings comparison**  
   Show the book's yield vs a familiar benchmark: "Same capital as an X% staker" +
   "This book's rate" APR.
6. **Machine-state panel**  
   Regime, resolved shape, transition state, lean, next check, and a one-sentence
   explanation of why the current shape was chosen.
7. **Chart as data**  
   A chart must carry its own scale: max-bin label, price bounds, spot-position ruler,
   and a legend whose order matches the visual order.
8. **Data-trust strip**  
   Last-read timestamp, data source, and a ledger-vs-shape delta so the user can verify
   the numbers without trusting the agent.

## Cost model for K3/T3 design passes

Use this when Jordan asks how much a professional redesign costs.

- Kimi K3 (T3) is roughly **$15 per million output tokens** (check the current routing
  table for exact rate).
- One full front-end redesign pass is roughly **15–20k output tokens** = **~$0.25–0.35**.
- With revision passes and a couple of discarded directions, total is typically **$2–5**.
- A cheaper seat model can produce the same artifact; K3 buys taste and iteration volume,
  not correctness.

When a user says "around $5", confirm that aligns with the real rate rather than quoting
a different number. If the wallet balance is known, state it so the user can decide
whether to fund the K3 route or accept the current model's output.

## Responsive QA pitfall: headless Chrome viewport floor

When verifying mobile layouts with `google-chrome --headless --screenshot`, requested
window widths below ~500px may produce a screenshot laid out at ~500px and then cropped
to the requested width. This creates a false "right-edge overflow" defect.

Before chasing clipping bugs, run a control test:
```html
<!DOCTYPE html>
<html><head><meta name="viewport" content="width=device-width,initial-scale=1">
<style>body{background:#00ff00}@media(max-width:620px){body{background:#ff0000}}
#w{font:40px monospace}</style></head>
<body><div id="w">X</div>
<script>document.getElementById('w').textContent='vw='+window.innerWidth;</script>
</body></html>
```

If the screenshot shows a red background and `vw=500` for a 390px requested width, the
instrument is cropping the image. The page itself is not broken.

## Verification sequence

1. Build the HTML in the canonical repo (per `web-deployment` skill Step 1).
2. Copy to `/var/www/gentechlabs/`, `chmod 644`.
3. Verify HTTP 200 on the live URL.
4. Screenshot at desktop width (~1100px) and at the headless floor (~500px).
5. Add a control test if the mobile screenshot shows clipping.
6. Send the link in its own short message, not buried in a long status recap.
