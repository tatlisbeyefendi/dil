"""Reverse analysis: from a surface form back to a stem and its features.

``dil`` already knows how to *build* forms. Parsing is the same knowledge used
backwards: guess a stem, guess the features, generate the word again, and keep
the analysis only if the generator reproduces the input exactly. That round
trip is the proof — nothing is accepted on a hunch.

    >>> analyze("kitaplarımızda")[0].describe()
    'kitap + çoğul + 1. çoğul iyelik + bulunma'
    >>> analyze("okumuyorum")[0].describe()
    'oku + şimdiki zaman + 1. tekil + olumsuz'
"""

from __future__ import annotations

from dataclasses import dataclass, field
from itertools import product

from .lexicon import DEFAULT as LEXICON
from .nouns import CASES, POSSESSIVES, decline
from .phonetics import VOWELS
from .verbs import PERSONS, TENSES, conjugate

#: Stems worth preferring when several analyses fit equally well.
COMMON_STEMS = frozenset(
    [
        "adam",
        "ad",
        "araba",
        "ay",
        "ağaç",
        "ağız",
        "akıl",
        "alan",
        "altın",
        "ana",
        "anne",
        "ara",
        "araç",
        "arka",
        "arkadaş",
        "armut",
        "asker",
        "aslan",
        "ateş",
        "ayak",
        "ayran",
        "ayna",
        "ayrıntı",
        "aziz",
        "baba",
        "bahçe",
        "bakır",
        "bal",
        "balık",
        "banka",
        "bardak",
        "baş",
        "başarı",
        "bebek",
        "beden",
        "bekle",
        "benzin",
        "beraber",
        "beyaz",
        "biber",
        "bilek",
        "bilgi",
        "bin",
        "bina",
        "bir",
        "biçim",
        "bıçak",
        "böcek",
        "bu",
        "bulut",
        "burun",
        "bak",
        "başla",
        "bekle",
        "bil",
        "bul",
        "büyü",
        "çalış",
        "çek",
        "çık",
        "çiz",
        "çöz",
        "de",
        "dinle",
        "dön",
        "dur",
        "düşün",
        "düş",
        "et",
        "geç",
        "gel",
        "getir",
        "gir",
        "git",
        "gör",
        "götür",
        "gül",
        "iç",
        "in",
        "iste",
        "izle",
        "kal",
        "kalk",
        "kapa",
        "kes",
        "konuş",
        "koş",
        "kullan",
        "ol",
        "oku",
        "otur",
        "oyna",
        "sev",
        "söyle",
        "söyle",
        "sil",
        "uç",
        "uyu",
        "var",
        "ver",
        "vur",
        "yap",
        "yaz",
        "ye",
        "yen",
        "yıka",
        "yürü",
        "yüz",
        "al",
        "aç",
        "ara",
        "ağla",
        "anla",
        "at",
        "azalt",
        "öğren",
        "öğret",
        "öl",
        "pişir",
        "büyük",
        "bütün",
        "büro",
        "cam",
        "can",
        "cevap",
        "ceza",
        "cilt",
        "coğrafya",
        "cuma",
        "çaba",
        "çadır",
        "çalış",
        "çanta",
        "çay",
        "çek",
        "çiçek",
        "çizgi",
        "çocuk",
        "çorba",
        "çorap",
        "çözüm",
        "çuval",
        "dağ",
        "daire",
        "dakika",
        "dal",
        "dar",
        "dayı",
        "dede",
        "defter",
        "delil",
        "demir",
        "deniz",
        "ders",
        "destek",
        "dil",
        "dilek",
        "diş",
        "diyet",
        "diz",
        "doğa",
        "doktor",
        "dolap",
        "dost",
        "durak",
        "duvar",
        "düğün",
        "dünya",
        "düş",
        "düşün",
        "dün",
        "ebe",
        "ek",
        "ekmek",
        "el",
        "elbise",
        "eldiven",
        "emek",
        "emir",
        "enerji",
        "engel",
        "erik",
        "erkek",
        "ekmek",
        "eş",
        "eşek",
        "et",
        "etki",
        "ev",
        "evlat",
        "eylül",
        "ezber",
        "fasulye",
        "fayda",
        "felsefe",
        "fener",
        "fırsat",
        "fıstık",
        "fikir",
        "fil",
        "film",
        "fincan",
        "fiş",
        "fizik",
        "fotoğraf",
        "fırın",
        "fırça",
        "fiyat",
        "gece",
        "gemi",
        "genç",
        "gerçek",
        "gemi",
        "gez",
        "göz",
        "gökyüzü",
        "göl",
        "gölge",
        "gömlek",
        "gönül",
        "gün",
        "günah",
        "güneş",
        "güzel",
        "güç",
        "gümüş",
        "haber",
        "hafta",
        "hak",
        "hala",
        "halı",
        "halk",
        "hamur",
        "hane",
        "hangi",
        "hap",
        "harf",
        "hasta",
        "hata",
        "hava",
        "hayal",
        "hayat",
        "hayvan",
        "hazır",
        "hız",
        "hikâye",
        "hindistan?",
        "hoca",
        "hukuk",
        "hurma",
        "ırmak",
        "ışık",
        "iğne",
        "iklim",
        "ilaç",
        "ile",
        "ilgi",
        "imza",
        "inan",
        "inci",
        "insan",
        "iplik",
        "iş",
        "işçi",
        "istek",
        "iyi",
        "izin",
        "kabak",
        "kabuk",
        "kadeh",
        "kafa",
        "kağıt",
        "kâğıt",
        "kalem",
        "kalp",
        "kamyon",
        "kan",
        "kanat",
        "kanun",
        "kapı",
        "kaplan",
        "kar",
        "kara",
        "kardeş",
        "kare",
        "karın",
        "kas",
        "kase",
        "kasap",
        "kaş",
        "kat",
        "katman",
        "kavun",
        "kaya",
        "kayık",
        "kaz",
        "kazan",
        "keçi",
        "kedi",
        "kelime",
        "kemer",
        "kendi",
        "kent",
        "kervan",
        "kese",
        "keşif",
        "kılıç",
        "kırmızı",
        "kış",
        "kıyı",
        "kitap",
        "klasör",
        "koku",
        "kol",
        "koltuk",
        "konu",
        "kopya",
        "koru",
        "koşu",
        "kova",
        "koyun",
        "köpek",
        "köprü",
        "körü",
        "köy",
        "kral",
        "kule",
        "kum",
        "kumaş",
        "kural",
        "kurt",
        "kuş",
        "kutu",
        "kuzu",
        "küçük",
        "kül",
        "kültür",
        "küme",
        "lamba",
        "lastik",
        "lavabo",
        "leke",
        "lezzet",
        "liman",
        "limon",
        "lira",
        "liste",
        "lokma",
        "maaş",
        "maç",
        "macera",
        "mağaza",
        "mahalle",
        "makas",
        "makine",
        "masa",
        "masal",
        "matematik",
        "maya",
        "mayıs",
        "mektup",
        "melek",
        "mera",
        "merkez",
        "mesaj",
        "mesele",
        "meslek",
        "mevsim",
        "meyve",
        "milat",
        "mimar",
        "miras",
        "misafir",
        "model",
        "motor",
        "mudur",
        "mutfak",
        "muz",
        "müzik",
        "müdür",
        "nakit",
        "nane",
        "nehir",
        "nisan",
        "nokta",
        "not",
        "numara",
        "ocak",
        "oda",
        "odun",
        "ofis",
        "oğul",
        "ok",
        "okul",
        "okçu",
        "olay",
        "olta",
        "omuz",
        "onur",
        "orak",
        "ordu",
        "orman",
        "orta",
        "ortam",
        "ot",
        "obur",
        "oyun",
        "ödev",
        "öğle",
        "öğren",
        "öğretmen",
        "öğüt",
        "ölçü",
        "ömür",
        "ön",
        "örnek",
        "öykü",
        "özgür",
        "özür",
        "para",
        "parça",
        "parmak",
        "pasta",
        "patates",
        "patika",
        "pazar",
        "pehlivan",
        "pencere",
        "perde",
        "perşembe",
        "pilav",
        "pirinç",
        "piyasa",
        "plan",
        "polis",
        "portakal",
        "poşet",
        "proje",
        "puan",
        "radyo",
        "raf",
        "rahat",
        "rakip",
        "renk",
        "resim",
        "roman",
        "ruh",
        "rüya",
        "saat",
        "sabah",
        "sabır",
        "saç",
        "saha",
        "sahne",
        "sakat",
        "salata",
        "salı",
        "salon",
        "sanat",
        "sandalye",
        "sanık",
        "sarı",
        "satır",
        "savaş",
        "sayfa",
        "sayı",
        "sefer",
        "sel",
        "selam",
        "senet",
        "sepet",
        "serçe",
        "ses",
        "sergi",
        "sevgi",
        "sıcak",
        "sınav",
        "sınır",
        "sıra",
        "sigara",
        "silgi",
        "sinema",
        "sinir",
        "sirke",
        "sistem",
        "siyah",
        "soba",
        "sofra",
        "sokak",
        "solucan",
        "sonbahar",
        "soru",
        "sözlük",
        "söz",
        "su",
        "sucuk",
        "süngü",
        "süt",
        "şair",
        "şaka",
        "şapka",
        "şarap",
        "şarkı",
        "şehir",
        "şeker",
        "şekil",
        "şemsiye",
        "şehir",
        "şiir",
        "şimşek",
        "şirket",
        "şoför",
        "şube",
        "tabak",
        "tablo",
        "tahta",
        "takım",
        "takvim",
        "talep",
        "tamam",
        "tanık",
        "tarak",
        "tarım",
        "tarih",
        "tartı",
        "taş",
        "tat",
        "tatil",
        "tavşan",
        "tavan",
        "tavuk",
        "tayfa",
        "taze",
        "tebeşir",
        "tehlike",
        "tekne",
        "telefon",
        "telgraf",
        "temel",
        "temmuz",
        "tencere",
        "tepe",
        "tepsi",
        "terazi",
        "tercih",
        "tereyağı",
        "terzi",
        "tesis",
        "teşhis",
        "teşekkür",
        "tırnak",
        "ticaret",
        "tiyatro",
        "top",
        "toprak",
        "torba",
        "tost",
        "toz",
        "tuz",
        "tüfek",
        "tünel",
        "türkü",
        "türlü",
        "tütün",
        "uçak",
        "uçurtma",
        "ufuk",
        "uğur",
        "ulus",
        "umut",
        "un",
        "unvan",
        "uranyum",
        "ustura",
        "uyku",
        "uzay",
        "uzman",
        "ülke",
        "ümit",
        "üniversite",
        "ürün",
        "üzüm",
        "ütü",
        "vakit",
        "vali",
        "vana",
        "varlık",
        "vatan",
        "vazo",
        "vergi",
        "veri",
        "vezir",
        "vida",
        "vinç",
        "viraj",
        "vişne",
        "vitrin",
        "vücut",
        "yaka",
        "yalan",
        "yaprak",
        "yarış",
        "yasa",
        "yastık",
        "yaş",
        "yaşam",
        "yat",
        "yatak",
        "yavru",
        "yay",
        "yaya",
        "yaz",
        "yazı",
        "yelken",
        "yemek",
        "yemin",
        "yeni",
        "yer",
        "yeterli",
        "yıl",
        "yıldız",
        "yine",
        "yol",
        "yolcu",
        "yonca",
        "yorum",
        "yumurta",
        "yunus",
        "yurt",
        "yürüyüş",
        "yüz",
        "yüzük",
        "zafer",
        "zaman",
        "zambak",
        "zarf",
        "zeka",
        "zemin",
        "zeytin",
        "zil",
        "zincir",
        "zirve",
        "ziyaret",
        "zorluk",
    ]
)

