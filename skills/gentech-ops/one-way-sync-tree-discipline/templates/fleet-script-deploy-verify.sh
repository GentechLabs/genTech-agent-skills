#!/bin/bash
# Template: deploy a single script from an upstream source to every seat, then verify
# each seat matches the upstream — not each other, and not a source copy that is itself a seat.
#
# Copy this file and adapt SRC, SEATS, and the source-of-truth checks for your artifact.
# The pattern was proven on `deploy-handoff-watcher-fleet.sh` (2026-09-27).
set -u

SRC=/root/vaults/gentech/10-Labs/agent-kit-self-tracking/my-script.py   # upstream, tracked in git
SEATS=(gentech gentech-treasury gizmo pixel)                            # every downstream target
STAMP=$(date +%Y%m%dT%H%M%S)
DIVERGED=0

echo "=== source ==="
[ -f "$SRC" ] || { echo "  ❌ SOURCE MISSING: $SRC — aborting"; exit 1; }
printf "  %s  %s bytes  md5=%s\n" "$SRC" "$(stat -c%s "$SRC")" "$(md5sum "$SRC" | cut -c1-10)"

# Add cheap content checks that prove the source carries the fix/feature you are deploying.
# grep -qc '_hours_open' "$SRC" && echo "  ✅ contains the age fix" || { echo "  ❌ missing age fix"; exit 1; }

echo
echo "=== deploy ==="
for s in "${SEATS[@]}"; do
  DST="/root/.hermes/profiles/$s/scripts/my-script.py"
  if [ ! -f "$DST" ]; then
    echo "  $s: no file at $DST — skipped"
    DIVERGED=$((DIVERGED+1))
    continue
  fi
  # Back up before touching anything
  cp "$DST" "$DST.bak-${STAMP}"
  # ATOMIC replace: rename is atomic within a filesystem; plain cp is a torn read.
  if cp -p "$SRC" "$DST.tmp-${STAMP}" 2>/dev/null && mv -f "$DST.tmp-${STAMP}" "$DST"; then
    :
  else
    rm -f "$DST.tmp-${STAMP}" 2>/dev/null
    printf "  %-18s ❌ COPY FAILED — leaving original\n" "$s"
    DIVERGED=$((DIVERGED+1))
    continue
  fi
  # Syntax check the copied file
  if python3 -m py_compile "$DST" 2>/dev/null; then
    printf "  %-18s ✅ %s bytes  md5=%s\n" "$s" "$(stat -c%s "$DST")" "$(md5sum "$DST" | cut -c1-10)"
  else
    printf "  %-18s ❌ COMPILE FAILED — restoring backup\n" "$s"
    cp "$DST.bak-${STAMP}" "$DST"
    DIVERGED=$((DIVERGED+1))
  fi
done

echo
echo "=== verify every seat against the UPSTREAM (the authority) ==="
TARGET=$(md5sum "$SRC" | cut -c1-10)
for s in "${SEATS[@]}"; do
  f="/root/.hermes/profiles/$s/scripts/my-script.py"
  if [ ! -f "$f" ]; then
    printf "  %-18s ⚠️ absent\n" "$s"; DIVERGED=$((DIVERGED+1)); continue
  fi
  m=$(md5sum "$f" | cut -c1-10)
  if [ "$m" = "$TARGET" ]; then printf "  %-18s ✅ %s\n" "$s" "$m"
  else printf "  %-18s ❌ %s (upstream is %s)\n" "$s" "$m" "$TARGET"; DIVERGED=$((DIVERGED+1)); fi
done
echo "  upstream authority md5: $TARGET"

echo
if [ "$DIVERGED" -gt 0 ]; then
  echo "RESULT: $DIVERGED issue(s) — fleet NOT uniform (see ❌ lines above)"; exit 2
fi
echo "RESULT: all seats match the upstream ✓"; exit 0
