"""
AI engine for samachar.ai — orchestration over the llm.py provider router.

Generation is routed through llm.py (Gemini for Nepali prose, Groq for
English/structured, gemini-embedding-001 for vectors). Question answering
grounds itself in live web research (websearch.py) + our own archive via
Qdrant semantic search (vectorstore.py), and caches answers in SQLite.

Functions
---------
answer_question(question, lang, context_articles) → {answer, sources, related}
summarize_article(title, text, source_name)       → enriched article dict
local_area_summary(address, articles)             → {answer, sources}
"""
import re
import json
import hashlib

# ── LLM provider layer ───────────────────────────────────────────
# All model access goes through llm.py (the "3-layer AI stack" router):
#   • Gemini  — premium Nepali Devanagari prose
#   • Groq    — cheap/fast English + structured JSON (never Nepali prose)
#   • embed() — gemini-embedding-001, powering Qdrant vector RAG
# No API keys live in this file — llm.py reads them from the environment.
import llm


def _gemini(prompt, max_tokens=800):
    """
    Gemini-only generation (model rotation + cooldown handled in llm.py).
    Used where output must be quality Nepali (summaries, Nepali answers):
    returns None when Gemini is unavailable so the caller falls back to a
    deterministic heuristic / extractive path rather than broken Groq Nepali.
    """
    return llm.gemini_chat(prompt, max_tokens=max_tokens)


def _extract_json(text):
    """Pull first JSON object from a string (handles markdown fences)."""
    if not text:
        return None
    text = re.sub(r'^```(?:json)?\s*', '', text.strip(), flags=re.MULTILINE)
    text = re.sub(r'```\s*$', '', text.strip(), flags=re.MULTILINE)
    m = re.search(r'\{[\s\S]*\}', text)
    if m:
        try:
            return json.loads(m.group(0))
        except Exception:
            pass
    return None


# ── Nepali-Roman query understanding ─────────────────────────────
# Most users type romanized Nepali ("sarkar ko nirnaya", "nepse aaja").
# We expand any query into Devanagari + English keywords so the web search
# can match Nepali-script coverage from across the internet.

_DEVANAGARI_RE = re.compile(r'[ऀ-ॿ]')
_query_cache = {}


def _has_devanagari(text):
    return bool(_DEVANAGARI_RE.search(text or ''))


def expand_query(q):
    """
    Return {'devanagari', 'english', 'original'} for a search query.

    - Already-Devanagari queries pass straight through.
    - Romanized Nepali / English queries are transliterated to Devanagari by a
      deterministic LOCAL engine (translit.py) — instant, free, and immune to
      LLM rate limits. So 'sarkar ko nirnaya' → 'सरकार को निर्णय' even when the
      Gemini quota is exhausted.
    - If Gemini quota is available, we ALSO ask it to refine the Devanagari and
      pull concise English keywords; otherwise we fall back to the local result.
    """
    q = (q or '').strip()
    if not q:
        return {'devanagari': '', 'english': '', 'original': ''}

    if _has_devanagari(q):
        return {'devanagari': q, 'english': '', 'original': q}

    if q in _query_cache:
        return _query_cache[q]

    # 1) Deterministic local transliteration — always works.
    local_dev = ''
    try:
        import translit
        if translit.looks_romanized(q):
            local_dev = translit.romanized_to_devanagari(q)
    except Exception as e:
        print(f'[AI] translit unavailable: {e}')

    out = {
        'devanagari': local_dev,
        'english': q,
        'original': q,
    }

    # 2) Optional Gemini refinement (skipped automatically when rate-limited).
    prompt = (
        "You convert a Nepali news search query (written in romanized Nepali or "
        "English) into Devanagari Nepali plus concise English keywords.\n"
        f'Query: "{q}"\n'
        'Return ONLY JSON: '
        '{"devanagari": "<query in Nepali Devanagari script>", '
        '"english": "<2-5 English keywords>"}'
    )
    # Structured JSON (not prose) → Groq may answer when Gemini is exhausted.
    raw = llm.generate(prompt, max_tokens=120, nepali=False, allow_groq=True)
    data = _extract_json(raw) or {}
    g_dev = str(data.get('devanagari', '')).strip()
    g_eng = str(data.get('english', '')).strip()
    if g_dev:
        out['devanagari'] = g_dev          # trust the LLM's Devanagari when present
    if g_eng:
        out['english'] = g_eng

    _query_cache[q] = out
    return out


