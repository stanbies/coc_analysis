"""Sporza commentator: excited live commentary, exclamation marks, repetition,
comparisons with cycling and football."""

from .common import Facts, attacks_word, leagues

TITLE = "Commentaarcabine"


def compose(f: Facts, pick) -> dict:
    n, league, bench = f.name, f.league_name, f.benchmark_name
    paragraphs = [pick([f"En daar is {n}!", f"Daar komt {n}, beste kijkers!",
                        f"Let op, let op, {n} komt in beeld!"])]

    if f.standing == "above":
        paragraphs.append(pick([
            f"{league}! {league}, beste kijkers! Van een TH{f.th} verwachten we {bench}, en {n} rijdt "
            f"gewoon {leagues(f.diff)} hoger! {leagues(f.diff)}! Ongelooflijk!",
            f"Wat een demarrage! Verwacht werd {bench}, en {n} zit in {league}! Dat is {leagues(f.diff)} "
            f"boven het niveau van een TH{f.th}. Dit is Van Aert op de Muur van Geraardsbergen!",
        ]))
    elif f.standing == "equal":
        paragraphs.append(pick([
            f"{league}, beste kijkers! Precies de league die we van een TH{f.th} verwachten. "
            "Een penalty in de winkelhaak, zo simpel ziet het eruit!",
            f"{n} zit in {league}, precies waar een TH{f.th} hoort! Geen meter te veel, geen meter te "
            "weinig. Dit is koers rijden met de rekenmachine!",
        ]))
    elif f.standing == "below":
        paragraphs.append(pick([
            f"Het is even afzien voor {n} in {league}! De kopgroep van de TH{f.th}'s rijdt in {bench}, "
            f"{leagues(-f.diff)} verder. Maar ik heb al straffere comebacks gezien, beste kijkers!",
            f"{n} zit in {league}, en van een TH{f.th} verwachten we {bench}. Dat is {leagues(-f.diff)} "
            "achterstand op de kopgroep. Maar het gat is niet onoverbrugbaar, nee nee nee!",
        ]))
    elif f.standing == "unranked":
        expected = f" Een TH{f.th} hoort in {bench}!" if bench else ""
        paragraphs.append(pick([
            f"{n} staat nog altijd aan de start! Nog geen ranked league deze week!{expected} "
            "De koers is vertrokken, beste kijkers, tijd om in de pedalen te gaan!",
            f"Waar is {n}? Nog niet in koers! Geen ranked league deze week!{expected} "
            "De bal ligt op de stip, iemand moet hem binnentrappen!",
        ]))
    else:
        paragraphs.append(f"{n} draait mee in {league}! Een TH{f.th}, en voor die Town Hall hebben we "
                          "nog geen verwachting. Alles is mogelijk, beste kijkers, alles!")

    if f.trend == "up":
        paragraphs.append(pick([
            f"Vorige week nog in {f.previous_name}, nu in {league}! {leagues(f.change)} hoger! "
            "Kijk naar die benen, beste kijkers, kijk naar die benen!",
            f"Van {f.previous_name} naar {league}! {n} schuift {leagues(f.change)} op in het klassement! "
            "Wat een vorm!",
        ]))
    elif f.trend == "same":
        paragraphs.append(pick([
            f"Zelfde league als vorige week: {league}. {n} houdt het tempo, mooi in het wiel!",
            f"Nog altijd {league}, net als vorige week. Rustig in het peloton, energie sparen voor de finale!",
        ]))
    elif f.trend == "down":
        paragraphs.append(pick([
            f"Vorige week nog in {f.previous_name}, nu in {league}. {leagues(-f.change)} lager. "
            f"Een valpartij, beste kijkers! Maar {n} staat alweer recht!",
            f"Oei, oei, oei. Van {f.previous_name} naar {league}, {leagues(-f.change)} terug. "
            "Een lekke band in de finale, dat kan iedereen overkomen!",
        ]))

    if f.attacks:
        paragraphs.append(pick([
            f"Vorige week: plaats {f.placement}! {f.trophies} trofeeën op de teller!",
            f"Plaats {f.placement} in de groep, beste kijkers, met {f.trophies} trofeeën!",
        ]))
        if f.attacks == "all":
            paragraphs.append(pick([
                f"En {n} laat geen enkele aanval liggen! {f.played} op {f.allowed}! "
                f"{f.allowed} op {f.allowed}, beste kijkers!",
                f"Alle {f.allowed} aanvallen gespeeld! {f.played} van de {f.allowed}! "
                "Dat is werken voor de ploeg, dat is een echte knecht!",
            ]))
        elif f.attacks == "some":
            paragraphs.append(pick([
                f"Maar wat zien we daar? {f.played} van de {f.allowed} aanvallen gespeeld. "
                f"{attacks_word(f.missed)} blijven liggen, en dat zijn gratis punten, beste kijkers, "
                "gratis punten!",
                f"{f.played} van de {f.allowed} aanvallen. Er blijven er {f.missed} liggen! "
                "Je laat toch geen open doel liggen!",
            ]))
        else:
            paragraphs.append(pick([
                f"En dan het slechte nieuws: 0 van de {f.allowed} aanvallen gespeeld! "
                "De fiets stond de hele week in de garage!",
                f"Nul aanvallen! 0 van de {f.allowed}! {n} is niet eens komen opdagen voor de aftrap!",
            ]))

    if f.good_week:
        closing = [pick([f"Wat een week van {n}. Ik ben er stil van. Bijna.",
                         f"Volgende week rijden we opnieuw, en ik hoop dat {n} dan weer zo in koers zit!"])]
    else:
        closing = [pick(["Maar de koers is pas gedaan als de laatste over de meet is! "
                         "Volgende week nieuwe kansen!",
                         "De wedstrijd duurt negentig minuten, en er is altijd een tweede helft! "
                         "Volgende week beter!"])]

    subjects = {
        "above": f"{n} rijdt weg uit het peloton in {league}!",
        "equal": f"{n} komt mooi op tijd over de meet in {league}!",
        "below": f"{n} moet even lossen in {league}, maar de koers is lang!",
        "unranked": f"{n} staat nog aan de start!",
        "none": f"{n} live in {league}!",
    }
    return {
        "subject": subjects[f.standing],
        "greeting": pick([f"Goeiemiddag beste kijkers, en goeiemiddag {n}!",
                          f"Welkom in de commentaarcabine, {n}!"]),
        "paragraphs": paragraphs,
        "videos_intro": f"We schakelen even naar de analyse in de studio. Deze beelden voor TH{f.th} "
                        "moet je zeker bekijken:",
        "closing": closing,
        "sign": "Terug naar de studio,",
    }
