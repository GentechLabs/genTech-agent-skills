# JSON Merge Conflict Sanitizer — Reference Implementation

Copy these functions into any script that reads JSON files shared via git.
Handles: conflict markers, BOM, trailing commas, missing commas after conflict removal,
rebase-introduced markers, and vault-fallback recovery.

## Imports Needed

```python
import json
import os
import re
import subprocess
```

## Function 1: sanitize_json_text

```python
def sanitize_json_text(text):
    """Strip merge conflict markers and common JSON corruption from raw text.

    Keeps the "theirs" side (between ======= and >>>>>>>) since during a
    rebase/pull, "theirs" is what's on the remote. Also auto-fixes trailing
    commas and missing commas caused by conflict removal.
    """
    lines = text.splitlines(keepends=True)
    clean = []
    in_conflict = False
    keep_side = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('<<<<<<< '):
            in_conflict = True
            keep_side = False
            continue
        if stripped == '=======' and in_conflict:
            keep_side = True
            continue
        if stripped.startswith('>>>>>>> ') and in_conflict:
            in_conflict = False
            keep_side = False
            continue
        if not in_conflict:
            clean.append(line)
        elif keep_side:
            clean.append(line)
    cleaned = ''.join(clean)
    # Strip BOM
    cleaned = cleaned.lstrip('\ufeff')
    # Fix trailing commas before closing braces/brackets
    cleaned = re.sub(r',\s*}', '}', cleaned)
    cleaned = re.sub(r',\s*]', ']', cleaned)
    # Fix missing commas between object entries (after conflict removal)
    cleaned = re.sub(r'("\s*:\s*[^,{}\\[\]]+)\s*\n(\s*")', r'\1,\n\2', cleaned)
    # Fix missing commas in arrays
    cleaned = re.sub(r']\s*\n\s*"', '],\n"', cleaned)
    return cleaned
```

## Function 2: load_json_safe

```python
def load_json_safe(path):
    """Load a JSON file, sanitizing merge conflict artifacts first.

    Returns (parsed_dict, error_string). error_string is None on success.

    If the file had to be cleaned, the clean version is written back
    to prevent recurrence on subsequent reads.
    """
    if not os.path.exists(path):
        return None, f"{path} not found"
    try:
        with open(path, 'r') as f:
            raw = f.read()
        cleaned = sanitize_json_text(raw)
        data = json.loads(cleaned)
        if cleaned != raw:
            with open(path, 'w') as f:
                f.write(cleaned)
        return data, None
    except json.JSONDecodeError as e:
        return None, f"Invalid JSON in {path}: {e}"
    except Exception as e:
        return None, f"Error reading {path}: {e}"
```

## Function 3: Pre-Commit Conflict Check

```python
def check_and_clean_conflicts(file_path):
    """Scan file for merge conflict markers, strip if found.

    Returns True if file was cleaned, False if already clean.
    Use this before git commit to prevent pushing corrupted files.
    """
    with open(file_path, 'r') as f:
        raw = f.read()
    if '<<<<<<<' in raw or '=======' in raw or '>>>>>>>' in raw:
        clean = sanitize_json_text(raw)
        with open(file_path, 'w') as f:
            f.write(clean)
        return True
    return False
```

## Function 4: Post-Rebase Conflict Check (⚠️ Critical Timing Fix)

**Don't rely on pre-commit scan alone.** If your push flow does `git pull --rebase` after commit, the rebase can introduce NEW conflict markers that the pre-commit scan (Function 3) never saw. This function catches those — run it AFTER `git add -u` and AFTER rebase conflict resolution, RIGHT BEFORE `git rebase --continue`.

