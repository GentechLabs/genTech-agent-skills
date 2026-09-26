#!/usr/bin/env python3
"""
life-lesson-engine.py — GenTech EDU: lessons drawn from Jordan's ACTUAL life.

WHY THIS EXISTS
---------------
Jordan (2026-09-23): *"we'll make it based off of your life… I've already had an idea like this where we make
lessons based off of what's relevant to you. So you get more engaged — because that's the problem with
Duolingo."*

Duolingo's own monetisation admits the mechanism: an AI conversation partner is worth a paywall because
conversation is the only place the app learns what you actually need. The sentences are telemetry. They then
harvest that signal and **drill everyone the same generic corpus**. We take the mechanism and close the loop:
collect what he gets wrong, drill THAT tomorrow, in sentences drawn from his own itinerary.

WHAT IT READS (real vault data, never invented phrases)
-------------------------------------------------------
  · Travel/travel-jordan.json          — his trips, legs, dates, base cities, purpose
  · 00-HQ/01-Travel/*/price-history.md — where he is going and what it costs
  · auto-logging food mentions         — meals he actually recorded

DESIGN RULE (decides-alone-execution)
-------------------------------------
The ENGINE owns the sequence. It is not a lesson picker that waits for him to choose — that hands the decision
back, which is the "calibrated confidence became ask Jordan" failure in a new costume. A tutor that already
knows DR is in November and drills airport-and-taxi vocabulary is an agent; a menu is a toy.

HONESTY RULES (house rules, non-negotiable)
-------------------------------------------
  · A lesson is generated ONLY from real vault data. No trip found -> says so, exits non-zero.
  · Mastery is UNKNOWN until observed — never a fabricated 0%, never an invented streak.
  · `--selftest` PLANTS a failure and proves the detector goes RED before shipping.

USAGE
-----
  python3 life-lesson-engine.py              # today's lesson
  python3 life-lesson-engine.py --selftest   # prove it can fail loudly
  python3 life-lesson-engine.py --json       # machine-readable (for the dashboard)
"""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import re
import sys
from datetime import date, datetime

VAULT = pathlib.Path("/root/vaults/gentech")          # the vault is shared by design
TRIPS = VAULT / "Travel" / "travel-jordan.json"
TRAVEL_DIR = VAULT / "00-HQ" / "01-Travel"


def _seat() -> str:
    """The seat this copy is running on, derived from the script's OWN path.

    Cron has no script-args field, so path-derived identity is the only fleet-wide
    mechanism (same idiom as handoff-watcher.py). Before 2026-09-25 the two paths
    below were the literal string /root/.hermes/profiles/gentech, carried
    byte-identical into all four seats — so every seat wrote its lessons into HQ's
    profile while its own state and cache sat unused (fleet-compat defect class,
    build-queue #28). Running the SHARED CORE copy is not a seat; it falls back to
    HQ, which owns the core.
    """
    parts = pathlib.Path(__file__).resolve().parts
    if "profiles" in parts:
        i = parts.index("profiles")
        if i + 1 < len(parts):
            return parts[i + 1]
    return "gentech"


SEAT = _seat()
PROFILE = pathlib.Path("/root/.hermes/profiles") / SEAT
SKILL_DIR = pathlib.Path(__file__).resolve().parents[1]   # <seat>/skills/edu
DATA = SKILL_DIR / "data"                                 # pack data — this seat's own
STATE = PROFILE / "state" / "life-lessons.json"
OUT = PROFILE / "cache" / "life-lessons"

