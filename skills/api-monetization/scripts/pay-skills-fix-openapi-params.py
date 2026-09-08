#!/usr/bin/env python3
"""Add missing OpenAPI parameters to all GET endpoints in pay-skills PAY.md files.

Usage:
    python3 pay-skills-fix-openapi-params.py

    Scans providers/gentech/*/PAY.md and adds 'parameters' arrays to every
    GET endpoint that lacks them. Uses the PARAM_MAP below to determine
    which parameters to add per operationId.

    To adapt for other edits, modify the modifier_fn() instead.
"""

import re
import json
import os

PROVIDERS_DIR = "providers/gentech"

# Parameters by operationId — add/edit entries here to cover new endpoints
PARAM_MAP = {
    "api_agentscan": [
        {"name": "q", "in": "query", "required": True, "schema": {"type": "string"},
         "description": "Search query for agent discovery"}
    ],
    "api_airdrops_check": [
        {"name": "wallet", "in": "query", "required": True, "schema": {"type": "string"},
         "description": "Wallet address to check for airdrop eligibility"}
    ],
    "api_games_search": [
        {"name": "q", "in": "query", "required": True, "schema": {"type": "string"},
         "description": "Game title search query"}
    ],
    "api_games_cheapest": [
        {"name": "title", "in": "query", "required": True, "schema": {"type": "string"},
         "description": "Game title to find cheapest price for"}
    ],
    "api_games_news": [
        {"name": "q", "in": "query", "required": True, "schema": {"type": "string"},
         "description": "Search query for gaming news and patch notes"}
    ],
    "api_games_release": [
        {"name": "title", "in": "query", "required": True, "schema": {"type": "string"},
         "description": "Game title to look up release info"}
    ],
    "api_intel_search": [
        {"name": "q", "in": "query", "required": True, "schema": {"type": "string"},
         "description": "Product search query across games and movies"}
    ],
    "api_intel_cheapest": [
        {"name": "q", "in": "query", "required": True, "schema": {"type": "string"},
         "description": "Product name to find cheapest option"}
    ],
    "api_movies_search": [
        {"name": "q", "in": "query", "required": True, "schema": {"type": "string"},
         "description": "Movie title search query"}
    ],
    "api_movies_cheapest": [
        {"name": "title", "in": "query", "required": True, "schema": {"type": "string"},
         "description": "Movie title to find cheapest watch option"}
    ],
    "api_movies_details": [
        {"name": "title", "in": "query", "required": True, "schema": {"type": "string"},
         "description": "Movie title to get details for"},
        {"name": "id", "in": "query", "required": False, "schema": {"type": "string"},
         "description": "Optional movie ID for precise lookup"}
    ],
    "api_movies_trailers": [
        {"name": "title", "in": "query", "required": True, "schema": {"type": "string"},
         "description": "Movie title to find trailers for"}
    ],
    "api_nft_search": [
        {"name": "collection", "in": "query", "required": True, "schema": {"type": "string"},
         "description": "NFT collection slug or contract address"}
    ],
    "api_shipping_track": [
        {"name": "tracking", "in": "query", "required": True, "schema": {"type": "string"},
         "description": "Tracking number to look up"},
        {"name": "carrier", "in": "query", "required": False,
         "schema": {"type": "string", "enum": ["ups", "fedex", "usps", "dhl", "auto"]},
         "description": "Carrier code (auto-detect by default)"}
    ],
    "api_token_risk": [
        {"name": "mint", "in": "query", "required": True, "schema": {"type": "string"},
         "description": "Token mint address to analyze"}
    ],
    "api_wallet_analyze": [
        {"name": "address", "in": "query", "required": True, "schema": {"type": "string"},
         "description": "Wallet address to analyze"}
    ],
}


def modifier_fn(spec):
    """Add parameters to every operation that needs them."""
    for _path, path_item in spec.get("paths", {}).items():
        for method, operation in path_item.items():
            op_id = operation.get("operationId", "")
            if op_id in PARAM_MAP and "parameters" not in operation:
                operation["parameters"] = PARAM_MAP[op_id]
    return spec


def edit_openapi_in_pay_md(filepath, modifier_fn):
    """Edit inline OpenAPI JSON in a PAY.md via the modifier_fn pattern."""
    with open(filepath) as f:
        content = f.read()

    m = re.search(r"openapi:\s*\n\s+content:\s*\|\s*\n", content)
    if not m:
        return 0

    start = m.end()
    lines = content[start:].split("\n")
    first = lines[0]
    indent = len(first) - len(first.lstrip())

    json_lines = []
    for line in lines:
        if line.strip() == "":
            json_lines.append(line)
            continue
        line_indent = len(line) - len(line.lstrip())
        if line_indent < indent and line.strip():
            break
        json_lines.append(line)

    json_text = "\n".join(json_lines)
    try:
        spec = json.loads(json_text)
    except json.JSONDecodeError as e:
        print(f"  ERROR: JSON decode failed in {filepath}: {e}")
        return 0

    old_spec = json.dumps(spec)
    spec = modifier_fn(spec)
    if json.dumps(spec) == old_spec:
        return 0  # no changes

    new_json = json.dumps(spec, indent=4)
    indented = "\n".join(" " * indent + line for line in new_json.split("\n"))

    content = content[:start] + indented + content[start + len(json_text) :]
    with open(filepath, "w") as f:
        f.write(content)
    return 1


def main():
    if not os.path.isdir(PROVIDERS_DIR):
        print(f"ERROR: {PROVIDERS_DIR}/ not found. Run from the pay-skills repo root.")
        return 1

    total = 0
    for d in sorted(os.listdir(PROVIDERS_DIR)):
        dp = os.path.join(PROVIDERS_DIR, d)
        if os.path.isdir(dp):
            pay = os.path.join(dp, "PAY.md")
            if os.path.exists(pay):
                result = edit_openapi_in_pay_md(pay, modifier_fn)
                if result:
                    print(f"  {d}: updated")
                    total += 1
    print(f"Done: {total} file(s) modified.")
    return 0


if __name__ == "__main__":
    exit(main())
