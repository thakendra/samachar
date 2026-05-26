FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    libxml2-dev libxslt-dev libffi-dev gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN python -c "import nltk; nltk.download('punkt', quiet=True); nltk.download('punkt_tab', quiet=True); nltk.download('stopwords', quiet=True)"

COPY backend/ ./backend/
COPY static/ ./static/

EXPOSE 8080
ENV PORT=8080

CMD ["gunicorn", "--chdir", "backend", "--worker-class", "gthread", "--threads", "4", "--workers", "1", "--bind", "0.0.0.0:8080", "--timeout", "120", "server:app"]
