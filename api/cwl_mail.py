"""CWL recap mail: the clan's league in numbers plus a personal part per subscriber.

Uses the live CWL group while the API still returns it, otherwise the newest
saved season (cwl/<season>.json, written by the scraper). Same subscribers as
the weekly ranked mail. The HTML uses Clash of Clans art (mail_art.py) instead
of emoji: fan kit icons, and titles and numbers in the Clash font.

Usage:
    python api/cwl_mail.py --dry-run                   # every subscriber, nothing sent
    python api/cwl_mail.py --dry-run --tag "#2PP"      # preview any player
    python api/cwl_mail.py --dry-run --season 2026-11-01
    python api/cwl_mail.py --test-to me@x.be           # send every mail to one address
    python api/cwl_mail.py --send                      # send to the subscribers

--send only sends a finished season, once: it records the season in
cwl/recaps_sent.json and skips seasons already in there (unless --resend), so
the workflow can run it every day. Run --send from the workflow, so that file
is the committed one. Sending logs tags only, never addresses.
"""

import argparse
import html
import json
import os
import random
import sys
import urllib.parse

from coc_api import get_clan_info, get_cwl_group, get_cwl_war, get_player_info
from config import CLAN_TAG, CWL_RECAPS_SENT_FILE, MAIL_ADDRESS, MAIL_PREVIEW_DIR
from cwl import (awards, build_season, clan_totals, is_finished, load_season, our_rounds,
                 player_stats, standings, star_ranking)
from history import utc_now
from mail_art import GOLD, MailArt
from mailer import Mailer, build_message
from subscribers import load_subscribers, normalize_tag

MONTHS = ["januari", "februari", "maart", "april", "mei", "juni", "juli", "augustus",
          "september", "oktober", "november", "december"]

# Colours from the dashboard's theme.css
OUTLINE, INK, WOOD, PARCHMENT, PARCHMENT_DARK = "#1b1208", "#4a2f17", "#8a5528", "#f6eacb", "#dcc597"
GREEN, RED, STONE, GOLD_DARK = "#3f8f1c", "#b3261e", "#58626e", "#e2900c"
RESULT_LABELS = {"win": ("Gewonnen", GREEN), "draw": ("Gelijk", INK), "loss": ("Verloren", RED),
                 "inWar": ("Bezig", STONE), "preparation": ("Voorbereiding", STONE)}

# In table cells and tiles this marks a star icon (an asterisk in the text version)
STAR = "⭐"


def month_name(season: str) -> str:
    """'2026-11-01' or '2026-11' -> 'november 2026'."""
    year, month = season.split("-")[:2]
    return f"{MONTHS[int(month) - 1]} {year}"


def number(value: float, decimals: int = 0) -> str:
    """Dutch decimal comma."""
    return f"{value:.{decimals}f}".replace(".", ",")


def plural(n: int, one: str, many: str) -> str:
    return f"{n} {one if n == 1 else many}"


def build_recap(season: dict) -> dict:
    """Everything the mails share: the clan's season, as data."""
    stats = player_stats(season)
    table = standings(season)
    ours = next(r for r in table if r["tag"] == season["clanTag"])
    return {
        "season": season["season"],
        "month": month_name(season["season"]),
        "clan": ours["name"],
        "league": season.get("warLeague"),
        "position": ours["position"],
        "clans": len(table),
        "standings": table,
        "rounds": our_rounds(season),
        "totals": clan_totals(season, stats),
        "awards": awards(stats),
        "ranking": star_ranking(stats),
        "players": stats,
        "roster": {m["tag"] for c in season["clans"] if c["tag"] == season["clanTag"]
                   for m in c["members"]},
    }


OPENERS = {
    "first": ["We hebben onze groep gewonnen!",
              "Eerste plaats in de groep. Wat een CWL."],
    "podium": ["Plaats {position} in de groep: we staan op het podium.",
               "Een plek op het podium, plaats {position} van {clans}."],
    "middle": ["Een CWL met mooie overwinningen en een paar lastige oorlogen.",
               "Zeven oorlogen verder, en we eindigen in de middenmoot."],
    "bottom": ["Deze CWL liep niet zoals we wilden.",
               "Geen makkelijke CWL deze keer."],
}


