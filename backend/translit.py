"""
Romanized-Nepali → Devanagari transliteration for samachar.ai search.

Most Nepali users type searches in romanized Nepali ("nirvachan", "sarkar ko
nirnaya", "nepse aaja", "pradhanmantri"). Google News only indexes the
Devanagari coverage well, so we must convert those queries to Devanagari
BEFORE searching — and we must do it WITHOUT depending on a rate-limited LLM.

Strategy (deterministic, instant, free):
  1. A curated dictionary of the ~250 terms people actually search for in
     Nepali news (politics, economy, places, people, weather…). High precision.
  2. A rule-based phonetic transliterator for everything else. Best-effort.

Public API
----------
romanized_to_devanagari(text) -> str     full-query transliteration
looks_romanized(text)         -> bool     heuristic: is this romanized Nepali?
"""
import re

# ── 1. Curated news-term dictionary (romanized → Devanagari) ──────────
# Lowercased keys. Covers the high-frequency Nepali news search vocabulary,
# including schwa-deletion cases the phonetic engine can't infer.
DICT = {
    # governance / politics
    "sarkar": "सरकार", "sarakar": "सरकार", "nirvachan": "निर्वाचन",
    "nirbachan": "निर्वाचन", "chunav": "चुनाव", "matdan": "मतदान",
    "rajniti": "राजनीति", "rajneeti": "राजनीति", "dal": "दल",
    "neta": "नेता", "sansad": "संसद", "samsad": "संसद", "sambidhan": "संविधान",
    "samvidhan": "संविधान", "mantri": "मन्त्री", "pradhanmantri": "प्रधानमन्त्री",
    "pradhan": "प्रधान", "rastrapati": "राष्ट्रपति", "uparastrapati": "उपराष्ट्रपति",
    "sabhamukh": "सभामुख", "mukhyamantri": "मुख्यमन्त्री", "mantralaya": "मन्त्रालय",
    "nirnaya": "निर्णय", "nirnay": "निर्णय", "andolan": "आन्दोलन",
    "bandh": "बन्द", "hadtal": "हडताल", "bhrastachar": "भ्रष्टाचार",
    "akhtiyar": "अख्तियार", "adalat": "अदालत", "sarbochcha": "सर्वोच्च",
    "faisla": "फैसला", "mudda": "मुद्दा", "kanun": "कानुन", "ain": "ऐन",
    "gathabandhan": "गठबन्धन", "pratinidhi": "प्रतिनिधि", "sabha": "सभा",
    "rashtriya": "राष्ट्रिय", "rastriya": "राष्ट्रिय", "pradesh": "प्रदेश",
    "sthaniya": "स्थानीय", "palika": "पालिका", "nagarpalika": "नगरपालिका",
    "gaupalika": "गाउँपालिका", "mahanagar": "महानगर", "wada": "वडा",
    "mayor": "मेयर", "byabastha": "व्यवस्था",
    # parties
    "congress": "कांग्रेस", "kangres": "कांग्रेस", "emale": "एमाले",
    "maobadi": "माओवादी", "rabi": "रवि", "rastriya swatantra": "राष्ट्रिय स्वतन्त्र",
    "rsp": "रास्वपा", "raswapa": "रास्वपा", "balen": "बालेन",
    # economy / business
    "arthatantra": "अर्थतन्त्र", "artha": "अर्थ", "bajet": "बजेट",
    "budget": "बजेट", "bajar": "बजार", "share": "शेयर", "sheyar": "शेयर",
    "nepse": "नेप्से", "bank": "बैंक", "byaj": "ब्याज", "byaaj": "ब्याज",
    "karja": "कर्जा", "rin": "ऋण", "kar": "कर", "rajaswa": "राजस्व",
    "byapar": "व्यापार", "byapaar": "व्यापार", "udyog": "उद्योग",
    "lagani": "लगानी", "remittance": "रेमिट्यान्स", "remit": "रेमिट्यान्स",
    "mudra": "मुद्रा", "dollar": "डलर", "sun": "सुन", "sunko": "सुनको",
    "chandi": "चाँदी", "petrol": "पेट्रोल", "diesel": "डिजेल",
    "mahangi": "महँगी", "mahangee": "महँगी", "rastra bank": "राष्ट्र बैंक",
    "rastrabank": "राष्ट्र बैंक", "abadhi": "अवधि", "aayojana": "आयोजना",
    "aayojna": "आयोजना", "jalvidhyut": "जलविद्युत्", "jalbidhyut": "जलविद्युत्",
    "bidhyut": "विद्युत्", "bijuli": "बिजुली", "nea": "नेविप्रा",
    # geography / places
    "nepal": "नेपाल", "kathmandu": "काठमाडौं", "kathmandau": "काठमाडौं",
    "ktm": "काठमाडौं", "lalitpur": "ललितपुर", "bhaktapur": "भक्तपुर",
    "pokhara": "पोखरा", "biratnagar": "विराटनगर", "birgunj": "वीरगन्ज",
    "dharan": "धरान", "butwal": "बुटवल", "nepalgunj": "नेपालगन्ज",
    "dhangadi": "धनगढी", "chitwan": "चितवन", "janakpur": "जनकपुर",
    "hetauda": "हेटौंडा", "itahari": "इटहरी", "bharatpur": "भरतपुर",
    "madhesh": "मधेस", "madhes": "मधेस", "karnali": "कर्णाली",
    "gandaki": "गण्डकी", "lumbini": "लुम्बिनी", "koshi": "कोशी",
    "bagmati": "बागमती", "sudurpaschim": "सुदूरपश्चिम", "himal": "हिमाल",
    "tarai": "तराई", "terai": "तराई", "pahad": "पहाड",
    # weather / disaster
    "barsa": "वर्षा", "barsha": "वर्षा", "pani": "पानी", "badi": "बाढी",
    "baadi": "बाढी", "pahiro": "पहिरो", "bhukampa": "भूकम्प",
    "bhukamp": "भूकम्प", "mausam": "मौसम", "monsoon": "मनसुन",
    "mansun": "मनसुन", "hyundo": "हिउँदो", "garmi": "गर्मी", "jado": "जाडो",
    "agalo": "आगलागी", "bibhag": "विभाग",
    # health
    "swasthya": "स्वास्थ्य", "aspatal": "अस्पताल", "rog": "रोग",
    "mahamari": "महामारी", "khop": "खोप", "ausadhi": "औषधी",
    "dengue": "डेंगु", "corona": "कोरोना", "covid": "कोभिड",
    "doctor": "डाक्टर", "bigyan": "विज्ञान",
    # sports
    "khel": "खेल", "khelkud": "खेलकुद", "cricket": "क्रिकेट",
    "football": "फुटबल", "futsal": "फुटसल", "kheladi": "खेलाडी",
    "olympic": "ओलम्पिक", "match": "खेल", "team": "टोली", "toli": "टोली",
    # tech
    "prabidhi": "प्रविधि", "praviddhi": "प्रविधि", "internet": "इन्टरनेट",
    "mobile": "मोबाइल", "computer": "कम्प्युटर", "software": "सफ्टवेयर",
    "digital": "डिजिटल", "online": "अनलाइन", "social media": "सामाजिक सञ्जाल",
    "facebook": "फेसबुक", "tiktok": "टिकटक", "youtube": "युट्युब",
    # common words / time
    "samachar": "समाचार", "khabar": "खबर", "taja": "ताजा",
    "bartaman": "वर्तमान", "aaja": "आज", "aja": "आज", "hijo": "हिजो",
    "bholi": "भोलि", "abako": "अबको", "naya": "नयाँ", "ghatana": "घटना",
    "durghatana": "दुर्घटना", "samasya": "समस्या", "bikas": "विकास",
    "yojana": "योजना", "samaj": "समाज", "sikshya": "शिक्षा",
    "shiksha": "शिक्षा", "bidyalaya": "विद्यालय", "bidyarthi": "विद्यार्थी",
    "shikshak": "शिक्षक", "krishi": "कृषि", "kisan": "किसान",
    "kissan": "किसान", "anna": "अन्न", "dhan": "धान", "makai": "मकै",
    "yatayat": "यातायात", "sadak": "सडक", "bato": "बाटो", "rajmarga": "राजमार्ग",
    "biman": "विमान", "bimansthal": "विमानस्थल", "uddyan": "उद्यान",
    "paryatan": "पर्यटन", "paryatak": "पर्यटक", "manish": "मानिस",
    "janata": "जनता", "nagarik": "नागरिक", "mahila": "महिला",
    "purush": "पुरुष", "bal": "बाल", "yuva": "युवा", "budha": "बुढा",
    "prahari": "प्रहरी", "police": "प्रहरी", "sena": "सेना", "army": "सेना",
    "suraksha": "सुरक्षा", "apradh": "अपराध", "hatya": "हत्या",
    "chori": "चोरी", "thuna": "थुना", "pakrau": "पक्राउ",
}

