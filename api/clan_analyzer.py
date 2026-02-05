"""
Clash of Clans Clan Analyzer
Comprehensive analysis of clan and player data
With persistent data storage for historical tracking
"""

import requests
import json
from collections import defaultdict
from datetime import datetime
import urllib.parse
import os
from pathlib import Path
from dotenv import load_dotenv
import time

# Load environment variables from .env file (look in parent directory)
env_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(env_path)

# API Configuration - Load from environment
API_TOKEN = os.getenv('api_key', '')
if not API_TOKEN:
    raise ValueError("API key not found! Please set 'api_key' in your .env file")

BASE_URL = "https://api.clashofclans.com/v1"
CLAN_TAG = "#2J28LL2VU"

# Data storage files
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(SCRIPT_DIR, "clan_history.json")
HTML_REPORT_FILE = os.path.join(SCRIPT_DIR, "clan_dashboard.html")
# Comprehensive data output for Next.js dashboard
DASHBOARD_DATA_FILE = os.path.join(SCRIPT_DIR, "..", "coc-dashboard", "public", "clan_data.json")

# Headers for API requests
HEADERS = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Accept": "application/json"
}


# ============================================================================
# RUSH DETECTION DATA - Max levels per Town Hall
# ============================================================================

# Hero max levels by Town Hall (TH7-TH17)
# Updated for 2025 with Hero Hall system - levels are approximate max at each TH
# Note: Actual max depends on Hero Hall level, these are typical maximums
HERO_MAX_LEVELS = {
    "Barbarian King": {7: 5, 8: 10, 9: 30, 10: 40, 11: 50, 12: 65, 13: 75, 14: 85, 15: 90, 16: 95, 17: 100, 18: 105},
    "Archer Queen": {8: 10, 9: 30, 10: 40, 11: 50, 12: 65, 13: 75, 14: 85, 15: 90, 16: 95, 17: 100, 18: 105},
    "Grand Warden": {11: 20, 12: 40, 13: 50, 14: 55, 15: 65, 16: 70, 17: 75, 18: 80},
    "Royal Champion": {13: 25, 14: 30, 15: 40, 16: 45, 17: 50, 18: 55},
    "Minion Prince": {9: 10, 10: 20, 11: 30, 12: 40, 13: 50, 14: 60, 15: 70, 16: 80, 17: 90, 18: 95},
}

# Key troops max levels by Town Hall (simplified - focusing on important troops)
TROOP_MAX_LEVELS = {
    "Barbarian": {1: 1, 2: 1, 3: 2, 4: 2, 5: 3, 6: 4, 7: 4, 8: 5, 9: 6, 10: 7, 11: 8, 12: 9, 13: 10, 14: 11, 15: 11, 16: 12, 17: 12},
    "Archer": {1: 1, 2: 1, 3: 2, 4: 2, 5: 3, 6: 4, 7: 4, 8: 5, 9: 6, 10: 7, 11: 8, 12: 9, 13: 10, 14: 11, 15: 11, 16: 12, 17: 12},
    "Giant": {1: 1, 2: 1, 3: 2, 4: 2, 5: 3, 6: 4, 7: 5, 8: 6, 9: 7, 10: 8, 11: 9, 12: 10, 13: 10, 14: 11, 15: 11, 16: 12, 17: 12},
    "Balloon": {4: 2, 5: 3, 6: 4, 7: 5, 8: 6, 9: 6, 10: 7, 11: 8, 12: 9, 13: 10, 14: 10, 15: 10, 16: 11, 17: 11},
    "Wizard": {5: 3, 6: 4, 7: 4, 8: 5, 9: 6, 10: 7, 11: 9, 12: 10, 13: 10, 14: 11, 15: 11, 16: 12, 17: 12},
    "Healer": {4: 1, 5: 2, 6: 3, 7: 3, 8: 4, 9: 4, 10: 5, 11: 5, 12: 6, 13: 7, 14: 8, 15: 8, 16: 9, 17: 9},
    "Dragon": {7: 2, 8: 3, 9: 4, 10: 5, 11: 6, 12: 7, 13: 8, 14: 9, 15: 10, 16: 11, 17: 12},
    "P.E.K.K.A": {8: 3, 9: 4, 10: 5, 11: 6, 12: 7, 13: 8, 14: 9, 15: 10, 16: 10, 17: 11},
    "Golem": {8: 2, 9: 4, 10: 5, 11: 6, 12: 7, 13: 9, 14: 10, 15: 11, 16: 12, 17: 13},
    "Witch": {9: 2, 10: 3, 11: 4, 12: 5, 13: 5, 14: 6, 15: 6, 16: 7, 17: 7},
    "Lava Hound": {9: 2, 10: 3, 11: 4, 12: 5, 13: 6, 14: 6, 15: 6, 16: 7, 17: 7},
    "Bowler": {10: 2, 11: 3, 12: 4, 13: 5, 14: 6, 15: 6, 16: 7, 17: 7},
    "Miner": {10: 3, 11: 5, 12: 6, 13: 7, 14: 8, 15: 8, 16: 9, 17: 9},
    "Electro Dragon": {11: 2, 12: 3, 13: 4, 14: 5, 15: 5, 16: 6, 17: 6},
    "Yeti": {12: 2, 13: 3, 14: 4, 15: 4, 16: 5, 17: 5},
    "Dragon Rider": {14: 2, 15: 3, 16: 3, 17: 4},
    "Electro Titan": {15: 2, 16: 3, 17: 3},
    "Root Rider": {16: 2, 17: 3},
}

# Spell max levels by Town Hall
SPELL_MAX_LEVELS = {
    "Lightning Spell": {5: 4, 6: 4, 7: 4, 8: 5, 9: 6, 10: 7, 11: 8, 12: 9, 13: 9, 14: 10, 15: 10, 16: 11, 17: 11},
    "Healing Spell": {6: 3, 7: 4, 8: 5, 9: 6, 10: 7, 11: 7, 12: 8, 13: 8, 14: 9, 15: 9, 16: 10, 17: 10},
    "Rage Spell": {7: 4, 8: 5, 9: 5, 10: 5, 11: 6, 12: 6, 13: 6, 14: 6, 15: 6, 16: 6, 17: 6},
    "Jump Spell": {9: 2, 10: 3, 11: 3, 12: 4, 13: 4, 14: 5, 15: 5, 16: 5, 17: 5},
    "Freeze Spell": {9: 1, 10: 5, 11: 6, 12: 7, 13: 7, 14: 7, 15: 7, 16: 8, 17: 8},
    "Poison Spell": {8: 2, 9: 3, 10: 4, 11: 5, 12: 6, 13: 7, 14: 8, 15: 9, 16: 10, 17: 10},
    "Earthquake Spell": {8: 2, 9: 3, 10: 4, 11: 5, 12: 5, 13: 5, 14: 5, 15: 5, 16: 5, 17: 5},
    "Haste Spell": {9: 2, 10: 4, 11: 5, 12: 5, 13: 5, 14: 5, 15: 5, 16: 5, 17: 5},
    "Clone Spell": {10: 3, 11: 5, 12: 6, 13: 7, 14: 7, 15: 8, 16: 8, 17: 8},
    "Invisibility Spell": {11: 2, 12: 3, 13: 4, 14: 4, 15: 4, 16: 4, 17: 4},
    "Recall Spell": {13: 2, 14: 3, 15: 4, 16: 5, 17: 5},
    "Bat Spell": {10: 3, 11: 4, 12: 5, 13: 5, 14: 5, 15: 5, 16: 5, 17: 5},
    "Overgrowth Spell": {15: 2, 16: 3, 17: 3},
}


# ============================================================================
# DATA PERSISTENCE FUNCTIONS
# ============================================================================

def load_historical_data() -> dict:
    """Load historical data from JSON file."""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"⚠️  Warning: Could not load historical data: {e}")
            return create_empty_data_structure()
    return create_empty_data_structure()


def save_historical_data(data: dict):
    """Save historical data to JSON file."""
    try:
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


def update_player_historical_stats(historical_data: dict, player_tag: str, player_name: str, 
                                    th_level: int, attack_data: dict, war_type: str, war_id: str):
    """Update a player's historical statistics with new attack data."""
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
    
    # Check if this war was already recorded
    if war_id in player["war_ids"]:
        return  # Already recorded this war
    
    player["war_ids"].append(war_id)
    player["wars_participated"] += 1
    
    # Add attack data
    for attack in attack_data.get('attacks', []):
        attack_record = {
            "war_id": war_id,
            "war_type": war_type,
            "date": datetime.now().isoformat(),
            "stars": attack.get('stars', 0),
            "destruction": attack.get('destruction', 0),
            "defender_th": attack.get('defender_th', 0),
            "attacker_th": th_level,
            "hit_type": attack.get('hit_type', 'unknown')
        }
        player["attacks_history"].append(attack_record)
        
        player["total_attacks"] += 1
        player["total_stars"] += attack.get('stars', 0)
        player["total_destruction"] += attack.get('destruction', 0)
        
        stars = attack.get('stars', 0)
        if stars == 3:
            player["three_stars"] += 1
        elif stars == 2:
            player["two_stars"] += 1
        elif stars == 1:
            player["one_star"] += 1
        else:
            player["zero_stars"] += 1


# ============================================================================
# RUSH DETECTION FUNCTIONS
# ============================================================================

def get_max_level_for_th(item_name: str, th_level: int, item_type: str = "hero") -> int | None:
    """Get the max level for an item at a specific Town Hall."""
    if item_type == "hero":
        levels = HERO_MAX_LEVELS.get(item_name, {})
    elif item_type == "troop":
        levels = TROOP_MAX_LEVELS.get(item_name, {})
    elif item_type == "spell":
        levels = SPELL_MAX_LEVELS.get(item_name, {})
    else:
        return None
    
    return levels.get(th_level)


