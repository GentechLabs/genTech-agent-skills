# Recovering Files Dropped During a Rebase (Missing from Working Tree)

**Symptom:** A file that was "shipped" (committed) earlier is now MISSING from the working tree. `ls` shows the directory exists but the file is gone. Handoffs reference a path that 404s. The build looks unbuilt — but it was actually committed.

**Root cause (proven Aug 24, 2026):** The vault is mid-rebase on `main` (detached HEAD, hundreds of commits remaining). A file committed in an earlier commit (e.g. `37678591`) got dropped from the current working tree — either the rebase replayed commits without re-materializing the file, or the checkout moved HEAD to a point where the file isn't present. The handoff said "shipped" and the build looked lost.

**The critical distinction:** a file present in git history but absent from disk is RECOVERABLE — it's not lost work. Always check git before concluding a build was never done.

## Recovery steps

```bash
# 1. Confirm the file exists in history (not truly lost)
cd /root/vaults/gentech
git log --all --oneline -- "*gentech-token-security.yaml"   # find the commit that added it
# e.g. → 37678591 Labs: #49 Telegraph miner YAML + prediction-market rail assessment

# 2. See exactly what that commit contains (file path + size)
git show 37678591 --stat | grep -i telegraph

# 3. Recover the file content from the commit
git show 37678591:10-Labs/telegraph-miners/gentech-token-security.yaml

# 4. Restore it into the working tree at the CORRECT path
#    (handoffs may reference a stale path — verify against git ls-files)
git ls-files | grep -i telegraph      # find where git thinks it lives
```

## Pitfalls

- **Handoff paths lie during a rebase.** The Aug 22 handoff pointed to `10-Labs/telegraph-miners/`, but the file actually lives at `Gentech/10-Labs/telegraph-miners/`. Cross-check the handoff path against `git ls-files` / the actual `find` result before recovering.
- **`find` only shows the working tree.** `find . -iname "*file*"` returning nothing does NOT mean the file never existed — it means it's not on disk. Pair `find` with `git log --all` to distinguish "never built" from "committed but dropped."
- **Don't dispatch a rebuild before checking git history.** In this session the miner was marked "shipped," looked gone on disk, and was almost re-scoped as unbuilt — but `git show` recovered the full 60-line valid YAML. Always `git log --all` first.

## Prevention

When a mid-rebase state is active (detached HEAD, `git log --oneline -5` shows work-in-progress), treat `ls`/`find` results as unreliable for files committed recently. Verify against `git ls-files` + `git log --all` before declaring a shipped build lost, and before dispatching a rebuild.
