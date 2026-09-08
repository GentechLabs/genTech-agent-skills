#!/bin/bash
# Family Hub Deployment Verification Script
# Verifies that all family member hubs, dashboards, and data files are properly deployed on GitHub Pages

set -e

# Configuration
GITHUB_PAGES_URL="https://protojay4789.github.io"
DEPLOY_WAIT_SECONDS=30
COLOR_GREEN='\033[0;32m'
COLOR_RED='\033[0;31m'
COLOR_YELLOW='\033[1;33m'
COLOR_RESET='\033[0m'

# Family member registry
declare -A FAMILY_MEMBERS=(
    ["vanito"]="hub-vanito.html hub-vanito-data.json Gaming/vanito-music-dashboard.html Gaming/vanito-music.json Gaming/wishlist-vanito.html"
    ["jordan"]="hub-jordan.html hub-jordan-data.json"
    ["christel"]="Cookbook/christel-hub.html Cookbook/shopping-list.html Cookbook/christel-kitchen.html"
)

# Steam ID registry
declare -A STEAM_IDS=(
    ["jordan"]="76561197996487689"
    ["vanito"]="76561198132811363"
)

# Cronjob registry
declare -A CRONJOBS=(
    ["jordan-game-intel"]="41f8e6d0e24b"
    ["jordan-voice-notes"]="90e51510349c"
    ["vanito-game-intel"]="e28c895e6a11"
    ["vanito-voice-notes"]="a564b3353770"
    ["vanito-music-sync"]="f3e90d867b9c"
)

echo -e "${COLOR_YELLOW}🔍 GenTech Family Hub Deployment Verification${COLOR_RESET}"
echo ""

# Function to check if URL is accessible
check_url() {
    local url=$1
    local search_term=$2
    
    echo "  Checking: $url"
    if curl -s -f "$url" | grep -q "$search_term" 2>/dev/null; then
        echo -e "    ${COLOR_GREEN}✓ Found: $search_term${COLOR_RESET}"
        return 0
    else
        echo -e "    ${COLOR_RED}✗ Not found: $search_term${COLOR_RESET}"
        return 1
    fi
}

# Function to check if local file exists
check_local_file() {
    local file_path=$1
    
    echo "  Checking: $file_path"
    if [ -f "$file_path" ]; then
        echo -e "    ${COLOR_GREEN}✓ File exists${COLOR_RESET}"
        return 0
    else
        echo -e "    ${COLOR_RED}✗ File not found${COLOR_RESET}"
        return 1
    fi
}

# Function to check cronjob status
check_cronjob() {
    local job_name=$1
    local job_id=$2
    
    echo "  Checking cronjob: $job_name ($job_id)"
    if cronjob action=list 2>/dev/null | grep -q "$job_id"; then
        echo -e "    ${COLOR_GREEN}✓ Cronjob exists${COLOR_RESET}"
        return 0
    else
        echo -e "    ${COLOR_RED}✗ Cronjob not found${COLOR_RESET}"
        return 1
    fi
}

# Function to check Steam ID configuration
check_steam_id() {
    local person=$1
    local steam_id=$2
    
    echo "  Checking Steam ID for $person: $steam_id"
    if [ -n "$steam_id" ]; then
        echo -e "    ${COLOR_GREEN}✓ Steam ID configured${COLOR_RESET}"
        return 0
    else
        echo -e "    ${COLOR_RED}✗ Steam ID not configured${COLOR_RESET}"
        return 1
    fi
}

# Main verification
echo -e "${COLOR_YELLOW}=== Local File Verification ===${COLOR_RESET}"
for person in "${!FAMILY_MEMBERS[@]}"; do
    echo -e "\n${COLOR_YELLOW}Person: $person${COLOR_RESET}"
    files=${FAMILY_MEMBERS[$person]}
    
    for file in $files; do
        check_local_file "/root/ProtoJay4789.github.io/$file"
    done
done

echo -e "\n${COLOR_YELLOW}=== GitHub Pages Deployment Verification ===${COLOR_RESET}"
for person in "${!FAMILY_MEMBERS[@]}"; do
    echo -e "\n${COLOR_YELLOW}Person: $person${COLOR_RESET}"
    files=${FAMILY_MEMBERS[$person]}
    
    for file in $files; do
        if [[ $file == *.html ]]; then
            # HTML files: check for title or specific content
            person_capitalized=$(echo "$person" | sed 's/\b\(.\)/\u\1/g')
            check_url "$GITHUB_PAGES_URL/$file" "$person_capitalized"
        elif [[ $file == *.json ]]; then
            # JSON files: check for valid JSON
            echo "  Checking: $file"
            if curl -s -f "$GITHUB_PAGES_URL/$file" | jq empty 2>/dev/null; then
                echo -e "    ${COLOR_GREEN}✓ Valid JSON${COLOR_RESET}"
            else
                echo -e "    ${COLOR_RED}✗ Invalid or missing JSON${COLOR_RESET}"
            fi
        fi
    done
