# Code Walkthrough

This file explains the major sections of `app.py` and why they exist. It is written for a developer who wants to modify the project confidently.

## 1. sqlite Compatibility Shim

```python
try:
    __import__("pysqlite3")
    import sys
    sys.modules["sqlite3"] = sys.modules.pop("pysqlite3")
except Exception:
    pass
```

Meaning:

- ChromaDB needs a modern sqlite build.
- Some hosted Linux images ship an older sqlite.
- `pysqlite3-binary` provides a newer sqlite implementation.
- The module swap makes libraries that import `sqlite3` use `pysqlite3` instead.
- The `try/except` keeps local environments working even if `pysqlite3` is unavailable.

## 2. Constants

```python
APP_DIR = Path(__file__).resolve().parent
PDF_PATH = APP_DIR / "gita_book.pdf"
BACKGROUND_PATH = APP_DIR / "krishna_ji.jpeg"
VECTOR_DIR = APP_DIR / "gita_chroma"
```

Meaning:

- All important files are resolved relative to `app.py`.
- This avoids path bugs when Streamlit is launched from a different directory.
- `gita_chroma/` is the runtime vector database cache.

## 3. Configuration Loading

```python
load_local_env(APP_DIR / ".env")
GOOGLE_API_KEY = get_secret("GOOGLE_API_KEY")
CHAT_MODEL = get_secret("GITA_GPT_MODEL", DEFAULT_MODEL)
```

Meaning:

- `load_local_env()` loads simple local `.env` values without an extra dependency.
- `get_secret()` checks Streamlit Secrets first, then environment variables.
- This supports local development and hosted deployment without changing code.
- Real keys stay outside Git.

## 4. Streamlit Page Setup

```python
st.set_page_config(...)
```

Meaning:

- Sets browser tab title.
- Uses wide layout for a modern landing page and chat surface.
- Opens the sidebar so runtime settings and controls are immediately visible.

## 5. Theme and Hero UI

```python
apply_theme()
render_hero()
```

Meaning:

- `apply_theme()` injects CSS for the background, panels, cards, buttons, and responsive layout.
- `image_to_base64()` embeds `krishna_ji.jpeg` as a CSS background.
- `render_hero()` shows the first-viewport brand signal and explains the app in one glance.

## 6. Configuration Gate

```python
require_configuration()
```

Meaning:

- The app stops early if required config is missing.
- It checks for `GOOGLE_API_KEY` and `gita_book.pdf`.
- This gives a clear setup message instead of failing deep inside LangChain.

## 7. Cached LLM Loader

```python
@st.cache_resource(show_spinner=False)
def load_llm(api_key: str, model_name: str) -> ChatGoogleGenerativeAI:
```

Meaning:

- Creates the Gemini chat model once.
- Streamlit reruns the script often; caching prevents repeated object creation.
- The API key is passed at runtime but never written to disk.

## 8. Cached Vector Store Loader

```python
@st.cache_resource(show_spinner=False)
def load_vectorstore(...):
```

Meaning:

- Creates or loads the Chroma vector store.
- If `gita_chroma/` exists, it loads the previous index.
- If not, it reads `gita_book.pdf`, chunks the text, embeds chunks, and persists the index.
- `PDF_PATH.stat().st_mtime` is an argument so the cache invalidates when the PDF changes.
- If an old Chroma cache cannot be loaded, the app removes that generated cache and rebuilds it from the PDF.

## 9. Text Splitting

```python
splitter = RecursiveCharacterTextSplitter(
    chunk_size=chunk_size,
    chunk_overlap=chunk_overlap,
    separators=["\n\n", "\n", ".", " ", ""],
)
```

Meaning:

- The Gita PDF is too large to send as one prompt.
- Chunking creates smaller passages for semantic search.
- Overlap preserves context across chunk boundaries.
- Separator order tries to split on paragraphs first, then smaller boundaries.

## 10. Retrieval

```python
docs = vectorstore.similarity_search(question, k=top_k)
```

Meaning:

- The user's question is embedded.
- Chroma finds the most semantically similar Gita chunks.
- `top_k` controls how many passages are sent to Gemini.

## 11. Prompt Construction

```python
prompt = build_prompt(name=name, age=age, question=question, context=context)
```

Meaning:

- The prompt includes seeker context, retrieved passages, and response rules.
- It tells Gemini to ground answers in the provided Gita passages.
- It asks for a direct answer, reflection, and practical action.
- It instructs the model not to invent verse numbers.

## 12. Answer Generation

```python
response = llm.invoke(prompt)
```

Meaning:

- Gemini receives the grounded prompt.
- The response text is displayed in the chat.
- Retrieved source documents are saved for the source expander.

## 13. Session State

```python
st.session_state.messages
st.session_state.last_sources
```

Meaning:

- Streamlit reruns the script after each interaction.
- Session state keeps profile info, chat history, and the latest retrieved sources.
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

- Keeps app startup explicit.
- `main()` applies the theme, validates config, renders the sidebar and profile form, then loads AI resources only after the user starts a chat session.