#: Labels the CLI prints for feature names.
FEATURE_LABELS = {
    "plural": "çoğul",
    "possessive": "iyelik",
    "case": "hâl",
    "copula": "bildirme (-dir)",
    "tense": "zaman",
    "person": "kişi",
    "negative": "olumsuz",
    "ability": "yeterlilik",
}

POSSESSIVE_LABELS = {
    "1s": "1. tekil iyelik",
    "2s": "2. tekil iyelik",
    "3s": "3. tekil iyelik",
    "1p": "1. çoğul iyelik",
    "2p": "2. çoğul iyelik",
    "3p": "3. çoğul iyelik",
}

PERSON_LABELS = {
    "1s": "1. tekil",
    "2s": "2. tekil",
    "3s": "3. tekil",
    "1p": "1. çoğul",
    "2p": "2. çoğul",
    "3p": "3. çoğul",
}

TENSE_LABELS = {
    "present": "şimdiki zaman",
    "aorist": "geniş zaman",
    "past": "görülen geçmiş",
    "evidential": "duyulan geçmiş",
    "future": "gelecek zaman",
    "necessitative": "gereklilik",
}

CASE_LABELS = {
    "nominative": "yalın",
    "accusative": "belirtme",
    "dative": "yönelme",
    "locative": "bulunma",
    "ablative": "ayrılma",
    "genitive": "tamlayan",
    "instrumental": "vasıta",
}


