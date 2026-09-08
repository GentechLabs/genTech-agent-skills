#!/bin/bash

# ElevenLabs API Key Validation Script
# Purpose: Test API keys before voice generation to avoid JSON responses
# Usage: ./test-elevenlabs-key.sh [API_KEY]
# Returns: 0 if valid, 1 if invalid

API_KEY="$1"

if [ -z "$API_KEY" ]; then
    echo "❌ ERROR: No API key provided"
    echo "Usage: ./test-elevenlabs-key.sh YOUR_ELEVENLABS_API_KEY"
    exit 1
fi

echo "🔍 Testing ElevenLabs API key..."
echo "Key: ${API_KEY:0:10}...${API_KEY: -10}"

# Test the API key
RESPONSE=$(curl -s -X GET "https://api.elevenlabs.io/v1/user" \
    -H "Content-Type: application/json" \
    -H "xi-api-key: $API_KEY" 2>/dev/null)

if echo "$RESPONSE" | grep -q "user_id"; then
    USER_ID=$(echo "$RESPONSE" | jq -r '.user_id' 2>/dev/null)
    echo "✅ API key valid!"
    echo "User ID: $USER_ID"
    echo "Credits remaining: $(echo "$RESPONSE" | jq -r '.subscription.character_count' 2>/dev/null)"
    exit 0
else
    echo "❌ ERROR: Invalid API key"
    echo "Response: $RESPONSE"
    exit 1
fi