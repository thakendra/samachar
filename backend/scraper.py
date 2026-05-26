"""
Real-time news scanner for samachar.ai.
Uses newspaper4k (primary) + feedparser RSS + BeautifulSoup fallback.
AI-powered Nepali summarisation via Gemini after each scan.

Public API
----------
scrape_all()       → int   (new articles inserted)
get_status()       → dict  (last_run, total_articles, running, ...)
start_scheduler()  → None  (background thread, every INTERVAL_MIN minutes)
"""
import hashlib
import time
import re
import json
import threading
import datetime

import requests
import feedparser
from concurrent.futures import ThreadPoolExecutor, as_completed

# newspaper4k for high-quality article extraction
try:
    import newspaper
    from newspaper import Article as NpArticle
    NEWSPAPER_OK = True
except ImportError:
    NEWSPAPER_OK = False
    print('[scanner] newspaper4k not installed — using BeautifulSoup fallback')

from bs4 import BeautifulSoup

from db import get_db, now
import ai as ai_module

# ─── Source definitions ──────────────────────────────────────────────────────
SOURCES = [
    {
        'id':         'onlinekhabar',
        'name':       'OnlineKhabar',
        'url':        'https://www.onlinekhabar.com',
        'rss':        'https://www.onlinekhabar.com/feed',
        'bias':       42,
        'bias_label': 'Center-Left',
        'color':      '#e53935',
        'lang':       'np',
    },
    {
        'id':         'setopati',
        'name':       'Setopati',
        'url':        'https://www.setopati.com',
        'rss':        'https://setopati.com/feed',
        'bias':       38,
        'bias_label': 'Left-Center',
        'color':      '#1565c0',
        'lang':       'np',
    },
    {
        'id':         'ratopati',
        'name':       'Ratopati',
        'url':        'https://ratopati.com',
        'rss':        'https://ratopati.com/feed',
        'bias':       55,
        'bias_label': 'Center',
        'color':      '#c62828',
        'lang':       'np',
    },
    {
        'id':         'shilapatra',
        'name':       'Shilapatra',
        'url':        'https://shilapatra.com',
        'rss':        'https://shilapatra.com/feed',
        'bias':       52,
        'bias_label': 'Center',
        'color':      '#4527a0',
        'lang':       'np',
    },
    {
        'id':         'ekantipur',
        'name':       'Ekantipur',
        'url':        'https://ekantipur.com',
        'rss':        'https://ekantipur.com/rss',
        'bias':       55,
        'bias_label': 'Center',
        'color':      '#2e7d32',
        'lang':       'np',
    },
    {
        'id':         'nagarik',
        'name':       'Nagarik News',
        'url':        'https://nagariknews.nagariknetwork.com',
        'rss':        'https://nagariknews.nagariknetwork.com/feed',
        'bias':       60,
        'bias_label': 'Center-Right',
        'color':      '#e65100',
        'lang':       'np',
    },
    {
        'id':         'annapurnapost',
        'name':       'Annapurna Post',
        'url':        'https://annapurnapost.com',
        'rss':        'https://annapurnapost.com/feed',
        'bias':       50,
        'bias_label': 'Center',
        'color':      '#00695c',
        'lang':       'np',
    },
    {
        'id':         'galaxykhabar',
        'name':       'Galaxy Khabar',
        'url':        'https://www.galaxykhabar.com',
        'rss':        'https://www.galaxykhabar.com/feed',
        'bias':       50,
        'bias_label': 'Center',
        'color':      '#6a1b9a',
        'lang':       'np',
    },
]

HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/124.0.0.0 Safari/537.36'
    ),
    'Accept-Language': 'ne,en;q=0.9',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
}

INTERVAL_MIN    = 15    # scan every N minutes
MAX_PER_SOURCE  = 12    # articles per source per run
REQUEST_TIMEOUT = 15    # seconds per HTTP request
AI_ENRICH_DELAY = 4     # seconds between AI calls (free-tier safe: ~15/min)
MAX_WORKERS     = 4     # concurrent source threads

