#!/usr/bin/env python3
"""
Entry Price Field Validator & Fixer
====================================

This script detects and fixes entry price field naming conflicts
across the DeFi system that cause incorrect IL calculations and
efficiency tracking.

PROBLEM: Multiple files had both `entry_avax_price` (deprecated) 
and `entry_price` (current) fields, causing cron jobs to use 
the wrong values.

USAGE:
    python3 entry-price-field-validator.py [--fix]
    
    --fix: Automatically apply fixes
    --dry-run: Show what would be changed without doing it
    
EXAMPLES:
    # Check for conflicts
    python3 entry-price-field-validator.py
    
    # Auto-fix conflicts
    python3 entry-price-field-validator.py --fix
    
    # Preview changes
    python3 entry-price-field-validator.py --dry-run
"""

import json
import os
import glob
import sys
import argparse
from pathlib import Path


def find_all_config_files():
    """Find all configuration files that might have entry price fields"""
    patterns = [
        '/root/.hermes/scripts/.lfj-position-tracker.json',
        '/root/.hermes/profiles/gentech/scripts/.lfj-position-tracker.json',
        '/root/.hermes/**/scripts/.lfj-aae-config.json'
    ]
    
    files = []
    for pattern in patterns:
        if '*' in pattern:
            # Handle recursive pattern
            for file_path in glob.glob(pattern, recursive=True):
                if os.path.exists(file_path):
                    files.append(file_path)
        else:
            if os.path.exists(pattern):
                files.append(pattern)
    
    return list(set(files))  # Remove duplicates


def check_file_for_conflicts(file_path):
    """Check a single file for entry price field conflicts"""
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        old_field = data.get('entry_avax_price')
        new_field = data.get('entry_price')
        
        conflicts = []
        
        if old_field is not None and new_field is not None:
            # Both fields exist - conflict
            conflicts.append({
                'type': 'both_fields_exist',
                'old_value': old_field,
                'new_value': new_field,
                'magnitude': abs(old_field - new_field)
            })
        
        elif old_field is not None and new_field is None:
            # Only old field exists - needs migration
            conflicts.append({
                'type': 'only_old_field',
                'old_value': old_field,
                'recommended_fix': f"Set entry_price = {old_field}"
            })
        
        elif new_field is not None and old_field is not None:
            # Only new field exists - good
            pass
        
        else:
            # No entry price fields found
            pass
        
        return conflicts
    
    except Exception as e:
        return [{
            'type': 'read_error',
            'error': str(e)
        }]


def apply_fix_to_file(file_path, conflicts):
    """Apply fix to a single file"""
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        changes_made = []
        
        for conflict in conflicts:
            if conflict['type'] == 'both_fields_exist':
                # Remove old field, keep new field
                old_value = data.pop('entry_avax_price', None)
                changes_made.append(f"Removed entry_avax_price = {old_value}")
                
                # Ensure new field exists
                if 'entry_price' not in data:
                    data['entry_price'] = conflict['new_value']
                    changes_made.append(f"Set entry_price = {conflict['new_value']}")
            
            elif conflict['type'] == 'only_old_field':
                # Migrate old field to new field
                old_value = data.pop('entry_avax_price', None)
                data['entry_price'] = old_value
                changes_made.append(f"Migrated entry_avax_price → entry_price = {old_value}")
        
        # Write back to file
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        return changes_made
    
    except Exception as e:
        return [f"Fix failed: {str(e)}"]


def main():
    parser = argparse.ArgumentParser(description='Entry Price Field Validator & Fixer')
    parser.add_argument('--fix', action='store_true', help='Apply fixes automatically')
    parser.add_argument('--dry-run', action='store_true', help='Show changes without applying them')
    args = parser.parse_args()
    
    print("🔍 Entry Price Field Validator")
    print("=" * 50)
    
    # Find all config files
    config_files = find_all_config_files()
    print(f"📁 Found {len(config_files)} config files")
    
    total_conflicts = 0
    total_fixes_applied = 0
    
    for file_path in config_files:
        conflicts = check_file_for_conflicts(file_path)
        
        if conflicts:
            print(f"\n❌ CONFLICTS FOUND: {file_path}")
            total_conflicts += len(conflicts)
            
            for conflict in conflicts:
                if conflict['type'] == 'both_fields_exist':
                    print(f"   • Both fields exist:")
                    print(f"     - entry_avax_price = {conflict['old_value']}")
                    print(f"     - entry_price = {conflict['new_value']}")
                    print(f"     → Difference: {conflict['magnitude']:.4f}")
                
                elif conflict['type'] == 'only_old_field':
                    print(f"   • Only old field exists:")
                    print(f"     - entry_avax_price = {conflict['old_value']}")
                    print(f"     → Missing entry_price")
                
                elif conflict['type'] == 'read_error':
                    print(f"   • Error reading file: {conflict['error']}")
            
            if args.fix or args.dry_run:
                print(f"\n🔧 FIX APPLIED:")
                if args.dry_run:
                    print("   [DRY RUN] Would apply fixes...")
                    changes = ["Would remove entry_avax_price", "Would ensure entry_price exists"]
                else:
                    changes = apply_fix_to_file(file_path, conflicts)
                
                for change in changes:
                    print(f"   • {change}")
                
                if not args.dry_run:
                    total_fixes_applied += 1
    
    if total_conflicts == 0:
        print("\n✅ No conflicts found! All entry price fields are consistent.")
        return 0
    
    print("\n" + "=" * 50)
    print(f"SUMMARY:")
    print(f"• Total conflicts found: {total_conflicts}")
    print(f"• Fixes applied: {total_fixes_applied}")
    print(f"• Files checked: {len(config_files)}")
    
    if args.fix and total_fixes_applied > 0:
        print("\n🎉 Fixes applied successfully!")
        print("💡 Tip: Run the cron job next to verify IL calculations are now correct")
    
    return 0 if total_fixes_applied == total_conflicts else 1


if __name__ == "__main__":
    sys.exit(main())