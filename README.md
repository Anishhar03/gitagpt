# 🕉️ Gita GPT – Converse with the Bhagavad Gita using Gemini Flash 🌟

**Gita GPT** is a spiritual AI assistant that offers life advice and philosophical insights based on the **Bhagavad Gita**. It uses **Google's Gemini 1.5 Flash** model to answer your questions with context-aware responses drawn from the sacred scripture. The app is built entirely with **Python**, runs beautifully in **Streamlit**, and features a soothing, Krishna-themed UI. No vector databases, embeddings, or server infrastructure required — just wisdom at your fingertips.

---

## 🌄 Live Demo

👉 [Gita GPT Live on Streamlit](https://gitagptkanha.streamlit.app/)

---

## ✨ Features

- 🔮 Powered by **Google Gemini 1.5 Flash**
- 📖 Loads full **Bhagavad Gita** PDF locally (no vector DB or FAISS)
- 🧘 Life guidance based on ancient Indian philosophy
- 🎨 Krishna-themed gradient **glassmorphism UI**
- 💬 Natural language Q&A powered by contextual prompting
- ⚡ Lightning-fast, entirely in-memory and serverless
- 📦 No backend server, just pure frontend Python
- ✅ Deployable instantly via **Streamlit Cloud**

---

## 📸 Preview

> AI chatbot that answers life and spiritual questions using Bhagavad Gita teachings.  
> Built with **Google Gemini**, **PyPDF2**, and **Streamlit**.  
> Simulated lightweight **RAG** (Retrieval-Augmented Generation) using PDF parsing + prompt injection.  
> UI themed around Lord Krishna with custom CSS, gradients, and blur effects.

---

## 🧠 How It Works

1. **PDF Processing**: The app loads the Gita from a local PDF using `PyPDF2` and caches the full text.
2. **Prompt Generation**: When a user asks a question, a carefully crafted prompt is constructed. The first ~3000 characters of the Gita are used as reference text.
3. **Model Interaction**: The prompt is sent to **Gemini 1.5 Flash** using the `google-generativeai` SDK.
4. **Response Rendering**: The result is shown in a Krishna-themed glass UI using Streamlit's markdown and component system.

---

## 📁 Project Structure
gita-gpt/
├── gita_app.py # Main Streamlit app file
├── gita_book.pdf # The Bhagavad Gita (input PDF)
├── krishna_ji.jpeg # Background image for Krishna theme
├── .env # Environment file with API key
├── requirements.txt # Python dependencies
└── README.md # This documentation


---

## 🛠️ Installation

### 1. Clone the Repository

```bash
git clone https://github.com/Anishhar03/gitagpt.git
cd gita-gpt