```python
def check_post_rebase(repo_path, staged_files):
    """Scan staged files for rebase-introduced conflict markers.
    
    Call this AFTER git add -u and BEFORE git rebase --continue.
    If markers found: strips them, re-stages, amends the rebase commit.
    
    Returns True if file was cleaned, False if already clean.
    """
    cleaned_any = False
    for f in staged_files:
        full_path = os.path.join(repo_path, f)
        if not os.path.exists(full_path):
            continue
        with open(full_path, 'r') as fh:
            raw = fh.read()
        if '<<<<<<<' in raw or '=======' in raw or '>>>>>>>' in raw:
            clean = sanitize_json_text(raw)
            with open(full_path, 'w') as fh:
                fh.write(clean)
            subprocess.run(["git", "add", full_path], 
                          cwd=repo_path, check=True, capture_output=True)
            cleaned_any = True
    if cleaned_any:
        # Amend the rebase commit to replace corrupted version
        subprocess.run(["git", "commit", "--amend", "--no-edit"],
                      cwd=repo_path, check=False)
    return cleaned_any
```

## Function 5: Vault-Fallback Recovery (NEW — Jul 15, 2026)

**When to use:** AFTER `check_post_rebase()` has been called and AFTER `git rebase --continue` is complete, but when the JSON is STILL invalid after sanitization. This happens when `sanitize_json_text()` strips markers but leaves the JSON structurally incomplete (missing closing `}`, `]`, or structural commas).

**Why it works:** In the standard push-flow, the vault file was written by the update function BEFORE `push_to_github()` runs. So the vault always has a valid, authoritative copy that post-dates the repo working copy.

```python
def vault_fallback_recovery(staged_file, vault_source, repo_path, errors):
    """If JSON is still invalid after sanitization, re-copy from vault.

    Returns True if recovery succeeded, False if vault copy is also corrupted.

    Call this after check_post_rebase() and rebase --continue, but before git push.
    """
    with open(staged_file) as f:
        try:
            json.load(f)
            return True  # already valid, no recovery needed
        except json.JSONDecodeError as e:
            errors.append(f"🔴 JSON invalid after post-rebase clean: {e}")
    
    # Vault fallback: re-copy from authoritative source
    subprocess.run(f"cp {vault_source} {staged_file}", shell=True, check=True)
    subprocess.run(f"cd {repo_path} && git add {staged_file}", shell=True, capture_output=True)
    errors.append("🔄 Re-copied from vault — re-verifying…")
    
    with open(staged_file) as f2:
        try:
            json.load(f2)
            errors.append("✅ Vault copy valid — continuing")
            return True
        except json.JSONDecodeError as e2:
            errors.append(f"🔴 Vault copy also invalid: {e2}")
            return False
```

## Vault-Fallback Integration Example (hub-sync-nightly.py pattern)

Here's how Functions 4 and 5 compose in the actual `push_to_github()` flow:

```python
def push_to_github():
    # ... copy file, commit ...

    # Pull rebase first to handle remote divergence
    rebase_out, rebase_rc = run_cmd(f"cd {REPO_PATH} && git pull --rebase origin main", timeout=60)
    if rebase_rc != 0:
        # Rebase conflicted — auto-resolve with theirs
        run_cmd(f"cd {REPO_PATH} && git add -u", timeout=15)

        # Step A: Strip any conflict markers from staged files
        check_post_rebase(REPO_PATH, ["DeFi/defi-data.json"])

        # Step B: Check if JSON is still structurally broken (missing closing braces)
        vault_fallback_recovery(
            staged_file=f"{REPO_PATH}/DeFi/defi-data.json",
            vault_source="/root/vaults/gentech/defi-data.json",
            repo_path=REPO_PATH,
            errors=errors
        )

        # Step C: Continue the rebase (required after conflict resolution)
        run_cmd(f"cd {REPO_PATH} && GIT_EDITOR=true git rebase --continue", timeout=30)

    # Pre-push JSON validation
    with open(f"{REPO_PATH}/DeFi/defi-data.json") as f:
        try:
            json.load(f)
        except json.JSONDecodeError as e:
            errors.append(f"🔴 Pre-push validation failed: {e} — data not pushed")
            return "corrupted", errors

    # Push with retry
    for attempt in range(3):
        out, rc = run_cmd(f"cd {REPO_PATH} && git push", timeout=30)
        if rc == 0:
            break
    return "pushed", errors
```

## Complete Push Function (All 4 Layers)