@dataclass(frozen=True)
class Analysis:
    """One way to read a surface form."""

    stem: str
    kind: str
    features: dict[str, object] = field(default_factory=dict)
    score: float = 0.0

    @property
    def phonetic(self) -> dict[str, object]:
        """The two sound events the analysis had to assume."""
        return {
            key: self.features[key] for key in ("softening", "vowel_drop") if key in self.features
        }

    def describe(self) -> str:
        parts = [self.stem]
        for key in ("plural", "possessive", "case", "copula"):
            value = self.features.get(key)
            if key == "plural" and value:
                parts.append("çoğul")
            elif key == "possessive" and value:
                parts.append(POSSESSIVE_LABELS[str(value)])
            elif key == "case" and value and value != "nominative":
                parts.append(CASE_LABELS[str(value)])
            elif key == "copula" and value:
                parts.append("bildirme")
        for key in ("tense", "person", "ability", "negative"):
            value = self.features.get(key)
            if key == "tense" and value:
                parts.append(TENSE_LABELS[str(value)])
            elif key == "person" and value:
                parts.append(PERSON_LABELS[str(value)])
            elif key == "ability" and value:
                parts.append("yeterlilik")
            elif key == "negative" and value:
                parts.append("olumsuz")
        return " + ".join(parts)

    def as_dict(self) -> dict[str, object]:
        return {
            "stem": self.stem,
            "kind": self.kind,
            "features": self.features,
            "describe": self.describe(),
            "score": round(self.score, 2),
        }


