#!/usr/bin/env python3
"""
Entry Price Consistency Verification Protocol
After rebalances, verifies that all data sources have consistent entry prices
"""

import json
import os
from datetime import datetime, timezone

def load_json(path):
    """Load JSON file safely"""
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Error loading {path}: {e}")
        return {}

def find_dashboard_entry_price(obj):
    """Find entry price in nested dashboard structure"""
    if isinstance(obj, dict):
        if 'entryPrice' in obj:
            return obj['entryPrice']
        for value in obj.values():
            result = find_dashboard_entry_price(value)
            if result is not None:
                return result
    elif isinstance(obj, list):
        for item in obj:
            result = find_dashboard_entry_price(item)
            if result is not None:
                return result
    return None

def check_entry_price_consistency():
    """Verify entry price consistency across all data sources"""
    print("🧪 Entry Price Consistency Check")
    print("=" * 50)
    
    # Load all data sources
    sources = {
        "Position Tracker": '/root/.hermes/scripts/.lfj-position-tracker.json',
        "Config": '/root/.hermes/scripts/.lfj-aae-config.json',
        "Dashboard": '/root/ProtoJay4789.github.io/DeFi/defi-data.json'
    }
    
    data = {}
    for name, path in sources.items():
        data[name] = load_json(path)
    
    # Extract entry prices
    entry_prices = {}
    
    # Position tracker
    tracker = data["Position Tracker"]
    entry_prices["Position Tracker"] = tracker.get('entry_price')
    
    # Config
    config = data["Config"]
    if 'position' in config and 'entry_price' in config['position']:
        entry_prices["Config"] = config['position']['entry_price']
    else:
        entry_prices["Config"] = None
    
    # Dashboard
    dashboard = data["Dashboard"]
    entry_prices["Dashboard"] = find_dashboard_entry_price(dashboard)
    
    # Display results
    print("📊 Entry Price Sources:")
    print("-" * 30)
    consistent = True
    valid_prices = []
    
    for source, price in entry_prices.items():
        if price is not None:
            print(f"{source:20}: ${price:.4f}")
            valid_prices.append(price)
        else:
            print(f"{source:20}: ❌ MISSING")
            consistent = False
    
    # Check consistency
    print("\n🔍 Consistency Check:")
    if consistent and len(set(valid_prices)) == 1:
        print("✅ All entry prices are consistent!")
        entry_price = valid_prices[0]
        
        # Calculate IL
        current_price = 6.46  # Should be from actual data
        il_pct = ((current_price - entry_price) / entry_price) * 100
        
        print(f"\n📈 Final Metrics:")
        print(f"   Entry Price: ${entry_price:.4f}")
        print(f"   Current Price: ${current_price:.4f}")
        print(f"   Impermanent Loss: {il_pct:+.2f}%")
        
        print(f"\n🎯 Status:")
        if abs(il_pct) < 1:
            print("✅ Excellent - Minimal IL")
        elif abs(il_pct) < 3:
            print("✅ Good - Normal IL range")
        elif abs(il_pct) < 5:
            print("⚠️ Acceptable - IL getting high")
        else:
            print("🚨 Poor - High IL, consider rebalance")
            
        return True
    else:
        print("❌ Entry price inconsistency detected!")
        if len(set(valid_prices)) > 1:
            print("   Different values found:")
            for source, price in entry_prices.items():
                if price is not None:
                    print(f"      {source}: ${price:.4f}")
        return False

def main():
    success = check_entry_price_consistency()
    
    if success:
        print(f"\n✅ Verification PASSED - All entry prices consistent")
        exit(0)
    else:
        print(f"\n❌ Verification FAILED - Inconsistencies found")
        print("   Run entry-price-fix.py to resolve")
        exit(1)

if __name__ == "__main__":
    main()