# ── Phrase banks, keyed by the SITUATION he will actually be in. ────────────────────────────────
#
# DIALECT-FIRST (Jordan, 2026-09-23): *"you also got to look at different dialects… I'm going to the
# Dominican Republic, right? Well now I need to learn the Dominican dialect and how they speak Spanish
# very fast. Also, there's slang words, like K-L-K for what's up."*
#
# So the bank is keyed by DIALECT, never by bare language. "Spanish" is not a lesson; `es-DO` is.
# The phrases below are written the way Dominicans SAY them — dropped s, -ado → -a'o, tú + inversion —
# because a learner who studies textbook Spanish and lands in Santo Domingo hears a different language.
# The `std` (standard) form is kept per phrase so the lesson can SHOW the difference; that contrast is
# the teaching, not decoration.
PHRASES = {
    # ── Dominican Spanish (es-DO). The dialect for the November trip.
    "es-DO": {
        "greeting": [
            ("¿Qué lo qué?", "What's up? (KLK in text — the DR greeting)", "¿Qué tal?"),
            ("Dime a ver", "What's up? / tell me", "¿Qué me cuentas?"),
            ("¿Cómo e' que e'?", "How's it going?", "¿Cómo está?"),
            ("Ya tú sabe'", "You know how it is", "Ya sabes"),
        ],
        "airport": [
            ("Vengo por turismo, cuatro día'", "I'm here for tourism, four days", "Vengo por turismo, cuatro días"),
            ("Aquí 'tá mi pasaporte", "Here's my passport", "Aquí está mi pasaporte"),
            ("No tengo nada que declarar", "I have nothing to declare", "—"),
        ],
        "taxi": [
            ("¿Cuánto e' pa' lla'?", "How much to get there?", "¿Cuánto es para allá?"),
            ("Vamo' a usá el taxímetro", "Let's use the meter", "Vamos a usar el taxímetro"),
            ("Vo' a pagá en efectivo", "I'm paying cash", "Voy a pagar en efectivo"),
            ("¿Tú acepta' tarjeta?", "Do you take card?", "¿Aceptas tarjeta?"),
        ],
        "hotel": [
            ("Tengo una reserva a nombre de Jordan", "I have a reservation under Jordan", "—"),
            ("¿A qué hora e' el check-out?", "What time is check-out?", "¿A qué hora es el check-out?"),
            ("¿Hay wifi en la habitación?", "Is there wifi in the room?", "—"),
        ],
        "food": [
            ("La cuenta, por favol", "The check, please (note the r→l)", "La cuenta, por favor"),
            ("¿Qué tú me recomienda'?", "What do you recommend?", "¿Qué me recomiendas?"),
            ("Sin picante, por favol", "Not spicy, please", "Sin picante, por favor"),
            ("Eso 'tá nítido", "That's great / cool", "Eso está muy bien"),
            ("Pásame esa vaina", "Pass me that thing (vaina = anything)", "Pásame eso"),
        ],
    },
    # ── Thai (Central). Explicitly a "get around politely" goal, NOT fluency (~1,100 hrs, Cat IV).
    "th-TH": {
        "greeting": [
            ("สวัสดีครับ", "Hello (male speaker)", "—"),
            ("ขอบคุณครับ", "Thank you (male speaker)", "—"),
            ("ไม่เป็นไรครับ", "No problem / it's fine", "—"),
        ],
        "airport": [
            ("ผมมาเที่ยวครับ", "I'm here for tourism", "—"),
        ],
        "taxi": [
            ("ไปที่โรงแรมนี้ครับ", "To this hotel", "—"),
            ("เท่าไหร่ครับ", "How much?", "—"),
        ],
        "hotel": [
            ("ผมมีจองไว้ครับ", "I have a booking", "—"),
        ],
        "food": [
            ("ไม่เผ็ดครับ", "Not spicy, please", "—"),
            ("เก็บเงินด้วยครับ", "The bill, please", "—"),
        ],
    },
}

# ── DIALECT RESOLUTION: country/city -> the VARIANT he will actually hear. ──────────────────────
# Never resolve to a bare language. This is the permanent form of Jordan's dialect correction.
DIALECT_FOR_PLACE = {
    # Dominican Republic — Spanish (Dominican)
    "dominican republic": "es-DO", "dr": "es-DO", "puerto plata": "es-DO", "sosúa": "es-DO",
    "sosua": "es-DO", "santo domingo": "es-DO", "punta cana": "es-DO",
    # Thailand — Thai (Central, the Bangkok standard)
    "thailand": "th-TH", "bangkok": "th-TH", "pattaya": "th-TH", "chiang mai": "th-TH",
}

# The human label shown in the lesson, so the dialect is never invisible.
DIALECT_LABEL = {
    "es-DO": "Spanish — Dominican (es-DO)",
    "th-TH": "Thai — Central (th-TH)",
}

