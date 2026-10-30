"""Weekly ranked snapshots: town hall, ranked league and weekly results per player.

Snapshots live in ranked_snapshots.json, one entry per ISO week (UTC):
    {"weeks": {"2026-W44": {"recorded_at": ..., "players": {"#TAG": {...}}}}}
A tournament week starts Monday 05:00 UTC, so it falls in a single ISO week.
Each player entry holds the status seen when the week was recorded and, once
the week is over, its "result" from the API's league history. The API only
keeps 8 weeks of that history, so every run merges it in to keep it longer.
Reruns are safe: they overwrite the same week's entries.

Usage:
    python api/ranked.py                  # snapshot every clan member
    python api/ranked.py --tag "#2PP"     # snapshot one player
    python api/ranked.py --tag "#2PP" --inspect   # also print raw ranked API fields
"""

import argparse
import json
import os
import sys
from datetime import date, datetime, timezone

import yaml

from coc_api import get_clan_members, get_player_info, get_player_league_history
from config import CLAN_TAG, PUBLISHED_RANKED_FILE, RANKED_FILE

# leagueTier ids are this base + the league number: 0 Unranked, 1-33 Skeleton
# League 1 up to Electro League 33 (three numbered leagues per creature name),
# 34-36 Legend III, II, I. Checked against /leaguetiers in October 2026.
LEAGUE_TIER_BASE_ID = 105000000
LEAGUE_CREATURES = ("Skeleton", "Barbarian", "Archer", "Wizard", "Valkyrie", "Witch",
                    "Golem", "P.E.K.K.A", "Titan", "Dragon", "Electro")
LEGEND_LEAGUES = {34: "Legend III", 35: "Legend II", 36: "Legend I"}

# Raw player fields shown by --inspect, to check the API against our assumptions
RANKED_FIELDS = ("townHallLevel", "trophies", "bestTrophies", "league", "leagueTier",
                 "currentLeagueGroupTag", "currentLeagueSeasonId",
                 "previousLeagueGroupTag", "previousLeagueSeasonId", "legendStatistics")


def league_number(league_tier: dict | None) -> int:
    """Ranked league number from a leagueTier object (0 when unranked)."""
    if not league_tier or not league_tier.get("id"):
        return 0
    return league_tier["id"] - LEAGUE_TIER_BASE_ID


def league_name(number: int) -> str:
    """Display name of a league number, as the API names it."""
    if number in LEGEND_LEAGUES:
        return LEGEND_LEAGUES[number]
    if 1 <= number <= 3 * len(LEAGUE_CREATURES):
        return f"{LEAGUE_CREATURES[(number - 1) // 3]} League {number}"
    return "Unranked"


def ranked_status(player: dict) -> dict:
    """The fields we keep per player per week."""
    tier = player.get("leagueTier")
    return {
        "name": player.get("name"),
        "townHallLevel": player.get("townHallLevel"),
        "league": league_number(tier),
        "leagueName": tier.get("name") if tier else "Unranked",
        "trophies": player.get("trophies"),
    }


def week_key(when: datetime) -> str:
    """ISO week label like 2026-W44."""
    year, week, _ = when.isocalendar()
    return f"{year}-W{week:02d}"


def load_snapshots() -> dict:
    """Load snapshots; local runs fall back to the committed file, like the war history."""
    for path in (RANKED_FILE, PUBLISHED_RANKED_FILE):
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"⚠️  Warning: Could not load ranked snapshots from {path}: {e}")
    return {"weeks": {}}


def save_snapshots(data: dict):
    os.makedirs(os.path.dirname(RANKED_FILE), exist_ok=True)
    with open(RANKED_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"💾 Ranked snapshots saved to {RANKED_FILE}")


def record_snapshot(data: dict, statuses: dict, when: datetime) -> str:
    """Store player statuses (tag -> ranked_status) under the week of `when`.

    Players already in that week but not in `statuses` are kept, so a
    single-player run doesn't wipe the rest of the clan.
    """
    key = week_key(when)
    week = data["weeks"].setdefault(key, {"players": {}})
    week["recorded_at"] = when.isoformat()
    for tag, status in statuses.items():
        week["players"].setdefault(tag, {}).update(status)
    return key


