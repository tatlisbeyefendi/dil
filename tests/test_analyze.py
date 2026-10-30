"""Reverse analysis: the generator run backwards, with a round-trip proof."""

from __future__ import annotations

import pytest

from dil.analyze import COMMON_STEMS, Analysis, analyze, stem_candidates


def top(word: str, kind: str | None = None) -> Analysis:
    rows = analyze(word, kind=kind)
    assert rows, f"{word} için çözümleme yok"
    return rows[0]


@pytest.mark.parametrize(
    ("word", "expected"),
    [
        ("kitaplarımızda", "kitap + çoğul + 1. çoğul iyelik + bulunma"),
        ("evde", "ev + bulunma"),
        ("arabasına", "araba + 3. tekil iyelik + yönelme"),
        ("şehrimizde", "şehir + 1. çoğul iyelik + bulunma"),
        ("suyu", "su + belirtme"),
    ],
)
def test_noun_readings(word: str, expected: str) -> None:
    assert top(word, "isim").describe() == expected


@pytest.mark.parametrize(
    ("word", "expected"),
    [
        ("geldim", "gel + görülen geçmiş + 1. tekil"),
        ("gidiyorlar", "git + şimdiki zaman + 3. çoğul"),
        ("okumuyorum", "oku + şimdiki zaman + 1. tekil + olumsuz"),
        ("gelebileceğim", "gel + gelecek zaman + 1. tekil + yeterlilik"),
        ("bakacak", "bak + gelecek zaman + 3. tekil"),
        ("yiyemiyorum", "ye + şimdiki zaman + 1. tekil + yeterlilik + olumsuz"),
        ("diyor", "de + şimdiki zaman + 3. tekil"),
    ],
)
def test_verb_readings(word: str, expected: str) -> None:
    assert top(word, "fiil").describe() == expected


def test_the_round_trip_regenerates_the_word() -> None:
    """Every analysis must be provable by generating the form again."""
    from dil.nouns import decline
    from dil.verbs import conjugate

    for word in ("kitaplarımızda", "geldim", "çocuğuna", "okumuyorum", "ağzında"):
        for row in analyze(word, limit=20):
            features = row.features
            if row.kind == "isim":
                again = decline(
                    row.stem,
                    plural=bool(features["plural"]),
                    possessive=features["possessive"],  # type: ignore[arg-type]
                    case=str(features["case"]),
                    copula=bool(features["copula"]),
                    softening=bool(features["softening"]),
                    vowel_drop=bool(features["vowel_drop"]),
                )
            else:
                again = conjugate(
                    row.stem,
                    tense=str(features["tense"]),
                    person=str(features["person"]),
                    negative=bool(features["negative"]),
                    ability=bool(features["ability"]),
                )
            assert again == word, f"{row.describe()} -> {again}"


@pytest.mark.parametrize(
    ("word", "stem", "marker"),
    [
        ("çocuğuna", "çocuk", "yönelme"),
        ("ağzında", "ağız", "bulunma"),
        ("şehrimizde", "şehir", "bulunma"),
    ],
)
def test_ambiguous_readings_still_find_the_right_stem(word: str, stem: str, marker: str) -> None:
    rows = analyze(word, kind="isim")
    assert rows[0].stem == stem
    assert any(row.features["case"] == marker or marker in row.describe() for row in rows)


def test_unknown_word_has_no_reading() -> None:
    assert analyze("zzzz") == []


def test_empty_input() -> None:
    assert analyze("   ") == []


def test_kind_filter_limits_results() -> None:
    assert all(row.kind == "isim" for row in analyze("evde", kind="isim"))
    assert all(row.kind == "fiil" for row in analyze("geldim", kind="fiil"))


def test_limit_caps_the_output() -> None:
    assert len(analyze("kitapları", limit=2)) <= 2


def test_common_stem_wins_over_a_longer_unknown_one() -> None:
    rows = analyze("kitaplarımızda")
    assert rows[0].stem == "kitap"
    assert "kitap" in COMMON_STEMS


def test_stem_candidates_undo_sound_changes() -> None:
    assert "git" in stem_candidates("gidiyor")
    assert "kitap" in stem_candidates("kitabı")
    assert "ağız" in stem_candidates("ağzında")


def test_as_dict_is_json_ready() -> None:
    payload = analyze("evde")[0].as_dict()
    assert payload["stem"] == "ev"
    assert payload["kind"] == "isim"
    assert isinstance(payload["features"], dict)
    assert isinstance(payload["describe"], str)
