"""Turkish verb conjugation: tense, person, negation, ability, questions.

>>> conjugate("gel", tense="present", person="1s")
'geliyorum'
>>> conjugate("bak", tense="future", person="1p")
'bakacağız'
"""

from __future__ import annotations

from . import phonetics as ph

TENSES = ("present", "aorist", "past", "evidential", "future", "necessitative")

PERSONS = ("1s", "2s", "3s", "1p", "2p", "3p")

TENSE_LABELS = {
    "present": "şimdiki zaman",
    "aorist": "geniş zaman",
    "past": "görülen geçmiş",
    "evidential": "duyulan geçmiş",
    "future": "gelecek zaman",
    "necessitative": "gereklilik",
}

PERSON_LABELS = {
    "1s": "ben",
    "2s": "sen",
    "3s": "o",
    "1p": "biz",
    "2p": "siz",
    "3p": "onlar",
}

#: Monosyllabic stems that take -Ir in the aorist instead of the usual -Ar.
AORIST_IR = frozenset(
    [
        "al",
        "bil",
        "bul",
        "dur",
        "gel",
        "gör",
        "kal",
        "ol",
        "öl",
        "san",
        "var",
        "ver",
        "vur",
        "yen",
        "den",
    ]
)

#: Stems whose aorist is irregular.
AORIST_IRREGULAR = {"de": "der", "ye": "yer", "et": "eder"}

#: de/ye keep an -i- before the ability suffix (diyebil-, yiyebil-).
ABILITY_STEM = {"de": "di", "ye": "yi"}

#: Stems that voice their final t before a vowel (etmek -> ediyor, gidecek, edebilir).
VOICING = {"et": "ed", "git": "gid", "tat": "tad"}


def _necessitative_suffix(stem: str) -> str:
    """-mAlI: the final vowel is always the unrounded high one (okumalı, görmeli)."""
    back = ph.harmony_2(stem)
    return "m" + back + "l" + ("ı" if back == "a" else "i")


def _aorist_base(stem: str) -> str:
    if stem in AORIST_IRREGULAR:
        return AORIST_IRREGULAR[stem]
    root = VOICING.get(stem, stem)
    if ph.ends_with_vowel(root):
        return root + "r"
    if ph.is_monosyllabic(stem) and stem not in AORIST_IR:
        return root + ph.harmony_2(root) + "r"
    return root + ph.harmony_4(root) + "r"


def _present_base(stem: str) -> str:
    root = VOICING.get(stem, stem)
    if ph.ends_with_vowel(root):
        last = ph.fold(root)[-1]
        return root[:-1] + ph.high_counterpart(last) + "yor"
    return root + ph.harmony_4(root) + "yor"


def _ability_base(stem: str) -> str:
    root = ABILITY_STEM.get(stem) or VOICING.get(stem, stem)
    buffer = "y" if ph.ends_with_vowel(root) else ""
    return root + buffer + ph.harmony_2(root) + "bil"


def _negative_base(stem: str) -> str:
    return stem + "m" + ph.harmony_2(stem)


def _ability_reduced(stem: str) -> str:
    """The stem inability is built on: -yA-, with no -bil- (uyuyamıyorum).

    Turkish cannot say *uyuyabilmiyorum* — negation shrinks the ability suffix to
    a single vowel, so "uyu" + "-ya-" + "-mı-" + "-yor" is the correct shape.
    """
    root = ABILITY_STEM.get(stem) or VOICING.get(stem, stem)
    buffer = "y" if ph.ends_with_vowel(root) else ""
    return root + buffer + ph.harmony_2(root)


def _type_a(base: str) -> dict[str, str]:
    """Personal endings of present, aorist, evidential and necessitative."""
    h2 = ph.harmony_2(base)
    h4 = ph.harmony_4(base)
    buffer = "y" if ph.ends_with_vowel(base) else ""
    plural_l = "l" + h2 + "r"
    return {
        "1s": base + buffer + h4 + "m",
        "2s": base + "s" + h4 + "n",
        "3s": base,
        "1p": base + buffer + h4 + "z",
        "2p": base + "s" + h4 + "n" + h4 + "z",
        "3p": base + plural_l,
    }


def _type_b(base: str) -> dict[str, str]:
    """Personal endings of the -di past, which has a paradigm of its own."""
    h2 = ph.harmony_2(base)
    h4 = ph.harmony_4(base)
    return {
        "1s": base + "m",
        "2s": base + "n",
        "3s": base,
        "1p": base + "k",
        "2p": base + "n" + h4 + "z",
        "3p": base + "l" + h2 + "r",
    }


