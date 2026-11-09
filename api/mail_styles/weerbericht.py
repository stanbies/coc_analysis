"""Weather forecast: above the expectation is sunny and warm, below is showers,
missed attacks are calm winds. Ends with an outlook for next week."""

from .common import Facts, leagues

TITLE = "Het KMI van Zwegerneet"


def compose(f: Facts, pick) -> dict:
    n, league, bench = f.name, f.league_name, f.benchmark_name
    paragraphs = [pick(["Hier is het weerbericht voor de nieuwe ranked-week.",
                        "Tijd voor het weer.",
                        "En dan nu het weer, met de vooruitzichten voor de komende dagen."])]

    if f.standing == "above":
        paragraphs.append(pick([
            f"Voor {n}: zonnig en droog in {league}, {leagues(f.diff)} boven het seizoensgemiddelde "
            f"voor een TH{f.th}. Dat gemiddelde ligt op {bench}. Zonnecrème aanbevolen.",
            f"Voor {n}: stralend weer in {league}. Voor een TH{f.th} is {bench} normaal voor de "
            f"tijd van het jaar, dus dat is {leagues(f.diff)} warmer. Een uitzonderlijk mooie week.",
        ]))
    elif f.standing == "equal":
        paragraphs.append(pick([
            f"Voor {n}: aangenaam en zacht in {league}, precies het seizoensgemiddelde voor een "
            f"TH{f.th}. Geen extremen, perfect terrasweer.",
            f"Voor {n}: {league}, helemaal normaal voor een TH{f.th} in deze tijd van het jaar. "
            "Licht bewolkt, droog, en een zacht briesje.",
        ]))
    elif f.standing == "below":
        paragraphs.append(pick([
            f"Voor {n}: bewolkt met buien in {league}. Het seizoensgemiddelde voor een TH{f.th} "
            f"ligt op {bench}, nog {leagues(-f.diff)} hoger. Paraplu bij de hand houden.",
            f"Voor {n}: grijs en nat in {league}. Normaal voor een TH{f.th} is {bench}, dus het "
            f"is {leagues(-f.diff)} frisser dan gemiddeld.",
        ]))
    elif f.standing == "unranked":
        expected = f" Het seizoensgemiddelde voor een TH{f.th} is {bench}." if bench else ""
        paragraphs.append(f"Voor {n}: dichte mist. Nog geen ranked league te bespeuren deze week."
                          f"{expected} De zichtbaarheid is nul.")
    else:
        paragraphs.append(f"Voor {n} (TH{f.th}): weer in {league}. Voor deze Town Hall hebben we nog "
                          "geen seizoensgemiddelde, dus elke temperatuur is een record.")

    if f.trend == "up":
        paragraphs.append(pick([f"De temperatuur stijgt: vorige week nog {f.previous_name}, nu {league}. "
                                f"Dat is {leagues(f.change)} warmer.",
                                f"Een warmtefront trekt over het land: van {f.previous_name} naar {league}, "
                                f"{leagues(f.change)} erbij."]))
    elif f.trend == "same":
        paragraphs.append(pick([f"Stabiel weer: net als vorige week {league}. Een hogedrukgebied houdt "
                                "alles op de plaats.",
                                f"Geen verandering ten opzichte van vorige week: {league}."]))
    elif f.trend == "down":
        paragraphs.append(pick([f"Afkoeling: vorige week nog {f.previous_name}, nu {league}, "
                                f"{leagues(-f.change)} kouder.",
                                f"Een koufront uit het noorden: van {f.previous_name} naar {league}, "
                                f"{leagues(-f.change)} lager op de thermometer."]))

    if f.attacks:
        paragraphs.append(pick([f"Terugblik op vorige week: plaats {f.placement} in de groep en "
                                f"{f.trophies} trofeeën gevallen.",
                                f"De metingen van vorige week: plaats {f.placement}, met {f.trophies} "
                                "trofeeën neerslag."]))
        if f.attacks == "all":
            paragraphs.append(pick([f"Er stond de hele week een stevige wind: alle {f.allowed} aanvallen "
                                    f"gespeeld, {f.played} van de {f.allowed}.",
                                    f"Windkracht 10: {f.played} van de {f.allowed} aanvallen gespeeld. "
                                    "Geen moment windstil."]))
        elif f.attacks == "some":
            paragraphs.append(pick([f"Wel plaatselijk windstil: {f.played} van de {f.allowed} aanvallen "
                                    f"gespeeld, {f.missed} bleven liggen.",
                                    f"Af en toe viel de wind helemaal weg: {f.missed} van de {f.allowed} "
                                    f"aanvallen bleven liggen, {f.played} werden gespeeld."]))
        else:
            paragraphs.append(f"Volledige windstilte: 0 van de {f.allowed} aanvallen gespeeld. "
                              "Geen zuchtje wind te bespeuren.")

    if f.good_week:
        outlook = pick(["Vooruitzicht voor volgende week: aanhoudend zonnig, met kans op promotie.",
                        "Vooruitzicht voor volgende week: droog en warm. Hou het zo."])
    elif f.attacks in ("some", "none"):
        outlook = pick(["Vooruitzicht voor volgende week: opklaringen, als de wind weer opsteekt. "
                        "Elke gespeelde aanval brengt zon.",
                        "Vooruitzicht voor volgende week: wisselvallig, maar met alle aanvallen "
                        "gespeeld breekt de zon door."])
    else:
        outlook = pick(["Vooruitzicht voor volgende week: geleidelijk opklarend vanuit het westen.",
                        "Vooruitzicht voor volgende week: na de buien komen de opklaringen."])

    subjects = {
        "above": f"Zonnig en warm in {league}",
        "equal": f"Zacht en aangenaam in {league}",
        "below": f"Buien in {league}, opklaringen in zicht",
        "unranked": "Dichte mist: nog geen ranked league",
        "none": f"Het weer in {league}",
    }
    return {
        "subject": subjects[f.standing],
        "greeting": f"Goeiemorgen {n},",
        "paragraphs": paragraphs,
        "videos_intro": f"Voor wie binnen blijft tijdens de buien, wat kijkvoer voor TH{f.th}:",
        "closing": [outlook],
        "sign": "Tot het volgende weerbericht,",
    }
