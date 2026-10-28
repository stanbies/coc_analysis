"""Rush detection: max-level tables per Town Hall and the rush score."""

# Max levels per Town Hall (TH1-TH18), cross-checked against the live clan data
# Heroes: Hero Hall caps (the Hero Hall level is capped by TH). Includes the June 2026
# BK/AQ/GW increase. Troops/spells: laboratory caps, last checked 2026-10-28.
# Pets, siege machines and super troops are not part of the rush score.
# api/check_caps.py warns in the daily workflow when these go out of date.
HERO_MAX_LEVELS = {
    "Barbarian King": {7: 10, 8: 20, 9: 30, 10: 40, 11: 50, 12: 65, 13: 75, 14: 85, 15: 90, 16: 95, 17: 100, 18: 110},
    "Archer Queen":   {8: 10, 9: 30, 10: 40, 11: 50, 12: 65, 13: 75, 14: 85, 15: 90, 16: 95, 17: 100, 18: 110},
    "Minion Prince":  {9: 10, 10: 20, 11: 30, 12: 40, 13: 50, 14: 60, 15: 70, 16: 80, 17: 90, 18: 95},
    "Grand Warden":   {11: 20, 12: 40, 13: 50, 14: 60, 15: 65, 16: 70, 17: 75, 18: 85},
    "Royal Champion": {13: 25, 14: 30, 15: 40, 16: 45, 17: 50, 18: 55},
    "Dragon Duke":    {15: 10, 16: 15, 17: 20, 18: 25},
}

# Heroes the clan doesn't use; still shown on the dashboard (with their cap),
# but not scored. Remove a name to count it again.
RUSH_EXCLUDED_HEROES = {"Minion Prince"}

# Points per missing level, compared against the previous Town Hall's caps
HERO_WEIGHT = 1.0
TROOP_WEIGHT = 0.3
SPELL_WEIGHT = 0.4

# (highest score for this status, status, counts as rushed), checked in order
STATUS_THRESHOLDS = [
    (3, "✅ Maxed", False),
    (10, "🟢 Slightly Behind", False),
    (25, "🟡 Moderately Rushed", True),
    (50, "🟠 Rushed", True),
]
SEVERE_STATUS = "🔴 Severely Rushed"  # anything above the last threshold

# More missing hero levels than this always means severely rushed
HERO_SEVERE_MISSING = 20
HERO_SEVERE_STATUS = "🔴 Severely Rushed (Heroes)"


