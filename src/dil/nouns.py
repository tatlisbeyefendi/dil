"""Turkish noun inflection: plural, possessive, case, copula — and combinations.

>>> decline("kitap", possessive="1p", case="locative", softening=True)
'kitaplarımızda'
>>> decline("araba", case="instrumental")
'arabayla'
"""

from __future__ import annotations

from dataclasses import dataclass, field

from . import phonetics as ph

CASES = (
    "nominative",
    "accusative",
    "dative",
    "locative",
    "ablative",
    "genitive",
    "instrumental",
)

POSSESSIVES = ("1s", "2s", "3s", "1p", "2p", "3p")

CASE_LABELS = {
    "nominative": "yalın",
    "accusative": "belirtme",
    "dative": "yönelme",
    "locative": "bulunma",
    "ablative": "ayrılma",
    "genitive": "tamlayan",
    "instrumental": "vasıta",
}

POSSESSIVE_LABELS = {
    "1s": "benim",
    "2s": "senin",
    "3s": "onun",
    "1p": "bizim",
    "2p": "sizin",
    "3p": "onların",
}


@dataclass(frozen=True)
class Noun:
    """A stem plus the lexical accidents that inflection has to know about."""

    stem: str
    softening: bool = False
    vowel_drop: bool = False
    proper: bool = False
    notes: tuple[str, ...] = field(default=(), compare=False)

    def __post_init__(self) -> None:
        if not self.stem:
            raise ValueError("stem must not be empty")


class _Form:
    """Tracks a word while suffixes are glued on, so each change happens once."""

    __slots__ = ("text", "stem", "softened", "dropped")

    def __init__(self, text: str) -> None:
        self.text = text
        self.stem = text
        self.softened = False
        self.dropped = False

    def add(self, suffix: str, *, softening: bool, vowel_drop: bool) -> None:
        # Softening and vowel drop act on the lexical stem, never on a stem that
        # already carries a suffix (ağızlar -> ağızları, not ağızlrı).
        on_stem = self.text == self.stem
        if suffix and ph.starts_with_vowel(suffix):
            if vowel_drop and on_stem and not self.dropped and not self.softened:
                new = ph.drop_last_vowel(self.text)
                if new != self.text:
                    self.text = new
                    self.dropped = True
            if (
                softening
                and self.text == self.stem
                and not self.softened
                and ph.can_soften(self.text)
            ):
                new = ph.soften(self.text)
                if new != self.text:
                    self.text = new
                    self.softened = True
        self.text += suffix

    def add_d(self, suffix_tail: str) -> None:
        """Add a ``d``-initial suffix, voicing or devoicing the final consonant."""
        self.text += ph.assimilate(self.text, "d" + suffix_tail)

    def soften_final_k(self) -> None:
        """Turn a final k into ğ (gelecek + im -> geleceğim)."""
        if ph.fold(self.text)[-1:] == "k":
            self.text = self.text[:-1] + "ğ"

    def ends_with_vowel(self) -> bool:
        return ph.ends_with_vowel(self.text)


#: Vowel-final stems that still take a -y- buffer ("su" -> "suyu", "suyun").
NEEDS_Y = frozenset({"su"})


def _possessive_suffix(form: _Form, possessive: str, *, needs_y: bool = False) -> str:
    vowel = form.ends_with_vowel() and not needs_y
    h4 = ph.harmony_4(form.text)
    prefix = "y" if needs_y else ""
    match possessive:
        case "1s":
            return prefix + ("m" if vowel else h4 + "m")
        case "2s":
            return prefix + ("n" if vowel else h4 + "n")
        case "3s":
            # "araba" -> "arabası", "kitap" -> "kitabı", "su" -> "suyu"
            return prefix + ("s" + h4 if vowel else h4)
        case "1p":
            return prefix + ("m" + h4 + "z" if vowel else h4 + "m" + h4 + "z")
        case "2p":
            return prefix + ("n" + h4 + "z" if vowel else h4 + "n" + h4 + "z")
        case "3p":
            back = ph.harmony_2(form.text)
            return "l" + back + "r" + ("ı" if back == "a" else "i")
    raise ValueError(f"unknown possessive: {possessive!r}")


