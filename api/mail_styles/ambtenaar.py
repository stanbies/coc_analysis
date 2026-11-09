"""Belgian civil servant's letter: stiff and formal, with a file number,
references to articles and the strategy videos as attachments."""

from .common import Facts, leagues

TITLE = "Dienst Ranked Aangelegenheden"


def compose(f: Facts, pick) -> dict:
    league, bench = f.league_name, f.benchmark_name
    dossier = f"RA/{f.week}/{f.tag.lstrip('#')}"
    paragraphs = [
        f"Betreft: wekelijkse evaluatie van uw ranked-prestaties, week {f.week_number}\n"
        f"Dossiernummer: {dossier}\nUw kenmerk: TH{f.th}",
        pick(["Ingevolge artikel 4, §2 van het Ranked-reglement van Zwegerneet hebben wij de eer u "
              "het volgende mee te delen.",
              "Na grondig onderzoek van uw dossier delen wij u het volgende mee.",
              "In uitvoering van de wekelijkse controleplicht (artikel 2) delen wij u het volgende mee."]),
    ]

    if f.standing == "above":
        paragraphs.append(f"Uit ons onderzoek blijkt dat u zich momenteel in {league} bevindt. De norm "
                          f"voor een TH{f.th}, vastgelegd in artikel 7, bedraagt {bench}. U overschrijdt "
                          f"deze norm met {leagues(f.diff)}. Deze overschrijding wordt gunstig geadviseerd.")
    elif f.standing == "equal":
        paragraphs.append(f"Uit ons onderzoek blijkt dat u zich in {league} bevindt. Dit stemt overeen "
                          f"met de norm voor een TH{f.th} (artikel 7). Uw dossier is in orde.")
    elif f.standing == "below":
        paragraphs.append(f"Uit ons onderzoek blijkt dat u zich in {league} bevindt. De norm voor een "
                          f"TH{f.th} (artikel 7) bedraagt {bench}. Er werd een tekort vastgesteld van "
                          f"{leagues(-f.diff)}. U beschikt over een termijn van zeven dagen om deze "
                          "toestand te regulariseren.")
    elif f.standing == "unranked":
        norm = f" De norm voor een TH{f.th} (artikel 7) bedraagt {bench}." if bench else ""
        paragraphs.append(f"Uit ons onderzoek blijkt dat u deze week in geen enkele ranked league "
                          f"ingeschreven bent.{norm} Wij verzoeken u uw inschrijving zo spoedig mogelijk "
                          "in orde te brengen.")
    else:
        paragraphs.append(f"U bevindt zich in {league}. Voor een TH{f.th} werd nog geen norm vastgelegd. "
                          "Uw dossier wordt ter informatie bewaard.")

    if f.trend == "up":
        paragraphs.append(f"Ten opzichte van de vorige meting ({f.previous_name}) werd een stijging van "
                          f"{leagues(f.change)} geregistreerd.")
    elif f.trend == "same":
        paragraphs.append(f"Ten opzichte van de vorige meting werd geen wijziging vastgesteld ({league}).")
    elif f.trend == "down":
        paragraphs.append(f"Ten opzichte van de vorige meting ({f.previous_name}) werd een daling van "
                          f"{leagues(-f.change)} geregistreerd. Deze daling wordt opgenomen in uw dossier.")

    if f.attacks:
        paragraphs.append(f"Voor de afgesloten periode werd u gerangschikt op plaats {f.placement}, met "
                          f"een saldo van {f.trophies} trofeeën.")
        if f.attacks == "all":
            paragraphs.append(f"Overeenkomstig artikel 12 werden alle {f.allowed} toegekende aanvallen "
                              f"benut ({f.played}/{f.allowed}). Wij danken u voor uw medewerking.")
        elif f.attacks == "some":
            paragraphs.append(f"Van de {f.allowed} toegekende aanvallen werden er {f.played} benut. "
                              f"{f.missed} aanvallen vervielen. Wij wijzen u erop dat vervallen aanvallen "
                              "niet worden overgedragen naar een volgende periode (artikel 12, lid 3).")
        else:
            paragraphs.append(f"Er werd vastgesteld dat geen enkele van de {f.allowed} toegekende "
                              f"aanvallen werd benut (0/{f.allowed}). Dit wordt beschouwd als een "
                              "onwettige afwezigheid.")

    if f.good_week:
        closing = [pick(["Tegen deze beslissing staat geen beroep open, want er valt niets tegen in te brengen.",
                         "Deze evaluatie wordt zonder opmerkingen aan uw dossier toegevoegd."])]
    else:
        closing = [pick(["Tegen deze beslissing kunt u beroep aantekenen bij de leiding, binnen een "
                         "termijn van dertig dagen, in drievoud.",
                         "U wordt verzocht de nodige maatregelen te nemen vóór de volgende controle."])]
    closing.append("Voor verdere inlichtingen kunt u zich wenden tot ons loket, open op werkdagen "
                   "tussen 9u00 en 11u45.")

    return {
        "subject": f"Betreft: evaluatie ranked-prestaties, dossier {dossier}",
        "greeting": f"Geachte {f.name},",
        "paragraphs": paragraphs,
        "videos_intro": "Bijlagen (door te nemen vóór de volgende controle):",
        "closing": closing,
        "sign": "Hoogachtend,",
        "after": "Deze brief werd automatisch opgemaakt en is geldig zonder handtekening.",
    }
