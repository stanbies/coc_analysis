"""LinkedIn motivational post: a hook, short lines, a "lesson" and hashtags.

The original weekly mail, text unchanged.
"""

from .common import Facts, leagues

TITLE = "Chief Motivation Officers"

OPENERS = {
    "above": ["Ik wil even iets met je delen.",
              "Iedereen wil resultaten. Weinigen leveren ze.",
              "Soms moet je even stilstaan bij hoe ver je al gekomen bent."],
    "equal": ["Er zijn twee soorten spelers: zij die over hun doelen praten, en zij die ze halen.",
              "Een doel zonder plan is een wens. Jij had een plan.",
              "Consistentie verslaat talent. Elke week opnieuw."],
    "below": ["Elke legende begon ergens.",
              "Succes is geen rechte lijn. Het is een trap.",
              "Ik ga eerlijk met je zijn, want dat verdien je."],
    "unranked": ["Het moeilijkste aan elke reis is de eerste stap.",
                 "Elke grote carrière begon met een eerste aanval."],
}

SUBJECTS = {
    "above": "{league}. Boven verwachting. Laat dat even bezinken. 🚀",
    "equal": "{league}. Doel gehaald. 🎯",
    "below": "{league}. Dit is waar je comeback begint. 💪",
    "unranked": "Je ranked-verhaal moet nog beginnen. 🌱",
    "none": "{league}. Je wekelijkse ranked-update. 📊",
}


def compose(f: Facts, pick) -> dict:
    th, current, target, status = f.th, f.league_name, f.benchmark_name, f.standing
    paragraphs = [pick(OPENERS[status])] if status in OPENERS else []

    if status == "unranked":
        paragraphs.append("Je hebt deze week nog geen ranked league."
                          + (f" Voor TH{th} mikken we op minstens {target}." if target else ""))
        paragraphs.append("De beste tijd om te beginnen was vorige week. "
                          "De op één na beste tijd is vandaag. 🌱")
    elif status == "none":
        paragraphs.append(f"Je zit in {current}.")
    elif status == "above":
        paragraphs.append(f"Deze week zit je in {current}.\nVoor TH{th} verwachten we {target}.\n"
                          f"Jij zit er {leagues(f.diff)} boven.")
        paragraphs.append("Dat is geen geluk. Dat is discipline. 💯")
    elif status == "equal":
        paragraphs.append(f"Jij zit in {current}: precies de lat die we voor TH{th} legden. "
                          "Doel gehaald. ✅")
    else:
        paragraphs.append(f"Jij zit nu in {current}.\nVoor TH{th} mikken we op {target}. "
                          f"Dat is {leagues(-f.diff)} verder.")
        paragraphs.append("Is dat een probleem? Nee. Dat is een kans. 🔥")

    if f.trend == "up":
        paragraphs.append(f"📈 Vorige week: {f.previous_name}. Nu: {current}.\n"
                          "Groei is geen toeval. Groei is een keuze.")
    elif f.trend == "down":
        paragraphs.append(f"📉 Vorige week: {f.previous_name}. Nu: {current}.\n"
                          "Een terugval is geen mislukking. Het is feedback. "
                          "En feedback is een cadeau. 🎁")
    elif f.trend == "same":
        paragraphs.append(f"Je staat in dezelfde league als vorige week. Een plateau is geen "
                          "stilstand: het is de aanloop naar je volgende sprong. 🧗")

    if f.attacks:
        paragraphs.append(f"Vorige week eindigde je op plaats {f.placement} in je groep, "
                          f"met {f.trophies} trofeeën.")
        if f.attacks != "all":
            paragraphs.append(f"Hier zit je grootste groeikans: je speelde {f.played} van je {f.allowed} "
                              f"aanvallen. Dat {'is 1 kans' if f.missed == 1 else f'zijn {f.missed} kansen'} "
                              "die je liet liggen.\nJe mist 100% van de aanvallen die je niet doet. 🎯")
        elif f.has_videos:
            paragraphs.append(f"Je speelde al je {f.allowed} aanvallen. De inzet is er. "
                              "Nu de techniek nog. 📚")
        else:
            paragraphs.append(f"Je speelde al je {f.allowed} aanvallen. Showing up is half the battle. "
                              "Jij deed het volledige werk. 👏")

    if status in ("below", "unranked"):
        closing = ["Volgende week staat er een nieuwe groep klaar. De vraag is niet óf je stijgt. "
                   "De vraag is wanneer. 💭"]
    else:
        closing = ["Blijf bouwen. Blijf aanvallen. Blijf groeien.", "Agree? 👇"]
    closing.append(f"#Zwegerneet #RankedMindset #TH{th} #NeverStopAttacking")

    return {
        "subject": SUBJECTS[status].format(league=current),
        "greeting": f"Hoi {f.name},",
        "paragraphs": paragraphs,
        "videos_intro": f"Leren stopt nooit. Mijn tips van de week voor TH{th}: 👇",
        "closing": closing,
        "sign": "Groetjes,",
    }