def _score(stem: str, kind: str, features: dict[str, object]) -> float:
    """Rank readings: a known stem beats a long unknown one, always.

    Without this, the trivial reading of any word ("kitaplarımızda" = a noun whose
    stem is "kitaplarımızda") would win every time, because it explains nothing.
    """
    weight = 20.0 if stem in COMMON_STEMS else 0.0
    weight += 8.0 if LEXICON.knows_softening(stem) or LEXICON.knows_drop(stem) else 0.0
    weight += len(stem) * 0.3
    filled = sum(1 for value in features.values() if value not in (None, False, "nominative"))
    weight -= filled * 2.2
    if kind == "fiil":
        weight -= 1.5  # a noun reading is the safer default
    return weight


#: A surface form hides the stem: "kitabı" comes from "kitap", "gidiyor" from "git".
UNVOICE = {"b": "p", "c": "ç", "d": "t", "ğ": "k", "g": "k"}

#: de/ye look different once -yor or -yA- is attached: "diyor", "yiyemiyorum".
IRREGULAR_STEM_BACK = {"di": "de", "yi": "ye"}


def stem_candidates(word: str) -> list[str]:
    """Plausible stems: every prefix, its un-voiced twin, and a vowel put back.

    ``ağzında`` hides ``ağız`` (the vowel of the last syllable is gone) and
    ``gidiyor`` hides ``git`` (the final consonant voiced), so the search has to
    undo both changes to find the stem at all.
    """
    candidates: list[str] = []
    for split in range(2, len(word) + 1):
        stem = word[:split]
        candidates.append(stem)
        last = stem[-1]
        if last in UNVOICE:
            candidates.append(stem[:-1] + UNVOICE[last])
        if stem in IRREGULAR_STEM_BACK:
            candidates.append(IRREGULAR_STEM_BACK[stem])
        if len(stem) >= 3 and last not in VOWELS and stem[-2] not in VOWELS:
            # "ağz" -> "ağız": try putting a vowel back before the last consonant
            candidates.extend(stem[:-1] + vowel + last for vowel in "aeıiuü")
    return candidates


