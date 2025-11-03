# LexChunk Backend (FastAPI + spaCy + Textacy)

A minimal backend that extracts **lexical chunks** (noun phrases + verb/multiword expressions) and returns JSON.

## 0) Local quick start

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn app:app --reload --port 8000
# visit http://127.0.0.1:8000/health
```

> The model `en_core_web_sm` will be auto-downloaded on first run if missing.

## 1) Deploy on Render (recommended)

1. Create a new GitHub repo and push these files: `app.py`, `requirements.txt`, `Procfile`, `README.md`.
2. Go to https://render.com → New → Web Service → connect your repo.
3. Environment: **Python**. Build command: `pip install -r requirements.txt`
4. Start command: `uvicorn app:app --host 0.0.0.0 --port $PORT`
5. Click **Deploy**. After it turns green, your public API URL will be something like:
   ```
   https://<your-service>.onrender.com/chunks
   ```
6. In your frontend, set Backend API to that URL.

## 2) Deploy on Hugging Face Spaces (no credit card, simple)

1. Create a new **Space** (SDK = **Docker** or **Gradio/Streamlit** not required here).
2. If using **Docker**, add a `Dockerfile` like below, push to the Space, it builds automatically.
3. Your Space will get a public URL you can call from your frontend.

### Dockerfile

```dockerfile
# Use slim Python
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt \
    && python -c "import spacy,spacy.cli; spacy.cli.download('en_core_web_sm')"

COPY app.py /app/

EXPOSE 7860
CMD uvicorn app:app --host 0.0.0.0 --port 7860
```

> After build finishes, the API will be at `https://<your-space>.hf.space/chunks`.

## 3) Frontend configuration

In your React app (Canvas), set the **backend API** to your deployed URL:
```
https://<your-service>.onrender.com/chunks
# or
https://<your-space>.hf.space/chunks
```

## 4) API

- `GET /health` → `{"ok": true}`
- `POST /chunks` with JSON body: `{"text": "She takes care of her little brother every day."}`

Response:
```json
{
  "collocations": [
    {"type":"verb_chunk","phrase":"takes care of","start":4,"end":17,"sentence":"She takes care of her little brother every day."},
    {"type":"noun_chunk","phrase":"her little brother","start":18,"end":36,"sentence":"She takes care of her little brother every day."},
    {"type":"noun_chunk","phrase":"every day","start":37,"end":46,"sentence":"She takes care of her little brother every day."}
  ]
}
```

## Notes
- For better accuracy, switch to `en_core_web_trf` (transformer model) and install it.
- To restrict CORS in production, set `allow_origins` to your domain only.
