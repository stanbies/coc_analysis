"""Tests for the weekly ranked mail and its config tables. Run: pytest api/"""

from datetime import datetime, timezone

from config import BENCHMARKS_FILE, STRATEGIES_FILE
from ranked import league_name, ranked_status, record_snapshot
from weekly_mail import (WEEK_SECONDS, build_report, compose_mail, for_town_hall, load_th_table,
                         render_html, render_text)

NOW = datetime(2026, 11, 2, 7, tzinfo=timezone.utc)  # Monday, 2026-W45
SEASON = 1793595600  # 2026-11-02 05:00 UTC
BENCHMARKS = {17: 29, 1: 1}
VIDEOS = [{"title": f"Video {i}", "url": f"https://youtu.be/{i}"} for i in range(5)]
STRATEGIES = {17: VIDEOS}


def player(league=29, th=17, name="Speler"):
    return {"tag": "#P1", "name": name, "townHallLevel": th, "clan": {"name": "Zwegerneet"},
            "leagueTier": {"id": 105000000 + league}, "currentLeagueSeasonId": SEASON}


def week_entry(league, weeks_ago=1, placement=12):
    return {"leagueSeasonId": SEASON - weeks_ago * WEEK_SECONDS, "leagueTierId": 105000000 + league,
            "placement": placement, "leagueTrophies": 640, "attackWins": 10, "attackLosses": 2,
            "maxBattles": 14}


def mail_for(p, history=(), snapshots=None):
    report = build_report(p, list(history), snapshots or {"weeks": {}}, BENCHMARKS, STRATEGIES, NOW)
    return report, compose_mail(report)


def test_league_names_match_the_api():
    assert league_name(29) == "Dragon League 29"
    assert league_name(22) == "P.E.K.K.A League 22"
    assert league_name(34) == "Legend III" and league_name(36) == "Legend I"
    assert league_name(0) == "Unranked"


def test_town_hall_falls_back_to_closest_lower_level():
    assert for_town_hall({17: 29, 15: 22}, 16) == 22
    assert for_town_hall({17: 29}, 12) is None


def test_committed_config_tables_are_valid():
    benchmarks = load_th_table(BENCHMARKS_FILE)
    strategies = load_th_table(STRATEGIES_FILE)
    for th in range(1, 19):
        assert 1 <= for_town_hall(benchmarks, th) <= 36
        videos = for_town_hall(strategies, th)
        assert videos and all(v["title"] and v["url"].startswith("https://") for v in videos)


def body(mail):
    return "\n".join(mail["paragraphs"])


def test_above_benchmark_gets_praise_and_no_videos():
    report, mail = mail_for(player(league=31), [week_entry(30)])
    assert "Jij zit er 2 leagues boven." in body(mail)
    assert "📈 Vorige week: Dragon League 30. Nu: Electro League 31." in body(mail)
    assert "Boven verwachting" in mail["subject"] and mail["subject"].startswith("Week 45 · ")
    assert report["videos"] == []


def test_exactly_on_benchmark_counts_as_reaching_it():
    report, mail = mail_for(player(league=29), [week_entry(29)])
    assert "precies de lat die we voor TH17 legden" in body(mail)
    assert "dezelfde league als vorige week" in body(mail)
    assert report["videos"] == []


def test_below_benchmark_gets_a_push_and_at_most_three_videos():
    report, mail = mail_for(player(league=28), [week_entry(29)])
    assert "Dat is 1 league verder." in body(mail)
    assert "📉 Vorige week: Dragon League 29." in body(mail)
    assert "comeback" in mail["subject"]
    assert len(report["videos"]) == 3
    assert "https://youtu.be/0" in render_text(mail)


def test_last_week_placement_and_unplayed_attacks_are_reported():
    _, mail = mail_for(player(), [week_entry(27, weeks_ago=2), week_entry(29, placement=12)])
    assert "plaats 12 in je groep, met 640 trofeeën" in body(mail)
    assert "je speelde 12 van je 14 aanvallen. Dat zijn 2 kansen die je liet liggen." in body(mail)


def test_all_attacks_played():
    all_played = {**week_entry(30), "attackWins": 14, "attackLosses": 0}
    _, above = mail_for(player(league=30), [all_played])
    assert "Je speelde al je 14 aanvallen. Showing up" in body(above)
    _, below = mail_for(player(league=27), [all_played])
    assert "Nu de techniek nog" in body(below)


def test_opener_is_stable_for_a_player_and_week():
    _, first = mail_for(player(league=31))
    _, again = mail_for(player(league=31))
    assert first["paragraphs"][0] == again["paragraphs"][0]


def test_older_history_is_not_last_week_so_snapshot_is_used():
    snapshots = {"weeks": {}}
    record_snapshot(snapshots, {"#P1": ranked_status({**player(league=27), "name": "Speler"})},
                    datetime(2026, 10, 26, 7, tzinfo=timezone.utc))
    report, mail = mail_for(player(), [week_entry(25, weeks_ago=3)], snapshots)
    assert report["lastWeek"] is None and report["previousLeague"] == 27
    assert "📈" in body(mail) and "trofeeën" not in body(mail)


def test_no_previous_data_means_no_evolution_line():
    _, mail = mail_for(player())
    assert "Vorige week" not in body(mail) and "vorige week" not in body(mail)


def test_unranked_player():
    report, mail = mail_for(player(league=0))
    assert "Je hebt deze week nog geen ranked league." in body(mail)
    assert report["videos"]


def test_html_escapes_names_and_has_unsubscribe_link():
    _, mail = mail_for(player(name="<b>Bob</b>"))
    page = render_html(mail)
    assert "<b>Bob</b>" not in page and "&lt;b&gt;Bob&lt;/b&gt;" in page
    assert 'href="mailto:cocanalysis686@gmail.com?subject=Uitschrijven%20%23P1"' in page
    assert 'Uitschrijven #P1' in render_text(mail)


def test_message_has_text_html_and_unsubscribe_header():
    from mailer import build_message
    _, mail = mail_for(player())
    msg = build_message("lid@example.com", mail["subject"], render_text(mail), render_html(mail),
                        mail["unsubscribeUrl"])
    assert msg["To"] == "lid@example.com"
    assert msg["List-Unsubscribe"] == "<mailto:cocanalysis686@gmail.com?subject=Uitschrijven%20%23P1>"
    assert [p.get_content_type() for p in msg.iter_parts()] == ["text/plain", "text/html"]