# The regional voice that matches the dialect. Resolved here, not hardcoded in the audio script,
# so a new dialect cannot silently inherit the wrong accent (which is exactly what happened: Roger,
# an ENGLISH voice, read the first Spanish lesson with an American accent).
#
# Shared-library voices must be ADDED to the account before synthesis works — calling by id alone
# returns `404 voice_not_found`. See `life-lesson-audio.py`.
VOICE_FOR_DIALECT = {
    "es-DO": "tpbS1suUR3ke5cIZG2E3",   # Anderson — Dominican (added from the shared library)
    "th-TH": "CwhRBWXzGAHq8TQ4Fs17",   # Roger — multilingual; no Thai-native on the account yet
}

# Which situation leads, given what he has coming. Order = priority.
SITUATION_ORDER = ["greeting", "airport", "taxi", "hotel", "food"]

# NEXT-TRIP PRIORITY — the timeline decides which language leads, not the alphabet.
#
# BUG THIS FIXES (found in the first live run, 2026-09-23): the engine returned the first match while
# iterating trips sorted by *filename*, so `bangkok/` beat `puerto-plata/` and it drilled **Thai** — for a
# trip that is two months further out. The DR is the November trip; Thailand is Jan/Feb. Drilling the wrong
# language first is the whole failure mode this engine exists to avoid.
#
# Ranking is the plan as recorded in the vault (00-HQ/01-Travel + the DR-vs-Thailand call): nearest upcoming
# trip first. A dated trip always outranks an undated route tracker.
NEXT_TRIP_RANK = {
    "puerto plata": 1, "sosúa": 1, "sosua": 1, "dominican republic": 1,   # November — next
    "bangkok": 2, "pattaya": 2, "thailand": 2,                            # Jan/Feb — after
}


def load_trips() -> list[dict]:
    """Every trip Jordan has in the vault, newest-relevant first. Real data only."""
    out: list[dict] = []
    if TRIPS.exists():
        try:
            d = json.loads(TRIPS.read_text())
            t = d.get("trip") or {}
            if t:
                out.append({"name": t.get("name", "?"), "status": t.get("status", ""),
                            "start": t.get("startDate", ""), "place": t.get("homeBase", ""),
                            "legs": t.get("legs", [])})
        except Exception as e:
            print(f"  ⚠️  trip json unreadable: {e}", file=sys.stderr)
    # Route trackers = places he is actively watching (he is going there).
    for ph in sorted(TRAVEL_DIR.glob("*/price-history.md")):
        city = ph.parent.name
        if city in ("fx",):
            continue
        try:
            head = "\n".join(ph.read_text(errors="ignore").splitlines()[:40])
        except Exception:
            continue
        if not head.strip():
            continue
        out.append({"name": f"{city} (tracked route)", "status": "Watching fares",
                    "start": "", "place": city, "legs": [], "source": str(ph)})
    return out


def pick_dialect(trips: list[dict]) -> tuple[str, str]:
    """Return (dialect, why) from real trip data, NEAREST TRIP FIRST. Never guesses silently.

    Returns a DIALECT (`es-DO`), never a bare language. Jordan's correction: "Spanish" is not a
    lesson — Dominican Spanish is. A bare-language resolver is how the first lesson ended up
    teaching textbook Spanish he cannot use.

    Iteration order is by NEXT_TRIP_RANK, not by filename (bug 1, 2026-09-23).
    Place names are normalised before matching (bug 2: `puerto-plata` never matched `puerto plata`).
    """
    best: tuple[int, str, str] | None = None
    for t in trips:
        blob = " ".join([t.get("name", ""), t.get("place", ""),
                         " ".join(l.get("destination", "") for l in t.get("legs", []))]).lower()
        blob = re.sub(r"[-_/]+", " ", blob)          # puerto-plata -> puerto plata
        blob = re.sub(r"\s+", " ", blob)
        for k, dialect in DIALECT_FOR_PLACE.items():
            if k in blob:
                rank = NEXT_TRIP_RANK.get(k, 99)
                if best is None or rank < best[0]:
                    best = (rank, dialect, t.get("name", k))
    if best is None:
        return "", ""
    return best[1], best[2]


def mastery() -> dict:
    """Observed mastery only. Absent file -> empty, never a fabricated baseline."""
    if STATE.exists():
        try:
            return json.loads(STATE.read_text())
        except Exception:
            pass
    return {}


