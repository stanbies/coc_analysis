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
import os
import random
import sys
import urllib.parse

from coc_api import get_clan_info, get_cwl_group, get_cwl_war, get_player_info
from config import CLAN_TAG, CWL_RECAPS_SENT_FILE, MAIL_ADDRESS, MAIL_PREVIEW_DIR
from cwl import (awards, build_season, clan_totals, is_finished, load_season, our_rounds,
                 player_stats, standings, star_ranking)
from mail_art import GOLD, MailArt
from mailer import Mailer, build_message, load_sent_log, record_sent
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


# The mail reads like a sports site's season report: the CWL is a league
# that just ended, the clan is the team and each subscriber gets a player
# analysis with football-style rapportcijfers (cwl.match_rating).

NUMBER_WORDS = ["nul", "één", "twee", "drie", "vier", "vijf", "zes", "zeven", "acht", "negen", "tien"]
STAR_WORDS = {0: "geen ster", 1: "één ster", 2: "twee sterren", 3: "drie sterren"}


def in_words(n: int) -> str:
    return NUMBER_WORDS[n] if n < len(NUMBER_WORDS) else str(n)


def join(items: list[str]) -> str:
    return items[0] if len(items) == 1 else ", ".join(items[:-1]) + " en " + items[-1]


def placing(position: int, clans: int) -> str:
    if position == 1:
        return "first"
    if position <= 3:
        return "podium"
    return "bottom" if position > clans - 2 else "middle"


def headline(recap: dict) -> str:
    clan, position = recap["clan"], recap["position"]
    status = placing(position, recap["clans"])
    if status == "first":
        return f"{clan} kampioen!"
    if status == "podium":
        return f"{'Zilver' if position == 2 else 'Brons'} voor {clan}"
    if status == "middle":
        return f"{clan} eindigt {position}e"
    return f"Zware maand voor {clan}"


def margin(r: dict) -> int:
    return r["us"]["stars"] - r["them"]["stars"]


def score(r: dict) -> str:
    return f"{r['us']['stars']}-{r['them']['stars']}"


def match_label(r: dict) -> tuple[str, str]:
    """Short verdict for the results table, coloured like the game's win/loss."""
    if r["result"] is None:
        return RESULT_LABELS[r["war"]["state"]]
    m = margin(r)
    if r["result"] == "draw":
        return ("Gelijkspel", INK)
    if r["result"] == "win":
        text = ("Zege op vernietiging" if m == 0 else "Nipte zege" if m < 10
                else "Overtuigende zege" if m < 25 else "Ruime zege")
        return (text, GREEN)
    text = "Nederlaag op vernietiging" if m == 0 else "Nipte nederlaag" if m > -10 else "Duidelijke nederlaag"
    return (text, RED)


def win_streak(rounds: list[dict]) -> tuple[int, int, int]:
    """(length, first round, last round) of the longest run of wins."""
    best, current, start = (0, 0, 0), 0, 0
    for r in rounds:
        if r["result"] == "win":
            current += 1
            start = r["round"] if current == 1 else start
            if current > best[0]:
                best = (current, start, r["round"])
        else:
            current = 0
    return best


