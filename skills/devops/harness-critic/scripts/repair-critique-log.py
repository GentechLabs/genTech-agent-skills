#!/usr/bin/env python3
"""
Repair read_file line-number corruption in a markdown file.

When a prior Critic run reads the critique log with the read_file tool,
each line is prefixed with N|. If the Critic then appends its output
using a tool that includes those prefixes, they become embedded in the
file content, producing lines like:

    35|- Rationale: Recommendation is grounded in...

This script strips all such prefixes. It handles both single corruption
(N|) and double corruption (N|N|).

Usage:
    python3 repair-critique-log.py [path]

Default path: facts/critique-log.md
"""

import re
import sys
from pathlib import Path


def repair(path: str) -> int:
    p = Path(path)
    if not p.exists():
        print(f"File not found: {path}", file=sys.stderr)
        return 1

    b = p.read_bytes()
    text = b.decode()
    original = text

    lines = text.split('\n')
    fixed = []
    corruption_count = 0

    for line in lines:
        # Remove double corruption first: N|N|...
        while re.match(r'^\d+\|\d+\|', line):
            line = re.sub(r'^\d+\|', '', line)
            corruption_count += 1
        # Remove single corruption: N|...
        if re.match(r'^\d+\|', line):
            stripped = re.sub(r'^\d+\|', '', line)
            # Only strip if the result looks like legitimate content
            if stripped.startswith(('-', '##', '|', '[', '#', ' ', '')) or stripped == '':
                line = stripped
                corruption_count += 1
        fixed.append(line)

    text = '\n'.join(fixed)

    # Ensure trailing newline
    if not text.endswith('\n'):
        text += '\n'

    if text != original:
        p.write_text(text)
        print(f"Repaired {corruption_count} corrupted lines in {path}")
        return 0
    else:
        print(f"No corruption found in {path}")
        return 0


if __name__ == '__main__':
    path = sys.argv[1] if len(sys.argv) > 1 else 'facts/critique-log.md'
    sys.exit(repair(path))