def generate_rush_report(player: dict) -> dict:
    """
    Generate a rush report for a player.
    Compares current levels to max levels at PREVIOUS Town Hall.
    """
    th_level = player.get('townHallLevel', 1)
    
    # If player is TH1 or TH2, they can't really be rushed
    if th_level <= 2:
        return {
            "is_rushed": False,
            "rush_score": 0,
            "rush_percentage": 0,
            "rushed_heroes": [],
            "rushed_troops": [],
            "rushed_spells": [],
            "status": "New Account"
        }
    
    previous_th = th_level - 1
    
    rush_data = {
        "is_rushed": False,
        "rush_score": 0.0,
        "rush_percentage": 0,
        "rushed_heroes": [],
        "rushed_troops": [],
        "rushed_spells": [],
        "hero_score": 0,
        "troop_score": 0,
        "spell_score": 0,
        "total_missing_hero_levels": 0,
        "status": "Not Rushed"
    }
    
    # --- 1. CHECK HEROES (Most important - weight: 1.0 per level) ---
    heroes = player.get('heroes', [])
    total_hero_possible = 0
    total_hero_current = 0
    
    for hero in heroes:
        hero_name = hero.get('name', '')
        hero_level = hero.get('level', 0)
        village = hero.get('village', '')
        
        # Only check home village heroes
        if village != 'home':
            continue
        
        # Get max level at previous TH
        max_at_prev = get_max_level_for_th(hero_name, previous_th, "hero")
        
        if max_at_prev is not None and max_at_prev > 0:
            total_hero_possible += max_at_prev
            total_hero_current += min(hero_level, max_at_prev)
            
            if hero_level < max_at_prev:
                missing_levels = max_at_prev - hero_level
                rush_data["rushed_heroes"].append({
                    "name": hero_name,
                    "current": hero_level,
                    "target": max_at_prev,
                    "missing": missing_levels
                })
                rush_data["hero_score"] += missing_levels  # Full weight for heroes
                rush_data["total_missing_hero_levels"] += missing_levels
    
    # --- 2. CHECK TROOPS (weight: 0.3 per level) ---
    troops = player.get('troops', [])
    total_troop_possible = 0
    total_troop_current = 0
    
    for troop in troops:
        troop_name = troop.get('name', '')
        troop_level = troop.get('level', 0)
        village = troop.get('village', '')
        
        # Only check home village troops
        if village != 'home':
            continue
        
        max_at_prev = get_max_level_for_th(troop_name, previous_th, "troop")
        
        if max_at_prev is not None and max_at_prev > 0:
            total_troop_possible += max_at_prev
            total_troop_current += min(troop_level, max_at_prev)
            
            if troop_level < max_at_prev:
                missing_levels = max_at_prev - troop_level
                rush_data["rushed_troops"].append({
                    "name": troop_name,
                    "current": troop_level,
                    "target": max_at_prev,
                    "missing": missing_levels
                })
                rush_data["troop_score"] += missing_levels * 0.3  # Lower weight
    
    # --- 3. CHECK SPELLS (weight: 0.4 per level) ---
    spells = player.get('spells', [])
    total_spell_possible = 0
    total_spell_current = 0
    
    for spell in spells:
        spell_name = spell.get('name', '')
        spell_level = spell.get('level', 0)
        village = spell.get('village', '')
        
        if village != 'home':
            continue
        
        max_at_prev = get_max_level_for_th(spell_name, previous_th, "spell")
        
        if max_at_prev is not None and max_at_prev > 0:
            total_spell_possible += max_at_prev
            total_spell_current += min(spell_level, max_at_prev)
            
            if spell_level < max_at_prev:
                missing_levels = max_at_prev - spell_level
                rush_data["rushed_spells"].append({
                    "name": spell_name,
                    "current": spell_level,
                    "target": max_at_prev,
                    "missing": missing_levels
                })
                rush_data["spell_score"] += missing_levels * 0.4
    
    # --- 4. CALCULATE FINAL SCORES ---
    rush_data["rush_score"] = rush_data["hero_score"] + rush_data["troop_score"] + rush_data["spell_score"]
    
    # Calculate overall rush percentage (how far behind they are)
    total_possible = total_hero_possible + total_troop_possible + total_spell_possible
    total_current = total_hero_current + total_troop_current + total_spell_current
    
    if total_possible > 0:
        completion_pct = (total_current / total_possible) * 100
        rush_data["rush_percentage"] = round(100 - completion_pct, 1)
    
    # --- 5. DETERMINE STATUS ---
    score = rush_data["rush_score"]
    hero_missing = rush_data["total_missing_hero_levels"]
    
    if score <= 3:
        rush_data["status"] = "✅ Maxed"
        rush_data["is_rushed"] = False
    elif score <= 10:
        rush_data["status"] = "🟢 Slightly Behind"
        rush_data["is_rushed"] = False
    elif score <= 25:
        rush_data["status"] = "🟡 Moderately Rushed"
        rush_data["is_rushed"] = True
    elif score <= 50:
        rush_data["status"] = "🟠 Rushed"
        rush_data["is_rushed"] = True
    else:
        rush_data["status"] = "🔴 Severely Rushed"
        rush_data["is_rushed"] = True
    
    # Extra penalty for very low heroes
    if hero_missing > 20:
        rush_data["status"] = "🔴 Severely Rushed (Heroes)"
        rush_data["is_rushed"] = True
    
    return rush_data


def analyze_clan_rush(players_data: list) -> list:
    """Analyze rush status for all clan members."""
    print_separator("RUSH ANALYSIS")
    
    rush_reports = []
    
    for player in players_data:
        report = generate_rush_report(player)
        report["player_name"] = player.get('name', 'Unknown')
        report["player_tag"] = player.get('tag', '')
        report["th_level"] = player.get('townHallLevel', 0)
        rush_reports.append(report)
    
    # Sort by rush score (most rushed first)
    rush_reports.sort(key=lambda x: -x["rush_score"])
    
    # Print summary
    rushed_count = sum(1 for r in rush_reports if r["is_rushed"])
    total = len(rush_reports)
    
    print(f"\n📊 CLAN RUSH OVERVIEW:")
    print(f"   Total Members: {total}")
    print(f"   Rushed Players: {rushed_count} ({rushed_count/total*100:.1f}%)")
    print(f"   Not Rushed: {total - rushed_count} ({(total-rushed_count)/total*100:.1f}%)")
    
    # Status distribution
    status_counts = defaultdict(int)
    for r in rush_reports:
        status_counts[r["status"]] += 1
    
    print(f"\n📈 STATUS DISTRIBUTION:")
    for status, count in sorted(status_counts.items(), key=lambda x: -x[1]):
        print(f"   {status}: {count}")
    
    # Print detailed table
    print(f"\n{'#':<3} {'Player':<18} {'TH':<4} {'Score':<8} {'Heroes':<8} {'Status':<25}")
    print(f"{'-'*75}")
    
    for i, report in enumerate(rush_reports, 1):
        name = report["player_name"][:17]
        th = report["th_level"]
        score = report["rush_score"]
        hero_missing = report["total_missing_hero_levels"]
        status = report["status"]
        
        print(f"{i:<3} {name:<18} {th:<4} {score:<8.1f} -{hero_missing:<7} {status}")
    
    # Most rushed heroes
    print(f"\n⚠️  PLAYERS WITH MOST RUSHED HEROES:")
    hero_rushed = [(r["player_name"], r["th_level"], r["total_missing_hero_levels"], r["rushed_heroes"]) 
                   for r in rush_reports if r["total_missing_hero_levels"] > 5]
    hero_rushed.sort(key=lambda x: -x[2])
    
    for name, th, missing, heroes in hero_rushed[:10]:
        hero_details = ", ".join([f"{h['name'][:2]}: {h['current']}/{h['target']}" for h in heroes[:4]])
        print(f"   • {name} (TH{th}): -{missing} levels [{hero_details}]")
    
    return rush_reports


def encode_tag(tag: str) -> str:
    """URL encode a clan or player tag."""
    return urllib.parse.quote(tag)


def api_request(endpoint: str) -> dict | None:
    """Make an API request and return JSON response."""
    url = f"{BASE_URL}{endpoint}"
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e}")
        print(f"Response: {response.text}")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None


def get_clan_info(clan_tag: str) -> dict | None:
    """Get detailed clan information."""
    return api_request(f"/clans/{encode_tag(clan_tag)}")


def get_clan_members(clan_tag: str) -> list | None:
    """Get list of clan members."""
    data = api_request(f"/clans/{encode_tag(clan_tag)}/members")
    return data.get("items", []) if data else None


def get_clan_warlog(clan_tag: str) -> list | None:
    """Get clan war log."""
    data = api_request(f"/clans/{encode_tag(clan_tag)}/warlog")
    return data.get("items", []) if data else None


def get_current_war(clan_tag: str) -> dict | None:
    """Get current war information."""
    return api_request(f"/clans/{encode_tag(clan_tag)}/currentwar")


def get_player_info(player_tag: str) -> dict | None:
    """Get detailed player information."""
    return api_request(f"/players/{encode_tag(player_tag)}")


def get_cwl_group(clan_tag: str) -> dict | None:
    """Get CWL league group information."""
    return api_request(f"/clans/{encode_tag(clan_tag)}/currentwar/leaguegroup")


def get_cwl_war(war_tag: str) -> dict | None:
    """Get specific CWL war details."""
    return api_request(f"/clanwarleagues/wars/{encode_tag(war_tag)}")


def get_capital_raid_seasons(clan_tag: str, limit: int = 10) -> list | None:
    """Get clan's capital raid seasons."""
    data = api_request(f"/clans/{encode_tag(clan_tag)}/capitalraidseasons?limit={limit}")
    return data.get("items", []) if data else None


# ============================================================================
# ADDITIONAL API ENDPOINTS - Leagues, Locations, Labels, Gold Pass
# ============================================================================

def get_leagues() -> list | None:
    """Get list of all leagues."""
    data = api_request("/leagues")
    return data.get("items", []) if data else None


def get_war_leagues() -> list | None:
    """Get list of all war leagues."""
    data = api_request("/warleagues")
    return data.get("items", []) if data else None


def get_capital_leagues() -> list | None:
    """Get list of all capital leagues."""
    data = api_request("/capitalleagues")
    return data.get("items", []) if data else None


def get_builder_base_leagues() -> list | None:
    """Get list of all builder base leagues."""
    data = api_request("/builderbaseleagues")
    return data.get("items", []) if data else None


def get_locations() -> list | None:
    """Get list of all locations."""
    data = api_request("/locations")
    return data.get("items", []) if data else None


def get_location_clan_rankings(location_id: int, limit: int = 200) -> list | None:
    """Get clan rankings for a specific location."""
    data = api_request(f"/locations/{location_id}/rankings/clans?limit={limit}")
    return data.get("items", []) if data else None


def get_location_player_rankings(location_id: int, limit: int = 200) -> list | None:
    """Get player rankings for a specific location."""
    data = api_request(f"/locations/{location_id}/rankings/players?limit={limit}")
    return data.get("items", []) if data else None


def get_location_capital_rankings(location_id: int, limit: int = 200) -> list | None:
    """Get capital rankings for a specific location."""
    data = api_request(f"/locations/{location_id}/rankings/capitals?limit={limit}")
    return data.get("items", []) if data else None


def get_player_labels() -> list | None:
    """Get list of all player labels."""
    data = api_request("/labels/players")
    return data.get("items", []) if data else None


def get_clan_labels() -> list | None:
    """Get list of all clan labels."""
    data = api_request("/labels/clans")
    return data.get("items", []) if data else None


def get_gold_pass_season() -> dict | None:
    """Get current gold pass season information."""
    return api_request("/goldpass/seasons/current")


def print_separator(title: str = "", char: str = "=", length: int = 80):
    """Print a separator line."""
    if title:
        padding = (length - len(title) - 2) // 2
        print(f"\n{char * padding} {title} {char * padding}")
    else:
        print(char * length)


