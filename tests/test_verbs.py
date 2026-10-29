"""Verb conjugation: six tenses, six persons, negation, ability and questions."""

from __future__ import annotations

import pytest

from dil.verbs import PERSONS, TENSES, conjugate, paradigm

THIRD_PERSON = [
    ("de", "diyor", "der", "dedi", "demiş", "diyecek", "demeli"),
    ("ye", "yiyor", "yer", "yedi", "yemiş", "yiyecek", "yemeli"),
    ("et", "ediyor", "eder", "etti", "etmiş", "edecek", "etmeli"),
    ("git", "gidiyor", "gider", "gitti", "gitmiş", "gidecek", "gitmeli"),
    ("oku", "okuyor", "okur", "okudu", "okumuş", "okuyacak", "okumalı"),
    ("başla", "başlıyor", "başlar", "başladı", "başlamış", "başlayacak", "başlamalı"),
    ("gör", "görüyor", "görür", "gördü", "görmüş", "görecek", "görmeli"),
    ("bak", "bakıyor", "bakar", "baktı", "bakmış", "bakacak", "bakmalı"),
    ("yürü", "yürüyor", "yürür", "yürüdü", "yürümüş", "yürüyecek", "yürümeli"),
    ("çalış", "çalışıyor", "çalışır", "çalıştı", "çalışmış", "çalışacak", "çalışmalı"),
]


@pytest.mark.parametrize(("stem", "forms"), [(row[0], list(row[1:])) for row in THIRD_PERSON])
def test_third_person_across_every_tense(stem: str, forms: list[str]) -> None:
    assert [conjugate(stem, tense=tense, person="3s") for tense in TENSES] == forms


@pytest.mark.parametrize(
    ("person", "expected"),
    [
        ("1s", "geliyorum"),
        ("2s", "geliyorsun"),
        ("3s", "geliyor"),
        ("1p", "geliyoruz"),
        ("2p", "geliyorsunuz"),
        ("3p", "geliyorlar"),
    ],
)
def test_present_persons(person: str, expected: str) -> None:
    assert conjugate("gel", tense="present", person=person) == expected


@pytest.mark.parametrize(
    ("person", "expected"),
    [
        ("1s", "geldim"),
        ("2s", "geldin"),
        ("3s", "geldi"),
        ("1p", "geldik"),
        ("2p", "geldiniz"),
        ("3p", "geldiler"),
    ],
)
def test_past_persons(person: str, expected: str) -> None:
    assert conjugate("gel", tense="past", person=person) == expected


def test_future_softens_its_final_k() -> None:
    assert conjugate("gel", tense="future", person="1s") == "geleceğim"
    assert conjugate("bak", tense="future", person="1p") == "bakacağız"


def test_necessitative_takes_a_y_buffer() -> None:
    assert conjugate("oku", tense="necessitative", person="1s") == "okumalıyım"
    assert conjugate("oku", tense="necessitative", person="1p") == "okumalıyız"


@pytest.mark.parametrize(
    ("stem", "tense", "person", "expected"),
    [
        ("gel", "present", "1s", "gelmiyorum"),
        ("bak", "present", "3s", "bakmıyor"),
        ("oku", "present", "3s", "okumuyor"),
        ("gör", "present", "3s", "görmüyor"),
        ("gel", "aorist", "2s", "gelmezsin"),
        ("oku", "aorist", "3s", "okumaz"),
        ("bak", "aorist", "1p", "bakmayız"),
        ("gel", "past", "3s", "gelmedi"),
        ("gel", "evidential", "3s", "gelmemiş"),
        ("gel", "future", "3s", "gelmeyecek"),
        ("gel", "necessitative", "3s", "gelmemeli"),
    ],
)
def test_negation(stem: str, tense: str, person: str, expected: str) -> None:
    assert conjugate(stem, tense=tense, person=person, negative=True) == expected


@pytest.mark.parametrize(
    ("stem", "tense", "person", "expected"),
    [
        ("gel", "present", "1s", "gelebiliyorum"),
        ("gel", "aorist", "3s", "gelebilir"),
        ("oku", "future", "3s", "okuyabilecek"),
        ("et", "aorist", "1s", "edebilirim"),
        ("de", "present", "3s", "diyebiliyor"),
    ],
)
def test_ability(stem: str, tense: str, person: str, expected: str) -> None:
    assert conjugate(stem, tense=tense, person=person, ability=True) == expected


@pytest.mark.parametrize(
    ("stem", "tense", "person", "expected"),
    [
        ("gel", "present", "1s", "geliyor muyum"),
        ("gel", "present", "2s", "geliyor musun"),
        ("gel", "present", "3p", "geliyorlar mı"),
        ("gel", "past", "2s", "geldin mi"),
        ("gel", "past", "3p", "geldiler mi"),
        ("oku", "aorist", "1s", "okur muyum"),
        ("bak", "future", "1p", "bakacak mıyız"),
    ],
)
def test_questions(stem: str, tense: str, person: str, expected: str) -> None:
    assert conjugate(stem, tense=tense, person=person, question=True) == expected


def test_paradigm_has_every_person() -> None:
    forms = paradigm("gel", tense="aorist")
    assert set(forms) == set(PERSONS)
    assert forms["3p"] == "gelirler"


def test_bad_tense_and_person_are_rejected() -> None:
    with pytest.raises(ValueError):
        paradigm("gel", tense="imperative")
    with pytest.raises(ValueError):
        conjugate("gel", person="4s")
    with pytest.raises(ValueError):
        paradigm("gel", tense="aorist", negative=True, ability=True)
