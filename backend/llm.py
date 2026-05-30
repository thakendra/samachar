"""
LLM provider layer + smart router for samachar.ai.

The "3-layer AI stack":
  • Groq (LLaMA 3.3 70B)   — cheap, fast bulk brain: English + structured JSON.
  • Gemini (Flash family)  — premium brain: quality Nepali Devanagari prose.
  • Embeddings (Gemini)    — gemini-embedding-001 → powers Qdrant vector RAG.

Routing principle: "Cheap models process data. Smart models talk to users."
Groq is NEVER trusted to write Nepali prose (it produces broken Devanagari),
so the router protects Nepali quality:

    generate(prompt, nepali=True)   → Gemini only  (else None → extractive fallback)
    generate(prompt, nepali=False)  → Gemini, then Groq fallback (English/JSON)

Every function is defensive: returns None / [] on any failure, never raises.
All credentials come from the environment — nothing is hardcoded here.
"""
import os
import re
import time
import threading

import requests

# ── Credentials (env only — never commit keys) ───────────────────
GROQ_API_KEY   = os.getenv('GROQ_API_KEY', '')
# Primary Gemini key (generation). A second key can be supplied for embeddings
# (the new key has a separate embedding quota pool even when generation is 0).
GEMINI_API_KEY     = os.getenv('GEMINI_API_KEY', '')
GEMINI_EMBED_KEY   = os.getenv('GEMINI_EMBED_KEY', '') or GEMINI_API_KEY

# ── Endpoints / models ───────────────────────────────────────────
GROQ_URL    = 'https://api.groq.com/openai/v1/chat/completions'
GROQ_MODEL  = os.getenv('GROQ_MODEL', 'llama-3.3-70b-versatile')

GEMINI_BASE   = 'https://generativelanguage.googleapis.com/v1beta'
GEMINI_MODELS = [
    'models/gemini-2.0-flash-lite',   # 30 RPM free — primary
    'models/gemini-2.0-flash',        # 15 RPM free — fallback
    'models/gemini-2.5-flash',        # 5 RPM free  — separate quota pool
]
EMBED_MODEL = os.getenv('GEMINI_EMBED_MODEL', 'models/gemini-embedding-001')
EMBED_DIM   = int(os.getenv('EMBED_DIM', '768'))

TIMEOUT = 30

# ── Gemini model rotation / cooldown ─────────────────────────────
_model_index    = 0
_model_lock     = threading.Lock()
_model_cooldown = {}   # model → epoch when safe to retry


def _current_model():
    return GEMINI_MODELS[_model_index % len(GEMINI_MODELS)]


def _advance_model(bad_model):
    global _model_index
    with _model_lock:
        if _current_model() == bad_model:
            _model_index += 1
            if _model_index >= len(GEMINI_MODELS):
                _model_index = 0


# ── Gemini generation (REST) ─────────────────────────────────────
def gemini_chat(prompt, max_tokens=800, temperature=0.3):
    """
    Call Gemini via REST and return text, rotating models on 429/404.
    Returns None if no key or all models are exhausted/unavailable.
    """
    if not GEMINI_API_KEY:
        return None

    tried = set()
    for _ in range(len(GEMINI_MODELS) + 1):
        model = _current_model()
        if model in tried:
            break
        tried.add(model)

        if time.time() < _model_cooldown.get(model, 0):
            _advance_model(model)
            continue

        url = f'{GEMINI_BASE}/{model}:generateContent?key={GEMINI_API_KEY}'
        payload = {
            'contents': [{'parts': [{'text': prompt}]}],
            'generationConfig': {
                'temperature': temperature,
                'maxOutputTokens': max_tokens,
            },
        }
        try:
            r = requests.post(url, json=payload, timeout=TIMEOUT)
            if r.status_code == 200:
                data = r.json()
                cands = data.get('candidates') or []
                if cands:
                    parts = cands[0].get('content', {}).get('parts', [])
                    text = ''.join(p.get('text', '') for p in parts).strip()
                    if text:
                        return text
                # Empty/blocked response — try next model.
                _advance_model(model)
                continue
            if r.status_code in (429, 503):
                delay = 65
                m = re.search(r'retryDelay["\s:]+(\d+)', r.text)
                if m:
                    delay = int(m.group(1)) + 5
                _model_cooldown[model] = time.time() + delay
                print(f'[llm] gemini {model} rate-limited — cooldown {delay}s')
                _advance_model(model)
                continue
            if r.status_code in (400, 404):
                print(f'[llm] gemini {model} unavailable ({r.status_code})')
                _advance_model(model)
                continue
            # Other error (401 etc.) — no point rotating.
            print(f'[llm] gemini error {r.status_code}: {r.text[:160]}')
            return None
        except Exception as e:
            print(f'[llm] gemini request failed: {e}')
            return None

    return None


