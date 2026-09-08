"""
Collaborator Identification
Detects and routes messages from different human collaborators.
"""

import os
import json
import re
from pathlib import Path

# Paths
VAULT_PATH = Path("/root/vaults/gentech")
COLLAB_DIR = VAULT_PATH / "00-HQ" / "collaborators"
MAPPING_FILE = COLLAB_DIR / "mapping.json"

# Environment variables
JORDAN_TELEGRAM_ID = os.getenv("JORDAN_TELEGRAM_ID", "")
VANITO_TELEGRAM_ID = os.getenv("VANITO_TELEGRAM_ID", "")


def load_mapping():
    """Load collaborator mapping from file."""
    if not MAPPING_FILE.exists():
        # Create default mapping
        default_mapping = {
            "version": "1.0",
            "last_updated": "2026-07-06",
            "collaborators": {
                "jordan": {
                    "telegram_username": "@ProtoJay4789",
                    "telegram_id": JORDAN_TELEGRAM_ID,
                    "profile": str(COLLAB_DIR / "jordan.md"),
                    "topics": ["all"],
                    "permissions": ["all"]
                },
                "vanito": {
                    "telegram_username": "@Vanito",
                    "telegram_id": VANITO_TELEGRAM_ID,
                    "profile": str(COLLAB_DIR / "vanito.md"),
                    "topics": ["metaglasses", "entertainment", "ar-vr"],
                    "permissions": ["limited"]
                }
            }
        }
        save_mapping(default_mapping)
        return default_mapping

    with open(MAPPING_FILE, "r") as f:
        return json.load(f)


def save_mapping(mapping):
    """Save collaborator mapping to file."""
    COLLAB_DIR.mkdir(parents=True, exist_ok=True)
    with open(MAPPING_FILE, "w") as f:
        json.dump(mapping, f, indent=2)


def detect_by_user_id(telegram_id, mapping):
    """Detect collaborator by Telegram user ID."""
    if not telegram_id:
        return None

    telegram_id = str(telegram_id)

    for name, data in mapping["collaborators"].items():
        if data.get("telegram_id") == telegram_id:
            return name

    return None


def detect_by_username(telegram_username, mapping):
    """Detect collaborator by Telegram username."""
    if not telegram_username:
        return None

    telegram_username = telegram_username.lower()

    for name, data in mapping["collaborators"].items():
        username = data.get("telegram_username", "").lower()
        if username and username == telegram_username:
            return name

    return None


def detect_by_pattern(content):
    """Detect collaborator by message content patterns."""
    content = content.lower()

    # Self-identification
    jordan_patterns = [
        r"jordan:\s*",
        r"jordan here:\s*",
        r"^\s*jordan\b",
    ]
    vanito_patterns = [
        r"vanito:\s*",
        r"vanito here:\s*",
        r"^\s*vanito\b",
    ]

    for pattern in jordan_patterns:
        if re.match(pattern, content):
            return "jordan"

    for pattern in vanito_patterns:
        if re.match(pattern, content):
            return "vanito"

    # Topic clues
    metaglasses_keywords = [
        "metaglasses", "ray-ban", "meta ray-ban", "ar glasses",
        "vr glasses", "emulation", "xenia", "rpcs3"
    ]
    coordination_keywords = [
        "x402", "deploy", "grant", "build queue", "strategy",
        "task", "priority", "blocked"
    ]

    metaglasses_count = sum(1 for kw in metaglasses_keywords if kw in content)
    coordination_count = sum(1 for kw in coordination_keywords if kw in content)

    if metaglasses_count > coordination_count:
        return "vanito"
    elif coordination_count > metaglasses_count:
        return "jordan"

    # Default: unknown
    return None


def detect_collaborator(message_metadata, message_content):
    """Detect collaborator from message metadata and content."""
    mapping = load_mapping()

    # Method 1: User ID (most reliable)
    telegram_id = message_metadata.get("telegram_user_id", None)
    if telegram_id:
        collaborator = detect_by_user_id(telegram_id, mapping)
        if collaborator:
            return {
                "collaborator": collaborator,
                "method": "user_id",
                "confidence": "high"
            }

    # Method 2: Username (reliable)
    telegram_username = message_metadata.get("telegram_username", None)
    if telegram_username:
        collaborator = detect_by_username(telegram_username, mapping)
        if collaborator:
            return {
                "collaborator": collaborator,
                "method": "username",
                "confidence": "high"
            }

    # Method 3: Pattern detection (fallback)
    collaborator = detect_by_pattern(message_content)
    if collaborator:
        return {
            "collaborator": collaborator,
            "method": "pattern",
            "confidence": "medium"
        }

    # Unknown
    return {
        "collaborator": None,
        "method": "unknown",
        "confidence": "low"
    }


def load_profile(collaborator_name):
    """Load collaborator profile from file."""
    mapping = load_mapping()
    collab_data = mapping["collaborators"].get(collaborator_name)

    if not collab_data:
        return None

    profile_path = Path(collab_data.get("profile", ""))
    if not profile_path.exists():
        return None

    with open(profile_path, "r") as f:
        content = f.read()

    return {
        "name": collaborator_name,
        "content": content,
        "topics": collab_data.get("topics", []),
        "permissions": collab_data.get("permissions", [])
    }


