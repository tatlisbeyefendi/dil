"""Turkish phonology: vowels, harmony, consonant assimilation and softening.

Everything in the rest of the package leans on the handful of rules encoded
here, so this module is deliberately small and heavily tested.
"""

from __future__ import annotations

VOWELS = "aeıioöuü"

#: Vowels that make a suffix take "a" (art damak) rather than "e" (ön damak).
BACK_VOWELS = "aıou"
FRONT_VOWELS = "eiöü"
ROUNDED_VOWELS = "oöuü"
UNROUNDED_VOWELS = "aeıi"
HIGH_VOWELS = "ıiuü"
LOW_VOWELS = "aeoö"

#: Voiceless consonants: a following "d" becomes "t" (kitap -> kitapta).
VOICELESS = "pçtkfhsş"

#: Final consonants that soften before a vowel-initial suffix (kitap -> kitabı).
SOFTENING = {"p": "b", "ç": "c", "t": "d", "k": "ğ", "g": "ğ"}

#: Circumflexed vowels are read as their plain counterparts for harmony.
FOLD = {"â": "a", "î": "i", "û": "u", "ô": "o", "ê": "e"}

_LOWER = str.maketrans("Iİ", "ıi")
_UPPER = str.maketrans("iı", "İI")


def fold(word: str) -> str:
    """Lower-case ``word`` the Turkish way and strip circumflexes."""
    return word.translate(_LOWER).lower().translate(str.maketrans(FOLD))


def upper(text: str) -> str:
    """Upper-case ``text`` Turkish style: i -> İ, ı -> I."""
    return text.replace("i", "İ").replace("ı", "I").upper().translate(_UPPER)


def lower(text: str) -> str:
    """Lower-case ``text`` Turkish style: I -> ı, İ -> i."""
    return text.replace("I", "ı").replace("İ", "i").lower()


def vowels_in(word: str) -> str:
    """Return only the vowels of ``word``, in order."""
    return "".join(char for char in fold(word) if char in VOWELS)


def last_vowel(word: str) -> str:
    """Last vowel of ``word``; ``""`` when it has none (rare, e.g. initials)."""
    found = vowels_in(word)
    return found[-1] if found else ""


def ends_with_vowel(word: str) -> bool:
    return bool(word) and fold(word)[-1] in VOWELS


def starts_with_vowel(word: str) -> bool:
    return bool(word) and fold(word)[0] in VOWELS


def ends_with_voiceless(word: str) -> bool:
    return bool(word) and fold(word)[-1] in VOICELESS


def syllable_count(word: str) -> int:
    return len(vowels_in(word))


def is_monosyllabic(word: str) -> bool:
    return syllable_count(word) == 1


def harmony_2(word: str) -> str:
    """Two-way harmony: ``a`` or ``e`` (kitap -> a, ev -> e)."""
    vowel = last_vowel(word)
    if not vowel:
        return "a"
    return "a" if vowel in BACK_VOWELS else "e"


def harmony_4(word: str) -> str:
    """Four-way harmony: ``ı``, ``i``, ``u`` or ``ü`` (kitap -> ı, ev -> i)."""
    vowel = last_vowel(word)
    if vowel in "aı":
        return "ı"
    if vowel in "ei":
        return "i"
    if vowel in "ou":
        return "u"
    if vowel in ("ö", "ü"):
        return "ü"
    return "ı"


def high_counterpart(vowel: str) -> str:
    """The high vowel a vowel becomes before ``-yor`` (başla -> başlıyor)."""
    return {"a": "ı", "e": "i", "ı": "ı", "i": "i", "o": "u", "ö": "ü", "u": "u", "ü": "ü"}[vowel]


def soften(word: str) -> str:
    """Soften a final p/ç/t/k: ``kitap`` -> ``kitab``, ``renk`` -> ``reng``.

    ``k`` only becomes ``ğ`` after a vowel or a liquid — after ``n`` it is ``g``
    (``renk`` -> ``rengi``, ``çocuk`` -> ``çocuğu``).
    """
    if not word:
        return word
    head, tail = word[:-1], word[-1]
    replacement = SOFTENING.get(fold(tail) or tail, tail)
    if fold(tail) == "k" and fold(head)[-1:] == "n":
        replacement = "g"
    return head + replacement


def can_soften(word: str) -> bool:
    return bool(word) and (fold(word)[-1] in SOFTENING)


def drop_last_vowel(word: str) -> str:
    """Drop the vowel of the final syllable: ``ağız`` -> ``ağz``, ``şehir`` -> ``şehr``."""
    text = fold(word)
    for index in range(len(text) - 1, -1, -1):
        if text[index] in VOWELS and index > 0:
            return word[:index] + word[index + 1 :]
    return word


def assimilate(word: str, suffix: str) -> str:
    """Apply voiceless assimilation to a ``d``-initial suffix (``kitap`` + ``da``)."""
    if suffix and fold(suffix)[0] == "d" and ends_with_voiceless(word):
        return "t" + suffix[1:]
    return suffix
