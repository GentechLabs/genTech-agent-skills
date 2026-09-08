#!/bin/bash

# Dual-Agent Coordination Health Check
# Run daily to verify system coherence and token usage

set -e

echo "=== Dual-Agent Coordination Health Check ==="
date

# Configuration
VAULT_PATH="/root/vaults/gentech"
DEEPSEEK_THRESHOLD=4000000  # 80% of 5M tokens

# Check 1: Vault Status
echo "1. Checking vault status..."
cd "$VAULT_PATH"
if ! git status --porcelain | grep -q ""; then
    echo "✅ Vault is clean"
else
    echo "❌ Vault has uncommitted changes"
    git status
    exit 1
fi

# Check 2: Ollama Service (Desktop component)
echo "2. Checking Ollama service..."
if systemctl is-active ollama > /dev/null 2>&1; then
    echo "✅ Ollama is running"
    
    # Test model availability
    if curl -s http://localhost:11434/api/tags | grep -q "llama3.1:8b"; then
        echo "✅ llama3.1:8b model available"
    else
        echo "❌ llama3.1:8b model not available"
        exit 1
    fi
else
    echo "❌ Ollama is not running"
    exit 1
fi

# Check 3: DeepSeek Token Usage
echo "3. Checking DeepSeek token usage..."
if [ -n "$DEEPSEEK_API_KEY" ]; then
    usage=$(curl -s "https://api.deepseek.com/v1/usage" \
        -H "Authorization: Bearer $DEEPSEEK_API_KEY" | \
        jq '.data.total_tokens_used' 2>/dev/null)
    
    if [ -n "$usage" ]; then
        echo "Current usage: $usage / 5000000 tokens"
        if [ "$usage" -gt "$DEEPSEEK_THRESHOLD" ]; then
            echo "⚠️  WARNING: DeepSeek tokens >80% used"
        else
            echo "✅ DeepSeek tokens within threshold"
        fi
    else
        echo "❌ Failed to fetch DeepSeek usage"
    fi
else
    echo "⚠️  DEEPSEEK_API_KEY not set"
fi

# Check 4: Cron Jobs
echo "4. Checking cron jobs..."
if hermes cron list > /dev/null 2>&1; then
    echo "✅ Hermes cron accessible"
    echo "Active cron jobs:"
    hermes cron list | grep -E "job_id|schedule" | head -8
else
    echo "❌ Hermes cron not accessible"
    exit 1
fi

# Check 5: Model Routing Configuration
echo "5. Checking model routing..."
if [ -f "$VAULT_PATH/09-Green Room/forge-implementation-plan.md" ]; then
    echo "✅ Implementation plan exists"
    if grep -q "Model Strategy" "$VAULT_PATH/09-Green Room/forge-implementation-plan.md"; then
        echo "✅ Model strategy documented"
    else
        echo "⚠️  Model strategy not fully documented"
    fi
else
    echo "❌ Implementation plan missing"
    exit 1
fi

# Check 6: Status Board Update
echo "6. Checking status board..."
if [ -f "$VAULT_PATH/00-HQ/current-status.md" ]; then
    if grep -q "Forge Integration" "$VAULT_PATH/00-HQ/current-status.md"; then
        echo "✅ Status board updated"
    else
        echo "⚠️  Status board needs Forge Integration section"
    fi
else
    echo "❌ Status board not found"
    exit 1
fi

echo ""
echo "=== Health Check Complete ==="
echo "Recommendations:"
echo "- Monitor DeepSeek token usage weekly"
echo "- Keep Ollama service running for desktop components"
echo "- Sync vault regularly between systems"
echo "- Update implementation status as progress is made"