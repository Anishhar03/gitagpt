# Optional sqlite compatibility shim for hosted Linux environments where
# ChromaDB needs a newer sqlite build than the system Python provides.
try:
    __import__("pysqlite3")
    import sys

    sys.modules["sqlite3"] = sys.modules.pop("pysqlite3")
except Exception:
    pass

import base64
import os
import re
import shutil
import textwrap
from pathlib import Path
from typing import Iterable

os.environ.setdefault("ANONYMIZED_TELEMETRY", "False")

import streamlit as st
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter


APP_DIR = Path(__file__).resolve().parent
PDF_PATH = APP_DIR / "gita_book.pdf"
BACKGROUND_PATH = APP_DIR / "krishna_ji.jpeg"
VECTOR_DIR = APP_DIR / "gita_chroma"
COLLECTION_NAME = "gita_gpt"

DEFAULT_MODEL = "gemini-1.5-flash"
DEFAULT_EMBEDDING_MODEL = "models/embedding-001"
DEFAULT_CHUNK_SIZE = 1000
DEFAULT_CHUNK_OVERLAP = 150
DEFAULT_TOP_K = 4


def load_local_env(path: Path) -> None:
    """Load simple KEY=VALUE pairs from .env without requiring extra packages."""
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


load_local_env(APP_DIR / ".env")


def get_secret(name: str, default: str = "") -> str:
    """Read a value from Streamlit secrets first, then environment variables."""
    try:
        value = st.secrets.get(name)
    except Exception:
        value = None
    return str(value or os.getenv(name, default)).strip()


def get_int_setting(name: str, default: int) -> int:
    """Parse integer settings safely so bad env values do not crash startup."""
    raw_value = get_secret(name, str(default))
    try:
        return int(raw_value)
    except ValueError:
        return default


GOOGLE_API_KEY = get_secret("GOOGLE_API_KEY")
CHAT_MODEL = get_secret("GITA_GPT_MODEL", DEFAULT_MODEL)
EMBEDDING_MODEL = get_secret("GITA_GPT_EMBEDDING_MODEL", DEFAULT_EMBEDDING_MODEL)
CHUNK_SIZE = get_int_setting("GITA_GPT_CHUNK_SIZE", DEFAULT_CHUNK_SIZE)
CHUNK_OVERLAP = get_int_setting("GITA_GPT_CHUNK_OVERLAP", DEFAULT_CHUNK_OVERLAP)
TOP_K = get_int_setting("GITA_GPT_TOP_K", DEFAULT_TOP_K)


st.set_page_config(
    page_title="Gita GPT",
    page_icon="Om",
    layout="wide",
    initial_sidebar_state="expanded",
)


def image_to_base64(path: Path) -> str:
    """Convert a local image into a base64 data URL payload for CSS backgrounds."""
    if not path.exists():
        return ""
    return base64.b64encode(path.read_bytes()).decode("utf-8")


