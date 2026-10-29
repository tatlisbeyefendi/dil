# dil

> ## ⚠️ HEAVY DEVELOPMENT — EXPECT PLENTY OF BUGS, SORRY
>
> This is an experimental engine. The rule set is still being written, some forms it
> produces are wrong, and the exception lexicon is incomplete. If a word comes out
> broken, that is expected — open an issue and we will fix it together. Do not rely on
> this alone for anything critical; check the output by eye.

> ### ⚠️ AĞIR GELİŞTİRME AŞAMASINDA — BOL BOL HATA VAR, KUSURA BAKMAYIN
>
> (Türkçe: bu araç ağır geliştirme aşamasında, bol bol hata var, kusura bakmayın.)

**A Turkish language engine** — inflection, numbers, syllables and sound changes.
Zero dependencies, fully offline, Python 3.11+.

*dil* does not guess at Turkish morphology: vowel harmony, consonant softening and
devoicing, vowel elision, the buffer letters and the personal endings are all spelled
out as rules. Give it a stem and it produces every form of the word — before you have to
write them yourself.

![demo](docs/demo.svg)

## What it does

| Command | Job |
| --- | --- |
| `dil noun <stem>` | 4 stem shapes × 7 cases as one table |
| `dil verb <stem>` | 6 tenses × 6 persons, negation, ability, questions |
| `dil number <value>` | spells a number, plus its ordinal, distributive and case suffix |
| `dil syllables <word>` | syllabification, hyphenation, stress guess |
| `dil sound <word>` | dissects harmony, softening and elision |
| `dil lexicon` | the exception tables (softening and vowel-dropping stems) |
| `--json` | machine-readable output for every command |

## Examples

```
$ dil noun kitap
kitap  (yumuşama · düşme yok)

                yalın      belirtme     yönelme      bulunma       ayrılma        tamlayan      vasıta
  ------------  ---------  -----------  -----------  ------------  -------------  ------------  ------------
  tekil         kitap      kitabı       kitaba       kitapta       kitaptan       kitabın       kitapla
  çoğul         kitaplar   kitapları    kitaplara    kitaplarda    kitaplardan    kitapların    kitaplarla
  tekil iyelik  kitabı     kitabını     kitabına     kitabında     kitabından     kitabının     kitabıyla
  çoğul iyelik  kitapları  kitaplarını  kitaplarına  kitaplarında   kitaplarından  kitaplarının  kitaplarıyla
```

```
$ dil verb oku
                  ben         sen          o         biz         siz            onlar
  şimdiki zaman   okuyorum    okuyorsun    okuyor    okuyoruz    okuyorsunuz    okuyorlar
  geniş zaman     okurum      okursun      okur      okuruz      okursunuz      okurlar
  görülen geçmiş  okudum      okudun       okudu     okuduk      okudunuz       okudular
  duyulan geçmiş  okumuşum    okumuşsun    okumuş    okumuşuz    okumuşsunuz    okumuşlar
  gelecek zaman   okuyacağım  okuyacaksın  okuyacak  okuyacağız  okuyacaksınız  okuyacaklar
  gereklilik      okumalıyım  okumalısın   okumalı   okumalıyız  okumalısınız   okumalılar
```

```
$ dil number 1.234.567
1.234.567 → bir milyon iki yüz otuz dört bin beş yüz altmış yedi
  sıra      : bir milyon iki yüz otuz dört bin beş yüz altmış yedinci
  üleştirme : bir milyon iki yüz otuz dört bin beş yüz altmış yedişer
  ekler     : 1.234.567'e · 1.234.567'de · 1.234.567'ten
```

```
$ dil syllables kalemtraş öğretmen pencereden
       kalemtraş  ka-lem-traş             3 hece · vurgu 3. hecede
        öğretmen  öğ-ret-men              3 hece · vurgu 3. hecede
      pencereden  pen-ce-re-den           4 hece · vurgu 4. hecede
```

