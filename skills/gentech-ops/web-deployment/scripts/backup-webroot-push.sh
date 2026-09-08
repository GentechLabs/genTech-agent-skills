#!/bin/bash
# Chunked webroot backup push to GitHub — proven Sep 4, 2026.
# Usage: backup-webroot-push.sh <staging-dir> <remote-name>
#   Staging dir must be a git repo with the files committed or staged-ready.
#   Strategy: git-over-HTTPS dies silently on single pushes >1.2G
#   ("send-pack: unexpected disconnect"). Chunks of ~250MB push reliably;
#   the tail goes up as a release asset (gh release create, 2GB/file limit).
#   VERIFY THE REMOTE SHA after every push — never trust push exit text
#   (a dead push can still print "Everything up-to-date").
set -e
DIR="${1:?usage: backup-webroot-push.sh <staging-dir> <remote-name>}"
REMOTE="${2:-origin}"
cd "$DIR"
LOG=push-log.txt
log(){ echo "[$(date +%H:%M:%S)] $*" | tee -a "$LOG"; }
CHUNK=250000000   # ~250MB per commit; drop to 150000000 on repeated failures

remote_head(){ git ls-remote "$REMOTE" refs/heads/main | cut -d' ' -f1; }

# files not yet tracked in HEAD
comm -23 \
  <(find . -type f -not -path './.git/*' -not -name push-log.txt -not -name "$(basename "$0")" | sed 's|^\./||' | sort) \
  <(git ls-files | sort) > /tmp/backup-remaining.txt
log "files remaining: $(wc -l < /tmp/backup-remaining.txt)"

BATCH=(); SIZE=0; PART=0
flush(){
  PART=$((PART+1))
  git add -f -- "${BATCH[@]}"
  git commit -q -m "backup part $PART: ~$((SIZE/1000000))MB"
  if git push -q "$REMOTE" main; then
    log "part $PART OK: ${#BATCH[@]} files, $((SIZE/1000000))MB — remote=$(remote_head)"
  else
    log "part $PART failed, retrying once..."
    sleep 10
    git push -q "$REMOTE" main && log "part $PART OK on retry" || { log "part $PART FAILED twice — stop; tail goes to a release asset instead"; exit 2; }
  fi
  BATCH=(); SIZE=0
}

while IFS= read -r f; do
  S=$(stat -c%s "$f")
  if (( SIZE + S > CHUNK )) && (( ${#BATCH[@]} > 0 )); then flush; fi
  BATCH+=("$f"); SIZE=$((SIZE+S))
done < /tmp/backup-remaining.txt
(( ${#BATCH[@]} > 0 )) && flush

LOCAL=$(git rev-parse HEAD); R=$(remote_head)
if [ "$LOCAL" = "$R" ]; then
  log "MATCH — backup complete: $(git ls-files | wc -l) files on $REMOTE"
else
  log "MISMATCH local=$LOCAL remote=$R"
  exit 1
fi