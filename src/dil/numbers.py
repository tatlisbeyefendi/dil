"""Numbers in Turkish: cardinal, ordinal, distributive, decimals and suffixes.

>>> cardinal(1234567)
'bir milyon iki yüz otuz dört bin beş yüz altmış yedi'
>>> ordinal(4)
'dördüncü'
>>> with_suffix(1923, "locative")
"1923'te"
"""

from __future__ import annotations

import re

from . import phonetics as ph

ONES = ("", "bir", "iki", "üç", "dört", "beş", "altı", "yedi", "sekiz", "dokuz")
TENS = ("", "on", "yirmi", "otuz", "kırk", "elli", "altmış", "yetmiş", "seksen", "doksan")
SCALES: tuple[tuple[int, str, bool], ...] = (
    (10**12, "trilyon", False),
    (10**9, "milyar", False),
    (10**6, "milyon", False),
    (1000, "bin", True),
    (100, "yüz", True),
)

#: Ordinals whose stem is irregular ("dört" -> "dörd", "altı" -> "altı").
ORDINAL_SOFTENING = {"dört": "dörd"}

#: Distributives with an irregular stem.
DISTRIBUTIVE_IRREGULAR = {"bir": "birer"}

_SMALL = {
    "sıfır": 0,
    "bir": 1,
    "iki": 2,
    "üç": 3,
    "dört": 4,
    "beş": 5,
    "altı": 6,
    "yedi": 7,
    "sekiz": 8,
    "dokuz": 9,
    "on": 10,
    "yirmi": 20,
    "otuz": 30,
    "kırk": 40,
    "elli": 50,
    "altmış": 60,
    "yetmiş": 70,
    "seksen": 80,
    "doksan": 90,
    "yüz": 100,
    "bin": 1000,
    "milyon": 10**6,
    "milyar": 10**9,
    "trilyon": 10**12,
}


def _below_thousand(value: int) -> list[str]:
    words: list[str] = []
    hundreds, rest = divmod(value, 100)
    if hundreds:
        words.append("yüz" if hundreds == 1 else f"{ONES[hundreds]} yüz")
    tens, ones = divmod(rest, 10)
    if tens:
        words.append(TENS[tens])
    if ones:
        words.append(ONES[ones])
    return words


def cardinal(number: int) -> str:
    """Spell an integer the way Turkish does — "bir yüz" and "bir bin" never happen."""
    if number < 0:
        return "eksi " + cardinal(-number)
    if number == 0:
        return "sıfır"

    words: list[str] = []
    remaining = number
    for scale, name, drop_one in SCALES:
        if remaining >= scale:
            count, remaining = divmod(remaining, scale)
            if drop_one and count == 1:
                # Turkish says "yüz", never "bir yüz" — but "iki yüz".
                words.append(name)
            else:
                words.extend(_below_thousand(count))
                words.append(name)
    words.extend(_below_thousand(remaining))
    return " ".join(word for word in words if word)


def percentage(number: int) -> str:
    """``40`` -> ``yüzde kırk``."""
    return "yüzde " + cardinal(number)


def ordinal(number: int) -> str:
    """``1`` -> ``birinci``, ``4`` -> ``dördüncü``, ``1000`` -> ``bininci``."""
    words = cardinal(number).split()
    last = words[-1]
    stem = ORDINAL_SOFTENING.get(last, last)
    if ph.ends_with_vowel(stem):
        suffix = "nc" + ph.harmony_4(last)
    else:
        if ph.fold(stem)[-1] == "t" and stem not in ORDINAL_SOFTENING:
            # "dört" -> "dördüncü", but "üç" -> "üçüncü" (no voicing there)
            stem = ph.soften(stem)
        suffix = ph.harmony_4(last) + "nc" + ph.harmony_4(last)
    words[-1] = stem + suffix
    return " ".join(words)


