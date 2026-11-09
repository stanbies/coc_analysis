"""Facts the weekly mail styles write about, derived once from a player's report.

The styles only turn these cases into text; none of them computes anything:
  standing: above / equal / below the expected league for the Town Hall,
            unranked (no league this week) or none (no expectation for the TH)
  trend:    up / same / down compared with last week, None without last week's league
  attacks:  all / some / none played last week, None without last week's results
"""

from dataclasses import dataclass

from ranked import league_name


@dataclass(frozen=True)
class Facts:
    name: str
    tag: str
    clan: str
    week: str                 # ISO week of the mail, 2026-W47
    th: int
    league: int
    league_name: str
    benchmark: int | None
    benchmark_name: str | None
    standing: str
    diff: int | None          # league - benchmark
    previous: int | None
    previous_name: str | None
    trend: str | None
    change: int | None        # league - previous
    placement: int | None
    trophies: int | None
    played: int | None
    allowed: int | None
    missed: int | None
    attacks: str | None
    has_videos: bool

    @property
    def week_number(self) -> str:
        return self.week[-2:]

    @property
    def good_week(self) -> bool:
        """At or above the expectation, and not a week without attacks."""
        return self.standing in ("above", "equal", "none") and self.attacks != "none"


def standing(league: int, benchmark: int | None) -> str:
    if league == 0:
        return "unranked"
    if benchmark is None:
        return "none"
    return "above" if league > benchmark else "equal" if league == benchmark else "below"


def build_facts(report: dict) -> Facts:
    league, benchmark, previous = report["league"], report["benchmark"], report["previousLeague"]
    last_week = report["lastWeek"]
    played = allowed = missed = attacks = None
    if last_week:
        played = last_week.get("attackWins", 0) + last_week.get("attackLosses", 0)
        allowed = last_week["maxBattles"]
        missed = max(allowed - played, 0)
        attacks = "none" if played == 0 else "some" if missed else "all"
    trend = None
    if previous is not None:
        trend = "up" if league > previous else "down" if league < previous else "same"
    return Facts(
        name=report["name"],
        tag=report["tag"],
        clan=report["clan"] or "de clan",
        week=report["week"],
        th=report["townHall"],
        league=league,
        league_name=league_name(league),
        benchmark=benchmark,
        benchmark_name=league_name(benchmark) if benchmark else None,
        standing=standing(league, benchmark),
        diff=league - benchmark if benchmark is not None else None,
        previous=previous,
        previous_name=league_name(previous) if previous is not None else None,
        trend=trend,
        change=league - previous if previous is not None else None,
        placement=last_week["placement"] if last_week else None,
        trophies=last_week["leagueTrophies"] if last_week else None,
        played=played,
        allowed=allowed,
        missed=missed,
        attacks=attacks,
        has_videos=bool(report["videos"]),
    )


def leagues(n: int) -> str:
    return f"{n} league" if n == 1 else f"{n} leagues"


def attacks_word(n: int) -> str:
    return f"{n} aanval" if n == 1 else f"{n} aanvallen"
