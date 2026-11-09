"""Tests for the CWL archive, standings and recap mail. Run: pytest api/"""

from cwl import build_season, is_finished, match_rating, player_stats, standings
from cwl_mail import build_recap, compose_mail, render_html, render_text
from mail_art import MailArt
from mailer import build_message

US, A, B = "#US", "#A", "#B"


def member(tag, position, th=17, attacks=(), name=None):
    return {"tag": tag, "name": name or tag.lstrip("#"), "townhallLevel": th, "mapPosition": position,
            "attacks": [{"attackerTag": tag, "defenderTag": d, "stars": s, "destructionPercentage": p}
                        for d, s, p in attacks]}


def side(tag, stars, destruction, members=()):
    return {"tag": tag, "name": tag.lstrip("#"), "stars": stars, "destructionPercentage": destruction,
            "attacks": sum(len(m["attacks"]) for m in members), "members": list(members),
            "badgeUrls": {"small": "x"}}


def war(clan, opponent, state="warEnded"):
    return {"state": state, "teamSize": 2, "startTime": "20261102T194035.000Z", "clan": clan,
            "opponent": opponent}


def season(round2_state="warEnded"):
    group = {
        "season": "2026-11", "state": "inWar",
        "clans": [{"tag": t, "name": t.lstrip("#"),
                   "members": [{"tag": f"{t}1", "name": "Een", "townHallLevel": 17},
                               {"tag": f"{t}2", "name": "Twee", "townHallLevel": 16},
                               {"tag": f"{t}3", "name": "Reserve", "townHallLevel": 15}]}
                  for t in (US, A, B)],
        "rounds": [{"warTags": ["#W1", "#0"]}, {"warTags": ["#W2", "#W3"]}],
    }
    wars = {
        # Round 1: we beat A; #US1 three-stars, #US2 misses its attack
        "#W1": war(side(US, 3, 50.0, [member("#US1", 5, attacks=[("#A2", 3, 100)]),
                                      member("#US2", 9, th=16)]),
                   side(A, 1, 40.0, [member("#A1", 1, th=17, attacks=[("#US1", 1, 60)]),
                                     member("#A2", 2, th=18)])),
        # Round 2: B beats us; we are the war's opponent side
        "#W2": war(side(B, 4, 90.0, [member("#B1", 1, attacks=[("#US2", 3, 100)]),
                                     member("#B2", 2, attacks=[("#US1", 1, 70)])]),
                   side(US, 2, 60.0, [member("#US1", 1, attacks=[("#B1", 2, 80)]),
                                      member("#US2", 2, th=16, attacks=[("#B2", 0, 30)])]),
                   state=round2_state),
        "#W3": war(side(A, 5, 100.0), side(B, 0, 0.0)),
    }
    return build_season(group, wars, US, {"name": "Crystal League I"})


def test_archive_strips_badges_and_other_clans_rosters():
    s = season()
    assert s["rounds"] == [["#W1"], ["#W2", "#W3"]]
    assert "badgeUrls" not in s["wars"]["#W1"]["clan"]
    assert "members" in s["wars"]["#W1"]["clan"] and "members" not in s["wars"]["#W3"]["clan"]


def test_a_failed_fetch_keeps_the_saved_war():
    s = season()
    group = {"season": "2026-11", "state": "ended", "clans": [], "rounds": []}
    again = build_season(group, {"#W1": None}, US, None, previous=s)
    assert again["wars"]["#W1"] == s["wars"]["#W1"] and again["warLeague"] == "Crystal League I"


def test_finished_when_all_our_rounds_ended():
    assert is_finished(season())
    assert not is_finished(season(round2_state="inWar"))


def test_standings_add_the_win_bonus():
    table = {r["tag"]: r for r in standings(season())}
    assert table[A]["stars"] == 1 + 5 + 10 and table[A]["position"] == 1
    assert table[B]["stars"] == 4 + 10 + 0 and (table[B]["wins"], table[B]["losses"]) == (1, 1)
    assert table[US]["stars"] == 3 + 10 + 2 and table[US]["position"] == 2


