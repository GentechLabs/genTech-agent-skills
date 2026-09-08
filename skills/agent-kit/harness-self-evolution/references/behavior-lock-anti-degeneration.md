# BEHAVIOR LOCK — Hardened Cron Prompt (Anti-Degeneration Pattern)

**Class:** Harness cron agents (Evolution, Critic, Verifier, Gardener) degenerating into greetings on cheap/free models.

**Symptom:** Cron delivers "Sure thing, Jordan. How can I help you today?" instead of executing the evolution loop. Wastes every cycle. The pipeline may still dispatch (execution-loop.sh runs), but the agent's chat response is noise.

**Root cause:** Cheap models (DeepSeek V4 Flash free tier) sometimes ignore elaborate multi-step prompts and fall back to default assistant behavior (greeting). This is a prompt-compliance failure, not a mechanical failure.

## Fix: Hardened Prompt Block

Add this block to EVERY harness cron prompt, immediately after the delivery preamble:

```
## BEHAVIOR LOCK (hard rules — never violate)
- Begin executing STEP 0 immediately. Do NOT greet the user, do NOT ask "how can I help", do NOT introduce yourself.
- Always end your final response with the ACTION REPORT or NO-OP REPORT. Never end with a question, an offer, "let me know", or any prompt back to the user.
- If there is genuinely nothing new to report, respond with exactly "[SILENT]" (nothing else) to suppress delivery.
- COMMIT GUARD: before ending your turn, run `git status --porcelain`. If any file under facts/ or prompts/ is modified/untracked, commit it (git add + git commit). NEVER end a cycle with uncommitted harness files — stranded work recurs when the ledger is left dirty.
- TRUTH GUARD: only claim work actually done. If a file mutation fails (patch returns "Could not find a match"), report it as a blocker — do NOT describe it as complete. Fabricated success claims cause the harness to grade its own homework on phantom fixes.
```

## Verification Checklist

After hardening a cron prompt, fire once and confirm:

1. **No greeting** in the delivered response
2. **Ends with ACTION REPORT or NO-OP REPORT**, not a question or "let me know"
3. `git status --porcelain` in `${HERMES_HOME}/harness` is **clean** post-run (no stranded ledger writes)
4. No file-mutation verifier warnings about failed patches being described as "complete"

## Iterative Hardening (Aug 8-9, 2026)

**Pass 1:** Added "never greet" and "always end with ACTION/NO-OP" rules. Verification run (12:38) eliminated the greeting but still ended with "let me know if you'd like..." (question) and left `execution-log.md` uncommitted.

**Pass 2:** Added COMMIT GUARD (git status before ending, commit if dirty) and TRUTH GUARD (don't claim success on failed patches). The 21:38 cycle on V4 Pro ran clean: no greeting, clean git tree, valid ACTION REPORT.

## Applicable Jobs

- Harness Evolution (22d8ad319fd4)
- Harness Critic (8f71e23cbfd6)
- Harness Verifier (6e771a4bf8a3)
- Harness Gardener (c1fc1e48409a)