TROOP_MAX_LEVELS = {
    "Barbarian":         {1: 1, 2: 1, 3: 2, 4: 2, 5: 3, 6: 3, 7: 4, 8: 5, 9: 6, 10: 7, 11: 8, 12: 9, 13: 9, 14: 10, 15: 11, 16: 12, 17: 12, 18: 13},
    "Archer":            {1: 1, 2: 1, 3: 2, 4: 2, 5: 3, 6: 3, 7: 4, 8: 5, 9: 6, 10: 7, 11: 8, 12: 9, 13: 9, 14: 10, 15: 11, 16: 12, 17: 13, 18: 14},
    "Giant":             {1: 1, 2: 1, 3: 1, 4: 2, 5: 2, 6: 3, 7: 4, 8: 5, 9: 6, 10: 7, 11: 8, 12: 9, 13: 10, 14: 10, 15: 11, 16: 12, 17: 13, 18: 14},
    "Goblin":            {2: 1, 3: 2, 4: 2, 5: 3, 6: 3, 7: 4, 8: 5, 9: 6, 10: 7, 11: 7, 12: 8, 13: 8, 14: 8, 15: 9, 16: 9, 17: 9, 18: 10},
    "Wall Breaker":      {3: 1, 4: 2, 5: 2, 6: 3, 7: 4, 8: 5, 9: 5, 10: 6, 11: 7, 12: 8, 13: 9, 14: 10, 15: 11, 16: 12, 17: 13, 18: 14},
    "Balloon":           {4: 2, 5: 2, 6: 3, 7: 4, 8: 5, 9: 6, 10: 6, 11: 7, 12: 8, 13: 9, 14: 10, 15: 10, 16: 11, 17: 12, 18: 13},
    "Wizard":            {5: 2, 6: 3, 7: 4, 8: 5, 9: 6, 10: 7, 11: 8, 12: 9, 13: 10, 14: 10, 15: 11, 16: 12, 17: 13, 18: 14},
    "Healer":            {6: 1, 7: 2, 8: 3, 9: 4, 10: 4, 11: 5, 12: 5, 13: 6, 14: 7, 15: 8, 16: 9, 17: 10, 18: 11},
    "Dragon":            {7: 2, 8: 3, 9: 4, 10: 5, 11: 6, 12: 7, 13: 8, 14: 9, 15: 10, 16: 11, 17: 12, 18: 13},
    "P.E.K.K.A":         {8: 3, 9: 4, 10: 6, 11: 7, 12: 8, 13: 9, 14: 9, 15: 10, 16: 11, 17: 12, 18: 13},
    "Baby Dragon":       {9: 2, 10: 4, 11: 5, 12: 6, 13: 7, 14: 8, 15: 9, 16: 10, 17: 11, 18: 12},
    "Miner":             {10: 3, 11: 5, 12: 6, 13: 7, 14: 8, 15: 9, 16: 10, 17: 11, 18: 12},
    "Electro Dragon":    {11: 2, 12: 3, 13: 4, 14: 5, 15: 6, 16: 7, 17: 8, 18: 9},
    "Yeti":              {12: 2, 13: 3, 14: 4, 15: 5, 16: 6, 17: 7, 18: 8},
    "Dragon Rider":      {13: 2, 14: 3, 15: 3, 16: 4, 17: 5, 18: 6},
    "Electro Titan":     {14: 2, 15: 3, 16: 4, 17: 4, 18: 5},
    "Root Rider":        {15: 2, 16: 3, 17: 3, 18: 4},
    "Thrower":           {16: 2, 17: 3, 18: 4},
    "Meteor Golem":      {17: 2, 18: 3},
    "Minion":            {7: 2, 8: 4, 9: 5, 10: 6, 11: 7, 12: 8, 13: 9, 14: 10, 15: 11, 16: 12, 17: 13, 18: 14},
    "Hog Rider":         {7: 2, 8: 4, 9: 5, 10: 6, 11: 7, 12: 9, 13: 10, 14: 11, 15: 12, 16: 13, 17: 14, 18: 15},
    "Valkyrie":          {8: 2, 9: 4, 10: 5, 11: 6, 12: 7, 13: 8, 14: 9, 15: 10, 16: 11, 17: 12, 18: 12},
    "Golem":             {8: 2, 9: 4, 10: 5, 11: 7, 12: 9, 13: 10, 14: 11, 15: 12, 16: 13, 17: 14, 18: 15},
    "Witch":             {9: 2, 10: 3, 11: 4, 12: 5, 13: 5, 14: 5, 15: 6, 16: 7, 17: 7, 18: 8},
    "Lava Hound":        {9: 2, 10: 3, 11: 4, 12: 5, 13: 6, 14: 6, 15: 6, 16: 7, 17: 7, 18: 8},
    "Bowler":            {10: 2, 11: 3, 12: 4, 13: 5, 14: 6, 15: 7, 16: 8, 17: 9, 18: 10},
    "Ice Golem":         {11: 3, 12: 5, 13: 5, 14: 6, 15: 7, 16: 8, 17: 9, 18: 9},
    "Headhunter":        {12: 2, 13: 3, 14: 3, 15: 3, 16: 3, 17: 3, 18: 4},
    "Apprentice Warden": {13: 2, 14: 3, 15: 4, 16: 4, 17: 4, 18: 4},
    "Druid":             {14: 2, 15: 3, 16: 4, 17: 5, 18: 6},
    "Furnace":           {15: 2, 16: 3, 17: 4, 18: 4},
    "Ruin Witch":        {16: 2, 17: 3, 18: 4},
}