# ─── Status tracking ─────────────────────────────────────────────────────────
_status = {
    'last_run':       None,
    'last_run_human': 'Never',
    'total_new':      0,
    'sources_ok':     [],
    'sources_err':    [],
    'running':        False,
}
_status_lock = threading.Lock()


def get_status():
    with _status_lock:
        conn = get_db()
        try:
            total = conn.execute(
                "SELECT COUNT(*) FROM articles WHERE source_url IS NOT NULL"
            ).fetchone()[0]
        finally:
            conn.close()
        return {**_status, 'scraped_articles': total}


# ─── Article text extraction ─────────────────────────────────────────────────

def _fetch_with_newspaper(url):
    """
    Use newspaper4k to download and parse an article.
    Returns (title, text, top_image) or (None, '', None) on failure.
    """
    if not NEWSPAPER_OK:
        return None, '', None
    try:
        art = NpArticle(
            url,
            language='ne',
            request_timeout=REQUEST_TIMEOUT,
            headers=HEADERS,
            fetch_images=True,
            memoize_articles=False,
        )
        art.download()
        art.parse()
        title = art.title or None
        text  = art.text or ''
        img   = art.top_image or None
        # Try meta description if body is too thin
        if len(text) < 100 and art.meta_description:
            text = art.meta_description
        return title, text[:6000], img
    except Exception as e:
        print(f'[scanner] newspaper4k failed {url}: {e}')
        return None, '', None


_ARTICLE_SELECTORS = [
    ('div', re.compile(r'(entry|article|post|content|single|body|detail|ok-single|news-detail|story-content|article-text)', re.I)),
]


def _fetch_with_bs4(url):
    """BeautifulSoup fallback when newspaper4k fails."""
    try:
        r = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        r.raise_for_status()
        r.encoding = r.apparent_encoding or 'utf-8'
        soup = BeautifulSoup(r.text, 'lxml')
        for tag in soup(['script', 'style', 'nav', 'header', 'footer',
                         'aside', 'form', 'button', 'iframe', 'figure']):
            tag.decompose()
        for pat in _ARTICLE_SELECTORS:
            el = soup.find('div', class_=pat[1])
            if el:
                text = el.get_text(separator=' ', strip=True)
                if len(text) > 200:
                    return text[:6000]
        # fallback: all <p> tags
        paras = soup.find_all('p')
        return ' '.join(p.get_text(strip=True) for p in paras if len(p.get_text(strip=True)) > 40)[:6000]
    except Exception as e:
        print(f'[scanner] bs4 fetch failed {url}: {e}')
        return ''


def _fetch_article(url):
    """
    Try newspaper4k first; fall back to BeautifulSoup.
    Returns (np_title_or_None, full_text, img_url_or_None).
    """
    np_title, np_text, np_img = _fetch_with_newspaper(url)
    if np_text and len(np_text) > 200:
        return np_title, np_text, np_img
    # Fallback
    bs_text = _fetch_with_bs4(url)
    return None, bs_text, None


# ─── RSS parsing ─────────────────────────────────────────────────────────────

