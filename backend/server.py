"""
samachar.ai — Flask REST API + live scraper + Gemini AI.

Run:  python server.py
Open: http://localhost:5000
"""
import json
import os
import re
import secrets
import hashlib
import datetime
import time
import queue
import threading

from flask import Flask, jsonify, request, session, send_from_directory, Response, stream_with_context
from flask_cors import CORS

from db import init_db, get_db, now, row_to_dict
from seed import seed_articles, ARTICLES as SEED_ARTICLES
import ai as ai_module
import scraper as scraper_module

STATIC_DIR = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', 'static'))

app = Flask(__name__, static_folder=STATIC_DIR, static_url_path='')
app.secret_key = os.environ.get('SAMACHAR_SECRET') or secrets.token_hex(32)
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_PERMANENT'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(days=30)
app.config['JSON_SORT_KEYS'] = False
CORS(app, supports_credentials=True, origins=['http://localhost:5000', 'http://127.0.0.1:5000'])

# ── SSE event bus ─────────────────────────────────────────────
_sse_clients = []
_sse_lock = threading.Lock()


def _broadcast(event_type, data):
    payload = f"event: {event_type}\ndata: {json.dumps(data)}\n\n"
    with _sse_lock:
        dead = []
        for q in _sse_clients:
            try:
                q.put_nowait(payload)
            except Exception:
                dead.append(q)
        for q in dead:
            _sse_clients.remove(q)


TOPICS = [
    {'id': 't1', 'icon': 'building',     'name': 'Politics',    'sub': 'Sansad · parties · policy'},
    {'id': 't2', 'icon': 'chart',        'name': 'Business',    'sub': 'NEPSE · trade · macro'},
    {'id': 't3', 'icon': 'pin',          'name': 'Hyperlocal',  'sub': 'Your ward · municipality'},
    {'id': 't4', 'icon': 'sparkle',      'name': 'Tech',        'sub': 'Fintech · digital · startup'},
    {'id': 't5', 'icon': 'plant',        'name': 'Agriculture', 'sub': 'Farming · prices · climate'},
    {'id': 't6', 'icon': 'globe',        'name': 'Remittance',  'sub': 'Diaspora · forex · banking'},
    {'id': 't7', 'icon': 'shield-check', 'name': 'Health',      'sub': 'Public health · hospitals'},
    {'id': 't8', 'icon': 'mountain',     'name': 'Climate',     'sub': 'Floods · glaciers · air'},
]

DISTRICTS = [
    {'name': 'Kathmandu', 'stories': '1.2k', 'icon': 'building'},
    {'name': 'Pokhara',   'stories': '430',  'icon': 'mountain'},
    {'name': 'Chitwan',   'stories': '218',  'icon': 'plant'},
    {'name': 'Biratnagar','stories': '176',  'icon': 'building'},
    {'name': 'Butwal',    'stories': '92',   'icon': 'water'},
    {'name': 'All 75',    'stories': 'full', 'icon': 'pin'},
]

# ── Helpers ───────────────────────────────────────────────────

def jerr(msg, code=400):
    return jsonify({'error': msg}), code


def require_auth(fn):
    from functools import wraps
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            return jerr('not authenticated', 401)
        return fn(*args, **kwargs)
    return wrapper


def current_user():
    if 'user_id' not in session:
        return None
    conn = get_db()
    try:
        row = conn.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
        return row_to_dict(row)
    finally:
        conn.close()


def _hash_pw(pw):
    return hashlib.sha256(pw.encode('utf-8')).hexdigest()


def reset_quota_if_needed(conn, user_id):
    today = datetime.date.today().isoformat()
    row = conn.execute('SELECT ai_quota_date, plan FROM users WHERE id = ?', (user_id,)).fetchone()
    if not row:
        return
    if row['ai_quota_date'] != today:
        quota = 999 if row['plan'] == 'pro' else 10
        conn.execute('UPDATE users SET ai_quota = ?, ai_quota_date = ? WHERE id = ?',
                     (quota, today, user_id))
        conn.commit()


def article_to_dict(row):
    d = row_to_dict(row)
    if d is None:
        return None
    d['body']       = json.loads(d.get('body') or '[]')
    d['key_points'] = json.loads(d.get('key_points') or '[]')
    d.pop('full_text', None)   # don't send raw text to frontend
    return d