def placing(position: int, clans: int) -> str:
    if position == 1:
        return "first"
    if position <= 3:
        return "podium"
    return "bottom" if position > clans - 2 else "middle"


def verdict(average: float) -> str:
    if average >= 2.7:
        return "Sterk gespeeld, dit was een topmaand."
    if average >= 2.3:
        return "Een mooie, constante CWL."
    if average >= 1.8:
        return "Degelijk, en er zitten volgende keer nog sterren in."
    return "Volgende maand beter: daar zitten zeker nog sterren in."


def clan_section(recap: dict) -> dict:
    t = recap["totals"]
    league = f" in {recap['league']}" if recap["league"] else ""
    rate = round(100 * t["threeStars"] / t["attacks"]) if t["attacks"] else 0
    paragraphs = [
        f"We eindigden op plaats {recap['position']} van {recap['clans']}{league}, met "
        f"{plural(t['wins'], 'overwinning', 'overwinningen')}, {t['draws']} gelijkspel en "
        f"{plural(t['losses'], 'nederlaag', 'nederlagen')}.",
        f"Samen haalden we {t['stars']} sterren uit {t['attacks']} van de {t['allowed']} aanvallen. "
        f"{t['threeStars']} daarvan waren drie sterren, dat is {rate}%.",
    ]
    if t["missed"]:
        paragraphs.append(f"{t['perfectAttendance']} van de {t['players']} spelers in de line-up deden "
                          f"al hun aanvallen. {plural(t['missed'], 'aanval bleef', 'aanvallen bleven')} "
                          "liggen, daar zitten volgende keer makkelijke sterren in.")
    else:
        paragraphs.append("Iedereen in de line-up deed al zijn aanvallen. Top!")
    return {
        "icon": "clan-war",
        "title": f"{recap['clan']} in {recap['month']}",
        "tiles": [(f"{recap['position']}/{recap['clans']}", "Plaats"),
                  (f"{t['wins']}-{t['draws']}-{t['losses']}", "W-G-V"),
                  (f"{t['stars']}{STAR}", "Sterren"),
                  (f"{rate}%", "Drie sterren")],
        "paragraphs": paragraphs,
        "tables": [
            {"title": "Ronde per ronde",
             "headers": ["Ronde", "Tegenstander", "Score", "Uitslag"],
             "rows": [[str(r["round"]), r["them"]["name"],
                       f"{r['us']['stars']}{STAR} - {r['them']['stars']}{STAR}",
                       RESULT_LABELS[r["result"] or r["war"]["state"]]]
                      for r in recap["rounds"]]},
            {"title": "Eindstand van de groep",
             "headers": ["#", "Clan", "Sterren", "W-G-V"],
             "rows": [[str(r["position"]), r["name"], str(r["stars"]),
                       f"{r['wins']}-{r['draws']}-{r['losses']}"] for r in recap["standings"]],
             "highlight": recap["position"] - 1},
        ],
    }


def awards_section(recap: dict) -> dict | None:
    a = recap["awards"]
    items = []
    if "mvp" in a:
        p = a["mvp"]
        items.append(("crown", "MVP", f"{p['name']}, met {p['stars']} sterren uit "
                                      f"{plural(len(p['attacks']), 'aanval', 'aanvallen')}."))
    if "perfect" in a:
        names = ", ".join(p["name"] for p in a["perfect"])
        items.append(("three-stars", "Altijd drie sterren", f"{names}. Geen enkele aanval onder de drie."))
    if "daredevil" in a:
        p = a["daredevil"]
        items.append(("barbarian", "Durfal", f"{p['name']}, met {p['hitUpStars']} sterren tegen hogere "
                                             "Town Halls."))
    if "wall" in a:
        p = a["wall"]
        average = sum(d["stars"] for d in p["defenses"]) / len(p["defenses"])
        items.append(("standard-shield", "De Muur", f"{p['name']}. {len(p['defenses'])} keer aangevallen "
                                                    f"en gemiddeld maar {number(average, 1)} ster weggegeven."))
    return {"icon": "legend-shield", "title": "Hall of Fame", "items": items} if items else None