# ── 2. Phonetic transliteration tables ────────────────────────────────
_CONS = {
    "ksh": "क्ष", "gy": "ज्ञ", "shr": "श्र", "chh": "छ",
    "kh": "ख", "gh": "घ", "ng": "ङ", "ch": "च", "jh": "झ",
    "th": "थ", "dh": "ध", "ph": "फ", "bh": "भ", "sh": "श", "ss": "ष",
    "k": "क", "g": "ग", "c": "च", "j": "ज", "t": "त", "d": "द",
    "n": "न", "p": "प", "f": "फ", "b": "ब", "m": "म", "y": "य",
    "r": "र", "l": "ल", "v": "व", "w": "व", "s": "स", "h": "ह",
}
_VOWEL_IND = {
    "aa": "आ", "ai": "ऐ", "au": "औ", "ee": "ई", "ii": "ई",
    "oo": "ऊ", "uu": "ऊ", "a": "अ", "i": "इ", "u": "उ", "e": "ए", "o": "ओ",
}
_VOWEL_MAT = {
    "aa": "ा", "ai": "ै", "au": "ौ", "ee": "ी", "ii": "ी",
    "oo": "ू", "uu": "ू", "a": "", "i": "ि", "u": "ु", "e": "े", "o": "ो",
}
_HALANT = "्"
_ASCII = re.compile(r"^[a-z]+$")


