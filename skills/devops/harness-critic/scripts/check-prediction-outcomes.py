#!/usr/bin/env python3
"""
Cross-reference the predictions ledger against the outcome ledger and report
which past-due predictions have NO grade block.

Usage:
    python3 check-prediction-outcomes.py [--harness-dir DIR]
                                         [--predictions PATH]... [--outcomes PATH]...
                                         [--list-archive] [--quiet]
    python3 check-prediction-outcomes.py [predictions.md] [outcomes.md]   # legacy positional

CORPUS DISCOVERY (default): every file matching the NAME PREFIX `predictions`
under facts/ and facts/history/, and every file matching `prediction-outcomes`
under facts/ and facts/history/. Match by PREFIX, not by `.md` suffix: the
2026-08-08 compaction wrote its archive as
`facts/history/predictions.md-archive-20260808T041001Z` with no trailing `.md`,
so a `*.md` glob silently drops 41 authored pids.

DUE GRAMMARS ACCEPTED (all four occur in the live corpus and the archives):
    - due: 2026-08-17T08:00:00Z      (live facts/predictions.md)
    due: 2026-08-17T08:00:00Z        (archive 2026-09-01)
    - Due: 2026-08-15                (archive 2026-08-15)
    ## PREDICTION #68 — evolve-68 (2026-08-.. — due 2026-08-..)   (inline, archive 2026-08-15)
    DUE: 4 cycles                    (legacy, archives 2026-08-01 / 2026-08-08)

GRADE RULE — a pid is GRADED only if the outcome corpus contains a BLOCK whose
header names that pid (`## PREDICTION #N` / `## OUTCOME #N`) and whose body
carries a verdict token. A bare mention of a pid inside prose (a tally line, a
`DEFECT C` enumeration of never-graded pids, an `EARLY WARNING` note) is NOT a
grade — the corpus contains all three, and a whole-file `PREDICTION #(\d+)`
scan scores them as outcomes. `UNVERIFIABLE` / `INCONCLUSIVE` are counted as
referenced-but-not-adjudicated, separately from graded.

Exit codes:
    0  every past-due prediction in the LIVE corpus has a grade block
    1  at least one live past-due prediction has none
    2  VACUOUS CHECK — zero predictions parsed, or zero grade blocks parsed
"""

import argparse
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_HARNESS_DIR = "."

PRED_PREFIX = "predictions"
OUT_PREFIX = "prediction-outcomes"

PID_HEADER_RE = re.compile(r'^#{1,4}\s*(?:PREDICTION|PRED|OUTCOME)S?\s*#\s*(\d+)', re.I)
ANY_HEADER_RE = re.compile(r'^#{1,4}\s')
DUE_ISO_RE = re.compile(
    r'(?im)^\s*[-*]?\s*(?:due|deadline)\s*:?\s*(\d{4}-\d{2}-\d{2}(?:[T ]\d{2}:\d{2}(?::\d{2})?(?:Z|[+-]\d{2}:?\d{2})?)?)'
)
DUE_INLINE_RE = re.compile(r'(?i)\bdue\s+(\d{4}-\d{2}-\d{2}(?:T\d{2}:\d{2}(?::\d{2})?Z?)?)')
DUE_LEGACY_RE = re.compile(r'(?im)^\s*[-*]?\s*DUE\s*:\s*(\d+)\s*cycle')

VERDICT_TOKENS = (r'FULFILLED|FALSIFIED|CONFIRMED|PARTIALLY|PARTIAL|OPEN|SKIPPED|TRACKING|'
                  r'UNVERIFIABLE|INCONCLUSIVE')
VERDICT_RE = re.compile(
    r'(?im)^\s*[-*]?\s*(?:status|verdict)\s*:\s*(' + VERDICT_TOKENS + r')')
BARE_VERDICT_RE = re.compile(
    r'(?im)^\s*[-*]?\s*(' + VERDICT_TOKENS + r')\b')
# Rule (b): the grade frequently sits in the HEADER TAIL, e.g.
#   `## OUTCOME #28 — 2026-08-01T16:00Z (Cycle evolve-28) — PARTIAL (2/3 falsifiers)`
#   `## OUTCOME #13 — SKIPPED`
# so the header line itself is also a grade surface. Position-independent token scan
# of the header LINE (not the block body — see rule (f)).
HEADER_TOKEN_RE = re.compile(r'(?i)\b(' + VERDICT_TOKENS + r')\b')
NON_ADJUDICATED = {"UNVERIFIABLE", "INCONCLUSIVE"}


