"""Weekly personal ranked status mail.

Compares each subscriber's ranked league with the benchmark for their Town
Hall (mail_config/benchmarks.yaml) and with last week, and writes a Dutch
mail in this week's style (mail_styles/, a different style every week).
Members below the benchmark also get strategy videos for their Town Hall
(mail_config/strategies.yaml).

Last week's league and placement come from the player's league history; when
that has no entry for last week we fall back to our own ranked snapshots.

Usage:
    python api/weekly_mail.py --dry-run                # every subscriber, nothing sent
    python api/weekly_mail.py --dry-run --tag "#2PP"   # preview any player
    python api/weekly_mail.py --test-to me@x.be        # send every mail to one address
    python api/weekly_mail.py --send                   # send to the subscribers

--send mails each week once: it records the week in weekly_mails_sent.json and
skips weeks already in there (unless --resend), so a manual workflow run and a
late scheduled one can't both send. Run --send from the workflow, so that file
is the committed one. Sending only logs tags, never email addresses, since
workflow logs are visible to everyone with access to the repo.
"""

import argparse
import html
import os
import sys
import urllib.parse
from datetime import datetime, timezone

from coc_api import get_player_info, get_player_league_history
from config import (BENCHMARKS_FILE, MAIL_ADDRESS, MAIL_PREVIEW_DIR, STRATEGIES_FILE,
                    WEEKLY_MAILS_SENT_FILE)
from mail_styles import build_facts, compose, style_for_week
from mailer import Mailer, build_message, load_sent_log, record_sent
from ranked import (LEAGUE_TIER_BASE_ID, for_town_hall, league_number, load_snapshots, load_th_table,
                    previous_status, week_key)
from subscribers import load_subscribers, normalize_tag

WEEK_SECONDS = 7 * 24 * 3600
MAX_VIDEOS = 3


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


def compose_mail(report: dict, style=None) -> dict:
    """Subject and paragraphs in this week's style (mail_styles); rendered to text and HTML below."""
    facts = build_facts(report)
    style = style or style_for_week(report["week"])
    text = compose(facts, style)
    signoff = f"{text['sign']}\nDe leiding van {facts.clan}\n{style.TITLE}"
    if text.get("after"):
        signoff += f"\n\n{text['after']}"
    unsubscribe = f"Uitschrijven {report['tag']}"
    return {
        "subject": f"Week {facts.week_number} · {text['subject']}",
        "greeting": text["greeting"],
        "paragraphs": text["paragraphs"],
        "videosIntro": text["videos_intro"],
        "videos": report["videos"],
        "closing": text["closing"],
        "signoff": signoff,
        "unsubscribeSubject": unsubscribe,
        "unsubscribeUrl": f"mailto:{MAIL_ADDRESS}?subject={urllib.parse.quote(unsubscribe)}",
        "footer": f"Je krijgt deze mail omdat je je inschreef voor de wekelijkse ranked-update "
                  f"van {facts.clan}.",
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
    parser.add_argument("--resend", action="store_true", help="with --send: also if this week was sent")
    args = parser.parse_args()

    if args.tag and args.send:
        parser.error("--tag only works with --dry-run or --test-to")
    now = datetime.now(timezone.utc)
    if args.send and week_key(now) in load_sent_log(WEEKLY_MAILS_SENT_FILE) and not args.resend:
        print(f"The mail for {week_key(now)} was already sent; nothing to do.")
        return
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
        # Recorded even after partial failures, so a rerun never mails everyone twice
        if args.send and len(failed) < len(mails):
            record_sent(WEEKLY_MAILS_SENT_FILE, week_key(now))

    if missing:
        print(f"::warning::No mail for {len(missing)} player(s) that couldn't be fetched: {', '.join(missing)}")
    if failed:
        print(f"::error::{len(failed)} mail(s) failed to send: {', '.join(failed)}")
    if failed or (missing and not mails):
        sys.exit(1)


if __name__ == "__main__":
    main()
