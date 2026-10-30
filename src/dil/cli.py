"""Command line interface for ``dil`` — the Turkish language engine."""

from __future__ import annotations

import argparse
import contextlib
import json
import sys
import unicodedata
from pathlib import Path
from typing import Any

from . import __version__
from . import lint as linting
from . import numbers as num
from . import phonetics as ph
from . import stats as textstats
from . import syllables as syl
from .analyze import analyze
from .lexicon import DEFAULT as LEXICON
from .nouns import CASE_LABELS, CASES, POSSESSIVES, decline, full_paradigm
from .verbs import (
    PERSON_LABELS,
    PERSONS,
    TENSE_LABELS,
    TENSES,
    conjugate,
    full_table,
)

PROG = "dil"


# --------------------------------------------------------------------------- output


def _width(text: str) -> int:
    return sum(2 if unicodedata.east_asian_width(char) in "WF" else 1 for char in text)


def _pad(text: str, width: int) -> str:
    return text + " " * max(0, width - _width(text))


def render_table(headers: list[str], rows: list[list[str]], *, indent: str = "  ") -> str:
    """A plain, aligned table — no colour, no dependency, copy-paste friendly."""
    widths = [_width(header) for header in headers]
    for row in rows:
        for index, cell in enumerate(row):
            widths[index] = max(widths[index], _width(cell))
    lines = [
        indent
        + "  ".join(_pad(header, widths[index]) for index, header in enumerate(headers)).rstrip(),
        indent + "  ".join("-" * widths[index] for index in range(len(headers))),
    ]
    for row in rows:
        lines.append(
            indent + "  ".join(_pad(cell, widths[index]) for index, cell in enumerate(row)).rstrip()
        )
    return "\n".join(lines)


