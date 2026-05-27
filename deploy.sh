#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# samachar.ai — VPS deployment script (Ubuntu 24.04)
# Usage (run as root on VPS):
#   curl -fsSL https://raw.githubusercontent.com/thakendra/samachar/master/deploy.sh | bash
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail

APP_DIR="/opt/samachar"
REPO="https://github.com/thakendra/samachar.git"
DOMAIN=""          # set to your domain/IP if you want nginx

echo "═══════════════════════════════════════════════"
echo "  samachar.ai  —  VPS Setup"
echo "═══════════════════════════════════════════════"

# ── 1. System deps ────────────────────────────────────────────────────────────
apt-get update -qq
apt-get install -y -qq git python3 python3-pip python3-venv \
    libxml2-dev libxslt-dev libffi-dev gcc nginx certbot python3-certbot-nginx

# ── 2. Clone / update repo ───────────────────────────────────────────────────
if [ -d "$APP_DIR/.git" ]; then
    echo "[git] Pulling latest..."
    git -C "$APP_DIR" pull --ff-only
else
    echo "[git] Cloning..."
    git clone "$REPO" "$APP_DIR"
fi

# ── 3. Python venv + deps ────────────────────────────────────────────────────
cd "$APP_DIR"
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip -q
pip install -r backend/requirements.txt -q

# Download NLTK data
python3 -c "
import nltk, ssl
try: _create_unverified_https_context = ssl._create_unverified_context
except AttributeError: pass
else: ssl._create_default_https_context = _create_unverified_https_context
nltk.download('punkt', quiet=True)
nltk.download('punkt_tab', quiet=True)
nltk.download('stopwords', quiet=True)
"
echo "[nltk] Data downloaded."

# ── 4. Environment file ──────────────────────────────────────────────────────
ENV_FILE="$APP_DIR/.env"
if [ ! -f "$ENV_FILE" ]; then
    SAMACHAR_SECRET=$(python3 -c "import secrets; print(secrets.token_hex(32))")
    cat > "$ENV_FILE" <<EOF
GEMINI_API_KEY=AIzaSyBcqNqnwS8-lRg203CWMd71diAyUL2_bbU
SAMACHAR_SECRET=$SAMACHAR_SECRET
PORT=8000
EOF
    echo "[env] Created $ENV_FILE"
else
    echo "[env] $ENV_FILE already exists — skipping."
fi

# ── 5. Systemd service ───────────────────────────────────────────────────────
cat > /etc/systemd/system/samachar.service <<'UNIT'
[Unit]
Description=samachar.ai Flask app
After=network.target

[Service]
User=root
WorkingDirectory=/opt/samachar
EnvironmentFile=/opt/samachar/.env
ExecStart=/opt/samachar/venv/bin/gunicorn \
    --chdir backend \
    --worker-class gthread \
    --threads 4 \
    --workers 2 \
    --bind 0.0.0.0:8000 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    server:app
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
UNIT

systemctl daemon-reload
systemctl enable samachar
systemctl restart samachar
sleep 3
systemctl status samachar --no-pager | head -20

# ── 6. Nginx reverse proxy ───────────────────────────────────────────────────
cat > /etc/nginx/sites-available/samachar <<'NGINX'
server {
    listen 80 default_server;
    listen [::]:80 default_server;

    client_max_body_size 10M;
    proxy_read_timeout 120s;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        # SSE support
        proxy_buffering off;
        proxy_cache off;
    }
}
NGINX

ln -sf /etc/nginx/sites-available/samachar /etc/nginx/sites-enabled/samachar
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl reload nginx

echo ""
echo "═══════════════════════════════════════════════"
echo "  ✅  samachar.ai is LIVE!"
echo "  URL: http://$(curl -s ifconfig.me)"
echo "  Logs: journalctl -u samachar -f"
echo "  Restart: systemctl restart samachar"
echo "═══════════════════════════════════════════════"
