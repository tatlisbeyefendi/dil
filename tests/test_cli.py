"""The command line: exit codes, tables and JSON."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from dil.cli import build_parser, main


def test_parser_accepts_every_subcommand() -> None:
    parser = build_parser()
    for argv in (
        ["noun", "kitap"],
        ["verb", "gel"],
        ["number", "42"],
        ["syllables", "kalem"],
        ["sound", "kitap"],
        ["lexicon"],
    ):
        assert parser.parse_args(argv).command is not None


def test_noun_table_prints_a_form_for_every_case(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["noun", "kitap"]) == 0
    out = capsys.readouterr().out
    for form in ("kitabı", "kitaba", "kitapta", "kitaptan", "kitabın", "kitapla"):
        assert form in out


def test_noun_aliases_work(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["isim", "ev"]) == 0
    assert "evi" in capsys.readouterr().out


def test_noun_json_is_machine_readable(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["--json", "noun", "ağız", "--drop-vowel"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["stem"] == "ağız"
    assert payload["vowel_drop"] is True
    assert payload["forms"]["tekil"]["accusative"] == "ağzı"


def test_noun_uses_the_lexicon_automatically(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["noun", "kitap"]) == 0
    assert "yumuşama" in capsys.readouterr().out


def test_verb_table_has_six_tenses(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["verb", "gel"]) == 0
    out = capsys.readouterr().out
    assert "geliyorum" in out
    assert "geleceğim" in out
    assert "gelmeliyim" in out


def test_verb_negative_and_ability(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["verb", "oku", "--negative"]) == 0
    assert "okumuyorum" in capsys.readouterr().out
    assert main(["verb", "gel", "--ability"]) == 0
    assert "gelebiliyorum" in capsys.readouterr().out


def test_verb_json(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["--json", "verb", "bak", "--tense", "future"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["table"]["future"]["1s"] == "bakacağım"
    assert payload["questions"]["2s"] == "bakacak mısın"


def test_number_command(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["number", "1923"]) == 0
    out = capsys.readouterr().out
    assert "bin dokuz yüz yirmi üç" in out
    assert "1923'te" in out


def test_number_rejects_junk(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["number", "kırk iki"]) == 2
    assert "not a number" in capsys.readouterr().err


def test_number_decimal(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["number", "12,5"]) == 0
    assert "on iki virgül beş" in capsys.readouterr().out


def test_syllables_command(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["syllables", "kalemtraş", "öğretmen"]) == 0
    out = capsys.readouterr().out
    assert "ka-lem-traş" in out
    assert "öğ-ret-men" in out


def test_sound_command_reports_harmony(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["sound", "kitap"]) == 0
    out = capsys.readouterr().out
    assert "harmony_4" in out
    assert "kitab" in out


def test_lexicon_command_lists_and_filters(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["lexicon", "--search", "kitap"]) == 0
    out = capsys.readouterr().out
    assert "kitap" in out
    assert "kayıt" in out


def test_lexicon_json(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["--json", "lexicon", "--kind", "fiil"]) == 0
    rows = json.loads(capsys.readouterr().out)
    assert rows and all(row["kind"] == "fiil" for row in rows)


def test_version_flag_exits_zero(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exit_info:
        main(["--version"])
    assert exit_info.value.code == 0
    assert "dil" in capsys.readouterr().out


def test_missing_subcommand_exits_with_usage() -> None:
    with pytest.raises(SystemExit) as exit_info:
        main([])
    assert exit_info.value.code == 2


def test_analyze_command(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["analyze", "kitaplarımızda"]) == 0
    out = capsys.readouterr().out
    assert "kitap" in out
    assert "1. çoğul iyelik" in out


def test_analyze_json(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["--json", "analyze", "geldim", "--kind", "fiil"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["geldim"][0]["stem"] == "gel"
    assert payload["geldim"][0]["features"]["tense"] == "past"


def test_lint_command_from_text(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["lint", "--text", "herşey yanlız 1923de"]) == 0
    out = capsys.readouterr().out
    assert "IMLA001" in out
    assert "SAYI001" in out


def test_lint_clean_text(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["lint", "--text", "Bu cümle doğru."]) == 0
    assert "sorun bulunamadı" in capsys.readouterr().out


def test_lint_fix_prints_corrected_text(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["lint", "-t", "yanlız geldim ...", "--fix"]) == 0
    out = capsys.readouterr().out
    assert "yalnız" in out
    assert "…" in out


def test_lint_fix_writes_file_with_backup(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    target = tmp_path / "metin.txt"
    target.write_text("herşey yanlız", encoding="utf-8")
    assert main(["lint", str(target), "--fix", "--write"]) == 0
    assert target.read_text(encoding="utf-8") == "her şey yalnız"
    assert (tmp_path / "metin.txt.bak").read_text(encoding="utf-8") == "herşey yanlız"
    assert "yedek" in capsys.readouterr().out


def test_lint_json(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    target = tmp_path / "metin.txt"
    target.write_text("yanlız", encoding="utf-8")
    assert main(["--json", "lint", str(target)]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["total"] == 1
    assert payload["summary"] == {"IMLA001": 1}


def test_stats_command(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["stats", "--text", "Bir cümle. İki cümle."]) == 0
    out = capsys.readouterr().out
    assert "kelime" in out
    assert "Ateşman" in out


def test_stats_json(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["--json", "stats", "-t", "Bir cümle. İki cümle."]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["words"] == 4
    assert payload["sentences"] == 2
    assert "hyphenation" in payload


def test_missing_file_is_reported(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["stats", str(tmp_path / "yok.txt")]) == 2
    assert "dil" in capsys.readouterr().err


def test_lint_without_input_is_an_error(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["lint"]) == 2
