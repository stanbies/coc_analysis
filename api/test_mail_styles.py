"""Tests for the rotating weekly mail styles. Run: pytest api/"""

import itertools
from datetime import timedelta

import pytest

from mail_styles import STARTDATUM, STIJLEN, WEKEN_PER_STIJL, build_facts, compose, linkedin, style_for_week
from mail_styles.common import leagues
from weekly_mail import compose_mail, render_html, render_text

BENCHMARK = 29


def week_of(day) -> str:
    year, week, _ = day.isocalendar()
    return f"{year}-W{week:02d}"


def report(standing="above", trend="up", attacks="some", name="Speler", videos=False):
    league = {"above": 31, "equal": 29, "below": 26, "unranked": 0, "none": 30}[standing]
    previous = {"up": league - 2, "same": league, "down": league + 3, None: None}[trend]
    last_week = None
    if attacks:
        played = {"all": 14, "some": 11, "none": 0}[attacks]
        last_week = {"placement": 61, "leagueTrophies": 623, "attackWins": played, "attackLosses": 0,
                     "maxBattles": 14}
    return {"tag": "#2PP", "name": name, "clan": "Zwegerneet", "week": "2026-W47", "townHall": 17,
            "league": league, "benchmark": None if standing == "none" else BENCHMARK,
            "previousLeague": previous, "lastWeek": last_week,
            "videos": [{"title": "Video", "url": "https://youtu.be/x"}] if videos else []}


def test_rotation_starts_at_the_start_date_and_wraps():
    assert style_for_week(week_of(STARTDATUM)).__name__.endswith("sporza")
    for weeks in range(30):
        expected = STIJLEN[(weeks // WEKEN_PER_STIJL) % len(STIJLEN)]
        assert style_for_week(week_of(STARTDATUM + timedelta(weeks=weeks))) is expected
    assert style_for_week(week_of(STARTDATUM + timedelta(weeks=len(STIJLEN)))) is STIJLEN[0]
    assert style_for_week(week_of(STARTDATUM - timedelta(weeks=1))) is STIJLEN[-1]


def test_rotation_continues_over_the_turn_of_the_year():
    # 2026-12-28 (2026-W53) and 2027-01-04 (2027-W01) are consecutive Mondays
    last, first = style_for_week("2026-W53"), style_for_week("2027-W01")
    assert STIJLEN.index(first) == (STIJLEN.index(last) + 1) % len(STIJLEN)


def test_every_style_has_a_title_and_linkedin_keeps_its_own():
    assert len(STIJLEN) == 9 and all(style.TITLE for style in STIJLEN)
    assert linkedin.TITLE == "Chief Motivation Officers"


NAMES = [f"Speler {i}" for i in range(12)]
CASES = list(itertools.product(["above", "equal", "below", "unranked", "none"],
                               ["up", "same", "down", None],
                               ["all", "some", "none", None]))


@pytest.mark.parametrize("style", STIJLEN, ids=lambda s: s.__name__.split(".")[-1])
def test_every_case_keeps_all_numbers_and_has_no_long_dashes(style):
    # Several names, so every variant of every sentence gets picked at least once
    for (standing, trend, attacks), name in itertools.product(CASES, NAMES):
        r = report(standing, trend, attacks, name=name, videos=standing in ("below", "unranked"))
        f = build_facts(r)
        mail = compose_mail(r, style=style)
        text = (mail["subject"] + "\n" + render_text(mail)).lower()
        case = f"{style.__name__} {standing}/{trend}/{attacks} {name}"
        assert "–" not in text and "—" not in text, case
        assert "17" in text, case
        if standing != "unranked":
            assert f.league_name.lower() in text, case
        if standing != "none":
            assert f.benchmark_name.lower() in text, case
        if standing in ("above", "below"):
            assert leagues(abs(f.diff)) in text, case
        if trend in ("up", "down"):
            assert f.previous_name.lower() in text, case
            # The original LinkedIn text names last week's league but not the difference
            assert style is linkedin or leagues(abs(f.change)) in text, case
        if attacks:
            assert "61" in text and "623" in text and str(f.played) in text and "14" in text, case
        if attacks == "some":
            assert str(f.missed) in text, case
        assert style.TITLE.lower() in text and "de leiding van zwegerneet" in text, case
        assert render_html(mail).count("<p>") >= 3, case


def test_same_player_and_week_give_the_same_text_other_players_vary():
    style = STIJLEN[0]
    first = compose(build_facts(report(name="oli")), style)
    assert compose(build_facts(report(name="oli")), style) == first
    others = {str(compose(build_facts(report(name=f"Speler {i}")), style)) for i in range(10)}
    assert len(others) > 1


def test_civil_servant_letter_ends_without_signature():
    from mail_styles import ambtenaar
    mail = compose_mail(report(), style=ambtenaar)
    assert mail["signoff"].startswith("Hoogachtend,\nDe leiding van Zwegerneet\nDienst Ranked Aangelegenheden")
    assert mail["signoff"].endswith("Deze brief werd automatisch opgemaakt en is geldig zonder handtekening.")
    assert "Dossiernummer: RA/2026-W47/2PP" in render_text(mail)


def test_bad_week_is_sold_for_parts():
    from mail_styles import tweedehands
    assert "voor onderdelen" in compose_mail(report("below"), style=tweedehands)["subject"]
    assert "voor onderdelen" not in compose_mail(report("above", attacks="all"), style=tweedehands)["subject"]