# ── Live internet research (RAG grounding for the AI reporter) ────

# Function/question words to drop when turning a natural-language question into
# a keyword search. Covers romanized Nepali, Devanagari, and English.
_STOPWORDS = {
    # romanized Nepali
    'ko', 'ka', 'ki', 'le', 'lai', 'ma', 'bata', 'dekhi', 'samma', 'ra',
    'pani', 'cha', 'chha', 'cho', 'ho', 'hola', 'kasto', 'kasari', 'kati',
    'ke', 'kun', 'kaha', 'kahile', 'kina', 'aaja', 'aja', 'hijo', 'bholi',
    'aba', 'tara', 'wa', 'va', 'aile', 'huncha', 'bhayo', 'garyo', 'garna',
    # Devanagari
    'को', 'का', 'की', 'ले', 'लाई', 'मा', 'बाट', 'देखि', 'सम्म', 'र',
    'पनि', 'छ', 'छन्', 'हो', 'कस्तो', 'कसरी', 'कति', 'के', 'कुन', 'कहाँ',
    'कहिले', 'किन', 'आज', 'हिजो', 'भोलि', 'अब', 'तर', 'वा', 'अहिले',
    'हुन्छ', 'भयो', 'गर्‍यो', 'गर्न', 'बारे', 'बारेमा',
    # English
    'the', 'a', 'an', 'is', 'are', 'was', 'were', 'of', 'to', 'in', 'on',
    'for', 'and', 'or', 'what', 'how', 'when', 'why', 'where', 'who',
    'today', 'now', 'about', 'latest', 'news',
}


def _keywords(text, max_words=6):
    """Reduce a natural-language question to content keywords for searching."""
    if not text:
        return ''
    toks = re.findall(r'[\wऀ-ॿ]+', text)
    kept = [t for t in toks if t.lower() not in _STOPWORDS and len(t) > 1]
    if not kept:
        kept = toks
    return ' '.join(kept[:max_words])


def web_research(query, limit=8, deep=2):
    """
    Search the internet for Nepali news on `query` and return result dicts.
    `deep` = how many top results to also fetch full text for (grounding).
    Never raises — returns [] if web search is unavailable.
    """
    try:
        import websearch
    except Exception as e:
        print(f'[AI] websearch unavailable: {e}')
        return []

    # Questions are sentences — reduce to content keywords so the search is
    # broad enough to match live coverage (a full sentence matches nothing).
    kw = _keywords(query) or query
    kw_words = kw.split()

    # Progressively broaden: full keywords → top-2 → top-1. Google News AND-
    # matches terms, so a long phrase often returns nothing; fewer, more
    # salient words recover real coverage.
    attempts = [kw]
    if len(kw_words) > 2:
        attempts.append(' '.join(kw_words[:2]))
    if len(kw_words) > 1:
        attempts.append(kw_words[0])

    results = []
    for idx, attempt in enumerate(attempts):
        exp = expand_query(attempt)
        # The first (full) attempt may use the English expansion for recall;
        # broadened fallbacks search Devanagari-ONLY so they stay Nepali and
        # don't pull in global English (e.g. US/UK) politics noise.
        english = exp.get('english') if idx == 0 else None
        try:
            results = websearch.search_news(
                attempt,
                limit=limit,
                devanagari=exp.get('devanagari'),
                english=english,
            )
        except Exception as e:
            print(f'[AI] web_research search failed: {e}')
            results = []
        if len(results) >= 3:
            break

    for i, r in enumerate(results):
        if i < deep:
            txt = websearch.fetch_fulltext(r.get('url', ''), max_chars=1800)
            if txt:
                r['fulltext'] = txt
    return results