```python
def push_to_github(repo_path, data_path, vault_source):
    """Copy data → commit → rebase → check → recover → push.
    Guards against pre-existing corruption AND rebase-introduced corruption.
    """

    # Step 1: Copy and pre-commit scan (Layer 3)
    staged = "DeFi/defi-data.json"
    staged_full = os.path.join(repo_path, staged)
    shutil.copy(data_path, staged_full)
    if check_and_clean_conflicts(staged_full):
        print("⚠️ Pre-commit: stripped conflict markers")

    # Step 2: Commit
    subprocess.run(["git", "add", staged], cwd=repo_path, check=True)
    subprocess.run(["git", "commit", "-m", "Nightly hub sync"], cwd=repo_path, check=True)

    # Step 3: Pull rebase (may introduce conflicts)
    subprocess.run(["git", "pull", "--rebase", "origin", "main"],
                  cwd=repo_path, check=False, capture_output=True)

    # Step 4: Stage all rebase results
    subprocess.run(["git", "add", "-u"], cwd=repo_path, check=True)

    # Step 5: Post-rebase conflict check (Layer 3.5)
    check_post_rebase(repo_path, [staged])

    # Step 6: Vault-fallback recovery if sanitized JSON is structurally broken (Layer 4)
    errors = []
    vault_fallback_recovery(staged_full, vault_source, repo_path, errors)
    for e in errors:
        print(f"  {e}")

    # Step 7: Continue the rebase (critical!)
    subprocess.run(["git", "rebase", "--continue"], cwd=repo_path, 
                   check=False, capture_output=True)

    # Step 8: Pre-push validation (final gate)
    try:
        json.load(open(staged_full))
    except json.JSONDecodeError as e:
        print(f"🔴 Pre-push validation failed: {e}")
        return False

    # Step 9: Push with retry
    for attempt in range(3):
        result = subprocess.run(["git", "push"], cwd=repo_path, 
                               capture_output=True, text=True)
        if result.returncode == 0:
            return True
    return False
```

## Test Suite

```python
def test_sanitize_json():
    # Test 1: Basic conflict — keeps theirs
    corrupted = '''{\n      "test": 1,\n    <<<<<<< HEAD\n      "value": "old"\n    =======\n      "value": "new"\n    >>>>>>> branch\n    }\n    '''
    data = json.loads(sanitize_json_text(corrupted))
    assert data == {"test": 1, "value": "new"}, f"Test 1: {data}"

    # Test 2: Nested conflict
    nested = '''{\n      "items": [\n    <<<<<<< HEAD\n        "first"\n    =======\n        "changed"\n    >>>>>>> branch\n      ]\n    }\n    '''
    data = json.loads(sanitize_json_text(nested))
    assert data == {"items": ["changed"]}, f"Test 2: {data}"

    # Test 3: Clean passthrough
    assert sanitize_json_text('{"a": 1}') == '{"a": 1}'

    # Test 4: BOM stripped
    assert sanitize_json_text('\ufeff{"x": 1}') == '{"x": 1}'

    # Test 5: Realistic nested object conflict
    realistic = '''{\n      "pool": "AVAX/USDC",\n      "price": 6.43,\n      "lpPosition": {\n    <<<<<<< HEAD\n        "inRange": true\n    =======\n        "inRange": false\n    >>>>>>> branch\n      },\n      "fees": {\n        "daily": 0.05,\n        "cumulative": 1.23\n      }\n    }\n    '''
    data = json.loads(sanitize_json_text(realistic))
    assert data["lpPosition"]["inRange"] == False
    assert data["fees"]["daily"] == 0.05

    print("All 5 tests passed ✅")
```

## Usage Pattern for Cron Scripts

Replace bare `json.load()` calls with `load_json_safe()`:

```python
# BEFORE (brittle):
with open(path, 'r') as f:
    data = json.load(f)

# AFTER (resilient):
data, err = load_json_safe(path)
if err:
    print(f"⚠️ {err}")
    data = {}  # fallback
```

Add pre-commit scan to git push functions:

```python
if check_and_clean_conflicts(staged_file):
    print("⚠️ Stripped merge conflict markers before commit")
```
