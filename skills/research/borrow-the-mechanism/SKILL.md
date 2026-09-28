---
name: borrow-the-mechanism
description: Jordan's preferred analytical frame for evaluating reference repos/links he shares — extract the mechanism, map against our stack, verify it runs, and reject the tool while adopting the idea. "Eat the meat, spit out the bones."
version: 1.0.0
author: Gentech
license: MIT
tags: [research, evaluation, github, reference-repo, mechanism-analysis, a2a]
---

# Borrow-the-Mechanism Analysis

Jordan's preferred frame for any reference repo/link he shares: **do NOT adopt the tool wholesale — extract the mechanism(s) that benefit us, wire them into our own stack, and reject the rest.** He stated it plainly (Aug 3, 2026) and it recurred across three links the same session (LoopX, awesome-llm-apps, kroger-mcp). He endorsed it explicitly: *"we can take different philosophies that benefit us and add them to the stack even if small."*

End every evaluation with a clear "borrow vs spit out" verdict — not a generic thumbs-up/down.

## The Frame — 5 steps

1. **Pull the repo** — GitHub API metadata + README, or clone to `/tmp` / `/root/repos/` for a real look (depth-1 clone is fine).
2. **Identify the core mechanisms** — what primitives does it actually implement? Name them concretely (e.g. "delegation scope narrowing", "trust scoring", "quota-aware should-run", "evidence lineage").
3. **Map each mechanism against our stack** — a table is clearest: `| primitive | we already have | borrow? |`. Mark `✅ already have` vs `🔴 real gap` vs `🟡 partial`.
4. **Verify it actually runs** — don't just read it. If self-contained, run it (`python3 file.py` or the repo's run command) to confirm before calling it real. A repo that "reads well but doesn't run" is a red flag. For a *skill/prompt* repo (agents, personas, curricula) "runs" means read the operational file end to end — the SKILL.md or system prompt is the artifact, and the enforcement text inside it is where the mechanism lives.
5. **Cross-check the math / invariants independently** — for any code that computes numbers (finance, risk, rates, percentages, APR, runway, PnL), **re-derive the formula from the docstrings and sweep it against the shipped code with your own probe.** A green test suite is only evidence that the test author believed the same thing; a randomized invariant sweep is evidence the code actually conserves the property. Report the number of cases and any mismatches explicitly. A mismatch is a `100×` unit discrepancy more often than a sign error, so check units first.
5. **Check whether it's really a product for us, not just a tool** — a shared artifact with our exact feature can be a **competitor's implementation or a customer's requirement list** rather than a build candidate. Name which one before assigning work.
5. **Borrow / spit out verdict** — be explicit:
   - **BORROW (the meat):** the 1-3 mechanisms worth taking into our design. Name each + where it wires in (skill, queue item, module).
   - **SPIT OUT (the bones):** the tool as a dependency, licensing constraints, wrong stack, corporate-owned control plane, non-applicable projections.

## Scope every benchmark number to the fixture that produced it

A reference repo that publishes an accuracy figure is publishing **a measurement on the author's
fixture, with the delta the author chose.** That is useful evidence and it is not our number.

- **Absorb the apparatus, re-measure the figure.** Take the mechanism; run it against **our**
  fixture before the number is ever repeated to a user or a customer. Quote it only as
  "their benchmark, on their contest" — never as a capability we can promise.
- **A published before/after delta is the most borrowable thing in the repo.** Vendors usually
  print only the after number. A repo that prints the weak version *beside* the strong one is
  handing over an honesty apparatus, and that apparatus is often worth more than the feature.
- **Name what the mechanism must NOT be allowed to mean, in the same breath as what it is for.**
  An absorbed capability drifts into a claim within days unless the boundary is written down with
  it. State the limit at absorption time, not at the first overreach.

## Classify the source by its sales motion before adopting its backlog

Before treating any list, curriculum, or backlog as a build order, ask **who is selling what to
whom.** The same item can be a product for us and a chore for someone else.

- A list written from the **consultancy / deploy-into-their-stack** side is frequently a
  **buyer's requirements document** — it describes the thing *we* sell. Read it as demand
  evidence, not as our roadmap.
