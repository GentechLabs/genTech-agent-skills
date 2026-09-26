---
name: skill-library-maintenance
description: "Use when a SKILL.md hits the size limit or an edit fails."
version: 1.0.0
author: Gentech
tags: [skills, maintenance, editing, limits, fleet, references]
---

# Skill Library Maintenance

Editing, extracting from, and propagating skill files that are at or near the platform size limit.

The platform keeps skills loadable by capping them. **The cap is enforced at WRITE time, not at
write-intent time** — so a skill can absorb lessons for months and only reveal it is full on the day
you need to record the most important one.

## The hard limit: 100,000 CHARACTERS

**It is characters, not bytes.** `len(open(p, encoding='utf-8').read())` — never `wc -c`, which counts
bytes and over-reports by roughly the multibyte density. Measuring in bytes has already produced a
batch of false "uneditable" flags on files that patched fine.

At or over the cap, **every** edit is refused: no corrections, no new lessons, nothing. The skill keeps
loading, so it looks healthy — it is the writes that are dead.

**Sweep the whole fleet, not the seat you happen to be in** — the same skill exists on every seat and
they drift:

```python
import glob
for p in glob.glob('/root/.hermes/profiles/*/skills/**/SKILL.md', recursive=True):
    n = len(open(p, encoding='utf-8', errors='replace').read())
    if n >= 90000:
        print(f'{n:>7}  {p}')       # 90k = act now. 100k = already too late.
```

**Treat 90k as the action threshold, not 100k.** A skill parked at 88–99k is a skill whose *next*
ordinary lesson silently fails to land, and the failure surfaces weeks later as "that fix never got
recorded." Headroom is the feature.

## Procedure — extract to `references/`, never delete

1. **Back up first.** `shutil.copy2(SKILL.md, SKILL.md + '.bak-<what-you-are-doing>')`. Do not skip this
   because the edit is mechanical — mechanical edits are exactly the ones that go wrong silently.
2. **Rank sections by size and extract the largest NARRATIVE ones** — changelogs, incident
   post-mortems, long runbooks, historical session logs. They are *depth*, not *procedure*. **Start
   with the single biggest:** one oversized changelog commonly accounts for most of the overage, and
   extracting it alone restores full headroom without touching procedural content.
3. **Write each to `references/<topic>.md`, named by TOPIC** (`evolution-changelog.md`,
   `cron-execution-workflow.md`, `common-pitfalls.md`) — never by date or incident. Convert the
   section's H2 into an H1 in the extracted file so it reads as a standalone document.
4. **Leave a pointer in `SKILL.md`**: the section's original H2 heading, plus one line naming the
   reference path, its character count, and that it is read on demand. The heading must survive so
   the skill's table of contents still describes itself.
5. **Prove editability with a REAL edit.** Apply a `skill_manage` patch and let it succeed. A character
   count is a proxy for editability; **the write is the gate** — and the write is what you were fixing.
6. **Propagate `SKILL.md` AND the new `references/` to every seat**, keeping the original as a `.bak`
   on each, then re-sweep to confirm zero remain over the threshold.

**Never drop content to make a skill fit.** Extraction preserves it in `references/`; deletion destroys
it. A skill that sheds its own history to pass a size check has lost the thing that made it valuable.

## ⚠️ Split on `\n(?=## )`, never `(?=\n## )`

The lookahead placement decides whether the heading comes back with its section:

```python
secs = re.split(r'(?=\n## )', text)   # ❌ captures the leading newline INTO the section
                                        #    -> s.split('\n')[0] is '' -> title detection blank
                                        #    -> pointers land with EMPTY headings
                                        #    -> references get named section-5.md, section-18.md

secs = re.split(r'\n(?=## )', text)   # ✅ heading stays at the front of its own section
```

**A blank title does not raise.** It silently produces pointer blocks with no heading text and
placeholder filenames — plausible-looking output from a script that reported success. This is a
one-character defect whose damage is invisible until someone opens the skill.

## Verify the OUTPUT, not the operation's success

## ✅ Validate against the OFFICIAL spec before publishing a skill outward

**The Agent Skills reference validator** (`skills-ref`) is the same one third-party packs run in CI:

```bash
uvx --from "git+https://github.com/agentskills/agentskills.git#subdirectory=skills-ref" skills-ref validate <skill_dir>
```

