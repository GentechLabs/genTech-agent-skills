# KeeperHub Submission: Public Repo + Demo Script Pattern (Aug 12, 2026)

When the onchain build is verified and the hackathon deadline looms, the submission
needs TWO deliverables beyond the working transaction:

1. **A public GitHub repo judges can see** (the code living only in the private vault
   is invisible to judging).
2. **A demo video script** that walks judges through the live workflow + real tx.

## Public repo — critical gap

The submission code often lives only inside the private vault git (`/root/vaults/gentech`).
Judges can't see it. Create a clean **public** repo and push the submission there.

**Use the Gentech-Labs org, not Jordan's flagged personal account** (ProtoJay4789 is
rate-limited/flagged from over-updating). Org repo creation is REST, not GraphQL — so it
works even when GraphQL quota is exhausted (0 remaining):

```bash
gh api -X POST "orgs/Gentech-Labs/repos" \
  -f "name=keeperhub-yield-guard" \
  -F "private=false" \
  -f "description=..." \
  --jq '.html_url'
```

**Repo contents for a hackathon submission:**
- `LICENSE` — Apache 2.0 at repo root. **The #1 thing judges check** (a missing license
  auto-fails many rubrics). Verify it serves 200 on raw.githubusercontent after push.
- `README.md` — the pitch.
- The core source file(s).
- `docs/WORKFLOW.md` — the live workflow reference (ID, flow diagram, steps).
- `.env.example` — env template (never real keys).

**Push + verify:**
```bash
git init -b main && git add -A
git -c user.email="gentech@gentechlabs.net" -c user.name="GenTech Labs" commit -m "..."
git remote add origin https://github.com/Gentech-Labs/<repo>.git
git push -u origin main
# verify each file is live:
curl -s -o /dev/null -w "%{http_code}" \
  "https://raw.githubusercontent.com/Gentech-Labs/<repo>/main/LICENSE"
```

## Demo video script

Use the 4-part structure (Intro → Mechanism → It's Real → Close) built around the
**actual live workflow** and **real test execution ID** — judges see working infra, not a
mockup. 90-120s, film it yourself.

- Intro: hook — autonomous agent protecting a live DeFi position.
- Mechanism: read → check → execute loop (the `execute_check_and_execute` shape).
- It's real: show the KeeperHub run view + paste the real execution/tx ID.
- Close: open-source, link the public repo.

## Tracker / action-list sync

- Update the KeeperHub entry in the vault action list: mark repo URL + demo status.
- Push the demo script to the vault so it's on the user's phone to film.
- The one thing left for the user: film the video + (optionally) open a small position
  so the guard fires a real rebalance tx hash to paste.
