"""The exception lexicon."""

from __future__ import annotations

from dil.lexicon import DEFAULT, Entry


def test_softening_words_are_known() -> None:
    assert DEFAULT.knows_softening("kitap")
    assert DEFAULT.knows_softening("çocuk")
    assert DEFAULT.knows_softening("ağaç")


def test_vowel_drop_words_are_known() -> None:
    assert DEFAULT.knows_drop("ağız")
    assert DEFAULT.knows_drop("şehir")
    assert not DEFAULT.knows_drop("kitap")


def test_unknown_words_have_no_flags() -> None:
    assert DEFAULT.flags("masa") == {"softening": False, "vowel_drop": False}


def test_flags_combine_both_tables() -> None:
    assert DEFAULT.flags("kitap")["softening"] is True
    assert DEFAULT.flags("şehir")["vowel_drop"] is True


def test_entries_cover_nouns_and_verbs() -> None:
    entries = DEFAULT.entries()
    kinds = {entry.kind for entry in entries}
    assert kinds == {"isim", "fiil"}
    assert all(isinstance(entry, Entry) for entry in entries)


def test_verb_entries_carry_a_note() -> None:
    verbs = [entry for entry in DEFAULT.entries() if entry.kind == "fiil"]
    assert verbs
    assert all(entry.note for entry in verbs)
