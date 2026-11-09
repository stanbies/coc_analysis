"""Print the weekly ranked mail in all styles for three example players.

Nothing is fetched and nothing is sent: the players are made up, the
benchmarks and videos come from mail_config/. Each style is shown for the
week in which the rotation will send it.

Usage: python api/preview_weekly_styles.py
"""

from datetime import datetime, time, timedelta, timezone

from config import BENCHMARKS_FILE, STRATEGIES_FILE
from mail_styles import STARTDATUM, STIJLEN, WEKEN_PER_STIJL
from ranked import LEAGUE_TIER_BASE_ID, load_th_table
from weekly_mail import WEEK_SECONDS, build_report, compose_mail, render_text

# (description, name, TH, league now, league last week, placement, trophies, attacks played, allowed)
EXAMPLES = [
    ("boven verwachting", "oli", 18, 33, 32, 61, 623, 18, 18),
    ("op verwachting", "Lotte", 16, 27, 27, 34, 702, 14, 14),
    ("onder verwachting, aanvallen gemist", "Pieter", 17, 26, 27, 88, 214, 9, 14),
]


def example_report(example: tuple, now: datetime, benchmarks: dict, strategies: dict) -> dict:
    _, name, th, league, previous, placement, trophies, played, allowed = example
    season = int(now.timestamp())
    player = {"tag": f"#VOORBEELD{th}", "name": name, "townHallLevel": th, "clan": {"name": "Zwegerneet"},
              "leagueTier": {"id": LEAGUE_TIER_BASE_ID + league}, "currentLeagueSeasonId": season}
    last_week = {"leagueSeasonId": season - WEEK_SECONDS, "leagueTierId": LEAGUE_TIER_BASE_ID + previous,
                 "placement": placement, "leagueTrophies": trophies, "attackWins": played,
                 "attackLosses": 0, "maxBattles": allowed}
    return build_report(player, [last_week], {"weeks": {}}, benchmarks, strategies, now)


def main():
    benchmarks, strategies = load_th_table(BENCHMARKS_FILE), load_th_table(STRATEGIES_FILE)
    for number, style in enumerate(STIJLEN, 1):
        monday = STARTDATUM + timedelta(weeks=(number - 1) * WEKEN_PER_STIJL)
        now = datetime.combine(monday, time(7, 17), timezone.utc)
        print("#" * 78)
        print(f"# Stijl {number}: {style.__name__.split('.')[-1]} ({style.TITLE}), "
              f"eerst verstuurd op maandag {monday:%d-%m-%Y}")
        print("#" * 78)
        for example in EXAMPLES:
            mail = compose_mail(example_report(example, now, benchmarks, strategies), style=style)
            print(f"\n--- Voorbeeld: {example[1]}, {example[0]} ---")
            print(f"Onderwerp: {mail['subject']}\n")
            # Without the footer, which is the same in every style
            print(render_text(mail).split("\n--\n")[0].rstrip())
        print()


if __name__ == "__main__":
    main()
