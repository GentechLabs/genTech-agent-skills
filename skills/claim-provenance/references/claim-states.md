# Claim States — how to label what you are reporting

A reader must be able to classify every claim in your report without asking you. Use one of these
four labels, and use the words, not a tone of voice.

| State | Meaning | Label to write |
|---|---|---|
| **Verified by me** | You ran the instrument in this session and read the result back | Name the command/endpoint in the same sentence + the value |
| **Inherited** | A peer or an earlier note reported it; you did not re-run it | "reported by <source>, not re-measured here" |
| **Superseded** | It was true at a named revision; the artifact has since changed | "<hash> @ <commit> — superseded by <new hash> @ <commit>" |
| **Unverifiable** | The digests/methods are not comparable, or the source cannot be reached | "unverifiable — <why>", never "reopened", "edited", or "missing" |

## Why the four, and not just "true / false"

- **Inherited** is the one that silently propagates errors. A number you did not measure but repeat
  in a confident voice arrives at a third party wearing your authority. Re-run it before building on
  it, or label it.
- **Superseded** protects a correct report from looking wrong. Two seats can each be right and still
  disagree, purely because the artifact moved between their measurements. Without the revision, that
  disagreement reads as a defect and costs a full round to disprove.
- **Unverifiable** is the honest answer when two methods produce incomparable results. Reporting it
  as an edit or a reopen **accuses a peer of changing a file they never touched** — which is a
  stronger and more damaging claim than "I could not check this".

## Rules that apply to all four

- **Retraction is a state, not a deletion.** Strike the false claim where it lives, mark the date,
  and state the measured value beside it. An artefact that describes the old state keeps being
  believed long after the fix.
- **Never let a state be inferred from sentence position.** "The key is valid (HTTP 200). Only 14%
  remains." reads as two measurements. If only one was measured, say which.
- **Publish the label with the claim, in the same artifact.** A correction filed somewhere else is
  not a correction — a reader who finds the original is never told.
