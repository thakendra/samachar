"""
Internet-wide Nepali news search for samachar.ai.

Uses Google News RSS search — free, no API key required — which indexes
virtually every Nepali publisher on the web (not just our 8 scraped feeds).
We bias the locale to Nepal/Nepali (hl=ne-NP, gl=NP, ceid=NP:ne) so results
come back as Nepali-language news from sources all over the internet.

Public API
----------
search_news(query, limit=20)      → [ {title, url, source, published, snippet} ]
fetch_fulltext(url, max_chars)    → str   (best-effort article body, for RAG)
"""
import re
import html
import urllib.parse

import requests
import feedparser

GOOGLE_NEWS_RSS = "https://news.google.com/rss/search"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Mobile Safari/537.36 samachar.ai/2.0"
    )
}
TIMEOUT = 12


def _clean(text):
    """Strip HTML tags and unescape entities."""
    if not text:
        return ""
    text = re.sub(r"<[^>]+>", " ", text)
    text = html.unescape(text)
    return re.sub(r"\s+", " ", text).strip()


def _split_title_source(title):
    """Google News titles look like 'Headline - Source'. Split that out."""
    if " - " in title:
        head, src = title.rsplit(" - ", 1)
        # Only treat the tail as a source if it's short (a publisher name)
        if 0 < len(src) <= 40:
            return head.strip(), src.strip()
    return title.strip(), ""


def _google_news(query, lang="ne", region="NP", when="45d", limit=20):
    """Run one Google News RSS search and return parsed entries."""
    q = f"{query} when:{when}".strip()
    params = {
        "q": q,
        "hl": f"{lang}-{region}",
        "gl": region,
        "ceid": f"{region}:{lang}",
    }
    url = f"{GOOGLE_NEWS_RSS}?{urllib.parse.urlencode(params)}"

    feed = None
    try:
        r = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        if r.ok:
            feed = feedparser.parse(r.content)
    except Exception as e:
        print(f"[websearch] google news fetch failed: {e}")
    if feed is None:
        try:
            feed = feedparser.parse(url)
        except Exception:
            return []

    out = []
    for e in feed.entries[:limit]:
        raw_title = _clean(e.get("title", ""))
        if not raw_title:
            continue
        title, src = _split_title_source(raw_title)

        # Prefer the structured <source> element when present.
        source = ""
        src_obj = e.get("source")
        if isinstance(src_obj, dict):
            source = src_obj.get("title", "")
        elif src_obj is not None:
            source = getattr(src_obj, "title", "") or str(src_obj)
        source = source or src or "Google News"

        out.append({
            "title": title,
            "url": e.get("link", ""),
            "source": source,
            "published": e.get("published", ""),
            "snippet": _clean(e.get("summary", ""))[:240],
        })
    return out


# Known Nepali publishers (name fragments, lowercased) — used to keep results
# genuinely Nepali and filter out cross-script English/Indian noise.
NEPALI_SOURCES = (
    "onlinekhabar", "setopati", "ratopati", "shilapatra", "ekantipur", "kantipur",
    "nagarik", "annapurna", "galaxy", "ratna", "himalkhabar", "himal", "nepalkhabar",
    "nepali", "nepal", "thehimalayantimes", "myrepublica", "republica", "khabarhub",
    "bizmandu", "merolagani", "sharesansar", "techpana", "ictframe", "lokaantar",
    "baahrakhari", "nepalpress", "deshsanchar", "pardafas", "swasthyakhabar",
    "rajdhanidaily", "gorkhapatra", "nayapatrika", "naya patrika", "hamrokhelkud",
    "nepalnews", "nepallive", "imagekhabar", "dcnepal", "ujyaalo", "hamropatro",
    "kathmandupost", "nepalitimes", "spotlightnepal", "english.onlinekhabar",
)

_DEVANAGARI = re.compile(r"[ऀ-ॿ]")


def _has_devanagari(text):
    return bool(_DEVANAGARI.search(text or ""))


def _nepali_score(item):
    """Higher = more likely to be genuine Nepali news (vs cross-script noise)."""
    score = 0
    if _has_devanagari(item.get("title", "")):
        score += 3
    src = (item.get("source", "") or "").lower()
    if any(s in src for s in NEPALI_SOURCES):
        score += 3
    url = (item.get("url", "") or "").lower()
    if ".np" in url or any(s in url for s in NEPALI_SOURCES):
        score += 2
    return score


def search_news(query, limit=20, devanagari=None, english=None, nepali_only=True):
    """
    Search the wider internet for Nepali news on `query`.

    If `devanagari` / `english` expansions are supplied (from ai.expand_query),
    we search BOTH forms and merge — this is what makes romanized-Nepali
    queries ("sarkar ko nirnaya") return the right Devanagari results.

    Results are ranked by Nepali relevance so genuine Nepali coverage floats
    to the top and cross-script English/Indian noise sinks (or is dropped when
    `nepali_only` and we have enough Nepali hits).

    Returns a de-duplicated, source-diverse list of result dicts.
    """
    queries = []
    if devanagari:
        queries.append(devanagari)
    if english:
        queries.append(english)
    if not queries:
        queries.append(query)
    if query and query not in queries:
        queries.append(query)

    seen = set()
    merged = []
    per_query = max(10, limit + 6)
    for q in queries:
        for item in _google_news(q, limit=per_query):
            key = (item["title"] or "").lower()[:80]
            if not key or key in seen:
                continue
            seen.add(key)
            item["_score"] = _nepali_score(item)
            merged.append(item)

    # Rank Nepali-relevant results first (stable within score by recency order).
    merged.sort(key=lambda x: x.get("_score", 0), reverse=True)

    nepali = [m for m in merged if m.get("_score", 0) > 0]
    if nepali_only and len(nepali) >= 3:
        merged = nepali

    for m in merged:
        m.pop("_score", None)
    return merged[:limit]


def fetch_fulltext(url, max_chars=2500):
    """
    Best-effort full-text extraction for a result URL (used to ground RAG).
    Tries newspaper4k, falls back to a crude paragraph scrape. Never raises.
    """
    if not url:
        return ""
    try:
        import newspaper  # noqa: F401
        from newspaper import Article as NpArticle
        art = NpArticle(url)
        art.download()
        art.parse()
        if art.text and len(art.text) > 120:
            return art.text[:max_chars]
    except Exception:
        pass
    try:
        from bs4 import BeautifulSoup
        r = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        soup = BeautifulSoup(r.content, "lxml")
        paras = [p.get_text(" ", strip=True) for p in soup.find_all("p")]
        text = " ".join(p for p in paras if len(p) > 40)
        return text[:max_chars]
    except Exception:
        return ""
