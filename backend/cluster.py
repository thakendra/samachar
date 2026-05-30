"""
Topic clustering + deduplication for samachar.ai.

The scrapers and web search return the SAME story from many outlets (e.g. five
articles about a casino-royalty hike). Feeding all five to the AI — or showing
them as five "Source says X" lines — makes the product feel like a spammy RSS
dump. This module groups near-duplicate items into ONE story per topic so the
rest of the app can reason about, and present, a single clean story.

Pure-Python, deterministic, zero external calls — works even when every LLM and
the embedding quota is exhausted. (Embeddings can refine this later, but cheap
content-token overlap already collapses same-story duplicates reliably because
Nepali headlines about one event share their key nouns.)

Public API
----------
cluster_items(items, threshold=...)  → [ cluster, ... ]   (largest first)
    where each item is a dict with at least 'title' and ideally
    'source', 'snippet'/'dek', 'url', 'fulltext'.
    Each cluster = {
        lead, items, sources, size, headline, summary, tokens
    }
"""
import re

# Function/stop words to ignore when comparing headlines — romanized Nepali,
# Devanagari and English. (Kept compact; only words with no topical meaning.)
_STOP = {
    # romanized Nepali
    'ko', 'ka', 'ki', 'le', 'lai', 'ma', 'bata', 'dekhi', 'samma', 'ra',
    'pani', 'cha', 'chha', 'ho', 'hola', 'aaja', 'aja', 'hijo', 'bholi',
    'aba', 'tara', 'wa', 'va', 'aile', 'huncha', 'bhayo', 'garyo',
    # Devanagari
    'को', 'का', 'की', 'ले', 'लाई', 'मा', 'बाट', 'देखि', 'सम्म', 'र',
    'पनि', 'छ', 'छन्', 'हो', 'भयो', 'गर्‍यो', 'गर्ने', 'भएको', 'रहेको',
    'हुने', 'गरी', 'लागि', 'साथ', 'पछि', 'अघि', 'बारे', 'बारेमा', 'यो',
    'त्यो', 'एक', 'दुई', 'मात्र', 'आज', 'हिजो', 'अब',
    # English
    'the', 'a', 'an', 'is', 'are', 'was', 'were', 'of', 'to', 'in', 'on',
    'for', 'and', 'or', 'at', 'by', 'with', 'as', 'from', 'after', 'over',
    'new', 'says', 'said', 'news', 'latest', 'update', 'report', 'reports',
}

# Match word characters + the Devanagari letter block, but NOT the danda
# punctuation (।=U+0964, ॥=U+0965) which sits inside the block — otherwise
# "वृद्धि।" and "वृद्धि" become different tokens and same-story overlap breaks.
_WORD = re.compile(r'[\wऀ-ॣ०-ॿ]+', re.UNICODE)
_PUNCT = re.compile(r'[।॥]')


def _tokens(text):
    """Content tokens of a string: lowercased, stop-words and noise removed."""
    if not text:
        return set()
    text = _PUNCT.sub(' ', text.lower())
    out = set()
    for t in _WORD.findall(text):
        if len(t) < 2 or t in _STOP or t.isdigit():
            continue
        out.add(t)
    return out


def _overlap(a, b):
    """Overlap coefficient: |a∩b| / min(|a|,|b|) — lenient for short headlines."""
    if not a or not b:
        return 0.0
    return len(a & b) / min(len(a), len(b))


def _jaccard(a, b):
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def _same_story(toks_a, toks_b):
    """Decide whether two token sets describe the same story."""
    shared = len(toks_a & toks_b)
    if shared < 2:                       # one common word is coincidence
        return False
    return _overlap(toks_a, toks_b) >= 0.5 or _jaccard(toks_a, toks_b) >= 0.32


def _clean_title(title):
    """Drop a trailing ' - Publisher' (Google News style) from a headline."""
    if title and ' - ' in title:
        head, tail = title.rsplit(' - ', 1)
        if 0 < len(tail) <= 40:
            return head.strip()
    return (title or '').strip()


def _strip_source(text, source):
    """Remove a trailing ' - Publisher' or a dangling publisher name from text."""
    t = (text or '').strip()
    if ' - ' in t:
        head, tail = t.rsplit(' - ', 1)
        if 0 < len(tail) <= 40:
            t = head.strip()
    s = (source or '').strip()
    if s and t.lower().endswith(s.lower()):
        t = t[:-len(s)].strip(' -–—|:।.')
    return t