def _phonetic_word(w):
    """Best-effort phonetic transliteration of a single romanized word."""
    out = []
    i, n = 0, len(w)
    while i < n:
        cons = None
        for ln in (3, 2, 1):
            seg = w[i:i + ln]
            if seg in _CONS:
                cons = (seg, _CONS[seg])
                break
        if cons:
            i += len(cons[0])
            out.append(cons[1])
            vow = None
            for ln in (2, 1):
                seg = w[i:i + ln]
                if seg in _VOWEL_MAT:
                    vow = (seg, _VOWEL_MAT[seg])
                    break
            if vow:
                i += len(vow[0])
                if vow[1]:
                    out.append(vow[1])
            # No explicit vowel → keep inherent 'a' (Nepali retains schwa);
            # bare consonant matches Devanagari word-final convention too.
        else:
            vow = None
            for ln in (2, 1):
                seg = w[i:i + ln]
                if seg in _VOWEL_IND:
                    vow = (seg, _VOWEL_IND[seg])
                    break
            if vow:
                i += len(vow[0])
                out.append(vow[1])
            else:
                i += 1  # skip unknown char
    return "".join(out)


def _convert_word(w):
    lw = w.lower()
    if lw in DICT:
        return DICT[lw]
    if _ASCII.match(lw) and len(lw) >= 2:
        return _phonetic_word(lw)
    return w


def romanized_to_devanagari(text):
    """
    Convert a romanized-Nepali query to Devanagari.

    Multi-word queries are converted token-by-token: dictionary hits map to
    exact Devanagari, the rest go through the phonetic engine. Two-word
    dictionary phrases (e.g. 'rastra bank') are matched first.
    """
    text = (text or "").strip()
    if not text:
        return ""
    tokens = re.split(r"(\s+)", text)  # keep whitespace
    # First pass: try to merge adjacent word pairs that exist as phrases.
    words = [t for t in tokens if t.strip()]
    joined = " ".join(words).lower()
    for phrase, dev in DICT.items():
        if " " in phrase and phrase in joined:
            joined = joined.replace(phrase, dev)
    out_parts = []
    for tok in joined.split(" "):
        out_parts.append(_convert_word(tok) if tok else tok)
    return " ".join(p for p in out_parts if p).strip()


_DEVANAGARI = re.compile(r"[ऀ-ॿ]")


def looks_romanized(text):
    """True if the text is plausibly romanized Nepali (ASCII, no Devanagari)."""
    text = (text or "").strip()
    if not text or _DEVANAGARI.search(text):
        return False
    return bool(re.search(r"[a-zA-Z]", text))
