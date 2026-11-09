"""Clan War League archive and the numbers behind the CWL recap mail.

The API only returns a CWL group during and shortly after the league, so the
6-hourly scraper saves every season to cwl/<season>.json (same publish/local
split as the war history): the group roster, our own wars in full and the
scores of the other wars in the group, which is enough for the standings.
"""

import json
import os

from config import CWL_DIR, PUBLISHED_CWL_DIR

# Standings: a won war adds 10 stars on top of the stars scored
WIN_BONUS = 10

# Rapportcijfer (1-10) for one war day, like a football paper's player rating:
# a base per stars, adjusted for the target's Town Hall and for the defence.
RATING_BY_STARS = {3: 8.0, 2: 6.0, 1: 5.0, 0: 4.0}
RATING_MISSED = 3.0          # in the lineup, attack not used
RATING_NEAR_THREE = 0.5      # two stars with at least 90% destruction
RATING_HIT_UP = 1.0          # target has a higher Town Hall
RATING_HIT_DOWN = -0.5       # three stars on a lower Town Hall
RATING_HELD = 0.5            # attacked, but nobody three-starred the base


def _side(side: dict, members: bool) -> dict:
    kept = {k: side.get(k) for k in ("tag", "name", "stars", "destructionPercentage", "attacks")}
    if members:
        kept["members"] = side.get("members", [])
    return kept


def strip_war(war: dict, clan_tag: str) -> dict:
    """A war without badges; members only for our own wars."""
    ours = clan_tag in (war.get("clan", {}).get("tag"), war.get("opponent", {}).get("tag"))
    return {
        **{k: war.get(k) for k in ("state", "teamSize", "startTime", "endTime")},
        "clan": _side(war.get("clan", {}), ours),
        "opponent": _side(war.get("opponent", {}), ours),
    }


def build_season(group: dict, wars: dict, clan_tag: str, war_league: dict | None,
                 previous: dict | None = None) -> dict:
    """Archive entry for a season; wars that failed to fetch keep their previous version."""
    stored = dict((previous or {}).get("wars", {}))
    stored.update({tag: strip_war(war, clan_tag) for tag, war in wars.items() if war})
    return {
        "season": group.get("season"),
        "state": group.get("state"),
        "clanTag": clan_tag,
        "warLeague": (war_league or {}).get("name") or (previous or {}).get("warLeague"),
        "clans": [{"tag": c.get("tag"), "name": c.get("name"),
                   "members": [{k: m.get(k) for k in ("tag", "name", "townHallLevel")}
                               for m in c.get("members", [])]}
                  for c in group.get("clans", [])],
        "rounds": [[t for t in r.get("warTags", []) if t != "#0"] for r in group.get("rounds", [])],
        "wars": stored,
    }


def season_path(season: str, directory: str = CWL_DIR) -> str:
    return os.path.join(directory, f"{season}.json")


def load_season(season: str | None = None) -> dict | None:
    """A saved season (the newest one when season is None), local output first."""
    for directory in dict.fromkeys((CWL_DIR, PUBLISHED_CWL_DIR)):
        if not os.path.isdir(directory):
            continue
        names = sorted(n for n in os.listdir(directory) if n.endswith(".json") and n[0].isdigit())
        if season:
            names = [n for n in names if n == f"{season}.json"]
        if names:
            with open(os.path.join(directory, names[-1]), "r", encoding="utf-8") as f:
                return json.load(f)
    return None


