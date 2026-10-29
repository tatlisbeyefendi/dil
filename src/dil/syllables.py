"""Syllables and hyphenation for Turkish.

Turkish syllabification is mostly regular: every syllable has exactly one
vowel and a single intervocalic consonant starts the next syllable. Loanwords
keep their onset clusters (``kalem-traş``, not ``kalemt-raş``), so a small list
of legal onsets is consulted.
"""

from __future__ import annotations

from . import phonetics as ph

#: Two-consonant onsets Turkish tolerates, mostly in loanwords.
ONSETS = frozenset(
    [
        "pr",
        "tr",
        "kr",
        "gr",
        "br",
        "dr",
        "fr",
        "vr",
        "pl",
        "kl",
        "gl",
        "bl",
        "fl",
        "st",
        "sp",
        "sk",
        "sf",
        "sm",
        "sn",
        "ps",
        "ks",
    ]
)


def _boundaries(word: str) -> list[int]:
    folded = ph.fold(word)
    vowel_positions = [index for index, char in enumerate(folded) if char in ph.VOWELS]
    if len(vowel_positions) < 2:
        return [len(word)]

    cuts: list[int] = []
    for left, right in zip(vowel_positions, vowel_positions[1:], strict=False):
        cluster = right - left - 1
        if cluster == 0:
            cuts.append(right)
        elif cluster == 1:
            cuts.append(right - 1)
        elif folded[right - 2 : right] in ONSETS:
            cuts.append(right - 2)
        else:
            cuts.append(right - 1)
    cuts.append(len(word))
    return cuts


def syllables(word: str) -> list[str]:
    """Split ``word`` into syllables, keeping punctuation attached.

    >>> syllables("kalemtraş")
    ['ka', 'lem', 'traş']
    """
    if not word:
        return []
    cuts = _boundaries(word)
    parts: list[str] = []
    start = 0
    for cut in cuts:
        if cut > start:
            parts.append(word[start:cut])
            start = cut
    if start < len(word):
        parts.append(word[start:])
    return parts


def count(word: str) -> int:
    """Number of syllables, which is also the number of vowels."""
    return len(syllables(word))


def hyphenate(word: str, separator: str = "-") -> str:
    """Hyphenate for line breaking, never leaving a one-letter syllable.

    >>> hyphenate("öğretmen")
    'öğ-ret-men'
    """
    parts = syllables(word)
    if len(parts) < 2:
        return word
    merged: list[str] = []
    for part in parts:
        if merged and (len(merged[-1]) < 2 or len(ph.vowels_in(part)) == 0):
            merged[-1] += part
        else:
            merged.append(part)
    return separator.join(merged)


def stress(word: str) -> int:
    """Index of the stressed syllable — penultimate, with Turkish exceptions.

    Turkish is largely final-stressed, but place names and a handful of
    adverbs and loanwords take the stress earlier; this returns a best guess.
    """
    total = count(word)
    if total < 2:
        return 0
    if ph.fold(word).endswith(("ma", "me")) and total >= 3:
        return total - 2
    return total - 1
