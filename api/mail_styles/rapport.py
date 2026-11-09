"""School report: sections with marks out of 10 and a remark from the class teacher.

Inzet = attacks played out of allowed, scaled to 10. Resultaat = 7 at the
expected league, one point more or less per league above or below.
Evolutie = 6 for the same league as last week, two points per league up or down.
"""

from .common import Facts, attacks_word, leagues

TITLE = "De klastitularis"


def mark(value: float) -> int:
    return max(1, min(10, round(value)))


def compose(f: Facts, pick) -> dict:
    n, league, bench = f.name, f.league_name, f.benchmark_name
    lines = []

    if f.attacks:
        detail = f"{f.played} van {f.allowed} aanvallen gespeeld"
        if f.missed:
            detail += f", {f.missed} gemist"
        lines.append(f"Inzet: {mark(10 * f.played / f.allowed)}/10 ({detail})")
    else:
        lines.append("Inzet: niet beoordeeld (geen gegevens van vorige week)")

    if f.standing == "above":
        lines.append(f"Resultaat: {mark(7 + f.diff)}/10 ({league}, verwacht voor TH{f.th}: {bench}, "
                     f"{leagues(f.diff)} erboven)")
    elif f.standing == "equal":
        lines.append(f"Resultaat: 7/10 ({league}, precies wat we voor TH{f.th} verwachten)")
    elif f.standing == "below":
        lines.append(f"Resultaat: {mark(7 + f.diff)}/10 ({league}, verwacht voor TH{f.th}: {bench}, "
                     f"{leagues(-f.diff)} eronder)")
    elif f.standing == "unranked":
        expected = f", verwacht voor TH{f.th}: {bench}" if bench else ""
        lines.append(f"Resultaat: 1/10 (nog geen ranked league deze week{expected})")
    else:
        lines.append(f"Resultaat: niet beoordeeld ({league}; voor TH{f.th} is er nog geen verwachting)")

    if f.trend == "up":
        lines.append(f"Evolutie: {mark(6 + 2 * f.change)}/10 (van {f.previous_name} naar {league}, "
                     f"{leagues(f.change)} hoger)")
    elif f.trend == "same":
        lines.append(f"Evolutie: 6/10 (zelfde league als vorige week, {league})")
    elif f.trend == "down":
        lines.append(f"Evolutie: {mark(6 + 2 * f.change)}/10 (van {f.previous_name} naar {league}, "
                     f"{leagues(-f.change)} lager)")
    else:
        lines.append("Evolutie: niet beoordeeld (geen gegevens van vorige week)")

    if f.attacks:
        lines.append(f"Rangschikking in de groep: plaats {f.placement}, {f.trophies} trofeeën")

    if f.attacks == "none":
        remark = pick([f"{n} was de hele week afwezig. Graag een briefje van de ouders.",
                       f"Geen enkele taak ingediend. {n} wordt verwacht op de inhaalles."])
    elif f.attacks == "some":
        remark = pick([f"{n} kan meer, maar laat te vaak huiswerk liggen ({attacks_word(f.missed)}).",
                       f"{n} is slim genoeg, maar moet leren plannen. Er bleven {attacks_word(f.missed)} liggen."])
    elif f.standing in ("below", "unranked"):
        remark = pick([f"{n} doet goed mee, de inzet is er. Wat bijles kan geen kwaad (zie hieronder).",
                       f"{n} werkt hard. De resultaten volgen nog, met wat extra oefening."])
    elif f.standing == "above":
        remark = pick([f"{n} is een voorbeeld voor de klas. Zo verder!",
                       f"{n} presteert boven het niveau van de klas. Proficiat."])
    else:
        remark = pick([f"{n} is een rustige leerling die het huiswerk altijd maakt.",
                       f"{n} doet wat gevraagd wordt, netjes en op tijd."])

    subjects = {
        "above": "Rapport: met grote onderscheiding",
        "equal": "Rapport: geslaagd",
        "below": "Rapport: werkpunten voor volgende week",
        "unranked": "Rapport: afwezig",
        "none": "Rapport: geslaagd",
    }
    return {
        "subject": f"{subjects[f.standing]} ({league})",
        "greeting": pick([f"Beste {n},", f"Beste ouders van {n},"]),
        "paragraphs": [f"Hierbij het rapport voor week {f.week_number}.", "\n".join(lines),
                       f"Opmerking van de klastitularis: {remark}"],
        "videos_intro": f"Bijles voor TH{f.th}, te bekijken voor volgende week:",
        "closing": [pick(["Gelieve dit rapport te laten ondertekenen en volgende maandag terug mee te brengen.",
                          "Het volgende rapport volgt maandag. Veel succes deze week."])],
        "sign": "Met vriendelijke groeten,",
    }
