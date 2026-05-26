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
    'models/gemini-1.5-flash-8b',     # 15 RPM free — last resort
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

ASK_PROMPT_NP = """तपाईं samachar.ai का AI सम्पादक हुनुहुन्छ — नेपालको सबैभन्दा स्मार्ट समाचार एप।
प्रयोगकर्ताको प्रश्नको उत्तर नेपालीमा ३-५ वाक्यमा दिनुहोस्।
नेपालको वास्तविक तथ्यहरू (राजनीति, NEPSE, जलविद्युत, मनसुन, क्रिकेट, आदि) मा आधारित रहनुहोस्।
थाहा नभए स्पष्ट भन्नुहोस् — कहिल्यै तथ्याङ्क बनाउनु हुँदैन।

हालको समाचार सन्दर्भ:
{context}

प्रयोगकर्ताको प्रश्न: {question}

अन्तमा ठ्याक्कै यो लाइन राख्नुहोस्: SOURCES: <२-३ नेपाली प्रकाशनहरूको नाम, comma separated>"""

ASK_PROMPT_EN = """You are the AI editor of samachar.ai — Nepal's smartest news app.
Answer in 3-5 sentences using real Nepal context (politics, NEPSE, hydropower, monsoon, cricket, etc.).
If unsure, say so briefly — never fabricate statistics.

Recent Nepal headlines for context:
{context}

User question: {question}

End with exactly: SOURCES: <2-3 Nepali publication names, comma separated>"""


def answer_question(question, lang='np', context_articles=None):
    """Ask Gemini a Nepal news question. Returns {answer, sources, related}."""
    ctx_lines = []
    if context_articles:
        for a in context_articles[:10]:
            ctx_lines.append(
                f"• [{a.get('source', '')}] {a.get('title', '')} — {a.get('dek', '')}"
            )
    context = '\n'.join(ctx_lines) if ctx_lines else 'हालको समाचार लोड भएको छैन।'

    prompt_template = ASK_PROMPT_NP if lang == 'np' else ASK_PROMPT_EN
    prompt = prompt_template.format(context=context, question=question)

    raw = _gemini(prompt, max_tokens=700)

    if raw:
        parts = re.split(r'SOURCES\s*:', raw, maxsplit=1, flags=re.IGNORECASE)
        answer = parts[0].strip()
        sources = []
        if len(parts) > 1:
            raw_sources = parts[1].split('\n')[0]
            sources = [s.strip().strip('.,।') for s in raw_sources.split(',') if s.strip()]
        if not sources:
            sources = ['OnlineKhabar', 'Kantipur']
        return {'answer': answer, 'sources': sources[:4], 'related': []}

    return _keyword_fallback(question)


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
