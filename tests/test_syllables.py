"""Syllables, hyphenation and the stress guess."""

from __future__ import annotations

import pytest

from dil import syllables as syl


@pytest.mark.parametrize(
    ("word", "expected"),
    [
        ("kalemtraş", ["ka", "lem", "traş"]),
        ("kitap", ["ki", "tap"]),
        ("öğretmen", ["öğ", "ret", "men"]),
        ("dostlar", ["dost", "lar"]),
        ("kardeş", ["kar", "deş"]),
        ("araba", ["a", "ra", "ba"]),
        ("ev", ["ev"]),
        ("kâğıt", ["kâ", "ğıt"]),
    ],
)
def test_syllables(word: str, expected: list[str]) -> None:
    assert syl.syllables(word) == expected


def test_count_matches_vowel_count() -> None:
    assert syl.count("Ankara") == 3
    assert syl.count("ev") == 1


@pytest.mark.parametrize(
    ("word", "expected"),
    [
        ("öğretmen", "öğ-ret-men"),
        ("kalemtraş", "ka-lem-traş"),
        ("kitap", "ki-tap"),
        ("ev", "ev"),
    ],
)
def test_hyphenate(word: str, expected: str) -> None:
    assert syl.hyphenate(word) == expected


def test_hyphenate_never_leaves_a_single_letter() -> None:
    for word in ("araba", "okul", "defter", "pencereden"):
        for part in syl.hyphenate(word).split("-"):
            assert len(part) >= 2 or part == word


def test_stress_defaults_to_the_last_syllable() -> None:
    assert syl.stress("kitap") == 1
    assert syl.stress("ev") == 0


def test_stress_moves_back_for_negatives() -> None:
    assert syl.stress("anlamama") == 2


def test_empty_word() -> None:
    assert syl.syllables("") == []
    assert syl.count("") == 0
    assert syl.hyphenate("") == ""
