#!/bin/bash
# check-hub-data.sh — Verify data source connectivity and freshness
# Usage: ./check-hub-data.sh <hub-file>

if [ -z "$1" ]; then
    echo "Usage: $0 <hub-file>"
    exit 1
fi

HUB_FILE="$1"
if [ ! -f "$HUB_FILE" ]; then
    echo "Error: File not found: $HUB_FILE"
    exit 1
fi

echo "### Data Source Check: $HUB_FILE"
echo ""

# Check for fetch() calls
FETCH_COUNT=$(grep -c 'fetch(' "$HUB_FILE" 2>/dev/null || echo 0)

if [ "$FETCH_COUNT" -gt 0 ]; then
    echo "✅ Live data detected: $FETCH_COUNT fetch() call(s) found"
    
    # Extract data URLs
    DATA_URLS=$(grep -oP 'fetch\s*\(\s*["\047](https?://[^"\047]+)["\047]' "$HUB_FILE" 2>/dev/null || echo "")
    
    if [ -n "$DATA_URLS" ]; then
        echo ""
        echo "Data URLs found:"
        echo "$DATA_URLS" | while read -r url; do
            # Test URL
            HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$url" 2>/dev/null || echo "000")
            
            if [ "$HTTP_CODE" = "200" ]; then
                echo "  ✅ $url → HTTP $HTTP_CODE"
            else
                echo "  ❌ $url → HTTP $HTTP_CODE (BROKEN)"
            fi
        done
    else
        echo "⚠️ fetch() found but no URLs extracted"
    fi
    
    # Check for cache-busting
    if grep -q "cache.*no-store" "$HUB_FILE" 2>/dev/null; then
        echo ""
        echo "✅ Cache-busting enabled: cache: 'no-store'"
    else
        echo ""
        echo "⚠️ No cache-busting — may show stale data"
    fi
else
    echo "❌ STATIC HUB: No fetch() calls found — data is hardcoded"
    echo ""
    echo "Impact: Dashboard will never update automatically"
    echo "Fix: Add fetch() to live data JSON file"
fi

echo ""
echo "### Summary"
if [ "$FETCH_COUNT" -gt 0 ]; then
    echo "✅ PASS: Hub has live data source"
else
    echo "⚠️ WARN: Hub is static — no live data"
fi