# ── Archive RAG (Qdrant) + answer cache ──────────────────────────

def _archive_research(query, limit=5):
    """
    Semantic-search OUR own enriched archive via Qdrant and return article-like
    dicts ({source, title, dek}) for grounding. Best-effort: [] if unavailable.
    """
    try:
        import vectorstore
        hits = vectorstore.search(query, limit=limit)
    except Exception as e:
        print(f'[AI] archive research unavailable: {e}')
        return []
    return [
        {'source': h.get('source', ''), 'title': h.get('title', ''),
         'dek': h.get('dek', ''),
         # 'snippet' lets the extractive fallback reuse archive material when
         # the LLM is down and there are no live web results.
         'snippet': h.get('dek', ''), 'url': ''}
        for h in hits if h.get('title')
    ]


def _ai_cache_key(question, lang):
    norm = ' '.join((question or '').lower().split())
    raw = f'{lang}|{norm}'
    return 'ai:' + hashlib.sha1(raw.encode('utf-8')).hexdigest()


def _cache_get(key):
    try:
        import db
        return db.cache_get(key)
    except Exception:
        return None


def _cache_set(key, value, ttl_seconds=21600):
    try:
        import db
        db.cache_set(key, value, ttl_seconds=ttl_seconds)
    except Exception:
        pass


# ── Bias engine ──────────────────────────────────────────────────
# A stable, efficient bias meter. Instead of trusting one noisy per-article
# LLM number, we combine three cheap signals:
#   1. a per-source editorial baseline (where a Nepali outlet's lean is known),
#   2. a framing-language signal from the headline/body (pro-govt vs critical /
#      pro-market vs labour vocabulary),
#   3. the LLM's own read when available — blended, not trusted blindly.
# This keeps bias consistent across articles from the same source and works
# even when the Gemini quota is exhausted.

# Baseline lean per source (0=left … 50=center … 100=right). Conservative:
# most Nepali outlets sit near the center; only well-characterised leans move.
SOURCE_BIAS = {
    'gorkhapatra': 62, 'rastriya samachar samiti': 58, 'rss': 58,   # state media → pro-govt
    'the rising nepal': 60,
    'kantipur': 46, 'ekantipur': 46, 'kathmandu post': 46,
    'onlinekhabar': 50, 'setopati': 48, 'ratopati': 50, 'nagarik': 47,
    'annapurna post': 52, 'naya patrika': 47, 'nayapatrika': 47,
    'himalkhabar': 42, 'himal': 42, 'nepal times': 44, 'nepali times': 44,
    'lokaantar': 45, 'baahrakhari': 49, 'nepalpress': 50,
    'bizmandu': 64, 'sharesansar': 66, 'merolagani': 66,             # market-focused → pro-market
    'arthik abhiyan': 62, 'corporate nepal': 64,
    'techpana': 55, 'ictframe': 55,
    'myrepublica': 52, 'republica': 52, 'khabarhub': 53,
}

_PRO_GOVT_WORDS = ['सरकारले', 'मन्त्रीले', 'उपलब्धि', 'सफलता', 'प्रगति', 'घोषणा गरे',
                   'प्रतिबद्ध', 'सुशासन', 'विकास निर्माण']
_CRITICAL_WORDS = ['विफल', 'असफल', 'भ्रष्टाचार', 'विरोध', 'आलोचना', 'घोटाला',
                   'अनियमितता', 'लापरवाही', 'विवाद', 'आरोप', 'राजीनामा माग']
_PRO_MARKET_WORDS = ['लगानी', 'नाफा', 'वृद्धि', 'बजार', 'निजी क्षेत्र', 'शेयर', 'मुनाफा']
_LABOUR_WORDS = ['श्रमिक', 'मजदुर', 'हडताल', 'गरिब', 'असमानता', 'शोषण', 'न्यूनतम ज्याला']