def discover(base: Path, prefix: str):
    """Files whose NAME starts with prefix under facts/ and facts/history/."""
    found = []
    for d in ("facts", "facts/history"):
        p = base / d
        if not p.is_dir():
            continue
        for f in sorted(p.iterdir()):
            if f.is_file() and f.name.startswith(prefix):
                found.append(f)
    return found


def parse_dt(raw: str):
    raw = raw.strip().rstrip(',;')
    for fmt in ("%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%MZ", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M",
                "%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%Y-%m-%d %H:%M"):
        try:
            return datetime.strptime(raw, fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    m = re.match(r'(\d{4}-\d{2}-\d{2})', raw)
    if m:
        return datetime.strptime(m.group(1), "%Y-%m-%d").replace(tzinfo=timezone.utc)
    return None


def blocks(text: str):
    """Yield (pid|None, body) for every pid header block, plus preamble as (None, preamble)."""
    lines = text.splitlines()
    out, cur_pid, cur_body, started = [], None, [], False
    for ln in lines:
        m = PID_HEADER_RE.match(ln)
        if m:
            if started:
                out.append((cur_pid, "\n".join(cur_body)))
            cur_pid, cur_body, started = int(m.group(1)), [ln], True
        elif ANY_HEADER_RE.match(ln) and started:
            out.append((cur_pid, "\n".join(cur_body)))
            cur_pid, cur_body = None, [ln]
        elif started:
            cur_body.append(ln)
        else:
            cur_body.append(ln)
    if started or cur_body:
        out.append((cur_pid, "\n".join(cur_body)))
    return out


def parse_predictions(paths):
    """{pid: {'due': datetime|None, 'legacy_cycles': int|None, 'source': name}}"""
    preds = {}
    for p in paths:
        text = p.read_text(errors="replace")
        for pid, body in blocks(text):
            if pid is None:
                continue
            due = legacy = None
            m = DUE_ISO_RE.search(body) or DUE_INLINE_RE.search(body)
            if m:
                due = parse_dt(m.group(1))
            if due is None:
                m = DUE_LEGACY_RE.search(body)
                if m:
                    legacy = int(m.group(1))
            if pid not in preds:
                preds[pid] = {"due": due, "legacy_cycles": legacy, "source": p.name}
            else:
                if preds[pid]["due"] is None and due is not None:
                    preds[pid]["due"] = due
                    preds[pid]["source"] = p.name
    return preds


def parse_grades(paths):
    """{pid: (token, file_name)} for outcome blocks that carry a verdict token.

    Grade surfaces, in order: the BLOCK HEADER LINE (rule (b) — the grade often
    sits in the header tail, and for `## OUTCOME #N` headers there is no body
    verdict line at all), then the block's own `VERDICT:`/`Status:` line, then a
    line that opens with a bare verdict token. Never a body-wide token scan —
    blocks quote other pids' verdicts in their EVIDENCE prose (rule (f)).
    """
    graded = {}
    for p in paths:
        text = p.read_text(errors="replace")
        for pid, body in blocks(text):
            if pid is None:
                continue
            lines = body.splitlines()
            header = lines[0] if lines else ""
            tok = None
            m = HEADER_TOKEN_RE.search(header)
            if m:
                tok = m.group(1).upper()
            if tok is None:
                rest = "\n".join(lines[1:])
                m = VERDICT_RE.search(rest) or BARE_VERDICT_RE.search(rest)
                if m:
                    tok = m.group(1).upper()
            if tok is None:
                continue
            if pid not in graded or graded[pid][0] in NON_ADJUDICATED:
                graded[pid] = (tok, p.name)
    return graded


def main(argv=None):
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("positional", nargs="*", help="legacy: [predictions.md] [outcomes.md]")
    ap.add_argument("--harness-dir", default=None)
    ap.add_argument("--predictions", action="append", default=[])
    ap.add_argument("--outcomes", action="append", default=[])
    ap.add_argument("--list-archive", action="store_true")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args(argv)

    base = Path(args.harness_dir) if args.harness_dir else Path(DEFAULT_HARNESS_DIR)

    if args.list_archive:
        if not (base / "facts").is_dir():
            print(f"no facts/ dir under {base.resolve()}", file=sys.stderr)
            return 2
        print("archive candidates (matched by NAME PREFIX, not by .md suffix):")
        for f in discover(base, PRED_PREFIX) + discover(base, OUT_PREFIX):
            print(f"  {f.relative_to(base)}")
        return 0

    explicit_pred = [Path(x) for x in args.predictions]
    explicit_out = [Path(x) for x in args.outcomes]
    if args.positional and not explicit_pred and args.positional[0]:
        explicit_pred = [Path(args.positional[0])]
    if args.positional and len(args.positional) > 1 and not explicit_out:
        explicit_out = [Path(args.positional[1])]

    if not (explicit_pred and explicit_out) and not (base / "facts").is_dir():
        print(f"VACUOUS CHECK — no facts/ dir under harness dir {base.resolve()}; pass "
              f"--harness-dir or explicit --predictions/--outcomes", file=sys.stderr)
        return 2

    pred_files = explicit_pred or discover(base, PRED_PREFIX)
    out_files = explicit_out or discover(base, OUT_PREFIX)

    present_pred = [f for f in pred_files if f.is_file()]
    present_out = [f for f in out_files if f.is_file()]

    if not present_pred:
        print(f"VACUOUS CHECK — 0 predictions file(s) present of {len(pred_files)} requested; "
              f"an empty input must not read as a clean bill of health", file=sys.stderr)
        return 2

    preds = parse_predictions(present_pred)
    if not preds:
        print(f"VACUOUS CHECK — 0 predictions parsed from {len(present_pred)} file(s); "
              f"the header or due grammar may have drifted", file=sys.stderr)
        return 2

    graded = parse_grades(present_out)
    if not graded:
        print(f"VACUOUS CHECK — 0 grade blocks parsed from {len(present_out)} outcome file(s); "
              f"every prediction would read as ungraded, which is a parse failure, not a finding. "
              f"Check the corpus list (grades of older pids live in facts/history/ archives) and "
              f"run with --list-archive.", file=sys.stderr)
        return 2

    now = datetime.now(timezone.utc)
    if explicit_pred:
        live_names = {f.name for f in present_pred}
    else:
        live_names = {f.name for f in present_pred if f.parent.name == "facts"}

    dated = [p for p, v in preds.items() if v["due"] is not None]
    past_due = [p for p, v in preds.items() if v["due"] is not None and v["due"] <= now]
    undated = [p for p, v in preds.items() if v["due"] is None]
    legacy_undated = [p for p in undated if preds[p]["legacy_cycles"] is not None]

    live_past_due = sorted(p for p in past_due if preds[p]["source"] in live_names)
    live_missing = [p for p in live_past_due if p not in graded]

    graded_pids = sorted(graded)
    ungraded = sorted(set(preds) - set(graded))
    graded_not_authored = sorted(set(graded) - set(preds))

    print(f"corpus: {len(present_pred)} predictions file(s), {len(present_out)} outcome file(s)")
    if not args.quiet:
        for f in present_pred:
            print(f"  predictions: {f}")
        for f in present_out:
            print(f"  outcomes:    {f}")
    print(f"parsed: {len(preds)} predictions, {len(dated)} dated, {len(past_due)} past due, "
          f"{len(undated)} undated ({len(legacy_undated)} legacy-cycle form)")
    print(f"graded: {len(graded_pids)} distinct pid(s) carry a grade block "
          f"({sum(1 for v in graded.values() if v[0] not in NON_ADJUDICATED)} adjudicated, "
          f"{sum(1 for v in graded.values() if v[0] in NON_ADJUDICATED)} unverifiable/inconclusive)")
    if graded_not_authored:
        print(f"NOTE: {len(graded_not_authored)} graded pid(s) have no authored header: "
              f"{graded_not_authored}")

    print(f"LIVE corpus: {len(live_past_due)} past-due prediction(s) authored in "
          f"{sorted(live_names)}")
    if live_missing:
        print(f"MISSING (live): {len(live_missing)} of {len(live_past_due)} live past-due "
              f"prediction(s) have no grade block:")
        for p in live_missing:
            print(f"  PREDICTION #{p} (due {preds[p]['due'].isoformat()}, authored in {preds[p]['source']})")
    elif live_past_due:
        print(f"ACTIONABLE: all {len(live_past_due)} live past-due prediction(s) carry a "
              f"grade block")
    else:
        print("ACTIONABLE: no live past-due prediction in this corpus")

    print(f"ARCHIVE SWEEP: {len(ungraded)} authored prediction(s) have no grade block anywhere "
          f"in the corpus (block-scoped: a prose mention does not count)")
    if ungraded:
        print(f"  no-grade-block pids: {ungraded}")

    if live_missing:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
