#!/usr/bin/env python3
"""Bypass the broken Hermes KeeperHub plugin wrappers and call the MCP server directly.

Why: the Hermes kh_execute_* wrappers pass network/recipient_address/contract_address,
but the KeeperHub MCP server validates chain_id/to_address — so every wrapper fails with
"expected chain_id, received undefined". Also, EVM contract addresses must carry a correct
EIP-55 checksum or KeeperHub rejects them as "Invalid contract address".

This script:
  1. Reads KH_API_KEY from the profile .env.
  2. Checksum-corrects the contract address (the #1 fix for "Invalid ... address").
  3. Optionally simulates (--simulate) then executes USDC.transfer on Base mainnet.
  4. On success, prints the tx hash / execution result so you can capture the live link.

Usage:
  python3 keeperhub-direct-call.py --simulate           # dry-run, no funds moved
  python3 keeperhub-direct-call.py                      # real 0.01 USDC transfer (confirm first)

Requires: pip install httpx eth_utils
"""
import json, os, sys, httpx

try:
    import eth_utils
except ImportError:
    print("pip install eth_utils httpx"); sys.exit(1)

MCP_URL = "https://app.keeperhub.com/mcp"
CHAIN = "8453"  # Base mainnet
USDC = "0x833589fCD6eDb6E08f4c7C32D4f71b54bDA02913"
RECIPIENT = "0x77C622D02A1518fC0FDcd83B8C28010FA5ebB7dE"
AMOUNT_RAW = "10000"  # 0.01 USDC at 6 decimals

def key():
    for f in ("/root/.hermes/profiles/gentech/.env",):
        if os.path.exists(f):
            for line in open(f):
                if line.startswith("KH_API_KEY="):
                    return line.strip().split("=", 1)[1].strip()
    return os.environ.get("KH_API_KEY", "")

def main():
    sim = "--simulate" in sys.argv
    addr = eth_utils.to_checksum_address(USDC)
    # The checksum fix is the whole point — show the before/after.
    print(f"passed-in : {USDC}")
    print(f"checksum'd: {addr}")
    if addr != USDC:
        print(">>> WARNING: address had a bad EIP-55 checksum; using corrected form.")

    abi = json.dumps([{"constant": False,
                       "inputs": [{"name": "to", "type": "address"},
                                  {"name": "value", "type": "uint256"}],
                       "name": "transfer", "outputs": [{"name": "", "type": "bool"}],
                       "payable": False, "stateMutability": "nonpayable", "type": "function"}])
    args = {"chain_id": CHAIN, "contract_address": addr,
            "function_name": "transfer",
            "function_args": json.dumps([RECIPIENT, AMOUNT_RAW]), "abi": abi}
    if sim:
        args["simulate"] = True

    h = httpx.Client(timeout=120)
    hdr = {"Content-Type": "application/json", "Accept": "application/json, text/event-stream",
           "Authorization": f"Bearer {key()}"}
    r = h.post(MCP_URL, headers=hdr, json={"jsonrpc": "2.0", "id": 1, "method": "initialize",
               "params": {"protocolVersion": "2024-11-05", "capabilities": {},
                          "clientInfo": {"name": "gentech-direct", "version": "1.0"}}})
    sid = r.headers.get("mcp-session-id")
    if not sid:
        print("NO SESSION ID:", r.text); sys.exit(1)
    hdr["mcp-session-id"] = sid

    body = {"jsonrpc": "2.0", "id": 2, "method": "tools/call",
            "params": {"name": "execute_contract_call", "arguments": args}}
    rr = h.post(MCP_URL, headers=hdr, json=body)
    print(f"\n{'SIMULATE' if sim else 'EXECUTE'} execute_contract_call -> {rr.status_code}")
    print(rr.text[:1500])
    # For a real (non-sim) run, capture the tx link from the result.
    if not sim and rr.status_code == 200 and "transactionHash" in rr.text:
        print("\nLIVE TX — capture this link for the submission.")

if __name__ == "__main__":
    main()