- Enterprise-machinery items (SSO/SAML/SCIM connectors, HITL approval gates for chat tools,
  legacy-UI computer-use, compliance proxies, SOW pipelines) are **bones** for a company that has
  no enterprise contract to unblock. They look professional, which is exactly why they get
  mistaken for priorities.
- Apply the DECIDES-ALONE TEST to the whole list: does it make us better at deciding and acting on
  our own, or does it add deliberation and hand decisions back? A backlog of professional-looking
  deliberation is a bone however well-written it is.

**Pitfall: re-reading a list is not the same as refining it.** A second pass over the same source
that yields a *different* set of "meat" items means the first pass was associative, not
principled. Pick the frame (does it make us decide alone? what do we already sell?) and let it
determine the keep-list, so two passes agree.

**Pitfall: unit inconsistency across sibling modules is the most dangerous kind of correctness.**
Two functions in the same org, both named `apr`, returning a FRACTION in one module and a
PERCENT in the other is not a test failure — it is a semantic failure. Always compare units
across adjacent outputs before calling the math verified, and state the unit explicitly when
reporting a number.

## Key pitfalls
- **Empty allow-list must mean DENY, never ALLOW.** Caught a real security bug in awesome-llm-apps' trust layer: an empty `allowed_actions` set originally read as "all allowed" (least-privilege hole). In ANY delegation/permission logic we build, an empty allow-list must deny.
- **Borrowing a mechanism ≠ adopting the dependency.** Often the right move is porting a ~200-line core into our own design (LoopX state kernel, trust-layer core), not installing their tool. Keeps us independent and avoids building around corporate-owned or churn-heavy projects.
- **Verify the tool actually solves the problem before recommending a key/cost.** e.g. kroger-mcp still needed a Kroger API key — it wrapped the blocker, didn't remove it. Don't oversell a repo with an external credential gate the user can't pass.
- **Re-anchor on the real problem.** When Jordan clarifies the true goal (e.g. "the Cookbook is about substitutions, not grocery prices"), re-evaluate against the real problem, not the initial framing.
- **When you correct your own finding, say so in the report — and update the skill, not just the log.** A wrong suspicion (e.g. "their CI is red") that you later disprove should be **withdrawn publicly** and the corrected conclusion stated. Do not leave the wrong claim in the transcript for the next agent to read as fact.

## Output shape Jordan expects
Lead with the verdict, not the architecture explainer:
```
**{Project}** — {stars/license/stack}
**The mechanism worth borrowing:** {one-liner}
**Where it wires into our stack:** {skill / queue item / module}
**Verdict:** Borrow the {mechanism}; spit out the {tool/dependency}
```

## Where the borrows land
- Mechanisms worth adding to our design → `agent-handoff-enforcement`, `considerations.md`, build queue, or a new spec under `09-Green Room/specs/`.
- Deep-dive analysis notes → `09-Green Room/specs/{topic}-deep-dive.md` (or `03-Projects/Research/`).
- Vault changes should follow the wiring: one link can trigger multiple vault files (spec + queue item + skill patch).

## Support references
- `references/vault-routing-file.md` — how to route vault writes efficiently before scanning.
- `references/port-and-verify-mocked-backend.md` — porting a mechanism and testing it against a mocked backend without API cost.
- `references/independent-math-verification.md` — when the repo computes numbers: re-derive, sweep, and check units across modules.

## Working examples (Aug 3, 2026)
- **LoopX** (state kernel / control plane, 680★) → borrowed: explicit user gates, quota-aware `should-run`, evidence-lineage stubs; rejected: the tool + Feishu projection + Bytedance-adjacent control plane. Wired into `agent-handoff-enforcement` skill; spec at `09-Green Room/specs/loopx-a2a-handoff-borrow.md`.
- **awesome-llm-apps multi-agent trust layer** (Apache-2.0, 130K★, verified running) → borrowed: delegation-scope narrowing + trust scoring; cloned to `/root/repos/`; deep-dive at `09-Green Room/specs/a2a-trust-layer-deep-dive.md`.
- **kroger-mcp** (66★) → evaluated, found it still needs the Kroger API key the user can't get → pivoted to the real Cookbook substitution problem (no external keys needed).