def _emit_json(payload: Any) -> None:
    json.dump(payload, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")


# --------------------------------------------------------------------------- noun


def cmd_noun(args: argparse.Namespace) -> int:
    stem = args.stem.lower()
    flags = LEXICON.flags(stem)
    softening = args.softening or flags["softening"]
    vowel_drop = args.drop_vowel or flags["vowel_drop"]

    if args.json:
        _emit_json(
            {
                "stem": stem,
                "softening": softening,
                "vowel_drop": vowel_drop,
                "forms": full_paradigm(stem, softening=softening, vowel_drop=vowel_drop),
            }
        )
        return 0

    soften_note = "yumuşama" if softening else "düz"
    drop_note = "ünlü düşmesi" if vowel_drop else "düşme yok"
    print(f"{stem}  ({soften_note} · {drop_note})")
    print()
    cases = [case for case in CASES if args.cases is None or case in args.cases]
    rows = []
    for label, forms in full_paradigm(stem, softening=softening, vowel_drop=vowel_drop).items():
        rows.append([label] + [forms[case] for case in cases])
    print(render_table([""] + [CASE_LABELS[case] for case in cases], rows))
    print()
    print(
        "  tek form: "
        + ", ".join(
            decline(
                stem,
                plural=args.plural,
                possessive=args.possessive,
                case=args.case,
                copula=args.copula,
                softening=softening,
                vowel_drop=vowel_drop,
            )
            for _ in (0,)
        )
    )
    return 0


# --------------------------------------------------------------------------- verb


def cmd_verb(args: argparse.Namespace) -> int:
    stem = args.stem.lower()
    if args.json:
        _emit_json(
            {
                "stem": stem,
                "negative": args.negative,
                "ability": args.ability,
                "table": full_table(stem, negative=args.negative, ability=args.ability),
                "questions": {
                    person: conjugate(
                        stem,
                        tense=args.tense,
                        person=person,
                        negative=args.negative,
                        ability=args.ability,
                        question=True,
                    )
                    for person in PERSONS
                },
            }
        )
        return 0

    print(
        f"{stem}  ({'olumsuz' if args.negative else 'olumlu'}"
        f"{' · yeterlilik' if args.ability else ''})"
    )
    print()
    table = full_table(stem, negative=args.negative, ability=args.ability)
    rows = [
        [TENSE_LABELS[tense]] + [table[tense][person] for person in PERSONS] for tense in TENSES
    ]
    print(render_table([""] + [PERSON_LABELS[person] for person in PERSONS], rows))
    print()
    print(
        "  soru: "
        + " · ".join(
            conjugate(
                stem,
                tense=args.tense,
                person=person,
                negative=args.negative,
                ability=args.ability,
                question=True,
            )
            for person in ("1s", "2s", "3p")
        )
    )
    return 0


# --------------------------------------------------------------------------- number


def cmd_number(args: argparse.Namespace) -> int:
    text = args.value.strip()
    try:
        spelled = num.read(text)
    except ValueError as error:
        print(f"{PROG}: {error}", file=sys.stderr)
        return 2

    try:
        value = num.to_number(spelled)
    except ValueError:  # pragma: no cover - only for decimals
        value = None

    payload: dict[str, Any] = {
        "input": text,
        "cardinal": spelled,
        "round_trip": value,
    }
    if value is not None and "," not in text:
        payload["ordinal"] = num.ordinal(value)
        payload["distributive"] = num.distributive(value)
        payload["suffixes"] = {
            case: num.suffix(value, case) for case in CASES if case != "nominative"
        }
    if args.json:
        _emit_json(payload)
        return 0

    print(f"{text} → {spelled}")
    if value is not None and "," not in text:
        print("  sıra      : " + num.ordinal(value))
        print("  üleştirme : " + num.distributive(value))
        print(
            "  ekler     : "
            + " · ".join(num.suffix(value, case) for case in ("dative", "locative", "ablative"))
        )
        if value >= 0 and value <= 100:
            print("  yüzde     : " + num.percentage(value))
    return 0


# --------------------------------------------------------------------------- syllables


def cmd_syllables(args: argparse.Namespace) -> int:
    words = args.words
    results = []
    for word in words:
        parts = syl.syllables(word)
        results.append(
            {
                "word": word,
                "syllables": parts,
                "count": len(parts),
                "hyphenated": syl.hyphenate(word),
                "stress": syl.stress(word) + 1 if parts else 0,
                "vowels": ph.vowels_in(word),
            }
        )
    if args.json:
        _emit_json(results)
        return 0
    for row in results:
        print(
            f"{row['word']:>16}  {'-'.join(row['syllables']):<24}"
            f"{row['count']} hece · vurgu {row['stress']}. hecede"
        )
    return 0


# --------------------------------------------------------------------------- phonetics


def cmd_sound(args: argparse.Namespace) -> int:
    word = args.word
    payload = {
        "word": word,
        "vowels": ph.vowels_in(word),
        "last_vowel": ph.last_vowel(word),
        "harmony_2": ph.harmony_2(word),
        "harmony_4": ph.harmony_4(word),
        "ends_with_vowel": ph.ends_with_vowel(word),
        "ends_with_voiceless": ph.ends_with_voiceless(word),
        "can_soften": ph.can_soften(word),
        "softened": ph.soften(word),
        "lexicon_softening": LEXICON.knows_softening(word),
        "lexicon_vowel_drop": LEXICON.knows_drop(word),
        "syllables": syl.syllables(word),
    }
    if args.json:
        _emit_json(payload)
        return 0
    print(f"{word}")
    for key, value in payload.items():
        if key != "word":
            print(f"  {key:<22}{value}")
    return 0


# --------------------------------------------------------------------------- lexicon


def cmd_lexicon(args: argparse.Namespace) -> int:
    entries = LEXICON.entries()
    if args.kind:
        entries = [entry for entry in entries if entry.kind == args.kind]
    if args.search:
        needle = args.search.lower()
        entries = [entry for entry in entries if needle in entry.stem]
    if args.json:
        _emit_json([entry.__dict__ for entry in entries])
        return 0
    print(
        render_table(
            ["kök", "tür", "not"],
            [[entry.stem, entry.kind, entry.note] for entry in entries],
        )
    )
    print()
    print(f"  {len(entries)} kayıt")
    return 0


# --------------------------------------------------------------------------- analyze


def cmd_analyze(args: argparse.Namespace) -> int:
    words = args.words
    results = {word: analyze(word, kind=args.kind, limit=args.limit) for word in words}
    if args.json:
        _emit_json({word: [item.as_dict() for item in rows] for word, rows in results.items()})
        return 0
    empty = 0
    for word, rows in results.items():
        print(f"  {word}")
        if not rows:
            print("      çözümleme bulunamadı (kök bilinmiyor veya türetme eki var)")
            empty += 1
            continue
        for index, item in enumerate(rows, start=1):
            print(f"    {index}. {item.describe():<52} {item.kind:<5} {item.score:5.1f}")
        print()
    return 0 if empty == 0 else 0


# --------------------------------------------------------------------------- lint


def _read_text(args: argparse.Namespace) -> str:
    if args.text is not None:
        return args.text
    if args.path is None:
        raise ValueError("bir dosya ya da --text ver")
    return Path(args.path).expanduser().read_text(encoding="utf-8")


def cmd_lint(args: argparse.Namespace) -> int:
    try:
        text = _read_text(args)
    except (OSError, ValueError) as error:
        print(f"{PROG}: {error}", file=sys.stderr)
        return 2

    issues = linting.lint(text)
    if args.json:
        _emit_json(
            {
                "issues": [issue.as_dict() for issue in issues],
                "summary": linting.summary(issues),
                "total": len(issues),
            }
        )
        return 0

    if not issues:
        print("  ✓ sorun bulunamadı")
        return 0

    print(
        render_table(
            ["yer", "kod", "açıklama"],
            [[f"{issue.line}:{issue.column}", issue.code, issue.message] for issue in issues],
        )
    )
    print()
    counts = linting.summary(issues)
    print("  " + " · ".join(f"{code} {count}" for code, count in counts.items()))

    if args.fix:
        fixed, applied = linting.apply_fixes(text, issues)
        if args.output or (args.path and args.write):
            target = Path(args.output or args.path).expanduser()
            if args.path and not args.output:
                backup = target.with_name(target.name + ".bak")
                backup.write_text(text, encoding="utf-8")
                print(f"  yedek: {backup}")
            target.write_text(fixed, encoding="utf-8")
            print(f"  {applied} düzeltme → {target}")
        else:
            print()
            sys.stdout.write(fixed)
    return 0


# --------------------------------------------------------------------------- stats


def cmd_stats(args: argparse.Namespace) -> int:
    try:
        text = _read_text(args)
    except (OSError, ValueError) as error:
        print(f"{PROG}: {error}", file=sys.stderr)
        return 2
    numbers = textstats.measure(text)
    if args.json:
        payload = numbers.as_dict()
        payload["hyphenation"] = textstats.hyphenation_report(text)
        _emit_json(payload)
        return 0

    print(f"  kelime        : {numbers.words} ({numbers.unique_words} tekil)")
    print(f"  cümle         : {numbers.sentences} · paragraf: {numbers.paragraphs}")
    print(
        f"  ort. cümle    : {numbers.average_sentence_length:.1f} kelime"
        f" · ort. kelime: {numbers.average_word_length:.1f} harf"
        f" · {numbers.average_syllables_per_word:.2f} hece"
    )
    print(f"  en uzun kelime: {numbers.longest_word} ({len(numbers.longest_word)} harf)")
    print(
        f"  çeşitlilik    : {numbers.lexical_diversity:.2f}"
        f" · okuma süresi: {numbers.reading_time_minutes:.1f} dk"
    )
    print(f"  Ateşman       : {numbers.atesman:.1f} → {numbers.atesman_label}")
    if numbers.content_word_frequency:
        print(
            "  sık kelimeler : "
            + ", ".join(f"{word} ({count})" for word, count in numbers.content_word_frequency[:8])
        )
    if numbers.sentences_over_40:
        print(f"  ⚠ {numbers.sentences_over_40} cümle 40 kelimeden uzun")
    return 0


# --------------------------------------------------------------------------- parser


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog=PROG,
        description="Türkçe dil motoru: çekim, sayı, hece, ses olayları.",
        epilog="Örnek: dil verb bak --tense future   ·   dil noun kitap   ·   dil number 1923",
    )
    parser.add_argument("--version", action="version", version=f"{PROG} {__version__}")
    parser.add_argument("--json", action="store_true", help="makine okunur JSON çıktı")
    subparsers = parser.add_subparsers(dest="command", required=True)

    noun = subparsers.add_parser("noun", aliases=["isim"], help="isim çekimi tablosu")
    noun.add_argument("stem", help="isim kökü (örn. kitap)")
    noun.add_argument("--plural", "-p", action="store_true", help="çoğul")
    noun.add_argument("--possessive", "-i", choices=POSSESSIVES, help="iyelik eki")
    noun.add_argument("--case", "-c", choices=CASES, default="nominative", help="hâl eki")
    noun.add_argument("--copula", action="store_true", help="-dir eki")
    noun.add_argument("--softening", action="store_true", help="ünsüz yumuşaması uygula")
    noun.add_argument("--drop-vowel", action="store_true", help="ünlü düşmesi uygula")
    noun.add_argument("--cases", nargs="+", choices=CASES, help="yalnız bu hâlleri göster")
    noun.set_defaults(func=cmd_noun)

    verb = subparsers.add_parser("verb", aliases=["fiil"], help="fiil çekim tablosu")
    verb.add_argument("stem", help="fiil kökü (örn. gel)")
    verb.add_argument("--tense", "-t", choices=TENSES, default="present", help="soru için zaman")
    verb.add_argument("--negative", "-n", action="store_true", help="olumsuz")
    verb.add_argument("--ability", "-a", action="store_true", help="yeterlilik (-ebil)")
    verb.set_defaults(func=cmd_verb)

    number = subparsers.add_parser("number", aliases=["sayı"], help="sayıyı yazıya dök")
    number.add_argument("value", help="sayı (1923, 1.234.567, 12,5)")
    number.set_defaults(func=cmd_number)

    word = subparsers.add_parser("syllables", aliases=["hece"], help="heceleme")
    word.add_argument("words", nargs="+", help="kelime(ler)")
    word.set_defaults(func=cmd_syllables)

    sound = subparsers.add_parser("sound", aliases=["ses"], help="ses olaylarını çözümle")
    sound.add_argument("word", help="kelime")
    sound.set_defaults(func=cmd_sound)

    analyzer = subparsers.add_parser(
        "analyze", aliases=["çözümle"], help="kelimeyi kök + özelliklerine ayır"
    )
    analyzer.add_argument("words", nargs="+", help="çözümlenecek kelime(ler)")
    analyzer.add_argument("--kind", "-k", choices=["isim", "fiil"], help="yalnız bu türü ara")
    analyzer.add_argument(
        "--limit", "-n", type=int, default=5, help="kelime başına en fazla kaç okuma"
    )
    analyzer.set_defaults(func=cmd_analyze)

    linter = subparsers.add_parser(
        "lint", aliases=["denetle"], help="metni denetle: yazım, ek, noktalama"
    )
    linter.add_argument("path", nargs="?", help="dosya")
    linter.add_argument("--text", "-t", help="metni doğrudan ver")
    linter.add_argument("--fix", action="store_true", help="düzeltilmiş metni üret")
    linter.add_argument("--write", action="store_true", help="dosyayı yerinde düzelt (.bak yedeği)")
    linter.add_argument("--output", "-o", help="düzeltilmiş metni buraya yaz")
    linter.set_defaults(func=cmd_lint)

    stats = subparsers.add_parser(
        "stats", aliases=["istatistik"], help="kelime, cümle ve okunabilirlik ölçümü"
    )
    stats.add_argument("path", nargs="?", help="dosya")
    stats.add_argument("--text", "-t", help="metni doğrudan ver")
    stats.set_defaults(func=cmd_stats)

    lexicon = subparsers.add_parser("lexicon", aliases=["sözlük"], help="istisna sözlüğü")
    lexicon.add_argument("--kind", choices=["isim", "fiil"], help="türe göre süz")
    lexicon.add_argument("--search", "-s", help="kök içinde ara")
    lexicon.set_defaults(func=cmd_lexicon)

    return parser


def _utf8_console() -> None:
    """Turkish output needs UTF-8 even on a Windows console."""
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            # A closed or redirected stream must not stop the tool.
            with contextlib.suppress(OSError, ValueError):  # pragma: no cover
                reconfigure(encoding="utf-8", errors="replace")


def main(argv: list[str] | None = None) -> int:
    _utf8_console()
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
