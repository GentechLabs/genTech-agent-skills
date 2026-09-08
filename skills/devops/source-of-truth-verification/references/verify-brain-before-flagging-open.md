# Verify the Vault Brain Before Flagging an Opportunity as "Open" (Aug 26, 2026)

## The recurring correction (Jordan)
A scanner / Personal Assistant repeatedly flags a grant/hackathon as **"apply now"** or a
**blocker** when it was **already applied / submitted / interviewed / resolved** long ago.
Jordan (Aug 26): *"the personal assistant has to catch these things by confirming with info
in the brain. Already applied for GOAT network, and Circle development grant."* This erodes
trust in every flag and wastes his time.

## The guardrail
Before ANY cron or agent flags an opportunity as open/apply-now/needs-signup — or surfaces a
"blocker" involving money/keys/wallets — search the vault brain for that name first:

```bash
grep -rn -i "<opportunity-or-program-name>" /root/vaults/gentech/ \
  --include="*.md" -l | grep -E "09-Green Room|HQ/jordan-queue|01-HANDOFFS|10-Labs"
```

Apply the verdict:
- **submitted / applied / registered / interviewed / in-the-pipe / waiting-to-hear-back**
  → ALREADY HANDLED. Do NOT flag as open/apply-now. At most "already applied — awaiting
  decision" if a status reminder is genuinely useful.
- **resolved / closed / taking-the-L / dropped / do-not-re-flag** → DEAD. NEVER re-surface.
- **no record found** → only THEN treat as genuinely new/open.

## Known already-applied (do NOT re-flag as open)
Circle Developer Grant (circle.questbook.app, Jul 2026), GOAT Network AI Builder Grant
(applied + interviewed), TheDAO Security Fund, SPC Founder Fellowship, Superteam Agentic
Engineering, 0G Bridge Wave 3, BUIDL CTC, CALL-E, Arc Programmable Money.

## Known resolved/closed (do NOT re-flag)
payTo `0xF9dc…734` stranded $33.63 (Jordan took the L Aug 22 — keyless wallet), Gemini XPRIZE
(dropped), Octant Epoch 13 (skipped), Shutter Melee 3 (skipped).

## Where it must be embedded
The guardrail belongs in the **PA prompt** AND every collector feeding it (Opportunity Scanner,
Grant Deadline Tracker). The PA/scanner is a *consumer of the brain's state*, not an independent
source of truth about what's still open. A stale flag on an already-handled item silently
undermines all subsequent reports.

## Also: verify "shipped/resolved" claims too
Same principle as source-of-truth-verification Part 2 — a queue/handoff claiming an item is
"resolved" or a wallet is "keyed" is an assertion. Grep the live config (`.env`, `server.py`
payTo fallback, wallet keypair files) before trusting it. E.g. the Solana treasury wallet was
*recorded* but never wired (`solana_homebase.py` reports `no_keypair`) — recorded ≠ active.
