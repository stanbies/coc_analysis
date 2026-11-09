"""Writing styles for the weekly ranked mail, one module per style.

All players get the same style in a week; the styles rotate in the order of
STIJLEN, counted in weeks from STARTDATUM. The count uses dates, not week
numbers, so the turn of the year doesn't matter and no state file is needed.

A style module has TITLE (the line under "De leiding van ..." in the signoff)
and compose(f, pick) returning a dict with subject, greeting, paragraphs,
videos_intro, closing (a list), sign (the word(s) before the signature) and
optionally after (a line below the signature). f is the player's Facts;
pick(options) chooses one variant of a sentence. To add a style, write the
module and put it in STIJLEN; to drop one, take it out of STIJLEN.
"""

import random
from datetime import date

from . import (ambtenaar, heraut, linkedin, natuur, rapport, sergeant, sporza, tweedehands,
               weerbericht)
from .common import Facts, build_facts

# Settings
STARTDATUM = date(2026, 11, 16)  # a Monday: the week the first style in STIJLEN is sent
WEKEN_PER_STIJL = 1
STIJLEN = [sporza, natuur, weerbericht, ambtenaar, rapport, sergeant, heraut, tweedehands, linkedin]


def style_for_week(week: str):
    """The style for an ISO week like 2026-W47."""
    year, number = week.split("-W")
    monday = date.fromisocalendar(int(year), int(number), 1)
    weeks = (monday - STARTDATUM).days // 7
    return STIJLEN[(weeks // WEKEN_PER_STIJL) % len(STIJLEN)]


def compose(facts: Facts, style) -> dict:
    """The style's text; reruns give the same variants, other players and weeks differ."""
    rng = random.Random(f"{facts.name}{facts.week}")
    return style.compose(facts, rng.choice)


__all__ = ["STARTDATUM", "WEKEN_PER_STIJL", "STIJLEN", "Facts", "build_facts", "compose",
           "style_for_week"]