def team_section(recap: dict) -> dict:
    clan, t, table = recap["clan"], recap["totals"], recap["standings"]
    ours = table[recap["position"] - 1]
    league = f" in {recap['league']}" if recap["league"] else ""
    rounds = recap["rounds"]
    ended = [r for r in rounds if r["result"]]

    if recap["position"] == 1 and len(table) > 1:
        gap = ours["stars"] - table[1]["stars"]
        standing = (f"pas na de vernietiging beslist tegen {table[1]['name']}" if gap == 0 else
                    f"met {gap} {'ster' if gap == 1 else 'sterren'} voorsprong op {table[1]['name']}")
        lead = f"{clan} wint de CWL-groep van {recap['month']}{league}, {standing}."
    else:
        gap = table[0]["stars"] - ours["stars"]
        behind = (f"met evenveel sterren als leider {table[0]['name']}, maar minder vernietiging" if gap == 0
                  else f"op {gap} {'ster' if gap == 1 else 'sterren'} van leider {table[0]['name']}")
        lead = (f"{clan} sluit de CWL van {recap['month']} af op plaats {recap['position']} van "
                f"{recap['clans']}{league}, {behind}.")

    record = [plural(t["wins"], "zege", "zeges")]
    if t["draws"]:
        record.append(plural(t["draws"], "gelijkspel", "gelijke spelen"))
    record.append(plural(t["losses"], "nederlaag", "nederlagen"))
    paragraphs = [f"De balans na {in_words(len(ended))} speeldagen: {join(record)}."]
    length, first, last = win_streak(ended)
    if length >= 3:
        paragraphs[-1] += (f" {clan} begon met {in_words(length)} zeges op rij." if first == 1 else
                           f" Van speeldag {first} tot {last} won {clan} {in_words(length)} keer op rij.")

    wins = [r for r in ended if r["result"] == "win"]
    losses = [r for r in ended if r["result"] == "loss"]
    biggest = max(wins, key=margin, default=None)
    story = []
    if biggest:
        story.append(f"De grootste zege kwam er op speeldag {biggest['round']} tegen {biggest['them']['name']}: "
                     f"{score(biggest)}.")
    if not losses and ended:
        story.append("En wat nog meer telt: geen enkele nederlaag.")
    elif len(losses) == 1:
        r = losses[0]
        story.append(f"Alleen tegen {r['them']['name']} ging het mis ({score(r)} op speeldag {r['round']}).")
    elif losses:
        story.append("Nederlagen waren er tegen " + join([f"{r['them']['name']} ({score(r)})" for r in losses]) + ".")
    closest = min((r for r in ended if r is not biggest), key=lambda r: abs(margin(r)), default=None)
    if closest and abs(margin(closest)) <= 5:
        how = ("pas op vernietiging beslist werd" if margin(closest) == 0 else
               "nipt gewonnen werd" if closest["result"] == "win" else "nipt verloren ging")
        story.append(f"Het spannendste duel was speeldag {closest['round']} tegen {closest['them']['name']}, "
                     f"dat met {score(closest)} {how}.")
    if story:
        paragraphs.append(" ".join(story))

    rate = round(100 * t["threeStars"] / t["attacks"]) if t["attacks"] else 0
    paragraphs.append(f"In totaal haalde de ploeg {t['stars']} sterren uit {t['attacks']} aanvallen. {rate}% "
                      "daarvan was een drie-sterrenaanval, en " +
                      (f"{plural(t['missed'], 'aanval bleef', 'aanvallen bleven')} onbenut." if t["missed"]
                       else "er bleef geen enkele aanval liggen."))
    return {
        "icon": "clan-war",
        "title": "Wedstrijdverslag",
        "lead": lead,
        "tiles": [(f"{recap['position']}/{recap['clans']}", "Plaats"),
                  (f"{t['wins']}-{t['draws']}-{t['losses']}", "W-G-V"),
                  (f"{t['stars']}{STAR}", "Sterren"),
                  (f"{rate}%", "Drie sterren")],
        "paragraphs": paragraphs,
        "tables": [
            {"title": "Speeldag per speeldag",
             "headers": ["Speeldag", "Tegenstander", "Uitslag", ""],
             "rows": [[str(r["round"]), r["them"]["name"],
                       f"{r['us']['stars']}{STAR} - {r['them']['stars']}{STAR}", match_label(r)]
                      for r in rounds]},
            {"title": "Eindklassement",
             "headers": ["#", "Clan", "Sterren", "W-G-V"],
             "rows": [[str(r["position"]), r["name"], str(r["stars"]),
                       f"{r['wins']}-{r['draws']}-{r['losses']}"] for r in table],
             "highlight": recap["position"] - 1},
        ],
    }


def prizes_section(recap: dict) -> dict | None:
    a = recap["awards"]
    items = []
    if "best" in a:
        p = a["best"]
        items.append(("legend-shield", "Speler van de maand",
                      f"{p['name']}, met een gemiddeld rapportcijfer van {number(p['rating'], 1)}."))
    if "mvp" in a:
        p = a["mvp"]
        items.append(("star", "Topschutter", f"{p['name']}, met {p['stars']} sterren uit "
                                             f"{plural(len(p['attacks']), 'aanval', 'aanvallen')}."))
    if "perfect" in a:
        names = join([p["name"] for p in a["perfect"]])
        items.append(("three-stars", "Foutloos", f"{names}: bij elke aanval drie sterren."))
    if "daredevil" in a:
        p = a["daredevil"]
        items.append(("barbarian", "Durfal", f"{p['name']}, met {p['hitUpStars']} sterren tegen hogere Town Halls."))
    if "wall" in a:
        p = a["wall"]
        average = sum(d["stars"] for d in p["defenses"]) / len(p["defenses"])
        items.append(("standard-shield", "De Muur", f"{p['name']}, {len(p['defenses'])} keer aangevallen en "
                                                    f"gemiddeld maar {number(average, 1)} ster tegen."))
    return {"icon": "crown", "title": "Prijzen van de maand", "items": items} if items else None


def rating_cell(rating: float | None) -> tuple[str, str] | str:
    if rating is None:
        return "-"
    return (number(rating, 1), GREEN if rating >= 7.5 else RED if rating < 5.5 else INK)


