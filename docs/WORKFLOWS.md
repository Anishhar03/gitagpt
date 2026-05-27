# Workflows

This document explains how Gita GPT behaves from the user's point of view and from the system's point of view.

## User Workflow

1. The user opens the Streamlit app.
2. The app checks for required configuration:
   - `GOOGLE_API_KEY`
   - `gita_book.pdf`
   - `krishna_ji.jpeg`
3. The user enters:
   - name
   - age
   - intention or topic of guidance
4. The chat interface opens and prepares the Gita knowledge base.
5. The user asks a question.
6. The app retrieves relevant Bhagavad Gita passages.
7. Gemini produces a grounded answer.
8. The answer appears in the chat.
9. The user can expand "View retrieved source passages" to inspect the retrieved context.
10. The user can download a PDF transcript after at least one answer exists.

## RAG Workflow

1. `PyPDFLoader` reads `gita_book.pdf`.
2. `RecursiveCharacterTextSplitter` splits the PDF into overlapping chunks.
3. `GoogleGenerativeAIEmbeddings` converts chunks into embeddings.
4. `Chroma.from_documents()` stores embeddings in `gita_chroma/`.
5. On later runs, `Chroma(...)` loads the existing vector store.
6. When a user asks a question, `similarity_search()` retrieves the top passages.
7. The retrieved passages become source context in the prompt.
8. Gemini receives:
   - seeker name
   - seeker age
   - question
   - retrieved Gita passages
   - response structure instructions
9. The model returns a response with:
   - direct answer
   - Gita-grounded reflection
   - practical action

## Transcript Workflow

1. Chat messages are stored in `st.session_state.messages`.
2. The sidebar shows a download button when messages exist.
3. `build_transcript_pdf()` creates an in-memory PDF.
4. `st.download_button()` sends that PDF to the browser.

The transcript is not stored on the server.

## Deployment Workflow

Streamlit Cloud:

1. Push the repository to GitHub.
2. Create a Streamlit app from the repository.
3. Set `GOOGLE_API_KEY` in Streamlit Secrets.
4. Deploy `app.py`.
5. The app builds the vector index on first use.

Docker:

1. Build the container image.
2. Run the container with `GOOGLE_API_KEY`.
3. Expose port `8501`.
4. Open the app in a browser.

## Data and Runtime Files

Tracked source files:

- `app.py`
- `gita_book.pdf`
- `krishna_ji.jpeg`
- `requirements.txt`
- docs and deployment files

Generated or secret files:

- `.env`: local API key, ignored by Git
- `gita_chroma/`: generated vector index, ignored by Git
- `.streamlit/secrets.toml`: local Streamlit secrets, ignored by Git
