# samachar.ai

A fully functional Nepal news app — Python Flask REST API + SQLite + a React frontend served from the same Flask process.

```
samachar ai/
├── backend/
│   ├── server.py         Flask app, all REST endpoints
│   ├── db.py             SQLite schema + helpers
│   ├── ai.py             AI chat engine (rule-based, optional LLM)
│   ├── seed.py           Article + comment + trend seed data
│   ├── requirements.txt
│   └── samachar.db       SQLite database (created on first run)
├── static/
│   ├── index.html        Frontend shell
│   ├── style.css         Editorial-press theme
│   ├── api.js            Vanilla JS API client
│   ├── icons.js          Lucide-style SVG icons
│   ├── components.js     UI primitives + iOS frame + AppCtx
│   ├── screens.js        All screens (login, home, article, etc.)
│   └── app.js            Root component + router + auth gate
├── run.bat               Windows one-click runner
├── run.sh                macOS / Linux runner
└── README.md
```

## Quick start

### Windows

Double-click `run.bat`, or in a terminal:

```bat
run.bat
```

### macOS / Linux

```bash
chmod +x run.sh
./run.sh
```

### Manual setup (any OS)

```bash
cd backend
python -m venv venv
# Windows:  venv\Scripts\activate
# Unix:     source venv/bin/activate
pip install -r requirements.txt
python server.py
```

Then open <http://localhost:5000>

On first launch you'll be asked for a name + ward; that creates an account. All your bookmarks, comments, AI history and preferences are persisted server-side in SQLite (`backend/samachar.db`).

## What works

| Area | Feature |
| --- | --- |
| **Auth** | Name-based session (demo). Cookie-backed. Sign out from Profile. |
| **Onboarding** | Topic selection + language preference. Persisted per user. |
| **Feed** | 15 seed articles. Filterable by tag (Politics / Hyperlocal / Business / Tech / Agri / Nepal). For-you composite view. |
| **Article** | Full body, AI brief, why-it-matters, bias meter, source attribution, fact-check panel, related stories. |
| **Comments** | Post comments (saved to DB), upvote/downvote (saved per-user, no double votes). |
| **Bookmarks** | Toggle from any card or article. Dedicated Saved screen. |
| **Search** | Full-text across title / dek / body / key points. Debounced. |
| **AI chat** | 10 free questions/day, unlimited on Pro. Rule-based Nepal-specific responses; optional OpenAI integration via `SAMACHAR_OPENAI_KEY` env var. Chat history saved per user. |
| **Notifications** | 5 seed notifications. Mark individual / all read. Unread badge on tab bar. |
| **Premium** | Toggle plan, real subscription state stored in DB. Pro unlocks unlimited AI. |
| **Profile** | Live stats from server (reads, saves, AI asks). |
| **Settings** | Theme (light/dark), accent, density, language, ward — all persisted to user record. |
| **Bilingual** | EN ↔ नेपाली headline swap for translated articles. |
| **Daily quota reset** | AI quota refills at midnight server time. |

## REST API reference

All endpoints expect/return JSON. Cookies must be sent with every request (`credentials: 'include'`).

### Auth
- `POST /api/auth/login` — `{name, ward}` → creates user if new, sets session cookie
- `POST /api/auth/logout`
- `GET /api/auth/me` — returns current user or null

### Preferences
- `PUT /api/prefs` — update any subset of `{theme, language, accent, density, ward, show_frame, onboarded}`
- `PUT /api/topics` — `{topics: [t1,t3]}`

### Catalog
- `GET /api/topics`
- `GET /api/districts`
- `GET /api/trends`

### Articles
- `GET /api/articles?tag=tech&q=budget&limit=50`
- `GET /api/articles/:id` — also tracks read history; includes 3 related

### Bookmarks
- `GET /api/bookmarks`
- `POST /api/bookmarks/:id/toggle` → `{saved: bool}`

### Comments
- `GET /api/articles/:id/comments`
- `POST /api/articles/:id/comments` — `{text}`
- `POST /api/comments/:id/vote` — `{vote: 1 | -1 | 0}`

### AI
- `POST /api/ai/ask` — `{question}`; respects quota; returns `{answer, sources, remaining_quota}`
- `GET /api/ai/history`

### Notifications
- `GET /api/notifications` — `is_read` per current user
- `POST /api/notifications/:id/read`
- `POST /api/notifications/read-all`

### Billing
- `POST /api/subscribe` — `{plan: 'free' | 'pro'}`

### Stats
- `GET /api/me/stats`

## Plug in a real LLM

```bash
export SAMACHAR_OPENAI_KEY=sk-...
export SAMACHAR_OPENAI_MODEL=gpt-4o-mini   # optional
python server.py
```

The `/api/ai/ask` endpoint will route through OpenAI-compatible chat completions and gracefully fall back to the rule engine on failure.

## Database

SQLite file at `backend/samachar.db`. Inspect with:

```bash
sqlite3 backend/samachar.db ".tables"
sqlite3 backend/samachar.db "SELECT * FROM articles LIMIT 3;"
```

Wipe the DB:

```bash
rm backend/samachar.db && python backend/server.py
```

## Tech

- **Backend** — Python 3.9+ · Flask 3 · SQLite (stdlib)
- **Frontend** — React 18 + Babel standalone (no build step) · vanilla `fetch`
- **Design** — Editorial-press: Source Serif 4 + Manrope + JetBrains Mono + Noto Serif Devanagari · light/dark themes · iOS 26 device frame

## Production deployment notes

- Replace name-only auth with proper OAuth / magic-link
- Move sessions to Redis (currently signed cookies)
- Run behind gunicorn: `gunicorn -w 4 -b 0.0.0.0:5000 server:app`
- Front with nginx for static files
- Set `SAMACHAR_SECRET=` env var to a stable key