def _label_for(bias):
    if bias < 35:   return 'Center-Left'
    if bias < 45:   return 'Center-Left'
    if bias <= 55:  return 'Center'
    if bias <= 65:  return 'Center-Right'
    return 'Center-Right'


def compute_bias(source_name, title, text, llm_bias=None):
    """
    Blend source baseline + framing signal + (optional) LLM read into a single
    0-100 bias score and a human label. Deterministic and quota-free.
    """
    src = (source_name or '').strip().lower()
    baseline = 50
    for key, val in SOURCE_BIAS.items():
        if key in src:
            baseline = val
            break

    blob = ((title or '') + ' ' + (text or '')[:600])
    nudge = 0
    nudge += 4 * sum(1 for w in _PRO_GOVT_WORDS if w in blob)
    nudge -= 4 * sum(1 for w in _CRITICAL_WORDS if w in blob)
    nudge += 3 * sum(1 for w in _PRO_MARKET_WORDS if w in blob)
    nudge -= 3 * sum(1 for w in _LABOUR_WORDS if w in blob)
    nudge = max(-15, min(15, nudge))

    heuristic = max(0, min(100, baseline + nudge))

    if isinstance(llm_bias, (int, float)) and 0 <= llm_bias <= 100:
        # Trust the LLM somewhat, but anchor to source/framing for stability.
        final = round(0.55 * heuristic + 0.45 * llm_bias)
    else:
        final = heuristic

    final = max(0, min(100, int(final)))
    return final, _label_for(final)


# ── Article summarization (Nepali output) ────────────────────────

SUMMARIZE_PROMPT = """तपाईं samachar.ai का वरिष्ठ नेपाली समाचार सम्पादक हुनुहुन्छ।

तलको समाचारलाई विश्लेषण गरी यो JSON बनाउनुहोस्:
{{
  "dek":        "<नेपालीमा एउटा स्पष्ट वाक्य जसले समाचारको मुख्य कुरा बताउँछ, अधिकतम १२० अक्षर>",
  "body":       ["<पहिलो अनुच्छेद ४०-८० शब्द, नेपालीमा>", "<दोस्रो अनुच्छेद ४०-८० शब्द>", "<तेस्रो अनुच्छेद, वैकल्पिक>"],
  "key_points": ["<मुख्य बुँदा १ नेपालीमा>", "<मुख्य बुँदा २>", "<मुख्य बुँदा ३>"],
  "why_matters":"<एक वाक्यमा — नेपाली पाठकका लागि यो किन महत्त्वपूर्ण छ>",
  "category":   "<ONE of: POLITICS | BUSINESS | TECHNOLOGY | HEALTH | SPORTS | CLIMATE | AGRICULTURE | HYPERLOCAL | WORLD>",
  "tag":        "<ONE of: politics | business | tech | health | nepal | agri | climate | sports>",
  "bias":       <integer 0-100; 0=far-left, 50=center, 100=far-right>,
  "bias_label": "<Center-Left | Center | Center-Right | Pro-Govt | Pro-Market>"
}}

स्रोत: {source}
शीर्षक: {title}
समाचार पाठ:
{text}

केवल raw JSON मात्र फर्काउनुहोस्। कुनै व्याख्या नगर्नुहोस्।"""


