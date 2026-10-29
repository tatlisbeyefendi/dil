# dil

**Türkçe dil motoru** — çekim, sayı, hece ve ses olayları. Sıfır bağımlılık, tamamen offline, Python 3.11+.

Türkçe'nin kurallarını tahmine bırakmaz: ünlü uyumu, ünsüz yumuşaması ve sertleşmesi, ünlü düşmesi, kaynaştırma harfleri ve kişi ekleri tek tek kodlanmıştır. `dil`, bir kelimenin bütün çekimlerini üretir — siz yazmadan önce.

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

## Neler yapar

| Komut | İş |
| --- | --- |
| `dil noun <kök>` | 4 şekil × 7 hâl isim çekim tablosu |
| `dil verb <kök>` | 6 zaman × 6 kişi fiil çekimi, olumsuzluk, yeterlilik, soru |
| `dil number <sayı>` | sayıyı yazıya döker, sıra/üleştirme eki ve hâl ekini hesaplar |
| `dil syllables <kelime>` | heceleme, tireleme, vurgu tahmini |
| `dil sound <kelime>` | ünlü uyumu, yumuşama, düşme — ses olaylarını çözümler |
| `dil lexicon` | istisna sözlüğü (yumuşayan ve ünlü düşüren kökler) |
| `--json` | her komut için makine okunur çıktı |

## Örnekler

Fiil çekimi — tek komut, bütün zamanlar:

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

Sayılar:

```
$ dil number 1.234.567
1.234.567 → bir milyon iki yüz otuz dört bin beş yüz altmış yedi
  sıra      : bir milyon iki yüz otuz dört bin beş yüz altmış yedinci
  üleştirme : bir milyon iki yüz otuz dört bin beş yüz altmış yedişer
  ekler     : 1.234.567'e · 1.234.567'de · 1.234.567'ten
```

Heceleme:

```
$ dil syllables kalemtraş öğretmen pencereden
       kalemtraş  ka-lem-traş             3 hece · vurgu 3. hecede
        öğretmen  öğ-ret-men              3 hece · vurgu 3. hecede
      pencereden  pen-ce-re-den           4 hece · vurgu 4. hecede
```

## Kütüphane olarak

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

## Kurallar nasıl kodlanmış

- **Ünlü uyumu** — iki yönlü (`a/e`) ve dört yönlü (`ı/i/u/ü`), `â î û` düz ünlü sayılır.
- **Ünsüz yumuşaması** — `p ç t k` → `b c d ğ`; `n`'den sonra `k` → `g` (`renk` → `rengi`).
  Yalnızca ünlüyle başlayan ek geldiğinde ve yalnızca kök üzerinde olur (`kitap` → `kitabı`,
  ama `kitapları`).
- **Ünsüz sertleşmesi** — `d` → `t`: `kitap` + `da` = `kitapta`.
- **Ünlü düşmesi** — `ağız` → `ağzı`, `şehir` → `şehri`; çoğul ekinden sonra uygulanmaz.
- **Kaynaştırma harfleri** — iyelikten sonra `-n-` (`arabasına`), düz ünlüyle biten kökten sonra
  `-y-` (`arabaya`), `su` gibi istisnalarda her yerde `-y-` (`suyu`, `suyun`).
- **Fiil çekimi** — `-yor`, `-r`, `-di`, `-miş`, `-ecek`, `-meli`; olumsuzluk, yeterlilik
  (`-ebil`) ve soru eki kişi çekimiyle birlikte.

Kurallara uymayan kökler `src/dil/lexicon.py` içindeki istisna listelerinde tutulur; sözlükte
olmayan bir kelime de sorunsuz çekilir, sadece istisnaları bilemez.

## Testler

```bash
python3 -m pytest      # 235 test
python3 -m ruff check .
```

Testler gerçek Türkçe formları doğrular: `kitabımızda`, `okumuyorum`, `görmeliler`,
`dörder`, `1923'te`, `ka-lem-traş`… Ayrıca üç işletim sistemi × dört Python sürümü için CI var.

## Sınırlar

- Bu bir **üretici** motordur: kök verirsiniz, çekimli biçimi alırsınız. Ters yön
  (bir yüzey biçimini kök + özellik olarak çözümlemek) henüz yok — yol haritasında.
- Heceleme bir sezgiseldir; alıntı kelimelerin ünsüz kümelerinde TDK kılavuzundan sapabilir.
- Vurgu tahmini son hece varsayımına dayanır, yer adları ve bazı zarflar farklıdır.

## Yol haritası

- [ ] `dil analyze` — yüzey biçimden kök ve özellik çözümlemesi (`kitaplarımızdakiler`)
- [ ] `dil lint` — metin denetimi: `de/da`, `ki`, `mi`, `herşey`, `yanlız` ve noktalama
- [ ] `dil stats` — okunabilirlik (Ateşman), kelime sıklığı, cümle uzunluğu
- [ ] `dil hyphenate` — dosya adı/için satır sonu tirelemesi ve `--max` genişlik

## Lisans

MIT — bkz. [LICENSE](LICENSE).