def save_season(group: dict, wars: dict, clan_tag: str, war_league: dict | None):
    season = group.get("season")
    if not season:
        return
    previous = load_season(season)
    data = build_season(group, wars, clan_tag, war_league, previous)
    os.makedirs(CWL_DIR, exist_ok=True)
    with open(season_path(season), "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"💾 CWL season {season} saved to {season_path(season)}")


# --- Analysis ---------------------------------------------------------------

def sides(war: dict, clan_tag: str) -> tuple[dict, dict] | None:
    """(our side, their side) when we play in this war."""
    if war["clan"]["tag"] == clan_tag:
        return war["clan"], war["opponent"]
    if war["opponent"]["tag"] == clan_tag:
        return war["opponent"], war["clan"]
    return None


def outcome(a: dict, b: dict) -> str:
    """win / loss / draw for side a: stars first, then destruction."""
    key_a = (a.get("stars", 0), a.get("destructionPercentage", 0))
    key_b = (b.get("stars", 0), b.get("destructionPercentage", 0))
    return "win" if key_a > key_b else "loss" if key_a < key_b else "draw"


def our_rounds(season: dict) -> list[dict]:
    """Our war of every round that has one, in round order."""
    rounds = []
    for number, tags in enumerate(season["rounds"], 1):
        for tag in tags:
            war = season["wars"].get(tag)
            pair = war and sides(war, season["clanTag"])
            if pair:
                us, them = pair
                rounds.append({"round": number, "war": war, "us": us, "them": them,
                               "result": outcome(us, them) if war["state"] == "warEnded" else None})
    return rounds


def is_finished(season: dict) -> bool:
    """Every round played and ended (also true when the group state never reached 'ended')."""
    if season.get("state") == "ended":
        return True
    rounds = our_rounds(season)
    return (len(rounds) == len(season["clans"]) - 1
            and all(r["war"]["state"] == "warEnded" for r in rounds))


def standings(season: dict) -> list[dict]:
    """Group table: stars plus the win bonus, then destruction (summed over all bases)."""
    table = {c["tag"]: {"tag": c["tag"], "name": c["name"], "stars": 0, "destruction": 0.0,
                        "wins": 0, "draws": 0, "losses": 0} for c in season["clans"]}
    for war in season["wars"].values():
        if war["state"] not in ("inWar", "warEnded"):
            continue
        for a, b in ((war["clan"], war["opponent"]), (war["opponent"], war["clan"])):
            row = table.get(a["tag"])
            if not row:
                continue
            row["stars"] += a.get("stars", 0)
            row["destruction"] += a.get("destructionPercentage", 0) * (war.get("teamSize") or 0)
            if war["state"] == "warEnded":
                result = outcome(a, b)
                row[{"win": "wins", "draw": "draws", "loss": "losses"}[result]] += 1
                if result == "win":
                    row["stars"] += WIN_BONUS
    ranked = sorted(table.values(), key=lambda r: (-r["stars"], -r["destruction"]))
    for position, row in enumerate(ranked, 1):
        row["position"] = position
    return ranked


def _positions(members: list) -> dict:
    """Player tag -> rank on the war map (1 = top), from the API's mapPosition."""
    order = sorted(members, key=lambda m: m.get("mapPosition", 0))
    return {m["tag"]: i for i, m in enumerate(order, 1)}


def player_stats(season: dict) -> dict:
    """Per player of our clan: lineups, attacks, missed attacks and defences."""
    roster = next((c["members"] for c in season["clans"] if c["tag"] == season["clanTag"]), [])
    stats = {m["tag"]: {"tag": m["tag"], "name": m["name"], "th": m.get("townHallLevel", 0),
                        "lineups": 0, "missed": 0, "attacks": [], "defenses": [], "matches": []} for m in roster}

    for r in our_rounds(season):
        war, us, them = r["war"], r["us"], r["them"]
        if war["state"] not in ("inWar", "warEnded"):
            continue
        ours, theirs = _positions(us["members"]), _positions(them["members"])
        defenders = {m["tag"]: m for m in them["members"]}
        conceded = {}  # our player -> best stars an opponent took off their base
        for enemy in them["members"]:
            for attack in enemy.get("attacks") or []:
                tag = attack["defenderTag"]
                conceded[tag] = max(conceded.get(tag, 0), attack["stars"])
        for member in us["members"]:
            player = stats.setdefault(member["tag"], {
                "tag": member["tag"], "name": member["name"], "th": member.get("townhallLevel", 0),
                "lineups": 0, "missed": 0, "attacks": [], "defenses": [], "matches": []})
            player["name"] = member["name"]
            player["th"] = max(player["th"], member.get("townhallLevel", 0))
            player["lineups"] += 1
            attacks = member.get("attacks") or []
            missed = not attacks and war["state"] == "warEnded"
            if missed:
                player["missed"] += 1
            for attack in attacks:
                defender = defenders.get(attack["defenderTag"], {})
                player["attacks"].append({
                    "round": r["round"], "opponent": them["name"],
                    "stars": attack["stars"], "destruction": attack["destructionPercentage"],
                    "th": member.get("townhallLevel", 0),
                    "defenderTh": defender.get("townhallLevel", 0),
                    "position": ours.get(member["tag"]),
                    "defenderPosition": theirs.get(attack["defenderTag"]),
                })
            match = {"round": r["round"], "opponent": them["name"], "position": ours.get(member["tag"]),
                     "attack": player["attacks"][-1] if attacks else None, "missed": missed,
                     "conceded": conceded.get(member["tag"])}
            match["rating"] = match_rating(match)
            player["matches"].append(match)
        for enemy in them["members"]:
            for attack in enemy.get("attacks") or []:
                if attack["defenderTag"] in stats:
                    stats[attack["defenderTag"]]["defenses"].append({
                        "round": r["round"], "stars": attack["stars"],
                        "destruction": attack["destructionPercentage"]})

    for player in stats.values():
        attacks = player["attacks"]
        player["stars"] = sum(a["stars"] for a in attacks)
        player["destructionTotal"] = sum(a["destruction"] for a in attacks)
        player["threeStars"] = sum(a["stars"] == 3 for a in attacks)
        player["hitUpStars"] = sum(a["stars"] for a in attacks if a["defenderTh"] > a["th"])
        ratings = [m["rating"] for m in player["matches"] if m["rating"] is not None]
        player["rating"] = sum(ratings) / len(ratings) if ratings else None
    return stats


def match_rating(match: dict) -> float | None:
    """Rapportcijfer for one war day; None while the attack can still come."""
    attack = match["attack"]
    if attack is None:
        if not match["missed"]:
            return None
        rating = RATING_MISSED
    else:
        rating = RATING_BY_STARS[attack["stars"]]
        if attack["stars"] == 2 and attack["destruction"] >= 90:
            rating += RATING_NEAR_THREE
        if attack["defenderTh"] > attack["th"]:
            rating += RATING_HIT_UP
        elif attack["stars"] == 3 and attack["defenderTh"] < attack["th"]:
            rating += RATING_HIT_DOWN
    if match["conceded"] is not None and match["conceded"] < 3:
        rating += RATING_HELD
    return max(1.0, min(10.0, rating))


def clan_totals(season: dict, stats: dict) -> dict:
    rounds = our_rounds(season)
    played = [p for p in stats.values() if p["lineups"]]
    attacks = [a for p in played for a in p["attacks"]]
    allowed = sum(r["war"]["teamSize"] for r in rounds if r["war"]["state"] == "warEnded")
    allowed += sum(len(r["us"].get("members", [])) for r in rounds if r["war"]["state"] == "inWar")
    return {
        "wins": sum(r["result"] == "win" for r in rounds),
        "draws": sum(r["result"] == "draw" for r in rounds),
        "losses": sum(r["result"] == "loss" for r in rounds),
        "stars": sum(a["stars"] for a in attacks),
        "attacks": len(attacks),
        "allowed": allowed,
        "threeStars": sum(a["stars"] == 3 for a in attacks),
        "missed": sum(p["missed"] for p in played),
        "players": len(played),
        "perfectAttendance": sum(p["missed"] == 0 for p in played),
    }


def awards(stats: dict) -> dict:
    """Clan awards; a key is missing when nobody qualifies."""
    played = [p for p in stats.values() if p["attacks"]]
    result = {}
    if played:
        result["mvp"] = max(played, key=lambda p: (p["stars"], p["destructionTotal"]))
    # Player of the month: best average rapportcijfer over at least 4 war days
    regulars = [p for p in played if sum(m["rating"] is not None for m in p["matches"]) >= 4]
    if regulars:
        result["best"] = max(regulars, key=lambda p: (p["rating"], p["stars"]))
    perfect = [p for p in played if len(p["attacks"]) >= 4 and p["threeStars"] == len(p["attacks"])]
    if perfect:
        result["perfect"] = sorted(perfect, key=lambda p: -len(p["attacks"]))
    daredevil = max(played, key=lambda p: (p["hitUpStars"], p["stars"]), default=None)
    if daredevil and daredevil["hitUpStars"]:
        result["daredevil"] = daredevil
    defenders = [p for p in stats.values() if len(p["defenses"]) >= 3]
    if defenders:
        result["wall"] = min(defenders, key=lambda p: (
            sum(d["stars"] for d in p["defenses"]) / len(p["defenses"]), -len(p["defenses"])))
    return result


def star_ranking(stats: dict) -> list[dict]:
    """Players who attacked, best first."""
    return sorted((p for p in stats.values() if p["attacks"]),
                  key=lambda p: (-p["stars"], -p["destructionTotal"]))
