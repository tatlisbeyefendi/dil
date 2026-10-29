"""Numbers: spelling, ordinals, distributives, decimals and case suffixes."""

from __future__ import annotations

import pytest

from dil import numbers as num


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (0, "sıfır"),
        (1, "bir"),
        (10, "on"),
        (11, "on bir"),
        (42, "kırk iki"),
        (100, "yüz"),
        (200, "iki yüz"),
        (1000, "bin"),
        (2100, "iki bin yüz"),
        (1234567, "bir milyon iki yüz otuz dört bin beş yüz altmış yedi"),
        (10**9, "bir milyar"),
        (-5, "eksi beş"),
    ],
)
def test_cardinal(value: int, expected: str) -> None:
    assert num.cardinal(value) == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (1, "birinci"),
        (2, "ikinci"),
        (3, "üçüncü"),
        (4, "dördüncü"),
        (6, "altıncı"),
        (7, "yedinci"),
        (9, "dokuzuncu"),
        (10, "onuncu"),
        (20, "yirminci"),
        (100, "yüzüncü"),
        (1000, "bininci"),
        (10**6, "bir milyonuncu"),
    ],
)
def test_ordinal(value: int, expected: str) -> None:
    assert num.ordinal(value) == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (1, "birer"),
        (2, "ikişer"),
        (4, "dörder"),
        (5, "beşer"),
        (6, "altışar"),
        (20, "yirmişer"),
        (100, "yüzer"),
        (1000, "biner"),
    ],
)
def test_distributive(value: int, expected: str) -> None:
    assert num.distributive(value) == expected


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("12,5", "on iki virgül beş"),
        ("0,25", "sıfır virgül yirmi beş"),
        ("-0,25", "eksi sıfır virgül yirmi beş"),
        ("3,0", "üç virgül sıfır"),
    ],
)
def test_decimal(text: str, expected: str) -> None:
    assert num.decimal(text) == expected


def test_read_accepts_thousands_separators() -> None:
    assert num.read("1.234.567") == num.cardinal(1234567)
    assert num.read("1923") == "bin dokuz yüz yirmi üç"


def test_read_rejects_junk() -> None:
    with pytest.raises(ValueError):
        num.read("bin iki")
    with pytest.raises(ValueError):
        num.read("12a")


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("bin dokuz yüz yirmi üç", 1923),
        ("kırk iki", 42),
        ("yüz", 100),
        ("iki yüz", 200),
        ("bir milyon", 10**6),
        ("sıfır", 0),
        ("eksi beş", -5),
    ],
)
def test_to_number(text: str, expected: int) -> None:
    assert num.to_number(text) == expected


def test_to_number_rejects_unknown_words() -> None:
    with pytest.raises(ValueError):
        num.to_number("kırk fil")


@pytest.mark.parametrize(
    ("value", "case", "expected"),
    [
        (1923, "locative", "1923'te"),
        (1985, "ablative", "1985'ten"),
        (2000, "locative", "2000'de"),
        ("1.234", "locative", "1.234'te"),
        (6, "dative", "6'ya"),
        ("4", "dative", "4'e"),
        (100, "genitive", "100'ün"),
        (2, "dative", "2'ye"),
    ],
)
def test_suffix(value: int | str, case: str, expected: str) -> None:
    assert num.suffix(value, case) == expected


def test_suffix_rejects_unknown_case() -> None:
    with pytest.raises(ValueError):
        num.suffix(3, "locative-ish")


def test_percentage() -> None:
    assert num.percentage(40) == "yüzde kırk"