SPELL_MAX_LEVELS = {
    "Lightning Spell":    {5: 4, 6: 4, 7: 4, 8: 5, 9: 6, 10: 7, 11: 8, 12: 9, 13: 9, 14: 9, 15: 10, 16: 11, 17: 12, 18: 13},
    "Healing Spell":      {6: 3, 7: 4, 8: 5, 9: 6, 10: 7, 11: 7, 12: 7, 13: 8, 14: 8, 15: 9, 16: 10, 17: 11, 18: 12},
    "Rage Spell":         {7: 4, 8: 5, 9: 5, 10: 5, 11: 5, 12: 6, 13: 6, 14: 6, 15: 6, 16: 6, 17: 6, 18: 7},
    "Jump Spell":         {9: 2, 10: 3, 11: 3, 12: 3, 13: 4, 14: 4, 15: 5, 16: 5, 17: 5, 18: 5},
    "Freeze Spell":       {9: 2, 10: 5, 11: 6, 12: 7, 13: 7, 14: 7, 15: 7, 16: 7, 17: 7, 18: 8},
    "Clone Spell":        {10: 3, 11: 5, 12: 5, 13: 6, 14: 7, 15: 8, 16: 8, 17: 8, 18: 9},
    "Invisibility Spell": {11: 2, 12: 3, 13: 4, 14: 4, 15: 4, 16: 4, 17: 4, 18: 4},
    "Recall Spell":       {13: 2, 14: 3, 15: 4, 16: 5, 17: 6, 18: 7},
    "Revive Spell":       {15: 2, 16: 3, 17: 4, 18: 5},
    "Totem Spell":        {16: 2, 17: 3, 18: 4},
    "Poison Spell":       {8: 2, 9: 3, 10: 4, 11: 5, 12: 6, 13: 7, 14: 8, 15: 9, 16: 10, 17: 11, 18: 12},
    "Earthquake Spell":   {8: 2, 9: 3, 10: 4, 11: 5, 12: 5, 13: 5, 14: 6, 15: 6, 16: 7, 17: 7, 18: 8},
    "Haste Spell":        {9: 2, 10: 4, 11: 5, 12: 5, 13: 5, 14: 5, 15: 5, 16: 5, 17: 6, 18: 7},
    "Skeleton Spell":     {9: 1, 10: 3, 11: 4, 12: 6, 13: 7, 14: 7, 15: 8, 16: 8, 17: 8, 18: 8},
    "Bat Spell":          {10: 3, 11: 4, 12: 5, 13: 5, 14: 5, 15: 6, 16: 6, 17: 7, 18: 8},
    "Overgrowth Spell":   {12: 2, 13: 2, 14: 3, 15: 3, 16: 4, 17: 4, 18: 5},
    "Ice Block Spell":    {14: 2, 15: 3, 16: 4, 17: 5, 18: 6},
    "Angry Spell":        {15: 1, 16: 2, 17: 3, 18: 4},
}


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
    
    # --- 1. CHECK HEROES ---
    heroes = player.get('heroes', [])
    total_hero_possible = 0
    total_hero_current = 0
    
    for hero in heroes:
        hero_name = hero.get('name', '')
        hero_level = hero.get('level', 0)
        village = hero.get('village', '')
        
        # Only check home village heroes the clan actually uses
        if village != 'home' or hero_name in RUSH_EXCLUDED_HEROES:
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
                rush_data["hero_score"] += missing_levels * HERO_WEIGHT
                rush_data["total_missing_hero_levels"] += missing_levels
    
    # --- 2. CHECK TROOPS ---
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
                rush_data["troop_score"] += missing_levels * TROOP_WEIGHT
    
    # --- 3. CHECK SPELLS ---
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
                rush_data["spell_score"] += missing_levels * SPELL_WEIGHT
    
    # --- 4. CALCULATE FINAL SCORES ---
    rush_data["hero_score"] = round(rush_data["hero_score"], 1)
    rush_data["troop_score"] = round(rush_data["troop_score"], 1)
    rush_data["spell_score"] = round(rush_data["spell_score"], 1)
    rush_data["rush_score"] = round(rush_data["hero_score"] + rush_data["troop_score"] + rush_data["spell_score"], 1)
    
    # Calculate overall rush percentage (how far behind they are)
    total_possible = total_hero_possible + total_troop_possible + total_spell_possible
    total_current = total_hero_current + total_troop_current + total_spell_current
    
    if total_possible > 0:
        completion_pct = (total_current / total_possible) * 100
        rush_data["rush_percentage"] = round(100 - completion_pct, 1)
    
    # --- 5. DETERMINE STATUS ---
    score = rush_data["rush_score"]
    hero_missing = rush_data["total_missing_hero_levels"]
    
    rush_data["status"], rush_data["is_rushed"] = SEVERE_STATUS, True
    for max_score, status, is_rushed in STATUS_THRESHOLDS:
        if score <= max_score:
            rush_data["status"], rush_data["is_rushed"] = status, is_rushed
            break

    # Extra penalty for very low heroes
    if hero_missing > HERO_SEVERE_MISSING:
        rush_data["status"], rush_data["is_rushed"] = HERO_SEVERE_STATUS, True

    return rush_data


def rush_method() -> dict:
    """The scoring rules, exported so the dashboard's explanation page can't drift from the code."""
    return {
        "weights": {"hero": HERO_WEIGHT, "troop": TROOP_WEIGHT, "spell": SPELL_WEIGHT},
        "statusThresholds": [
            {"maxScore": max_score, "status": status, "isRushed": is_rushed}
            for max_score, status, is_rushed in STATUS_THRESHOLDS
        ],
        "severeStatus": SEVERE_STATUS,
        "heroSevereMissing": HERO_SEVERE_MISSING,
        "heroSevereStatus": HERO_SEVERE_STATUS,
        "excludedHeroes": sorted(RUSH_EXCLUDED_HEROES),
        "heroCaps": {name: {str(th): cap for th, cap in caps.items()}
                     for name, caps in HERO_MAX_LEVELS.items()},
        "scoredTroopCount": len(TROOP_MAX_LEVELS),
        "scoredSpellCount": len(SPELL_MAX_LEVELS),
    }
