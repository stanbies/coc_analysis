"""Nature documentary: a calm, wondering narrator. The league is the territory,
attacks are hunts, the Town Hall is the species."""

from .common import Facts, leagues

TITLE = "Afdeling Gedragsonderzoek"


def compose(f: Facts, pick) -> dict:
    n, league, bench = f.name, f.league_name, f.benchmark_name
    paragraphs = [pick(["Diep in het land van Clash leeft een bijzondere soort.",
                        "Het is maandagochtend. Over de vlakten van de ranked leagues komt langzaam het licht op.",
                        "Stil nu. Als we heel voorzichtig zijn, kunnen we het van dichtbij bekijken."])]

    if f.standing == "above":
        paragraphs.append(pick([
            f"Hier zien we de TH{f.th} in de natuurlijke habitat: {league}. Opmerkelijk, want deze soort "
            f"leeft doorgaans in {bench}. Dit exemplaar, {n}, heeft het territorium {leagues(f.diff)} "
            "hoger gevestigd.",
            f"Dit is {n}, een TH{f.th}. Soortgenoten vestigen zich doorgaans in {bench}, maar dit "
            f"exemplaar heeft {league} veroverd, {leagues(f.diff)} hoger. Een zeldzaam schouwspel.",
        ]))
    elif f.standing == "equal":
        paragraphs.append(pick([
            f"Hier zien we de TH{f.th} in de natuurlijke habitat: {league}. Precies het territorium "
            f"waar we deze soort verwachten. {n} leeft in volmaakt evenwicht met de omgeving.",
            f"{n}, een TH{f.th}, heeft zich gevestigd in {league}, het territorium dat bij deze soort "
            "hoort. Alles is zoals de natuur het bedoeld heeft.",
        ]))
    elif f.standing == "below":
        paragraphs.append(pick([
            f"We treffen {n}, een TH{f.th}, aan in {league}. Deze soort hoort thuis in {bench}, nog "
            f"{leagues(-f.diff)} hogerop. Het dier lijkt dat te weten. Het wacht. Het observeert.",
            f"{n}, een TH{f.th}, verblijft deze week in {league}. Soortgenoten leven doorgaans in "
            f"{bench}, {leagues(-f.diff)} hoger. Maar in de natuur is niets voorgoed.",
        ]))
    elif f.standing == "unranked":
        expected = f" Soortgenoten vestigen zich doorgaans in {bench}." if bench else ""
        paragraphs.append(f"{n}, een TH{f.th}, heeft deze week nog geen territorium gekozen.{expected} "
                          "Geduld is een deugd in de natuur, maar ook hier wacht het seizoen op niemand.")
    else:
        paragraphs.append(f"{n}, een TH{f.th}, heeft zich gevestigd in {league}. Over het gedrag van "
                          "deze soort in de ranked leagues is nog maar weinig bekend.")

    if f.trend == "up":
        paragraphs.append(pick([
            f"Vorige week leefde {n} nog in {f.previous_name}. Nu, {leagues(f.change)} hoger, in {league}. "
            "Een migratie naar betere gronden.",
            f"Van {f.previous_name} naar {league}: {leagues(f.change)} hoger. Zo trekt de soort elk "
            "seizoen naar vruchtbaarder land.",
        ]))
    elif f.trend == "same":
        paragraphs.append(pick([
            f"Het territorium is hetzelfde als vorige week: {league}. Een teken van een gevestigde populatie.",
            f"Net als vorige week blijft {n} in {league}. Het dier kent hier elke steen.",
        ]))
    elif f.trend == "down":
        paragraphs.append(pick([
            f"Vorige week hield {n} nog stand in {f.previous_name}. Nu is het dier teruggedrongen naar "
            f"{league}, {leagues(-f.change)} lager. Wie vandaag terrein verliest, herovert het morgen.",
            f"Van {f.previous_name} naar {league}, {leagues(-f.change)} lager. Zelfs de sterkste "
            "dieren moeten soms wijken.",
        ]))

    if f.attacks:
        paragraphs.append(f"In de groep van vorige week eindigde {n} op plaats {f.placement}, met "
                          f"{f.trophies} trofeeën als buit.")
        if f.attacks == "all":
            paragraphs.append(pick([
                f"En dan, een prachtig schouwspel. Alle {f.allowed} jachtpartijen werden ondernomen, "
                f"{f.played} van de {f.allowed}. Geen enkele kans bleef onbenut.",
                f"{f.played} van de {f.allowed} jachtkansen benut. Dit dier laat geen prooi lopen.",
            ]))
        elif f.attacks == "some":
            paragraphs.append(pick([
                f"Van de {f.allowed} jachtkansen werden er {f.played} benut. {f.missed} keer bleef het "
                "dier in het hol liggen. Misschien was het koud. Misschien was het moe.",
                f"{f.played} van de {f.allowed} jachtpartijen. De overige {f.missed} keer keek het dier "
                "de prooi alleen maar na.",
            ]))
        else:
            paragraphs.append(f"Opvallend: geen enkele van de {f.allowed} jachtkansen werd benut. "
                              "0 aanvallen. Het dier hield een volledige winterslaap.")

    if f.good_week:
        closing = [pick([f"En zo eindigt een nieuwe week in het leven van {n}. Volgende maandag kijken we opnieuw mee.",
                         "Een gezond exemplaar, in een gezonde populatie. Wat een voorrecht om dit te mogen zien."])]
    else:
        closing = [pick([f"De natuur geeft altijd een tweede kans. Volgende week trekt {n} opnieuw op jacht.",
                         "Na elke winter komt een lente. Ook in de ranked leagues."])]

    return {
        "subject": pick([f"Een TH{f.th} in de natuurlijke habitat: {league}",
                         f"{n} in het wild: {league}"]) if f.standing != "unranked"
                   else f"{n}, een TH{f.th} zonder territorium",
        "greeting": f"Beste {n},",
        "paragraphs": paragraphs,
        "videos_intro": f"Ter studie: beelden van soortgenoten (TH{f.th}) die het territorium wel veroverden.",
        "closing": closing,
        "sign": "Met verwondering,",
    }
