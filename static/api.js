// API client — all calls go to /api on same origin.

const API = (() => {
  const base = '/api';

  async function request(path, opts = {}) {
    const init = {
      credentials: 'include',
      headers: { 'Content-Type': 'application/json', ...(opts.headers || {}) },
      ...opts,
    };
    if (opts.body && typeof opts.body !== 'string') init.body = JSON.stringify(opts.body);
    const res  = await fetch(base + path, init);
    const text = await res.text();
    let body   = null;
    try { body = text ? JSON.parse(text) : null; } catch { body = text; }
    if (!res.ok) {
      const err  = new Error((body && body.error) || `HTTP ${res.status}`);
      err.status = res.status; err.body = body; throw err;
    }
    return body;
  }

  return {
    // auth
    me:         ()        => request('/auth/me'),
    login:      (d)       => request('/auth/login',  { method: 'POST', body: d }),
    signup:     (d)       => request('/auth/signup', { method: 'POST', body: d }),
    logout:     ()        => request('/auth/logout', { method: 'POST' }),

    // prefs
    updatePrefs:  (p)     => request('/prefs',  { method: 'PUT', body: p }),
    updateTopics: (t)     => request('/topics', { method: 'PUT', body: { topics: t } }),

    // catalog
    topics:    ()         => request('/topics'),
    trends:    ()         => request('/trends'),
    sources:   ()         => request('/sources'),

    // articles — p can include: tag, q, topic, limit
    articles:  (p = {})   => {
      const qs = new URLSearchParams(p).toString();
      return request('/articles' + (qs ? '?' + qs : ''));
    },
    article:   (id)       => request('/articles/' + id),

    // internet-wide Nepali news search (PRO) — q can be romanized Nepali
    searchWeb: (q)        => request('/search/web?q=' + encodeURIComponent(q)),

    // local area news
    localNews: (address)  => request('/local-news?q=' + encodeURIComponent(address)),

    // bookmarks
    bookmarks:      ()    => request('/bookmarks'),
    toggleBookmark: (id)  => request('/bookmarks/' + id + '/toggle', { method: 'POST' }),

    // comments
    comments:    (aid)        => request('/articles/' + aid + '/comments'),
    postComment: (aid, text)  => request('/articles/' + aid + '/comments',
                                          { method: 'POST', body: { text } }),
    voteComment: (cid, vote)  => request('/comments/' + cid + '/vote',
                                          { method: 'POST', body: { vote } }),

    // AI
    askAi:     (q, lang)  => request('/ai/ask', { method: 'POST', body: { question: q, lang } }),
    aiHistory: ()         => request('/ai/history'),

    // notifications
    notifications: ()     => request('/notifications'),
    markRead:  (nid)      => request('/notifications/' + nid + '/read', { method: 'POST' }),
    markAllRead: ()       => request('/notifications/read-all', { method: 'POST' }),

    // subscription
    subscribe: (plan)     => request('/subscribe', { method: 'POST', body: { plan } }),

    // stats
    stats:     ()         => request('/me/stats'),

    // news scanner (was: scraper)
    scanStatus:   ()      => request('/scrape/status'),
    triggerScan:  ()      => request('/scrape/trigger', { method: 'POST' }),

    // SSE live feed — returns EventSource
    liveFeed: (onArticle, onScan) => {
      const es = new EventSource('/api/feed/live');
      es.addEventListener('new_article', e => onArticle && onArticle(JSON.parse(e.data)));
      es.addEventListener('scrape_done', e => onScan    && onScan(JSON.parse(e.data)));
      es.addEventListener('ping', () => {});
      return es;
    },
  };
})();

window.API = API;
