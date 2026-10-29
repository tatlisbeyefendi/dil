"""Noun inflection: cases, plurals, possessives and their combinations."""

from __future__ import annotations

import pytest

from dil.nouns import CASES, decline, full_paradigm, paradigm


@pytest.mark.parametrize(
    ("case", "expected"),
    [
        ("nominative", "ev"),
        ("accusative", "evi"),
        ("dative", "eve"),
        ("locative", "evde"),
        ("ablative", "evden"),
        ("genitive", "evin"),
        ("instrumental", "evle"),
    ],
)
def test_regular_consonant_stem(case: str, expected: str) -> None:
    assert decline("ev", case=case) == expected


@pytest.mark.parametrize(
    ("case", "expected"),
    [
        ("nominative", "araba"),
        ("accusative", "arabayı"),
        ("dative", "arabaya"),
        ("locative", "arabada"),
        ("ablative", "arabadan"),
        ("genitive", "arabanın"),
        ("instrumental", "arabayla"),
    ],
)
def test_vowel_stem_uses_the_y_buffer(case: str, expected: str) -> None:
    assert decline("araba", case=case) == expected


@pytest.mark.parametrize(
    ("case", "expected"),
    [
        ("accusative", "kitabı"),
        ("dative", "kitaba"),
        ("locative", "kitapta"),
        ("ablative", "kitaptan"),
        ("genitive", "kitabın"),
        ("instrumental", "kitapla"),
    ],
)
def test_softening_stem(case: str, expected: str) -> None:
    assert decline("kitap", case=case, softening=True) == expected


def test_softening_is_off_by_default() -> None:
    assert decline("kitap", case="accusative") == "kitapı"


@pytest.mark.parametrize(
    ("case", "expected"),
    [
        ("accusative", "ağzı"),
        ("dative", "ağza"),
        ("locative", "ağızda"),
        ("ablative", "ağızdan"),
        ("genitive", "ağzın"),
    ],
)
def test_vowel_drop(case: str, expected: str) -> None:
    assert decline("ağız", case=case, vowel_drop=True) == expected


def test_vowel_drop_does_not_eat_the_plural_suffix() -> None:
    assert decline("ağız", plural=True, case="accusative", vowel_drop=True) == "ağızları"
    assert decline("ağız", plural=True, case="dative", vowel_drop=True) == "ağızlara"


@pytest.mark.parametrize(
    ("possessive", "expected"),
    [
        ("1s", "evim"),
        ("2s", "evin"),
        ("3s", "evi"),
        ("1p", "evimiz"),
        ("2p", "eviniz"),
        ("3p", "evleri"),
    ],
)
def test_possessives_on_a_consonant_stem(possessive: str, expected: str) -> None:
    assert decline("ev", possessive=possessive) == expected


@pytest.mark.parametrize(
    ("possessive", "expected"),
    [
        ("1s", "arabam"),
        ("2s", "araban"),
        ("3s", "arabası"),
        ("1p", "arabamız"),
        ("2p", "arabanız"),
        ("3p", "arabaları"),
    ],
)
def test_possessives_on_a_vowel_stem(possessive: str, expected: str) -> None:
    assert decline("araba", possessive=possessive) == expected


def test_possessive_plus_case_uses_the_n_buffer() -> None:
    assert decline("araba", possessive="3s", case="dative") == "arabasına"
    assert decline("araba", possessive="3s", case="locative") == "arabasında"
    assert decline("araba", possessive="3s", case="ablative") == "arabasından"
    assert decline("araba", possessive="3s", case="accusative") == "arabasını"
    assert decline("araba", possessive="3s", case="genitive") == "arabasının"
    assert decline("araba", possessive="3s", case="instrumental") == "arabasıyla"


def test_plural_plus_possessive() -> None:
    assert decline("kitap", plural=True, possessive="1p", case="locative", softening=True) == (
        "kitaplarımızda"
    )
    assert decline("ev", plural=True, possessive="3s", case="dative") == "evlerine"


def test_copula() -> None:
    assert decline("ev", copula=True) == "evdir"
    assert decline("kitap", copula=True) == "kitaptır"
    assert decline("araba", copula=True) == "arabadır"


def test_su_is_irregular() -> None:
    assert decline("su", case="accusative") == "suyu"
    assert decline("su", case="genitive") == "suyun"
    assert decline("su", case="instrumental") == "suyla"
    assert decline("su", case="locative") == "suda"
    assert decline("su", possessive="3s") == "suyu"
    assert decline("su", plural=True, possessive="3s", case="dative") == "sularına"


def test_proper_noun_flag_is_kept() -> None:
    assert decline("Ankara", case="locative") == "Ankarada"


def test_paradigm_covers_every_case() -> None:
    table = paradigm("ev")
    assert set(table) == set(CASES)
    assert table["genitive"] == "evin"


def test_full_paradigm_has_four_shapes() -> None:
    table = full_paradigm("kitap", softening=True)
    assert list(table) == ["tekil", "çoğul", "tekil iyelik", "çoğul iyelik"]
    assert table["çoğul iyelik"]["vergence" if False else "dative"] == "kitaplarına"


def test_bad_arguments_are_rejected() -> None:
    with pytest.raises(ValueError):
        decline("ev", case="prepositional")
    with pytest.raises(ValueError):
        decline("ev", possessive="4s")


def test_softening_never_applies_after_a_suffix() -> None:
    assert decline("kitap", plural=True, case="accusative", softening=True) == "kitapları"