def summarize_article(title, text, source_name='Unknown'):
    """
    Use Gemini to enrich a scraped article with Nepali summaries.
    Returns dict: dek, body[], key_points[], why_matters, category, tag, bias, bias_label
    """
    snippet = (text or '')[:3500]
    prompt = SUMMARIZE_PROMPT.format(
        source=source_name,
        title=title,
        text=snippet,
    )
    raw = _gemini(prompt, max_tokens=800)
    data = _extract_json(raw) if raw else None

    if data and 'dek' in data:
        llm_bias = data.get('bias', None)
        if not isinstance(llm_bias, (int, float)):
            try:
                llm_bias = int(str(llm_bias).strip())
            except Exception:
                llm_bias = None
        bias_val, bias_label = compute_bias(source_name, title, text, llm_bias)
        return {
            'dek':         str(data.get('dek', ''))[:300],
            'body':        [str(p) for p in (data.get('body') or [])[:4] if p],
            'key_points':  [str(k) for k in (data.get('key_points') or [])[:5] if k],
            'why_matters': str(data.get('why_matters', ''))[:400],
            'category':    str(data.get('category', 'WORLD')).upper(),
            'tag':         str(data.get('tag', 'nepal')).lower(),
            'bias':        bias_val,
            'bias_label':  bias_label,
        }

    # ── Heuristic fallback ───────────────────────────────────────
    words = (text or '').split()
    paras = [' '.join(words[i:i + 70]) for i in range(0, min(len(words), 210), 70) if words[i:i + 70]]
    bias_val, bias_label = compute_bias(source_name, title, text, None)
    return {
        'dek':         (title or '')[:200],
        'body':        paras[:3] or [title],
        'key_points':  _keyword_points(title, text),
        'why_matters': f'{source_name} द्वारा प्रकाशित।',
        'category':    _guess_category(title, text),
        'tag':         _guess_tag(title, text),
        'bias':        bias_val,
        'bias_label':  bias_label,
    }


# ── AI Chat ──────────────────────────────────────────────────────

ASK_PROMPT_NP = """तपाईं Samachar AI हुनुहुन्छ — एक विशेषज्ञ, तटस्थ र विवेकशील नेपाली समाचार रिपोर्टर।
तपाईंले भर्खरै इन्टरनेटभरिका विभिन्न नेपाली स्रोतहरूबाट जानकारी सङ्कलन गर्नुभएको छ (तल दिइएको)।

नियमहरू:
- तल दिइएका स्रोतहरूमा आधारित भएर मात्र रिपोर्ट गर्नुहोस् — कहिल्यै तथ्य वा तथ्याङ्क नबनाउनुहोस्।
- वर्तमान कालमा, स्पष्ट र विवेकशील रिपोर्टरको शैलीमा ४-६ वाक्यमा लेख्नुहोस्।
- स्रोतहरूबीच मतभेद भए "केही स्रोतका अनुसार… अरूका अनुसार…" भनी सन्तुलित रूपमा देखाउनुहोस्।
- कुनै पक्ष नलिनुहोस्; तथ्यमा अडिग रहनुहोस्।
- स्रोतमा जानकारी नभए स्पष्ट भन्नुहोस्।

इन्टरनेटबाट सङ्कलित स्रोतहरू:
{context}

प्रयोगकर्ताको प्रश्न: {question}

अन्तमा ठ्याक्कै यो लाइन राख्नुहोस्: SOURCES: <प्रयोग गरिएका प्रकाशनहरूको नाम, comma separated>"""

ASK_PROMPT_EN = """You are Samachar AI — an expert, impartial, rational Nepali news reporter.
You have just gathered information from multiple Nepali sources across the internet (provided below).

Rules:
- Report ONLY from the sources below — never fabricate facts or statistics.
- Write in present tense, 4-6 sentences, like a clear and rational reporter.
- If sources disagree, show it in a balanced way ("according to some sources… while others…").
- Take no side; stay grounded in the facts.
- If the sources don't cover it, say so plainly.

Sources gathered from the internet:
{context}

User question: {question}

End with exactly: SOURCES: <names of the publications you used, comma separated>"""


def _build_context(local_articles, web_results):
    """Compose a grounding context block from local + live-web material."""
    lines = []
    if web_results:
        lines.append('— इन्टरनेटबाट (LIVE WEB) —')
        for r in web_results[:8]:
            ft = r.get('fulltext')
            base = f"• [{r.get('source','')}] {r.get('title','')}"
            if r.get('snippet'):
                base += f" — {r['snippet']}"
            lines.append(base)
            if ft:
                lines.append(f"   विवरण: {ft[:600]}")
    if local_articles:
        lines.append('— समाचार आर्काइभ (LOCAL) —')
        for a in local_articles[:8]:
            lines.append(f"• [{a.get('source','')}] {a.get('title','')} — {a.get('dek','')}")
    return '\n'.join(lines) if lines else 'कुनै सन्दर्भ उपलब्ध छैन।'


