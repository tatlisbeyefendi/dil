"""Measuring a Turkish text: length, rhythm, vocabulary and readability.

The readability number is Ateşman's index (Ateşman, 1997), the first formula
built for Turkish. It adapts Flesch to Turkish word and sentence lengths:

    score = 198,825 - 40,175 × (hece / kelime) - 2,610 × (kelime / cümle)

The scale: 90-100 very easy, 70-89 easy, 50-69 moderate, 30-49 hard, 1-29 very hard.
"""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass, field

from .phonetics import fold, vowels_in
from .syllables import syllables

#: Very common words that say nothing about the topic; skipped in word counts.
STOP_WORDS = frozenset(
    [
        "acaba",
        "ama",
        "ancak",
        "artık",
        "asla",
        "aslında",
        "az",
        "bana",
        "bazen",
        "bazı",
        "belki",
        "ben",
        "benden",
        "beni",
        "benim",
        "beri",
        "beş",
        "bile",
        "bir",
        "biraz",
        "birçok",
        "biri",
        "birkaç",
        "birşey",
        "biz",
        "bizden",
        "bize",
        "bizim",
        "bu",
        "buna",
        "bunda",
        "bundan",
        "bunu",
        "bunun",
        "burada",
        "çok",
        "çünkü",
        "da",
        "daha",
        "dahi",
        "de",
        "defa",
        "değil",
        "diğer",
        "diye",
        "dolayı",
        "dolayısıyla",
        "edilecek",
        "eden",
        "ederek",
        "edilen",
        "eğer",
        "elbette",
        "en",
        "gibi",
        "hem",
        "hep",
        "hepsi",
        "her",
        "herhangi",
        "herkes",
        "hiç",
        "hiçbir",
        "için",
        "içinde",
        "iki",
        "ile",
        "ilgili",
        "ise",
        "işte",
        "kadar",
        "kendi",
        "kendine",
        "ki",
        "kim",
        "kimi",
        "kimse",
        "madem",
        "mi",
        "mu",
        "mü",
        "nasıl",
        "ne",
        "neden",
        "nedenle",
        "nerede",
        "nereye",
        "niçin",
        "nin",
        "nın",
        "o",
        "olan",
        "olarak",
        "oldu",
        "olduğu",
        "olduğunu",
        "olmadı",
        "olmak",
        "olması",
        "olmayan",
        "olup",
        "on",
        "ona",
        "ondan",
        "onlar",
        "onları",
        "onun",
        "orada",
        "oysa",
        "öyle",
        "sadece",
        "sanki",
        "sen",
        "senden",
        "seni",
        "senin",
        "siz",
        "sizden",
        "size",
        "sizin",
        "son",
        "sonra",
        "şey",
        "şu",
        "şuna",
        "şunda",
        "şundan",
        "şunu",
        "şunun",
        "tüm",
        "üç",
        "üzere",
        "var",
        "ve",
        "veya",
        "veyahut",
        "ya",
        "yalnız",
        "yani",
        "yapacak",
        "yapılan",
        "yapılmış",
        "yaptı",
        "yaptığı",
        "yedi",
        "yine",
        "yoksa",
        "zaten",
        "zira",
    ]
)

_WORD = re.compile(r"[A-Za-zÇĞİÖŞÜçğıöşüâîûÂÎÛ]+")
_SENTENCE_END = re.compile(r"[.!?…]+[\s\"”’)]*|\n\s*\n")

ATESMAN_LABELS = (
    (90, "çok kolay"),
    (70, "kolay"),
    (50, "orta güçlükte"),
    (30, "zor"),
    (0, "çok zor"),
)