def _future_paradigm(base: str) -> dict[str, str]:
    h2 = ph.harmony_2(base)
    h4 = ph.harmony_4(base)

    def soften(word: str) -> str:
        return word[:-1] + "ğ" if ph.fold(word)[-1:] == "k" else word

    return {
        "1s": soften(base) + h4 + "m",
        "2s": base + "s" + h4 + "n",
        "3s": base,
        "1p": soften(base) + h4 + "z",
        "2p": base + "s" + h4 + "n" + h4 + "z",
        "3p": base + "l" + h2 + "r",
    }


def _aorist_paradigm(stem: str) -> dict[str, str]:
    negative = _negative_base(stem)
    h2 = ph.harmony_2(negative)
    h4 = ph.harmony_4(negative)
    return {
        "1s": negative + "m",
        "2s": negative + "z" + "s" + h4 + "n",
        "3s": negative + "z",
        "1p": negative + "y" + h4 + "z",
        "2p": negative + "z" + "s" + h4 + "n" + h4 + "z",
        "3p": negative + "z" + "l" + h2 + "r",
    }


def paradigm(
    stem: str, *, tense: str = "present", negative: bool = False, ability: bool = False
) -> dict[str, str]:
    """All six persons of one stem/tense combination."""
    if tense not in TENSES:
        raise ValueError(f"unknown tense: {tense!r}")

    base = _ability_base(stem) if ability else stem
    # Negation always attaches to the plain stem, or to the reduced -yA- of an
    # ability verb; -bil- never survives next to -mA.
    negative_stem = _ability_reduced(stem) if ability else stem

    if negative:
        negative_base = _negative_base(negative_stem)
        if tense == "aorist":
            return _aorist_paradigm(negative_stem)
        if tense == "present":
            return _type_a(negative_base[:-1] + ph.harmony_4(negative_stem) + "yor")
        if tense == "past":
            return _type_b(
                negative_base + ph.assimilate(negative_base, "d" + ph.harmony_4(negative_base))
            )
        if tense == "evidential":
            return _type_a(negative_base + "m" + ph.harmony_4(negative_base) + "ş")
        if tense == "future":
            accented = ph.harmony_2(negative_base)
            return _future_paradigm(negative_base + "y" + accented + "c" + accented + "k")
        if tense == "necessitative":
            return _type_a(negative_base + _necessitative_suffix(negative_base))

    if tense == "present":
        return _type_a(_present_base(base))
    if tense == "aorist":
        return _type_a(_aorist_base(base))
    if tense == "past":
        return _type_b(base + ph.assimilate(base, "d" + ph.harmony_4(base)))
    if tense == "evidential":
        return _type_a(base + "m" + ph.harmony_4(base) + "ş")
    if tense == "future":
        base = VOICING.get(base, base)
        base = ABILITY_STEM.get(base, base)
        buffer = "y" if ph.ends_with_vowel(base) else ""
        accented = ph.harmony_2(base)
        return _future_paradigm(base + buffer + accented + "c" + accented + "k")
    if tense == "necessitative":
        return _type_a(base + _necessitative_suffix(base))
    raise ValueError(f"unknown tense: {tense!r}")  # pragma: no cover


def conjugate(
    stem: str,
    *,
    tense: str = "present",
    person: str = "1s",
    negative: bool = False,
    ability: bool = False,
    question: bool = False,
) -> str:
    """One full form, optionally turned into a question."""
    if person not in PERSONS:
        raise ValueError(f"unknown person: {person!r}")
    forms = paradigm(stem, tense=tense, negative=negative, ability=ability)
    if not question:
        return forms[person]

    third = forms["3s"]
    h4 = ph.harmony_4(third)
    particle = "m" + h4
    if tense == "past":
        # The -di past keeps its personal ending on the verb: "geldin mi".
        return f"{forms[person]} {particle}"
    if person == "3p":
        return f"{forms['3p']} {'m' + ph.harmony_4(forms['3p'])}"
    copula = {
        "1s": "y" + h4 + "m",
        "2s": "s" + h4 + "n",
        "3s": "",
        "1p": "y" + h4 + "z",
        "2p": "s" + h4 + "n" + h4 + "z",
    }[person]
    return f"{third} {particle}{copula}"


def full_table(
    stem: str, *, negative: bool = False, ability: bool = False
) -> dict[str, dict[str, str]]:
    """Every tense × person, which is what the CLI prints."""
    return {
        tense: paradigm(stem, tense=tense, negative=negative, ability=ability) for tense in TENSES
    }
