#!/usr/bin/env python3
"""
Direct Gemini vision call — session-hotfix when vision_analyze is broken.

WHY: When auxiliary.vision is stuck on a broken provider (e.g. nous +
tencent/hy3:free → 404), the in-session vision_analyze tool keeps failing
because config changes don't hot-reload until Hermes restarts. This script
calls Gemini's native vision API directly and works immediately.

USAGE:
    source /root/.hermes/profiles/gentech/.env
    python3 direct-gemini-vision.py /tmp/frame.png "Describe this image"

ARG 1: path to image (png/jpg)
ARG 2: question/prompt (optional, defaults to "Describe this image in detail.")

Requires: GOOGLE_API_KEY in env (sourced from .env). Uses gemini-2.5-flash.
"""
import base64
import json
import os
import sys
import urllib.request

MODEL = "gemini-2.5-flash"
BASE = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"


def main():
    if len(sys.argv) < 2:
        print("Usage: direct-gemini-vision.py <image_path> [question]")
        sys.exit(1)

    img_path = sys.argv[1]
    question = sys.argv[2] if len(sys.argv) > 2 else "Describe this image in detail."

    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        print("ERROR: GOOGLE_API_KEY not set. Run: source /root/.hermes/profiles/gentech/.env")
        sys.exit(1)

    with open(img_path, "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode()

    mime = "image/png" if img_path.lower().endswith(".png") else "image/jpeg"
    payload = {
        "contents": [{
            "parts": [
                {"text": question},
                {"inline_data": {"mime_type": mime, "data": img_b64}},
            ]
        }]
    }

    url = f"{BASE}?key={api_key}"
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
    )
    try:
        resp = json.loads(urllib.request.urlopen(req, timeout=60).read().decode())
        print(resp["candidates"][0]["content"]["parts"][0]["text"])
    except KeyError:
        print("RAW RESPONSE:", json.dumps(resp, indent=2)[:2000])


if __name__ == "__main__":
    main()