def verdict(name: str, rating: float) -> str:
    if rating >= 8.5:
        return "Wereldklasse. Een sterkhouder waar elke ploeg van droomt."
    if rating >= 7.5:
        return "Sterke competitie. Een vaste waarde in de ploeg."
    if rating >= 6.5:
        return "Degelijk. Geen uitschieters, wel betrouwbaar."
    if rating >= 5.5:
        return f"Wisselvallig. Dat er meer in zit, bewees {name} zelf op de beste speeldagen."
    return "Een competitie om snel te vergeten. Volgende maand revanche."


def player_section(recap: dict, tag: str, name: str) -> dict:
    player = recap["players"].get(tag)
    section = {"icon": "barbarian-king", "title": "Spelersanalyse", "subtitle": name, "personal": True}
    if not player or not player["lineups"]:
        if tag in recap["roster"]:
            text = [f"{name} zat deze maand in de selectie, maar kwam op geen enkele speeldag van de bank.",
                    "Volgende maand ligt er een nieuwe kans om een basisplaats af te dwingen."]
        else:
            text = [f"{name} stond deze CWL niet op het wedstrijdblad.",
                    "Zin om er volgende maand bij te zijn? Laat het de leiding weten."]
        return {**section, "paragraphs": text}

    rounds = len(recap["rounds"])
    attacks, matches = player["attacks"], player["matches"]
    rated = [m for m in matches if m["rating"] is not None]
    positions = [m["position"] for m in matches if m["position"]]
    team_size = recap["rounds"][0]["war"].get("teamSize") or 1
    average_position = sum(positions) / len(positions)
    where = ("bovenaan in" if average_position <= team_size / 3 else
             "in het midden van" if average_position <= 2 * team_size / 3 else "onderaan in")
    paragraphs = [
        (f"{name} (TH{player['th']}) stond op alle {in_words(rounds)} speeldagen in de basis"
         if player["lineups"] == rounds else
         f"{name} (TH{player['th']}) kreeg op {player['lineups']} van de {rounds} speeldagen een basisplaats")
        + f", meestal {where} de line-up (gemiddeld positie {round(average_position)})."]

    if len(attacks) >= 3 and player["threeStars"] == len(attacks) and not player["missed"]:
        paragraphs.append(f"Elke aanval was raak: {in_words(len(attacks))} keer drie sterren. "
                          "Een foutloze competitie.")
    elif rated:
        best = max(rated, key=lambda m: (m["rating"], -m["round"]))
        worst = min(rated, key=lambda m: (m["rating"], m["round"]))
        a = best["attack"]
        form = [f"Hoogtepunt was speeldag {best['round']} tegen {best['opponent']}: {STAR_WORDS[a['stars']]} "
                f"op een TH{a['defenderTh']}, goed voor een {number(best['rating'], 1)}."]
        if worst["rating"] <= best["rating"] - 1:
            if worst["missed"]:
                form.append(f"Het dieptepunt: op speeldag {worst['round']} tegen {worst['opponent']} "
                            "bleef de aanval liggen.")
            else:
                w = worst["attack"]
                form.append(f"Minder ging het op speeldag {worst['round']} tegen {worst['opponent']}: "
                            f"{STAR_WORDS[w['stars']]} en {w['destruction']}%, een {number(worst['rating'], 1)}.")
        paragraphs.append(" ".join(form))
    if len(rated) >= 4:
        half = len(rated) // 2
        first = sum(m["rating"] for m in rated[:half]) / half
        second = sum(m["rating"] for m in rated[half:]) / (len(rated) - half)
        if second - first >= 1:
            paragraphs.append(f"{name} groeide in de competitie: de tweede helft was duidelijk sterker dan de eerste.")
        elif first - second >= 1:
            paragraphs.append(f"Na een sterke start zakte {name} in de slotfase wat terug.")

    if attacks:
        rank = next(i for i, p in enumerate(recap["ranking"], 1) if p["tag"] == tag)
        t = recap["totals"]
        line = (f"Met {player['stars']} sterren eindigt {name} op plaats {rank} van {len(recap['ranking'])} in "
                f"het interne klassement. Het ploeggemiddelde lag op {number(t['stars'] / t['attacks'], 2)} "
                f"sterren per aanval, {name} haalde er {number(player['stars'] / len(attacks), 2)}.")
        if player["hitUpStars"]:
            line += f" Opvallend: {player['hitUpStars']} van die sterren kwamen tegen een hogere Town Hall."
        paragraphs.append(line)
    if player["missed"]:
        paragraphs.append(f"Minpunt: {plural(player['missed'], 'keer', 'keer')} bleef de aanval liggen, "
                          "en dat kost de ploeg sterren.")
    defenses = player["defenses"]
    if defenses:
        conceded = sum(d["stars"] for d in defenses) / len(defenses)
        line = (f"Verdedigend werd de basis van {name} {len(defenses)} keer aangevallen, met gemiddeld "
                f"{number(conceded, 1)} sterren tegen.")
        if not any(d["stars"] == 3 for d in defenses):
            line += " Geen enkele tegenstander haalde er drie sterren."
        paragraphs.append(line)
    if any(p is player or (isinstance(p, list) and player in p) for p in recap["awards"].values()):
        paragraphs.append(f"{name} staat ook bij de prijzen van de maand.")

    tiles = [(f"{player['lineups']}/{rounds}", "Speeldagen"), (f"{player['stars']}{STAR}", "Sterren")]
    if attacks:
        tiles.append((number(player["stars"] / len(attacks), 2), "Per aanval"))
    if player["rating"] is not None:
        tiles.append((number(player["rating"], 1), "Rapportcijfer"))
    rows = []
    for m in matches:
        a = m["attack"]
        what = (f"{STAR * a['stars'] if a['stars'] else '0' + STAR}  {a['destruction']}% op TH{a['defenderTh']}"
                if a else "Niet aangevallen" if m["missed"] else "Nog bezig")
        rows.append([str(m["round"]), m["opponent"], what, rating_cell(m["rating"])])
    return {
        **section,
        "tiles": tiles,
        "paragraphs": paragraphs,
        "verdict": verdict(name, player["rating"]) if player["rating"] is not None else None,
        "tables": [{"title": "Rapportcijfers", "headers": ["Speeldag", "Tegenstander", "Aanval", "Cijfer"],
                    "rows": rows}],
    }


