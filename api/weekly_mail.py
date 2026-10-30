"""Weekly personal ranked status mail.

Compares each subscriber's ranked league with the benchmark for their Town
Hall (mail_config/benchmarks.yaml) and with last week, and writes a Dutch
mail. Members below the benchmark also get strategy videos for their Town
Hall (mail_config/strategies.yaml).

Last week's league and placement come from the player's league history; when
that has no entry for last week we fall back to our own ranked snapshots.

Usage:
    python api/weekly_mail.py --dry-run                # every subscriber, nothing sent
    python api/weekly_mail.py --dry-run --tag "#2PP"   # preview any player
    python api/weekly_mail.py --test-to me@x.be        # send every mail to one address
    python api/weekly_mail.py --send                   # send to the subscribers

Sending only logs tags, never email addresses, since workflow logs are visible
to everyone with access to the repo.
"""

import argparse
import html
import os
import random
import sys
import urllib.parse
from datetime import datetime, timezone

import yaml

from coc_api import get_player_info, get_player_league_history
from config import BENCHMARKS_FILE, MAIL_ADDRESS, MAIL_PREVIEW_DIR, STRATEGIES_FILE
from mailer import Mailer, build_message
from ranked import (LEAGUE_TIER_BASE_ID, league_name, league_number, load_snapshots,
                    previous_status, week_key)
from subscribers import load_subscribers, normalize_tag

WEEK_SECONDS = 7 * 24 * 3600
MAX_VIDEOS = 3


def load_th_table(path: str) -> dict:
    """Load a {town hall: value} YAML table."""
    with open(path, "r", encoding="utf-8") as f:
        table = yaml.safe_load(f) or {}
    if not all(isinstance(th, int) for th in table):
        raise ValueError(f"{path}: keys must be Town Hall numbers")
    return table


def for_town_hall(table: dict, th: int):
    """Value for this Town Hall, or for the closest lower one listed."""
    lower = [level for level in table if level <= th]
    return table[max(lower)] if lower else None


def last_week_entry(player: dict, history: list) -> dict | None:
    """League history entry of the tournament week before the current one."""
    current = player.get("currentLeagueSeasonId")
    if not current:
        return None
    return next((e for e in history if e.get("leagueSeasonId") == current - WEEK_SECONDS), None)


def build_report(player: dict, history: list, snapshots: dict, benchmarks: dict,
                 strategies: dict, now: datetime) -> dict:
    """Everything the mail says about one player, as data."""
    th = player.get("townHallLevel", 0)
    league = league_number(player.get("leagueTier"))
    benchmark = for_town_hall(benchmarks, th)

    last_week = last_week_entry(player, history)
    if last_week:
        previous = last_week["leagueTierId"] - LEAGUE_TIER_BASE_ID
    else:
        _, snapshot = previous_status(snapshots, player["tag"], week_key(now))
        previous = snapshot["league"] if snapshot else None

    below = benchmark is not None and league < benchmark
    return {
        "tag": player["tag"],
        "name": player.get("name", ""),
        "clan": (player.get("clan") or {}).get("name"),
        "week": week_key(now),
        "townHall": th,
        "league": league,
        "benchmark": benchmark,
        "previousLeague": previous,
        "lastWeek": last_week,
        "videos": (for_town_hall(strategies, th) or [])[:MAX_VIDEOS] if below else [],
    }


def leagues(n: int) -> str:
    return f"{n} league" if n == 1 else f"{n} leagues"


# The mail is written as a LinkedIn-style motivational post: a hook, short
# lines, a "lesson" and hashtags. Openers rotate per player and week.
OPENERS = {
    "above": ["Ik wil even iets met je delen.",
              "Iedereen wil resultaten. Weinigen leveren ze.",
              "Soms moet je even stilstaan bij hoe ver je al gekomen bent."],
    "equal": ["Er zijn twee soorten spelers: zij die over hun doelen praten, en zij die ze halen.",
              "Een doel zonder plan is een wens. Jij had een plan.",
              "Consistentie verslaat talent. Elke week opnieuw."],
    "below": ["Elke legende begon ergens.",
              "Succes is geen rechte lijn. Het is een trap.",
              "Ik ga eerlijk met je zijn, want dat verdien je."],
    "unranked": ["Het moeilijkste aan elke reis is de eerste stap.",
                 "Elke grote carrière begon met een eerste aanval."],
}

SUBJECTS = {
    "above": "{league}. Boven verwachting. Laat dat even bezinken. 🚀",
    "equal": "{league}. Doel gehaald. 🎯",
    "below": "{league}. Dit is waar je comeback begint. 💪",
    "unranked": "Je ranked-verhaal moet nog beginnen. 🌱",
    "none": "{league}. Je wekelijkse ranked-update. 📊",
}


def standing(league: int, benchmark: int | None) -> str:
    if league == 0:
        return "unranked"
    if benchmark is None:
        return "none"
    return "above" if league > benchmark else "equal" if league == benchmark else "below"


