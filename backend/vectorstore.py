"""
Qdrant vector store for samachar.ai — RAG over our OWN news archive.

Every enriched article is embedded (gemini-embedding-001 via llm.embed) and
upserted into a Qdrant Cloud collection. At question time we embed the query
and pull the most semantically-similar archive articles to ground the answer —
this complements the live web search with our curated, already-summarized
coverage.

Design rules:
  • Pure REST (requests) — no extra SDK dependency, works on the VPS as-is.
  • Everything is best-effort: any failure returns []/False and logs, never
    raises, so the app keeps working when Qdrant or embeddings are down.
  • Credentials come only from the environment.
"""
import os
import requests

import llm

QDRANT_URL     = (os.getenv('QDRANT_URL', '') or '').rstrip('/')
QDRANT_API_KEY = os.getenv('QDRANT_API_KEY', '')
COLLECTION     = os.getenv('QDRANT_COLLECTION', 'samachar_articles')
TIMEOUT        = 20

_collection_ready = False


def _enabled():
    return bool(QDRANT_URL and QDRANT_API_KEY)


def _headers():
    return {'api-key': QDRANT_API_KEY, 'Content-Type': 'application/json'}


def _point_id(article_id):
    """Qdrant needs an unsigned-int or UUID id; hash our TEXT article id."""
    import hashlib
    h = hashlib.md5(str(article_id).encode('utf-8')).hexdigest()
    return int(h[:16], 16)   # 64-bit unsigned int


def ensure_collection(dim=None):
    """Create the collection if it doesn't exist. Returns True if ready."""
    global _collection_ready
    if not _enabled():
        return False
    if _collection_ready:
        return True
    dim = dim or llm.EMBED_DIM
    try:
        r = requests.get(f'{QDRANT_URL}/collections/{COLLECTION}',
                         headers=_headers(), timeout=TIMEOUT)
        if r.status_code == 200:
            _collection_ready = True
            return True
        # Create it (cosine distance for normalized semantic similarity).
        r = requests.put(
            f'{QDRANT_URL}/collections/{COLLECTION}',
            headers=_headers(),
            json={'vectors': {'size': dim, 'distance': 'Cosine'}},
            timeout=TIMEOUT,
        )
        if r.status_code in (200, 201):
            _collection_ready = True
            print(f'[vectorstore] created collection {COLLECTION} (dim={dim})')
            return True
        print(f'[vectorstore] ensure_collection failed {r.status_code}: {r.text[:160]}')
        return False
    except Exception as e:
        print(f'[vectorstore] ensure_collection error: {e}')
        return False


def index_article(article):
    """
    Embed + upsert one article. `article` is a dict with at least
    id, title; optionally dek, source, tag, category, published_at.
    Returns True on success. Best-effort — never raises.
    """
    if not _enabled():
        return False
    art_id = article.get('id')
    if not art_id:
        return False

    # Build the text we embed — title + dek/summary carry the meaning.
    text = ' '.join(filter(None, [
        article.get('title', ''),
        article.get('dek', ''),
        (article.get('why_matters', '') or '')[:200],
    ])).strip()
    if not text:
        return False

    vector = llm.embed(text)
    if not vector:
        return False

    if not ensure_collection(dim=len(vector)):
        return False

    payload = {
        'article_id': str(art_id),
        'title':      article.get('title', ''),
        'dek':        article.get('dek', ''),
        'source':     article.get('source', ''),
        'tag':        article.get('tag', ''),
        'category':   article.get('category', ''),
        'published_at': article.get('published_at', 0),
    }
    try:
        r = requests.put(
            f'{QDRANT_URL}/collections/{COLLECTION}/points',
            headers=_headers(),
            json={'points': [{
                'id': _point_id(art_id),
                'vector': vector,
                'payload': payload,
            }]},
            timeout=TIMEOUT,
        )
        if r.status_code in (200, 201):
            return True
        print(f'[vectorstore] upsert failed {r.status_code}: {r.text[:160]}')
        return False
    except Exception as e:
        print(f'[vectorstore] index_article error: {e}')
        return False


def search(query, limit=6):
    """
    Semantic search over the archive. Returns a list of result dicts
    {article_id, title, dek, source, tag, score}. [] if unavailable.
    """
    if not _enabled() or not query:
        return []
    vector = llm.embed(query)
    if not vector:
        return []
    if not ensure_collection(dim=len(vector)):
        return []
    try:
        r = requests.post(
            f'{QDRANT_URL}/collections/{COLLECTION}/points/search',
            headers=_headers(),
            json={'vector': vector, 'limit': limit, 'with_payload': True},
            timeout=TIMEOUT,
        )
        if r.status_code != 200:
            print(f'[vectorstore] search failed {r.status_code}: {r.text[:160]}')
            return []
        out = []
        for hit in r.json().get('result', []):
            p = hit.get('payload', {}) or {}
            out.append({
                'article_id': p.get('article_id', ''),
                'title':      p.get('title', ''),
                'dek':        p.get('dek', ''),
                'source':     p.get('source', ''),
                'tag':        p.get('tag', ''),
                'score':      hit.get('score', 0),
            })
        return out
    except Exception as e:
        print(f'[vectorstore] search error: {e}')
        return []


def status():
    info = {'enabled': _enabled(), 'collection': COLLECTION, 'ready': False, 'count': None}
    if not _enabled():
        return info
    try:
        r = requests.get(f'{QDRANT_URL}/collections/{COLLECTION}',
                         headers=_headers(), timeout=TIMEOUT)
        if r.status_code == 200:
            info['ready'] = True
            res = r.json().get('result', {})
            info['count'] = res.get('points_count')
    except Exception as e:
        info['error'] = str(e)
    return info
