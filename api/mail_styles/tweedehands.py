"""2dehands ad: the player is offered for sale, with a title, condition,
specifications and a price. A bad week is sold "voor onderdelen"."""

from .common import Facts, leagues

TITLE = "Verkoper. Geen tijdverspillers."


def compose(f: Facts, pick) -> dict:
    n, league, bench = f.name, f.league_name, f.benchmark_name
    for_parts = f.standing in ("below", "unranked") or f.attacks == "none"
    adjective = {
        "above": pick(["uitzonderlijke", "zeldzame"]),
        "equal": pick(["betrouwbare", "degelijke"]),
        "below": pick(["op te knappen", "verzorgde"]),
        "unranked": pick(["ongebruikte", "nooit gebruikte"]),
        "none": pick(["degelijke", "nette"]),
    }[f.standing]
    title = f"Te koop{' voor onderdelen' if for_parts else ''}: {adjective} TH{f.th}"
    if f.standing != "unranked":
        title += f", {league}"
    paragraphs = [pick(["We hebben een advertentie voor je geplaatst. Bekijk ze hieronder.",
                        "Je staat te koop. Hier is de advertentie."]),
                  title + "."]

    if f.standing == "above":
        paragraphs.append(pick([f"Staat: als nieuw. Presteert {leagues(f.diff)} boven de verwachte {bench}.",
                                f"Staat: uitstekend. Draait {leagues(f.diff)} hoger dan de {bench} die je van "
                                f"een TH{f.th} mag verwachten."]))
    elif f.standing == "equal":
        paragraphs.append(pick([f"Staat: zeer goed. Draait precies in de verwachte league ({bench}).",
                                f"Staat: goed onderhouden. Haalt {league}, zoals een TH{f.th} hoort."]))
    elif f.standing == "below":
        paragraphs.append(pick([f"Staat: gebruikt, met gebruikssporen. Haalt {league}, verwacht wordt {bench} "
                                f"({leagues(-f.diff)} hoger).",
                                f"Staat: moet wat aan gebeuren. Zit in {league}, een TH{f.th} hoort in {bench}, "
                                f"{leagues(-f.diff)} hoger."]))
    elif f.standing == "unranked":
        expected = f" Voor een TH{f.th} is {bench} normaal." if bench else ""
        paragraphs.append(f"Staat: nog in de verpakking. Deze week geen ranked league gespeeld.{expected}")
    else:
        paragraphs.append("Staat: goed. Voor deze Town Hall bestaat nog geen referentie.")

    specs = [f"- Town Hall: {f.th}", f"- League: {league}"]
    if f.trend:
        specs.append(f"- Vorige week: {f.previous_name}")
    if f.attacks:
        specs += [f"- Plaats vorige week: {f.placement}", f"- Trofeeën: {f.trophies}",
                  f"- Aanvallen: {f.played}/{f.allowed}"]
    paragraphs.append("Specificaties:\n" + "\n".join(specs))

    if f.trend == "up":
        paragraphs.append(pick([f"Recent opgewaardeerd: vorige week nog {f.previous_name}, nu {leagues(f.change)} hoger.",
                                f"Pas nog getuned: van {f.previous_name} naar {league}, {leagues(f.change)} sneller."]))
    elif f.trend == "same":
        paragraphs.append(pick([f"Geen recente wijzigingen, stabiel in {league}.",
                                "Rijdt al een week zonder problemen in dezelfde league."]))
    elif f.trend == "down":
        paragraphs.append(pick([f"Lichte schade: vorige week nog {f.previous_name}, nu {leagues(-f.change)} lager.",
                                f"Kleine deuk: {leagues(-f.change)} gezakt, van {f.previous_name} naar {league}."]))

    if f.attacks == "all":
        paragraphs.append(pick([f"Alle {f.allowed} aanvallen gespeeld. Rookvrij, geen huisdieren.",
                                f"{f.played} van de {f.allowed} aanvallen gespeeld. Altijd binnen gestald."]))
    elif f.attacks == "some":
        paragraphs.append(pick([f"{f.missed} van de {f.allowed} aanvallen niet gebruikt. Start soms wat traag.",
                                f"Slechts {f.played} van de {f.allowed} aanvallen gespeeld, {f.missed} "
                                "bleven liggen. Verbruik iets lager dan opgegeven."]))
    elif f.attacks == "none":
        paragraphs.append(f"Heeft vorige week stilgestaan: 0 van de {f.allowed} aanvallen. Start moeilijk.")

    if for_parts:
        price = pick(["Prijs: voor onderdelen. Ophalen in de clan.",
                      "Prijs: wat het waard is. Bod vanaf 1 Gold Pass."])
    elif f.standing == "above":
        price = pick(["Prijs: vast. Niet onder de vraagprijs.", "Prijs: op aanvraag. Enkel serieuze kopers."])
    else:
        price = pick(["Prijs bespreekbaar.", "Prijs: redelijk, gezien de staat."])
    paragraphs.append(price)

    return {
        "subject": title,
        "greeting": f"Hallo {n},",
        "paragraphs": paragraphs,
        "videos_intro": f"Handleiding en onderhoudstips voor deze TH{f.th}, gratis bij aankoop:",
        "closing": [pick(["Interesse? Stuur een bericht. Geen tijdverspillers.",
                          "Wie eerst komt, eerst maalt. Ruilen tegen een Electro Dragon kan ook."])],
        "sign": "Groetjes,",
    }
