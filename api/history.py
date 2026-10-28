"""Persistent war history (clan_history.json)."""

import json
import os
from datetime import datetime, timezone

from config import CLAN_TAG, DATA_FILE, PUBLISHED_HISTORY_FILE


def utc_now() -> str:
    """Current time as an ISO 8601 string with an explicit UTC offset."""
    return datetime.now(timezone.utc).isoformat()


def parse_coc_time(value: str | None) -> str | None:
    """Convert a CoC API timestamp (20261028T090000.000Z) to ISO 8601 UTC."""
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y%m%dT%H%M%S.%fZ").replace(tzinfo=timezone.utc).isoformat()
    except ValueError:
        return None


def load_historical_data() -> dict:
    """Load historical data from JSON file.

    Local runs write to api/out/; until the first local save they start from
    the committed history so they see the same wars as the daily workflow.
    """
    for path in (DATA_FILE, PUBLISHED_HISTORY_FILE):
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"⚠️  Warning: Could not load historical data from {path}: {e}")
                continue
            for player in data.get("players", {}).values():
                recompute_player_totals(player)
            return data
    return create_empty_data_structure()


def save_historical_data(data: dict):
    """Save historical data to JSON file."""
    try:
        os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"\n💾 Data saved to {DATA_FILE}")
    except IOError as e:
        print(f"❌ Error saving data: {e}")


def create_empty_data_structure() -> dict:
    """Create an empty data structure for historical tracking."""
    return {
        "clan_tag": CLAN_TAG,
        "last_updated": None,
        "players": {},  # Player tag -> player historical data
        "cwl_seasons": {},  # Season ID -> CWL data
        "wars": {},  # War ID -> war data
        "war_log": [],  # List of war summaries
    }


def generate_war_id(war: dict) -> str:
    """Generate a unique ID for a war based on participants and timing."""
    clan_tag = war.get('clan', {}).get('tag', '')
    opponent_tag = war.get('opponent', {}).get('tag', '')
    # Use preparation start time if available, or generate from tags
    prep_time = war.get('preparationStartTime', '')
    return f"{clan_tag}_{opponent_tag}_{prep_time}"


def recompute_player_totals(player: dict):
    """Derive a player's totals from their attack history and war list."""
    attacks = player.get("attacks_history", [])
    stars = [a.get("stars", 0) for a in attacks]
    player["total_attacks"] = len(attacks)
    player["total_stars"] = sum(stars)
    player["total_destruction"] = float(sum(a.get("destruction", 0) for a in attacks))
    player["three_stars"] = stars.count(3)
    player["two_stars"] = stars.count(2)
    player["one_star"] = stars.count(1)
    player["zero_stars"] = stars.count(0)
    player["wars_participated"] = len(player.get("war_ids", []))


def update_player_historical_stats(historical_data: dict, player_tag: str, player_name: str,
                                   th_level: int, attack_data: dict, war_type: str, war_id: str,
                                   war_date: str | None = None):
    """Record a player's attacks for one war.

    Safe to call on every run: the attacks stored for war_id are replaced with
    the latest snapshot, so attacks made after an earlier run during the same
    war are picked up instead of being lost.
    """
    if player_tag not in historical_data["players"]:
        historical_data["players"][player_tag] = {
            "name": player_name,
            "tag": player_tag,
            "current_th": th_level,
            "total_attacks": 0,
            "total_stars": 0,
            "total_destruction": 0.0,
            "three_stars": 0,
            "two_stars": 0,
            "one_star": 0,
            "zero_stars": 0,
            "wars_participated": 0,
            "cwl_seasons": 0,
            "attacks_history": [],  # List of individual attacks
            "war_ids": [],  # Track which wars they participated in
        }

    player = historical_data["players"][player_tag]
    player["name"] = player_name  # Update name in case it changed
    player["current_th"] = max(player["current_th"], th_level)

    if war_id not in player["war_ids"]:
        player["war_ids"].append(war_id)

    previous = [a for a in player["attacks_history"] if a.get("war_id") == war_id]
    date = war_date or (previous[0]["date"] if previous else utc_now())
    player["attacks_history"] = [a for a in player["attacks_history"] if a.get("war_id") != war_id]

    for attack in attack_data.get('attacks', []):
        player["attacks_history"].append({
            "war_id": war_id,
            "war_type": war_type,
            "date": date,
            "stars": attack.get('stars', 0),
            "destruction": attack.get('destruction', 0),
            "defender_th": attack.get('defender_th', 0),
            "attacker_th": th_level,
            "hit_type": attack.get('hit_type', 'unknown')
        })

    recompute_player_totals(player)
