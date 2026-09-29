#!/usr/bin/env python3
"""Append a lesson to the LIVE part of the develop-and-verify pitfalls ledger, then
regenerate the index so its part table and census line never drift.

WHY THIS EXISTS: the ledger is split across part files with an index that carries each
part's count and digest, plus a provenance census that makes an extraction checkable.
Both are numbers under a moving artifact — and a count or a digest is a claim about a
MOMENT. Refreshing them by hand is how an index becomes a stale recital, so the refresh
is mechanical: append, then re-read every part and rewrite the derived block.

USAGE
    ledger_append.py --item-file /path/to/item.md          # append + refresh
    ledger_append.py --refresh                             # refresh the index only
    ledger_append.py --check                               # per-file size against the cap

The index states the moment its digests were read, and the census distinguishes GROWTH
(items added after a move) from a REWRITE (a count that moves with nothing added) —
because a check that cannot tell them apart fails silently while looking fine.
"""
import argparse, hashlib, os, re, sys, datetime

CAP = 100_000                      # the platform's per-file character cap
SEATS = ["pixel", "gentech", "labs", "treasury", "gizmo"]
RULE = "lines beginning `- **` whose text CONTAINS `<seat>`, CASE-SENSITIVE, over the part files"

def here():
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def refs():
    return os.path.join(here(), "references")

def parts():
    """Every pitfalls-N.md, in order. The highest N is the live part."""
    d = refs()
    found = []
    for f in os.listdir(d):
        m = re.fullmatch(r"pitfalls-(\d+)\.md", f)
        if m:
            found.append((int(m.group(1)), f))
    return [f for _, f in sorted(found)]

def read(p):
    with open(p, encoding="utf-8") as fh:
        return fh.read()

def count_items(text):
    return [l for l in text.split("\n") if l.startswith("- **")]

def census(texts):
    out = {s: 0 for s in SEATS}
    for t in texts:
        for l in count_items(t):
            for s in SEATS:
                if s in l:                      # the stated rule: substring, case-sensitive
                    out[s] += 1
    return out

def stats():
    d = refs()
    rows = []
    for f in parts():
        p = os.path.join(d, f)
        t = read(p)
        rows.append({"file": f, "items": len(count_items(t)), "chars": len(t),
                     "md5": hashlib.md5(t.encode()).hexdigest()})
    return rows

def refresh():
    d = refs()
    idx_p = os.path.join(d, "pitfalls.md")
    idx = read(idx_p)
    now = datetime.datetime.now(datetime.timezone.utc).strftime("%H:%M:%SZ")
    rows = stats()
    grand = census([read(os.path.join(d, r["file"])) for r in rows])

    table = ("| part | items | chars | md5 |\n|---|---|---|---|\n" +
             "".join(f"| `references/{r['file']}` | {r['items']} | {r['chars']:,} | `{r['md5']}` |\n"
                     for r in rows))
    idx = re.sub(r"\| part \| items \| chars \| md5 \|\n\|---\|---\|---\|---\|\n(\|[^\n]*\n)+",
                 table, idx)
    idx = re.sub(r"## Parts — counts and digests read at \S+",
                 f"## Parts — counts and digests read at {now}", idx)

    tot = " · ".join(f"{s} {grand[s]}" for s in SEATS)
    idx = re.sub(r"SINCE THE SPLIT lessons have been appended[^\n]*\n(    [^\n]*\n)?",
                 "SINCE THE SPLIT lessons have been appended to the LIVE part, so totals GROW — that is growth, not a rewrite:\n"
                 f"    {tot}      (read {now})\n", idx)
    with open(idx_p, "w", encoding="utf-8") as fh:
        fh.write(idx)
    print(f"  index refreshed at {now} ({len(idx):,} chars, md5 {hashlib.md5(idx.encode()).hexdigest()})")
    for r in rows:
        print(f"    {r['file']:18s} {r['items']:>3d} items  {r['chars']:>7,} chars  {r['md5']}")
    print(f"    census total: {tot}")
    print(f"    RULE: {RULE}")
    return rows

def check():
    d = here()
    bad = []
    for root, dirs, files in os.walk(d):
        dirs[:] = [x for x in dirs if x != "__pycache__"]
        for f in files:
            p = os.path.join(root, f)
            try:
                n = len(read(p))
            except Exception:
                continue
            if n > CAP:
                bad.append((os.path.relpath(p, d), n))
    if bad:
        print(f"  ⛔ {len(bad)} file(s) OVER the {CAP:,}-char per-file cap:")
        for f, n in bad:
            print(f"      {f}  {n:,}")
        return 1
    print(f"  ✅ no file in the skill dir is over the {CAP:,}-char per-file cap")
    return 0

def verify_move(pre_split):
    """THE TWO-SIDED MOVE TEST, made mechanical so it is a practice and not a memory.

    A move of whole blocks must satisfy BOTH sides at once:
      LOST must be 0        (an item in the source and in no part => something was dropped or orphaned)
      GAINED must be NAMEABLE (items in the parts but not the source => growth, and each one can be pointed at)
    Duplicates across parts must be 0. A count that moves with LOST == 0 is GROWTH; a count that moves
    with LOST > 0 is a REWRITE. A check that cannot tell them apart fails silently while looking fine.
    """
    d = refs()
    def keys(text):
        return [l[:90] for l in text.split("\n") if l.startswith("- **")]
    src = keys(read(pre_split))
    got = {}
    for f in parts():
        for k in keys(read(os.path.join(d, f))):
            got.setdefault(k, []).append(f)
    lost = [k for k in src if k not in got]
    gained = [k for k in got if k not in src]
    dupes = [k for k, v in got.items() if len(v) > 1]
    print(f"  source items {len(src)} · parts items {sum(len(v) for v in got.values())} · distinct {len(got)}")
    print(f"  LOST   {len(lost)}   {'✅' if not lost else '⛔ A REWRITE — something was dropped or orphaned'}")
    for k in lost[:5]:
        print(f"      - {k[:80]}")
    print(f"  GAINED {len(gained)}   {'✅ none' if not gained else '✅ growth — nameable:'}")
    for k in gained[:8]:
        print(f"      + {k[:80]}  ({len(got[k])} part)" if k in got else f"      + {k[:80]}")
    print(f"  DUPLICATES across parts {len(dupes)}   {'✅' if not dupes else '⛔'}")
    verdict = ("GROWTH, NOT A REWRITE" if not lost else "A REWRITE — LOST is not zero")
    print(f"  VERDICT: {verdict}")
    return 0 if not lost else 2


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--item-file")
    ap.add_argument("--refresh", action="store_true")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--verify-move", metavar="PRE_SPLIT_FILE",
                    help="two-sided test: LOST must be 0, GAINED must be nameable")
    a = ap.parse_args()
    if a.verify_move:
        return verify_move(a.verify_move)
    if a.check:
        return check()
    if a.item_file:
        live = parts()[-1]
        p = os.path.join(refs(), live)
        t = read(p)
        item = read(a.item_file).strip()
        if item[:60] in t:
            print(f"  already present in {live} — no append")
        else:
            with open(p, "w", encoding="utf-8") as fh:
                fh.write(t.rstrip("\n") + "\n" + item + "\n")
            print(f"  appended to the LIVE part ({live})")
    refresh()
    return 0

if __name__ == "__main__":
    sys.exit(main())
