---
name: ethereum-development
description: "Ethereum smart contract development with Hardhat — setup, compilation, testing, deployment. Covers dependency pitfalls, ESM format, and local testnet workflows."
tags:
  - class-level
  - ethereum
  - solidity
  - hardhat
  - development
related:
  - solidity-security
  - solana-anchor-development
---

# Ethereum Development Skill

End-to-end workflow for building, testing, and deploying Ethereum smart contracts using Hardhat.

## When to Use

- Setting up a new Hardhat project
- Writing and compiling Solidity contracts
- Running tests against local Hardhat network
- Deploying to testnets (Sepolia, etc.)
- Debugging compilation or dependency issues

## Prerequisites

- Node.js 22.13.0+ (Hardhat 2.28+ requirement)
- npm or yarn

---

## 1. Project Setup (Critical Path)

### The Dependency Problem

The `@nomicfoundation/hardhat-toolbox` package is **broken for Hardhat 2**. Version 6 requires Hardhat 3; version 5 requires 8+ peer dependencies that cascade into more conflicts.

**Solution:** Install only the essentials:

```bash
mkdir my-project && cd my-project
npm init -y
npm pkg set type="module"  # Required: Hardhat 2.28+ is ESM-only

npm install --save-dev \
  "hardhat@^2.28.0" \
  "@nomicfoundation/hardhat-ethers@^3.0.0" \
  "ethers@^6.0.0" \
  "chai@^4.0.0" \
  --legacy-peer-deps
```

**Do NOT install `@nomicfoundation/hardhat-toolbox`** — it triggers an endless dependency cascade.

### Pitfall: Node.js Version

Hardhat 2.28+ requires Node.js 22.13.0 or later. Check with `node --version`.

If too old, install nvm and upgrade:
```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
nvm install 22.13.0
nvm use 22.13.0
```

### Pitfall: ESM Format

Hardhat 2.28+ requires ESM. You MUST:
1. Add `"type": "module"` to package.json: `npm pkg set type="module"`
2. Use `import` syntax in hardhat.config.js (not `require`)

**hardhat.config.js:**
```javascript
import "@nomicfoundation/hardhat-ethers";

export default {
  solidity: "0.8.24",
};
```

### Pitfall: Interactive Prompts

`npx hardhat init` uses interactive prompts that don't work in automated terminals. Create files manually instead — see template below.

---

## 2. Project Structure

```
project/
├── contracts/
│   └── MyContract.sol
├── test/
│   └── MyContract.test.js
├── hardhat.config.js
├── package.json
└── README.md
```

---

## 3. Minimal Contract Template

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

contract MyContract {
    string public message;
    address public owner;

    event MessageUpdated(string newMessage, address updatedBy);

    constructor(string memory _initialMessage) {
        message = _initialMessage;
        owner = msg.sender;
    }

    function setMessage(string memory _newMessage) public {
        require(msg.sender == owner, "Only owner can update");
        message = _newMessage;
        emit MessageUpdated(_newMessage, msg.sender);
    }

    function getMessage() public view returns (string memory) {
        return message;
    }
}
```

---

## 4. Minimal Test Template

Uses native `assert` instead of chai matchers to avoid additional dependencies:

```javascript
import hre from "hardhat";
const { ethers } = hre;

function assert(condition, message) {
  if (!condition) throw new Error(`FAIL: ${message}`);
  console.log(`  ✓ ${message}`);
}

describe("MyContract", function () {
  let contract, owner, addr1;

  beforeEach(async function () {
    [owner, addr1] = await ethers.getSigners();
    const Contract = await ethers.getContractFactory("MyContract");
    contract = await Contract.deploy("Hello, Blockchain!");
    await contract.waitForDeployment();
  });

  it("Should set initial message", async function () {
    const msg = await contract.message();
    assert(msg === "Hello, Blockchain!", "Message matches");
  });

  it("Should revert unauthorized update", async function () {
    try {
      await contract.connect(addr1).setMessage("Hacker!");
      assert(false, "Should have reverted!");
    } catch (error) {
      assert(error.message.includes("Only owner"), "Reverted with owner error");
    }
  });
});
```

---

## 5. Commands

```bash
# Compile
npx hardhat compile

# Test
npx hardhat test

# Start local blockchain (port 8545)
npx hardhat node

# Open console
npx hardhat console
```

---

## 6. Next Steps

After mastering basics:
1. ERC20 token (OpenZeppelin contracts)
2. Deploy to Sepolia testnet (need Infura/Alchemy key)
3. Security patterns — see `solidity-security` skill
4. Build for hackathons — see `hackathon` skill

---

## References

- `references/hardhat-dependency-fix.md` — Full troubleshooting for dependency conflicts
- `references/sepolia-deployment.md` — Testnet deployment workflow (coming soon)
