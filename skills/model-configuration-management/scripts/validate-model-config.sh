#!/bin/bash

# Model Configuration Validator
# Usage: validate-model-config.sh [provider]
# Validates that configured models exist in the live provider catalog

PROVIDER=${1:-"zai"}

echo "🔍 Validating model configuration for $PROVIDER..."

# Get current default model
CURRENT_MODEL=$(grep -A 3 -B 3 "default:" /root/.hermes/profiles/gentech/config.yaml | grep "default:" | awk '{print $2}')

echo "Current default model: $CURRENT_MODEL"

# Check model exists in OpenRouter catalog
if curl -s "https://openrouter.ai/api/v1/models" | jq -r '.data[].id' | grep -q "$CURRENT_MODEL"; then
    echo "✅ $CURRENT_MODEL exists in catalog"
    exit 0
else
    echo "❌ $CURRENT_MODEL not found in catalog"
    echo "Available $PROVIDER models:"
    curl -s "https://openrouter.ai/api/v1/models" | jq '.data[] | select(.id | contains("'"$PROVIDER"'")) | {id: .id, provider: .provider}'
    exit 1
fi