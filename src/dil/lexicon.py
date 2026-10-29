"""A compact lexicon of the Turkish words whose inflection is not predictable.

Only the irregulars live here: stems that soften their final consonant
(``kitap`` -> ``kitabı``), stems that drop the vowel of their last syllable
(``ağız`` -> ``ağzı``), and the verbs whose aorist has to be memorised.
``dil`` works without this file — it just gets fewer surprises when the stem
is listed.
"""

from __future__ import annotations

from dataclasses import dataclass

#: Final k/p/ç/t that voices before a vowel-initial suffix.
SOFTENING_NOUNS = [
    "ağaç",
    "bebek",
    "bıçak",
    "bilek",
    "böcek",
    "büyük",
    "cevap",
    "çiçek",
    "çocuk",
    "çorap",
    "dip",
    "dolap",
    "dudak",
    "ekmek",
    "erkek",
    "eşek",
    "hesap",
    "inek",
    "kabak",
    "kanat",
    "kaşık",
    "kayık",
    "kazak",
    "kelebek",
    "kilit",
    "kitap",
    "köpek",
    "kulak",
    "kurt",
    "küçük",
    "kuyruk",
    "mektup",
    "ocak",
    "orak",
    "renk",
    "sebep",
    "senet",
    "sokak",
    "tarak",
    "tat",
    "uçak",
    "umut",
    "yaprak",
    "yatak",
    "yelek",
    "yurt",
    "yüzük",
    "kâğıt",
    "kağıt",
]

#: Nouns whose last-syllable vowel disappears before a vowel-initial suffix.
VOWEL_DROP_NOUNS = [
    "ağız",
    "akıl",
    "alın",
    "asıl",
    "boyun",
    "burun",
    "fikir",
    "gönül",
    "göğüs",
    "isim",
    "karın",
    "kayıp",
    "nehir",
    "omuz",
    "oğul",
    "ömür",
    "özür",
    "resim",
    "sabır",
    "seyir",
    "şehir",
    "vakit",
    "zehir",
    "zihin",
]

#: Verbs whose forms have to be memorised.
VERB_NOTES = {
    "de": "der, diyor, dedi, diyecek — kök ünlüsü değişir",
    "ye": "yer, yiyor, yedi, yiyecek",
    "et": "eder, ediyor, etti",
    "git": "gider, gidiyor, gitti",
    "tat": "tadar, tadıyor, tattı",
}


@dataclass(frozen=True)
class Entry:
    """One row of the exception tables, as the CLI prints it."""

    stem: str
    kind: str = "isim"
    softening: bool = False
    vowel_drop: bool = False
    note: str = ""


class Lexicon:
    """What ``dil`` knows about a stem beyond the regular rules."""

    def __init__(self) -> None:
        self._softening = frozenset(SOFTENING_NOUNS)
        self._drop = frozenset(VOWEL_DROP_NOUNS)

    def knows_softening(self, stem: str) -> bool:
        return stem in self._softening

    def knows_drop(self, stem: str) -> bool:
        return stem in self._drop

    def flags(self, stem: str) -> dict[str, bool]:
        return {
            "softening": self.knows_softening(stem),
            "vowel_drop": self.knows_drop(stem),
        }

    def entries(self) -> list[Entry]:
        rows = [
            Entry(
                stem,
                softening=True,
                note="ünsüz yumuşaması: "
                + stem
                + " -> "
                + stem[:-1]
                + {"p": "b", "ç": "c", "t": "d", "k": "ğ", "g": "ğ"}.get(stem[-1], stem[-1]),
            )
            for stem in sorted(self._softening)
        ]
        rows += [Entry(stem, vowel_drop=True, note="ünlü düşmesi") for stem in sorted(self._drop)]
        rows += [Entry(stem, kind="fiil", note=note) for stem, note in sorted(VERB_NOTES.items())]
        return rows


DEFAULT = Lexicon()