def distributive(number: int) -> str:
    """``2`` -> ``ikişer``, ``4`` -> ``dörder``."""
    words = cardinal(number).split()
    last = words[-1]
    if last in DISTRIBUTIVE_IRREGULAR:
        words[-1] = DISTRIBUTIVE_IRREGULAR[last]
        return " ".join(words)
    if ph.ends_with_vowel(last):
        words[-1] = last + "ş" + ph.harmony_2(last) + "r"
    else:
        stem = ph.soften(last) if ph.fold(last)[-1] == "t" else last
        words[-1] = stem + ph.harmony_2(stem) + "r"
    return " ".join(words)


def decimal(text: str) -> str:
    """``"12,5"`` -> ``on iki virgül beş``; ``"-0,25"`` -> ``eksi sıfır virgül yirmi beş``."""
    negative = text.strip().startswith("-")
    cleaned = text.strip().lstrip("-").replace(".", "").replace(" ", "")
    if "," not in cleaned:
        spelled = cardinal(int(cleaned))
        return ("eksi " + spelled) if negative else spelled
    whole, fraction = cleaned.split(",", 1)
    whole_words = cardinal(int(whole)) if whole else "sıfır"
    fraction_words = cardinal(int(fraction)) if fraction else ""
    spelled = f"{whole_words} virgül {fraction_words}".strip()
    return ("eksi " + spelled) if negative else spelled


_NUMBER_RE = re.compile(r"^-?\d{1,3}(\.\d{3})*(,\d+)?$|^-?\d+(,\d+)?$")


def read(text: str) -> str:
    """Spell any number-looking string, thousands separators included."""
    stripped = text.strip()
    if not _NUMBER_RE.match(stripped):
        raise ValueError(f"not a number: {text!r}")
    if "," in stripped:
        return decimal(stripped)
    return cardinal(int(stripped.replace(".", "")))


def to_number(text: str) -> int:
    """Parse spelled-out Turkish back into an integer.

    ``"bin dokuz yüz yirmi üç"`` -> ``1923``.
    """
    negative = text.strip().startswith("eksi")
    words = text.replace("eksi", "").split()
    total = 0
    current = 0
    for word in words:
        if word not in _SMALL:
            raise ValueError(f"unknown number word: {word!r}")
        value = _SMALL[word]
        if value == 100:
            current = (current or 1) * 100
        elif value >= 1000:
            total += (current or 1) * value
            current = 0
        else:
            current += value
    total += current
    return -total if negative else total


def suffix(number: int | str, case: str = "locative") -> str:
    """Attach a case suffix to a numeral, with the apostrophe Turkish requires.

    ``1923`` + locative -> ``1923'te``; ``6`` + dative -> ``6'ya``.
    """
    # An int is printed exactly as given ("1923'te"); a string is kept verbatim,
    # so "1.234.567" stays grouped if the caller wrote it that way.
    literal = str(number)
    spelled = read(literal) if "," not in literal else decimal(literal)
    tail = spelled.split()[-1]
    return f"{literal}'{case_suffix(tail, case)}"


def case_suffix(spoken: str, case: str = "locative") -> str:
    """The case ending a numeral is pronounced with: ``üç`` + locative -> ``te``."""
    h2 = ph.harmony_2(spoken)
    h4 = ph.harmony_4(spoken)
    vowel = ph.ends_with_vowel(spoken)
    if case == "accusative":
        return ("y" if vowel else "") + h4
    if case == "dative":
        return ("y" if vowel else "") + h2
    if case == "locative":
        return ph.assimilate(spoken, "d" + h2)
    if case == "ablative":
        return ph.assimilate(spoken, "d" + h2 + "n")
    if case == "genitive":
        return ("n" + h4 + "n") if vowel else (h4 + "n")
    if case == "instrumental":
        return ("y" if vowel else "") + "l" + h2
    if case == "nominative":
        return ""
    raise ValueError(f"unknown case: {case!r}")