done

echo -e "\n${COLOR_YELLOW}=== Steam ID Verification ===${COLOR_RESET}"
for person in "${!STEAM_IDS[@]}"; do
    check_steam_id "$person" "${STEAM_IDS[$person]}"
done

echo -e "\n${COLOR_YELLOW}=== Cronjob Verification ===${COLOR_RESET}"
for job_name in "${!CRONJOBS[@]}"; do
    check_cronjob "$job_name" "${CRONJOBS[$job_name]}"
done

echo -e "\n${COLOR_YELLOW}=== Navigation Link Verification ===${COLOR_RESET}"
echo -e "\n${COLOR_YELLOW}Vanito: Main Hub → Music Dashboard${COLOR_RESET}"
check_url "$GITHUB_PAGES_URL/hub-vanito.html" "vanito-music-dashboard.html"

echo -e "\n${COLOR_YELLOW}Vanito: Music Dashboard → Main Hub${COLOR_RESET}"
check_url "$GITHUB_PAGES_URL/Gaming/vanito-music-dashboard.html" "Back to Main Hub"

echo -e "\n${COLOR_YELLOW}Christel: Hub → Shopping List${COLOR_RESET}"
check_url "$GITHUB_PAGES_URL/Cookbook/christel-hub.html" "shopping-list.html"

echo -e "\n${COLOR_YELLOW}Christel: Shopping List → Hub${COLOR_RESET}"
check_url "$GITHUB_PAGES_URL/Cookbook/shopping-list.html" "christel-hub.html"

echo -e "\n${COLOR_YELLOW}=== Data Source Verification ===${COLOR_RESET}"
echo -e "\n${COLOR_YELLOW}Vanito: Hub Data File${COLOR_RESET}"
check_local_file "/root/ProtoJay4789.github.io/hub-vanito-data.json"
if [ -f "/root/ProtoJay4789.github.io/hub-vanito-data.json" ]; then
    echo "  Validating JSON structure..."
    if jq -e '.music.songs' "/root/ProtoJay4789.github.io/hub-vanito-data.json" >/dev/null 2>&1; then
        song_count=$(jq '.music.songs | length' "/root/ProtoJay4789.github.io/hub-vanito-data.json")
        echo -e "    ${COLOR_GREEN}✓ Valid structure, $song_count songs found${COLOR_RESET}"
    else
        echo -e "    ${COLOR_RED}✗ Invalid structure or missing music.songs${COLOR_RESET}"
    fi
fi

echo -e "\n${COLOR_YELLOW}Vanito: Music Sync Script${COLOR_RESET}"
check_local_file "/root/my-music/vanito-music-sync.py"
if [ -f "/root/my-music/vanito-music-sync.py" ]; then
    echo "  Checking for hub-vanito-data.json reference..."
    if grep -q "hub-vanito-data.json" "/root/my-music/vanito-music-sync.py"; then
        echo -e "    ${COLOR_GREEN}✓ Correct data source${COLOR_RESET}"
    else
        echo -e "    ${COLOR_RED}✗ Missing or wrong data source${COLOR_RESET}"
    fi
fi

echo -e "\n${COLOR_YELLOW}=== Sync Status ===${COLOR_RESET}"
echo "Checking vault sync status..."
cd /root/vaults/gentech
if git status --porcelain | grep -q "family-member-registry.md\|cronjob-coordination-strategies.md"; then
    echo -e "    ${COLOR_YELLOW}⚠ Uncommitted changes in skill files${COLOR_RESET}"
    echo "    Run: cd /root/vaults/gentech && ob sync"
else
    echo -e "    ${COLOR_GREEN}✓ Vault synced${COLOR_RESET}"
fi

echo "Checking GitHub Pages repo status..."
cd /root/ProtoJay4789.github.io
if git status --porcelain | grep -q "\.html\|\.json"; then
    echo -e "    ${COLOR_YELLOW}⚠ Uncommitted changes in GitHub Pages repo${COLOR_RESET}"
    echo "    Run: git add . && git commit && git push"
else
    echo -e "    ${COLOR_GREEN}✓ GitHub Pages repo clean${COLOR_RESET}"
fi

echo -e "\n${COLOR_YELLOW}=== Verification Complete ===${COLOR_RESET}"
echo ""
echo "Summary:"
echo "  - All checks completed"
echo "  - Review ${COLOR_RED}✗${COLOR_RESET} items for issues"
echo "  - Review ${COLOR_YELLOW}⚠${COLOR_RESET} items for pending changes"
echo ""
echo "Next steps:"
echo "  1. Fix any ${COLOR_RED}✗${COLOR_RESET} issues found"
echo "  2. Commit pending changes"
echo "  3. Wait 30s for GitHub Pages deployment"
echo "  4. Re-run this script to verify fixes"
echo ""