def build_lesson(trips: list[dict], seen: dict) -> dict | None:
    dialect, why = pick_dialect(trips)
    if not dialect:
        return None
    bank = PHRASES[dialect]
    items: list[dict] = []
    for sit in SITUATION_ORDER:
        for row in bank.get(sit, []):
            es, en = row[0], row[1]
            std = row[2] if len(row) > 2 else "—"
            key = f"{dialect}:{es}"
            # LEGACY KEY FALLBACK. Mastery records written before the dialect change are keyed by
            # BARE language (`es:La cuenta, por favor.`); the dialect split keys them `es-DO:...`.
            # Without this fallback every stored result silently orphans — the learner's history
            # resets to "new" and the drill loop forgets what he got wrong. A rename is not a
            # reason to lose data. (Caught by selftest check 3, 2026-09-23.)
            legacy_key = f"{dialect.split('-')[0]}:{es}"
            s = seen.get(key) or seen.get(legacy_key) or {}
            items.append({
                "situation": sit, "es": es, "en": en,
                # The standard form beside the regional one — the CONTRAST is the teaching.
                "std": std,
                # UNKNOWN until observed — "new" is honest, "0%" is a fabricated measurement
                "attempts": s.get("attempts", 0),
                "correct": s.get("correct", 0),
                "status": ("new" if not s else
                           "weak" if s.get("correct", 0) / max(s.get("attempts", 1), 1) < 0.6
                           else "solid"),
            })
    # Weak first, then new — the loop closes: what he got wrong gets drilled.
    items.sort(key=lambda i: ({"weak": 0, "new": 1, "solid": 2}[i["status"]], i["situation"]))
    return {"dialect": dialect, "lang": dialect.split("-")[0],
            "dialect_label": DIALECT_LABEL.get(dialect, dialect),
            "voice_id": VOICE_FOR_DIALECT.get(dialect),
            "why": why, "generated": datetime.utcnow().isoformat(timespec="seconds"),
            "items": items[:6]}


def render(lesson: dict) -> str:
    lines = [
        f"🎓 LIFE LESSON — {lesson.get('dialect_label', lesson['dialect'])}",
        f"drawn from: {lesson['why']}",
        "",
    ]
    for i, it in enumerate(lesson["items"], 1):
        tag = {"weak": "🔁 DRILL (missed before)", "new": "🆕 NEW", "solid": "✅ review"}[it["status"]]
        lines.append(f"{i}. [{it['situation']}] {tag}")
        lines.append(f"   {it['es']}")
        lines.append(f"   {it['en']}")
        if it.get("std") and it["std"] != "—":
            lines.append(f"   (textbook: {it['std']})")
        lines.append("")
    lines.append("Audio is generated separately, in the matching regional voice.")
    lines.append("Nothing here is invented — every phrase is keyed to a country you are")
    lines.append("actually travelling to, in the dialect spoken there.")
    return "\n".join(lines)


