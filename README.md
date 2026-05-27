# Gita GPT

Gita GPT is an end-to-end Streamlit application that answers reflective questions with Retrieval-Augmented Generation over the Bhagavad Gita. It retrieves relevant passages from `gita_book.pdf`, answers locally by default, can use Gemini when a valid key is enabled, and returns source passages plus a downloadable chat transcript.

![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-App-FF4B4B?logo=streamlit&logoColor=white)
![LangChain](https://img.shields.io/badge/LangChain-RAG-1C3C3C)
![Local RAG](https://img.shields.io/badge/Local-RAG-0F766E)
![Gemini](https://img.shields.io/badge/Gemini-Google%20AI-4285F4?logo=google&logoColor=white)

## What It Does

- Collects seeker context: name, age, and intention.
- Loads the Bhagavad Gita PDF and chunks it into searchable passages.
- Builds a local TF-IDF retrieval index from the PDF.
- Retrieves the most relevant passages for each question.
- Answers locally by default, or sends retrieved context to Gemini when `GITA_GPT_ENGINE=auto` or `gemini`.
- Shows source passages used for the response.
- Exports the conversation as a PDF transcript.
- Runs locally, in Docker, on Streamlit Community Cloud, or on a container host.

## Architecture

```mermaid
flowchart LR
    A["gita_book.pdf"] --> B["PyPDFLoader"]
    B --> C["Recursive text splitter"]
    C --> D["Local TF-IDF index"]
    F["User question"] --> G["Similarity search"]
    D --> G
    G --> H["Prompt with retrieved passages"]
    H --> I{"Engine"}
    I --> M["Local answer builder"]
    I --> N["Gemini chat model"]
    M --> J["Grounded answer + sources"]
    N --> J
    J --> K["Streamlit UI"]
    J --> L["PDF transcript"]
```

## Quick Start

### 1. Clone and enter the project

```bash
git clone https://github.com/Anishhar03/gitagpt.git
cd gitagpt
```

### 2. Create a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Linux/macOS:

```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements.txt
```

### 4. Configure secrets

Copy the example file:

```bash
cp .env.example .env
```

The app works locally without a Google key:

```bash
GITA_GPT_ENGINE=local
```

To enable Gemini with a valid key:

```bash
GITA_GPT_ENGINE=auto
GOOGLE_API_KEY=your_google_gemini_api_key_here
```

Never commit `.env`.

### 5. Run the app

```bash
streamlit run app.py
```

Open:

```text
http://localhost:8501
```

## Environment Variables

| Variable | Required | Default | Meaning |
|---|---:|---|---|
| `GITA_GPT_ENGINE` | No | `local` | `local` works offline, `auto` tries Gemini then falls back, `gemini` requires Google. |
| `GOOGLE_API_KEY` | Only for Gemini | none | Google Generative Language API key used by Gemini answer synthesis. |
| `GITA_GPT_MODEL` | No | `gemini-1.5-flash` | Chat model used for answer generation. |
| `GITA_GPT_CHUNK_SIZE` | No | `1000` | Character target for each PDF chunk. |
| `GITA_GPT_CHUNK_OVERLAP` | No | `150` | Character overlap between chunks to preserve context. |
| `GITA_GPT_TOP_K` | No | `4` | Number of retrieved passages used for each answer. |

## Deployment

### Streamlit Community Cloud

1. Push this repo to GitHub.
2. Open Streamlit Community Cloud.
3. Create a new app from the GitHub repo.
4. Main file: `app.py`.
5. Optional: add `GITA_GPT_ENGINE="auto"` and `GOOGLE_API_KEY` in Streamlit Secrets for Gemini.
6. Deploy.

### Docker

```bash
docker build -t gita-gpt .
docker run --rm -p 8501:8501 gita-gpt
```

Then open:

```text
http://localhost:8501
```

Full deployment notes are in [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md).

## Documentation

- [docs/WORKFLOWS.md](docs/WORKFLOWS.md): user, RAG, transcript, and deployment workflows.
- [docs/CODE_WALKTHROUGH.md](docs/CODE_WALKTHROUGH.md): meaning of each major block in `app.py`.
- [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md): local, Streamlit Cloud, Docker, and troubleshooting guide.

## Project Structure

```text
.
|-- app.py
|-- gita_book.pdf
|-- krishna_ji.jpeg
|-- requirements.txt
|-- .env.example
|-- .streamlit/config.toml
|-- Dockerfile
|-- runtime.txt
|-- docs/
|   |-- CODE_WALKTHROUGH.md
|   |-- DEPLOYMENT.md
|   `-- WORKFLOWS.md
`-- scripts/
    |-- smoke_local_answer.py
    `-- verify_project.py
```

## Validation

Run the lightweight repository check:

```bash
python scripts/verify_project.py
python scripts/smoke_local_answer.py
```

Run the app:

```bash
streamlit run app.py
```

Expected behavior:

1. The landing page and profile form load.
2. You enter name, age, and intention.
3. The chat opens and prepares the Gita knowledge base.
4. A question retrieves Gita passages.
5. The local answer builder returns a grounded answer. If Gemini is enabled and healthy, Gemini returns the answer.
6. Retrieved sources are visible.
7. Transcript PDF download works after messages exist.

## Security Notes

- Do not commit `.env` or real API keys.
- The app can run without external AI services in `local` mode.
- If a Google key is exposed publicly, revoke it or restrict it immediately in Google Cloud Console.
- For public deployments, restrict the API key to the Generative Language API and trusted referrers or infrastructure where possible.

## Troubleshooting

| Problem | Fix |
|---|---|
| `GOOGLE_API_KEY` missing | Use `GITA_GPT_ENGINE=local`, or set a valid key and use `auto` or `gemini`. |
| Google connection error | Check API key restrictions, quota, Generative Language API access, and outbound network access. |
| PDF not found | Keep `gita_book.pdf` in the project root. |
| Background missing | Keep `krishna_ji.jpeg` in the project root. |
| Gemini quota error | Check Google API key, billing/quota, and Generative Language API access. |
| Slow first answer | The first run reads and chunks the PDF; later reruns use Streamlit's cache. |

## License

No license has been selected yet. Add one before accepting external contributions.