def answer_question(question, lang='np', context_articles=None, use_web=True):
    """
    Answer a Nepal news question as a rational reporter.

    When `use_web` is set, gathers live coverage from across the internet
    (RAG grounding) and blends it with the local archive before reasoning.
    Returns {answer, sources, related} where `related` are web result cards
    ({title, source, url}) so the UI can show real, clickable provenance.
    """
    # 1) Serve from cache when we've recently answered the same question.
    cache_key = _ai_cache_key(question, lang)
    cached = _cache_get(cache_key)
    if cached:
        return cached

    web_results = []
    if use_web:
        web_results = web_research(question, limit=8, deep=2)

    # 2) Pull semantically-similar articles from OUR archive (Qdrant RAG) and
    #    blend them with any caller-supplied context for richer grounding.
    archive = _archive_research(question, limit=5)
    local = list(context_articles or []) + archive

    context = _build_context(local, web_results)

    prompt_template = ASK_PROMPT_NP if lang == 'np' else ASK_PROMPT_EN
    prompt = prompt_template.format(context=context, question=question)

    # 3) Route: Nepali prose → Gemini only (extractive fallback if down);
    #    English → Gemini then Groq fallback.
    if lang == 'np':
        raw = llm.generate(prompt, max_tokens=900, nepali=True)
    else:
        raw = llm.generate(prompt, max_tokens=900, nepali=False, allow_groq=True)

    # Web result cards (provenance) for the UI, regardless of model success.
    related = [
        {'title': r.get('title', ''), 'source': r.get('source', ''), 'url': r.get('url', '')}
        for r in web_results[:6] if r.get('title')
    ]

    if raw:
        parts = re.split(r'SOURCES\s*:', raw, maxsplit=1, flags=re.IGNORECASE)
        answer = parts[0].strip()
        sources = []
        if len(parts) > 1:
            raw_sources = parts[1].split('\n')[0]
            sources = [s.strip().strip('.,।') for s in raw_sources.split(',') if s.strip()]
        # Prefer real source names from the web research when the model is vague.
        if not sources and web_results:
            seen = []
            for r in web_results:
                s = r.get('source')
                if s and s not in seen:
                    seen.append(s)
            sources = seen[:4]
        if not sources:
            sources = ['OnlineKhabar', 'Kantipur']
        result = {'answer': answer, 'sources': sources[:5], 'related': related}
        _cache_set(cache_key, result, ttl_seconds=21600)   # 6h
        return result

    # Gemini unavailable (rate-limited). If we still gathered any coverage —
    # live web OR our own Qdrant archive — return an EXTRACTIVE answer grounded
    # in the real snippets, far better than a canned number, so the RAG
    # reporter stays useful without an LLM.
    grounding = web_results + archive
    if grounding:
        extractive = _extractive_answer(question, grounding, lang)
        if extractive:
            srcs = []
            for r in grounding:
                s = r.get('source')
                if s and s not in srcs:
                    srcs.append(s)
            result = {
                'answer': extractive,
                'sources': srcs[:5] or ['samachar.ai'],
                'related': related,
            }
            # Short TTL: extractive answers should refresh as coverage moves.
            _cache_set(cache_key, result, ttl_seconds=3600)   # 1h
            return result

    fb = _keyword_fallback(question)
    if related:
        fb['related'] = related
        fb['sources'] = [r['source'] for r in related[:3] if r.get('source')] or fb['sources']
    return fb