def _item_text(item):
    """Best available body text for an item (for summary building)."""
    raw = (item.get('fulltext') or item.get('snippet') or item.get('dek') or '')
    return _strip_source(raw, item.get('source', '')).strip()


def _sentences(text):
    parts = re.split(r'(?<=[।.!?])\s+', text or '')
    return [s.strip() for s in parts if len(s.strip()) > 25]


# Site taglines / boilerplate that scrapers sometimes capture as a "title".
_JUNK = (
    'news portal', '24-hour', '24 hour', 'breaking news', 'latest news from',
    'online news', 'first.*portal',
)


def _is_junk(title):
    t = (title or '').strip().lower()
    if len(t) < 6:
        return True
    return any(re.search(j, t) for j in _JUNK)


def _build_summary(items, headline='', max_sentences=3, max_chars=520):
    """
    Compose a short, de-duplicated summary from a cluster's items WITHOUT an
    LLM. Prefer the richest item's text, add complementary sentences from other
    outlets, and never just echo the headline.
    """
    head_key = ' '.join(_tokens(headline))[:40]
    ranked = sorted(items, key=lambda it: len(_item_text(it)), reverse=True)

    picked = []
    seen_prefix = {head_key} if head_key else set()
    for it in ranked:
        body = _item_text(it)
        cands = _sentences(body)
        if not cands and body and len(body) > 25:
            cands = [body]
        for sent in cands:
            key = ' '.join(_tokens(sent[:60]))[:40]
            if not key or key in seen_prefix:
                continue
            seen_prefix.add(key)
            picked.append(sent.rstrip('।.!? ') + ('।' if _has_devanagari(sent) else '.'))
            if len(picked) >= max_sentences:
                break
        if len(picked) >= max_sentences:
            break

    summary = ' '.join(picked).strip()
    if len(summary) > max_chars:
        summary = summary[:max_chars].rsplit(' ', 1)[0] + '…'
    return summary


_DEV = re.compile(r'[ऀ-ॿ]')


def _has_devanagari(text):
    return bool(_DEV.search(text or ''))


def cluster_items(items, threshold=None):
    """
    Group a list of result/article dicts into topic clusters (largest first).

    Greedy single-pass clustering on content-token overlap. Each cluster keeps
    the most informative item as its `lead` and a merged, de-duplicated source
    list + summary so callers can render "one story → many sources".
    """
    clusters = []   # each: {'tokens', 'items', 'order'}
    for idx, item in enumerate(items or []):
        title = item.get('title', '')
        if _is_junk(_clean_title(title)):
            continue   # drop scraped site taglines / boilerplate
        toks = _tokens(_clean_title(title) + ' ' + (item.get('snippet') or item.get('dek') or ''))
        if not toks:
            # Untokenizable — keep as its own singleton so we don't drop it.
            clusters.append({'tokens': set(), 'items': [item], 'order': idx})
            continue
        placed = False
        for c in clusters:
            if c['tokens'] and _same_story(toks, c['tokens']):
                c['items'].append(item)
                # Bias the cluster signature toward shared terms over time.
                c['tokens'] |= toks
                placed = True
                break
        if not placed:
            clusters.append({'tokens': set(toks), 'items': [item], 'order': idx})

    out = []
    for c in clusters:
        members = c['items']
        # Lead = item with the richest body text (falls back to first).
        lead = max(members, key=lambda it: len(_item_text(it)) + len(it.get('title', '')))
        # Unique source names, lead's source first.
        sources = []
        for it in [lead] + members:
            s = (it.get('source') or '').strip()
            if s and s not in sources:
                sources.append(s)
        headline = _clean_title(lead.get('title', ''))
        out.append({
            'lead':     lead,
            'items':    members,
            'sources':  sources,
            'size':     len(members),
            'order':    c['order'],
            'headline': headline,
            'summary':  _build_summary(members, headline=headline),
            'tokens':   c['tokens'],
        })

    # Preserve the caller's RELEVANCE order (web search + Qdrant return items
    # best-match first): the cluster holding the most-relevant item leads. Among
    # equally-relevant clusters, more outlets (newsworthiness) then richer text.
    out.sort(key=lambda c: (c['order'], -c['size'], -len(c['summary'])))
    return out
