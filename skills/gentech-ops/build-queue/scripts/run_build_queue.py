#!/usr/bin/env python3
"""
Build Queue Runner — Autonomous pipeline processor (GENERIC VERSION).

Reads build_queue.json, runs tests for each pending item,
commits passing modules, generates a report.

Usage:
    python3 run_build_queue.py              # Run all pending items
    python3 run_build_queue.py --item ID    # Run specific item
    python3 run_build_queue.py --report     # Just generate report
    python3 run_build_queue.py --status     # Show queue status

Customize: Set VAULT to your project root.
"""

import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# ── CONFIGURE THIS ──────────────────────────────────────────────────────
VAULT = Path(os.environ.get("PROJECT_ROOT", "."))
QUEUE_FILE = VAULT / "build_queue.json"
REPORT_DIR = VAULT / "reports"
# ────────────────────────────────────────────────────────────────────────


def load_queue() -> dict:
    with open(QUEUE_FILE) as f:
        return json.load(f)


def save_queue(data: dict):
    data["last_updated"] = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    with open(QUEUE_FILE, "w") as f:
        json.dump(data, f, indent=2)


def run_tests(item: dict) -> dict:
    """Run tests for a build queue item."""
    item_path = VAULT / item["path"]
    test_cmd = item["test_cmd"]

    if not item_path.exists():
        return {"status": "error", "error": f"Dir not found: {item_path}",
                "tests_passed": 0, "tests_total": 0, "duration_s": 0}

    start = time.time()
    try:
        result = subprocess.run(test_cmd, shell=True, cwd=str(item_path),
                                capture_output=True, text=True, timeout=120)
        duration = time.time() - start
        output = result.stdout + result.stderr

        passed = 0
        total = 0
        for line in output.split("\n"):
            if "Results:" in line and "passed" in line:
                try:
                    parts = line.split("Results:")[1].split("passed")[0].strip()
                    p, t = parts.split("/")
                    passed, total = int(p.strip()), int(t.strip())
                    break
                except (ValueError, IndexError):
                    pass

        if total == 0:
            passed = output.count("✅")
            total = passed + output.count("❌")

        status = "shipped" if result.returncode == 0 and total > 0 else "failed"
        return {"status": status, "tests_passed": passed, "tests_total": total,
                "exit_code": result.returncode, "duration_s": round(duration, 1),
                "output": output[-2000:], "error": result.stderr if result.returncode != 0 else ""}
    except subprocess.TimeoutExpired:
        return {"status": "timeout", "error": "Timed out (120s)",
                "tests_passed": 0, "tests_total": 0, "duration_s": 120}
    except Exception as e:
        return {"status": "error", "error": str(e),
                "tests_passed": 0, "tests_total": 0, "duration_s": 0}


def git_commit(item: dict, result: dict) -> bool:
    if result["status"] != "shipped":
        return False
    item_path = VAULT / item["path"]
    try:
        subprocess.run(["git", "add", str(item_path)], cwd=str(VAULT), capture_output=True, timeout=10)
        subprocess.run(["git", "commit", "-m",
                        f"build(queue): {item['name']} — {result['tests_passed']}/{result['tests_total']} tests"],
                       cwd=str(VAULT), capture_output=True, timeout=10)
        return True
    except Exception:
        return False