def record_results(data: dict, tag: str, history: list):
    """Store finished weeks from a player's league history under their week."""
    for entry in history:
        number = entry["leagueTierId"] - LEAGUE_TIER_BASE_ID
        key = week_key(datetime.fromtimestamp(entry["leagueSeasonId"], timezone.utc))
        player = data["weeks"].setdefault(key, {"players": {}})["players"].setdefault(tag, {})
        # Weeks from before we took snapshots only know the league from here
        player.setdefault("league", number)
        player.setdefault("leagueName", league_name(number))
        player["result"] = {
            "league": number,
            "placement": entry.get("placement"),
            "trophies": entry.get("leagueTrophies"),
            "attacks": entry.get("attackWins", 0) + entry.get("attackLosses", 0),
            "maxAttacks": entry.get("maxBattles"),
        }


def previous_status(data: dict, tag: str, before_week: str) -> tuple[str, dict] | tuple[None, None]:
    """The player's most recent snapshot from a week before `before_week`."""
    for key in sorted(data["weeks"], reverse=True):
        if key < before_week and tag in data["weeks"][key]["players"]:
            return key, data["weeks"][key]["players"][tag]
    return None, None


def load_th_table(path: str) -> dict:
    """Load a {town hall: value} YAML table."""
    with open(path, "r", encoding="utf-8") as f:
        table = yaml.safe_load(f) or {}
    if not all(isinstance(th, int) for th in table):
        raise ValueError(f"{path}: keys must be Town Hall numbers")
    return table


def for_town_hall(table: dict, th: int):
    """Value for this Town Hall, or for the closest lower one listed."""
    lower = [level for level in table if level <= th]
    return table[max(lower)] if lower else None


def ranked_history_export(data: dict) -> list:
    """All recorded weeks, oldest first, in the shape the dashboard reads.

    Per player: the league, the Town Hall when the week was recorded live (not
    for weeks backfilled from league history) and the result once finished.
    """
    weeks = []
    for key in sorted(data["weeks"]):
        year, week = key.split("-W")
        players = {}
        for tag, p in data["weeks"][key]["players"].items():
            entry = {"league": p.get("league", 0)}
            if p.get("townHallLevel"):
                entry["townHallLevel"] = p["townHallLevel"]
            if p.get("result"):
                entry["result"] = p["result"]
            players[tag] = entry
        weeks.append({
            "week": key,
            "start": date.fromisocalendar(int(year), int(week), 1).isoformat(),
            "players": players,
        })
    return weeks


def inspect_player(tag: str, player: dict, history: list | None):
    """Print the raw ranked fields and recent league history of one player."""
    print(f"\n🔎 Raw ranked fields for {tag}:")
    fields = {k: player.get(k) for k in RANKED_FIELDS}
    # Catch league-related fields we don't know about yet
    fields.update({k: v for k, v in player.items() if "league" in k.lower() and k not in fields})
    print(json.dumps(fields, indent=2, ensure_ascii=False))
    print(f"\n🔎 League history ({len(history) if history is not None else 'unavailable'} entries, latest 3):")
    # Oldest first; the running week isn't in it yet
    print(json.dumps((history or [])[-3:], indent=2, ensure_ascii=False))


def main():
    parser = argparse.ArgumentParser(description="Record this week's ranked snapshot.")
    parser.add_argument("--tag", action="append", help="player tag (repeatable); default: all clan members")
    parser.add_argument("--inspect", action="store_true", help="print raw ranked API fields")
    args = parser.parse_args()

    tags = args.tag
    if not tags:
        members = get_clan_members(CLAN_TAG)
        if members is None:
            print("❌ Could not fetch clan members")
            sys.exit(1)
        tags = [m["tag"] for m in members]

    statuses, histories, missing = {}, {}, []
    for tag in tags:
        player = get_player_info(tag)
        if not player:
            missing.append(tag)
            continue
        statuses[player["tag"]] = ranked_status(player)
        histories[player["tag"]] = get_player_league_history(player["tag"])
        if args.inspect:
            inspect_player(player["tag"], player, histories[player["tag"]])

    if not statuses:
        print("❌ No players fetched")
        sys.exit(1)
    if missing:
        print(f"::warning::Ranked snapshot is missing {len(missing)} player(s): {', '.join(missing)}")
    no_history = [tag for tag, history in histories.items() if history is None]
    if no_history:
        print(f"::warning::No league history for {len(no_history)} player(s): {', '.join(no_history)}")

    data = load_snapshots()
    now = datetime.now(timezone.utc)
    key = record_snapshot(data, statuses, now)
    for tag, history in histories.items():
        record_results(data, tag, history or [])
    for tag, s in statuses.items():
        prev_week, prev = previous_status(data, tag, key)
        change = f", previous {prev_week}: league {prev['league']}" if prev else ""
        print(f"   {s['name']} ({tag}) TH{s['townHallLevel']}: {s['leagueName']} (league {s['league']}){change}")
    save_snapshots(data)


if __name__ == "__main__":
    main()