def apply_theme() -> None:
    """Inject the visual system for the Streamlit app."""
    background_b64 = image_to_base64(BACKGROUND_PATH)
    background_css = (
        f'linear-gradient(rgba(11, 18, 32, 0.78), rgba(11, 18, 32, 0.9)), '
        f'url("data:image/jpeg;base64,{background_b64}") center/cover fixed'
        if background_b64
        else "linear-gradient(135deg, #0f172a 0%, #312e81 52%, #14532d 100%)"
    )

    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

        .stApp {{
            background: {background_css};
            color: #f8fafc;
            font-family: 'Inter', sans-serif;
        }}

        [data-testid="stSidebar"] {{
            background: rgba(15, 23, 42, 0.92);
            border-right: 1px solid rgba(148, 163, 184, 0.25);
        }}

        .block-container {{
            padding-top: 2rem;
            padding-bottom: 3rem;
            max-width: 1180px;
        }}

        .hero {{
            padding: 2rem 0 1rem;
        }}

        .eyebrow {{
            color: #fde68a;
            font-weight: 700;
            letter-spacing: 0.16em;
            text-transform: uppercase;
            font-size: 0.8rem;
        }}

        .hero h1 {{
            font-size: clamp(2.4rem, 6vw, 5rem);
            line-height: 0.95;
            margin: 0.2rem 0 1rem;
            color: #ffffff;
        }}

        .hero p {{
            max-width: 760px;
            color: #dbeafe;
            font-size: 1.1rem;
            line-height: 1.7;
        }}

        .metric-grid {{
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 1rem;
            margin: 1rem 0 1.5rem;
        }}

        .metric {{
            border: 1px solid rgba(226, 232, 240, 0.18);
            background: rgba(15, 23, 42, 0.72);
            border-radius: 10px;
            padding: 1rem;
        }}

        .metric strong {{
            display: block;
            color: #fde68a;
            font-size: 1.4rem;
        }}

        .metric span {{
            color: #cbd5e1;
            font-size: 0.92rem;
        }}

        .section-panel {{
            border: 1px solid rgba(226, 232, 240, 0.18);
            background: rgba(15, 23, 42, 0.78);
            border-radius: 10px;
            padding: 1.2rem;
            margin: 1rem 0;
        }}

        .source-box {{
            border-left: 3px solid #38bdf8;
            background: rgba(8, 47, 73, 0.55);
            padding: 0.9rem 1rem;
            margin: 0.75rem 0;
            border-radius: 8px;
            color: #e0f2fe;
        }}

        .stChatMessage {{
            background: rgba(15, 23, 42, 0.76);
            border: 1px solid rgba(226, 232, 240, 0.12);
            border-radius: 10px;
        }}

        .stButton > button,
        .stDownloadButton > button,
        [data-testid="stFormSubmitButton"] button {{
            border-radius: 8px;
            border: 1px solid rgba(253, 230, 138, 0.5);
            background: linear-gradient(135deg, #f59e0b, #eab308);
            color: #111827;
            font-weight: 800;
        }}

        .stTextInput input,
        .stTextArea textarea,
        .stNumberInput input {{
            background: rgba(15, 23, 42, 0.88);
            color: #f8fafc;
            border-radius: 8px;
        }}

        @media (max-width: 800px) {{
            .metric-grid {{
                grid-template-columns: 1fr;
            }}
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_hero() -> None:
    """Render the first screen users see."""
    st.markdown(
        """
        <div class="hero">
            <div class="eyebrow">Bhagavad Gita RAG Companion</div>
            <h1>Gita GPT</h1>
            <p>
                Ask reflective questions and receive guidance grounded in retrieved
                passages from the Bhagavad Gita. The app combines Gemini, local
                Chroma retrieval, and a calm Streamlit interface for an end-to-end
                spiritual Q&A experience.
            </p>
        </div>
        <div class="metric-grid">
            <div class="metric"><strong>RAG</strong><span>Answers are grounded in the PDF corpus.</span></div>
            <div class="metric"><strong>Gemini</strong><span>Google Generative AI powers response synthesis.</span></div>
            <div class="metric"><strong>PDF</strong><span>Download your conversation as a transcript.</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def require_configuration() -> None:
    """Stop early with useful setup instructions if required assets are missing."""
    missing_items = []
    if not GOOGLE_API_KEY:
        missing_items.append("GOOGLE_API_KEY")
    if not PDF_PATH.exists():
        missing_items.append("gita_book.pdf")

    if not missing_items:
        return

    st.error("Gita GPT needs a little setup before it can run.")
    st.write("Missing: " + ", ".join(missing_items))
    st.code(
        "GOOGLE_API_KEY=your_google_gemini_api_key_here\n"
        "streamlit run app.py",
        language="bash",
    )
    st.stop()


@st.cache_resource(show_spinner=False)
def load_llm(api_key: str, model_name: str) -> ChatGoogleGenerativeAI:
    """Create the Gemini chat model once per app process."""
    return ChatGoogleGenerativeAI(
        model=model_name,
        google_api_key=api_key,
        temperature=0.55,
    )


def build_vectorstore(
    embedding_model: str,
    embeddings,
    chunk_size: int,
    chunk_overlap: int,
) -> Chroma:
    """Create a fresh Chroma vector store from the bundled Gita PDF."""
    loader = PyPDFLoader(str(PDF_PATH))
    pages = loader.load()
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ".", " ", ""],
    )
    chunks = splitter.split_documents(pages)
    if not chunks:
        raise RuntimeError("No text chunks were created from gita_book.pdf.")

    for index, chunk in enumerate(chunks):
        chunk.metadata["chunk_index"] = index
        chunk.metadata["source"] = "Bhagavad Gita"
        chunk.metadata["embedding_model"] = embedding_model

    return Chroma.from_documents(
        chunks,
        embedding=embeddings,
        persist_directory=str(VECTOR_DIR),
        collection_name=COLLECTION_NAME,
    )


def clear_chroma_client_cache() -> None:
    """Clear Chroma's in-process client cache before rebuilding generated data."""
    try:
        from chromadb.api.shared_system_client import SharedSystemClient

        SharedSystemClient.clear_system_cache()
    except Exception:
        pass


def remove_vector_cache() -> None:
    """Remove the generated vector cache so it can be rebuilt from the PDF."""
    clear_chroma_client_cache()
    shutil.rmtree(VECTOR_DIR, ignore_errors=True)
    clear_chroma_client_cache()


@st.cache_resource(show_spinner=False)
def load_vectorstore(
    api_key: str,
    embedding_model: str,
    pdf_mtime: float,
    chunk_size: int,
    chunk_overlap: int,
) -> Chroma:
    """Load or build the persistent Chroma vector store from the Gita PDF."""
    embeddings = GoogleGenerativeAIEmbeddings(
        model=embedding_model,
        google_api_key=api_key,
    )

    if VECTOR_DIR.exists() and any(VECTOR_DIR.iterdir()):
        try:
            vectorstore = Chroma(
                persist_directory=str(VECTOR_DIR),
                embedding_function=embeddings,
                collection_name=COLLECTION_NAME,
            )
            if vectorstore._collection.count() <= 0:
                raise RuntimeError("Existing vector cache is empty.")
            return vectorstore
        except Exception:
            remove_vector_cache()

    return build_vectorstore(embedding_model, embeddings, chunk_size, chunk_overlap)


def normalize_text(text: str) -> str:
    """Collapse excess whitespace for cleaner prompts and source previews."""
    return re.sub(r"\s+", " ", text).strip()


def redact_sensitive_text(text: str) -> str:
    """Remove accidental secrets from provider errors before rendering them."""
    secret_patterns = [
        r"AIza[0-9A-Za-z_-]+",
        r"ghp_[0-9A-Za-z_]+",
        r"github_pat_[0-9A-Za-z_]+",
    ]
    redacted = text
    for pattern in secret_patterns:
        redacted = re.sub(pattern, "[redacted-secret]", redacted)
    return redacted


def friendly_error_message(error: Exception) -> str:
    """Convert provider exceptions into concise, safe setup guidance."""
    message = redact_sensitive_text(str(error))
    if "CONSUMER_SUSPENDED" in message or "has been suspended" in message:
        return (
            "Google rejected the configured API key because the associated "
            "consumer is suspended. Create or enable a valid Gemini API key, "
            "set it as GOOGLE_API_KEY, and restart the app."
        )
    if "403" in message and "Permission denied" in message:
        return (
            "Google returned a permission error. Check that the Generative "
            "Language API is enabled, the key is valid, and any key "
            "restrictions allow this deployment."
        )
    if "Timeout" in message or "failed to connect" in message:
        return (
            "The app could not reach Google APIs before the request timed out. "
            "Check outbound network access from this machine or host."
        )
    return message


def format_sources(docs: Iterable) -> str:
    """Create compact source context for the Gemini prompt."""
    source_blocks = []
    for index, doc in enumerate(docs, start=1):
        page = doc.metadata.get("page")
        page_label = f"page {int(page) + 1}" if isinstance(page, int) else "source passage"
        source_blocks.append(
            f"[Source {index} | {page_label}]\n{normalize_text(doc.page_content)}"
        )
    return "\n\n".join(source_blocks)


def build_prompt(name: str, age: int | None, question: str, context: str) -> str:
    """Compose the final grounded prompt sent to Gemini."""
    age_text = f", age {age}" if age else ""
    return f"""
You are Gita GPT, a compassionate spiritual guide inspired by Lord Krishna's
teachings in the Bhagavad Gita. Address the seeker named {name}{age_text}.

Use only the provided Bhagavad Gita source passages for scriptural grounding.
If the passages do not fully answer the question, say so with humility and give
a careful reflective answer based on the available context. Do not invent verse
numbers. Do not claim to be a medical, legal, or financial authority.

Structure the response with:
1. A direct answer.
2. A Gita-grounded reflection.
3. A practical action the seeker can take today.

Source passages:
{context}

Seeker's question:
{question}
""".strip()


def answer_question(
    llm: ChatGoogleGenerativeAI,
    vectorstore: Chroma,
    name: str,
    age: int | None,
    question: str,
    top_k: int,
) -> tuple[str, list]:
    """Retrieve relevant passages, ask Gemini, and return answer plus sources."""
    docs = vectorstore.similarity_search(question, k=top_k)
    context = format_sources(docs)
    prompt = build_prompt(name=name, age=age, question=question, context=context)
    response = llm.invoke(prompt)
    return str(response.content), docs


def pdf_escape(text: str) -> str:
    """Escape text for a simple PDF text object."""
    safe_text = text.encode("latin-1", "replace").decode("latin-1")
    return safe_text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def build_transcript_pdf(name: str, messages: list[dict]) -> bytes:
    """Generate a small PDF transcript without external PDF dependencies."""
    lines = [f"Gita GPT Conversation with {name}", ""]
    for message in messages:
        role = "You" if message["role"] == "user" else "Gita GPT"
        lines.append(f"{role}:")
        for paragraph in message["content"].splitlines() or [""]:
            lines.extend(textwrap.wrap(paragraph, width=92) or [""])
        lines.append("")

    pages = [lines[index : index + 46] for index in range(0, len(lines), 46)] or [[]]
    objects: list[bytes] = [
        b"",
        b"",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    ]
    page_ids = []

    for page_lines in pages:
        commands = ["BT", "/F1 11 Tf", "14 TL"]
        y = 792
        for line in page_lines:
            commands.append(f"1 0 0 1 54 {y} Tm ({pdf_escape(line)}) Tj")
            y -= 15
        commands.append("ET")
        stream = "\n".join(commands).encode("latin-1", "replace")
        content_id = len(objects) + 1
        objects.append(
            f"<< /Length {len(stream)} >>\nstream\n".encode("latin-1")
            + stream
            + b"\nendstream"
        )
        page_id = len(objects) + 1
        page_ids.append(page_id)
        objects.append(
            (
                f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] "
                f"/Resources << /Font << /F1 3 0 R >> >> /Contents {content_id} 0 R >>"
            ).encode("latin-1")
        )

    kids = " ".join(f"{page_id} 0 R" for page_id in page_ids)
    objects[0] = b"<< /Type /Catalog /Pages 2 0 R >>"
    objects[1] = f"<< /Type /Pages /Kids [{kids}] /Count {len(page_ids)} >>".encode(
        "latin-1"
    )

    output = b"%PDF-1.4\n"
    offsets = [0]
    for object_id, payload in enumerate(objects, start=1):
        offsets.append(len(output))
        output += f"{object_id} 0 obj\n".encode("latin-1") + payload + b"\nendobj\n"

    xref_start = len(output)
    output += f"xref\n0 {len(objects) + 1}\n".encode("latin-1")
    output += b"0000000000 65535 f \n"
    for offset in offsets[1:]:
        output += f"{offset:010d} 00000 n \n".encode("latin-1")
    output += (
        f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\n"
        f"startxref\n{xref_start}\n%%EOF\n"
    ).encode("latin-1")
    return output


def initialize_session() -> None:
    """Create all Streamlit session keys used by the app."""
    defaults = {
        "profile_ready": False,
        "name": "",
        "age": None,
        "intention": "",
        "messages": [],
        "last_sources": [],
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def render_profile_form() -> None:
    """Collect lightweight seeker context before opening the chat."""
    st.markdown('<div class="section-panel">', unsafe_allow_html=True)
    st.subheader("Begin your dialogue")
    with st.form("profile_form"):
        name = st.text_input("Name", placeholder="Arjuna")
        age = st.number_input("Age", min_value=1, max_value=120, value=21)
        intention = st.text_area(
            "What guidance are you seeking?",
            placeholder="Clarity, discipline, purpose, peace, duty, devotion...",
            height=100,
        )
        submitted = st.form_submit_button("Start Gita GPT")

    if submitted:
        st.session_state.name = name.strip() or "Seeker"
        st.session_state.age = int(age)
        st.session_state.intention = intention.strip()
        st.session_state.profile_ready = True
        st.session_state.messages = []
        st.session_state.last_sources = []
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)


def render_sidebar() -> None:
    """Render operational controls and status in the sidebar."""
    with st.sidebar:
        st.title("Gita GPT")
        st.caption("Grounded spiritual Q&A powered by Gemini and local retrieval.")

        st.subheader("Runtime")
        st.write(f"Model: `{CHAT_MODEL}`")
        st.write(f"Embedding: `{EMBEDDING_MODEL}`")
        st.write(f"Top K: `{TOP_K}`")
        st.write(f"Vector store: `{VECTOR_DIR.name}`")
        st.write(f"PDF: `{PDF_PATH.name}`")

        st.subheader("Session")
        if st.session_state.profile_ready:
            st.write(f"Name: **{st.session_state.name}**")
            st.write(f"Age: **{st.session_state.age}**")
            if st.session_state.intention:
                st.write(f"Intention: {st.session_state.intention}")

        if st.button("Clear chat"):
            st.session_state.messages = []
            st.session_state.last_sources = []
            st.rerun()

        if st.button("Reset profile"):
            for key in ["profile_ready", "name", "age", "intention", "messages", "last_sources"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()

        if st.session_state.messages:
            transcript = build_transcript_pdf(st.session_state.name, st.session_state.messages)
            st.download_button(
                "Download transcript",
                data=transcript,
                file_name=f"gita_gpt_{st.session_state.name.replace(' ', '_')}.pdf",
                mime="application/pdf",
            )


def render_chat(llm: ChatGoogleGenerativeAI, vectorstore: Chroma) -> None:
    """Render chat history, handle user input, and display source passages."""
    st.markdown('<div class="section-panel">', unsafe_allow_html=True)
    st.subheader(f"Namaste, {st.session_state.name}")
    if st.session_state.intention:
        st.caption(f"Your intention: {st.session_state.intention}")

    if not st.session_state.messages:
        st.info("Ask about duty, fear, discipline, detachment, purpose, grief, focus, or inner conflict.")

    for message in st.session_state.messages:
        avatar = ":material/self_improvement:" if message["role"] == "assistant" else ":material/person:"
        with st.chat_message(message["role"], avatar=avatar):
            st.write(message["content"])

    user_question = st.chat_input("Ask your question...")
    if user_question:
        st.session_state.messages.append({"role": "user", "content": user_question})
        with st.chat_message("user", avatar=":material/person:"):
            st.write(user_question)

        with st.chat_message("assistant", avatar=":material/self_improvement:"):
            with st.spinner("Retrieving Gita passages and preparing an answer..."):
                try:
                    answer, sources = answer_question(
                        llm=llm,
                        vectorstore=vectorstore,
                        name=st.session_state.name,
                        age=st.session_state.age,
                        question=user_question,
                        top_k=TOP_K,
                    )
                except Exception as exc:
                    answer = (
                        "I could not complete the retrieval or Gemini response. "
                        "Please check your API key, quota, and network access. "
                        f"Details: {friendly_error_message(exc)}"
                    )
                    sources = []

            st.write(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})
            st.session_state.last_sources = sources

    if st.session_state.last_sources:
        with st.expander("View retrieved source passages"):
            for index, doc in enumerate(st.session_state.last_sources, start=1):
                page = doc.metadata.get("page")
                page_label = f"Page {int(page) + 1}" if isinstance(page, int) else "Source"
                st.markdown(
                    f"""
                    <div class="source-box">
                        <strong>Source {index} - {page_label}</strong><br>
                        {normalize_text(doc.page_content)[:900]}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    st.markdown("</div>", unsafe_allow_html=True)


def main() -> None:
    """Streamlit entrypoint."""
    apply_theme()
    render_hero()
    require_configuration()
    initialize_session()
    render_sidebar()

    if not st.session_state.profile_ready:
        render_profile_form()
        return

    try:
        with st.spinner("Preparing the Gita knowledge base..."):
            llm = load_llm(GOOGLE_API_KEY, CHAT_MODEL)
            vectorstore = load_vectorstore(
                GOOGLE_API_KEY,
                EMBEDDING_MODEL,
                PDF_PATH.stat().st_mtime,
                CHUNK_SIZE,
                CHUNK_OVERLAP,
            )
    except Exception as exc:
        st.error("Gita GPT could not prepare the knowledge base.")
        st.write(
            "Check the Google API key, Generative Language API access, quota, "
            "and outbound network access from this machine or deployment host."
        )
        st.code(friendly_error_message(exc), language="text")
        st.stop()

    render_chat(llm, vectorstore)


if __name__ == "__main__":
    main()
