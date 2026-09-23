#!/usr/bin/env bash
# sync-skill-from-core.sh — propagate ONE skill from the vault CORE to every seat.
#
# WHY: skills-distribution/ in the vault is the source of truth; each profile holds a working COPY.
# A lesson written on one seat silently diverges from CORE, and the seat that most needs the lesson
# is whichever one is behind. Jordan, 2026-09-22: "yes sync everyone".
#
# Skill files are read at LOAD time, so this needs NO gateway restart and no checkpoint ACK.
set -euo pipefail

SKILL_PATH="${1:?usage: sync-skill-from-core.sh <category>/<skill>}"
CORE="/root/vaults/gentech/10-Labs/skills-distribution/$SKILL_PATH"
PROFILES_DIR=/root/.hermes/profiles

[ -d "$CORE" ] || { echo "FATAL: no CORE dir at $CORE" >&2; exit 1; }
CORE_MD5=$(md5sum "$CORE/SKILL.md" | cut -d' ' -f1)
STAMP=$(date +%Y%m%d-%H%M%S)

echo "CORE: $CORE"
echo "      $(stat -c%s "$CORE/SKILL.md") bytes  md5 ${CORE_MD5:0:12}"
echo

# Every seat that holds a copy of this skill.
mapfile -t SEATS < <(for p in "$PROFILES_DIR"/*/; do
    [ -f "$p/skills/$SKILL_PATH/SKILL.md" ] && basename "$p"
  done)
[ ${#SEATS[@]} -gt 0 ] || { echo "FATAL: no seat holds this skill" >&2; exit 1; }

for seat in "${SEATS[@]}"; do
  DEST="$PROFILES_DIR/$seat/skills/$SKILL_PATH"
  BEFORE=$(md5sum "$DEST/SKILL.md" | cut -d' ' -f1)
  if [ "$BEFORE" = "$CORE_MD5" ]; then
    printf '  %-18s already current (%s)\n' "$seat" "${BEFORE:0:12}"
    continue
  fi
  cp "$DEST/SKILL.md" "$DEST/SKILL.md.bak-$STAMP"          # rollback-able
  cp "$CORE/SKILL.md" "$DEST/SKILL.md"
  # copy any supporting files CORE carries (references/, scripts/, ...) but never delete extras
  if [ -d "$CORE" ]; then
    (cd "$CORE" && find . -type f ! -name '*.bak-*' ! -name 'SKILL.md' -print0 \
      | while IFS= read -r -d '' f; do mkdir -p "$DEST/$(dirname "$f")"; cp "$f" "$DEST/$f"; done)
  fi
  AFTER=$(md5sum "$DEST/SKILL.md" | cut -d' ' -f1)
  if [ "$AFTER" = "$CORE_MD5" ]; then
    printf '  %-18s SYNCED  %s -> %s  (backup .bak-%s)\n' "$seat" "${BEFORE:0:12}" "${AFTER:0:12}" "$STAMP"
  else
    printf '  %-18s FAILED  copy did not take\n' "$seat" >&2; exit 1
  fi
done

echo
echo "── verify: every seat must now match CORE ──"
FAIL=0
for seat in "${SEATS[@]}"; do
  M=$(md5sum "$PROFILES_DIR/$seat/skills/$SKILL_PATH/SKILL.md" | cut -d' ' -f1)
  [ "$M" = "$CORE_MD5" ] && printf '  OK   %-18s %s\n' "$seat" "${M:0:12}" \
                         || { printf '  BAD  %-18s %s\n' "$seat" "${M:0:12}"; FAIL=1; }
done
[ "$FAIL" = 0 ] && echo "
  ✅ all ${#SEATS[@]} seats identical to CORE" || { echo "  ❌ drift remains"; exit 1; }
