# Changelog

All notable changes are recorded here. The format follows [Keep a Changelog](https://keepachangelog.com/)
and the project uses [Semantic Versioning](https://semver.org/).

## [0.1.0] — 2026-10-30

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