def personal_section(recap: dict, tag: str) -> dict:
    player = recap["players"].get(tag)
    section = {"icon": "barbarian-king", "title": "Jouw CWL", "personal": True}
    if not player or not player["lineups"]:
        if tag in recap["roster"]:
            text = "Je stond deze keer in de selectie, maar niet in de line-up. Volgende maand is er een nieuwe kans."
        else:
            text = "Je deed deze CWL niet mee. Wil je er volgende maand bij zijn? Laat het de leiding weten."
        return {**section, "paragraphs": [text]}

    attacks = player["attacks"]
    rounds = len(recap["rounds"])
    paragraphs = []
    tiles = [(f"{player['lineups']}/{rounds}", "Line-ups"), (f"{player['stars']}{STAR}", "Sterren")]
    if attacks:
        average = player["stars"] / len(attacks)
        destruction = player["destructionTotal"] / len(attacks)
        rank = next(i for i, p in enumerate(recap["ranking"], 1) if p["tag"] == tag)
        t = recap["totals"]
        clan_average = t["stars"] / t["attacks"]
        tiles += [(number(average, 2), "Per aanval"), (f"#{rank}", "In de clan")]
        paragraphs.append(f"Je stond in {player['lineups']} van de {rounds} line-ups en deed "
                          f"{plural(len(attacks), 'aanval', 'aanvallen')}: {player['stars']} sterren, "
                          f"gemiddeld {number(average, 2)} per aanval en {number(destruction)}% vernietiging.")
        comparison = ("daar zat je boven" if average > clan_average else
                      "daar zat je net onder" if average < clan_average else "precies evenveel")
        paragraphs.append(f"Daarmee sta je #{rank} van {len(recap['ranking'])} in de clan. Het clangemiddelde "
                          f"was {number(clan_average, 2)} sterren per aanval, {comparison}.")
    if player["missed"]:
        paragraphs.append(f"{plural(player['missed'], 'keer', 'keer')} heb je je aanval niet gedaan. "
                          "Volgende keer alles pakken!")
    defenses = player["defenses"]
    if defenses:
        conceded = sum(d["stars"] for d in defenses) / len(defenses)
        line = (f"Je basis werd {len(defenses)} keer aangevallen en gaf gemiddeld "
                f"{number(conceded, 1)} sterren weg.")
        if not any(d["stars"] == 3 for d in defenses):
            line += " Niemand kreeg er drie sterren op."
        paragraphs.append(line)
    if any(p is player or (isinstance(p, list) and player in p) for p in recap["awards"].values()):
        paragraphs.append("Je staat ook in de Hall of Fame!")
    if attacks:
        paragraphs.append(verdict(player["stars"] / len(attacks)))
    return {
        **section,
        "tiles": tiles,
        "paragraphs": paragraphs,
        "tables": [{
            "title": "Jouw aanvallen",
            "headers": ["Ronde", "Tegenstander", "Doelwit", "Resultaat"],
            "rows": [[str(a["round"]), a["opponent"], f"#{a['defenderPosition']} · TH{a['defenderTh']}",
                      f"{STAR * a['stars'] if a['stars'] else '0' + STAR}  {a['destruction']}%"]
                     for a in attacks],
        }] if attacks else [],
    }


def compose_mail(recap: dict, tag: str, name: str) -> dict:
    player = recap["players"].get(tag)
    # Same opener on reruns, a different one per player and season
    rng = random.Random(f"{tag}{recap['season']}")
    status = placing(recap["position"], recap["clans"])
    league = f" in {recap['league']}" if recap["league"] else ""
    subject = f"CWL {recap['month']}: {recap['clan']} {recap['position']}e{league}"
    if player and player["attacks"]:
        subject += f", jij haalde {player['stars']} sterren"
    sections = [clan_section(recap), awards_section(recap), personal_section(recap, tag)]
    unsubscribe = f"Uitschrijven {tag}"
    return {
        "subject": subject,
        "banner": f"CWL {recap['month']}",
        "bannerSub": f"{recap['clan']} · plaats {recap['position']}{league}",
        "greeting": f"Hoi {name},",
        "intro": [rng.choice(OPENERS[status]).format(position=recap["position"], clans=recap["clans"]),
                  f"De Clan War League van {recap['month']} zit erop. Eerst hoe het de clan verging, "
                  "daarna hoe jij het deed."],
        "sections": [s for s in sections if s],
        "closing": ["Bedankt voor jullie inzet, tot de volgende CWL!"],
        "signoff": f"Groetjes,\nDe leiding van {recap['clan']}",
        "unsubscribeSubject": unsubscribe,
        "unsubscribeUrl": f"mailto:{MAIL_ADDRESS}?subject={urllib.parse.quote(unsubscribe)}",
        "footer": f"Je krijgt deze mail omdat je ingeschreven bent voor de mails van {recap['clan']}. "
                  "Dit is fan content, niet goedgekeurd door of verbonden met Supercell.",
    }


