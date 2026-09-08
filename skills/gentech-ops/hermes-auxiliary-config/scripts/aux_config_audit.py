#!/usr/bin/env python3
"""
Auxiliary Configuration Audit Script

Usage:
  python3 aux_config_audit.py
  python3 aux_config_audit.py --tool vision
  python3 aux_config_audit.py --fix

This script systematically audits Hermes auxiliary configuration
for conflicts and can optionally auto-fix common issues.
"""

import argparse
import yaml
import sys
from pathlib import Path

# Default config path
CONFIG_PATH = Path.home() / ".hermes" / "profiles" / "gentech" / "config.yaml"


def load_config(path):
    """Load YAML config file."""
    with open(path, 'r') as f:
        return yaml.safe_load(f)


def save_config(config, path):
    """Save config back to file."""
    with open(path, 'w') as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)


def audit_auxiliary(config):
    """Audit auxiliary section."""
    auxiliary = config.get('auxiliary', {})
    print("=== AUXILIARY SECTION ===")
    print(yaml.dump(auxiliary, default_flow_style=False))
    return auxiliary


def audit_root_overrides(config):
    """Audit root-level overrides (deprecated, cause conflicts)."""
    print("\n=== ROOT-LEVEL OVERRIDES (BAD - MUST REMOVE) ===")
    overrides = []
    for key in config:
        if any(x in key for x in ['vision_provider', 'vision_model', 'web_extract_provider', 
                                   'approval_provider', 'compression_provider', 'mcp_provider',
                                   'skills_hub_provider', 'curator_provider', 
                                   'triage_specifier_provider', 'session_search_provider']):
            print(f"  {key}: {config[key]}")
            overrides.append(key)
    
    if not overrides:
        print("  CLEAN: No root-level overrides found")
    
    return overrides


def audit_provider_duplicates(config):
    """Audit for duplicate provider definitions."""
    print("\n=== PROVIDER DUPLICATES CHECK ===")
    providers = config.get('providers', {})
    duplicates = []
    
    for name in ['nous', 'zai', 'opencode-go']:
        if name in config and name in providers:
            duplicates.append(name)
            print(f"  DUPLICATE: {name} exists at both root level and providers section")
    
    if not duplicates:
        print("  CLEAN: No duplicate providers found")
    
    return duplicates


def audit_tool_config(config, tool_name):
    """Audit specific tool configuration."""
    tool_config = config.get('auxiliary', {}).get(tool_name, {})
    
    print(f"\n=== {tool_name.upper()} CONFIG ===")
    print(f"  Provider: {tool_config.get('provider', 'NOT SET')}")
    print(f"  Model: {tool_config.get('model', 'NOT SET')}")
    print(f"  Base URL: {tool_config.get('base_url') or 'Using provider default'}")
    print(f"  API Key: {'Using env var' if not tool_config.get('api_key') else 'HARDCODED'}")
    
    # Check provider exists
    provider_name = tool_config.get('provider')
    if provider_name:
        provider = config.get('providers', {}).get(provider_name, {})
        if provider:
            print(f"\n  {provider_name.upper()} PROVIDER:")
            print(f"    Base URL: {provider.get('base_url', 'NOT SET')}")
            print(f"    Type: {provider.get('type', 'NOT SET')}")
            print(f"    API Key: {'[SET]' if provider.get('api_key') else 'MISSING'}")
        else:
            print(f"\n  ERROR: Provider '{provider_name}' not found in providers section")
    else:
        print(f"\n  ERROR: No provider configured")


def fix_root_overrides(config, overrides):
    """Remove root-level overrides."""
    for key in overrides:
        if key in config:
            del config[key]
            print(f"  Removed: {key}")
    return config


def fix_provider_duplicates(config, duplicates):
    """Remove duplicate provider definitions at root level."""
    for name in duplicates:
        if name in config and 'providers' in config and name in config['providers']:
            del config[name]
            print(f"  Removed root-level duplicate: {name}")
    return config


def main():
    parser = argparse.ArgumentParser(description="Hermes auxiliary configuration audit")
    parser.add_argument('--tool', help="Audit specific tool (vision, web_extract, compression, etc.)")
    parser.add_argument('--fix', action='store_true', help="Auto-fix common issues")
    parser.add_argument('--config', default=str(CONFIG_PATH), help="Path to config.yaml")
    
    args = parser.parse_args()
    
    if not Path(args.config).exists():
        print(f"ERROR: Config file not found: {args.config}")
        sys.exit(1)
    
    config = load_config(args.config)
    
    # Run audits
    auxiliary = audit_auxiliary(config)
    overrides = audit_root_overrides(config)
    duplicates = audit_provider_duplicates(config)
    
    if args.tool:
        audit_tool_config(config, args.tool)
    
    # Fix if requested
    if args.fix:
        print("\n=== FIXING ISSUES ===")
        if overrides:
            print("Removing root-level overrides...")
            config = fix_root_overrides(config, overrides)
        
        if duplicates:
            print("Removing provider duplicates...")
            config = fix_provider_duplicates(config, duplicates)
        
        save_config(config, args.config)
        print(f"\nFixed config saved to: {args.config}")
        print("\nRun this script again without --fix to verify.")
    else:
        print("\n=== RECOMMENDATIONS ===")
        if overrides or duplicates:
            print("Issues found. Run with --fix to auto-resolve, or:")
            print("  1. Remove root-level overrides manually")
            print("  2. Remove duplicate provider definitions")
            print("  3. Ensure auxiliary.* section is the only config source")
        else:
            print("Configuration looks clean!")


if __name__ == '__main__':
    main()