def analyze_clan_info(clan: dict):
    """Analyze and display clan information."""
    print_separator("CLAN INFORMATION")
    
    print(f"\n🏰 Clan Name: {clan.get('name', 'N/A')}")
    print(f"🏷️  Clan Tag: {clan.get('tag', 'N/A')}")
    print(f"📝 Description: {clan.get('description', 'N/A')}")
    print(f"🌍 Location: {clan.get('location', {}).get('name', 'N/A')}")
    print(f"🗣️  Language: {clan.get('chatLanguage', {}).get('name', 'N/A')}")
    print(f"📊 Clan Level: {clan.get('clanLevel', 'N/A')}")
    print(f"🏆 Clan Points: {clan.get('clanPoints', 'N/A'):,}")
    print(f"⚔️  Clan Builder Base Points: {clan.get('clanBuilderBasePoints', 'N/A'):,}")
    print(f"🏅 Clan Capital Points: {clan.get('clanCapitalPoints', 'N/A'):,}")
    print(f"👥 Members: {clan.get('members', 'N/A')}/50")
    print(f"🔒 Type: {clan.get('type', 'N/A')}")
    print(f"⚔️  War Frequency: {clan.get('warFrequency', 'N/A')}")
    print(f"🏆 War Win Streak: {clan.get('warWinStreak', 'N/A')}")
    print(f"✅ War Wins: {clan.get('warWins', 'N/A')}")
    print(f"➖ War Ties: {clan.get('warTies', 'N/A')}")
    print(f"❌ War Losses: {clan.get('warLosses', 'N/A')}")
    print(f"⚔️  War League: {clan.get('warLeague', {}).get('name', 'N/A')}")
    print(f"🏛️  Capital League: {clan.get('capitalLeague', {}).get('name', 'N/A')}")
    
    # War statistics
    total_wars = clan.get('warWins', 0) + clan.get('warTies', 0) + clan.get('warLosses', 0)
    if total_wars > 0:
        win_rate = (clan.get('warWins', 0) / total_wars) * 100
        print(f"\n📈 War Win Rate: {win_rate:.1f}%")
    
    # Clan Labels
    labels = clan.get('labels', [])
    if labels:
        print(f"\n🏷️  Clan Labels:")
        for label in labels:
            print(f"   • {label.get('name', 'N/A')}")
    
    # Clan Capital
    clan_capital = clan.get('clanCapital', {})
    if clan_capital:
        print(f"\n🏛️  CLAN CAPITAL:")
        print(f"   Capital Hall Level: {clan_capital.get('capitalHallLevel', 'N/A')}")
        districts = clan_capital.get('districts', [])
        if districts:
            print(f"   Districts ({len(districts)}):")
            for district in districts:
                print(f"   • {district.get('name', 'N/A')} (Level {district.get('districtHallLevel', 'N/A')})")


def analyze_members(members: list, players_data: list):
    """Analyze clan members."""
    print_separator("MEMBER ANALYSIS")
    
    # Role distribution
    roles = defaultdict(int)
    for member in members:
        roles[member.get('role', 'unknown')] += 1
    
    print(f"\n👥 ROLE DISTRIBUTION:")
    role_emojis = {'leader': '👑', 'coLeader': '⭐', 'admin': '🛡️', 'member': '👤'}
    for role, count in sorted(roles.items(), key=lambda x: -x[1]):
        emoji = role_emojis.get(role, '❓')
        print(f"   {emoji} {role}: {count}")
    
    # Trophy analysis
    trophies = [m.get('trophies', 0) for m in members]
    print(f"\n🏆 TROPHY STATISTICS:")
    print(f"   Total Clan Trophies: {sum(trophies):,}")
    print(f"   Average Trophies: {sum(trophies)/len(trophies):,.0f}")
    print(f"   Highest: {max(trophies):,}")
    print(f"   Lowest: {min(trophies):,}")
    
    # Experience level analysis
    levels = [m.get('expLevel', 0) for m in members]
    print(f"\n📊 EXPERIENCE LEVEL STATISTICS:")
    print(f"   Average Level: {sum(levels)/len(levels):.1f}")
    print(f"   Highest: {max(levels)}")
    print(f"   Lowest: {min(levels)}")
    
    # League distribution
    leagues = defaultdict(int)
    for member in members:
        league = member.get('league', {}).get('name', 'Unranked')
        leagues[league] += 1
    
    print(f"\n🎖️  LEAGUE DISTRIBUTION:")
    for league, count in sorted(leagues.items(), key=lambda x: -x[1]):
        print(f"   • {league}: {count} members")
    
    # Donations analysis
    donations = [(m.get('name'), m.get('donations', 0), m.get('donationsReceived', 0)) for m in members]
    donations_sorted = sorted(donations, key=lambda x: -x[1])
    
    print(f"\n🎁 TOP 10 DONATORS:")
    for i, (name, donated, received) in enumerate(donations_sorted[:10], 1):
        ratio = donated / received if received > 0 else donated
        print(f"   {i}. {name}: {donated:,} donated | {received:,} received | Ratio: {ratio:.2f}")
    
    total_donations = sum(d[1] for d in donations)
    total_received = sum(d[2] for d in donations)
    print(f"\n   📊 Clan Total Donations: {total_donations:,}")
    print(f"   📊 Clan Total Received: {total_received:,}")


def analyze_player_details(players_data: list):
    """Analyze detailed player information."""
    print_separator("DETAILED PLAYER ANALYSIS")
    
    # Town Hall distribution
    th_distribution = defaultdict(int)
    for player in players_data:
        th_level = player.get('townHallLevel', 0)
        th_distribution[th_level] += 1
    
    print(f"\n🏠 TOWN HALL DISTRIBUTION:")
    for th, count in sorted(th_distribution.items(), reverse=True):
        bar = "█" * count
        print(f"   TH{th:2d}: {bar} ({count})")
    
    # Builder Hall distribution
    bh_distribution = defaultdict(int)
    for player in players_data:
        bh_level = player.get('builderHallLevel', 0)
        if bh_level > 0:
            bh_distribution[bh_level] += 1
    
    if bh_distribution:
        print(f"\n🏗️  BUILDER HALL DISTRIBUTION:")
        for bh, count in sorted(bh_distribution.items(), reverse=True):
            bar = "█" * count
            print(f"   BH{bh:2d}: {bar} ({count})")
    
    # Hero analysis
    print(f"\n⚔️  HERO ANALYSIS:")
    hero_stats = defaultdict(list)
    
    for player in players_data:
        heroes = player.get('heroes', [])
        for hero in heroes:
            hero_name = hero.get('name', 'Unknown')
            hero_level = hero.get('level', 0)
            hero_max = hero.get('maxLevel', 0)
            if hero.get('village', '') == 'home':
                hero_stats[hero_name].append((player.get('name'), hero_level, hero_max))
    
    for hero_name, data in hero_stats.items():
        levels = [d[1] for d in data]
        if levels:
            avg = sum(levels) / len(levels)
            max_level = max(levels)
            min_level = min(levels)
            print(f"\n   🦸 {hero_name}:")
            print(f"      Players with hero: {len(levels)}")
            print(f"      Average Level: {avg:.1f}")
            print(f"      Highest: {max_level}")
            print(f"      Lowest: {min_level}")
    
    # Top players by hero levels
    print(f"\n🏆 TOP 10 PLAYERS BY COMBINED HERO LEVELS:")
    player_hero_totals = []
    for player in players_data:
        heroes = player.get('heroes', [])
        home_heroes = [h for h in heroes if h.get('village', '') == 'home']
        total = sum(h.get('level', 0) for h in home_heroes)
        player_hero_totals.append((player.get('name'), total, len(home_heroes)))
    
    player_hero_totals.sort(key=lambda x: -x[1])
    for i, (name, total, count) in enumerate(player_hero_totals[:10], 1):
        print(f"   {i}. {name}: {total} total ({count} heroes)")
    
    # Troop/Spell levels analysis
    print(f"\n🔬 TROOP & SPELL STATISTICS:")
    max_troops_players = []
    for player in players_data:
        troops = player.get('troops', [])
        home_troops = [t for t in troops if t.get('village', '') == 'home']
        total_levels = sum(t.get('level', 0) for t in home_troops)
        max_troops_players.append((player.get('name'), total_levels, len(home_troops)))
    
    max_troops_players.sort(key=lambda x: -x[1])
    print(f"\n   🏆 TOP 10 BY TROOP LEVELS:")
    for i, (name, total, count) in enumerate(max_troops_players[:10], 1):
        print(f"   {i}. {name}: {total} total troop levels")
    
    # War Stars analysis
    print(f"\n⭐ WAR STARS ANALYSIS:")
    war_stars = [(p.get('name'), p.get('warStars', 0)) for p in players_data]
    war_stars.sort(key=lambda x: -x[1])
    
    total_war_stars = sum(w[1] for w in war_stars)
    avg_war_stars = total_war_stars / len(war_stars) if war_stars else 0
    
    print(f"   Total Clan War Stars: {total_war_stars:,}")
    print(f"   Average War Stars: {avg_war_stars:.0f}")
    
    print(f"\n   🏆 TOP 10 BY WAR STARS:")
    for i, (name, stars) in enumerate(war_stars[:10], 1):
        print(f"   {i}. {name}: {stars:,} ⭐")
    
    # Attack/Defense wins
    print(f"\n⚔️  ATTACK & DEFENSE STATISTICS:")
    attack_stats = [(p.get('name'), p.get('attackWins', 0), p.get('defenseWins', 0)) for p in players_data]
    attack_stats.sort(key=lambda x: -x[1])
    
    print(f"\n   🗡️  TOP 10 BY ATTACK WINS:")
    for i, (name, attacks, _) in enumerate(attack_stats[:10], 1):
        print(f"   {i}. {name}: {attacks:,} wins")
    
    defense_stats = sorted(attack_stats, key=lambda x: -x[2])
    print(f"\n   🛡️  TOP 10 BY DEFENSE WINS:")
    for i, (name, _, defenses) in enumerate(defense_stats[:10], 1):
        print(f"   {i}. {name}: {defenses:,} wins")
    
    # Clan Capital contributions
    print(f"\n🏛️  CLAN CAPITAL CONTRIBUTIONS:")
    capital_contributions = [(p.get('name'), p.get('clanCapitalContributions', 0)) for p in players_data]
    capital_contributions.sort(key=lambda x: -x[1])
    
    total_contributions = sum(c[1] for c in capital_contributions)
    print(f"   Total Clan Contributions: {total_contributions:,}")
    
    print(f"\n   🏆 TOP 10 CONTRIBUTORS:")
    for i, (name, contributions) in enumerate(capital_contributions[:10], 1):
        print(f"   {i}. {name}: {contributions:,}")


