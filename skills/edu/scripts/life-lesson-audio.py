#!/usr/bin/env python3
"""
life-lesson-audio.py — turn today's life-lesson into listenable Spanish/Thai audio.

Part of GenTech EDU (life-based lessons). Reads the lesson the engine produced and renders it with
ElevenLabs so Jordan can drill it while walking, not just read it.

WHY A SEPARATE SCRIPT: generation and synthesis fail for different reasons. The engine can be perfectly
correct while the API key is dead or the account is out of characters — keeping them apart means a voice
outage never masquerades as a broken lesson, and the engine stays runnable with zero network access.

HONESTY: never writes a "success" audio file from an error body. A non-audio response is a loud failure.

USAGE
  python3 life-lesson-audio.py            # renders cache/life-lessons/today.json
  python3 life-lesson-audio.py --quiet    # cron mode: silent unless it breaks
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys
import urllib.error
import urllib.request

def _seat() -> str:
    """The seat this copy is running on, derived from the script's OWN path.

    Cron has no script-args field, so path-derived identity is the only fleet-wide
    mechanism (same idiom as handoff-watcher.py). These three paths were hardcoded to
    /root/.hermes/profiles/gentech and carried byte-identical into all four seats, so
    a worker seat rendered from HQ's lesson file and could never produce its own audio.
    Running the SHARED CORE copy is not a seat; it falls back to HQ, which owns the core.
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
ENV = PROFILE / ".env"
LESSON = PROFILE / "cache" / "life-lessons" / "today.json"
OUT = PROFILE / "cache" / "life-lessons" / "lesson.mp3"

# FALLBACK voice only. The real choice comes from the lesson's own `voice_id`, which the engine
# resolves per DIALECT. Hardcoding a single voice here is what produced the first wrong lesson:
# Roger (an ENGLISH voice, accent=american) read Dominican Spanish with an American accent.
#
# ⚠️ Shared-library voices are NOT synthesis-capable by id alone — the API returns
#    `404 voice_not_found` until the voice is ADDED to our account:
#      POST /v1/voices/add/{public_owner_id}/{voice_id}
#    Anderson (Dominican, es-DO) is already added. A new dialect needs the same step.
FALLBACK_VOICE = "CwhRBWXzGAHq8TQ4Fs17"

INTRO = {
    "es": "Lección de español dominicano. Escucha y repite.",
    "th": "บทเรียนภาษาไทย ฟังแล้วพูดตาม",
}


def api_key() -> str:
    for line in ENV.read_text().splitlines():
        if line.startswith("ELEVENLABS_API_KEY="):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    raise SystemExit("🔴 ELEVENLABS_API_KEY not found in profile .env")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args()

    if not LESSON.exists():
        print(f"🔴 life-lesson-audio: no lesson at {LESSON} — run life-lesson-engine.py first",
              file=sys.stderr)
        return 1

    lesson = json.loads(LESSON.read_text())
    dialect = lesson.get("dialect") or lesson.get("lang", "")
    if not lesson.get("items"):
        print("🔴 life-lesson-audio: lesson has no items — refusing to synthesise silence",
              file=sys.stderr)
        return 1

    voice_id = lesson.get("voice_id") or FALLBACK_VOICE
    if not lesson.get("voice_id"):
        print("  ⚠️  lesson carries no dialect voice — falling back. The accent may not match "
              f"{dialect}.", file=sys.stderr)

    intro = INTRO.get(dialect.split("-")[0], "")
    # Speak the REGIONAL form, then the English meaning. The textbook form is for the eyes, not
    # the ear — drilling the textbook pronunciation is what makes a learner incomprehensible.
    script = intro + "\n" + "\n".join(
        f"{it['es']} ... {it['en']}" for it in lesson["items"])

    body = json.dumps({"text": script, "model_id": "eleven_multilingual_v2",
                       "voice_settings": {"stability": 0.45, "similarity_boost": 0.8}}).encode()
    req = urllib.request.Request(
        f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
        data=body, headers={"xi-api-key": api_key(), "Content-Type": "application/json"})
    try:
        audio = urllib.request.urlopen(req, timeout=200).read()
    except urllib.error.HTTPError as e:
        detail = e.read()[:300].decode("utf-8", "replace")
        print(f"🔴 life-lesson-audio: HTTP {e.code} — {detail}", file=sys.stderr)
        if e.code == 404:
            print("   hint: a shared-library voice must be ADDED to the account first —\n"
                  "   POST /v1/voices/add/{public_owner_id}/{voice_id}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"🔴 life-lesson-audio: {type(e).__name__}: {e}", file=sys.stderr)
        return 1

    # A JSON/HTML error body saved as .mp3 would look like success and play as noise. Verify it is audio.
    if not audio.startswith(b"ID3") and audio[:2] != b"\xff\xfb":
        print(f"🔴 life-lesson-audio: response is not MPEG audio (starts {audio[:12]!r}) — not writing it",
              file=sys.stderr)
        return 1

    OUT.write_bytes(audio)
    if not a.quiet:
        print(f"✅ {OUT} — {len(audio)} bytes, dialect={dialect}, voice={voice_id}, "
              f"{len(lesson['items'])} phrases")
    return 0


if __name__ == "__main__":
    sys.exit(main())