def test_player_stats_attacks_misses_and_defences():
    stats = player_stats(season())
    one, two = stats["#US1"], stats["#US2"]
    assert (one["stars"], one["threeStars"], one["missed"]) == (5, 1, 0)
    assert one["attacks"][0]["defenderPosition"] == 2 and one["attacks"][0]["defenderTh"] == 18
    assert one["hitUpStars"] == 3  # TH17 three-starred a TH18
    assert two["missed"] == 1 and two["lineups"] == 2
    assert [d["stars"] for d in one["defenses"]] == [1, 1]
    assert stats["#US3"]["lineups"] == 0  # in the roster, never in a lineup


def test_match_ratings_like_a_football_paper():
    stats = player_stats(season())
    one, two = stats["#US1"]["matches"], stats["#US2"]["matches"]
    # 3 stars on a higher TH (+1) and the base held (+0.5); 2 stars at 80% with the base held
    assert [m["rating"] for m in one] == [9.5, 6.5] and stats["#US1"]["rating"] == 8.0
    # missed attack; 0 stars on a higher TH and the base three-starred
    assert [m["rating"] for m in two] == [3.0, 5.0]


def test_attack_still_to_come_has_no_rating():
    stats = player_stats(season(round2_state="inWar"))
    assert stats["#US1"]["matches"][1]["rating"] == 6.5  # attacked already
    assert stats["#US2"]["matches"][1]["rating"] == 5.0
    assert match_rating({**stats["#US2"]["matches"][1], "attack": None, "missed": False}) is None


def test_mail_reads_as_a_season_report_with_player_analysis():
    recap = build_recap(season())
    mail = compose_mail(recap, "#US1", "Een")
    text = render_text(mail)
    assert mail["subject"] == "Zilver voor US | Eindverslag CWL november 2026 | Jouw cijfer: 8,0"
    assert "US sluit de CWL van november 2026 af op plaats 2 van 3 in Crystal League I, op 1 ster van leider A." in text
    assert "De balans na twee speeldagen: 1 zege en 1 nederlaag." in text
    assert "SPELERSANALYSE: EEN" in text
    assert "Een (TH17) stond op alle twee speeldagen in de basis" in text
    assert "Met 5 sterren eindigt Een op plaats 1 van 2 in het interne klassement." in text
    assert "Ons oordeel: Sterke competitie." in text
    assert "- Topschutter: US1, met 5 sterren uit 2 aanvallen." in text  # war names win over the roster


def test_mail_for_players_outside_the_lineup():
    recap = build_recap(season())
    bench = render_text(compose_mail(recap, "#US3", "Reserve"))
    assert "kwam op geen enkele speeldag van de bank" in bench and "Ons oordeel" not in bench
    assert "stond deze CWL niet op het wedstrijdblad" in render_text(compose_mail(recap, "#OTHER", "Gast"))


def test_html_escapes_names_and_highlights_our_row():
    recap = build_recap(season())
    page = render_html(compose_mail(recap, "#US1", "<b>Een</b>"))
    assert "<b>Een</b>" not in page and "&lt;b&gt;Een&lt;/b&gt;" in page
    assert 'href="mailto:cocanalysis686@gmail.com?subject=Uitschrijven%20%23US1"' in page


def test_html_uses_game_art_not_emoji_and_embeds_it():
    recap = build_recap(season())
    mail = compose_mail(recap, "#US1", "Een")
    art = MailArt()
    page = render_html(mail, art)
    assert "⭐" not in page and "🏆" not in page
    assert 'src="cid:star.png"' in page and "crown.png" in art.images
    assert all(f'src="cid:{cid}"' in page for cid in art.images)
    msg = build_message("lid@example.com", mail["subject"], render_text(mail), page,
                        mail["unsubscribeUrl"], art.images)
    related = msg.get_body(("related",))
    images = [p for p in related.iter_parts() if p.get_content_type() == "image/png"]
    assert {p["Content-ID"] for p in images} == {f"<{cid}>" for cid in art.images}
