# dil

> ## ⚠️ AĞIR GELİŞTİRME AŞAMASINDA — BOL BOL HATA VAR, KUSURA BAKMAYIN
>
> Bu araç **deneysel** durumda. Kurallar hâlâ yazılıyor, ürettiği biçimlerin bir kısmı
> yanlış olabilir, sözlükteki istisnalar eksik. Bir kelimede hata görürseniz şaşırmayın:
> issue açın, birlikte düzeltelim. Hiçbir kritik işte tek başına güvenmeyin — çıktıyı
> gözünüzle doğrulayın.

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
| **`dil analyze`** | **kelimeyi kök + özelliklerine ayırır** (`kitaplarımızda` → `kitap + çoğul + 1. çoğul iyelik + bulunma`) |
| **`dil lint`** | **metni denetler**: yazım, sayı eki, soru eki, noktalama, tekrar · `--fix` ile düzeltir |
| **`dil stats`** | **ölçer**: kelime/cümle/hece, çeşitlilik, okuma süresi, Ateşman okunabilirlik |
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

## Ters yön: çözümleme

`dil analyze`, üreticiyi tersine çalıştırır: bir kök ve özellik kümesi tahmin eder, kelimeyi
yeniden üretir ve **ancak birebir tutuyorsa** çözümlemeyi kabul eder. Yumuşama ve ünlü düşmesi
de geri alınır (`çocuğuna` → `çocuk`, `ağzında` → `ağız`, `gidiyorlar` → `git`).

```
$ dil analyze kitaplarımızda gidiyorlar
  kitaplarımızda
    1. kitap + çoğul + 1. çoğul iyelik + bulunma            isim   22.9

  gidiyorlar
    1. git + şimdiki zaman + 3. çoğul                       fiil   15.0
```

## Metin denetimi

Yalnızca savunabildiğimiz kurallar: kesinleşmiş yazım hataları, soru ekinin ayrı yazımı,
sayılara gelen ek ve kesme işareti, noktalama ve kelime tekrarı. `de/da`nın ayrı mı bitişik mi
yazılacağı gibi cümle anlamı gerektiren kurallar **bilerek** yok — tahmin etmiyoruz.

```
$ dil lint --text "herşey yanlız 1923de oldu , ve ve bitti..."
  yer   kod        açıklama
  1:1   IMLA001    yazım: «herşey» → «her şey»
  1:8   IMLA001    yazım: «yanlız» → «yalnız»
  1:15  SAYI001    ek uyumu ve kesme: «1923de» → «1923'te»
  1:26  NOKTA001   noktalamadan önce boşluk olmaz
  1:29  TEKRAR001  kelime iki kez yazılmış: «ve»
  1:40  NOKTA003   üç nokta «…» tek karakterdir

$ dil lint metin.txt --fix --write      # .bak yedeği alır, dosyayı düzeltir
```

## Ölçüm ve okunabilirlik

Ateşman (1997) formülü — `198,825 − 40,175 × (hece/kelime) − 2,610 × (kelime/cümle)` — ile
metnin okunabilirlik düzeyi; 90-100 çok kolay, 70-89 kolay, 50-69 orta, 30-49 zor.

```
$ dil stats makale.txt
  kelime        : 1.284 (612 tekil)
  cümle         : 74 · paragraf: 12
  ort. cümle    : 17,4 kelime · ort. kelime: 6,1 harf · 2,63 hece
  en uzun kelime: sorumluluklarımızdan (21 harf)
  çeşitlilik    : 0,48 · okuma süresi: 6,4 dk
  Ateşman       : 61,2 → orta güçlükte
  sık kelimeler : türkçe (18), kelime (14), ekler (11), cümle (9)
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
python3 -m pytest      # 317 test
python3 -m ruff check .
```

Testler gerçek Türkçe formları doğrular: `kitabımızda`, `okumuyorum`, `görmeliler`,
`dörder`, `1923'te`, `ka-lem-traş`… Ayrıca üç işletim sistemi × dört Python sürümü için CI var.

## Sınırlar

- Bu bir **üretici** motordur: kök verirsiniz, çekimli biçimi alırsınız. Ters yön
  (bir yüzey biçimini kök + özellik olarak çözümlemek) henüz yok — yol haritasında.
- Heceleme bir sezgiseldir; alıntı kelimelerin ünsüz kümelerinde TDK kılavuzundan sapabilir.
- Vurgu tahmini son hece varsayımına dayanır, yer adları ve bazı zarflar farklıdır.

## Bilinen hatalar ve eksikler

Her şey bitmedi, bilerek yayınlıyorum — nerede tökezlediğini bileyim diye:

- **Çözümleme tam değil.** Yapım eki almış kelimeler (`kitaptaki`, `güzellik`) çözümlenemez;
  sözlükte olmayan köklerde birden çok okuma çıkabilir.
- **Denetim bilerek dar.** `de/da` ayrı yazımı, büyük harf kullanımı ve cümle düzeyindeki
  hatalar denetlenmiyor, çünkü bunlar bağlam ister.

- **Yapım ekleri yok.** `-ki`, `-lik`, `-ci`, `-siz` gibi türetme ekleri henüz çalışmıyor,
  yalnızca çekim var. `kitaptaki`, `güzellik`, `gözcü` üretilemez.
- **İstisna sözlüğü küçük.** ~90 kök tanımlı; listede olmayan bir kelimenin yumuşaması ya da
  ünlü düşmesi bilinemez (`--softening` / `--drop-vowel` ile elle verilebilir).
- **Birleşik zamanlar eksik.** `geliyormuşum`, `gelecekmişim`, `gelmiş olacağım` gibi
  katmerli yapılar yok.
- **Heceleme sezgisel.** Alıntı kelimelerin ünsüz kümelerinde TDK kılavuzundan sapabilir.
- **Vurgu kaba bir tahmin.** Yer adları ve bazı zarflar farklı davranır.
- **Ters yön yok.** Yüzey biçimden kök çözümlemesi (`kitaplarımızdakiler` → ?) henüz yok.

Bir hata bulursan **issue aç**: hangi girdi, ne çıktı, Türkçede doğrusu ne. Düzeltmesi genelde
tek satır.

## Yol haritası

- [x] `dil analyze` — yüzey biçimden kök ve özellik çözümlemesi
- [x] `dil lint` — metin denetimi: `mi`, `herşey`, `yanlız`, sayı ekleri, noktalama
- [x] `dil stats` — Ateşman okunabilirlik, kelime sıklığı, cümle uzunluğu
- [ ] yapım ekleri (`-ki`, `-lik`, `-ci`, `-siz`) ve `kitaptaki` gibi türetmeler
- [ ] birleşik zamanlar (`geliyormuşum`, `gelmiş olacağım`)
- [ ] `dil lint` için `de/da` ve büyük harf kuralları (bağlam gerektiriyor)

## Lisans

MIT — bkz. [LICENSE](LICENSE).