Subcommands: `validate`, `read-properties` (JSON), `to-prompt` (generates the `<available_skills>` XML).

**The spec allows exactly six frontmatter fields:** `name`, `description`, `license`, `compatibility`,
`allowed-tools`, `metadata`. **Anything else fails validation.**

**Measured on our own library (2026-09-25): 528 skills carry frontmatter, only 64 (12%) conform.** The rest use
Hermes-native fields — `version` (356), `author` (335), `tags` (249), `platforms` (116), `category` (98),
`trigger` (82), `related_skills` (44), `hermes` (26), `prerequisites` (25), `triggers` (23).

### Two rules for a skill we intend to publish or share

1. **Nest custom keys under `metadata:`** — top-level custom keys are rejected outright
   (*"Unexpected fields in frontmatter: tags"*).
2. **Write EVERY list in BLOCK style — never flow style, at any depth.** `tags: [a, b, c]` is rejected as *"ugly
   disallowed JSONesque flow mapping"* **even though it is perfectly valid YAML.** Block form passes:
   ```yaml
   metadata:
     tags:
       - a
       - b
   ```
   **⚠️ This is not a `tags:` rule.** In a six-skill sample five failed on `tags: […]`, but `creative/comfyui`
   failed on `author: [kshitijk4poor, alt-glitch, purzbeats]` — **it has no `tags:` field at all**, and it still
   fails when the flow list sits *inside* `metadata:`. **Renaming the field fixes nothing; converting every list to
   block style is the fix.** Check each failing line rather than assuming they share a cause.
   **Verified both directions:** flow → ❌, nested+block → ✅ `Valid skill`.

### ⛔ Do NOT mass-rewrite the library to satisfy the validator

**Hermes reads those fields — `version`, `tags`, `trigger`, `hermes`, `related_skills` are load-bearing in our
runtime.** Stripping them to satisfy an external spec would break our own agent. **They are not wrong; they are
non-portable.** The cost of the gap is *interoperability*, not function — so adopt the spec shape for **new
outward-facing skills**, and leave the existing 464 alone unless we start publishing into that ecosystem.

**Always run a control when a validator fails your files:** validate a known-good third-party skill in the same
batch. If theirs passes and yours fails, the finding is yours — and if *nothing* passes, your harness is broken.

An extraction can exit 0 and still have failed. Assert all four before believing it:

- reference filenames are **meaningful** (not `section-N.md`)
- every pointer heading is **non-empty**
- the **section count is unchanged** (you extracted, you did not drop)
- the extracted file's **content actually contains** the section body

### ⚠️ A REFUSED write prints exactly like a successful one if you only print its result

**A write tool that declines to act returns a structured error instead of the bytes written — and if
your wrapper prints a single field, a refusal reads as success.** Measured: a document rewrite was
announced as written while the file on disk was **still the old version at the old byte count**.
Nothing in the output said no.

```python
res = write_file(path, body)
print(res.get("bytes_written"))          # ← prints None on a REFUSAL; the run carries on
assert res.get("bytes_written"), f"write did not land: {res}"   # ← the correct form
```

**Verify by grepping for a marker you INTRODUCED** (`grep -c '<marker>' <file>`) **and confirm the
byte count changed.** Re-reading the target and finding the old text is the only test that
distinguishes "refused" from "landed" — the call itself always returns.

**Recognise the refusal that bites here:** overwriting a file that was last read with `offset`/`limit`
(a partial view) is refused until you read the whole file or use `patch` instead. Overwriting an
already-extracted `references/` file from a partial read is the same shape. The guard is working
correctly — the miss is not checking its result.

**Generalise it:** when a tool returns a structured payload, **assert its success field rather than
printing it**, because an absent key and a failure both read as `None`.

## Recovery when an extraction went wrong

**The same skill normally exists on every seat — a pristine copy is the backup you did not take.**
Restore `SKILL.md` from another seat, redo the split correctly, and **keep the damaged version as a
`.bak`** so the mistake is recorded rather than erased. Then re-verify output and re-propagate.

## Related

- `fleet-compatible-skills` — fleet-wide propagation, the shared core, and the drift audits that
  distribute whatever you fix here.
- `fleet-hygiene-audit.py` — the sweep that reports oversized skills; run it before and after.