# ── Groq generation (OpenAI-compatible REST) ─────────────────────
def groq_chat(prompt, max_tokens=800, temperature=0.3, system=None):
    """
    Call Groq's OpenAI-compatible chat endpoint. Cheap + fast.
    Use for English text and structured JSON only — NOT Nepali prose.
    Returns None on any failure / missing key.
    """
    if not GROQ_API_KEY:
        return None
    messages = []
    if system:
        messages.append({'role': 'system', 'content': system})
    messages.append({'role': 'user', 'content': prompt})
    try:
        r = requests.post(
            GROQ_URL,
            headers={'Authorization': f'Bearer {GROQ_API_KEY}',
                     'Content-Type': 'application/json'},
            json={
                'model': GROQ_MODEL,
                'messages': messages,
                'temperature': temperature,
                'max_tokens': max_tokens,
            },
            timeout=TIMEOUT,
        )
        if r.status_code == 200:
            data = r.json()
            choices = data.get('choices') or []
            if choices:
                return (choices[0].get('message', {}).get('content') or '').strip()
            return None
        print(f'[llm] groq error {r.status_code}: {r.text[:160]}')
        return None
    except Exception as e:
        print(f'[llm] groq request failed: {e}')
        return None


# ── Devanagari guard (protects Nepali quality) ───────────────────
_DEVANAGARI = re.compile(r'[ऀ-ॿ]')


def _has_devanagari(text):
    return bool(_DEVANAGARI.search(text or ''))


def _devanagari_ratio(text):
    if not text:
        return 0.0
    dev = len(_DEVANAGARI.findall(text))
    letters = sum(1 for c in text if c.isalpha())
    return dev / letters if letters else 0.0


# ── The router ───────────────────────────────────────────────────
def generate(prompt, max_tokens=800, temperature=0.3, nepali=False, allow_groq=True):
    """
    Smart routing entry point.

    nepali=True  → the output must be Nepali Devanagari prose. Only Gemini can
                   do this well, so we call Gemini and DO NOT fall back to Groq
                   (broken Nepali is worse than none — caller uses extractive).
                   Returns None if Gemini is unavailable.

    nepali=False → English text or structured JSON. Try Gemini first (best
                   reasoning), then fall back to Groq when allowed. This is the
                   path for query expansion, tags, English answers, etc.
    """
    text = gemini_chat(prompt, max_tokens=max_tokens, temperature=temperature)

    if nepali:
        # Accept Gemini output only if it's genuinely Devanagari.
        if text and _devanagari_ratio(text) > 0.25:
            return text
        return None

    if text:
        return text
    if allow_groq:
        return groq_chat(prompt, max_tokens=max_tokens, temperature=temperature)
    return None


# ── Embeddings (Gemini) — powers Qdrant vector RAG ───────────────
def embed(text, dim=EMBED_DIM):
    """
    Return an embedding vector (list[float]) for `text`, or None on failure.
    Uses gemini-embedding-001 with outputDimensionality=dim. The embedding key
    has its own quota pool, so this keeps working even when generation is at 0.
    """
    if not GEMINI_EMBED_KEY or not text:
        return None
    url = f'{GEMINI_BASE}/{EMBED_MODEL}:embedContent?key={GEMINI_EMBED_KEY}'
    payload = {
        'model': EMBED_MODEL,
        'content': {'parts': [{'text': text[:8000]}]},
        'outputDimensionality': dim,
    }
    try:
        r = requests.post(url, json=payload, timeout=TIMEOUT)
        if r.status_code == 200:
            vals = (r.json().get('embedding') or {}).get('values')
            if vals:
                return vals
            return None
        if r.status_code == 429:
            print('[llm] embed rate-limited')
        else:
            print(f'[llm] embed error {r.status_code}: {r.text[:160]}')
        return None
    except Exception as e:
        print(f'[llm] embed request failed: {e}')
        return None


def status():
    """Quick capability report — handy for /health or debugging."""
    return {
        'groq':           bool(GROQ_API_KEY),
        'gemini':         bool(GEMINI_API_KEY),
        'gemini_embed':   bool(GEMINI_EMBED_KEY),
        'groq_model':     GROQ_MODEL,
        'gemini_models':  GEMINI_MODELS,
        'embed_model':    EMBED_MODEL,
        'embed_dim':      EMBED_DIM,
    }
