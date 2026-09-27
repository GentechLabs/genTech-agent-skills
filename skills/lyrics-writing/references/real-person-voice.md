# Writing a character's voice from a REAL person's messages

When a real, identifiable person is turned into a character (a friend, the boss, a collaborator),
**never invent their lyric voice.** Derive it from how they actually write. Inventing produces a
generic rapper; deriving produces *them*, and the difference is obvious on the page.

## 1. Find their corpus in the vault (do not ask them to supply it)
Their words are usually already recorded, quoted verbatim in handoffs and trackers. On the GenTech
vault, these carry the most verbatim quotes:

- `HQ/jordan-queue.md` — Jordan's action queue; quotes him at length in every section
- `01-HANDOFFS/*-completions.md` — daily completions notes, quote the human's asks verbatim
- `00-HQ/*.md`, `11-Mess Hall/agent-brain/**`, `Journal/journal-data.json`

Extraction patterns that work:

```
Jordan(?:,?\s*(?:verbatim|said|says|asked)\S{0,40})?\s*:\s*[\*_]*["\u201c\u2018](.{25,900}?)["\u201d\u2019]
[Jj]ordan(?:\s*verbatim)?\s*[\(\u2014-]{1,3}\s*[\*_]*["\u201c](.{25,900}?)["\u201d]
\(Jordan[^)]{0,30}\)\s*[\u2014:-]\s*[\*_]*["\u201c](.{25,900}?)["\u201d]
```

Dedupe by the first ~80 chars. A sweep of the GenTech vault returned **337 verbatim Jordan quotes** —
plenty to fingerprint from. Also count signature phrases across the vault; frequency is the signal that
a phrase is a genuine tic and not a one-off:
`"you know"` (85), `"going to go ahead"` (6), `"stuff like that"` (22), `"for the time being"` (26).

## 2. Build the fingerprint (same 8 axes every time)
1. **Pronoun habit** — Jordan says *"we"*, almost never *"I"*. The work is collective.
2. **Signature construction** — *"going to go ahead and…"* opens nearly every decision and hand-off.
3. **Sentence shape** — transcribed speech: run-ons joined by "so/because/and", trailing off with "…".
4. **Fillers** — his padding: "you know", "and stuff like that", "and different things".
5. **Interrogative delegation** — he asks, never commands: "why don't we…", "should we…", "is there a way…".
6. **Answer style** — blunt and short: "Yes fix these." "Yes sync everyone."
7. **Domain vocabulary** — top priority · green light · lock it in · square away · absolutely.
8. **How they state money/life** — plainly, no romance: "leave a few cents for gas", "send 1 dollar to test it", "I had to take care of a few bills".

## 3. Write from it
- **Genre fit first.** A producer/DJ character → spoken word over the beat, not sung bars. Their catchphrase can *be* the drop call: *"we're going to go ahead and drop it."*
- **Trace every line back to a real utterance.** Keep a mapping line-by-line so the borrow is auditable, e.g. *"leave a little for the gas"* ← *"leave a few cents for gas"*.
- **Do not make a catchphrase collage.** Pick the 3–4 strongest markers; let the rest of the language be natural. A voice is a register, not a quote reel.
- **Contract their signature construction if it repeats too much** — in lyric form, once or twice is a hook; five times is a gimmick.
- **Run real quotes in their own grammar but not their own words** where the source is mundane admin ("audit", "queue"); the *shape* transfers, the subject matter does not.

## 4. Report the fingerprint, not just the lyrics
The evidence is the deliverable co-equal with the lyric. Show the 6–8 traits with a real quote as proof
for each, then the lyric. It demonstrates the voice is derived rather than invented, and it is reusable
for every later track in the same character's voice.