def compose_mail(report: dict) -> dict:
    """Subject and paragraphs of the mail; rendered to text and HTML below."""
    th, league, benchmark = report["townHall"], report["league"], report["benchmark"]
    current = league_name(league)
    target = league_name(benchmark) if benchmark else None
    status = standing(league, benchmark)
    # Same opener on reruns, a different one most weeks
    rng = random.Random(f"{report['tag']}{report['week']}")
    paragraphs = [rng.choice(OPENERS[status])] if status in OPENERS else []

    if status == "unranked":
        paragraphs.append("Je hebt deze week nog geen ranked league."
                          + (f" Voor TH{th} mikken we op minstens {target}." if target else ""))
        paragraphs.append("De beste tijd om te beginnen was vorige week. "
                          "De op één na beste tijd is vandaag. 🌱")
    elif status == "none":
        paragraphs.append(f"Je zit in {current}.")
    elif status == "above":
        paragraphs.append(f"Deze week zit je in {current}.\nVoor TH{th} verwachten we {target}.\n"
                          f"Jij zit er {leagues(league - benchmark)} boven.")
        paragraphs.append("Dat is geen geluk. Dat is discipline. 💯")
    elif status == "equal":
        paragraphs.append(f"Jij zit in {current}: precies de lat die we voor TH{th} legden. "
                          "Doel gehaald. ✅")
    else:
        paragraphs.append(f"Jij zit nu in {current}.\nVoor TH{th} mikken we op {target}. "
                          f"Dat is {leagues(benchmark - league)} verder.")
        paragraphs.append("Is dat een probleem? Nee. Dat is een kans. 🔥")

    previous = report["previousLeague"]
    if previous is not None and league > previous:
        paragraphs.append(f"📈 Vorige week: {league_name(previous)}. Nu: {current}.\n"
                          "Groei is geen toeval. Groei is een keuze.")
    elif previous is not None and league < previous:
        paragraphs.append(f"📉 Vorige week: {league_name(previous)}. Nu: {current}.\n"
                          "Een terugval is geen mislukking. Het is feedback. "
                          "En feedback is een cadeau. 🎁")
    elif previous is not None:
        paragraphs.append(f"Je staat in dezelfde league als vorige week. Een plateau is geen "
                          "stilstand: het is de aanloop naar je volgende sprong. 🧗")

    last_week = report["lastWeek"]
    if last_week:
        played = last_week.get("attackWins", 0) + last_week.get("attackLosses", 0)
        allowed = last_week["maxBattles"]
        paragraphs.append(f"Vorige week eindigde je op plaats {last_week['placement']} in je groep, "
                          f"met {last_week['leagueTrophies']} trofeeën.")
        if played < allowed:
            missed = allowed - played
            paragraphs.append(f"Hier zit je grootste groeikans: je speelde {played} van je {allowed} "
                              f"aanvallen. Dat {'is 1 kans' if missed == 1 else f'zijn {missed} kansen'} "
                              "die je liet liggen.\nJe mist 100% van de aanvallen die je niet doet. 🎯")
        elif report["videos"]:
            paragraphs.append(f"Je speelde al je {allowed} aanvallen. De inzet is er. "
                              "Nu de techniek nog. 📚")
        else:
            paragraphs.append(f"Je speelde al je {allowed} aanvallen. Showing up is half the battle. "
                              "Jij deed het volledige werk. 👏")

    if status in ("below", "unranked"):
        closing = ["Volgende week staat er een nieuwe groep klaar. De vraag is niet óf je stijgt. "
                   "De vraag is wanneer. 💭"]
    else:
        closing = ["Blijf bouwen. Blijf aanvallen. Blijf groeien.", "Agree? 👇"]
    closing.append(f"#Zwegerneet #RankedMindset #TH{th} #NeverStopAttacking")

    clan = report["clan"] or "de clan"
    unsubscribe = f"Uitschrijven {report['tag']}"
    return {
        "subject": f"Week {report['week'][-2:]} · " + SUBJECTS[status].format(league=current),
        "greeting": f"Hoi {report['name']},",
        "paragraphs": paragraphs,
        "videosIntro": f"Leren stopt nooit. Mijn tips van de week voor TH{th}: 👇",
        "videos": report["videos"],
        "closing": closing,
        "signoff": f"Groetjes,\nDe leiding van {clan}\nChief Motivation Officers",
        "unsubscribeSubject": unsubscribe,
        "unsubscribeUrl": f"mailto:{MAIL_ADDRESS}?subject={urllib.parse.quote(unsubscribe)}",
        "footer": f"Je krijgt deze mail omdat je je inschreef voor de wekelijkse ranked-update "
                  f"van {clan}.",
    }


def render_text(mail: dict) -> str:
    lines = [mail["greeting"], ""]
    for paragraph in mail["paragraphs"]:
        lines += [paragraph, ""]
    if mail["videos"]:
        lines.append(mail["videosIntro"])
        lines += [f"- {v['title']}: {v['url']}" for v in mail["videos"]]
        lines.append("")
    for paragraph in mail["closing"]:
        lines += [paragraph, ""]
    lines += [mail["signoff"], "", "--", mail["footer"],
              f"Uitschrijven: stuur een mail naar {MAIL_ADDRESS} met als onderwerp "
              f"\"{mail['unsubscribeSubject']}\"."]
    return "\n".join(lines) + "\n"


