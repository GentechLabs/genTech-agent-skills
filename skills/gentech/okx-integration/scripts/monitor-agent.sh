#!/bin/bash

# OKX Agent Approval Monitor
# Automatically checks agent status every 5 minutes until approval
# Usage: ./monitor-agent.sh <agent-id>

AGENT_ID="$1"
if [[ -z "$AGENT_ID" ]]; then
    echo "Usage: $0 <agent-id>"
    exit 1
fi

export PATH="$HOME/.local/bin:$PATH"

echo "🔍 Monitoring OKX Agent #${AGENT_ID}..."
echo "⏳ Checking every 5 minutes..."

while true; do
    STATUS=$(onchainos agent get-agents --agent-ids "$AGENT_ID" 2>/dev/null | jq -r '.[0].approvalDisplayStatus')
    LABEL=$(onchainos agent get-agents --agent-ids "$AGENT_ID" 2>/dev/null | jq -r '.[0].approvalLabel')
    REMARK=$(onchainos agent get-agents --agent-ids "$AGENT_ID" 2>/dev/null | jq -r '.[0].approvalRemark // empty')

    case "$STATUS" in
        "4")
            echo "✅ APPROVED - $LABEL"
            echo "🎉 Agent #${AGENT_ID} is now live on OKX.AI!"
            exit 0
            ;;
        "5")
            echo "❌ REJECTED - $LABEL"
            if [[ -n "$REMARK" ]]; then
                echo "📝 Reason: $REMARK"
            fi
            echo "💡 Make changes and resubmit your agent."
            exit 1
            ;;
        "2")
            echo "⏳ UNDER REVIEW - $LABEL"
            echo "⏰ Waiting for approval..."
            ;;
        *)
            echo "📊 STATUS: $LABEL"
            if [[ -n "$REMARK" ]]; then
                echo "📝 Note: $REMARK"
            fi
            ;;
    esac

    sleep 300  # 5 minutes
done