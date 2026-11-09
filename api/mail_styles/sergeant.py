"""Drill sergeant: shouting in capitals, tough but friendly criticism and a
reluctant compliment after a good week. Never hurtful, no swearing."""

from .common import Facts, leagues

TITLE = "Sergeant van dienst"


def compose(f: Facts, pick) -> dict:
    n, league = f.name.upper(), f.league_name.upper()
    bench = f.benchmark_name.upper() if f.benchmark_name else None
    paragraphs = [pick(["IK HEB JE CIJFERS GEZIEN, SOLDAAT.", "OGEN HIER, SOLDAAT!", "STA STIL EN LUISTER!"])]

    if f.standing == "above":
        paragraphs.append(pick([
            f"{league}. EEN TH{f.th} HOORT IN {bench}, EN JIJ ZIT ER {leagues(f.diff).upper()} BOVEN. "
            "IK GA NIET ZEGGEN DAT HET GOED IS. ...HET IS GOED. ZO. GEZEGD.",
            f"{league}? {leagues(f.diff).upper()} BOVEN {bench}? DAT IS BOVEN DE NORM VOOR EEN TH{f.th}. "
            "DENK NU MAAR NIET DAT JE HIER KOMT UITRUSTEN!",
        ]))
    elif f.standing == "equal":
        paragraphs.append(pick([
            f"{league}. PRECIES WAT WE VAN EEN TH{f.th} VERWACHTEN. NIET MEER, NIET MINDER. "
            "ACCEPTABEL, SOLDAAT. ACCEPTABEL.",
            f"{league}, DE NORM VOOR EEN TH{f.th}. JE HAALT DE LAT. DE LAT, SOLDAAT, NIET DE STERREN!",
        ]))
    elif f.standing == "below":
        paragraphs.append(pick([
            f"{league}? EEN TH{f.th} HOORT IN {bench}! DAT IS {leagues(-f.diff).upper()} TE LAAG! "
            f"MIJN OMA HAALT {bench} MET EEN TH9 EN EEN GEBROKEN HEUP!",
            f"{league}! {leagues(-f.diff).upper()} ONDER {bench}! IS DAT EEN TH{f.th} OF EEN "
            "VAKANTIEKAMP?",
        ]))
    elif f.standing == "unranked":
        expected = f" EEN TH{f.th} HOORT IN {bench}!" if bench else ""
        paragraphs.append(f"GEEN RANKED LEAGUE? GEEN ENKELE?{expected} WAT DOE JE DE HELE DAG, "
                          "BASISSEN BEWONDEREN?")
    else:
        paragraphs.append(f"{league}. VOOR EEN TH{f.th} HEB IK NOG GEEN NORM. DAT IS GEEN EXCUUS "
                          "OM TE VERSLAPPEN!")

    if f.trend == "up":
        paragraphs.append(pick([
            f"VORIGE WEEK {f.previous_name.upper()}, NU {league}. {leagues(f.change).upper()} OMHOOG. "
            "DENK NIET DAT IK HET NIET GEZIEN HEB. GOED ZO. EN NU NIET ZWEVEN!",
            f"VAN {f.previous_name.upper()} NAAR {league}. {leagues(f.change).upper()} GESTEGEN. "
            "DAT NOEM IK VOORUITGANG. NIET VERDER VERTELLEN DAT IK DAT ZEI.",
        ]))
    elif f.trend == "same":
        paragraphs.append(pick([f"ZELFDE LEAGUE ALS VORIGE WEEK, {league}. STILSTAAN IS ACHTERUITGAAN, SOLDAAT!",
                                f"NOG ALTIJD {league}. IK HEB STANDBEELDEN GEZIEN DIE MEER BEWOGEN!"]))
    elif f.trend == "down":
        paragraphs.append(pick([
            f"VORIGE WEEK {f.previous_name.upper()}, NU {league}. {leagues(-f.change).upper()} OMLAAG! "
            "WIE HEEFT JOU TOESTEMMING GEGEVEN OM TE ZAKKEN?",
            f"VAN {f.previous_name.upper()} NAAR {league}? {leagues(-f.change).upper()} TERUG! "
            "IN MIJN LEGER MARCHEREN WE VOORUIT!",
        ]))

    if f.attacks:
        if f.placement > 1:
            paragraphs.append(pick([
                f"PLAATS {f.placement}? MIJN OMA HAALT PLAATS {f.placement - 1} MET EEN TH9! "
                f"EN {f.trophies} TROFEEËN, DAT IS ALLES?",
                f"PLAATS {f.placement}, {f.trophies} TROFEEËN. IK WIL VOLGENDE WEEK EEN KLEINER "
                "PLAATSNUMMER ZIEN!",
            ]))
        else:
            paragraphs.append(f"PLAATS 1, {f.trophies} TROFEEËN. ...NIET SLECHT. NIET OVERAL RONDVERTELLEN.")
        if f.attacks == "all":
            paragraphs.append(pick([
                f"{f.played} VAN DE {f.allowed} AANVALLEN GESPEELD. ALLEMAAL. ...GOED. DAT WAS EEN "
                "COMPLIMENT, NIET AAN WENNEN.",
                f"ALLE {f.allowed} AANVALLEN GESPEELD, {f.played} VAN DE {f.allowed}. ZO HOORT HET. "
                "VERWACHT GEEN MEDAILLE.",
            ]))
        elif f.attacks == "some":
            paragraphs.append(pick([
                f"{f.played} VAN DE {f.allowed} AANVALLEN? EN DIE ANDERE {f.missed}? LIGGEN DIE NOG TE SLAPEN?",
                f"{f.missed} AANVALLEN NIET GESPEELD! {f.played} VAN DE {f.allowed}! IN MIJN TIJD "
                "SPEELDEN WE ZE ALLEMAAL, IN DE SNEEUW, BERGOP!",
            ]))
        else:
            paragraphs.append(pick([
                f"NUL AANVALLEN. 0 VAN DE {f.allowed}! IK HEB DESERTEURS GEZIEN DIE ACTIEVER WAREN!",
                f"0 VAN DE {f.allowed} AANVALLEN! WAS JE OP VERLOF? IK HEB GEEN VERLOF GOEDGEKEURD!",
            ]))

    if f.good_week:
        closing = [pick(["INGERUKT. EN VOLGENDE WEEK HETZELFDE, OF BETER!",
                         "GOED GEDAAN, SOLDAAT. EN NU WEGWEZEN VOOR IK ME BEDENK!"])]
    else:
        closing = [pick(["VOLGENDE WEEK WIL IK RESULTATEN ZIEN. ALLE AANVALLEN. GEEN EXCUSES. INGERUKT!",
                         "IK GELOOF IN JE, SOLDAAT. DAAROM ROEP IK ZO HARD. VOLGENDE WEEK BETER!"])]

    subjects = {
        "above": f"{league}. NIET SLECHT, SOLDAAT. NIET SLECHT.",
        "equal": f"{league}. ACCEPTABEL, SOLDAAT.",
        "below": f"{league}? APPEL, SOLDAAT. NU!",
        "unranked": "GEEN RANKED LEAGUE? APPEL, SOLDAAT!",
        "none": f"{league}. TIJD VOOR APPEL!",
    }
    return {
        "subject": subjects[f.standing],
        "greeting": pick([f"SOLDAAT {n}!", f"{n}! IN DE RIJ!"]),
        "paragraphs": paragraphs,
        "videos_intro": f"HUISWERK, SOLDAAT. DEZE FILMPJES VOOR TH{f.th} BEKIJK JE VOOR MAANDAG:",
        "closing": closing,
        "sign": "INGERUKT MARS,",
    }
