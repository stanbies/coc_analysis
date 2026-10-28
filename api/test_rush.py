"""Tests for rush scoring and the max-level tables. Run: pytest api/"""

import json

import pytest

from rush import (HERO_MAX_LEVELS, SPELL_MAX_LEVELS, TROOP_MAX_LEVELS, generate_rush_report,
                  rush_method)


def player(th, heroes=(), troops=(), spells=()):
    """Build a minimal API-shaped player; items are (name, level) tuples."""
    item = lambda name, level: {"name": name, "level": level, "village": "home"}
    return {
        "townHallLevel": th,
        "heroes": [item(*h) for h in heroes],
        "troops": [item(*t) for t in troops],
        "spells": [item(*s) for s in spells],
    }


def test_low_town_hall_is_new_account():
    assert generate_rush_report(player(2))["status"] == "New Account"


def test_maxed_for_previous_town_hall():
    # TH16 player measured against TH15 caps
    report = generate_rush_report(player(16, heroes=[("Barbarian King", 90), ("Dragon Duke", 10)]))
    assert report["rush_score"] == 0
    assert report["status"] == "✅ Maxed"
    assert not report["is_rushed"]


def test_hero_levels_weigh_one_each():
    report = generate_rush_report(player(16, heroes=[("Barbarian King", 85)]))
    assert report["hero_score"] == 5
    assert report["rushed_heroes"] == [{"name": "Barbarian King", "current": 85, "target": 90, "missing": 5}]


def test_troop_and_spell_weights():
    report = generate_rush_report(player(16, troops=[("Barbarian", 9)], spells=[("Lightning Spell", 8)]))
    assert report["troop_score"] == pytest.approx(0.6)  # 2 missing x 0.3
    assert report["spell_score"] == pytest.approx(0.8)  # 2 missing x 0.4
    assert report["rush_score"] == pytest.approx(1.4)


def test_levels_above_benchmark_earn_no_credit():
    report = generate_rush_report(player(16, heroes=[("Barbarian King", 95), ("Archer Queen", 85)]))
    assert report["hero_score"] == 5
    assert report["rush_percentage"] == pytest.approx(round(100 - (90 + 85) / 180 * 100, 1))


def test_many_missing_hero_levels_is_severely_rushed():
    report = generate_rush_report(player(16, heroes=[("Barbarian King", 69)]))  # 21 missing
    assert report["status"] == "🔴 Severely Rushed (Heroes)"
    assert report["is_rushed"]


@pytest.mark.parametrize("score_levels, status", [
    (3, "✅ Maxed"), (10, "🟢 Slightly Behind"), (20, "🟡 Moderately Rushed"),
])
def test_status_thresholds(score_levels, status):
    report = generate_rush_report(player(16, heroes=[("Barbarian King", 90 - score_levels)]))
    assert report["status"] == status


def test_minion_prince_is_not_scored():
    report = generate_rush_report(player(16, heroes=[("Barbarian King", 90), ("Minion Prince", 10)]))
    assert report["rush_score"] == 0
    assert report["total_missing_hero_levels"] == 0
    assert report["rushed_heroes"] == []
    assert report["rush_percentage"] == 0  # MP not part of the benchmark either


def test_unknown_items_and_builder_base_are_ignored():
    p = player(16, heroes=[("Battle Machine", 1)], troops=[("Super Barbarian", 1)])
    p["heroes"].append({"name": "Barbarian King", "level": 1, "village": "builderBase"})
    assert generate_rush_report(p)["rush_score"] == 0


def test_rush_method_export_matches_scoring():
    method = json.loads(json.dumps(rush_method()))  # must survive the JSON export
    assert method["weights"] == {"hero": 1.0, "troop": 0.3, "spell": 0.4}
    limits = [t["maxScore"] for t in method["statusThresholds"]]
    assert limits == sorted(limits)
    assert method["excludedHeroes"] == ["Minion Prince"]
    assert method["heroCaps"]["Dragon Duke"]["17"] == 20
    # Each threshold's top score really produces that status (above
    # heroSevereMissing hero levels, the hero rule takes over)
    for t in method["statusThresholds"]:
        if t["maxScore"] > method["heroSevereMissing"]:
            continue
        hero_missing = int(t["maxScore"])
        report = generate_rush_report(player(16, heroes=[("Barbarian King", 90 - hero_missing)]))
        assert report["status"] == t["status"]


@pytest.mark.parametrize("table", [HERO_MAX_LEVELS, TROOP_MAX_LEVELS, SPELL_MAX_LEVELS],
                         ids=["heroes", "troops", "spells"])
def test_tables_never_decrease_with_town_hall(table):
    for name, levels in table.items():
        ths = sorted(levels)
        assert ths == list(range(ths[0], ths[-1] + 1)), f"{name} has a gap in Town Halls"
        caps = [levels[th] for th in ths]
        assert caps == sorted(caps), f"{name} cap decreases at a higher Town Hall"