def _parse_rss(source):
    """
    Parse RSS feed for a source.
    Returns list of raw entry dicts with title, url, dek, published_at.
    """
    rss_url = source['rss']
    try:
        feed = feedparser.parse(
            rss_url,
            request_headers={'User-Agent': HEADERS['User-Agent']},
        )
        if feed.bozo and not feed.entries:
            r = requests.get(rss_url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
            feed = feedparser.parse(r.content)
    except Exception as e:
        print(f'[scanner] RSS error {source["id"]}: {e}')
        return []

    items = []
    for entry in feed.entries[:MAX_PER_SOURCE]:
        url   = entry.get('link') or entry.get('id') or ''
        title = entry.get('title') or ''
        title = BeautifulSoup(title, 'lxml').get_text(strip=True)
        dek   = entry.get('summary') or entry.get('description') or ''
        dek   = BeautifulSoup(dek, 'lxml').get_text(strip=True)[:300]

        published_at = now()
        if entry.get('published_parsed'):
            try:
                t = entry.published_parsed
                published_at = int(datetime.datetime(
                    t.tm_year, t.tm_mon, t.tm_mday,
                    t.tm_hour, t.tm_min, t.tm_sec
                ).timestamp())
            except Exception:
                pass

        if url and title:
            items.append({
                'title':        title,
                'url':          url,
                'dek':          dek,
                'published_at': published_at,
            })
    return items


# ─── Article ID ───────────────────────────────────────────────────────────────

def _article_id(url):
    return 'sc_' + hashlib.md5(url.encode('utf-8')).hexdigest()[:12]


def _time_label(published_at):
    diff = int(time.time()) - published_at
    if diff < 3600:
        return f'{max(1, diff // 60)}M AGO'
    if diff < 86400:
        return f'{diff // 3600}H AGO'
    return f'{diff // 86400}D AGO'


# ─── Core scan logic ──────────────────────────────────────────────────────────

def _scan_source(source):
    """Scan one source, insert new articles, return count of new articles."""
    entries = _parse_rss(source)
    if not entries:
        return 0

    new_count = 0
    conn = get_db()
    try:
        for entry in entries:
            art_id = _article_id(entry['url'])

            existing = conn.execute(
                'SELECT id, ai_processed FROM articles WHERE id = ?', (art_id,)
            ).fetchone()

            if existing:
                # Re-try AI enrichment if not yet processed
                if existing['ai_processed'] == 0:
                    time.sleep(AI_ENRICH_DELAY)
                    _ai_enrich(conn, art_id, entry, source)
                continue

            # ── Fetch full article text via newspaper4k ──────────────────
            np_title, full_text, img_url = _fetch_article(entry['url'])
            time.sleep(0.8)  # polite crawl delay

            # newspaper4k may give a better title
            best_title = (np_title or entry['title'])[:300]

            # Insert raw article
            conn.execute("""
                INSERT INTO articles
                  (id, title, dek, source, source_url, source_color,
                   bias, bias_label, published_at, time_label,
                   body, key_points, why_matters, category, tag,
                   img_url, full_text, scraped_at, ai_processed,
                   verified, verified_count, comments_count, likes, developing)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """, (
                art_id,
                best_title,
                entry['dek'][:300],
                source['name'],
                entry['url'],
                source['color'],
                source['bias'],
                source['bias_label'],
                entry['published_at'],
                _time_label(entry['published_at']),
                json.dumps([entry['dek']] if entry['dek'] else [best_title]),
                json.dumps([]),
                '',
                'WORLD',
                'nepal',
                img_url or '',
                full_text[:8000],
                now(),
                0,     # ai_processed = False
                0, 0, 0, 0, 0,
            ))
            conn.commit()
            new_count += 1

            # ── AI enrichment (throttled) ────────────────────────────────
            time.sleep(AI_ENRICH_DELAY)
            _ai_enrich(conn, art_id, entry, source, full_text=full_text,
                       np_title=best_title)

    finally:
        conn.close()

    return new_count


def _ai_enrich(conn, art_id, entry, source, full_text=None, np_title=None):
    """
    Call Gemini to enrich an article with Nepali dek, body, key_points, etc.
    Updates the DB row in-place.
    """
    if full_text is None:
        row = conn.execute('SELECT full_text, title FROM articles WHERE id = ?',
                           (art_id,)).fetchone()
        full_text = row['full_text'] if row else ''
        if not np_title and row:
            np_title = row['title']

    title = np_title or entry.get('title', '')

    try:
        enriched = ai_module.summarize_article(
            title=title,
            text=full_text or entry.get('dek', ''),
            source_name=source['name'],
        )
        conn.execute("""
            UPDATE articles SET
              dek=?, body=?, key_points=?, why_matters=?,
              category=?, tag=?, bias=?, bias_label=?, ai_processed=1
            WHERE id=?
        """, (
            enriched['dek'][:300],
            json.dumps(enriched['body']),
            json.dumps(enriched['key_points']),
            enriched['why_matters'][:400],
            enriched['category'],
            enriched['tag'],
            enriched['bias'],
            enriched['bias_label'],
            art_id,
        ))
        conn.commit()
    except Exception as e:
        print(f'[scanner] AI enrich failed {art_id}: {e}')
        try:
            conn.execute('UPDATE articles SET ai_processed=1 WHERE id=?', (art_id,))
            conn.commit()
        except Exception:
            pass


# ─── Full scan ────────────────────────────────────────────────────────────────

def scrape_all():
    """
    Scan all sources. Returns total new articles inserted.
    Thread-safe — concurrent calls are no-ops.
    """
    with _status_lock:
        if _status['running']:
            return 0
        _status['running'] = True

    ok, err, total_new = [], [], 0
    try:
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
            futures = {pool.submit(_scan_source, src): src for src in SOURCES}
            for future in as_completed(futures):
                src = futures[future]
                try:
                    n = future.result()
                    ok.append(src['name'])
                    total_new += n
                    print(f'[scanner] {src["name"]}: +{n} new articles')
                except Exception as e:
                    err.append(src['name'])
                    print(f'[scanner] ERROR {src["name"]}: {e}')

        _update_trends()

    finally:
        with _status_lock:
            _status['running'] = False
            _status['last_run'] = now()
            _status['last_run_human'] = datetime.datetime.now().strftime('%H:%M · %d %b')
            _status['total_new'] = total_new
            _status['sources_ok'] = ok
            _status['sources_err'] = err

    print(f'[scanner] Done — {total_new} new articles from {len(ok)} sources.')
    return total_new


# ─── Trend updater ────────────────────────────────────────────────────────────

def _update_trends():
    conn = get_db()
    try:
        rows = conn.execute("""
            SELECT title, category, source FROM articles
            ORDER BY published_at DESC LIMIT 100
        """).fetchall()

        from collections import Counter
        cats = Counter(r['category'] for r in rows)

        trends = []
        rank = 1
        for cat, count in cats.most_common(7):
            heat = 'hot' if count > 10 else ('breaking' if count > 6 else 'rising')
            trends.append({
                'rank': rank,
                'title': _cat_to_trend_title(cat),
                'sub': f'{count} stories · live',
                'heat': heat,
            })
            rank += 1

        conn.execute('DELETE FROM trends')
        for t in trends:
            conn.execute(
                'INSERT INTO trends (rank, title, sub, heat) VALUES (?, ?, ?, ?)',
                (t['rank'], t['title'], t['sub'], t['heat'])
            )
        conn.commit()
    except Exception as e:
        print(f'[scanner] trend update failed: {e}')
    finally:
        conn.close()


def _cat_to_trend_title(cat):
    return {
        'POLITICS':    'नेपाल राजनीति',
        'BUSINESS':    'नेप्से र अर्थतन्त्र',
        'TECHNOLOGY':  'प्रविधि र डिजिटल',
        'HEALTH':      'स्वास्थ्य',
        'SPORTS':      'खेलकुद · क्रिकेट',
        'CLIMATE':     'मौसम र वातावरण',
        'AGRICULTURE': 'कृषि',
        'HYPERLOCAL':  'काठमाडौं स्थानीय',
        'WORLD':       'विश्व समाचार',
    }.get(cat, cat.title())


# ─── Background scheduler ─────────────────────────────────────────────────────

_scheduler_started = False


def start_scheduler():
    """Start background scan thread — runs once only."""
    global _scheduler_started
    if _scheduler_started:
        return
    _scheduler_started = True

    def _loop():
        print(f'[scraper] Scheduler started — every {INTERVAL_MIN} min.')
        try:
            scrape_all()
        except Exception as e:
            print(f'[scanner] First-run error: {e}')
        while True:
            time.sleep(INTERVAL_MIN * 60)
            try:
                scrape_all()
            except Exception as e:
                print(f'[scanner] Loop error: {e}')

    t = threading.Thread(target=_loop, daemon=True, name='scanner')
    t.start()