def cell_text(cell) -> str:
    return cell[0] if isinstance(cell, tuple) else cell


def render_text(mail: dict) -> str:
    def plain(text: str) -> str:
        return text.replace(STAR, "*")

    lines = [mail["greeting"], ""]
    for paragraph in mail["intro"]:
        lines += [paragraph, ""]
    for section in mail["sections"]:
        lines += [section["title"].upper(), ""]
        if section.get("tiles"):
            lines += [plain(" · ".join(f"{label}: {value}" for value, label in section["tiles"])), ""]
        for paragraph in section.get("paragraphs", []):
            lines += [paragraph, ""]
        for _, title, text in section.get("items", []):
            lines.append(f"- {title}: {text}")
        if section.get("items"):
            lines.append("")
        for table in section.get("tables", []):
            lines.append(table["title"] + ":")
            lines += ["  " + plain(" | ".join(cell_text(c) for c in row)) for row in table["rows"]]
            lines.append("")
    for paragraph in mail["closing"]:
        lines += [paragraph, ""]
    lines += [mail["signoff"], "", "--", mail["footer"],
              f"Uitschrijven: stuur een mail naar {MAIL_ADDRESS} met als onderwerp "
              f"\"{mail['unsubscribeSubject']}\"."]
    return "\n".join(lines) + "\n"