def analyze_warlog(warlog: list):
    """Analyze war log."""
    print_separator("WAR LOG ANALYSIS")
    
    if not warlog:
        print("\n⚠️  War log is not public or no wars found.")
        return
    
    print(f"\n📜 Total Wars in Log: {len(warlog)}")
    
    # Win/Loss/Tie breakdown
    results = defaultdict(int)
    for war in warlog:
        results[war.get('result', 'unknown')] += 1
    
    print(f"\n📊 WAR RESULTS:")
    result_emojis = {'win': '✅', 'lose': '❌', 'tie': '➖'}
    for result, count in results.items():
        emoji = result_emojis.get(result, '❓')
        percentage = (count / len(warlog)) * 100
        result_name = result.capitalize() if result else 'Unknown'
        print(f"   {emoji} {result_name}: {count} ({percentage:.1f}%)")
    
    # Stars analysis
    total_stars_for = 0
    total_stars_against = 0
    total_destruction_for = 0
    total_destruction_against = 0
    
    for war in warlog:
        clan_data = war.get('clan', {})
        opponent_data = war.get('opponent', {})
        
        total_stars_for += clan_data.get('stars', 0)
        total_stars_against += opponent_data.get('stars', 0)
        total_destruction_for += clan_data.get('destructionPercentage', 0)
        total_destruction_against += opponent_data.get('destructionPercentage', 0)
    
    print(f"\n⭐ STAR STATISTICS:")
    print(f"   Total Stars Earned: {total_stars_for}")
    print(f"   Total Stars Conceded: {total_stars_against}")
    print(f"   Star Difference: {total_stars_for - total_stars_against:+d}")
    print(f"   Average Stars per War: {total_stars_for / len(warlog):.1f}")
    
    print(f"\n💥 DESTRUCTION STATISTICS:")
    print(f"   Average Destruction Dealt: {total_destruction_for / len(warlog):.1f}%")
    print(f"   Average Destruction Received: {total_destruction_against / len(warlog):.1f}%")
    
    # War size analysis
    war_sizes = defaultdict(int)
    for war in warlog:
        size = war.get('teamSize', 0)
        war_sizes[size] += 1
    
    print(f"\n👥 WAR SIZE DISTRIBUTION:")
    for size, count in sorted(war_sizes.items(), reverse=True):
        print(f"   {size}v{size}: {count} wars")
    
    # Recent wars detail
    print(f"\n📋 RECENT 10 WARS:")
    print(f"   {'Opponent':<25} {'Result':<8} {'Stars':<10} {'Destruction':<15}")
    print(f"   {'-'*60}")
    
    for war in warlog[:10]:
        opponent_name = war.get('opponent', {}).get('name', 'Unknown')[:24]
        result = war.get('result', 'N/A')
        clan_stars = war.get('clan', {}).get('stars', 0)
        opp_stars = war.get('opponent', {}).get('stars', 0)
        clan_dest = war.get('clan', {}).get('destructionPercentage', 0)
        opp_dest = war.get('opponent', {}).get('destructionPercentage', 0)
        
        result_emoji = result_emojis.get(result, '❓')
        print(f"   {opponent_name:<25} {result_emoji} {result:<5} {clan_stars}-{opp_stars:<6} {clan_dest:.1f}% vs {opp_dest:.1f}%")


def analyze_current_war(war: dict):
    """Analyze current war if active."""
    print_separator("CURRENT WAR")
    
    state = war.get('state', 'notInWar')
    
    if state == 'notInWar':
        print("\n⚠️  Clan is not currently in a war.")
        return None
    
    print(f"\n⚔️  War State: {state}")
    
    clan = war.get('clan', {})
    opponent = war.get('opponent', {})
    
    print(f"\n🏰 {clan.get('name', 'Your Clan')} vs 🏰 {opponent.get('name', 'Opponent')}")
    print(f"   Team Size: {war.get('teamSize', 'N/A')}v{war.get('teamSize', 'N/A')}")
    
    if state in ['inWar', 'warEnded', 'preparation']:
        if state != 'preparation':
            print(f"\n📊 CURRENT SCORE:")
            print(f"   Your Clan: {clan.get('stars', 0)} ⭐ ({clan.get('destructionPercentage', 0):.1f}%)")
            print(f"   Opponent:  {opponent.get('stars', 0)} ⭐ ({opponent.get('destructionPercentage', 0):.1f}%)")
            print(f"   Attacks Used: {clan.get('attacks', 0)}/{war.get('teamSize', 0) * 2}")
        
        # Return attack data for further analysis
        return analyze_war_attacks(war, "Current War")
    
    return None


def analyze_war_attacks(war: dict, war_label: str = "War") -> dict:
    """Analyze individual attacks in a war and return player stats."""
    clan_members = war.get('clan', {}).get('members', [])
    opponent_members = war.get('opponent', {}).get('members', [])
    
    if not clan_members:
        return {}
    
    # Build opponent lookup by tag
    opponent_lookup = {m.get('tag'): m for m in opponent_members}
    
    print(f"\n{'='*80}")
    print(f"   📊 DETAILED ATTACK ANALYSIS - {war_label}")
    print(f"{'='*80}")
    
    # Collect all attack data
    player_stats = {}
    all_attacks = []
    
    members_sorted = sorted(clan_members, key=lambda x: x.get('mapPosition', 0))
    
    print(f"\n{'#':<4} {'Attacker':<16} {'TH':<4} {'Target':<4} {'⭐':<3} {'%':<6} {'New⭐':<5} {'Hit':<8}")
    print(f"{'-'*60}")
    
    for member in members_sorted:
        name = member.get('name', 'Unknown')
        tag = member.get('tag', '')
        th = member.get('townhallLevel', 0)
        map_pos = member.get('mapPosition', 0)
        attacks = member.get('attacks', [])
        
        # Initialize player stats
        if tag not in player_stats:
            player_stats[tag] = {
                'name': name,
                'tag': tag,
                'th': th,
                'attacks': [],
                'total_stars': 0,
                'total_destruction': 0,
                'new_stars': 0,
                'attacks_used': 0,
                'missed_attacks': 0,
                'three_stars': 0,
                'two_stars': 0,
                'one_star': 0,
                'zero_stars': 0,
                'hit_up': 0,
                'hit_same': 0,
                'hit_down': 0,
            }
        
        if attacks:
            for attack in attacks:
                defender_tag = attack.get('defenderTag', '')
                defender = opponent_lookup.get(defender_tag, {})
                defender_th = defender.get('townhallLevel', 0)
                defender_pos = defender.get('mapPosition', 0)
                stars = attack.get('stars', 0)
                destruction = attack.get('destructionPercentage', 0)
                
                # Calculate new stars (stars that weren't already earned)
                # This info is in the attack data
                new_stars = stars  # API doesn't always provide this clearly
                
                # Determine hit direction
                if defender_th > th:
                    hit_type = "↑ UP"
                    player_stats[tag]['hit_up'] += 1
                elif defender_th < th:
                    hit_type = "↓ DOWN"
                    player_stats[tag]['hit_down'] += 1
                else:
                    hit_type = "= SAME"
                    player_stats[tag]['hit_same'] += 1
                
                # Update stats
                player_stats[tag]['attacks'].append({
                    'stars': stars,
                    'destruction': destruction,
                    'defender_th': defender_th,
                    'defender_pos': defender_pos,
                    'hit_type': hit_type
                })
                player_stats[tag]['total_stars'] += stars
                player_stats[tag]['total_destruction'] += destruction
                player_stats[tag]['attacks_used'] += 1
                
                if stars == 3:
                    player_stats[tag]['three_stars'] += 1
                elif stars == 2:
                    player_stats[tag]['two_stars'] += 1
                elif stars == 1:
                    player_stats[tag]['one_star'] += 1
                else:
                    player_stats[tag]['zero_stars'] += 1
                
                all_attacks.append({
                    'attacker': name,
                    'attacker_th': th,
                    'attacker_pos': map_pos,
                    'defender_pos': defender_pos,
                    'defender_th': defender_th,
                    'stars': stars,
                    'destruction': destruction,
                    'hit_type': hit_type
                })
                
                print(f"{map_pos:<4} {name[:15]:<16} TH{th:<2} → #{defender_pos:<3} {stars}⭐   {destruction:>5.1f}%  {hit_type}")
        else:
            # No attacks made
            player_stats[tag]['missed_attacks'] = 2
            print(f"{map_pos:<4} {name[:15]:<16} TH{th:<2}   ❌ NO ATTACKS USED")
    
    # Print summary statistics
    print(f"\n{'='*60}")
    print(f"   📈 ATTACK SUMMARY - {war_label}")
    print(f"{'='*60}")
    
    total_attacks = len(all_attacks)
    if total_attacks > 0:
        total_stars = sum(a['stars'] for a in all_attacks)
        total_destruction = sum(a['destruction'] for a in all_attacks)
        three_stars = sum(1 for a in all_attacks if a['stars'] == 3)
        two_stars = sum(1 for a in all_attacks if a['stars'] == 2)
        one_star = sum(1 for a in all_attacks if a['stars'] == 1)
        zero_stars = sum(1 for a in all_attacks if a['stars'] == 0)
        
        print(f"\n   Total Attacks: {total_attacks}")
        print(f"   Total Stars: {total_stars} ({total_stars/total_attacks:.2f} avg)")
        print(f"   Total Destruction: {total_destruction:.1f}% ({total_destruction/total_attacks:.1f}% avg)")
        print(f"\n   ⭐⭐⭐ Three Stars: {three_stars} ({three_stars/total_attacks*100:.1f}%)")
        print(f"   ⭐⭐  Two Stars:   {two_stars} ({two_stars/total_attacks*100:.1f}%)")
        print(f"   ⭐   One Star:    {one_star} ({one_star/total_attacks*100:.1f}%)")
        print(f"   ❌   Zero Stars:  {zero_stars} ({zero_stars/total_attacks*100:.1f}%)")
        
        # Hit direction analysis
        hits_up = sum(1 for a in all_attacks if 'UP' in a['hit_type'])
        hits_same = sum(1 for a in all_attacks if 'SAME' in a['hit_type'])
        hits_down = sum(1 for a in all_attacks if 'DOWN' in a['hit_type'])
        
        print(f"\n   📊 HIT DIRECTION:")
        print(f"   ↑ Hit Up (higher TH):   {hits_up} attacks")
        print(f"   = Hit Same (equal TH):  {hits_same} attacks")
        print(f"   ↓ Hit Down (lower TH):  {hits_down} attacks")
    
    # Players who missed attacks
    missed = [(p['name'], 2 - p['attacks_used']) for tag, p in player_stats.items() if p['attacks_used'] < 2]
    if missed:
        print(f"\n   ⚠️  MISSED ATTACKS:")
        for name, missed_count in missed:
            print(f"   • {name}: {missed_count} attack(s) not used")
    
    return player_stats


