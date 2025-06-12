import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
import os
import base64
import PyPDF2

# Load API Key
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)

# Load and process Gita PDF
@st.cache_data
def load_gita_text(pdf_path):
    with open(pdf_path, 'rb') as f:
        reader = PyPDF2.PdfReader(f)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
    return text

gita_text = load_gita_text("gita_book.pdf")

# Set Background Krishna Image with transparent UI and gradient overlay
def set_background(image_file):
    with open(image_file, "rb") as img_file:
        b64_encoded = base64.b64encode(img_file.read()).decode()
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap');

        .stApp {{
            background-image:
                linear-gradient(rgba(10, 10, 30, 0.6), rgba(10, 10, 30, 0.6)),
                url("data:image/jpg;base64,{b64_encoded}");
            background-size: cover;
            background-repeat: no-repeat;
            background-attachment: fixed;
            font-family: 'Poppins', sans-serif;
            color: #eee;
        }}

        .block-container {{
            background: rgba(255, 255, 255, 0.12);
            padding: 3rem 4rem;
            border-radius: 20px;
            margin: 3rem auto;
            max-width: 900px;
            box-shadow: 0 12px 40px rgba(90, 55, 145, 0.7);
            backdrop-filter: blur(15px);
            -webkit-backdrop-filter: blur(15px);
            border: 1.5px solid rgba(255, 255, 255, 0.2);
            color: #f0f0f0;
            transition: background 0.3s ease;
        }}

        .block-container:hover {{
            background: rgba(255, 255, 255, 0.18);
        }}

        .title-style {{
            font-size: 4rem;
            font-weight: 700;
            text-align: center;
            color: #dcd0ff;
            text-shadow: 0 0 15px rgba(130, 80, 200, 0.9);
            margin-bottom: 0.25rem;
            user-select: none;
        }}

        .subtitle-style {{
            font-size: 1.4rem;
            text-align: center;
            color: #c6b9f7cc;
            margin-bottom: 2.5rem;
            font-style: italic;
            user-select: none;
        }}

        .stTextArea>div>div>textarea {{
            background: rgba(255, 255, 255, 0.22) !important;
            color: #fefefe !important;
            border-radius: 14px !important;
            border: 1.8px solid rgba(255, 255, 255, 0.35) !important;
            font-size: 1.2rem !important;
            padding: 1rem !important;
            min-height: 160px !important;
            resize: vertical !important;
            box-shadow: inset 0 2px 6px rgba(255,255,255,0.2);
            transition: border-color 0.3s ease;
            font-family: 'Poppins', sans-serif;
        }}

        .stTextArea>div>div>textarea:focus {{
            outline: none;
            border-color: #a984ff !important;
            box-shadow: 0 0 8px #a984ff;
            background: rgba(255, 255, 255, 0.3) !important;
        }}

        /* Custom scrollbar for textarea */
        .stTextArea>div>div>textarea::-webkit-scrollbar {{
            width: 8px;
        }}
        .stTextArea>div>div>textarea::-webkit-scrollbar-track {{
            background: rgba(255, 255, 255, 0.1);
            border-radius: 10px;
        }}
        .stTextArea>div>div>textarea::-webkit-scrollbar-thumb {{
            background-color: #6b32b3;
            border-radius: 10px;
        }}

        .stButton>button {{
            background: linear-gradient(135deg, #8a64d9, #6b32b3);
            color: white;
            font-weight: 600;
            font-size: 1.2rem;
            padding: 0.75rem 2.2rem;
            border-radius: 18px;
            border: none;
            box-shadow: 0 7px 20px rgba(107, 50, 179, 0.7);
            transition: all 0.35s ease;
            font-family: 'Poppins', sans-serif;
            user-select: none;
        }}

        .stButton>button:hover {{
            background: linear-gradient(135deg, #6b32b3, #4a1f7b);
            box-shadow: 0 10px 30px rgba(107, 50, 179, 0.9);
            cursor: pointer;
            transform: translateY(-3px);
        }}

        .stMarkdown {{
            font-size: 1.2rem;
            line-height: 1.7;
            color: #f3f0ff;
        }}

        </style>
        """,
        unsafe_allow_html=True,
    )

set_background("krishna_ji.jpeg")

# Title and subtitle
st.markdown('<div class="title-style">🕉️ Gita GPT</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle-style">Find solutions to life problems with the wisdom of Bhagavad Gita</div>',
    unsafe_allow_html=True,
)

# User Input
user_query = st.text_area(
    "🙏 Please enter your question:", height=170, placeholder="Example: I am feeling stressed, what should I do?"
)

# Gemini Model
model = genai.GenerativeModel("gemini-1.5-flash")

# Generate Response
def generate_gita_response(user_input):
    prompt = f"""
You are a wise guide inspired by the teachings of the Bhagavad Gita.

Answer the user's life problems by referring to relevant wisdom from the Gita. Provide motivation, perspective, and practical guidance rooted in Indian philosophy.

Here is some Gita content you can use as reference (limited to 3000 chars):
{gita_text[:3000]}

Now respond to this query:
"{user_input}"
    """
    response = model.generate_content(prompt)
    return response.text.strip()


# Submit Button
if st.button("🕊️ Get Answer"):
    if user_query.strip():
        with st.spinner("Please wait while Krishna’s wisdom is being fetched..."):
            answer = generate_gita_response(user_query)
            st.markdown("### 🧘‍♂️ Krishna's Guidance:")
            st.success(answer)
    else:
        st.warning("Please enter a question first.")

# Footer - Made by Anish
st.markdown(
    """
    <style>
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        padding: 1rem 0;
        background: transparent;
        text-align: center;
        font-size: 1rem;
        color: #cfc1f7;
        font-family: 'Poppins', sans-serif;
        text-shadow: 0 0 5px rgba(160, 130, 255, 0.6);
        z-index: 100;
    }
    </style>
    <div class="footer">
        🌸 Made with devotion by <strong>Anish</strong> 🙏
    </div>
    """,
    unsafe_allow_html=True
)
