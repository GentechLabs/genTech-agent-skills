#!/usr/bin/env python3
"""
Cross-reference predictions.md against prediction-outcomes.md and report
which past-due predictions are missing outcomes.

Usage:
    python3 check-prediction-outcomes.py [predictions.md] [outcomes.md]

Default paths: facts/predictions.md facts/prediction-outcomes.md
Exit code: 0 if all past-due predictions have outcomes, 1 if any are missing.
"""

import re
import sys
from datetime import datetime, timezone
from pathlib import Path


def parse_predictions(path: str) -> dict:
    """Return {prediction_number: due_cycle_count} for all predictions."""
    text = Path(path).read_text()
    results = {}
    # Match: ## PREDICTION #N — <ISO8601>
    for m in re.finditer(r'^## PREDICTION #(\d+).*?\n(?:.*?\n)*?DUE: (\d+)', text, re.MULTILINE):
        num = int(m.group(1))
        due_cycles = int(m.group(2))
        results[num] = due_cycles
    return results


def parse_outcomes(path: str) -> set[int]:
    """Return set of prediction numbers that have outcomes recorded."""
    text = Path(path).read_text()
    return {int(m.group(1)) for m in re.finditer(r'PREDICTION #(\d+)', text)}


def main():
    pred_path = sys.argv[1] if len(sys.argv) > 1 else 'facts/predictions.md'
    out_path = sys.argv[2] if len(sys.argv) > 2 else 'facts/prediction-outcomes.md'

    predictions = parse_predictions(pred_path)
    outcomes = parse_outcomes(out_path)

    missing = set(predictions.keys()) - outcomes

    if not missing:
        print(f"All {len(predictions)} predictions have outcomes recorded.")
        return 0

    print(f"MISSING OUTCOMES for {len(missing)} prediction(s):")
    for num in sorted(missing):
        due = predictions[num]
        print(f"  PREDICTION #{num} (due in {due} cycle(s))")
    return 1


if __name__ == '__main__':
    sys.exit(main())