def decline(
    stem: str,
    *,
    plural: bool = False,
    possessive: str | None = None,
    case: str = "nominative",
    copula: bool = False,
    softening: bool = False,
    vowel_drop: bool = False,
    proper: bool = False,
) -> str:
    """Return the inflected form of ``stem``.

    ``possessive`` is one of ``1s 2s 3s 1p 2p 3p``; ``case`` is a member of
    :data:`CASES`; ``copula`` adds ``-dir``.
    """
    if possessive is not None and possessive not in POSSESSIVES:
        raise ValueError(f"unknown possessive: {possessive!r}")
    if case not in CASES:
        raise ValueError(f"unknown case: {case!r}")

    form = _Form(stem)
    needs_y = ph.fold(stem) in NEEDS_Y

    if plural:
        form.add("l" + ph.harmony_2(form.text) + "r", softening=False, vowel_drop=False)

    if possessive is not None:
        # The -y- of "su" only shows on the bare stem (suyu, but suları).
        suffix = _possessive_suffix(form, possessive, needs_y=needs_y and form.text == stem)
        form.add(suffix, softening=softening, vowel_drop=vowel_drop)

    has_possessive = possessive is not None
    vowel_end = form.ends_with_vowel()
    # -n- after a possessive, -y- after a bare vowel stem, nothing otherwise.
    buffer = ("n" if has_possessive else "y") if vowel_end else ""
    if case != "nominative":
        h2 = ph.harmony_2(form.text)
        h4 = ph.harmony_4(form.text)
        if case == "accusative":
            form.add(buffer + h4, softening=softening, vowel_drop=vowel_drop)
        elif case == "dative":
            form.add(buffer + h2, softening=True, vowel_drop=vowel_drop)
        elif case == "locative":
            if vowel_end:
                form.text += ("n" if has_possessive else "") + "d" + h2
            else:
                form.add_d(h2)
        elif case == "ablative":
            if vowel_end:
                form.text += ("n" if has_possessive else "") + "d" + h2 + "n"
            else:
                form.add_d(h2 + "n")
        elif case == "genitive":
            # "araba" -> "arabanın", "kitabı" -> "kitabının", "kitap" -> "kitabın",
            # "su" -> "suyun" (the one stem that keeps a -y- even here)
            if needs_y and not has_possessive and form.text == stem:
                form.add("y" + h4 + "n", softening=softening, vowel_drop=vowel_drop)
            elif vowel_end:
                form.text += "n" + h4 + "n"
            else:
                form.add(h4 + "n", softening=softening, vowel_drop=vowel_drop)
        elif case == "instrumental":
            # "arabayla", "kitabıyla", "suyla", "evle" — never the -n- buffer
            form.text += ("y" if vowel_end else "") + "l" + h2

    if copula:
        h4 = ph.harmony_4(form.text)
        if form.ends_with_vowel():
            form.text += "d" + h4 + "r"
        else:
            form.text += ph.assimilate(form.text, "d" + h4 + "r")

    return form.text


def paradigm(
    stem: str,
    *,
    plural: bool = False,
    possessive: str | None = None,
    softening: bool = False,
    vowel_drop: bool = False,
    copula: bool = False,
) -> dict[str, str]:
    """Every case of one stem/plural/possessive combination, keyed by case."""
    return {
        case: decline(
            stem,
            plural=plural,
            possessive=possessive,
            case=case,
            copula=copula,
            softening=softening,
            vowel_drop=vowel_drop,
        )
        for case in CASES
    }


def full_paradigm(
    stem: str, *, softening: bool = False, vowel_drop: bool = False
) -> dict[str, dict[str, str]]:
    """The whole noun table: 4 stem shapes × 7 cases."""
    table: dict[str, dict[str, str]] = {}
    for label, plural, possessive in (
        ("tekil", False, None),
        ("çoğul", True, None),
        ("tekil iyelik", False, "3s"),
        ("çoğul iyelik", True, "3s"),
    ):
        table[label] = paradigm(
            stem,
            plural=plural,
            possessive=possessive,
            softening=softening,
            vowel_drop=vowel_drop,
        )
    return table
