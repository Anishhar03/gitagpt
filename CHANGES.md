# Changes

## 2026-05-27

- Rebuilt the Streamlit app into an end-to-end Gita RAG assistant powered by local PDF retrieval, optional Gemini synthesis, LangChain, and the bundled Bhagavad Gita PDF.
- Moved secret handling to environment variables and Streamlit Secrets; real API keys are intentionally excluded from Git.
- Added a polished landing experience, profile intake, chat flow, source passage viewer, and downloadable PDF transcript.
- Added deployment assets for Streamlit Cloud, Docker, and generic Python web hosts.
- Added developer documentation covering workflows, deployment, and the meaning of the major code blocks.
- Added lightweight project verification through `scripts/verify_project.py`.
- Removed generated vector-store data and local `.env` content from version control.
- Switched the default runtime to local RAG so the app works end to end without a valid Google key.
- Kept Gemini as an optional answer-synthesis backend through `GITA_GPT_ENGINE=auto` or `gemini`.
