"""Vowel harmony, consonant assimilation and the other sound events."""

from __future__ import annotations

import pytest

from dil import phonetics as ph


@pytest.mark.parametrize(
    ("word", "expected"),
    [
        ("kitap", "a"),
        ("ev", "e"),
        ("okul", "u"),
        ("göz", "ö"),
        ("yüzük", "ü"),
        ("İstanbul", "u"),
    ],
)
def test_last_vowel(word: str, expected: str) -> None:
    assert ph.last_vowel(word) == expected


def test_vowels_in_handles_circumflex_and_uppercase() -> None:
    assert ph.vowels_in("kâğıt") == "aı"
    assert ph.vowels_in("İSTANBUL") == "iau"


@pytest.mark.parametrize(
    ("word", "expected"),
    [("kitap", "a"), ("ev", "e"), ("okul", "a"), ("göz", "e"), ("yüzük", "e")],
)
def test_harmony_2(word: str, expected: str) -> None:
    assert ph.harmony_2(word) == expected


@pytest.mark.parametrize(
    ("word", "expected"),
    [
        ("kitap", "ı"),
        ("ev", "i"),
        ("okul", "u"),
        ("göz", "ü"),
        ("yüzük", "ü"),
        ("araba", "ı"),
        ("kedi", "i"),
    ],
)
def test_harmony_4(word: str, expected: str) -> None:
    assert ph.harmony_4(word) == expected


@pytest.mark.parametrize(
    ("vowel", "expected"),
    [("a", "ı"), ("e", "i"), ("o", "u"), ("ö", "ü"), ("u", "u"), ("ü", "ü")],
)
def test_high_counterpart(vowel: str, expected: str) -> None:
    assert ph.high_counterpart(vowel) == expected


@pytest.mark.parametrize(
    ("word", "expected"),
    [
        ("kitap", "kitab"),
        ("ağaç", "ağac"),
        ("kanat", "kanad"),
        ("renk", "reng"),
        ("ev", "ev"),
    ],
)
def test_soften(word: str, expected: str) -> None:
    assert ph.soften(word) == expected


@pytest.mark.parametrize(
    ("word", "expected"),
    [("ağız", "ağz"), ("şehir", "şehr"), ("oğul", "oğl"), ("ev", "ev")],
)
def test_drop_last_vowel(word: str, expected: str) -> None:
    assert ph.drop_last_vowel(word) == expected


@pytest.mark.parametrize(
    ("word", "suffix", "expected"),
    [
        ("kitap", "da", "ta"),
        ("ağaç", "dan", "tan"),
        ("ev", "de", "de"),
        ("okul", "da", "da"),
    ],
)
def test_assimilate(word: str, suffix: str, expected: str) -> None:
    assert ph.assimilate(word, suffix) == expected


def test_uppercase_and_lowercase_are_turkish() -> None:
    assert ph.upper("istanbul") == "İSTANBUL"
    assert ph.lower("İSTANBUL") == "istanbul"
    assert ph.upper("ılık") == "ILIK"


def test_vowel_predicates() -> None:
    assert ph.ends_with_vowel("araba")
    assert not ph.ends_with_vowel("kitap")
    assert ph.ends_with_voiceless("kitap")
    assert not ph.ends_with_voiceless("ev")
    assert ph.starts_with_vowel("elma")
    assert not ph.starts_with_vowel("kitap")


def test_monosyllabic_and_counts() -> None:
    assert ph.is_monosyllabic("kar")
    assert not ph.is_monosyllabic("kalem")
    assert ph.syllable_count("kalemtraş") == 3


def test_empty_input_is_not_a_crash() -> None:
    assert ph.last_vowel("") == ""
    assert ph.harmony_2("") == "a"
    assert ph.harmony_4("") == "ı"
    assert ph.soften("") == ""
    assert not ph.ends_with_vowel("")