def analyze_cwl(clan_tag: str, historical_data: dict) -> dict:
    """Analyze Clan War League performance."""
    print_separator("CLAN WAR LEAGUE ANALYSIS")
    
    print("\n⏳ Fetching CWL group information...")
    cwl_group = get_cwl_group(clan_tag)
    
    if not cwl_group:
        print("\n⚠️  No active CWL found or CWL data not available.")
        print("   CWL data is only available during and shortly after CWL week.")
        return historical_data
    
    state = cwl_group.get('state', 'unknown')
    season = cwl_group.get('season', 'N/A')
    
    # Check if this season was already fully recorded
    season_key = f"cwl_{season}"
    if season_key in historical_data.get("cwl_seasons", {}) and historical_data["cwl_seasons"][season_key].get("complete", False):
        print(f"\n✅ CWL Season {season} already recorded in history.")
        # Still show the data but don't re-record
    
    print(f"\n🏆 CWL Season: {season}")
    print(f"📊 State: {state}")
    
    # Get all clans in the group
    clans = cwl_group.get('clans', [])
    print(f"\n👥 Clans in Group ({len(clans)}):")
    for clan in clans:
        print(f"   • {clan.get('name', 'Unknown')} ({clan.get('tag', 'N/A')})")
    
    # Get all rounds
    rounds = cwl_group.get('rounds', [])
    print(f"\n📅 Rounds: {len(rounds)}")
    
    # Aggregate player stats across all CWL wars
    all_player_stats = defaultdict(lambda: {
        'name': '',
        'tag': '',
        'th': 0,
        'total_stars': 0,
        'total_destruction': 0,
        'attacks_used': 0,
        'three_stars': 0,
        'two_stars': 0,
        'one_star': 0,
        'zero_stars': 0,
        'wars_participated': 0,
        'hit_up': 0,
        'hit_same': 0,
        'hit_down': 0,
    })
    
    wars_analyzed = 0
    our_clan_tag = clan_tag
    
    # Fetch and analyze each war
    for round_num, round_data in enumerate(rounds, 1):
        war_tags = round_data.get('warTags', [])
        
        for war_tag in war_tags:
            if war_tag == '#0':  # Placeholder for unscheduled wars
                continue
            
            print(f"\n⏳ Fetching CWL Round {round_num} war...", end='\r')
            war = get_cwl_war(war_tag)
            
            if not war:
                continue
            
            # Check if our clan is in this war
            clan_data = war.get('clan', {})
            opponent_data = war.get('opponent', {})
            
            our_clan = None
            opponent = None
            
            if clan_data.get('tag') == our_clan_tag:
                our_clan = clan_data
                opponent = opponent_data
            elif opponent_data.get('tag') == our_clan_tag:
                our_clan = opponent_data
                opponent = clan_data
            
            if not our_clan:
                continue
            
            wars_analyzed += 1
            state = war.get('state', 'unknown')
            
            print(f"\n{'='*70}")
            print(f"   🏆 CWL ROUND {round_num}: {our_clan.get('name')} vs {opponent.get('name')}")
            print(f"   State: {state}")
            print(f"{'='*70}")
            
            # Generate unique war ID for this CWL war
            war_id = f"cwl_{season}_round{round_num}_{war_tag}"
            
            if state in ['inWar', 'warEnded']:
                print(f"\n   Score: {our_clan.get('stars', 0)}⭐ vs {opponent.get('stars', 0)}⭐")
                print(f"   Destruction: {our_clan.get('destructionPercentage', 0):.1f}% vs {opponent.get('destructionPercentage', 0):.1f}%")
                
                # Analyze attacks
                war_stats = analyze_war_attacks(
                    {'clan': our_clan, 'opponent': opponent},
                    f"CWL Round {round_num}"
                )
                
                # Aggregate stats and save to historical data
                for tag, stats in war_stats.items():
                    all_player_stats[tag]['name'] = stats['name']
                    all_player_stats[tag]['tag'] = stats['tag']
                    all_player_stats[tag]['th'] = max(all_player_stats[tag]['th'], stats['th'])
                    all_player_stats[tag]['total_stars'] += stats['total_stars']
                    all_player_stats[tag]['total_destruction'] += stats['total_destruction']
                    all_player_stats[tag]['attacks_used'] += stats['attacks_used']
                    all_player_stats[tag]['three_stars'] += stats['three_stars']
                    all_player_stats[tag]['two_stars'] += stats['two_stars']
                    all_player_stats[tag]['one_star'] += stats['one_star']
                    all_player_stats[tag]['zero_stars'] += stats['zero_stars']
                    all_player_stats[tag]['hit_up'] += stats['hit_up']
                    all_player_stats[tag]['hit_same'] += stats['hit_same']
                    all_player_stats[tag]['hit_down'] += stats['hit_down']
                    if stats['attacks_used'] > 0:
                        all_player_stats[tag]['wars_participated'] += 1
                    
                    # Update historical data
                    update_player_historical_stats(
                        historical_data,
                        player_tag=tag,
                        player_name=stats['name'],
                        th_level=stats['th'],
                        attack_data=stats,
                        war_type=f"CWL_{season}",
                        war_id=war_id
                    )
            elif state == 'preparation':
                print(f"\n   ⏳ War is in preparation phase")
    
    # Store CWL season data
    if wars_analyzed > 0:
        historical_data["cwl_seasons"][season_key] = {
            "season": season,
            "wars_analyzed": wars_analyzed,
            "total_attacks": sum(p['attacks_used'] for p in all_player_stats.values()),
            "total_stars": sum(p['total_stars'] for p in all_player_stats.values()),
            "recorded_date": datetime.now().isoformat(),
            "complete": state == "ended"  # Mark as complete if CWL is over
        }
    
    # Print CWL overall summary
    if wars_analyzed > 0 and all_player_stats:
        print_separator("CWL OVERALL PLAYER PERFORMANCE")
        
        # Sort by total stars, then by destruction
        sorted_players = sorted(
            all_player_stats.values(),
            key=lambda x: (-x['total_stars'], -x['total_destruction'])
        )
        
        print(f"\n{'#':<3} {'Player':<18} {'TH':<4} {'Wars':<5} {'Atks':<5} {'⭐':<5} {'Avg⭐':<6} {'3⭐':<4} {'2⭐':<4} {'Avg%':<7}")
        print(f"{'-'*75}")
        
        for i, player in enumerate(sorted_players, 1):
            if player['attacks_used'] == 0:
                continue
            
            avg_stars = player['total_stars'] / player['attacks_used'] if player['attacks_used'] > 0 else 0
            avg_dest = player['total_destruction'] / player['attacks_used'] if player['attacks_used'] > 0 else 0
            
            print(f"{i:<3} {player['name'][:17]:<18} {player['th']:<4} {player['wars_participated']:<5} "
                  f"{player['attacks_used']:<5} {player['total_stars']:<5} {avg_stars:<6.2f} "
                  f"{player['three_stars']:<4} {player['two_stars']:<4} {avg_dest:<7.1f}")
        
        # Overall CWL stats
        total_attacks = sum(p['attacks_used'] for p in all_player_stats.values())
        total_stars = sum(p['total_stars'] for p in all_player_stats.values())
        total_three_stars = sum(p['three_stars'] for p in all_player_stats.values())
        
        print(f"\n📊 CWL TOTALS:")
        print(f"   Wars Analyzed: {wars_analyzed}")
        print(f"   Total Attacks: {total_attacks}")
        print(f"   Total Stars: {total_stars}")
        print(f"   Three Star Rate: {total_three_stars/total_attacks*100:.1f}%" if total_attacks > 0 else "   N/A")
        print(f"   Average Stars/Attack: {total_stars/total_attacks:.2f}" if total_attacks > 0 else "   N/A")
        
        # Top performers
        print(f"\n🏆 CWL TOP PERFORMERS:")
        
        # Most stars
        top_by_stars = sorted(all_player_stats.values(), key=lambda x: -x['total_stars'])[:5]
        print(f"\n   ⭐ Most Stars:")
        for i, p in enumerate(top_by_stars, 1):
            if p['total_stars'] > 0:
                print(f"   {i}. {p['name']}: {p['total_stars']}⭐ ({p['attacks_used']} attacks)")
        
        # Best average
        attackers = [p for p in all_player_stats.values() if p['attacks_used'] >= 2]
        if attackers:
            top_by_avg = sorted(attackers, key=lambda x: -x['total_stars']/x['attacks_used'])[:5]
            print(f"\n   📈 Best Average (min 2 attacks):")
            for i, p in enumerate(top_by_avg, 1):
                avg = p['total_stars'] / p['attacks_used']
                print(f"   {i}. {p['name']}: {avg:.2f}⭐/atk ({p['attacks_used']} attacks)")
        
        # Most three stars
        top_by_3star = sorted(all_player_stats.values(), key=lambda x: -x['three_stars'])[:5]
        print(f"\n   ⭐⭐⭐ Most Three Stars:")
        for i, p in enumerate(top_by_3star, 1):
            if p['three_stars'] > 0:
                print(f"   {i}. {p['name']}: {p['three_stars']} three-stars")
    
    return historical_data


def print_historical_summary(historical_data: dict):
    """Print a summary of all historical data collected."""
    print_separator("📚 HISTORICAL DATA SUMMARY")
    
    players = historical_data.get("players", {})
    cwl_seasons = historical_data.get("cwl_seasons", {})
    wars = historical_data.get("wars", {})
    
    print(f"\n📊 DATA OVERVIEW:")
    print(f"   Players tracked: {len(players)}")
    print(f"   CWL Seasons recorded: {len(cwl_seasons)}")
    print(f"   Wars recorded: {len(wars)}")
    print(f"   Last updated: {historical_data.get('last_updated', 'Never')}")
    
    if not players:
        print("\n   ℹ️  No historical attack data yet. Run during/after wars to collect data!")
        return
    
    # Calculate all-time stats
    total_attacks = sum(p.get('total_attacks', 0) for p in players.values())
    total_stars = sum(p.get('total_stars', 0) for p in players.values())
    total_three_stars = sum(p.get('three_stars', 0) for p in players.values())
    
    print(f"\n📈 ALL-TIME STATISTICS:")
    print(f"   Total Attacks Recorded: {total_attacks:,}")
    print(f"   Total Stars Earned: {total_stars:,}")
    print(f"   Total Three-Stars: {total_three_stars:,}")
    if total_attacks > 0:
        print(f"   All-Time Average: {total_stars/total_attacks:.2f}⭐/attack")
        print(f"   All-Time 3-Star Rate: {total_three_stars/total_attacks*100:.1f}%")
    
    # All-time leaderboard
    print(f"\n🏆 ALL-TIME LEADERBOARD (min 5 attacks):")
    
    # Filter players with enough attacks
    qualified_players = [p for p in players.values() if p.get('total_attacks', 0) >= 5]
    
    if qualified_players:
        # Sort by average stars
        sorted_by_avg = sorted(
            qualified_players,
            key=lambda x: (-x['total_stars'] / x['total_attacks'] if x['total_attacks'] > 0 else 0, -x['total_attacks'])
        )
        
        print(f"\n   📈 By Average Stars (min 5 attacks):")
        print(f"   {'#':<3} {'Player':<18} {'TH':<4} {'Attacks':<8} {'Stars':<7} {'Avg':<6} {'3⭐%':<7}")
        print(f"   {'-'*60}")
        
        for i, p in enumerate(sorted_by_avg[:15], 1):
            avg = p['total_stars'] / p['total_attacks'] if p['total_attacks'] > 0 else 0
            three_pct = p['three_stars'] / p['total_attacks'] * 100 if p['total_attacks'] > 0 else 0
            print(f"   {i:<3} {p['name'][:17]:<18} {p.get('current_th', '?'):<4} "
                  f"{p['total_attacks']:<8} {p['total_stars']:<7} {avg:<6.2f} {three_pct:<7.1f}")
    
    # Most attacks all-time
    sorted_by_attacks = sorted(players.values(), key=lambda x: -x.get('total_attacks', 0))
    
    print(f"\n   🎯 Most Attacks All-Time:")
    for i, p in enumerate(sorted_by_attacks[:10], 1):
        if p.get('total_attacks', 0) > 0:
            print(f"   {i}. {p['name']}: {p['total_attacks']} attacks, {p['total_stars']}⭐")
    
    # Most three-stars all-time
    sorted_by_3star = sorted(players.values(), key=lambda x: -x.get('three_stars', 0))
    
    print(f"\n   ⭐⭐⭐ Most Three-Stars All-Time:")
    for i, p in enumerate(sorted_by_3star[:10], 1):
        if p.get('three_stars', 0) > 0:
            print(f"   {i}. {p['name']}: {p['three_stars']} three-stars")
    
    # CWL history
    if cwl_seasons:
        print(f"\n📅 CWL SEASON HISTORY:")
        for season_id, data in sorted(cwl_seasons.items(), reverse=True):
            print(f"   • {data.get('season', season_id)}: {data.get('total_stars', 0)}⭐ "
                  f"({data.get('total_attacks', 0)} attacks) - "
                  f"{'Complete' if data.get('complete') else 'In Progress'}")