def _fresh_user(conn, user_id):
    """Return user dict with topics, stats."""
    user = row_to_dict(conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone())
    topics = [r['topic_id'] for r in conn.execute(
        'SELECT topic_id FROM user_topics WHERE user_id = ?', (user_id,))]
    user['topics'] = topics
    user.pop('password_hash', None)
    return user


# ── Auth ──────────────────────────────────────────────────────

@app.post('/api/auth/signup')
def signup():
    data = request.get_json(silent=True) or {}
    name  = (data.get('name') or '').strip()
    email = (data.get('email') or '').strip().lower()
    pw    = (data.get('password') or '').strip()
    ward  = (data.get('ward') or 'Ward 5, Lalitpur').strip()

    if not name:
        return jerr('Name is required')
    if not email or not re.match(r'^[^@\s]+@[^@\s]+\.[^@\s]+$', email):
        return jerr('Valid email required')
    if len(pw) < 6:
        return jerr('Password must be at least 6 characters')

    conn = get_db()
    try:
        if conn.execute('SELECT 1 FROM users WHERE email = ?', (email,)).fetchone():
            return jerr('Email already registered')
        today = datetime.date.today().isoformat()
        cur = conn.execute("""
            INSERT INTO users (name, email, password_hash, ward, ai_quota_date, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (name, email, _hash_pw(pw), ward, today, now()))
        conn.commit()
        session['user_id'] = cur.lastrowid
        session.permanent = True
        return jsonify(_fresh_user(conn, cur.lastrowid))
    finally:
        conn.close()


@app.post('/api/auth/login')
def login():
    data  = request.get_json(silent=True) or {}
    email = (data.get('email') or '').strip().lower()
    pw    = (data.get('password') or '').strip()
    # Legacy name-only login support
    name  = (data.get('name') or '').strip()

    conn = get_db()
    try:
        if email and pw:
            row = conn.execute(
                'SELECT * FROM users WHERE email = ?', (email,)
            ).fetchone()
            if not row or row['password_hash'] != _hash_pw(pw):
                return jerr('Invalid email or password', 401)
            user_id = row['id']
        elif name:
            # Legacy: name-only guest mode
            row = conn.execute('SELECT id FROM users WHERE name = ? AND email IS NULL', (name,)).fetchone()
            if row:
                user_id = row['id']
            else:
                today = datetime.date.today().isoformat()
                ward = (data.get('ward') or 'Ward 5, Lalitpur').strip()
                cur = conn.execute("""
                    INSERT INTO users (name, ward, ai_quota_date, created_at)
                    VALUES (?, ?, ?, ?)
                """, (name, ward, today, now()))
                conn.commit()
                user_id = cur.lastrowid
        else:
            return jerr('Email/password or name required')

        reset_quota_if_needed(conn, user_id)
        session['user_id'] = user_id
        session.permanent = True
        return jsonify(_fresh_user(conn, user_id))
    finally:
        conn.close()


@app.post('/api/auth/logout')
def logout():
    session.pop('user_id', None)
    return jsonify({'ok': True})


@app.get('/api/auth/me')
def me():
    uid = session.get('user_id')
    if not uid:
        return jsonify(None)
    conn = get_db()
    try:
        reset_quota_if_needed(conn, uid)
        return jsonify(_fresh_user(conn, uid))
    finally:
        conn.close()


# ── Preferences ───────────────────────────────────────────────

@app.put('/api/prefs')
@require_auth
def update_prefs():
    data = request.get_json(silent=True) or {}
    allowed = {'theme', 'language', 'accent', 'density', 'ward', 'show_frame', 'onboarded'}
    fields = {k: v for k, v in data.items() if k in allowed}
    if not fields:
        return jerr('no valid fields')
    sets = ', '.join(f'{k} = ?' for k in fields)
    vals = list(fields.values()) + [session['user_id']]
    conn = get_db()
    try:
        conn.execute(f'UPDATE users SET {sets} WHERE id = ?', vals)
        conn.commit()
        return jsonify(_fresh_user(conn, session['user_id']))
    finally:
        conn.close()


@app.put('/api/topics')
@require_auth
def update_topics():
    data = request.get_json(silent=True) or {}
    topics = data.get('topics') or []
    conn = get_db()
    try:
        conn.execute('DELETE FROM user_topics WHERE user_id = ?', (session['user_id'],))
        for t in topics:
            conn.execute('INSERT INTO user_topics (user_id, topic_id) VALUES (?, ?)',
                         (session['user_id'], t))
        conn.commit()
        return jsonify({'topics': topics})
    finally:
        conn.close()


# ── Catalogue ─────────────────────────────────────────────────

@app.get('/api/topics')
def list_topics():
    return jsonify(TOPICS)


@app.get('/api/districts')
def list_districts():
    return jsonify(DISTRICTS)


@app.get('/api/trends')
def list_trends():
    conn = get_db()
    try:
        rows = conn.execute('SELECT * FROM trends ORDER BY rank').fetchall()
        return jsonify([row_to_dict(r) for r in rows])
    finally:
        conn.close()


# ── Articles ──────────────────────────────────────────────────

@app.get('/api/articles')
def list_articles():
    tag      = request.args.get('tag', '').strip()
    q        = request.args.get('q', '').strip()
    topic    = request.args.get('topic', '').strip()   # category filter
    limit    = min(int(request.args.get('limit', 60)), 100)
    conn     = get_db()
    try:
        sql    = 'SELECT * FROM articles WHERE 1=1'
        params = []

        # Tag filter (feed tabs)
        if tag and tag != 'foryou':
            sql += ' AND tag = ?'
            params.append(tag)

        # Topic/category filter (search pills)
        if topic:
            sql += ' AND category = ?'
            params.append(topic.upper())

        # Word-based search — each word matched independently (OR logic across fields)
        if q:
            words = [w.strip() for w in q.split() if len(w.strip()) > 1][:6]
            if words:
                word_clauses = []
                for word in words:
                    like = f'%{word}%'
                    word_clauses.append(
                        "(title LIKE ? OR dek LIKE ? OR why_matters LIKE ? OR source LIKE ? OR key_points LIKE ?)"
                    )
                    params += [like, like, like, like, like]
                sql += ' AND (' + ' OR '.join(word_clauses) + ')'

        sql += ' ORDER BY published_at DESC LIMIT ?'
        params.append(limit)
        rows = conn.execute(sql, params).fetchall()
        return jsonify([article_to_dict(r) for r in rows])
    finally:
        conn.close()


@app.get('/api/articles/<aid>')
def get_article(aid):
    conn = get_db()
    try:
        row = conn.execute('SELECT * FROM articles WHERE id = ?', (aid,)).fetchone()
        if not row:
            return jerr('not found', 404)
        data = article_to_dict(row)
        rels = conn.execute("""
            SELECT * FROM articles
            WHERE id != ? AND (tag = ? OR category = ?)
            ORDER BY published_at DESC LIMIT 4
        """, (aid, row['tag'], row['category'])).fetchall()
        data['related'] = [article_to_dict(r) for r in rels]
        if 'user_id' in session:
            conn.execute("""
                INSERT OR REPLACE INTO read_history (user_id, article_id, read_at)
                VALUES (?, ?, ?)
            """, (session['user_id'], aid, now()))
            conn.commit()
        return jsonify(data)
    finally:
        conn.close()


# ── Scraper API ───────────────────────────────────────────────

@app.get('/api/scrape/status')
def scrape_status():
    return jsonify(scraper_module.get_status())


@app.post('/api/scrape/trigger')
@require_auth
def scrape_trigger():
    """Manually trigger a news scan (runs in background)."""
    def _run():
        n = scraper_module.scrape_all()
        _broadcast('scrape_done', {'new_articles': n})
    t = threading.Thread(target=_run, daemon=True)
    t.start()
    return jsonify({'ok': True, 'message': 'सबै स्रोतहरू स्क्यान सुरु भयो…'})


# ── Real-time SSE ─────────────────────────────────────────────

@app.get('/api/feed/live')
def feed_live():
    """Server-Sent Events stream for live updates."""
    q = queue.Queue(maxsize=50)
    with _sse_lock:
        _sse_clients.append(q)

    def generate():
        # Send initial ping
        yield "event: ping\ndata: {}\n\n"
        try:
            while True:
                try:
                    msg = q.get(timeout=25)
                    yield msg
                except queue.Empty:
                    yield "event: ping\ndata: {}\n\n"
        except GeneratorExit:
            pass
        finally:
            with _sse_lock:
                try:
                    _sse_clients.remove(q)
                except ValueError:
                    pass

    return Response(
        stream_with_context(generate()),
        mimetype='text/event-stream',
        headers={
            'Cache-Control':  'no-cache',
            'X-Accel-Buffering': 'no',
            'Connection':     'keep-alive',
        },
    )


# ── Bookmarks ─────────────────────────────────────────────────

@app.get('/api/bookmarks')
@require_auth
def list_bookmarks():
    conn = get_db()
    try:
        rows = conn.execute("""
            SELECT a.* FROM articles a
            JOIN bookmarks b ON b.article_id = a.id
            WHERE b.user_id = ?
            ORDER BY b.created_at DESC
        """, (session['user_id'],)).fetchall()
        return jsonify([article_to_dict(r) for r in rows])
    finally:
        conn.close()


@app.post('/api/bookmarks/<aid>/toggle')
@require_auth
def toggle_bookmark(aid):
    conn = get_db()
    try:
        if not conn.execute('SELECT 1 FROM articles WHERE id = ?', (aid,)).fetchone():
            return jerr('article not found', 404)
        existing = conn.execute(
            'SELECT 1 FROM bookmarks WHERE user_id = ? AND article_id = ?',
            (session['user_id'], aid)
        ).fetchone()
        if existing:
            conn.execute('DELETE FROM bookmarks WHERE user_id = ? AND article_id = ?',
                         (session['user_id'], aid))
            saved = False
        else:
            conn.execute('INSERT INTO bookmarks (user_id, article_id, created_at) VALUES (?, ?, ?)',
                         (session['user_id'], aid, now()))
            saved = True
        conn.commit()
        return jsonify({'saved': saved})
    finally:
        conn.close()


# ── Comments ──────────────────────────────────────────────────

@app.get('/api/articles/<aid>/comments')
def list_comments(aid):
    conn = get_db()
    try:
        rows = conn.execute("""
            SELECT c.*,
              (SELECT vote FROM comment_reactions
               WHERE comment_id = c.id AND user_id = ?) AS my_vote
            FROM comments c
            WHERE article_id = ?
            ORDER BY created_at DESC
        """, (session.get('user_id'), aid)).fetchall()
        return jsonify([row_to_dict(r) for r in rows])
    finally:
        conn.close()


@app.post('/api/articles/<aid>/comments')
@require_auth
def post_comment(aid):
    data = request.get_json(silent=True) or {}
    text = (data.get('text') or '').strip()
    if not text or len(text) > 1000:
        return jerr('text required (under 1000 chars)')
    user = current_user()
    initials = ''.join(p[0] for p in user['name'].split()[:2]).upper() or 'YO'
    conn = get_db()
    try:
        if not conn.execute('SELECT 1 FROM articles WHERE id = ?', (aid,)).fetchone():
            return jerr('article not found', 404)
        cur = conn.execute("""
            INSERT INTO comments (article_id, user_id, name, initials, place, text, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (aid, user['id'], user['name'], initials, user['ward'], text, now()))
        conn.execute('UPDATE articles SET comments_count = comments_count + 1 WHERE id = ?', (aid,))
        conn.commit()
        row = conn.execute('SELECT * FROM comments WHERE id = ?', (cur.lastrowid,)).fetchone()
        return jsonify(row_to_dict(row))
    finally:
        conn.close()


@app.post('/api/comments/<int:cid>/vote')
@require_auth
def vote_comment(cid):
    data = request.get_json(silent=True) or {}
    vote = data.get('vote')
    if vote not in (1, -1, 0):
        return jerr('vote must be 1, -1, or 0')
    conn = get_db()
    try:
        existing = conn.execute(
            'SELECT vote FROM comment_reactions WHERE comment_id = ? AND user_id = ?',
            (cid, session['user_id'])
        ).fetchone()
        old = existing['vote'] if existing else 0
        if vote == 0:
            conn.execute('DELETE FROM comment_reactions WHERE comment_id = ? AND user_id = ?',
                         (cid, session['user_id']))
        elif existing:
            conn.execute('UPDATE comment_reactions SET vote = ? WHERE comment_id = ? AND user_id = ?',
                         (vote, cid, session['user_id']))
        else:
            conn.execute('INSERT INTO comment_reactions (user_id, comment_id, vote) VALUES (?, ?, ?)',
                         (session['user_id'], cid, vote))
        like_d = (1 if vote == 1 else 0) - (1 if old == 1 else 0)
        dis_d  = (1 if vote == -1 else 0) - (1 if old == -1 else 0)
        if like_d: conn.execute('UPDATE comments SET likes    = likes    + ? WHERE id = ?', (like_d, cid))
        if dis_d:  conn.execute('UPDATE comments SET dislikes = dislikes + ? WHERE id = ?', (dis_d, cid))
        conn.commit()
        return jsonify(row_to_dict(conn.execute('SELECT * FROM comments WHERE id = ?', (cid,)).fetchone()))
    finally:
        conn.close()


# ── AI ────────────────────────────────────────────────────────

@app.post('/api/ai/ask')
def ai_ask():
    data     = request.get_json(silent=True) or {}
    question = (data.get('question') or '').strip()
    if not question or len(question) > 600:
        return jerr('question required (under 600 chars)')

    conn = get_db()
    try:
        # Pull recent articles for context (always available)
        recent = conn.execute("""
            SELECT title, source, dek FROM articles
            ORDER BY published_at DESC LIMIT 15
        """).fetchall()
        context_articles = [row_to_dict(r) for r in recent]

        # Authenticated web users: enforce quota, use their language pref
        if 'user_id' in session:
            reset_quota_if_needed(conn, session['user_id'])
            user = conn.execute(
                'SELECT plan, ai_quota, language FROM users WHERE id = ?',
                (session['user_id'],)
            ).fetchone()
            if user['plan'] != 'pro' and user['ai_quota'] <= 0:
                return jsonify({'quota_exceeded': True,
                                'message': 'Daily quota used. Upgrade to Pro for unlimited.'}), 429
            lang = user['language']
            result = ai_module.answer_question(question, lang=lang, context_articles=context_articles)
            if user['plan'] != 'pro':
                conn.execute('UPDATE users SET ai_quota = ai_quota - 1 WHERE id = ?',
                             (session['user_id'],))
            conn.execute("""
                INSERT INTO ai_log (user_id, question, answer, sources, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, (session['user_id'], question,
                  result['answer'], json.dumps(result.get('sources', [])), now()))
            conn.commit()
            new_quota = conn.execute(
                'SELECT ai_quota FROM users WHERE id = ?', (session['user_id'],)
            ).fetchone()['ai_quota']
            return jsonify({
                'question':        question,
                'answer':          result['answer'],
                'sources':         result.get('sources', []),
                'related':         result.get('related', []),
                'remaining_quota': new_quota if user['plan'] != 'pro' else 999,
            })

        # Unauthenticated (Android / mobile app): answer without quota tracking
        lang = (data.get('lang') or 'np')[:5]
        result = ai_module.answer_question(question, lang=lang, context_articles=context_articles)
        return jsonify({
            'question':        question,
            'answer':          result['answer'],
            'sources':         result.get('sources', []),
            'related':         result.get('related', []),
            'remaining_quota': 10,
        })
    finally:
        conn.close()


@app.get('/api/ai/history')
@require_auth
def ai_history():
    conn = get_db()
    try:
        rows = conn.execute("""
            SELECT id, question, answer, sources, created_at FROM ai_log
            WHERE user_id = ? ORDER BY created_at DESC LIMIT 50
        """, (session['user_id'],)).fetchall()
        out = []
        for r in rows:
            d = row_to_dict(r)
            d['sources'] = json.loads(d.get('sources') or '[]')
            out.append(d)
        return jsonify(out)
    finally:
        conn.close()


# ── Notifications ─────────────────────────────────────────────

@app.get('/api/notifications')
def list_notifications():
    conn = get_db()
    try:
        uid  = session.get('user_id')
        rows = conn.execute("""
            SELECT n.*,
              (SELECT 1 FROM notif_read WHERE notif_id = n.id AND user_id = ?) AS is_read
            FROM notifications n ORDER BY created_at DESC
        """, (uid,)).fetchall()
        return jsonify([row_to_dict(r) for r in rows])
    finally:
        conn.close()


@app.post('/api/notifications/<nid>/read')
@require_auth
def mark_read(nid):
    conn = get_db()
    try:
        conn.execute("""
            INSERT OR IGNORE INTO notif_read (user_id, notif_id, read_at)
            VALUES (?, ?, ?)
        """, (session['user_id'], nid, now()))
        conn.commit()
        return jsonify({'ok': True})
    finally:
        conn.close()


@app.post('/api/notifications/read-all')
@require_auth
def mark_all_read():
    conn = get_db()
    try:
        ids = [r['id'] for r in conn.execute('SELECT id FROM notifications')]
        for nid in ids:
            conn.execute("""
                INSERT OR IGNORE INTO notif_read (user_id, notif_id, read_at)
                VALUES (?, ?, ?)
            """, (session['user_id'], nid, now()))
        conn.commit()
        return jsonify({'ok': True, 'marked': len(ids)})
    finally:
        conn.close()


# ── Subscription ──────────────────────────────────────────────

@app.post('/api/subscribe')
@require_auth
def subscribe():
    data  = request.get_json(silent=True) or {}
    plan  = data.get('plan', 'pro')
    if plan not in ('free', 'pro'):
        return jerr('invalid plan')
    conn = get_db()
    try:
        quota = 999 if plan == 'pro' else 10
        conn.execute('UPDATE users SET plan = ?, ai_quota = ? WHERE id = ?',
                     (plan, quota, session['user_id']))
        conn.commit()
        return jsonify(_fresh_user(conn, session['user_id']))
    finally:
        conn.close()


# ── Stats ─────────────────────────────────────────────────────

@app.get('/api/me/stats')
@require_auth
def my_stats():
    conn = get_db()
    try:
        uid = session['user_id']
        read      = conn.execute('SELECT COUNT(*) c FROM read_history WHERE user_id=?', (uid,)).fetchone()['c']
        saved     = conn.execute('SELECT COUNT(*) c FROM bookmarks    WHERE user_id=?', (uid,)).fetchone()['c']
        asks      = conn.execute('SELECT COUNT(*) c FROM ai_log       WHERE user_id=?', (uid,)).fetchone()['c']
        commented = conn.execute('SELECT COUNT(*) c FROM comments     WHERE user_id=?', (uid,)).fetchone()['c']
        unread    = conn.execute("""
            SELECT COUNT(*) FROM notifications
            WHERE id NOT IN (SELECT notif_id FROM notif_read WHERE user_id=?)
        """, (uid,)).fetchone()[0]
        total_arts = conn.execute('SELECT COUNT(*) FROM articles').fetchone()[0]
        return jsonify({'read': read, 'saved': saved, 'ai_asks': asks,
                        'contributed': commented, 'unread_notifs': unread,
                        'total_articles': total_arts})
    finally:
        conn.close()


# ── Local area news ───────────────────────────────────────────

@app.get('/api/local-news')
def local_news():
    address = request.args.get('q', '').strip()
    if not address or len(address) > 200:
        return jerr('address required (under 200 chars)')

    conn = get_db()
    try:
        # Word-based search for all address words
        words = [w.strip() for w in address.split() if len(w.strip()) > 1][:5]
        sql = 'SELECT * FROM articles WHERE 1=1'
        params = []
        if words:
            word_clauses = []
            for word in words:
                like = f'%{word}%'
                word_clauses.append(
                    "(title LIKE ? OR dek LIKE ? OR why_matters LIKE ? OR key_points LIKE ?)"
                )
                params += [like, like, like, like]
            sql += ' AND (' + ' OR '.join(word_clauses) + ')'
        sql += ' ORDER BY published_at DESC LIMIT 20'
        rows = conn.execute(sql, params).fetchall()
        articles = [article_to_dict(r) for r in rows]

        # AI Nepali summary for this area
        ai_summary = None
        try:
            ai_summary = ai_module.local_area_summary(address, articles[:6])
        except Exception as e:
            print(f'[local-news] AI summary failed: {e}')

        return jsonify({
            'location': address,
            'articles': articles,
            'ai_summary': ai_summary,
            'total': len(articles),
        })
    finally:
        conn.close()


# ── Sources list ──────────────────────────────────────────────

@app.get('/api/sources')
def list_sources():
    return jsonify([{
        'id':         s['id'],
        'name':       s['name'],
        'url':        s['url'],
        'bias':       s['bias'],
        'bias_label': s['bias_label'],
        'color':      s['color'],
        'lang':       s.get('lang', 'np'),
    } for s in scraper_module.SOURCES])


# ── Frontend ──────────────────────────────────────────────────

@app.get('/')
def index():
    return send_from_directory(STATIC_DIR, 'index.html')


@app.errorhandler(404)
def not_found(e):
    if request.path.startswith('/api/'):
        return jerr('not found', 404)
    return send_from_directory(STATIC_DIR, 'index.html')


# ── Bootstrap ─────────────────────────────────────────────────

def bootstrap():
    init_db()
    inserted = seed_articles()
    if inserted:
        print(f'[seed] Inserted {len(SEED_ARTICLES)} seed articles.')
    else:
        print('[seed] Database already populated.')
    # Start background scraper
    scraper_module.start_scheduler()
    print('[boot] Scraper scheduler started.')


# Bootstrap runs both under gunicorn and direct python
bootstrap()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '0.0.0.0' if os.environ.get('RAILWAY_ENVIRONMENT') else '127.0.0.1')
    print(f'\n  samachar.ai  ->  http://{host}:{port}\n')
    app.run(host=host, port=port, debug=False, threaded=True)