def render_html(mail: dict) -> str:
    def e(text: str) -> str:
        return html.escape(text).replace("\n", "<br>")

    parts = [f"<p>{e(mail['greeting'])}</p>"]
    parts += [f"<p>{e(p)}</p>" for p in mail["paragraphs"]]
    if mail["videos"]:
        items = "".join(f'<li><a href="{e(v["url"])}">{e(v["title"])}</a></li>' for v in mail["videos"])
        parts.append(f"<p>{e(mail['videosIntro'])}</p><ul>{items}</ul>")
    parts += [f"<p>{e(p)}</p>" for p in mail["closing"]]
    parts.append(f"<p>{e(mail['signoff'])}</p>")
    parts.append(f'<p style="color:#777;font-size:12px;border-top:1px solid #ddd;padding-top:8px">'
                 f'{e(mail["footer"])} <a href="{e(mail["unsubscribeUrl"])}">Uitschrijven</a></p>')
    body = "\n".join(parts)
    return (f'<!doctype html><html><head><meta charset="utf-8"><title>{e(mail["subject"])}</title></head>'
            f'<body style="font-family:Arial,sans-serif;font-size:15px;line-height:1.5;color:#222;'
            f'max-width:560px">\n{body}\n</body></html>\n')


def write_preview(recipient: str | None, mail: dict, tag: str):
    """Save the mail as .txt and .html and print the text version."""
    os.makedirs(MAIL_PREVIEW_DIR, exist_ok=True)
    base = os.path.join(MAIL_PREVIEW_DIR, tag.lstrip("#"))
    text = render_text(mail)
    with open(base + ".txt", "w", encoding="utf-8") as f:
        f.write(text)
    with open(base + ".html", "w", encoding="utf-8") as f:
        f.write(render_html(mail))
    print("=" * 70)
    print(f"Aan: {recipient or '(preview, geen abonnee)'}")
    print(f"Onderwerp: {mail['subject']}\n")
    print(text)


def send_mails(mails: list[tuple[str, dict, str]], test_to: str | None) -> list[str]:
    """Send (email, mail, tag) tuples; returns the tags that failed."""
    failed = []
    with Mailer() as mailer:
        for email, mail, tag in mails:
            subject = f"[TEST {tag}] {mail['subject']}" if test_to else mail["subject"]
            msg = build_message(test_to or email, subject, render_text(mail), render_html(mail),
                                mail["unsubscribeUrl"])
            try:
                mailer.send(msg)
                print(f"   ✉️  sent {tag}")
            except Exception as e:
                print(f"   ❌ {tag}: {type(e).__name__}")
                failed.append(tag)
    return failed


def main():
    parser = argparse.ArgumentParser(description="Build the weekly ranked status mails.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true", help="write previews, send nothing")
    mode.add_argument("--send", action="store_true", help="send to the subscribers")
    mode.add_argument("--test-to", metavar="EMAIL", help="send every mail to this address instead")
    parser.add_argument("--tag", action="append", help="only these players (not with --send)")
    args = parser.parse_args()

    if args.tag and args.send:
        parser.error("--tag only works with --dry-run or --test-to")
    if args.tag:
        recipients = [{"email": None, "tag": normalize_tag(t)} for t in args.tag]
    else:
        recipients = load_subscribers()
    if not recipients:
        print("No subscribers (set mail_subscribers or create api/subscribers.csv).")
        return

    benchmarks = load_th_table(BENCHMARKS_FILE)
    strategies = load_th_table(STRATEGIES_FILE)
    snapshots = load_snapshots()
    now = datetime.now(timezone.utc)

    mails, missing = [], []
    for recipient in recipients:
        player = get_player_info(recipient["tag"])
        if not player:
            missing.append(recipient["tag"])
            continue
        history = get_player_league_history(recipient["tag"]) or []
        report = build_report(player, history, snapshots, benchmarks, strategies, now)
        mails.append((recipient["email"], compose_mail(report), player["tag"]))

    if args.dry_run:
        for email, mail, tag in mails:
            write_preview(email, mail, tag)
        print(f"📝 {len(mails)} mail(s) written to {MAIL_PREVIEW_DIR}")
        failed = []
    else:
        failed = send_mails(mails, args.test_to)
        print(f"✉️  {len(mails) - len(failed)} of {len(mails)} mail(s) sent")

    if missing:
        print(f"::warning::No mail for {len(missing)} player(s) that couldn't be fetched: {', '.join(missing)}")
    if failed:
        print(f"::error::{len(failed)} mail(s) failed to send: {', '.join(failed)}")
    if failed or (missing and not mails):
        sys.exit(1)


if __name__ == "__main__":
    main()