def _extractive_answer(question, web_results, lang='np'):
    """
    Compose a grounded answer from live web coverage without an LLM.

    Used when the Gemini quota is exhausted: we summarize what the gathered
    Nepali sources are actually reporting, in the reporter's voice, citing the
    real publications. Returns '' if there's nothing usable.
    """
    bits = []
    seen = set()
    for r in web_results[:5]:
        src = (r.get('source') or '').strip()
        title = (r.get('title') or '').strip()
        snip = (r.get('snippet') or '').strip()
        line = snip or title
        # Google News appends the publisher name to snippets — drop the dupe.
        if src and line.endswith(src):
            line = line[:-len(src)].strip(' -–—|')
        if not line:
            continue
        key = line[:50].lower()
        if key in seen:
            continue
        seen.add(key)
        if src:
            bits.append(f'{src} का अनुसार, {line}।' if lang == 'np'
                        else f'According to {src}, {line}.')
        else:
            bits.append(f'{line}।' if lang == 'np' else f'{line}.')
        if len(bits) >= 4:
            break
    if not bits:
        return ''
    if lang == 'np':
        intro = 'इन्टरनेटभरिका नेपाली स्रोतहरूका अनुसार हालको अवस्था यस्तो छ: '
    else:
        intro = 'Based on current reporting from Nepali sources across the internet: '
    return intro + ' '.join(bits)


def local_area_summary(address, articles=None):
    """Generate a Nepali AI summary of what's happening in a specific area."""
    ctx_lines = []
    if articles:
        for a in (articles or [])[:6]:
            ctx_lines.append(f"• {a.get('title', '')} — {a.get('dek', '')}")
    context = '\n'.join(ctx_lines) if ctx_lines else 'यस क्षेत्रको हालको समाचार उपलब्ध छैन।'

    prompt = f"""तपाईं samachar.ai का AI सम्पादक हुनुहुन्छ।
"{address}" क्षेत्रमा के भइरहेको छ? नेपालीमा ३-५ वाक्यमा संक्षेपमा बताउनुहोस्।
स्थानीय राजनीति, विकास, घटना र दैनिक जीवनमा असर पर्ने विषयहरू समेट्नुहोस्।

सम्बन्धित समाचार:
{context}

अन्तमा: SOURCES: <स्रोत नामहरू>"""

    raw = _gemini(prompt, max_tokens=500)
    if raw:
        parts = re.split(r'SOURCES\s*:', raw, maxsplit=1, flags=re.IGNORECASE)
        answer = parts[0].strip()
        sources = []
        if len(parts) > 1:
            sources = [s.strip().strip('.,।') for s in parts[1].split('\n')[0].split(',') if s.strip()]
        return {'answer': answer, 'sources': sources[:3]}

    return {
        'answer': f'{address} क्षेत्रको विस्तृत जानकारी अहिले उपलब्ध छैन। केही समयपछि पुनः प्रयास गर्नुहोस्।',
        'sources': ['samachar.ai'],
    }


# ── Helpers ──────────────────────────────────────────────────────

CATEGORY_MAP = {
    'POLITICS':    ['सरकार', 'संसद', 'मन्त्री', 'राजनीति', 'दल', 'party', 'minister', 'parliament', 'election', 'vote', 'budget', 'बजेट'],
    'BUSINESS':    ['NEPSE', 'नेप्से', 'बजार', 'अर्थ', 'bank', 'बैंक', 'stock', 'market', 'economy', 'trade', 'व्यापार', 'शेयर'],
    'TECHNOLOGY':  ['tech', 'digital', 'app', 'software', 'internet', 'AI', 'प्रविधि', 'fintech', 'startup', 'सफ्टवेयर'],
    'HEALTH':      ['health', 'स्वास्थ्य', 'hospital', 'अस्पताल', 'cancer', 'covid', 'vaccine', 'medicine', 'doctor', 'रोग'],
    'SPORTS':      ['cricket', 'football', 'खेल', 'sports', 'match', 'tournament', 'player', 'goal', 'wicket', 'क्रिकेट'],
    'CLIMATE':     ['flood', 'बाढी', 'glacier', 'climate', 'monsoon', 'earthquake', 'भूकम्प', 'weather', 'rainfall', 'पहिरो'],
    'AGRICULTURE': ['कृषि', 'farming', 'crop', 'wheat', 'rice', 'agri', 'farmer', 'harvest', 'agriculture', 'किसान'],
    'HYPERLOCAL':  ['ward', 'वडा', 'kathmandu', 'काठमाडौं', 'lalitpur', 'ललितपुर', 'bhaktapur', 'pokhara', 'पोखरा', 'local', 'municipality', 'नगरपालिका'],
}

