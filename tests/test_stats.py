"""Measuring a text, including Ateşman's readability index."""

from __future__ import annotations

import pytest

from dil.stats import ATESMAN_LABELS, STOP_WORDS, hyphenation_report, measure, split_sentences

SAMPLE = (
    "Türkçe, sondan eklemeli bir dildir. Bu yüzden bir kökten onlarca kelime türetilebilir.\n\n"
    "Ekler, kelimenin cümledeki görevini belirler. Ünlü uyumu en belirgin ses olayıdır."
)


def test_counts() -> None:
    numbers = measure(SAMPLE)
    assert numbers.words == 23
    assert numbers.sentences == 4
    assert numbers.paragraphs == 2
    assert numbers.unique_words <= numbers.words


def test_averages() -> None:
    numbers = measure(SAMPLE)
    assert numbers.average_sentence_length == pytest.approx(5.75)
    assert 2.0 < numbers.average_syllables_per_word < 3.5
    assert numbers.average_word_length > 4


def test_atesman_matches_the_published_example() -> None:
    """Ateşman's mean text: 2.294 syllables/word, 14.584 words/sentence -> ~68.6."""
    from dil.stats import TextStats

    numbers = TextStats(0, 0, 1000, 500, 68, 1, 2294, "x")
    assert numbers.atesman == pytest.approx(68.6, abs=0.5)
    assert numbers.atesman_label == "orta güçlükte"


def test_atesman_is_clamped_and_labelled() -> None:
    for threshold, label in ATESMAN_LABELS:
        assert threshold >= 0
        assert label
    shortest = measure("Gel. Git. Bak.")
    assert 0 <= shortest.atesman <= 100


def test_empty_text_does_not_divide_by_zero() -> None:
    numbers = measure("")
    assert numbers.words == 0
    assert numbers.sentences == 0
    assert numbers.atesman == 0.0
    assert numbers.reading_time_minutes == 0


def test_stop_words_are_excluded_from_content_frequency() -> None:
    numbers = measure("ve ve bir bir kitap kitap kitap")
    words = [word for word, _ in numbers.content_word_frequency]
    assert "kitap" in words
    assert "ve" not in words
    assert "ve" in STOP_WORDS


def test_longest_word_and_syllables() -> None:
    numbers = measure("kısa kelime türetilebilir")
    assert numbers.longest_word == "türetilebilir"
    assert numbers.syllables > numbers.words


def test_sentences_split_on_punctuation_and_blank_lines() -> None:
    assert len(split_sentences("Bir. İki! Üç?")) == 3
    assert len(split_sentences("Bir\n\nİki")) == 2


def test_lexical_diversity_and_reading_time() -> None:
    numbers = measure("kelime kelime kelime")
    assert numbers.lexical_diversity == pytest.approx(1 / 3, abs=0.01)
    assert numbers.reading_time_minutes == pytest.approx(3 / 200)


def test_hyphenation_report_returns_syllables() -> None:
    rows = hyphenation_report("kalemtraş öğretmen", limit=2)
    assert rows[0][0] == "kalemtraş"
    assert "-" in rows[0][1]


def test_as_dict_has_the_headline_keys() -> None:
    payload = measure(SAMPLE).as_dict()
    for key in ("words", "sentences", "atesman", "atesman_label", "content_word_frequency"):
        assert key in payload