Turkish README: [README.tr.md](README.tr.md).

## As a library

```python
from dil.nouns import decline
from dil.verbs import conjugate
from dil import numbers

decline("kitap", plural=True, possessive="1p", case="locative", softening=True)
# 'kitaplarımızda'

conjugate("bak", tense="future", person="1p")
# 'bakacağız'

conjugate("gel", tense="present", person="1s", negative=True, question=True)
# 'gelmiyor muyum'

numbers.cardinal(1923)  # 'bin dokuz yüz yirmi üç'
numbers.ordinal(4)  # 'dördüncü'
numbers.suffix(1923, "locative")  # "1923'te"
numbers.to_number("kırk iki")  # 42
```

## How the rules are encoded

- **Vowel harmony** — two-way (`a/e`) and four-way (`ı/i/u/ü`); `â î û` count as plain vowels.
- **Consonant softening** — `p ç t k` become `b c d ğ`; after `n`, `k` becomes `g`
  (`renk` → `rengi`). It only happens before a vowel-initial suffix and only on the stem
  itself (`kitap` → `kitabı`, but `kitapları`).
- **Devoicing** — `d` becomes `t` after a voiceless consonant: `kitap` + `da` = `kitapta`.
- **Vowel elision** — `ağız` → `ağzı`, `şehir` → `şehri`; never after the plural suffix.
- **Buffer letters** — `-n-` after a possessive (`arabasına`), `-y-` after a vowel-final stem
  (`arabaya`), and everywhere for irregular stems such as `su` (`suyu`, `suyun`).
- **Verb morphology** — `-yor`, `-r`, `-di`, `-miş`, `-ecek`, `-meli`, combined with negation,
  ability (`-ebil`) and the question particle, which keeps its own personal endings.

Stems that break the rules live in the exception tables in `src/dil/lexicon.py`. A word that
is not listed still inflects correctly — it just cannot know its exceptions.

## Tests

```bash
python3 -m pytest      # 244 tests
python3 -m ruff check .
```

The suite asserts real Turkish forms: `kitabımızda`, `okumuyorum`, `görmeliler`, `dörder`,
`1923'te`, `ka-lem-traş`… CI runs three operating systems × four Python versions.

## Limits

- This is a **generator**: you supply a stem, you get forms. The reverse direction — parsing a
  surface form into stem + features — is not here yet, it is first on the roadmap.
- Syllabification is a heuristic; loanword onsets may differ from the TDK guide.
- The stress guess assumes final stress, which place names and some adverbs break.

## Known bugs and gaps

Nothing here is finished — I am publishing it on purpose, to find out where it breaks:

- **No derivational morphology.** `-ki`, `-lik`, `-ci`, `-siz` are not implemented; only
  inflection works. `kitaptaki`, `güzellik`, `gözcü` cannot be produced yet.
- **The exception lexicon is small.** About 90 stems are listed. For anything else the engine
  cannot know about softening or vowel elision — pass `--softening` / `--drop-vowel` yourself.
- **No compound tenses.** `geliyormuşum`, `gelecekmişim`, `gelmiş olacağım` are missing.
- **Syllabification is a heuristic** and may differ from the TDK guide on loanword clusters.
- **Stress is a rough guess.** Place names and some adverbs behave differently.
- **No parsing yet** — turning `kitaplarımızdakiler` back into stem + features is not here.

If you find a bug, open an issue with the input, what came out, and what Turkish actually says.
The fix is usually one line.

## Roadmap

- [ ] `dil analyze` — stem + feature analysis of a surface form (`kitaplarımızdakiler`)
- [ ] `dil lint` — text checking: `de/da`, `ki`, `mi`, `herşey`, `yanlız`, punctuation
- [ ] `dil stats` — Ateşman readability, word frequency, sentence length
- [ ] `dil hyphenate` — line breaking with `--max` width

## License

MIT — see [LICENSE](LICENSE).
