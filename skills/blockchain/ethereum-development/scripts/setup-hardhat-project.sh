#!/bin/bash
# Quick Hardhat project setup — run from parent directory
# Usage: bash setup-hardhat-project.sh <project-name>

set -e

PROJECT_NAME="${1:-my-hardhat-project}"

echo "🚀 Setting up Hardhat project: $PROJECT_NAME"

# Create project
mkdir -p "$PROJECT_NAME" && cd "$PROJECT_NAME"

# Init npm and set ESM
npm init -y
npm pkg set type="module"

# Install dependencies
echo "📦 Installing dependencies..."
npm install --save-dev \
  "hardhat@^2.28.0" \
  "@nomicfoundation/hardhat-ethers@^3.0.0" \
  "ethers@^6.0.0" \
  "chai@^4.0.0" \
  --legacy-peer-deps

# Create directories
mkdir -p contracts test

# Create config
cat > hardhat.config.js << 'EOF'
import "@nomicfoundation/hardhat-ethers";

export default {
  solidity: "0.8.24",
};
EOF

# Create starter contract
cat > contracts/MyContract.sol << 'EOF'
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
EOF

# Create starter test
cat > test/MyContract.test.js << 'EOF'
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
EOF

echo "✅ Project ready!"
echo ""
echo "Next steps:"
echo "  cd $PROJECT_NAME"
echo "  npx hardhat compile"
echo "  npx hardhat test"