# Email clients ignore <style> blocks, so everything is inline and table-based.
def render_html(mail: dict, art: MailArt | None = None) -> str:
    """The HTML mail; the images it uses end up in art.images."""
    art = art or MailArt()

    def e(text: str) -> str:
        return (html.escape(text).replace("\n", "<br>")
                .replace(STAR, "&#8202;" + art.icon("star", 16, "ster")))

    def heading(icon: str, title: str, size: int) -> str:
        return (f'<table role="presentation" cellspacing="0" cellpadding="0"><tr>'
                f'<td style="padding-right:8px">{art.icon(icon, size + 12, "")}</td>'
                f'<td>{art.text(title, size)}</td></tr></table>')

    def tiles(items: list) -> str:
        cells = "".join(
            f'<td align="center" style="padding:10px 4px 8px;background:#fffaf0;border:2px solid '
            f'{PARCHMENT_DARK};border-radius:10px">{tile_value(value)}'
            f'<div style="font-size:12px;color:{INK};margin-top:2px">{e(label)}</div></td>'
            for value, label in items)
        return (f'<table role="presentation" width="100%" cellspacing="6" cellpadding="0" '
                f'style="margin:6px 0 8px"><tr>{cells}</tr></table>')

    def tile_value(value: str) -> str:
        if value.endswith(STAR):
            return art.text(value[:-1], 20) + "&nbsp;" + art.icon("star", 20, "sterren")
        return art.text(value, 20)

    def cell(c) -> str:
        if isinstance(c, tuple):
            return f'<span style="color:{c[1]};font-weight:bold">{e(c[0])}</span>'
        return e(c)

    def table(t: dict) -> str:
        head = "".join(f'<th align="left" style="padding:6px 8px;font-size:12px;color:{INK};'
                       f'border-bottom:2px solid {PARCHMENT_DARK}">{e(h)}</th>' for h in t["headers"])
        rows = []
        for i, row in enumerate(t["rows"]):
            style = f"background:#ffe58a;font-weight:bold" if i == t.get("highlight") else ""
            cells = "".join(f'<td style="padding:6px 8px;border-bottom:1px solid {PARCHMENT_DARK}">'
                            f'{cell(c)}</td>' for c in row)
            rows.append(f'<tr style="{style}">{cells}</tr>')
        return (f'<div style="margin:16px 0 6px">{art.text(t["title"], 15)}</div>'
                f'<table width="100%" cellspacing="0" cellpadding="0" style="border-collapse:collapse;'
                f'font-size:14px;background:#fffaf0"><tr>{head}</tr>\n' + "\n".join(rows) + "</table>")

    def awards(items: list) -> str:
        rows = "".join(f'<tr><td valign="top" style="padding:6px 10px 6px 0">{art.icon(icon, 32, title)}</td>'
                       f'<td style="padding:6px 0"><b>{e(title)}</b><br>{e(text)}</td></tr>'
                       for icon, title, text in items)
        return f'<table role="presentation" cellspacing="0" cellpadding="0">{rows}</table>'

    parts = [f"<p>{e(mail['greeting'])}</p>"] + [f"<p>{e(p)}</p>" for p in mail["intro"]]
    for section in mail["sections"]:
        border = f"3px solid {GOLD_DARK}" if section.get("personal") else f"2px solid {PARCHMENT_DARK}"
        inner = [heading(section["icon"], section["title"], 20)]
        if section.get("tiles"):
            inner.append(tiles(section["tiles"]))
        inner += [f"<p>{e(p)}</p>" for p in section.get("paragraphs", [])]
        if section.get("items"):
            inner.append(awards(section["items"]))
        inner += [table(t) for t in section.get("tables", [])]
        parts.append(f'<div style="background:{PARCHMENT};border:{border};border-radius:14px;'
                     f'padding:14px 16px;margin:18px 0">' + "\n".join(inner) + "</div>")
    parts += [f"<p>{e(p)}</p>" for p in mail["closing"]]
    parts.append(f"<p>{e(mail['signoff'])}</p>")
    parts.append(f'<p style="color:#777;font-size:12px;border-top:1px solid #ddd;padding-top:8px">'
                 f'{e(mail["footer"])} <a href="{e(mail["unsubscribeUrl"])}">Uitschrijven</a></p>')
    banner = (f'<div style="background:{WOOD};border:3px solid {OUTLINE};border-radius:16px;'
              f'padding:14px 16px;margin-bottom:8px">'
              f'<table role="presentation" cellspacing="0" cellpadding="0"><tr>'
              f'<td style="padding-right:12px">{art.icon("cwl", 64, "Clan War League")}</td>'
              f'<td><div>{art.text("Clan War League", 14, GOLD)}</div>'
              f'<div style="margin:4px 0">{art.text(mail["banner"], 26)}</div>'
              f'<div style="color:{PARCHMENT};font-size:14px">{e(mail["bannerSub"])}</div></td>'
              f'</tr></table></div>')
    body = "\n".join(parts)
    return (f'<!doctype html><html><head><meta charset="utf-8"><title>{e(mail["subject"])}</title></head>'
            f'<body style="margin:0;padding:12px;background:#efe4c8">'
            f'<div style="font-family:Arial,sans-serif;font-size:15px;line-height:1.5;color:#222;'
            f'max-width:600px;margin:0 auto">{banner}'
            f'<div style="background:#fff;padding:4px 16px 12px;border-radius:16px;'
            f'border:2px solid {PARCHMENT_DARK}">\n{body}\n'
            f'</div></div></body></html>\n')


def fetch_live_season() -> dict | None:
    """The current CWL group with all its wars, while the API still returns it."""
    group = get_cwl_group(CLAN_TAG)
    if not group or not group.get("season"):
        return None
    wars = {tag: get_cwl_war(tag) for r in group.get("rounds", []) for tag in r.get("warTags", [])
            if tag != "#0"}
    clan = get_clan_info(CLAN_TAG) or {}
    return build_season(group, wars, CLAN_TAG, clan.get("warLeague"), load_season(group["season"]))


