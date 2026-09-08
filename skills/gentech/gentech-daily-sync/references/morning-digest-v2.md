# Morning Digest v2.0 — Format Specification

## Purpose
Cross-group conversation synthesis delivered to HQ (`telegram:-1003863540828`) at 7:00 AM ET daily. Replaces passive summaries with active idea incubation.

## Workflow

### 1. Conversation Retrieval
- Use `session_search` with yesterday's date to pull conversations from ALL groups (HQ, Strategies, Labs, Entertainment)
- Query broadly: `"May 15 2026 HQ conversations"` or `"2026-05-15 conversation telegram"`
- **⚠️ `session_search` may return sparse results** for quiet days (mostly cron jobs, few user conversations). When this happens, use this **three-tier fallback** to reconstruct the day:
  1. **Archived today-context** — Read `11-Mess Hall/archive/2026-MM/W##-YYYY-MM-DD/today-context.md` and `rotation-log-*.md`. These contain the full picture of active discussions, action items, deadlines, and vault health from the nightly housekeeping cron. This is the fastest and most structured fallback.
  2. **Vault sweep reports** — Read `11-Mess Hall/vault-audits/vault-sweep-YYYY-MM-DD.md` for the day's audit findings.
  3. **Contest scans** — Read `02-Labs/Contest-Scans/summary_YYYY-MM-DD.md` for opportunity scanner output.
- **If all vault fallbacks are empty**, fall back to **direct session file scanning**:
  ```python
  import json, glob
  for f in sorted(glob.glob('/root/.hermes/profiles/gentech/sessions/YYYYMMDD_*.jsonl')):
      user_msgs = []
      with open(f) as fh:
          for line in fh:
              try:
                  m = json.loads(line)
                  if m.get('role') == 'user' and m.get('content'):
                      text = m['content'][:200]
                      if text.strip(): user_msgs.append(text.strip())
              except: pass
      if user_msgs:
          print(f'{f.split("/")[-1]}: {" | ".join(user_msgs[:3])}')
  ```
  This is slower but exhaustive — session files are the ground truth.
- If `session_search` returns incomplete results, read `_cap.md` fallback from `08-Daily-Digest/YYYY-MM/_cap.md`

### 2. Digest Structure
```markdown
# Morning Digest — YYYY-MM-DD

## HQ
- Key decisions
- Action items
- Unresolved questions

## Strategies
- DeFi/LP updates
- Market analysis

## Labs
- Build progress
- Technical blockers

## Entertainment
- Content pipeline
- Social media

## Brainstorm & Next Steps (Idea Incubator)
- Synthesize connections between yesterday's topics
- 2-3 specific questions or prompts for Jordan
- Suggest next steps for active ideas
```

### 3. Vault Save
- Path: `08-Daily-Digest/YYYY-MM/YYYY-MM-DD.md`
- Create month folder if missing: `mkdir -p 08-Daily-Digest/YYYY-MM`
- Include full conversation details, not just summary

### 4. Context Cap Rule
- When context approaches limits late in the day (~11:30 AM-12:00 PM UTC), save `_cap.md` to `08-Daily-Digest/YYYY-MM/`
- Content: brief summary of day's conversations, key ideas, decisions made
- This becomes the fallback if `session_search` returns incomplete results

## Idea Incubator Guidelines
- Actively synthesize, don't just summarize
- Connect topics across groups (e.g., "The privacy discussion in HQ overlaps with the Ghost Mode engine in Labs")
- Prompt with specific next steps: "Want me to draft the architecture?" "Should we check the vault for existing work on this?"
- Treat Green Room / Mess Hall as consolidated idea space
- Reference existing vault files when relevant

## Cron Configuration
- Schedule: `0 11 * * *` (11:00 UTC = 7:00 AM ET)
- Delivery: `telegram:-1003863540828` (HQ)
- Skills loaded: `defi-lp-monitoring`, `defi-lfj-monitoring`, `hackathon`