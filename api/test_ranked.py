"""Tests for ranked snapshots and the subscriber list. Run: pytest api/"""

from datetime import datetime, timezone

import pytest

from ranked import (league_number, previous_status, ranked_history_export, ranked_status, record_results,
                    record_snapshot, week_key)
from subscribers import parse_subscribers


def player(tag="#P1", th=17, league_id=105000029, name="Dragon League 29"):
    tier = {"id": league_id, "name": name} if league_id else None
    return {"tag": tag, "name": "Player", "townHallLevel": th, "leagueTier": tier, "trophies": 300}


def at(day):
    return datetime(2026, 10, day, 9, tzinfo=timezone.utc)


def test_league_number_from_tier_id():
    assert league_number({"id": 105000029}) == 29
    assert league_number({"id": 105000000, "name": "Unranked"}) == 0
    assert league_number(None) == 0


def test_ranked_status_unranked_player():
    s = ranked_status(player(league_id=None))
    assert s["league"] == 0 and s["leagueName"] == "Unranked"


def test_week_key_uses_iso_weeks():
    assert week_key(at(26)) == "2026-W44"   # Monday
    assert week_key(at(25)) == "2026-W43"   # Sunday before


def test_rerun_in_same_week_overwrites_and_keeps_other_players():
    data = {"weeks": {}}
    record_snapshot(data, {"#P1": ranked_status(player()), "#P2": ranked_status(player("#P2"))}, at(26))
    record_snapshot(data, {"#P1": ranked_status(player(league_id=105000030))}, at(27))
    players = data["weeks"]["2026-W44"]["players"]
    assert players["#P1"]["league"] == 30
    assert "#P2" in players


def test_previous_status_skips_weeks_without_the_player():
    data = {"weeks": {}}
    record_snapshot(data, {"#P1": ranked_status(player(league_id=105000027))}, at(12))
    record_snapshot(data, {"#P2": ranked_status(player("#P2"))}, at(19))
    key = record_snapshot(data, {"#P1": ranked_status(player())}, at(26))
    assert previous_status(data, "#P1", key) == ("2026-W42", data["weeks"]["2026-W42"]["players"]["#P1"])
    assert previous_status(data, "#P2", "2026-W43") == (None, None)


def history_entry(season_start, league=29, placement=12):
    return {"leagueSeasonId": int(season_start.timestamp()), "leagueTierId": 105000000 + league,
            "placement": placement, "leagueTrophies": 640, "attackWins": 10, "attackLosses": 2,
            "maxBattles": 14}


def test_results_go_to_the_week_they_were_played_and_keep_the_snapshot():
    data = {"weeks": {}}
    record_snapshot(data, {"#P1": ranked_status(player(th=17))}, at(19))   # W43, league 29
    week_start = datetime(2026, 10, 19, 5, tzinfo=timezone.utc)
    record_results(data, "#P1", [history_entry(week_start), history_entry(at(12), league=27)])
    w43 = data["weeks"]["2026-W43"]["players"]["#P1"]
    assert w43["townHallLevel"] == 17
    assert w43["result"] == {"league": 29, "placement": 12, "trophies": 640, "attacks": 12, "maxAttacks": 14}
    # A week from before our first snapshot is backfilled from the history
    w42 = data["weeks"]["2026-W42"]["players"]["#P1"]
    assert w42["league"] == 27 and w42["leagueName"] == "Titan League 27"
    # Recording the week again keeps its result
    record_snapshot(data, {"#P1": ranked_status(player(th=17))}, at(20))
    assert "result" in data["weeks"]["2026-W43"]["players"]["#P1"]


def test_parse_subscribers_normalizes_and_skips_comments():
    subs = parse_subscribers("# comment\n\nIemand@Mail.com, 2ppo\niemand@mail.com,#2PP0\nb@x.be,#8YQ\n")
    assert subs == [{"email": "iemand@mail.com", "tag": "#2PP0"}, {"email": "b@x.be", "tag": "#8YQ"}]


@pytest.mark.parametrize("line", ["geen-email,#2PP", "a@b.be,#ABC", "a@b.be", "a@b.be,#2PP,extra"])
def test_parse_subscribers_rejects_bad_lines(line):
    with pytest.raises(ValueError, match="line 1"):
        parse_subscribers(line)


def test_history_export_is_oldest_first_with_week_start_and_optional_fields():
    data = {"weeks": {}}
    record_snapshot(data, {"#P1": ranked_status(player(th=17))}, at(26))          # W44, live
    record_results(data, "#P1", [history_entry(datetime(2026, 10, 19, 5, tzinfo=timezone.utc), league=28)])  # W43
    weeks = ranked_history_export(data)
    assert [w["week"] for w in weeks] == ["2026-W43", "2026-W44"]
    assert weeks[0]["start"] == "2026-10-19"
    assert weeks[0]["players"]["#P1"] == {"league": 28, "result": {"league": 28, "placement": 12, "trophies": 640,
                                                                  "attacks": 12, "maxAttacks": 14}}
    assert weeks[1]["players"]["#P1"] == {"league": 29, "townHallLevel": 17}
