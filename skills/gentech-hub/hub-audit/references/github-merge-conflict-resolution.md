# GitHub Merge Conflict Resolution for Hub Data Files

## Problem

Merge conflict markers (`<<<<<<< Updated upstream`, `=======`, `>>>>>>> Stashed changes`) appear in JSON data files on GitHub, breaking JSON parsing and causing hub dashboards to fail loading.

## Root Cause

A manual git merge on another machine left unresolved conflicts, which were then pushed to `origin/main`. The conflict markers become embedded in the JSON file, making it invalid.

## Detection

```bash
# Check for merge conflict markers
grep -n "<<<<<<< Updated upstream" DeFi/defi-data.json

# Verify JSON is valid
curl -s "https://raw.githubusercontent.com/.../defi-data.json" | python3 -m json.tool
# If error: Expecting value: line 1 column 1 (char 0) → file is corrupted
```

## Resolution Steps

### 1. Find Last Clean Commit

```bash
# Find commit before conflicts appeared
git log --oneline -135 | grep -v "auto: on-chain position update" | head -5

# Example clean commit: e363dc89
```

### 2. Reset to Clean Version

```bash
# Reset local branch to last clean commit
git reset --hard e363dc89

# Or restore specific file from that commit
git show e363dc89:DeFi/defi-data.json > DeFi/defi-data.json
```

### 3. Force Push to Fix Remote

```bash
# Add the clean file
git add DeFi/defi-data.json
git commit -m "fix: Resolve defi-data.json merge conflict - clean JSON restored"

# Force push to overwrite corrupted remote
git push origin main --force-with-lease
```

### 4. Verify Fix

```bash
# Wait for GitHub to propagate (5-10 seconds)
sleep 5

# Verify remote JSON is now valid
curl -s "https://raw.githubusercontent.com/.../defi-data.json" | python3 -m json.tool | head -10
```

## Prevention

### Pre-commit Hook

Add a pre-commit hook to validate JSON before push:

```bash
# .git/hooks/pre-commit
#!/bin/bash
for file in $(git diff --cached --name-only | grep '\.json$'); do
    if ! python3 -m json.tool "$file" > /dev/null; then
        echo "ERROR: Invalid JSON in $file"
        exit 1
    fi
done
```

### Merge Workflow

When resolving conflicts:

1. **Never** push unresolved conflicts
2. Use `git mergetool` for interactive resolution
3. Verify JSON validity after merge: `python3 -m json.tool file.json`
4. Run hub audit script before push

## Common Pitfall: Branch Confusion

If you're on a branch with the same name as remote:

```bash
# This creates confusion: commits on wrong branch
git add file.json && git commit && git push origin main

# Better: explicitly checkout main first
git checkout main && git add file.json && git commit && git push origin main
```

## Related Files

- Hub audit scripts for data validation: `scripts/check-hub-data.sh`
- Audit report template: `11-Mess Hall/hub-audit-YYYY-MM-DD.md`

## History

- **July 1, 2026** — Documented after fixing defi-data.json merge conflict (8 layers of conflict markers embedded in file)