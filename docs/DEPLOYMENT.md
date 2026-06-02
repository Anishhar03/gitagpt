# Deployment Guide

This project is deployment-ready for Streamlit Community Cloud, Docker, and any platform that can run a Python web process. The default `local` engine does not need a Google API key.

## Local Deployment

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements.txt
cp .env.example .env
streamlit run app.py
```

Open:

```text
http://localhost:8501
```

## Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements.txt
Copy-Item .env.example .env
streamlit run app.py
```

## Engines

Local-only mode:

```text
GITA_GPT_ENGINE=local
```

Gemini with automatic local fallback:

```text
GITA_GPT_ENGINE=auto
GOOGLE_API_KEY=your_google_gemini_api_key_here
GITA_GPT_MODEL=gemini-2.5-flash
```

Strict Gemini mode:

```text
GITA_GPT_ENGINE=gemini
GOOGLE_API_KEY=your_google_gemini_api_key_here
GITA_GPT_MODEL=gemini-2.5-flash
```

Use strict Gemini mode only when the key is valid and the host has outbound access to Google APIs.

## Streamlit Community Cloud

1. Push the repository to GitHub.
2. Go to Streamlit Community Cloud.
3. Click **New app**.
4. Choose this repository.
5. Select branch `main`.
6. Set main file path to `app.py`.
7. Deploy with no secrets for local mode.

Optional Gemini secrets:

```toml
GITA_GPT_ENGINE = "auto"
GOOGLE_API_KEY = "your_google_gemini_api_key_here"
GITA_GPT_MODEL = "gemini-2.5-flash"
```

The first run may take longer because the app reads and chunks `gita_book.pdf`.

## Docker

Build:

```bash
docker build -t gita-gpt .
```

Run in local mode:

```bash
docker run --rm -p 8501:8501 gita-gpt
```

Run with Gemini:

```bash
docker run --rm -p 8501:8501 -e GITA_GPT_ENGINE=auto -e GOOGLE_API_KEY=your_key_here -e GITA_GPT_MODEL=gemini-2.5-flash gita-gpt
```

Open:

```text
http://localhost:8501
```

## Generic Container Host

Use these settings:

- Build command: `pip install -r requirements.txt`
- Start command: `streamlit run app.py`
- Port: `8501`
- Required environment variables: none for local mode
- Optional environment variables: `GITA_GPT_ENGINE=auto`, `GOOGLE_API_KEY=...`, `GITA_GPT_MODEL=gemini-2.5-flash`

## Render or Railway

Recommended start command:

```bash
streamlit run app.py --server.port $PORT --server.address 0.0.0.0
```

If the platform does not expose `PORT`, use `8501`.

## Secrets Checklist

- Do not commit `.env`.
- Do not commit `.streamlit/secrets.toml`.
- Restrict any Google API key in Google Cloud Console.
- Rotate the key if it is pasted into chat, logs, screenshots, or commits.

## Troubleshooting

### Google API key missing

Use `GITA_GPT_ENGINE=local`, or set `GOOGLE_API_KEY` in one of:

- `.env`
- shell environment
- Streamlit Secrets
- deployment platform environment variables

### Google key suspended or permission denied

Use local mode immediately:

```text
GITA_GPT_ENGINE=local
```

For Gemini, create or enable a valid key and confirm:

- Generative Language API is enabled.
- The API key is correct.
- The key has not been restricted to a different referrer or service.
- Billing/quota settings allow the request.
- The deployment host allows outbound HTTPS access to Google APIs.

### First query is slow

The first run reads and chunks the PDF. Later reruns use Streamlit's cache.

### App cannot find PDF or image

Keep these files in the repository root:

- `gita_book.pdf`
- `krishna_ji.jpeg`
