# Deployment Guide

This project is deployment-ready for Streamlit Community Cloud, Docker, and any platform that can run a Python web process.

## Local Deployment

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements.txt
cp .env.example .env
```

Edit `.env`:

```bash
GOOGLE_API_KEY=your_google_gemini_api_key_here
```

Run:

```bash
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

Set the key for the current terminal without writing a file:

```powershell
$env:GOOGLE_API_KEY = "your_google_gemini_api_key_here"
streamlit run app.py
```

## Streamlit Community Cloud

1. Push the repository to GitHub.
2. Go to Streamlit Community Cloud.
3. Click **New app**.
4. Choose this repository.
5. Select branch `main`.
6. Set main file path to `app.py`.
7. Open **Advanced settings**.
8. Add this secret:

```toml
GOOGLE_API_KEY = "your_google_gemini_api_key_here"
```

9. Deploy.

The first run may take longer because Chroma creates the vector index from `gita_book.pdf`.

## Docker

Build:

```bash
docker build -t gita-gpt .
```

Run:

```bash
docker run --rm -p 8501:8501 -e GOOGLE_API_KEY=your_google_gemini_api_key_here gita-gpt
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
- Required environment variable: `GOOGLE_API_KEY`

## Render or Railway

Recommended start command:

```bash
streamlit run app.py --server.port $PORT --server.address 0.0.0.0
```

Set environment variable:

```text
GOOGLE_API_KEY=your_google_gemini_api_key_here
```

If the platform does not expose `PORT`, use `8501`.

## Secrets Checklist

- Do not commit `.env`.
- Do not commit `.streamlit/secrets.toml`.
- Restrict the Google API key in Google Cloud Console.
- Rotate the key if it is pasted into chat, logs, screenshots, or commits.

## Troubleshooting

### Google API key missing

Set `GOOGLE_API_KEY` in one of:

- `.env`
- shell environment
- Streamlit Secrets
- deployment platform environment variables

### Chroma sqlite error

Linux deployments install `pysqlite3-binary` from `requirements.txt`, and `app.py` swaps it in before Chroma imports sqlite.

### Chroma cache load error

`gita_chroma/` is generated runtime data. If the local cache was created by an incompatible Chroma version, the app automatically removes it and rebuilds it from `gita_book.pdf`.

### First query is slow

The vector store is created on first run. Later runs load `gita_chroma/`.

### App cannot find PDF or image

Keep these files in the repository root:

- `gita_book.pdf`
- `krishna_ji.jpeg`

### Gemini quota or permission failure

Check:

- Generative Language API is enabled.
- The API key is correct.
- The key has not been restricted to a different referrer or service.
- Billing/quota settings allow the request.
- The deployment host allows outbound HTTPS access to Google APIs.
