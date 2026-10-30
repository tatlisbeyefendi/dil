# Changelog

All notable changes are recorded here. The format follows [Keep a Changelog](https://keepachangelog.com/)
and the project uses [Semantic Versioning](https://semver.org/).

## [0.2.0] — 2026-10-30

Hâlâ **ağır geliştirme aşamasında** — ama üç büyük eksik kapandı.

### Eklenenler
- **`dil analyze`** — ters çözümleme. Kök ve özellik tahmini üretilir, kelime yeniden üretilir ve
  ancak birebir tutuyorsa kabul edilir (gidiş-dönüş kanıtı). Yumuşama (`kitabı` → `kitap`), ünlü
  düşmesi (`ağzında` → `ağız`) ve `de/ye` düzensizliği (`yiyemiyorum` → `ye`) geri alınır.
- **`dil lint`** — yazım sözlüğü, soru ekinin ayrı yazımı, sayı eki + kesme işareti (mevcut sayı
  motoruyla hesaplanır), noktalama ve kelime tekrarı; `--fix`, `--write` (`.bak` yedekli), `--json`.
- **`dil stats`** — kelime/cümle/hece sayıları, sözcük çeşitliliği, okuma süresi, harf ve kelime
  sıklığı ve **Ateşman (1997) okunabilirlik** puanı.
- CLI'da `--json` desteği yeni komutlarda da var; 244 → **317 test**.

### Düzeltmeler
- Ateşman katsayıları kaynağından doğrulandı (`198,825 − 40,175 × hece/kelime − 2,610 ×
  kelime/cümle`); ilk denemede yanlış hatırlanmıştı.

## [0.1.0] — 2026-10-30

> **Ağır geliştirme aşamasında.** İlk yayın; kuralların bir kısmı hâlâ yazılıyor ve
> bilinen hatalar var. Geri bildirim için issue açın.

### Added
- **Nouns** — 4 stem shapes × 7 cases in one call: plural, six possessives, cases, copula and
  their combinations (`kitaplarımızda`, `arabasıyla`, `sularına`).
- **Verbs** — six tenses (`-yor`, `-r`, `-di`, `-miş`, `-ecek`, `-meli`) × six persons, with
  negation, ability (`-ebil`) and questions; `de/ye/et/git/tat` handled as irregulars.
- **Numbers** — cardinal spelling (including `bin` and `yüz` without `bir`), ordinals,
  distributives, decimals, `words → int` parsing, and case suffixes with the apostrophe
  (`1923'te`, `6'ya`).
- **Syllables** — syllabification, hyphenation that never leaves a one-letter syllable, and a
  stress guess.
- **Phonetics** — vowel harmony (2- and 4-way), softening (`k → ğ`, but `g` after `n`),
  devoicing, vowel elision, Turkish-aware upper/lower casing for `ı/İ`.
- **Lexicon** — exception tables for stems that soften or drop a vowel.
- **CLI** — `noun`, `verb`, `number`, `syllables`, `sound`, `lexicon`, every one with `--json`.
- Inability (`-yA-mA`): `uyuyamıyorum`, `gelemem`, `gelemeyeceğim`.
- 244 tests, ruff-clean, CI on three operating systems × four Python versions.