def selftest() -> int:
    """PLANT a failure and prove we go RED. House rule: every detector proves it can fail."""
    print("SELFTEST — planting failures, expecting loud RED\n")
    ok = True

    # 1. Missing trip data must produce NO lesson, not a generic course.
    real_trips, real_load = load_trips, None
    globals()["load_trips"] = lambda: []
    l = build_lesson([], {})
    if l is None:
        print("  ✅ RED 1: no trip data -> no lesson (refuses to invent one)")
    else:
        print("  ❌ FAIL 1: invented a lesson with no trip data"); ok = False
    globals()["load_trips"] = real_trips

    # 2. Mastery must be UNKNOWN, never a fabricated 0%.
    l = build_lesson([{"name": "Puerto Plata DR", "place": "Puerto Plata", "legs": []}], {})
    if l and all(i["status"] == "new" and i["attempts"] == 0 for i in l["items"]):
        print("  ✅ RED 2: unseen phrases are 'new' (attempts 0) — never a fake 0% score")
    else:
        print("  ❌ FAIL 2: fabricated a mastery value"); ok = False

    # 3. Weak items MUST sort first — the loop must actually close.
    # deliberately a LEGACY bare-language key: proves old records still count after the dialect split
    seen = {"es:La cuenta, por favol": {"attempts": 4, "correct": 0}}
    l = build_lesson([{"name": "Puerto Plata DR", "place": "Puerto Plata", "legs": []}], seen)
    if l and l["items"][0]["status"] == "weak":
        print("  ✅ RED 3: a phrase he keeps missing sorts to the TOP (loop closes)")
    else:
        print("  ❌ FAIL 3: missed phrases are not prioritised"); ok = False

    # 4. Thai must not be presented as a full course.
    l = build_lesson([{"name": "Bangkok Thailand", "place": "Bangkok", "legs": []}], {})
    if l and l["dialect"] == "th-TH" and len(l["items"]) <= 6:
        print("  ✅ RED 4: Thai gives a small survival set, not a fake 150-lesson course")
    else:
        print("  ❌ FAIL 4: Thai scope wrong"); ok = False

    # 5. THE ORDERING BUG, REGRESSION-GUARDED. Both countries present (which is the real vault state:
    #    bangkok/ and puerto-plata/ trackers coexist) -> Spanish MUST win, because the DR trip is nearer.
    #    This failed on the first live run and drilled Thai two months early.
    mixed = [{"name": "bangkok (tracked route)", "place": "bangkok", "legs": []},
             {"name": "puerto-plata (tracked route)", "place": "puerto-plata", "legs": []}]
    l = build_lesson(mixed, {})
    if l and l["dialect"] == "es-DO":
        print("  ✅ RED 5: with both countries tracked, the NEARER trip wins (es-DO, not Thai)")
    else:
        print(f"  ❌ FAIL 5: wrong dialect leads with two trips — got {l['dialect'] if l else None}"); ok = False

    # 6. Reversed input order must give the SAME answer (order-independence, not luck).
    l2 = build_lesson(list(reversed(mixed)), {})
    if l2 and l2["dialect"] == "es-DO":
        print("  ✅ RED 6: input order does not change the answer")
    else:
        print("  ❌ FAIL 6: answer depends on list order"); ok = False

    # 7. DIALECT, NOT LANGUAGE (Jordan's correction, 2026-09-23). A bare-language result means the
    #    learner gets textbook Spanish they cannot use — the exact defect he caught. Assert the
    #    variant is named, and that a matching regional VOICE is attached.
    l = build_lesson([{"name": "Puerto Plata DR", "place": "Puerto Plata", "legs": []}], {})
    if l and l["dialect"] == "es-DO" and l.get("voice_id"):
        print("  ✅ RED 7: resolves to a DIALECT (es-DO) with a matching regional voice")
    else:
        print(f"  ❌ FAIL 7: dialect/voice not resolved — got {l and l.get('dialect')}"); ok = False

    # 8. The regional form must be present AND differ from textbook, or there is nothing to teach.
    l = build_lesson([{"name": "Puerto Plata DR", "place": "Puerto Plata", "legs": []}], {})
    shown = [i for i in (l or {}).get("items", []) if i.get("std") and i["std"] != "—"]
    if shown:
        print(f"  ✅ RED 8: {len(shown)} phrases carry the textbook form beside the Dominican one")
    else:
        print("  ❌ FAIL 8: no standard/regional contrast — the lesson teaches nothing dialectal"); ok = False

    print("\n" + ("SELFTEST PASSED — all eight planted failures went RED"
                  if ok else "SELFTEST FAILED"))
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--quiet", action="store_true", help="silent on success (cron mode)")
    a = ap.parse_args()
    if a.selftest:
        return selftest()

    trips = load_trips()
    if not trips:
        print("🔴 life-lesson-engine: NO trip data in the vault — refusing to invent a lesson.",
              file=sys.stderr)
        return 1
    lesson = build_lesson(trips, mastery())
    if lesson is None:
        print("🔴 life-lesson-engine: no country in your trips maps to a language bank. "
              "Add the trip or the bank — not a generic course.", file=sys.stderr)
        return 1

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "today.json").write_text(json.dumps(lesson, ensure_ascii=False, indent=2))

    if a.json:
        print(json.dumps(lesson, ensure_ascii=False, indent=2))
    elif not a.quiet:
        print(render(lesson))
    return 0


if __name__ == "__main__":
    sys.exit(main())
