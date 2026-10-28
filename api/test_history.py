"""Tests for war history recording and the cap checker. Run: pytest api/"""

from check_caps import find_outdated_caps
from history import create_empty_data_structure, parse_coc_time, update_player_historical_stats


def attacks(*stars):
    return {"attacks": [{"stars": s, "destruction": 50 + 25 * s, "defender_th": 16,
                         "hit_type": "= SAME"} for s in stars]}


def record(history, attack_data, war_id="war1", war_date="2026-10-27T09:00:00+00:00"):
    update_player_historical_stats(history, "#P1", "Player", 16, attack_data,
                                   "regular_war", war_id, war_date)
    return history["players"]["#P1"]


def test_later_snapshot_of_same_war_replaces_attacks():
    history = create_empty_data_structure()
    record(history, attacks(2))       # first run: one attack so far
    p = record(history, attacks(2, 3))  # next run: second attack made
    assert p["total_attacks"] == 2
    assert p["total_stars"] == 5
    assert p["three_stars"] == 1 and p["two_stars"] == 1
    assert p["wars_participated"] == 1


def test_repeated_identical_snapshot_does_not_double_count():
    history = create_empty_data_structure()
    record(history, attacks(3, 3))
    p = record(history, attacks(3, 3))
    assert p["total_attacks"] == 2
    assert len(p["attacks_history"]) == 2


def test_separate_wars_accumulate():
    history = create_empty_data_structure()
    record(history, attacks(1), war_id="war1")
    p = record(history, attacks(0, 3), war_id="war2")
    assert p["wars_participated"] == 2
    assert p["total_attacks"] == 3
    assert p["zero_stars"] == 1 and p["one_star"] == 1 and p["three_stars"] == 1


def test_attack_date_is_war_start_not_run_time():
    history = create_empty_data_structure()
    p = record(history, attacks(3), war_date="2026-10-27T09:00:00+00:00")
    assert p["attacks_history"][0]["date"] == "2026-10-27T09:00:00+00:00"


def test_parse_coc_time():
    assert parse_coc_time("20261028T090000.000Z") == "2026-10-28T09:00:00+00:00"
    assert parse_coc_time(None) is None
    assert parse_coc_time("garbage") is None


def test_find_outdated_caps():
    data = {"players": [
        {"townHallLevel": 17, "heroes": [{"name": "Dragon Duke", "level": 21}], "troops": [], "spells": []},
        {"townHallLevel": 17, "heroes": [{"name": "Dragon Duke", "level": 20}], "troops": [], "spells": []},
    ]}
    assert find_outdated_caps(data) == {("Dragon Duke", 17): (21, 20)}
