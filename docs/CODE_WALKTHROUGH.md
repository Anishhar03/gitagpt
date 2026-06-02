# Code Walkthrough

This file explains the major sections of `app.py` and why they exist. It is written for a developer who wants to modify the project confidently.

## 1. Constants

```python
APP_DIR = Path(__file__).resolve().parent
PDF_PATH = APP_DIR / "gita_book.pdf"
BACKGROUND_PATH = APP_DIR / "krishna_ji.jpeg"
```

Meaning:

- Important files are resolved relative to `app.py`.
- This avoids path bugs when Streamlit is launched from another directory.
- The PDF is the knowledge source and the image powers the visual background.

## 2. Configuration Loading

```python
load_local_env(APP_DIR / ".env")
GOOGLE_API_KEY = get_secret("GOOGLE_API_KEY")
CHAT_MODEL = get_secret("GITA_GPT_MODEL", DEFAULT_MODEL)
ENGINE = get_secret("GITA_GPT_ENGINE", DEFAULT_ENGINE).lower()
```

Meaning:

- `load_local_env()` loads simple local `.env` values without another package.
- `get_secret()` checks Streamlit Secrets first, then environment variables.
- `GITA_GPT_ENGINE=local` works without a Google key.
- `GITA_GPT_ENGINE=auto` tries Gemini when a key is present and falls back locally.
- `GITA_GPT_ENGINE=gemini` requires a valid Google key.
- `GITA_GPT_MODEL` defaults to `gemini-2.5-flash`.

## 3. Streamlit Page Setup

```python
st.set_page_config(...)
```

Meaning:

- Sets the browser tab title.
- Uses a wide layout for the landing page and chat surface.
- Opens the sidebar so runtime status and controls are visible.

## 4. Theme and Hero UI

```python
apply_theme()
render_hero()
```

Meaning:

- `apply_theme()` injects CSS for the background, panels, buttons, and responsive layout.
- `image_to_base64()` embeds `krishna_ji.jpeg` as a CSS background.
- `render_hero()` shows the app identity and value immediately.

## 5. Configuration Gate

```python
require_configuration()
```

Meaning:

- The app stops early if `gita_book.pdf` is missing.
- It only requires `GOOGLE_API_KEY` when `GITA_GPT_ENGINE=gemini`.
- This keeps the default local mode runnable without external services.

## 6. PDF Loading and Chunking

```python
@st.cache_resource(show_spinner=False)
def load_corpus(pdf_mtime, chunk_size, chunk_overlap):
```

Meaning:

- `PyPDFLoader` extracts text from `gita_book.pdf`.
- `RecursiveCharacterTextSplitter` creates overlapping chunks.
- `pdf_mtime` makes Streamlit rebuild the cache when the PDF changes.
- Chunks keep metadata such as page number and chunk index.

## 7. Local Retrieval Index

```python
def tokenize(text: str) -> list[str]:
@st.cache_resource(show_spinner=False)
def load_local_index(...):
```

Meaning:

- `tokenize()` normalizes words and removes common stopwords.
- `load_local_index()` builds a TF-IDF style index from the PDF chunks.
- This index is local, free, fast, and does not need Google APIs.
- The app can retrieve relevant passages even when a key is missing, suspended, or over quota.

## 8. Runtime Resources

```python
def load_runtime_resources() -> RuntimeResources:
```

Meaning:

- Always prepares the local retrieval index.
- In `local` mode, the app answers with the local answer builder.
- In `auto` mode, the app uses Gemini if a key is configured and falls back locally if Gemini fails.
- In `gemini` mode, Gemini errors are shown as setup errors.

## 9. Retrieval

```python
docs = local_similarity_search(resources.local_index, question, top_k)
```

Meaning:

- The question is converted into weighted terms.
- Each PDF chunk receives a cosine-similarity score.
- The highest-scoring chunks become the source context for the answer.

## 10. Prompt Construction

```python
prompt = build_prompt(name=name, age=age, question=question, context=context)
```

Meaning:

- The prompt includes seeker context, retrieved passages, and response rules.
- It tells Gemini to ground answers in the provided Gita passages.
- It asks for a direct answer, reflection, and practical action.
- It instructs the model not to invent verse numbers.

## 11. Local Answer Builder

```python
def build_local_answer(name, age, question, docs):
```

Meaning:

- Creates a structured answer when Gemini is disabled or unavailable.
- Extracts relevant source sentences from retrieved chunks.
- Keeps the answer grounded in the PDF and preserves the same user workflow.

## 12. Answer Generation

```python
def answer_question(resources, name, age, question, top_k):
```

Meaning:

- Retrieves local source passages first.
- Uses Gemini when the active runtime includes an LLM.
- Falls back to the local answer builder in `auto` mode if Gemini fails.
- Returns answer text, source documents, and an optional runtime notice.

## 13. Session State

```python
st.session_state.messages
st.session_state.last_sources
st.session_state.active_engine
```

Meaning:

- Streamlit reruns the script after interactions.
- Session state keeps profile info, chat history, retrieved sources, and active runtime mode.
- This makes the chat feel continuous.

## 14. Transcript Generation

```python
build_transcript_pdf(name, messages)
```

Meaning:

- Creates a small PDF in memory using a built-in PDF writer.
- Adds each user and assistant message.
- Returns bytes for `st.download_button()`.
- The transcript is downloaded by the browser and is not stored on the server.

## 15. Main Entrypoint

```python
if __name__ == "__main__":
    main()
```

Meaning:

- Applies the theme and validates configuration.
- Shows the profile form before loading answer resources.
- Loads runtime resources after the user starts a chat session.
- Renders either the local or Gemini-backed chat experience.