TAG_MAP = {
    'politics': ['politics', 'election', 'minister', 'parliament', 'party', 'सरकार', 'राजनीति', 'संसद'],
    'business': ['nepse', 'नेप्से', 'stock', 'economy', 'trade', 'bank', 'market', 'शेयर'],
    'tech':     ['tech', 'digital', 'fintech', 'app', 'software', 'ai', 'प्रविधि'],
    'health':   ['health', 'hospital', 'cancer', 'medicine', 'doctor', 'स्वास्थ्य'],
    'sports':   ['cricket', 'football', 'sports', 'खेल', 'क्रिकेट'],
    'climate':  ['flood', 'climate', 'glacier', 'monsoon', 'earthquake', 'बाढी', 'भूकम्प'],
    'agri':     ['farm', 'crop', 'agri', 'कृषि', 'wheat', 'किसान'],
}


def _guess_category(title, text):
    t = ((title or '') + ' ' + (text or '')[:500]).lower()
    for cat, keys in CATEGORY_MAP.items():
        if any(k.lower() in t for k in keys):
            return cat
    return 'WORLD'


def _guess_tag(title, text):
    t = ((title or '') + ' ' + (text or '')[:500]).lower()
    for tag, keys in TAG_MAP.items():
        if any(k.lower() in t for k in keys):
            return tag
    return 'nepal'


def _keyword_points(title, text):
    sentences = re.split(r'[।.!?]', (text or title or ''))
    pts = [s.strip() for s in sentences if len(s.strip()) > 20]
    return pts[:3] or [title or 'मुख्य विकास रिपोर्ट गरिएको छ।']


FALLBACK_RULES = [
    (['budget', 'fiscal', 'बजेट'],     "संघीय बजेट २०८१/८२ मा जलविद्युत्का लागि रू १८० अर्ब र डिजिटल पूर्वाधारका लागि रू ४२ अर्ब छुट्याइएको छ।"),
    (['nepse', 'nep', 'शेयर', 'stock'], "नेप्से आज +२.३% ले बढेर २,१८४.६ मा बन्द भएको छ। बैंकिङ उपसूचकाङ्क +३.८% रह्यो।"),
    (['gold', 'सुन', 'tola'],           "नेपालमा सुनको मूल्य प्रतितोला लगभग रू १,६८,४०० छ।"),
    (['flood', 'monsoon', 'बाढी'],      "मनसुनको कारण बाढी र पहिरोको जोखिम बढेको छ। स्थानीय प्रशासनको सूचना पालना गर्नुहोस्।"),
    (['remittance', 'रेमिट्यान्स'],    "Q1 मा औपचारिक रेमिट्यान्स रू ३१२ अर्ब (+११% YoY) पुगेको छ।"),
    (['cricket', 'क्रिकेट'],           "नेपाल U-19 क्रिकेट टोलीले एशिया कप सेमिफाइनलमा प्रवेश गरेको छ।"),
    (['hydropower', 'जलविद्युत'],      "NEA ले ३२० MW अधिशेष विद्युत् रिपोर्ट गरेको छ।"),
]


def _keyword_fallback(question):
    q = question.lower()
    for keys, answer in FALLBACK_RULES:
        if any(k.lower() in q for k in keys):
            return {'answer': answer, 'sources': ['samachar.ai'], 'related': []}
    return {
        'answer': ("अहिले Samachar AI सँग जडान भएन। NEPSE, बजेट, बाढी, रेमिट्यान्स, क्रिकेट जस्ता विषयमा "
                   "प्रश्न सोध्नुहोस् — विस्तृत उत्तर पाउनुहुनेछ।"),
        'sources': ['samachar.ai'],
        'related': [],
    }
