# Grant/Hackathon Submission — Repo Verification & Tranche Unlock Pitfalls

Session-proven on Aug 10, 2026 (Superteam Earn Agentic Engineering tranche 2 + DataHub Agent Hackathon deadline day).

## 1. The application doc's repo URLs may not match reality

The drafted Superteam application referenced:
- `github.com/ProtoJay4789/x402-gateway` — DOES NOT EXIST publicly
- `github.com/ProtoJay4789/goat-agentkit` — DOES NOT EXIST publicly

The actual, verifiable Solana MVP is **`github.com/ProtoJay4789/agent-economy-solana`** (branch `master`).

**Rule:** Never trust repo URLs written in an original application doc when prepping a submission or a later tranche-unlock form. Live-check every referenced repo and substitute the real, cloneable one before the user pastes.

## 2. The `ProtoJay4789` account 404s on unauthenticated API/raw — even for PUBLIC repos

Unauthenticated checks that return 404 for public repos on this account:
- `curl https://api.github.com/repos/ProtoJay4789/<repo>` → 404
- `curl https://raw.githubusercontent.com/ProtoJay4789/<repo>/main/README.md` → 404
- `curl -L https://github.com/ProtoJay4789` (user page) → 404
- `codeload.github.com/ProtoJay4789/<repo>/zip/...` → 404

Authenticated API (with the PAT) correctly reports `"private": false, "visibility": "public"`.

**Consequence:** Using the unauth API/raw to verify visibility makes you wrongly conclude a public repo is private or missing — which would wrongly flag a submission as disqualified.

**Authoritative check — the clone path (what judges/consumers actually use):**
```bash
GIT_TERMINAL_PROMPT=0 git ls-remote https://github.com/OWNER/REPO 2>/dev/null | grep -q 'refs/heads/' && echo "PUBLIC/cloneable" || echo "NOT FOUND/private"
# definitive proof — fresh shallow clone:
cd /tmp && rm -rf probe && GIT_TERMINAL_PROMPT=0 git clone --depth 1 https://github.com/OWNER/REPO probe && ls probe
```
Treat a repo as public if `git ls-remote`/`clone` succeeds, regardless of API/raw 404s.

## 3. `git ls-remote | grep refs/heads/main` misses `master` branches

Many repos (e.g. `agent-economy-solana`) default to `master`. Grepping `refs/heads/main` returns nothing and falsely reports "not found." Grep `refs/heads/` (any branch) instead (as in the snippet above).

## 4. Superteam "Final Tranche Request" form — what re-collects and what stalls

The tranche-2 form re-collects (does NOT trust your original application):
- Project URL
- GitHub Repo (note: "if private, share with abhishek@gmail.com")
- **AI Subscription Receipt upload ≥ $200** — up to 3 PDFs/PNG, max 15MB each. THIS is the item most likely to stall approval.
- Solana wallet (pre-filled from Earn)
- Optional "Anything Else"

**Flag the receipt before the user finalizes** — don't let them submit with the repo link filled but no receipts attached. Our documented receipt path: VPS $43/mo + OpenCode Go $10/mo + Ollama Cloud $20/mo = $73/mo fixed; 3 months ≈ $219 clears the $200 bar.

**Payout cadence:** approvals Mondays, paid Friday same week. Track in `Treasury/YYYY-MM-DD-<program>-grant.md` (see Pitfall 10 in the main skill).
