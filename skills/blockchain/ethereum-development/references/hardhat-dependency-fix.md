# Hardhat Dependency Fix — Full Troubleshooting

## Problem: toolbox Dependency Cascade

Installing `@nomicfoundation/hardhat-toolbox` with Hardhat 2 triggers an endless chain:

```
hardhat-toolbox@6 → requires hardhat@3
hardhat-toolbox@5 → requires 8+ peer deps
  → @nomicfoundation/hardhat-ethers
  → @nomicfoundation/hardhat-chai-matchers
  → @nomicfoundation/hardhat-network-helpers
  → hardhat-gas-reporter
  → solidity-coverage
  → typechain + @typechain/hardhat + @typechain/ethers-v6
  → @types/mocha
  → ts-node
  → @nomicfoundation/hardhat-ignition-ethers
    → @nomicfoundation/hardhat-ignition
    → @nomicfoundation/ignition-core
```

Each package has its own peer deps. Resolving with `--legacy-peer-deps` sometimes works but is fragile.

## Solution: Minimal Install

```bash
npm install --save-dev \
  "hardhat@^2.28.0" \
  "@nomicfoundation/hardhat-ethers@^3.0.0" \
  "ethers@^6.0.0" \
  "chai@^4.0.0" \
  --legacy-peer-deps
```

This gives you:
- Contract compilation
- ethers.js integration
- Basic testing with assert

You DON'T get (but don't need for basics):
- Hardhat Ignition (deployment framework)
- TypeChain (typed contract bindings)
- Gas reporting
- Solidity coverage

Add those later if needed, one at a time.

## Error Messages and Fixes

| Error | Cause | Fix |
|-------|-------|-----|
| `Node.js 22.11.0 not supported` | Hardhat 2.28+ needs 22.13.0+ | `nvm install 22.13.0` |
| `Hardhat only supports ESM projects` | Missing `"type": "module"` | `npm pkg set type="module"` |
| `Plugin requires dependencies` | Missing peer deps | Use minimal install above |
| `HH801: Plugin requires...` | toolbox cascade | Don't use toolbox |
| `npx hardhat init` hangs | Interactive prompt in non-interactive terminal | Create files manually |

## Version Compatibility Matrix

| Component | Version | Notes |
|-----------|---------|-------|
| Node.js | 22.13.0+ | Required by Hardhat 2.28 |
| Hardhat | ^2.28.0 | ESM-only, don't use v3 yet |
| hardhat-ethers | ^3.0.0 | Must match Hardhat 2 |
| ethers | ^6.0.0 | v5 syntax differs |
| chai | ^4.0.0 | v5 is ESM-only, different syntax |
| Solidity | 0.8.24 | Current stable, use ^0.8.24 |

## Testing Without Chai Matchers

The toolbox provides `@nomicfoundation/hardhat-chai-matchers` for `.to.be.revertedWith()` syntax. Without it, use try/catch:

```javascript
try {
  await contract.someFunction();
  assert(false, "Should have reverted!");
} catch (error) {
  assert(error.message.includes("Expected error"), "Correct revert");
}
```

For events, parse logs manually:

```javascript
const tx = await contract.someFunction();
const receipt = await tx.wait();
const event = receipt.logs.find(log => {
  try {
    const parsed = contract.interface.parseLog(log);
    return parsed.name === "EventName";
  } catch { return false; }
});
assert(event !== undefined, "Event emitted");
```
