"""
Warn when players exceed the max-level tables in rush.py.

A player above the cap for their own Town Hall means a game update raised the
caps and the tables are out of date. Prints GitHub Actions ::warning::
annotations and always exits 0, so the daily update still publishes.

Usage: python api/check_caps.py [path/to/clan_data.json]
"""

import json
import sys
from collections import defaultdict

from config import DASHBOARD_DATA_FILE
from rush import HERO_MAX_LEVELS, SPELL_MAX_LEVELS, TROOP_MAX_LEVELS

TABLES = {"heroes": HERO_MAX_LEVELS, "troops": TROOP_MAX_LEVELS, "spells": SPELL_MAX_LEVELS}


def find_outdated_caps(data: dict) -> dict:
    """Return {(item, th): (highest level seen, table cap)} for every exceeded cap."""
    outdated = defaultdict(lambda: (0, 0))
    for player in data.get("players", []):
        th = player.get("townHallLevel")
        for kind, table in TABLES.items():
            for item in player.get(kind, []):
                cap = table.get(item.get("name"), {}).get(th)
                level = item.get("level", 0)
                if cap is not None and level > cap:
                    key = (item["name"], th)
                    outdated[key] = (max(outdated[key][0], level), cap)
    return dict(outdated)


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else DASHBOARD_DATA_FILE
    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    outdated = find_outdated_caps(data)
    for (name, th), (level, cap) in sorted(outdated.items()):
        print(f"::warning title=Max-level tables out of date::{name} at TH{th}: a player has "
              f"level {level}, table cap is {cap}. Update the tables in api/rush.py.")
    if not outdated:
        print("Max-level tables OK: no player exceeds the cap for their Town Hall.")


if __name__ == "__main__":
    main()
