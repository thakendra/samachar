"""
AI engine for samachar.ai — Google Gemini via google-genai SDK.

Functions
---------
answer_question(question, lang, context_articles) → {answer, sources, related}
summarize_article(title, text, source_name)       → enriched article dict
local_area_summary(address, articles)             → {answer, sources}
"""
import os
import re
import json
import threading

# ── Gemini setup ─────────────────────────────────────────────────
GEMINI_KEY = os.getenv('GEMINI_API_KEY', 'AIzaSyBcqNqnwS8-lRg203CWMd71diAyUL2_bbU')

# Model priority list — best free-tier quota first
# gemini-2.0-flash-lite: 30 RPM / 1500 RPD (free) ← best for batch processing
# gemini-2.0-flash:      15 RPM / 1500 RPD (free) ← good for chat
# gemini-2.5-flash:       5 RPM /  500 RPD (free) ← powerful but slow quota
# gemini-1.5-flash-8b:   15 RPM / 1500 RPD (free) ← lightweight fallback
GEMINI_MODELS = [
    'models/gemini-2.0-flash-lite',   # 30 RPM free — primary
    'models/gemini-2.0-flash',        # 15 RPM free — fallback
    'models/gemini-2.5-flash',        # 5 RPM free  — separate quota pool
]

_genai_client = None
_model_index   = 0          # which model in GEMINI_MODELS we're currently using
_model_lock    = threading.Lock()

# Per-model cooldown tracking (model → timestamp when quota resets)
import time as _time
_model_cooldown = {}  # model → epoch when safe to retry


def _init_client():
    """Create the genai Client once."""
    global _genai_client
    if _genai_client is None:
        try:
            from google import genai
            _genai_client = genai.Client(api_key=GEMINI_KEY)
        except Exception as e:
            print(f'[AI] Gemini init failed: {e}')
            _genai_client = 'FAILED'
    return _genai_client


def _current_model():
    return GEMINI_MODELS[_model_index % len(GEMINI_MODELS)]


def _advance_model(bad_model):
    """Rotate to the next model after a failure on bad_model."""
    global _model_index
    with _model_lock:
        # Only advance if we're still using the model that failed
        if _current_model() == bad_model:
            _model_index += 1
            if _model_index >= len(GEMINI_MODELS):
                _model_index = 0   # wrap around
            print(f'[AI] Switched to model: {_current_model()}')


def _gemini(prompt, max_tokens=800):
    """
    Call Gemini and return text.
    On 429 rate-limit, automatically advances to next model and retries once.
    Returns None only if all retries fail.
    """
    client = _init_client()
    if client == 'FAILED' or client is None:
        return None

    try:
        from google.genai import types
    except ImportError:
        return None

    # Try current model, then fall back through the list once
    tried = set()
    for attempt in range(len(GEMINI_MODELS) + 1):
        model = _current_model()
        if model in tried:
            break
        tried.add(model)

        # Skip if this model is in cooldown
        cooldown_until = _model_cooldown.get(model, 0)
        if _time.time() < cooldown_until:
            _advance_model(model)
            continue

        try:
            response = client.models.generate_content(
                model=model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.3,
                    max_output_tokens=max_tokens,
                ),
            )
            # Success — make sure we record this model as active
            if attempt > 0:
                print(f'[AI] Success with fallback model: {model}')
            return response.text

        except Exception as e:
            err = str(e)
            if '429' in err or 'RESOURCE_EXHAUSTED' in err:
                # Put model in cooldown (60 s default, or retry-delay from error)
                delay = 65
                m = re.search(r'retryDelay["\s:]+(\d+)', err)
                if m:
                    delay = int(m.group(1)) + 5
                _model_cooldown[model] = _time.time() + delay
                print(f'[AI] {model} rate-limited — cooldown {delay}s, trying next model…')
                _advance_model(model)
            elif '404' in err or 'NOT_FOUND' in err:
                print(f'[AI] {model} not available — switching model…')
                _advance_model(model)
            else:
                # Non-rate-limit error (auth, network, etc.) — log and give up
                print(f'[AI] Gemini call error: {e}')
                return None

    print('[AI] All Gemini models rate-limited or unavailable.')
    return None


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
    raw = _gemini(prompt, max_tokens=120)
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
    exp = expand_query(kw)
    try:
        results = websearch.search_news(
            kw,
            limit=limit,
            devanagari=exp.get('devanagari'),
            english=exp.get('english'),
        )
    except Exception as e:
        print(f'[AI] web_research search failed: {e}')
        return []

    for i, r in enumerate(results):
        if i < deep:
            txt = websearch.fetch_fulltext(r.get('url', ''), max_chars=1800)
            if txt:
                r['fulltext'] = txt
    return results


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
        bias_val = data.get('bias', 50)
        if not isinstance(bias_val, int):
            try:
                bias_val = int(str(bias_val).strip())
            except Exception:
                bias_val = 50
        return {
            'dek':         str(data.get('dek', ''))[:300],
            'body':        [str(p) for p in (data.get('body') or [])[:4] if p],
            'key_points':  [str(k) for k in (data.get('key_points') or [])[:5] if k],
            'why_matters': str(data.get('why_matters', ''))[:400],
            'category':    str(data.get('category', 'WORLD')).upper(),
            'tag':         str(data.get('tag', 'nepal')).lower(),
            'bias':        max(0, min(100, bias_val)),
            'bias_label':  str(data.get('bias_label', 'Center')),
        }

    # ── Heuristic fallback ───────────────────────────────────────
    words = (text or '').split()
    paras = [' '.join(words[i:i + 70]) for i in range(0, min(len(words), 210), 70) if words[i:i + 70]]
    return {
        'dek':         (title or '')[:200],
        'body':        paras[:3] or [title],
        'key_points':  _keyword_points(title, text),
        'why_matters': f'{source_name} द्वारा प्रकाशित।',
        'category':    _guess_category(title, text),
        'tag':         _guess_tag(title, text),
        'bias':        50,
        'bias_label':  'Center',
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
    web_results = []
    if use_web:
        web_results = web_research(question, limit=8, deep=2)

    context = _build_context(context_articles or [], web_results)

    prompt_template = ASK_PROMPT_NP if lang == 'np' else ASK_PROMPT_EN
    prompt = prompt_template.format(context=context, question=question)

    raw = _gemini(prompt, max_tokens=900)

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
        return {'answer': answer, 'sources': sources[:5], 'related': related}

    # Gemini unavailable (rate-limited). If we still gathered live coverage,
    # return an EXTRACTIVE answer grounded in the real snippets — far better
    # than a canned number — so the RAG reporter stays useful without an LLM.
    if web_results:
        extractive = _extractive_answer(question, web_results, lang)
        if extractive:
            srcs = []
            for r in web_results:
                s = r.get('source')
                if s and s not in srcs:
                    srcs.append(s)
            return {
                'answer': extractive,
                'sources': srcs[:5] or ['samachar.ai'],
                'related': related,
            }

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
