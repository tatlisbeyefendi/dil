"""Checking Turkish text: spelling, the apostrophe, punctuation and spacing.

Every rule here is one we can defend. Rules that cannot be decided without
understanding the sentence — ``de``/``da`` written apart or together, for
example — are deliberately **not** checked, rather than guessed at.

    >>> [issue.code for issue in lint("herşey yanlız 1923de oldu")]
    ['IMLA001', 'IMLA001', 'SAYI001']
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from .numbers import case_suffix
from .phonetics import fold

#: Misspellings that are settled, with the form the TDK writes.
CORRECTIONS: dict[str, str] = {
    "yanlız": "yalnız",
    "yalnış": "yanlış",
    "herkez": "herkes",
    "herkeş": "herkes",
    "birşey": "bir şey",
    "herşey": "her şey",
    "hiçbirşey": "hiçbir şey",
    "birçok": "birçok",
    "herzaman": "her zaman",
    "heryer": "her yer",
    "herhangibir": "herhangi bir",
    "demekki": "demek ki",
    "belkide": "belki de",
    "öyleki": "öyle ki",
    "tabiki": "tabii ki",
    "süpriz": "sürpriz",
    "orjinal": "orijinal",
    "şöför": "şoför",
    "asvalt": "asfalt",
    "labaratuar": "laboratuvar",
    "entellektüel": "entelektüel",
    "iddaa": "iddia",
    "makina": "makine",
    "klavuz": "kılavuz",
    "yanlızlık": "yalnızlık",
    "üstünkörü": "üstünkörü",
    "mütevazi": "mütevazı",
    "hıristiyan": "Hristiyan",
    "ateşli": "ateşli",
    "dahi": "dahi",
    "birçokları": "birçokları",
    "program": "program",
    "antreman": "antrenman",
    "eşortman": "eşofman",
    "kaçkın": "kaçkın",
    "snack": "snack",
}

#: Endings that mean a bare ``mi`` belongs to the previous word: "geldinmi".
VERB_ENDINGS = (
    "yor",
    "di",
    "dı",
    "du",
    "dü",
    "ti",
    "tı",
    "tu",
    "tü",
    "miş",
    "mış",
    "muş",
    "müş",
    "ecek",
    "acak",
    "eceğ",
    "acağ",
    "yim",
    "yım",
    "yiz",
    "yız",
    "sin",
    "sın",
    "sun",
    "sün",
    "niz",
    "nız",
    "nuz",
    "nüz",
    "lar",
    "ler",
    "m",
    "n",
    "k",
    "r",
)

#: Words that legitimately end in -mi and must not be split.
MI_EXCEPTIONS = frozenset(
    ["değil", "mi", "cuma?", "imi", "emmi", "gibi?", "kim", "mi?", "mide?", "mi?"]
)

_WORD = re.compile(r"[A-Za-zÇĞİÖŞÜçğıöşüâîûÂÎÛ0-9'’]+")
_MI_SPLIT = re.compile(r"^([A-Za-zÇĞİÖŞÜçğıöşüâîû]+?)(mi|mı|mu|mü)$", re.IGNORECASE)
_NUMBER_SUFFIX = re.compile(r"\b(\d{1,12}|[\d.]+)(['’]?)([a-zA-ZçğıöşüÇĞİÖŞÜ]{1,3})\b")
_DOUBLE_WORD = re.compile(r"\b(\w{2,})\s+\1\b", re.IGNORECASE)
_SPACE_BEFORE_PUNCT = re.compile(r"\s+([,.;:!?])")
_NO_SPACE_AFTER = re.compile(r"([,;:])(?=[^\s\d])")
_DOUBLE_SPACE = re.compile(r"[^\S\n]{2,}")
_ELLIPSIS = re.compile(r"\.\.\.+")

#: Numerals whose suffix we can verify: yönelme, bulunma, ayrılma, belirtme.
NUMBER_CASES = {
    "e": "dative",
    "a": "dative",
    "de": "locative",
    "da": "locative",
    "te": "locative",
    "ta": "locative",
    "den": "ablative",
    "dan": "ablative",
    "ten": "ablative",
    "tan": "ablative",
}


@dataclass(frozen=True)
class Issue:
    """One problem found in the text, with an optional replacement."""

    code: str
    message: str
    start: int
    end: int
    found: str
    suggestion: str
    line: int
    column: int
    fixable: bool = True

    def as_dict(self) -> dict[str, object]:
        return {
            "code": self.code,
            "message": self.message,
            "line": self.line,
            "column": self.column,
            "found": self.found,
            "suggestion": self.suggestion,
            "fixable": self.fixable,
        }


def _position(text: str, index: int) -> tuple[int, int]:
    line = text.count("\n", 0, index) + 1
    last_break = text.rfind("\n", 0, index)
    return line, index - last_break


def _fold(text: str) -> str:
    return fold(text)


def _check_misspellings(text: str) -> list[Issue]:
    issues: list[Issue] = []
    for match in _WORD.finditer(text):
        word = match.group(0)
        lowered = _fold(word)
        replacement = CORRECTIONS.get(lowered)
        if replacement is None or replacement == lowered:
            continue
        # keep the original casing of the first letter
        if word[:1].isupper():
            replacement = replacement[:1].upper() + replacement[1:]
        line, column = _position(text, match.start())
        issues.append(
            Issue(
                "IMLA001",
                f"yazım: «{word}» → «{replacement}»",
                match.start(),
                match.end(),
                word,
                replacement,
                line,
                column,
            )
        )
    return issues


def _check_mi(text: str) -> list[Issue]:
    issues: list[Issue] = []
    for match in _WORD.finditer(text):
        word = match.group(0)
        if word.lower() in MI_EXCEPTIONS:
            continue
        parts = _MI_SPLIT.match(word)
        if parts is None:
            continue
        base, particle = parts.group(1), parts.group(2)
        if len(base) < 3 or base.lower() in MI_EXCEPTIONS:
            continue
        if not _fold(base).endswith(VERB_ENDINGS):
            continue
        line, column = _position(text, match.start())
        issues.append(
            Issue(
                "IMLA002",
                f"soru eki ayrı yazılır: «{word}» → «{base} {particle}»",
                match.start(),
                match.end(),
                word,
                f"{base} {particle}",
                line,
                column,
            )
        )
    return issues


def _check_numbers(text: str) -> list[Issue]:
    from .numbers import read

    issues: list[Issue] = []
    for match in _NUMBER_SUFFIX.finditer(text):
        digits, apostrophe, suffix = match.group(1), match.group(2), match.group(3)
        lowered = _fold(suffix)
        case = NUMBER_CASES.get(lowered)
        if case is None:
            continue
        try:
            spoken = read(digits)
        except ValueError:
            continue
        expected = case_suffix(spoken.split()[-1], case)
        if lowered == _fold(expected) and apostrophe:
            continue
        if lowered == _fold(expected) and not apostrophe:
            suggestion = f"{digits}'{expected}"
            message = f"sayıya gelen ek kesme işaretiyle ayrılır: «{match.group(0)}»"
        elif lowered != _fold(expected) and apostrophe:
            suggestion = f"{digits}'{expected}"
            message = f"ek uyumu: «{match.group(0)}» → «{suggestion}»"
        else:
            suggestion = f"{digits}'{expected}"
            message = f"ek uyumu ve kesme: «{match.group(0)}» → «{suggestion}»"
        line, column = _position(text, match.start())
        issues.append(
            Issue(
                "SAYI001",
                message,
                match.start(),
                match.end(),
                match.group(0),
                suggestion,
                line,
                column,
            )
        )
    return issues


def _check_punctuation(text: str) -> list[Issue]:
    issues: list[Issue] = []
    for pattern, code, message in (
        (_SPACE_BEFORE_PUNCT, "NOKTA001", "noktalamadan önce boşluk olmaz"),
        (_DOUBLE_SPACE, "NOKTA002", "çift boşluk"),
        (_ELLIPSIS, "NOKTA003", "üç nokta «…» tek karakterdir"),
    ):
        for match in pattern.finditer(text):
            found = match.group(0)
            replacement = match.group(1) if match.groups() else (" " if code == "NOKTA002" else "…")
            line, column = _position(text, match.start())
            issues.append(
                Issue(code, message, match.start(), match.end(), found, replacement, line, column)
            )
    for match in _NO_SPACE_AFTER.finditer(text):
        line, column = _position(text, match.start())
        issues.append(
            Issue(
                "NOKTA004",
                "noktalama işaretinden sonra boşluk gerekir",
                match.start(),
                match.end(),
                match.group(0),
                match.group(0) + " ",
                line,
                column,
            )
        )
    return issues


def _check_repeats(text: str) -> list[Issue]:
    issues: list[Issue] = []
    for match in _DOUBLE_WORD.finditer(text):
        word = match.group(1)
        if word.lower() in {"çok", "pek", "çabuk", "yavaş", "hem", "ya"}:
            continue  # "çok çok", "ya ya" are deliberate repetitions
        line, column = _position(text, match.start())
        issues.append(
            Issue(
                "TEKRAR001",
                f"kelime iki kez yazılmış: «{word}»",
                match.start(),
                match.end(),
                match.group(0),
                word,
                line,
                column,
            )
        )
    return issues


def lint(text: str) -> list[Issue]:
    """Run every rule and return the issues, in reading order."""
    issues: list[Issue] = []
    issues.extend(_check_misspellings(text))
    issues.extend(_check_mi(text))
    issues.extend(_check_numbers(text))
    issues.extend(_check_punctuation(text))
    issues.extend(_check_repeats(text))
    issues.sort(key=lambda issue: (issue.start, issue.code))
    return issues


def apply_fixes(text: str, issues: list[Issue] | None = None) -> tuple[str, int]:
    """Apply the fixable issues, right to left so offsets stay valid.

    Returns the new text and how many replacements were made.
    """
    problems = [issue for issue in (issues if issues is not None else lint(text)) if issue.fixable]
    result = text
    for issue in sorted(problems, key=lambda item: item.start, reverse=True):
        result = result[: issue.start] + issue.suggestion + result[issue.end :]
    return result, len(problems)


def summary(issues: list[Issue]) -> dict[str, int]:
    """Issue counts per code, for the CLI footer."""
    counts: dict[str, int] = {}
    for issue in issues:
        counts[issue.code] = counts.get(issue.code, 0) + 1
    return dict(sorted(counts.items()))
