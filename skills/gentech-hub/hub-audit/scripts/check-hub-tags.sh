#!/bin/bash
# check-hub-tags.sh — Verify HTML tag balance
# Usage: ./check-hub-tags.sh <hub-file>

if [ -z "$1" ]; then
    echo "Usage: $0 <hub-file>"
    exit 1
fi

HUB_FILE="$1"
if [ ! -f "$HUB_FILE" ]; then
    echo "Error: File not found: $HUB_FILE"
    exit 1
fi

echo "### Tag Balance Check: $HUB_FILE"
echo ""

# Check div tags
DIV_OPENS=$(grep -c '<div' "$HUB_FILE" 2>/dev/null || echo 0)
DIV_CLOSES=$(grep -c '</div>' "$HUB_FILE" 2>/dev/null || echo 0)

if [ "$DIV_OPENS" -eq "$DIV_CLOSES" ]; then
    echo "✅ Div tags balanced: $DIV_OPENS open, $DIV_CLOSES close"
else
    echo "❌ Div tags UNBALANCED: $DIV_OPENS open, $DIV_CLOSES close"
fi

# Check script tags
SCRIPT_OPENS=$(grep -c '<script' "$HUB_FILE" 2>/dev/null || echo 0)
SCRIPT_CLOSES=$(grep -c '</script>' "$HUB_FILE" 2>/dev/null || echo 0)

if [ "$SCRIPT_OPENS" -eq "$SCRIPT_CLOSES" ]; then
    echo "✅ Script tags balanced: $SCRIPT_OPENS open, $SCRIPT_CLOSES close"
else
    echo "❌ Script tags UNBALANCED: $SCRIPT_OPENS open, $SCRIPT_CLOSES close"
fi

# Check p tags
P_OPENS=$(grep -c '<p' "$HUB_FILE" 2>/dev/null || echo 0)
P_CLOSES=$(grep -c '</p>' "$HUB_FILE" 2>/dev/null || echo 0)

if [ "$P_OPENS" -eq "$P_CLOSES" ]; then
    echo "✅ P tags balanced: $P_OPENS open, $P_CLOSES close"
else
    echo "⚠️ P tags may be unbalanced: $P_OPENS open, $P_CLOSES close (self-closing allowed)"
fi

echo ""
echo "### Summary"
if [ "$DIV_OPENS" -ne "$DIV_CLOSES" ] || [ "$SCRIPT_OPENS" -ne "$SCRIPT_CLOSES" ]; then
    echo "❌ FAIL: HTML syntax errors detected — GitHub Pages build will fail"
    exit 1
else
    echo "✅ PASS: All critical tags balanced"
    exit 0
fi