def check_permission(collaborator_name, action):
    """Check if collaborator has permission for action."""
    profile = load_profile(collaborator_name)

    if not profile:
        return False

    permissions = profile.get("permissions", [])

    if "all" in permissions:
        return True

    if action in permissions:
        return True

    return False


def can_use_skill(collaborator_name, skill_name):
    """Check if collaborator can use a specific skill."""
    profile = load_profile(collaborator_name)

    if not profile:
        return False

    permissions = profile.get("permissions", [])

    # Jordan has all permissions
    if "all" in permissions:
        return True

    # Vanito has limited permissions
    skill_allowed = {
        "entertainment": True,
        "metaglasses": True,
        "ar-vr": True,
        "gaming": True,
        "social-content": True,
        "game-intelligence": True,
        # Blocked skills
        "deploy": False,
        "finance": False,
        "defi": False,
        "defi-operations": False,
        "x402-payments": False,
        "cron-truth-layer": False,
    }

    return skill_allowed.get(skill_name, False)


def get_skill_permission_matrix():
    """Get full skill permission matrix for all collaborators."""
    mapping = load_mapping()
    matrix = {}

    for collaborator_name in mapping["collaborators"].keys():
        matrix[collaborator_name] = {
            "all": can_use_skill(collaborator_name, "any"),
            "entertainment": can_use_skill(collaborator_name, "entertainment"),
            "metaglasses": can_use_skill(collaborator_name, "metaglasses"),
            "gaming": can_use_skill(collaborator_name, "gaming"),
            "deploy": can_use_skill(collaborator_name, "deploy"),
            "finance": can_use_skill(collaborator_name, "finance"),
            "defi": can_use_skill(collaborator_name, "defi"),
        }

    return matrix


def add_mapping(collaborator_name, telegram_id=None, telegram_username=None):
    """Add or update collaborator mapping."""
    mapping = load_mapping()

    if collaborator_name not in mapping["collaborators"]:
        mapping["collaborators"][collaborator_name] = {}

    if telegram_id:
        mapping["collaborators"][collaborator_name]["telegram_id"] = telegram_id

    if telegram_username:
        if not telegram_username.startswith("@"):
            telegram_username = "@" + telegram_username
        mapping["collaborators"][collaborator_name]["telegram_username"] = telegram_username

    mapping["last_updated"] = "2026-07-06"
    save_mapping(mapping)

    return mapping["collaborators"][collaborator_name]


def get_collaborator_context(message_metadata, message_content):
    """Get full context for a message from a collaborator."""
    detection = detect_collaborator(message_metadata, message_content)
    collaborator = detection["collaborator"]

    if not collaborator:
        return {
            "collaborator": None,
            "profile": None,
            "method": detection["method"],
            "confidence": detection["confidence"],
            "action": "ask_who"
        }

    profile = load_profile(collaborator)

    return {
        "collaborator": collaborator,
        "profile": profile,
        "method": detection["method"],
        "confidence": detection["confidence"],
        "action": "route"
    }


# Testing
if __name__ == "__main__":
    print("Collaborator Identification — Test Suite")
    print("=" * 50)

    # Test 1: Jordan by pattern
    result = detect_collaborator({}, "Jordan: Deploy x402")
    print(f"Test 1 (Jordan by pattern): {result['collaborator']}")

    # Test 2: Vanito by pattern
    result = detect_collaborator({}, "Vanito here: Check out metaglasses")
    print(f"Test 2 (Vanito by pattern): {result['collaborator']}")

    # Test 3: Unknown user
    result = detect_collaborator({}, "Build this feature")
    print(f"Test 3 (Unknown user): {result['collaborator']}")

    # Test 4: Pattern detection (metaglasses)
    result = detect_collaborator({}, "The metaglasses are working great!")
    print(f"Test 4 (Metaglasses pattern): {result['collaborator']}")

    # Test 5: Pattern detection (coordination)
    result = detect_collaborator({}, "Deploy the grant application")
    print(f"Test 5 (Coordination pattern): {result['collaborator']}")

    # Test 6: Load Jordan profile
    profile = load_profile("jordan")
    print(f"Test 6 (Jordan profile topics): {profile['topics'] if profile else 'Not found'}")

    # Test 7: Check Jordan permission
    perm = check_permission("jordan", "deploy")
    print(f"Test 7 (Jordan deploy permission): {perm}")

    # Test 8: Check Vanito permission
    perm = check_permission("vanito", "deploy")
    print(f"Test 8 (Vanito deploy permission): {perm}")

    # Test 9: Jordan can use entertainment skill
    perm = can_use_skill("jordan", "entertainment")
    print(f"Test 9 (Jordan entertainment skill): {perm}")

    # Test 10: Vanito can use entertainment skill
    perm = can_use_skill("vanito", "entertainment")
    print(f"Test 10 (Vanito entertainment skill): {perm}")

    # Test 11: Vanito cannot use deploy skill
    perm = can_use_skill("vanito", "deploy")
    print(f"Test 11 (Vanito deploy skill): {perm}")

    # Test 12: Vanito can use gaming skill
    perm = can_use_skill("vanito", "gaming")
    print(f"Test 12 (Vanito gaming skill): {perm}")

    # Test 13: Get full permission matrix
    matrix = get_skill_permission_matrix()
    print(f"Test 13 (Permission matrix):")
    for collab, skills in matrix.items():
        print(f"  {collab}: {skills}")

    print("=" * 50)
    print("All tests complete")