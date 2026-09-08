# Weekly Report — Tiered Discount Formatter

## Purpose
`weekly_report.py` generates the formatted weekly deal sweep report for cron delivery. Replaces raw `cmd_check()` output with proper tiered classification.

## Usage
```bash
python3 /root/vaults/gentech/10-Labs/deal-tracker/weekly_report.py
```

## Output Format
- 🔥 Deep Cuts (50%+ off)
- 💰 Solid Sales (25-49% off)
- 🏷️ Light Marks (10-24% off)
- 📉 Barely Touching It (<10%)
- 🚨 Unreleased / Upcoming

## How It Works
1. Loads `watchlist.json` (handles both `items` and `games` keys)
2. For each game, calls `CheapSharkClient.get_cheapest_price()` with title search
3. Calculates discount from `normal_price` vs `sale_price`
4. Classifies into tiers using the same logic as `Deal.discount_tier`
5. Detects subscription-only pricing (XP, Member suffix in store name)
6. Groups unreleased games (no price data) separately

## Dependencies
- `deal_tracker.py` — CheapSharkClient, Deal dataclass
- `watchlist.json` — must be synced first via `deal_runner.py sync-steam`

## Notes
- Created 2026-06-24 because `cmd_check()` output was flat/unformatted
- The Deal class already has `discount_tier` and `discount_tier_emoji` properties but they weren't used in the CLI output