def generate_html_dashboard(clan: dict, players_data: list, rush_reports: list, historical_data: dict):
    """Generate a beautiful HTML dashboard for the clan analysis."""
    
    # Prepare data
    clan_name = clan.get('name', 'Unknown Clan')
    clan_tag = clan.get('tag', '')
    clan_level = clan.get('clanLevel', 0)
    members_count = clan.get('members', 0)
    war_wins = clan.get('warWins', 0)
    war_losses = clan.get('warLosses', 0)
    war_ties = clan.get('warTies', 0)
    total_wars = war_wins + war_losses + war_ties
    win_rate = (war_wins / total_wars * 100) if total_wars > 0 else 0
    
    # TH distribution
    th_dist = defaultdict(int)
    for p in players_data:
        th_dist[p.get('townHallLevel', 0)] += 1
    
    # Rush stats
    rushed_count = sum(1 for r in rush_reports if r.get('is_rushed', False))
    avg_rush_score = sum(r.get('rush_score', 0) for r in rush_reports) / len(rush_reports) if rush_reports else 0
    
    # Historical stats
    hist_players = historical_data.get('players', {})
    total_hist_attacks = sum(p.get('total_attacks', 0) for p in hist_players.values())
    total_hist_stars = sum(p.get('total_stars', 0) for p in hist_players.values())
    avg_stars = total_hist_stars / total_hist_attacks if total_hist_attacks > 0 else 0
    
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{clan_name} - Clan Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: #ffffff;
            min-height: 100vh;
            padding: 20px;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        .header {{
            text-align: center;
            padding: 30px;
            background: linear-gradient(135deg, #0f3460 0%, #16213e 100%);
            border-radius: 15px;
            margin-bottom: 20px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        }}
        .header h1 {{
            font-size: 2.5em;
            color: #e94560;
            margin-bottom: 10px;
        }}
        .header .clan-tag {{
            color: #888;
            font-size: 1.1em;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .stat-card {{
            background: linear-gradient(135deg, #1f4068 0%, #162447 100%);
            padding: 25px;
            border-radius: 12px;
            text-align: center;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            transition: transform 0.3s ease;
        }}
        .stat-card:hover {{
            transform: translateY(-5px);
        }}
        .stat-card .value {{
            font-size: 2.5em;
            font-weight: bold;
            color: #e94560;
        }}
        .stat-card .label {{
            color: #aaa;
            margin-top: 5px;
            font-size: 0.9em;
        }}
        .section {{
            background: rgba(255,255,255,0.05);
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 20px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        }}
        .section h2 {{
            color: #e94560;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #e94560;
        }}
        .charts-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 20px;
        }}
        .chart-container {{
            background: rgba(0,0,0,0.2);
            border-radius: 10px;
            padding: 20px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }}
        th {{
            background: rgba(233, 69, 96, 0.2);
            color: #e94560;
            font-weight: 600;
        }}
        tr:hover {{
            background: rgba(255,255,255,0.05);
        }}
        .rush-status {{
            padding: 5px 10px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: 500;
        }}
        .rush-maxed {{ background: #27ae60; }}
        .rush-slight {{ background: #2ecc71; }}
        .rush-moderate {{ background: #f39c12; }}
        .rush-rushed {{ background: #e67e22; }}
        .rush-severe {{ background: #e74c3c; }}
        .progress-bar {{
            width: 100%;
            height: 20px;
            background: rgba(255,255,255,0.1);
            border-radius: 10px;
            overflow: hidden;
        }}
        .progress-fill {{
            height: 100%;
            border-radius: 10px;
            transition: width 0.5s ease;
        }}
        .footer {{
            text-align: center;
            padding: 20px;
            color: #666;
            margin-top: 30px;
        }}
        .tab-container {{
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
        }}
        .tab {{
            padding: 10px 20px;
            background: rgba(255,255,255,0.1);
            border: none;
            color: #fff;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.3s ease;
        }}
        .tab:hover, .tab.active {{
            background: #e94560;
        }}
        .tab-content {{
            display: none;
        }}
        .tab-content.active {{
            display: block;
        }}
        .hero-bar {{
            display: flex;
            align-items: center;
            margin: 5px 0;
        }}
        .hero-name {{
            width: 100px;
            font-size: 0.85em;
        }}
        .hero-progress {{
            flex: 1;
            height: 15px;
            background: rgba(255,255,255,0.1);
            border-radius: 8px;
            overflow: hidden;
            margin: 0 10px;
        }}
        .hero-fill {{
            height: 100%;
            background: linear-gradient(90deg, #e94560, #f39c12);
            border-radius: 8px;
        }}
        .hero-level {{
            font-size: 0.85em;
            color: #aaa;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏰 {clan_name}</h1>
            <p class="clan-tag">{clan_tag} • Level {clan_level}</p>
            <p style="margin-top: 10px; color: #aaa;">Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="value">{members_count}</div>
                <div class="label">👥 Members</div>
            </div>
            <div class="stat-card">
                <div class="value">{win_rate:.1f}%</div>
                <div class="label">⚔️ War Win Rate</div>
            </div>
            <div class="stat-card">
                <div class="value">{war_wins}</div>
                <div class="label">✅ War Wins</div>
            </div>
            <div class="stat-card">
                <div class="value">{avg_stars:.2f}</div>
                <div class="label">⭐ Avg Stars/Attack</div>
            </div>
            <div class="stat-card">
                <div class="value">{total_hist_attacks}</div>
                <div class="label">🎯 Attacks Tracked</div>
            </div>
            <div class="stat-card">
                <div class="value">{rushed_count}</div>
                <div class="label">⚠️ Rushed Players</div>
            </div>
        </div>
        
        <div class="section">
            <h2>📊 Clan Composition</h2>
            <div class="charts-grid">
                <div class="chart-container">
                    <canvas id="thChart"></canvas>
                </div>
                <div class="chart-container">
                    <canvas id="rushChart"></canvas>
                </div>
            </div>
        </div>
        
        <div class="section">
            <h2>👥 Member Rush Analysis</h2>
            <div class="tab-container">
                <button class="tab active" onclick="showTab('all')">All Members</button>
                <button class="tab" onclick="showTab('rushed')">Rushed Only</button>
                <button class="tab" onclick="showTab('maxed')">Not Rushed</button>
            </div>
            <div id="tab-all" class="tab-content active">
                <table>
                    <thead>
                        <tr>
                            <th>#</th>
                            <th>Player</th>
                            <th>TH</th>
                            <th>Rush Score</th>
                            <th>Hero Deficit</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody>
'''
    
    # Add rows for all players
    for i, report in enumerate(rush_reports, 1):
        status = report.get('status', 'Unknown')
        status_class = 'rush-maxed'
        if 'Slightly' in status:
            status_class = 'rush-slight'
        elif 'Moderately' in status:
            status_class = 'rush-moderate'
        elif 'Rushed' in status and 'Severely' not in status:
            status_class = 'rush-rushed'
        elif 'Severely' in status:
            status_class = 'rush-severe'
        
        # Clean status for display
        display_status = status.replace('✅ ', '').replace('🟢 ', '').replace('🟡 ', '').replace('🟠 ', '').replace('🔴 ', '')
        
        html += f'''
                        <tr data-rushed="{str(report.get('is_rushed', False)).lower()}">
                            <td>{i}</td>
                            <td>{report.get('player_name', 'Unknown')}</td>
                            <td>{report.get('th_level', '?')}</td>
                            <td>{report.get('rush_score', 0):.1f}</td>
                            <td>-{report.get('total_missing_hero_levels', 0)}</td>
                            <td><span class="rush-status {status_class}">{display_status}</span></td>
                        </tr>'''
    
    html += '''
                    </tbody>
                </table>
            </div>
            <div id="tab-rushed" class="tab-content">
                <table>
                    <thead>
                        <tr>
                            <th>#</th>
                            <th>Player</th>
                            <th>TH</th>
                            <th>Rush Score</th>
                            <th>Hero Deficit</th>
                            <th>Rushed Heroes</th>
                        </tr>
                    </thead>
                    <tbody>
'''
    
    # Add rows for rushed players only
    rushed_only = [r for r in rush_reports if r.get('is_rushed', False)]
    for i, report in enumerate(rushed_only, 1):
        heroes_str = ', '.join([f"{h['name'][:2]}:{h['current']}/{h['target']}" for h in report.get('rushed_heroes', [])[:4]])
        html += f'''
                        <tr>
                            <td>{i}</td>
                            <td>{report.get('player_name', 'Unknown')}</td>
                            <td>{report.get('th_level', '?')}</td>
                            <td>{report.get('rush_score', 0):.1f}</td>
                            <td>-{report.get('total_missing_hero_levels', 0)}</td>
                            <td style="font-size: 0.85em;">{heroes_str}</td>
                        </tr>'''
    
    html += '''
                    </tbody>
                </table>
            </div>
            <div id="tab-maxed" class="tab-content">
                <table>
                    <thead>
                        <tr>
                            <th>#</th>
                            <th>Player</th>
                            <th>TH</th>
                            <th>Rush Score</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody>
'''
    
    # Add rows for non-rushed players
    not_rushed = [r for r in rush_reports if not r.get('is_rushed', False)]
    for i, report in enumerate(not_rushed, 1):
        html += f'''
                        <tr>
                            <td>{i}</td>
                            <td>{report.get('player_name', 'Unknown')}</td>
                            <td>{report.get('th_level', '?')}</td>
                            <td>{report.get('rush_score', 0):.1f}</td>
                            <td><span class="rush-status rush-maxed">Not Rushed</span></td>
                        </tr>'''
    
    html += '''
                    </tbody>
                </table>
            </div>
        </div>
        
        <div class="section">
            <h2>🏆 Historical War Performance</h2>
            <table>
                <thead>
                    <tr>
                        <th>#</th>
                        <th>Player</th>
                        <th>TH</th>
                        <th>Attacks</th>
                        <th>Stars</th>
                        <th>Avg ⭐</th>
                        <th>3-Star %</th>
                    </tr>
                </thead>
                <tbody>
'''
    
    # Historical performance table
    hist_sorted = sorted(hist_players.values(), key=lambda x: (-x.get('total_stars', 0) / x.get('total_attacks', 1) if x.get('total_attacks', 0) > 0 else 0, -x.get('total_attacks', 0)))
    
    for i, p in enumerate(hist_sorted[:30], 1):
        attacks = p.get('total_attacks', 0)
        stars = p.get('total_stars', 0)
        avg = stars / attacks if attacks > 0 else 0
        three_pct = p.get('three_stars', 0) / attacks * 100 if attacks > 0 else 0
        
        html += f'''
                    <tr>
                        <td>{i}</td>
                        <td>{p.get('name', 'Unknown')}</td>
                        <td>{p.get('current_th', '?')}</td>
                        <td>{attacks}</td>
                        <td>{stars}</td>
                        <td>{avg:.2f}</td>
                        <td>{three_pct:.1f}%</td>
                    </tr>'''
    
    # Prepare chart data
    th_labels = [f"TH{th}" for th in sorted(th_dist.keys(), reverse=True)]
    th_values = [th_dist[th] for th in sorted(th_dist.keys(), reverse=True)]
    
    rush_status_counts = defaultdict(int)
    for r in rush_reports:
        status = r.get('status', 'Unknown')
        if 'Maxed' in status:
            rush_status_counts['Maxed'] += 1
        elif 'Slightly' in status:
            rush_status_counts['Slightly Behind'] += 1
        elif 'Moderately' in status:
            rush_status_counts['Moderately Rushed'] += 1
        elif 'Severely' in status:
            rush_status_counts['Severely Rushed'] += 1
        elif 'Rushed' in status:
            rush_status_counts['Rushed'] += 1
        else:
            rush_status_counts['Other'] += 1
    
    html += f'''
                </tbody>
            </table>
        </div>
        
        <div class="footer">
            <p>Generated by Clash of Clans Clan Analyzer | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
    </div>
    
    <script>
        // TH Distribution Chart
        new Chart(document.getElementById('thChart'), {{
            type: 'bar',
            data: {{
                labels: {th_labels},
                datasets: [{{
                    label: 'Players',
                    data: {th_values},
                    backgroundColor: [
                        '#e94560', '#f39c12', '#3498db', '#2ecc71', '#9b59b6',
                        '#1abc9c', '#e74c3c', '#34495e', '#f1c40f', '#95a5a6'
                    ]
                }}]
            }},
            options: {{
                responsive: true,
                plugins: {{
                    title: {{
                        display: true,
                        text: 'Town Hall Distribution',
                        color: '#fff'
                    }},
                    legend: {{
                        display: false
                    }}
                }},
                scales: {{
                    y: {{
                        beginAtZero: true,
                        ticks: {{ color: '#aaa' }},
                        grid: {{ color: 'rgba(255,255,255,0.1)' }}
                    }},
                    x: {{
                        ticks: {{ color: '#aaa' }},
                        grid: {{ color: 'rgba(255,255,255,0.1)' }}
                    }}
                }}
            }}
        }});
        
        // Rush Status Chart
        new Chart(document.getElementById('rushChart'), {{
            type: 'doughnut',
            data: {{
                labels: {list(rush_status_counts.keys())},
                datasets: [{{
                    data: {list(rush_status_counts.values())},
                    backgroundColor: ['#27ae60', '#2ecc71', '#f39c12', '#e74c3c', '#e67e22', '#95a5a6']
                }}]
            }},
            options: {{
                responsive: true,
                plugins: {{
                    title: {{
                        display: true,
                        text: 'Rush Status Distribution',
                        color: '#fff'
                    }},
                    legend: {{
                        position: 'bottom',
                        labels: {{ color: '#aaa' }}
                    }}
                }}
            }}
        }});
        
        // Tab functionality
        function showTab(tabName) {{
            document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
            document.querySelectorAll('.tab').forEach(el => el.classList.remove('active'));
            document.getElementById('tab-' + tabName).classList.add('active');
            event.target.classList.add('active');
        }}
    </script>
</body>
</html>
'''
    
    # Save HTML file
    with open(HTML_REPORT_FILE, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"   ✅ Dashboard saved to: {HTML_REPORT_FILE}")


def create_member_report(players_data: list):
    """Create a detailed member report."""
    print_separator("COMPLETE MEMBER ROSTER")
    
    print(f"\n{'#':<3} {'Name':<18} {'TH':<4} {'Level':<6} {'Trophies':<9} {'War Stars':<10} {'Donations':<10}")
    print(f"{'-'*70}")
    
    # Sort by Town Hall level, then by trophies
    players_sorted = sorted(players_data, key=lambda x: (-x.get('townHallLevel', 0), -x.get('trophies', 0)))
    
    for i, player in enumerate(players_sorted, 1):
        name = player.get('name', 'Unknown')[:17]
        th = player.get('townHallLevel', '?')
        level = player.get('expLevel', 0)
        trophies = player.get('trophies', 0)
        war_stars = player.get('warStars', 0)
        donations = player.get('donations', 0)
        
        print(f"{i:<3} {name:<18} {th:<4} {level:<6} {trophies:<9,} {war_stars:<10,} {donations:<10,}")


def clan_strength_analysis(players_data: list):
    """Analyze overall clan strength."""
    print_separator("CLAN STRENGTH ANALYSIS")
    
    # Calculate weighted strength score
    print(f"\n💪 CLAN POWER METRICS:")
    
    # TH power (weighted)
    th_weights = {17: 100, 16: 90, 15: 80, 14: 70, 13: 60, 12: 50, 11: 40, 10: 30, 9: 20, 8: 10}
    th_power = sum(th_weights.get(p.get('townHallLevel', 1), 5) for p in players_data)
    print(f"   Town Hall Power Score: {th_power}")
    
    # Hero power
    total_hero_levels = 0
    for player in players_data:
        heroes = player.get('heroes', [])
        home_heroes = [h for h in heroes if h.get('village', '') == 'home']
        total_hero_levels += sum(h.get('level', 0) for h in home_heroes)
    print(f"   Total Hero Levels: {total_hero_levels}")
    
    # War experience
    total_war_stars = sum(p.get('warStars', 0) for p in players_data)
    print(f"   Total War Stars: {total_war_stars:,}")
    
    # Overall strength estimate
    strength_score = th_power + (total_hero_levels * 2) + (total_war_stars // 100)
    print(f"\n   🏆 OVERALL STRENGTH SCORE: {strength_score:,}")
    
    # Recommendations
    print(f"\n📝 RECOMMENDATIONS:")
    
    th_counts = defaultdict(int)
    for p in players_data:
        th_counts[p.get('townHallLevel', 0)] += 1
    
    low_th_count = sum(count for th, count in th_counts.items() if th < 12)
    high_th_count = sum(count for th, count in th_counts.items() if th >= 14)
    
    if low_th_count > len(players_data) * 0.3:
        print(f"   ⚠️  {low_th_count} members are below TH12. Consider recruiting higher TH players for CWL.")
    
    if high_th_count > len(players_data) * 0.5:
        print(f"   ✅ Strong high-level presence with {high_th_count} TH14+ members!")
    
    # Check for inactive players (low donations might indicate inactivity)
    low_activity = [p.get('name') for p in players_data if p.get('donations', 0) == 0 and p.get('donationsReceived', 0) == 0]
    if low_activity:
        print(f"   ⚠️  {len(low_activity)} members have 0 donations this season (possible inactives)")


def export_dashboard_data(clan: dict, players_data: list, rush_reports: list, 
                          historical_data: dict, warlog: list, current_war: dict,
                          capital_raids: list, gold_pass: dict, cwl_group: dict):
    """Export comprehensive data to JSON for the Next.js dashboard."""
    print("\n⏳ Exporting data for Next.js dashboard...")
    
    # Build comprehensive player data with rush info
    players_export = []
    for player in players_data:
        # Find matching rush report
        rush_report = next((r for r in rush_reports if r.get('player_tag') == player.get('tag')), {})
        
        # Get historical stats for this player
        hist_player = historical_data.get('players', {}).get(player.get('tag'), {})
        
        # Extract hero data with correct max levels for player's TH
        th_level = player.get('townHallLevel', 1)
        heroes = []
        for hero in player.get('heroes', []):
            if hero.get('village') == 'home':
                hero_name = hero.get('name')
                # Get max level for this hero at player's current TH from our defined data
                max_at_th = get_max_level_for_th(hero_name, th_level, "hero")
                heroes.append({
                    'name': hero_name,
                    'level': hero.get('level'),
                    'maxLevel': max_at_th if max_at_th else hero.get('maxLevel'),
                })
        
        # Extract key troops with correct max levels for player's TH
        troops = []
        for troop in player.get('troops', []):
            if troop.get('village') == 'home':
                troop_name = troop.get('name')
                # Get max level for this troop at player's current TH from our defined data
                max_at_th = get_max_level_for_th(troop_name, th_level, "troop")
                troops.append({
                    'name': troop_name,
                    'level': troop.get('level'),
                    # Use our defined max if available, otherwise fall back to API value
                    'maxLevel': max_at_th if max_at_th else troop.get('maxLevel'),
                })
        
        # Extract spells with correct max levels for player's TH
        spells = []
        for spell in player.get('spells', []):
            if spell.get('village') == 'home':
                spell_name = spell.get('name')
                # Get max level for this spell at player's current TH from our defined data
                max_at_th = get_max_level_for_th(spell_name, th_level, "spell")
                spells.append({
                    'name': spell_name,
                    'level': spell.get('level'),
                    # Use our defined max if available, otherwise fall back to API value
                    'maxLevel': max_at_th if max_at_th else spell.get('maxLevel'),
                })
        
        # Extract hero equipment
        hero_equipment = []
        for equip in player.get('heroEquipment', []):
            hero_equipment.append({
                'name': equip.get('name'),
                'level': equip.get('level'),
                'maxLevel': equip.get('maxLevel'),
                'village': equip.get('village'),
            })
        
        player_export = {
            'tag': player.get('tag'),
            'name': player.get('name'),
            'townHallLevel': player.get('townHallLevel'),
            'townHallWeaponLevel': player.get('townHallWeaponLevel'),
            'expLevel': player.get('expLevel'),
            'trophies': player.get('trophies'),
            'bestTrophies': player.get('bestTrophies'),
            'warStars': player.get('warStars'),
            'attackWins': player.get('attackWins'),
            'defenseWins': player.get('defenseWins'),
            'builderHallLevel': player.get('builderHallLevel'),
            'builderBaseTrophies': player.get('builderBaseTrophies'),
            'bestBuilderBaseTrophies': player.get('bestBuilderBaseTrophies'),
            'role': player.get('role'),
            'warPreference': player.get('warPreference'),
            'donations': player.get('donations'),
            'donationsReceived': player.get('donationsReceived'),
            'clanCapitalContributions': player.get('clanCapitalContributions'),
            'clan': player.get('clan'),
            'league': player.get('league'),
            'builderBaseLeague': player.get('builderBaseLeague'),
            'achievements': player.get('achievements', []),
            'labels': player.get('labels', []),
            'heroes': heroes,
            'troops': troops,
            'spells': spells,
            'heroEquipment': hero_equipment,
            # Rush analysis
            'rushAnalysis': {
                'isRushed': rush_report.get('is_rushed', False),
                'rushScore': rush_report.get('rush_score', 0),
                'rushPercentage': rush_report.get('rush_percentage', 0),
                'status': rush_report.get('status', 'Unknown'),
                'heroScore': rush_report.get('hero_score', 0),
                'troopScore': rush_report.get('troop_score', 0),
                'spellScore': rush_report.get('spell_score', 0),
                'totalMissingHeroLevels': rush_report.get('total_missing_hero_levels', 0),
                'rushedHeroes': rush_report.get('rushed_heroes', []),
                'rushedTroops': rush_report.get('rushed_troops', []),
                'rushedSpells': rush_report.get('rushed_spells', []),
            },
            # Historical war stats
            'warStats': {
                'totalAttacks': hist_player.get('total_attacks', 0),
                'totalStars': hist_player.get('total_stars', 0),
                'totalDestruction': hist_player.get('total_destruction', 0),
                'threeStars': hist_player.get('three_stars', 0),
                'twoStars': hist_player.get('two_stars', 0),
                'oneStars': hist_player.get('one_star', 0),
                'zeroStars': hist_player.get('zero_stars', 0),
                'warsParticipated': hist_player.get('wars_participated', 0),
            }
        }
        players_export.append(player_export)
    
    # Process war log
    warlog_export = []
    if warlog:
        for war in warlog[:50]:  # Last 50 wars
            warlog_export.append({
                'result': war.get('result'),
                'endTime': war.get('endTime'),
                'teamSize': war.get('teamSize'),
                'attacksPerMember': war.get('attacksPerMember'),
                'clan': {
                    'tag': war.get('clan', {}).get('tag'),
                    'name': war.get('clan', {}).get('name'),
                    'stars': war.get('clan', {}).get('stars'),
                    'destructionPercentage': war.get('clan', {}).get('destructionPercentage'),
                    'expEarned': war.get('clan', {}).get('expEarned'),
                },
                'opponent': {
                    'tag': war.get('opponent', {}).get('tag'),
                    'name': war.get('opponent', {}).get('name'),
                    'stars': war.get('opponent', {}).get('stars'),
                    'destructionPercentage': war.get('opponent', {}).get('destructionPercentage'),
                }
            })
    
    # Process current war
    current_war_export = None
    if current_war and current_war.get('state') not in ['notInWar', None]:
        current_war_export = {
            'state': current_war.get('state'),
            'teamSize': current_war.get('teamSize'),
            'attacksPerMember': current_war.get('attacksPerMember'),
            'preparationStartTime': current_war.get('preparationStartTime'),
            'startTime': current_war.get('startTime'),
            'endTime': current_war.get('endTime'),
            'clan': current_war.get('clan'),
            'opponent': current_war.get('opponent'),
        }
    
    # Process capital raids
    capital_raids_export = []
    if capital_raids:
        for raid in capital_raids[:10]:
            capital_raids_export.append({
                'state': raid.get('state'),
                'startTime': raid.get('startTime'),
                'endTime': raid.get('endTime'),
                'capitalTotalLoot': raid.get('capitalTotalLoot'),
                'raidsCompleted': raid.get('raidsCompleted'),
                'totalAttacks': raid.get('totalAttacks'),
                'enemyDistrictsDestroyed': raid.get('enemyDistrictsDestroyed'),
                'offensiveReward': raid.get('offensiveReward'),
                'defensiveReward': raid.get('defensiveReward'),
                'members': raid.get('members', []),
                'attackLog': raid.get('attackLog', []),
                'defenseLog': raid.get('defenseLog', []),
            })
    
    # Calculate clan statistics
    th_distribution = defaultdict(int)
    role_distribution = defaultdict(int)
    league_distribution = defaultdict(int)
    rush_distribution = defaultdict(int)
    
    for player in players_data:
        th_distribution[player.get('townHallLevel', 0)] += 1
        role_distribution[player.get('role', 'unknown')] += 1
        league_name = player.get('league', {}).get('name', 'Unranked') if player.get('league') else 'Unranked'
        league_distribution[league_name] += 1
    
    for report in rush_reports:
        status = report.get('status', 'Unknown')
        if 'Maxed' in status:
            rush_distribution['Maxed'] += 1
        elif 'Slightly' in status:
            rush_distribution['Slightly Behind'] += 1
        elif 'Moderately' in status:
            rush_distribution['Moderately Rushed'] += 1
        elif 'Severely' in status:
            rush_distribution['Severely Rushed'] += 1
        elif 'Rushed' in status:
            rush_distribution['Rushed'] += 1
        else:
            rush_distribution['Other'] += 1
    
    # Build final export object
    dashboard_data = {
        'lastUpdated': datetime.now().isoformat(),
        'clan': {
            'tag': clan.get('tag'),
            'name': clan.get('name'),
            'description': clan.get('description'),
            'type': clan.get('type'),
            'location': clan.get('location'),
            'chatLanguage': clan.get('chatLanguage'),
            'clanLevel': clan.get('clanLevel'),
            'clanPoints': clan.get('clanPoints'),
            'clanBuilderBasePoints': clan.get('clanBuilderBasePoints'),
            'clanCapitalPoints': clan.get('clanCapitalPoints'),
            'capitalLeague': clan.get('capitalLeague'),
            'requiredTrophies': clan.get('requiredTrophies'),
            'warFrequency': clan.get('warFrequency'),
            'warWinStreak': clan.get('warWinStreak'),
            'warWins': clan.get('warWins'),
            'warTies': clan.get('warTies'),
            'warLosses': clan.get('warLosses'),
            'isWarLogPublic': clan.get('isWarLogPublic'),
            'warLeague': clan.get('warLeague'),
            'members': clan.get('members'),
            'labels': clan.get('labels', []),
            'clanCapital': clan.get('clanCapital'),
            'badgeUrls': clan.get('badgeUrls'),
        },
        'players': players_export,
        'warLog': warlog_export,
        'currentWar': current_war_export,
        'capitalRaids': capital_raids_export,
        'goldPass': gold_pass,
        'cwlGroup': cwl_group,
        'historicalData': {
            'cwlSeasons': historical_data.get('cwl_seasons', {}),
            'lastUpdated': historical_data.get('last_updated'),
        },
        'statistics': {
            'thDistribution': dict(th_distribution),
            'roleDistribution': dict(role_distribution),
            'leagueDistribution': dict(league_distribution),
            'rushDistribution': dict(rush_distribution),
            'totalWarStars': sum(p.get('warStars', 0) for p in players_data),
            'totalDonations': sum(p.get('donations', 0) for p in players_data),
            'totalCapitalContributions': sum(p.get('clanCapitalContributions', 0) for p in players_data),
            'averageTrophies': sum(p.get('trophies', 0) for p in players_data) / len(players_data) if players_data else 0,
            'rushedCount': sum(1 for r in rush_reports if r.get('is_rushed', False)),
            'averageRushScore': sum(r.get('rush_score', 0) for r in rush_reports) / len(rush_reports) if rush_reports else 0,
        }
    }
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(DASHBOARD_DATA_FILE), exist_ok=True)
    
    # Save to JSON file
    with open(DASHBOARD_DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(dashboard_data, f, indent=2, ensure_ascii=False)
    
    print(f"   ✅ Dashboard data exported to: {DASHBOARD_DATA_FILE}")
    return dashboard_data


def main():
    """Main function to run all analyses."""
    print("\n" + "="*80)
    print("   🎮 CLASH OF CLANS - COMPREHENSIVE CLAN ANALYSIS 🎮")
    print("="*80)
    print(f"\n📅 Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🏷️  Clan Tag: {CLAN_TAG}")
    
    # Load historical data
    print("\n💾 Loading historical data...")
    historical_data = load_historical_data()
    
    # Get clan info
    print("\n⏳ Fetching clan information...")
    clan = get_clan_info(CLAN_TAG)
    if not clan:
        print("❌ Failed to fetch clan information. Check your API token and clan tag.")
        return
    
    analyze_clan_info(clan)
    
    # Get clan members
    print("\n⏳ Fetching clan members...")
    members = get_clan_members(CLAN_TAG)
    if not members:
        print("❌ Failed to fetch clan members.")
        return
    
    # Get detailed player info for each member
    print(f"\n⏳ Fetching detailed info for {len(members)} players...")
    players_data = []
    for i, member in enumerate(members, 1):
        player_tag = member.get('tag')
        print(f"   Fetching player {i}/{len(members)}: {member.get('name')}", end='\r')
        player = get_player_info(player_tag)
        if player:
            players_data.append(player)
        time.sleep(0.05)  # Small delay to avoid rate limiting
    print(" " * 60)  # Clear the line
    
    if not players_data:
        print("❌ Failed to fetch player details.")
        return
    
    # Run all analyses
    analyze_members(members, players_data)
    analyze_player_details(players_data)
    create_member_report(players_data)
    clan_strength_analysis(players_data)
    
    # Rush Analysis
    rush_reports = analyze_clan_rush(players_data)
    
    # Get war log
    print("\n⏳ Fetching war log...")
    warlog = get_clan_warlog(CLAN_TAG)
    analyze_warlog(warlog)
    
    # Get current war and save attack data
    print("\n⏳ Checking current war status...")
    current_war = get_current_war(CLAN_TAG)
    if current_war and current_war.get('state') not in ['notInWar', None]:
        war_stats = analyze_current_war(current_war)
        if war_stats:
            war_id = generate_war_id(current_war)
            for tag, stats in war_stats.items():
                update_player_historical_stats(
                    historical_data,
                    player_tag=tag,
                    player_name=stats['name'],
                    th_level=stats['th'],
                    attack_data=stats,
                    war_type="regular_war",
                    war_id=war_id
                )
    else:
        print_separator("CURRENT WAR")
        print("\n⚠️  Clan is not currently in a war.")
    
    # Analyze CWL
    print("\n⏳ Checking for Clan War League data...")
    cwl_group = get_cwl_group(CLAN_TAG)
    historical_data = analyze_cwl(CLAN_TAG, historical_data)
    
    # Fetch additional data for dashboard
    print("\n⏳ Fetching capital raid seasons...")
    capital_raids = get_capital_raid_seasons(CLAN_TAG)
    
    print("\n⏳ Fetching gold pass information...")
    gold_pass = get_gold_pass_season()
    
    # Print historical summary
    print_historical_summary(historical_data)
    
    # Update timestamp and save
    historical_data["last_updated"] = datetime.now().isoformat()
    save_historical_data(historical_data)
    
    # Generate HTML Dashboard
    print("\n⏳ Generating HTML Dashboard...")
    generate_html_dashboard(clan, players_data, rush_reports, historical_data)
    
    # Export comprehensive data for Next.js dashboard
    export_dashboard_data(
        clan=clan,
        players_data=players_data,
        rush_reports=rush_reports,
        historical_data=historical_data,
        warlog=warlog,
        current_war=current_war,
        capital_raids=capital_raids,
        gold_pass=gold_pass,
        cwl_group=cwl_group
    )
    
    print_separator("ANALYSIS COMPLETE")
    print("\n✅ All analyses completed successfully!")
    print(f"📊 HTML Dashboard: {HTML_REPORT_FILE}")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