@dataclass(frozen=True)
class TextStats:
    """Everything :func:`measure` can say about a text."""

    characters: int
    letters: int
    words: int
    unique_words: int
    sentences: int
    paragraphs: int
    syllables: int
    longest_word: str
    word_frequency: list[tuple[str, int]] = field(default_factory=list)
    content_word_frequency: list[tuple[str, int]] = field(default_factory=list)
    letter_frequency: list[tuple[str, int]] = field(default_factory=list)
    syllable_histogram: list[tuple[int, int]] = field(default_factory=list)
    sentences_over_40: int = 0

    @property
    def average_word_length(self) -> float:
        return self.letters / self.words if self.words else 0.0

    @property
    def average_sentence_length(self) -> float:
        return self.words / self.sentences if self.sentences else 0.0

    @property
    def average_syllables_per_word(self) -> float:
        return self.syllables / self.words if self.words else 0.0

    @property
    def reading_time_minutes(self) -> float:
        """Roughly 200 words a minute, the usual silent-reading figure."""
        return self.words / 200 if self.words else 0.0

    @property
    def lexical_diversity(self) -> float:
        return self.unique_words / self.words if self.words else 0.0

    @property
    def atesman(self) -> float:
        """Ateşman readability index, clamped to 0-100."""
        if not self.words or not self.sentences:
            return 0.0
        raw = (
            198.825
            - 40.175 * self.average_syllables_per_word
            - 2.610 * self.average_sentence_length
        )
        return max(0.0, min(100.0, raw))

    @property
    def atesman_label(self) -> str:
        score = self.atesman
        for threshold, label in ATESMAN_LABELS:
            if score >= threshold:
                return label
        return "çok zor"  # pragma: no cover

    def as_dict(self) -> dict[str, object]:
        return {
            "characters": self.characters,
            "letters": self.letters,
            "words": self.words,
            "unique_words": self.unique_words,
            "sentences": self.sentences,
            "paragraphs": self.paragraphs,
            "syllables": self.syllables,
            "average_word_length": round(self.average_word_length, 2),
            "average_sentence_length": round(self.average_sentence_length, 2),
            "average_syllables_per_word": round(self.average_syllables_per_word, 2),
            "lexical_diversity": round(self.lexical_diversity, 3),
            "reading_time_minutes": round(self.reading_time_minutes, 1),
            "longest_word": self.longest_word,
            "sentences_over_40": self.sentences_over_40,
            "atesman": round(self.atesman, 1),
            "atesman_label": self.atesman_label,
            "word_frequency": self.word_frequency,
            "content_word_frequency": self.content_word_frequency,
            "letter_frequency": self.letter_frequency,
            "syllable_histogram": self.syllable_histogram,
        }


def split_sentences(text: str) -> list[str]:
    """Split on sentence-final punctuation and blank lines, keeping it simple."""
    parts = [part.strip() for part in _SENTENCE_END.split(text)]
    return [part for part in parts if part]


def measure(text: str) -> TextStats:
    """Count everything worth counting in ``text``."""
    words = [word for word in _WORD.findall(text)]
    folded = [fold(word) for word in words]
    sentences = split_sentences(text)
    paragraphs = [block for block in re.split(r"\n\s*\n", text) if block.strip()]
    syllable_counts = [len(vowels_in(word)) for word in words]

    frequency = Counter(folded)
    content = Counter(word for word in folded if word not in STOP_WORDS and len(word) > 2)
    letters = Counter(character for word in folded for character in word)

    histogram = Counter(syllable_counts)
    longest = max(words, key=len, default="")

    return TextStats(
        characters=len(text),
        letters=sum(1 for character in text if character.isalpha()),
        words=len(words),
        unique_words=len(set(folded)),
        sentences=len(sentences),
        paragraphs=len(paragraphs),
        syllables=sum(syllable_counts),
        longest_word=longest,
        word_frequency=frequency.most_common(15),
        content_word_frequency=content.most_common(15),
        letter_frequency=letters.most_common(12),
        syllable_histogram=sorted(histogram.items()),
        sentences_over_40=sum(1 for sentence in sentences if len(_WORD.findall(sentence)) > 40),
    )


def hyphenation_report(text: str, *, limit: int = 5) -> list[tuple[str, str]]:
    """The hardest words to hyphenate, with their syllables — handy for layouts."""
    words = sorted({word for word in _WORD.findall(text)}, key=len, reverse=True)
    return [(word, "-".join(syllables(word))) for word in words[:limit]]
