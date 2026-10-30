"""Text checking: only rules we can defend."""

from __future__ import annotations

import pytest

from dil.lint import apply_fixes, lint, summary


def codes(text: str) -> list[str]:
    return [issue.code for issue in lint(text)]


def test_clean_text_has_no_issues() -> None:
    assert lint("Bu cümle tamamen doğru yazılmış.") == []


@pytest.mark.parametrize(
    ("text", "code", "suggestion"),
    [
        ("yanlız kaldım", "IMLA001", "yalnız"),
        ("herşey yolunda", "IMLA001", "her şey"),
        ("birşey soracağım", "IMLA001", "bir şey"),
        ("tabiki gelirim", "IMLA001", "tabii ki"),
        ("demekki haklıymış", "IMLA001", "demek ki"),
        ("orjinal fikir", "IMLA001", "orijinal"),
        ("geldinmi diye sordu", "IMLA002", "geldin mi"),
        ("olurmu böyle", "IMLA002", "olur mu"),
        ("1923de kuruldu", "SAYI001", "1923'te"),
        ("6da buluşalım", "SAYI001", "6'da"),
        ("2000de geldi", "SAYI001", "2000'de"),
        ("bitti ...", "NOKTA003", "…"),
        ("çok  fazla", "NOKTA002", " "),
        ("gel , git", "NOKTA001", ","),
        ("ve ve gitti", "TEKRAR001", "ve"),
    ],
)
def test_each_rule_fires(text: str, code: str, suggestion: str) -> None:
    issues = lint(text)
    assert code in [issue.code for issue in issues]
    assert any(issue.suggestion == suggestion for issue in issues if issue.code == code)


@pytest.mark.parametrize("text", ["kim geldi", "cuma günü", "değil mi", "mide ağrısı"])
def test_mi_rule_does_not_split_real_words(text: str) -> None:
    assert "IMLA002" not in codes(text)


def test_repeated_words_that_are_deliberate_are_ignored() -> None:
    assert "TEKRAR001" not in codes("çok çok güzel bir gün")


def test_issue_positions_point_at_the_text() -> None:
    text = "herşey"
    issue = lint(text)[0]
    assert text[issue.start : issue.end] == "herşey"
    assert (issue.line, issue.column) == (1, 1)


def test_multiline_positions() -> None:
    issue = lint("ilk satır\nikinci yanlız satır")[0]
    assert (issue.line, issue.column) == (2, 8)


def test_apply_fixes_repairs_everything_fixable() -> None:
    text = "herşey yanlız 1923de oldu , ve ve bitti..."
    fixed, count = apply_fixes(text)
    assert count >= 5
    assert "her şey" in fixed
    assert "yalnız" in fixed
    assert "1923'te" in fixed
    assert fixed.count("ve") == 1
    assert "…" in fixed


def test_apply_fixes_is_idempotent() -> None:
    fixed, _ = apply_fixes("yanlız ve ve bitti ...")
    again, count = apply_fixes(fixed)
    assert again == fixed
    assert count == 0


def test_summary_counts_by_code() -> None:
    counts = summary(lint("yanlız 1923de..."))
    assert counts == {"IMLA001": 1, "NOKTA003": 1, "SAYI001": 1}


def test_numbers_keep_the_apostrophe_when_already_correct() -> None:
    assert "SAYI001" not in codes("1923'te kuruldu")


def test_unknown_words_are_left_alone() -> None:
    assert lint("xyzzy plugh") == []
