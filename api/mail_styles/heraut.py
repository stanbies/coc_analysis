"""Medieval herald: "Hoort, hoort!", solemn old language, knights and battles,
the clan as a kingdom."""

from .common import Facts, leagues

TITLE = "Op bevel van de Raad"


def compose(f: Facts, pick) -> dict:
    n, league, bench = f.name, f.league_name, f.benchmark_name
    paragraphs = [pick(["Bij dezen maakt de Raad van het koninkrijk Zwegerneet het volgende bekend.",
                        "Zo spreekt de Raad, en zo zij het opgetekend.",
                        "Verneemt allen wat de Raad heden te verkondigen heeft."])]

    if f.standing == "above":
        paragraphs.append(pick([
            f"Ridder {n}, TH{f.th}, voert de banier in {league}. Van een ridder van die rang verwachtte "
            f"het hof {bench}, doch {n} streed {leagues(f.diff)} hoger. Het koninkrijk is verheugd.",
            f"Ridder {n}, TH{f.th}, heeft {league} veroverd, {leagues(f.diff)} voorbij {bench}, waar "
            "het hof een ridder van die rang verwachtte. Laat het in de kronieken worden opgetekend.",
        ]))
    elif f.standing == "equal":
        paragraphs.append(pick([
            f"Ridder {n}, TH{f.th}, houdt stand in {league}, zoals het hof van een ridder van die rang "
            "verwacht. Trouw en standvastig.",
            f"Ridder {n}, TH{f.th}, bewaakt {league}, de burcht die het hof een ridder van die rang "
            "toewees. De plicht is vervuld.",
        ]))
    elif f.standing == "below":
        paragraphs.append(pick([
            f"Ridder {n}, TH{f.th}, legert thans in {league}. Het hof verwacht een ridder van die rang "
            f"in {bench}, nog {leagues(-f.diff)} verder. De weg naar de burcht is lang, doch begaanbaar.",
            f"Ridder {n}, TH{f.th}, strijdt in {league}, {leagues(-f.diff)} onder {bench}, waar het hof "
            "een ridder van die rang verwacht. Het zwaard moet nog gescherpt.",
        ]))
    elif f.standing == "unranked":
        expected = f" Het hof verwacht een ridder van die rang in {bench}." if bench else ""
        paragraphs.append(f"Ridder {n}, TH{f.th}, heeft deze week nog geen veld betreden.{expected} "
                          "Het zwaard roest in de schede!")
    else:
        paragraphs.append(f"Ridder {n}, TH{f.th}, strijdt in {league}. Voor een ridder van die rang "
                          "heeft het hof nog geen verwachting uitgevaardigd.")

    if f.trend == "up":
        paragraphs.append(pick([
            f"Sinds de vorige maan rukte {n} op van {f.previous_name} naar {league}, {leagues(f.change)} "
            "hoger. Laat de trompetten schallen!",
            f"Van {f.previous_name} naar {league}: {leagues(f.change)} terrein gewonnen in één week. "
            "De vijand slaat op de vlucht.",
        ]))
    elif f.trend == "same":
        paragraphs.append(pick([f"Net als de vorige maan houdt {n} de stelling in {league}.",
                                f"De linies houden: {league}, zoals vorige week."]))
    elif f.trend == "down":
        paragraphs.append(pick([
            f"Helaas moest {n} terrein prijsgeven: van {f.previous_name} naar {league}, "
            f"{leagues(-f.change)} lager. Doch geen ridder die nooit uit het zadel werd gelicht.",
            f"De vijand drong {n} terug van {f.previous_name} naar {league}, {leagues(-f.change)} lager. "
            "Een veldslag verloren, niet de oorlog.",
        ]))

    if f.attacks:
        paragraphs.append(pick([f"In het toernooi van vorige week eindigde {n} op plaats {f.placement}, "
                                f"met {f.trophies} trofeeën als buit.",
                                f"Ten toernooie behaalde {n} vorige week plaats {f.placement} en "
                                f"{f.trophies} trofeeën."]))
        if f.attacks == "all":
            paragraphs.append(pick([
                f"Ridder {n} heeft {f.played} maal de vijand bestormd, zoveel als het reglement toestond "
                f"({f.allowed}). Geen enkele kans bleef onbenut.",
                f"Alle {f.allowed} bestormingen werden ondernomen, {f.played} van de {f.allowed}. "
                "De barden zingen ervan.",
            ]))
        elif f.attacks == "some":
            paragraphs.append(pick([
                f"Ridder {n} heeft {f.played} maal de vijand bestormd, doch {f.missed} van de "
                f"{f.allowed} toegestane bestormingen bleven achterwege. De vijand lachte in de vuist.",
                f"{f.played} van de {f.allowed} bestormingen werden ondernomen. {f.missed} maal bleef "
                "het paard op stal.",
            ]))
        else:
            paragraphs.append(f"Geen enkele van de {f.allowed} toegestane bestormingen werd ondernomen. "
                              f"0 maal trok {n} ten strijde. De barden zwijgen.")

    if f.good_week:
        closing = [pick([f"Lang leve ridder {n}! Lang leve Zwegerneet!",
                         "Het koninkrijk is u dank verschuldigd."])]
    else:
        closing = [pick(["Moge het zwaard volgende week scherper zijn. Het koninkrijk rekent op u.",
                         "Rust, verzorg uw wonden, en keer terug naar het slagveld."])]

    return {
        "subject": pick([f"Hoort, hoort! Nieuws over ridder {n}", f"Hoort, hoort! Ridder {n} en {league}"]),
        "greeting": f"Hoort, hoort, edele {n}!",
        "paragraphs": paragraphs,
        "videos_intro": f"Het hof schenkt u de volgende krijgskundige geschriften voor TH{f.th}:",
        "closing": closing,
        "sign": "Aldus beslist en afgekondigd,",
    }