def compose_mail(recap: dict, tag: str, name: str) -> dict:
    player = recap["players"].get(tag)
    title = headline(recap)
    subject = f"{title} | Eindverslag CWL {recap['month']}"
    if player and player["rating"] is not None:
        subject += f" | Jouw cijfer: {number(player['rating'], 1)}"
    sections = [team_section(recap), prizes_section(recap), player_section(recap, tag, name)]
    unsubscribe = f"Uitschrijven {tag}"
    return {
        "subject": subject,
        "kicker": f"CWL {recap['league']}" if recap["league"] else "Clan War League",
        "banner": title,
        "bannerSub": f"Eindverslag · {recap['month']}",
        "greeting": f"Hoi {name},",
        "intro": [f"De Clan War League van {recap['month']} zit erop. Hieronder het eindverslag van de ploeg, "
                  + ("en daarna de analyse van jouw competitie." if player and player["lineups"]
                     else "en daarna een woordje over jou.")],
        "sections": [s for s in sections if s],
        "closing": ["Tot de volgende CWL!"],
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
        title = section["title"] + (f": {section['subtitle']}" if section.get("subtitle") else "")
        lines += [title.upper(), ""]
        if section.get("lead"):
            lines += [section["lead"], ""]
        if section.get("tiles"):
            lines += [plain(" · ".join(f"{label}: {value}" for value, label in section["tiles"])), ""]
        for paragraph in section.get("paragraphs", []):
            lines += [paragraph, ""]
        if section.get("verdict"):
            lines += [f"Ons oordeel: {section['verdict']}", ""]
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
        if section.get("subtitle"):
            inner.append(f'<p style="margin:8px 0 0;font-size:18px;font-weight:bold;color:{INK}">'
                         f'{e(section["subtitle"])}</p>')
        if section.get("lead"):
            inner.append(f'<p style="font-size:17px;font-weight:bold;line-height:1.4">{e(section["lead"])}</p>')
        if section.get("tiles"):
            inner.append(tiles(section["tiles"]))
        inner += [f"<p>{e(p)}</p>" for p in section.get("paragraphs", [])]
        if section.get("verdict"):
            inner.append(f'<p style="background:#fffaf0;border-left:5px solid {GOLD_DARK};padding:10px 12px;'
                         f'font-size:16px"><b>Ons oordeel:</b> {e(section["verdict"])}</p>')
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
              f'<td><div>{art.text(mail["kicker"], 14, GOLD)}</div>'
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
        if season["season"] in load_sent_log(CWL_RECAPS_SENT_FILE) and not args.resend:
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
            record_sent(CWL_RECAPS_SENT_FILE, season["season"])

    if missing:
        print(f"::warning::No mail for {len(missing)} player(s) that couldn't be fetched: {', '.join(missing)}")
    if failed:
        print(f"::error::{len(failed)} mail(s) failed to send: {', '.join(failed)}")
    if failed or (missing and not mails):
        sys.exit(1)


if __name__ == "__main__":
    main()