def load_sent() -> dict:
    if os.path.exists(CWL_RECAPS_SENT_FILE):
        with open(CWL_RECAPS_SENT_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def mark_sent(season: str):
    sent = load_sent()
    sent[season] = utc_now()
    os.makedirs(os.path.dirname(CWL_RECAPS_SENT_FILE), exist_ok=True)
    with open(CWL_RECAPS_SENT_FILE, "w", encoding="utf-8") as f:
        json.dump(sent, f, indent=2)


def write_preview(recipient: str | None, mail: dict, tag: str):
    directory = os.path.join(MAIL_PREVIEW_DIR, "cwl")
    os.makedirs(directory, exist_ok=True)
    base = os.path.join(directory, tag.lstrip("#"))
    text = render_text(mail)
    with open(base + ".txt", "w", encoding="utf-8") as f:
        f.write(text)
    with open(base + ".html", "w", encoding="utf-8") as f:
        f.write(render_html(mail, MailArt(preview_dir=directory)))
    print("=" * 70)
    print(f"Aan: {recipient or '(preview, geen abonnee)'}")
    print(f"Onderwerp: {mail['subject']}\n")
    print(text)


def main():
    parser = argparse.ArgumentParser(description="Build the CWL recap mails.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true", help="write previews, send nothing")
    mode.add_argument("--send", action="store_true", help="send to the subscribers (once per season)")
    mode.add_argument("--test-to", metavar="EMAIL", help="send every mail to this address instead")
    parser.add_argument("--tag", action="append", help="only these players (not with --send)")
    parser.add_argument("--season", help="a saved season, e.g. 2026-11-01 (default: live or newest)")
    parser.add_argument("--resend", action="store_true", help="with --send: also if already sent")
    args = parser.parse_args()

    if args.tag and args.send:
        parser.error("--tag only works with --dry-run or --test-to")

    season = load_season(args.season) if args.season else (fetch_live_season() or load_season())
    if not season:
        print("No CWL season found (live or saved).")
        return
    if args.send:
        if not is_finished(season):
            print(f"CWL {season['season']} is not finished yet; nothing sent.")
            return
        if season["season"] in load_sent() and not args.resend:
            print(f"CWL {season['season']} recap was already sent; nothing to do.")
            return
    elif not is_finished(season):
        print(f"⚠️  CWL {season['season']} is still running; the recap shows the rounds so far.")

    if args.tag:
        recipients = [{"email": None, "tag": normalize_tag(t)} for t in args.tag]
    else:
        recipients = load_subscribers()
    if not recipients:
        print("No subscribers (set mail_subscribers or create api/subscribers.csv).")
        return

    recap = build_recap(season)
    mails, missing = [], []
    for recipient in recipients:
        tag = recipient["tag"]
        name = (recap["players"].get(tag) or {}).get("name")
        if not name:
            player = get_player_info(tag)
            if not player:
                missing.append(tag)
                continue
            name = player.get("name", "")
        mails.append((recipient["email"], compose_mail(recap, tag, name), tag))

    failed = []
    if args.dry_run:
        for email, mail, tag in mails:
            write_preview(email, mail, tag)
        print(f"📝 {len(mails)} mail(s) written to {os.path.join(MAIL_PREVIEW_DIR, 'cwl')}")
    else:
        with Mailer() as mailer:
            for email, mail, tag in mails:
                subject = f"[TEST {tag}] {mail['subject']}" if args.test_to else mail["subject"]
                art = MailArt()
                page = render_html(mail, art)
                msg = build_message(args.test_to or email, subject, render_text(mail), page,
                                    mail["unsubscribeUrl"], art.images)
                try:
                    mailer.send(msg)
                    print(f"   ✉️  sent {tag}")
                except Exception as e:
                    print(f"   ❌ {tag}: {type(e).__name__}")
                    failed.append(tag)
        print(f"✉️  {len(mails) - len(failed)} of {len(mails)} mail(s) sent")
        # Recorded even after partial failures, so a daily run never mails everyone twice
        if args.send and len(failed) < len(mails):
            mark_sent(season["season"])

    if missing:
        print(f"::warning::No mail for {len(missing)} player(s) that couldn't be fetched: {', '.join(missing)}")
    if failed:
        print(f"::error::{len(failed)} mail(s) failed to send: {', '.join(failed)}")
    if failed or (missing and not mails):
        sys.exit(1)


if __name__ == "__main__":
    main()
