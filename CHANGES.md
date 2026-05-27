# Changes

## 2026-05-27

- Rebuilt the Streamlit app into an end-to-end Gita RAG assistant powered by Gemini, LangChain, Chroma, and the local Bhagavad Gita PDF.
- Moved secret handling to environment variables and Streamlit Secrets; real API keys are intentionally excluded from Git.
- Added a polished landing experience, profile intake, chat flow, source passage viewer, and downloadable PDF transcript.
- Added deployment assets for Streamlit Cloud, Docker, and generic Python web hosts.
- Added developer documentation covering workflows, deployment, and the meaning of the major code blocks.
- Added lightweight project verification through `scripts/verify_project.py`.
- Removed generated vector-store data and local `.env` content from version control.