def generate_report(results: list, queue_data: dict) -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = [f"🔧 BUILD QUEUE REPORT", f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━", f"📅 {now}", ""]

    shipped = [r for r in results if r["result"]["status"] == "shipped"]
    failed = [r for r in results if r["result"]["status"] == "failed"]
    errors = [r for r in results if r["result"]["status"] in ("error", "timeout")]

    total_tests = sum(r["result"]["tests_passed"] for r in results if r["result"]["status"] == "shipped")
    total_time = sum(r["result"]["duration_s"] for r in results)

    lines.append(f"📊 SUMMARY")
    lines.append(f"   ✅ Shipped: {len(shipped)}")
    lines.append(f"   ❌ Failed: {len(failed)}")
    lines.append(f"   ⚠️  Errors: {len(errors)}")
    lines.append(f"   🧪 Total tests: {total_tests}")
    lines.append(f"   ⏱️  Total time: {total_time:.1f}s")
    lines.append("")

    if shipped:
        lines.append("✅ SHIPPED")
        for r in shipped:
            res = r["result"]
            lines.append(f"   • {r['item']['name']} — {res['tests_passed']}/{res['tests_total']} tests ({res['duration_s']}s)")
        lines.append("")

    if failed:
        lines.append("❌ FAILED")
        for r in failed:
            res = r["result"]
            lines.append(f"   • {r['item']['name']} — {res['tests_passed']}/{res['tests_total']}")
            for line in res.get("output", "").strip().split("\n")[-3:]:
                lines.append(f"     {line}")
        lines.append("")

    if errors:
        lines.append("⚠️ ERRORS")
        for r in errors:
            lines.append(f"   • {r['item']['name']} — {r['result'].get('error', '?')[:100]}")
        lines.append("")

    lines.append("📋 FULL QUEUE STATUS")
    emojis = {"shipped": "✅", "building": "🔨", "pending": "⏳", "failed": "❌"}
    for item in queue_data["items"]:
        e = emojis.get(item["status"], "❓")
        lines.append(f"   {e} {item['name']} — {item['status']} ({item['tests']})")

    lines.append("")
    lines.append(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    lines.append(f"💰 {len(shipped)} products ready")
    return "\n".join(lines)


def main():
    args = sys.argv[1:]
    queue_data = load_queue()

    if "--status" in args:
        emojis = {"shipped": "✅", "building": "🔨", "pending": "⏳", "failed": "❌"}
        print(f"📋 Build Queue — {len(queue_data['items'])} items")
        for item in queue_data["items"]:
            print(f"  {emojis.get(item['status'], '❓')} {item['name']} — {item['status']} ({item['tests']})")
        return

    if "--report" in args:
        results = []
        for item in queue_data["items"]:
            if item["status"] in ("shipped", "building"):
                result = run_tests(item)
                results.append({"item": item, "result": result})
                item["tests"] = f"{result['tests_passed']}/{result['tests_total']}"
                if result["status"] == "shipped":
                    item["status"] = "shipped"
        save_queue(queue_data)
        print(generate_report(results, queue_data))
        return

    target_id = None
    for i, arg in enumerate(args):
        if arg == "--item" and i + 1 < len(args):
            target_id = args[i + 1]

    items_to_run = []
    for item in queue_data["items"]:
        if target_id:
            if item["id"] == target_id:
                items_to_run.append(item)
        elif item["status"] in ("pending", "building"):
            items_to_run.append(item)

    if not items_to_run:
        print("✅ No pending items. Queue up to date.")
        return

    print(f"🔧 Running {len(items_to_run)} item(s)...\n")
    results = []
    for item in items_to_run:
        print(f"🔨 {item['name']}...")
        result = run_tests(item)
        results.append({"item": item, "result": result})
        item["tests"] = f"{result['tests_passed']}/{result['tests_total']}"
        if result["status"] == "shipped":
            item["status"] = "shipped"
            git_commit(item, result)
            print(f"  ✅ {result['tests_passed']}/{result['tests_total']} ({result['duration_s']}s)")
        elif result["status"] == "failed":
            item["status"] = "failed"
            print(f"  ❌ {result['tests_passed']}/{result['tests_total']}")
        else:
            print(f"  ⚠️  {result.get('error', '?')[:80]}")
        print()

    save_queue(queue_data)
    report = generate_report(results, queue_data)
    print(report)

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    rpt = REPORT_DIR / f"build-report-{datetime.now().strftime('%Y-%m-%d-%H%M')}.md"
    with open(rpt, "w") as f:
        f.write(report)
    print(f"\n📄 Report: {rpt}")


if __name__ == "__main__":
    main()