def noun_analyses(word: str) -> list[Analysis]:
    """Every noun reading whose generated form matches ``word`` exactly."""
    found: dict[tuple, Analysis] = {}
    for stem in stem_candidates(word):
        for plural, softening, vowel_drop, copula in product(
            (False, True), (False, True), (False, True), (False, True)
        ):
            if not plural and softening and vowel_drop:
                continue
            for possessive, case in product((None, *POSSESSIVES), CASES):
                features = {
                    "plural": plural,
                    "possessive": possessive,
                    "case": case,
                    "copula": copula,
                    "softening": softening,
                    "vowel_drop": vowel_drop,
                }
                try:
                    form = decline(
                        stem,
                        plural=plural,
                        possessive=possessive,
                        case=case,
                        copula=copula,
                        softening=softening,
                        vowel_drop=vowel_drop,
                    )
                except ValueError:  # pragma: no cover - defensive
                    continue
                if form != word:
                    continue
                bare = not any((plural, possessive, case != "nominative", copula))
                known = (
                    stem in COMMON_STEMS
                    or LEXICON.knows_softening(stem)
                    or (LEXICON.knows_drop(stem))
                )
                if bare and not known:
                    continue  # "the whole word is the stem" explains nothing
                key = (stem, plural, possessive, case, copula)
                candidate = Analysis(stem, "isim", features, _score(stem, "isim", features))
                if key not in found or candidate.score > found[key].score:
                    found[key] = candidate
    return list(found.values())


def verb_analyses(word: str) -> list[Analysis]:
    """Every verb reading whose generated form matches ``word`` exactly."""
    found: dict[tuple, Analysis] = {}
    for stem in stem_candidates(word):
        for tense, person, negative, ability in product(
            TENSES, PERSONS, (False, True), (False, True)
        ):
            features = {
                "tense": tense,
                "person": person,
                "negative": negative,
                "ability": ability,
            }
            try:
                form = conjugate(
                    stem,
                    tense=tense,
                    person=person,
                    negative=negative,
                    ability=ability,
                )
            except ValueError:  # pragma: no cover - defensive
                continue
            if form != word:
                continue
            key = (stem, tense, person, negative, ability)
            candidate = Analysis(stem, "fiil", features, _score(stem, "fiil", features))
            if key not in found or candidate.score > found[key].score:
                found[key] = candidate
    return list(found.values())


def analyze(word: str, *, kind: str | None = None, limit: int = 10) -> list[Analysis]:
    """All readings of ``word``, best first.

    ``kind`` restricts the search to ``"isim"`` or ``"fiil"``.
    """
    text = word.strip().lower()
    if not text:
        return []
    results: list[Analysis] = []
    if LEXICON.knows_softening(text) or kind in (None, "isim"):
        results.extend(noun_analyses(text))
    if kind in (None, "fiil"):
        results.extend(verb_analyses(text))
    results.sort(key=lambda item: (-item.score, item.stem, item.kind))
    return results[:limit]
