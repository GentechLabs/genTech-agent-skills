# Kimi Audit Prompt Pattern (proven Aug 2, 2026 on King's Gambit)

## Prompt skeleton

```
You are auditing a {stack} ({frameworks}) before we ship it. {N} concerns from the operator:

1. {CONCERN_1} - {detail}
2. {CONCERN_2} - {detail}
3. {CONCERN_3} - {detail}
4. {CONCERN_4} - {detail}

Files:
{=== filename === + content for each file, trimmed to ~12K chars each}

Output as a terse action list: for each finding give SEVERITY (HIGH/MED/LOW),
the file+line, the bug, and the exact minimal fix. Be specific enough to
implement directly. Prioritize real bugs over style.
```

## What the model returned (proven output quality)

The King's Gambit run returned implementable fixes, e.g.:
- `response.ok` checks missing in audio preload → silent 404 feeds HTML to
  `decodeAudioData()` — gave the exact try/catch patch.
- Volume API: master-gain `setVolume(0..1)` preserved across mute + unlock() init —
  gave exact `setTargetAtTime` snippet.
- Perf: `bodyFall()` allocating a new AudioBuffer per capture — cache it.
- Branding hooks: exact constants to tint (FACTION_ACCENT, DISSOLVE_EMBER, emissive).

## Two-call split that avoided 524

Call A: audio + settings files (~240 + ~120 lines).
Call B: quality + generated assets + pieces excerpt (~160 + 60 + 130 lines).

Each with max_tokens=6000, browser UA. Call A succeeded; retry of the merged
12K-token prompt 524'd. So: split by concern BEFORE calling, not after a failure.

## Verification pattern after fixes

1. Run the project's own test runner (check package.json `scripts` — `test:unit`
   style commands, not bare `node --test` for .ts files).
2. Run the adjacent test suites that touch the changed predicates (regression).
3. Typecheck the touched files (`npx tsc --noEmit -p <typecheck-config>`).
4. If the repo has a pre-commit gate (lint-staged), let it run on commit — it
   exercises prettier/eslint/quality checks automatically.
