#!/usr/bin/env python3
"""
Hive Marketplace Task Analyzer
Fetches tasks from uphive.xyz REST API and generates a scored report.

Usage:
  1. curl -sL "https://uphive.xyz/api/tasks?limit=100" -o /tmp/hive_tasks.json
  2. python3 analyze_hive_tasks.py /tmp/hive_tasks.json

Output: Scored task list with relevance ratings, competition assessment, and recommendations.
"""
import json
import sys
from datetime import datetime, timezone

# Categories we're strong in
STRONG_CATEGORIES = {"Development", "Security", "Analysis", "Research"}
WEAK_CATEGORIES = {"Social", "Design", "Translation"}

# Tags that indicate high-value work
HIGH_VALUE_TAGS = {
    "smart contract", "defi", "blockchain", "solana", "anchor",
    "security audit", "penetration", "vulnerability",
    "api", "rest", "graphql",
    "python", "typescript", "rust",
    "documentation", "technical writing",
}

# Tags to skip
SKIP_TAGS = {"linkedin", "content strategy", "b2b marketing", "social media"}


def score_task(task):
    """Score a task 0-10 based on relevance and value."""
    score = 0
    cat = task.get("category", "")
    tags = [t.lower() for t in task.get("tags", [])]
    budget = task.get("budgetAmount", 0)
    proposals = task.get("proposalsCount", 0)

    # Category match (0-3)
    if cat in STRONG_CATEGORIES:
        score += 3
    elif cat in WEAK_CATEGORIES:
        score -= 2

    # Tag alignment (0-4)
    for tag in tags:
        for hv in HIGH_VALUE_TAGS:
            if hv in tag:
                score += 2
                break
        for sk in SKIP_TAGS:
            if sk in tag:
                score -= 1
                break

    # Competition (0-2)
    if proposals <= 2:
        score += 2
    elif proposals <= 4:
        score += 1
    elif proposals >= 6:
        score -= 1

    # Budget (0-2)
    if budget >= 10:
        score += 2
    elif budget >= 5:
        score += 2
    elif budget >= 3:
        score += 1

    return max(0, min(10, score))


def star_rating(score):
    """Convert numeric score to star rating."""
    if score >= 7:
        return "★★★★★"
    elif score >= 5:
        return "★★★★☆"
    elif score >= 3:
        return "★★★☆☆"
    elif score >= 1:
        return "★★☆☆☆"
    else:
        return "★☆☆☆☆"


def analyze(data_path):
    with open(data_path) as f:
        data = json.load(f)

    tasks = data.get("tasks", [])
    now = datetime.now(timezone.utc)

    # Status breakdown
    statuses = {}
    for t in tasks:
        s = t.get("status", "Unknown")
        statuses[s] = statuses.get(s, 0) + 1

    # Category breakdown
    cats = {}
    for t in tasks:
        c = t.get("category", "Unknown")
        cats[c] = cats.get(c, 0) + 1

    # Budget stats
    budgets = [t.get("budgetAmount", 0) for t in tasks if t.get("budgetAmount")]

    # Open tasks (scored)
    open_tasks = [t for t in tasks if t.get("status") == "Open"]
    for t in open_tasks:
        t["_score"] = score_task(t)
    open_tasks.sort(key=lambda x: x["_score"], reverse=True)

    # Recently created (last 48h)
    recent = []
    for t in tasks:
        try:
            dt = datetime.fromisoformat(t["createdAt"].replace("Z", "+00:00"))
            if (now - dt).total_seconds() < 48 * 3600:
                recent.append(t)
        except Exception:
            pass

    # Output
    print(f"=== HIVE MARKETPLACE ANALYSIS ===")
    print(f"Total tasks: {len(tasks)}")
    print(f"Status: {statuses}")
    print(f"Budget: min=${min(budgets) if budgets else 0}, max=${max(budgets) if budgets else 0}, avg=${sum(budgets)/len(budgets):.2f}" if budgets else "No budget data")
    print()

    print(f"=== CATEGORIES ===")
    for c, n in sorted(cats.items(), key=lambda x: -x[1]):
        print(f"  {c}: {n}")
    print()

    print(f"=== OPEN TASKS ({len(open_tasks)}) ===")
    for t in open_tasks:
        s = t["_score"]
        print(f"\n{star_rating(s)} (score={s}) | {t['title']}")
        print(f"  Budget: {t.get('budget', 'N/A')} | Proposals: {t.get('proposalsCount', 0)} | Category: {t.get('category', 'N/A')}")
        print(f"  Tags: {t.get('tags', [])}")
        print(f"  Client: {t.get('clientName', 'N/A')} | Created: {t.get('createdAt', 'N/A')[:10]}")
        print(f"  URL: {t.get('url', 'N/A')}")

    print(f"\n=== RECENT TASKS (last 48h): {len(recent)} ===")
    for t in recent:
        print(f"  [{t.get('status')}] {t['title']} | {t.get('budget')} | {t.get('proposalsCount')} proposals")

    return open_tasks


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "/tmp/hive_tasks.json"
    analyze(path)
