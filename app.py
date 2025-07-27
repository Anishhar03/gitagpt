import streamlit as st
import os
import base64
from dotenv import load_dotenv
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain.chains import RetrievalQA
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from fpdf import FPDF
import time # For streaming effect
import asyncio # Import asyncio for event loop management

# ------------------- Load API Key -------------------
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# ------------------- Configure Streamlit Page -------------------
st.set_page_config(
    page_title="Gita GPT - Your Spiritual Companion",
    page_icon="🕉️",
    layout="centered",
    initial_sidebar_state="expanded"
)

# ------------------- Custom CSS for Devotional Look and Feel with New Effects -------------------
def set_custom_css(background_b64):
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Merriweather:wght@700&family=Open+Sans:wght@400;600&family=Playfair+Display:wght=700&display=swap');

        /* Overall Page Styling */
        .stApp {{
            background: url("data:image/jpeg;base64,{background_b64}") center center fixed;
            background-size: cover;
            color: #E0E0E0; /* Lighter text for dark background */
            font-family: 'Open Sans', sans-serif;
            overflow-x: hidden; /* Prevent horizontal scroll */
            padding-top: 2rem; /* Add some top padding */
        }}

        /* Central Container for content */
        .main-content-container {{
            background: rgba(0, 0, 0, 0.4); /* Slightly dark, translucent overlay for readability */
            border-radius: 25px;
            box-shadow: 0 8px 30px rgba(0, 0, 0, 0.6); /* Stronger, deeper shadow */
            padding: 3rem;
            margin: 2rem auto;
            max-width: 900px; /* Wider content area */
            animation: fadeInScale 1s ease-out forwards;
            border: 2px solid #7B1FA2; /* Divine purple border */
        }}

        @keyframes fadeInScale {{
            from {{ opacity: 0; transform: scale(0.95) translateY(20px); }}
            to {{ opacity: 1; transform: scale(1) translateY(0); }}
        }}

        /* Title and Header */
        h1, h2, h3 {{
            font-family: 'Playfair Display', serif; /* More elegant font for titles */
            color: #FFD700; /* Gold for prominence */
            text-align: center;
            text-shadow: 0px 0px 15px rgba(255, 215, 0, 0.8), 0px 0px 8px rgba(0,0,0,0.5); /* Glowing effect */
            margin-bottom: 1.5rem;
            letter-spacing: 2px;
            animation: textGlowGold 2s infinite alternate;
        }}

        @keyframes textGlowGold {{
            from {{ text-shadow: 0px 0px 10px rgba(255, 215, 0, 0.7), 0px 0px 5px rgba(0,0,0,0.3); }}
            to {{ text-shadow: 0px 0px 20px rgba(255, 215, 0, 1), 0px 0px 10px rgba(0,0,0,0.5); }}
        }}
        
        /* Subheaders and descriptions */
        .stMarkdown p, .stMarkdown h4 {{
            color: #F8F8F8; /* Lighter color for better contrast */
            text-align: center;
            font-size: 1.1em;
            margin-bottom: 1.5rem;
        }}
        .stMarkdown p:last-child {{
            margin-bottom: 0;
        }}


        /* Streamlit components specific overrides */
        .stTextInput>div>div>input, .stTextArea>div>div>textarea {{
            background-color: rgba(255, 255, 255, 0.1); /* Subtle, dark background */
            border: 1px solid rgba(255, 255, 255, 0.3);
            color: #E0E0E0; /* Lighter text color */
            border-radius: 15px;
            padding: 0.8rem 1rem;
            transition: all 0.3s ease;
            box-shadow: inset 0 1px 5px rgba(0,0,0,0.2);
        }}
        .stTextInput>div>div>input:focus, .stTextArea>div>div>textarea:focus {{
            border-color: #FFD700; /* Gold focus glow */
            box-shadow: 0 0 0 0.2rem rgba(255, 215, 0, 0.25), inset 0 1px 5px rgba(0,0,0,0.3);
            outline: none;
        }}
        
        .stButton>button {{
            background: linear-gradient(135deg, #9C27B0, #7B1FA2); /* Gradient purple button */
            color: white;
            border-radius: 15px;
            border: none;
            padding: 0.7rem 1.8rem;
            font-size: 1.1rem;
            font-weight: 600;
            transition: all 0.3s ease;
            box-shadow: 0px 6px 20px rgba(0,0,0,0.4); /* Deeper shadow */
            margin: 0.5rem auto;
            display: block;
            text-transform: uppercase;
            letter-spacing: 1px;
            cursor: pointer;
        }}
        .stButton>button:hover {{
            background: linear-gradient(135deg, #7B1FA2, #6A1B9A); /* Darker gradient on hover */
            transform: translateY(-3px) scale(1.02);
            box-shadow: 0px 10px 25px rgba(0,0,0,0.5);
        }}

        /* Chat Bubbles */
        /* Targets the actual content div within chat messages */
        .st-emotion-cache-eczf16 > div {{ 
            padding: 1rem 1.2rem;
            margin-bottom: 1rem;
            border-radius: 25px; 
            max-width: 90%; 
            box-shadow: 0px 4px 15px rgba(0,0,0,0.3); /* Clearer shadow */
            animation: fadeIn 0.8s ease-out;
            line-height: 1.6;
            position: relative;
            overflow: hidden; 
            /* Remove backdrop-filter to remove glass effect */
        }}
        /* No inner glow, instead a solid background for bubbles */
        .st-emotion-cache-eczf16 > div::before {{
            display: none; /* Hide the pseudo-element used for inner glow */
        }}

        /* Specific bubble colors based on role (Streamlit internal classes) */
        .st-emotion-cache-1c7y2qn.st-emotion-cache-18jva2u .st-emotion-cache-eczf16 > div {{ /* User message bubble */
            background-color: #4A148C; /* Deep purple for user */
            color: #FFEBEE; /* Light text for user bubble */
            border: 1px solid rgba(255, 255, 255, 0.2); 
            margin-left: auto; 
            border-bottom-right-radius: 8px; 
            border-top-right-radius: 25px; 
            border-bottom-left-radius: 25px; 
            border-top-left-radius: 25px; 
        }}

        .st-emotion-cache-1c7y2qn.st-emotion-cache-h6n150 .st-emotion-cache-eczf16 > div {{ /* Assistant message bubble */
            background-color: #1A237E; /* Deep blue for Krishna */
            color: #E8EAF6; /* Lighter text for Krishna bubble */
            border: 1px solid rgba(255, 255, 255, 0.2);
            margin-right: auto; 
            border-bottom-left-radius: 8px; 
            border-top-left-radius: 25px; 
            border-bottom-right-radius: 25px;
            border-top-right-radius: 25px;
        }}
        
        /* Avatars (Streamlit chat elements) - Adjusting alignment to place message next to avatar */
        .st-emotion-cache-1c7y2qn {{ /* Targets the overall chat message container */
            display: flex;
            align-items: flex-start; /* Align avatar and message to the top */
            gap: 0.7rem; /* Space between avatar and message */
            width: 100%; /* Ensure it takes full width */
            margin-bottom: 0.5rem; /* Reduce space between chat entries */
        }}

        /* User message container (avatar on right, content on left of avatar) */
        .st-emotion-cache-1c7y2qn.st-emotion-cache-18jva2u {{ 
            flex-direction: row-reverse; 
            justify-content: flex-start; 
        }}
        .st-emotion-cache-1c7y2qn.st-emotion-cache-18jva2u .st-emotion-cache-eczf16 {{ /* User chat content wrapper */
            margin-left: 0.5rem; 
            flex-grow: 1; 
            display: flex; 
            justify-content: flex-end; 
        }}

        /* Assistant chat container (avatar on left, content on right of avatar) */
        .st-emotion-cache-1c7y2qn.st-emotion-cache-h6n150 {{ 
            flex-direction: row;
            justify-content: flex-start;
        }}
        .st-emotion-cache-1c7y2qn.st-emotion-cache-h6n150 .st-emotion-cache-eczf16 {{ /* Assistant chat content wrapper */
            margin-right: 0.5rem; 
            flex-grow: 1; 
            display: flex; 
            justify-content: flex-start; 
        }}

        /* Intro Form */
        .intro-container {{
            background: rgba(20, 0, 40, 0.7); /* Darker, more solid background */
            border: 2px solid #FFD700; /* Gold border */
            border-radius: 30px; 
            box-shadow: 0px 10px 40px rgba(0,0,0,0.6);
            text-align: center;
            max-width: 550px;
            margin: 4rem auto; 
            padding: 3rem;
            animation: popIn 1s ease-out forwards; 
        }}
        .intro-container h3 {{
            color: #FFD700; /* Gold for intro heading */
            margin-bottom: 2rem;
            font-size: 1.8rem; 
            text-shadow: 0px 0px 8px rgba(255, 215, 0, 0.5);
        }}
        
        /* Footer */
        .footer {{
            font-family: 'Open Sans', sans-serif;
            font-size: 0.95rem;
            color: #FFD700; /* Gold color for footer text */
            text-align: center;
            padding: 1.8rem;
            margin-top: 4rem;
            text-shadow: 1px 1px 4px rgba(0,0,0,0.3);
            background: rgba(0, 0, 0, 0.5); /* Solid dark background for footer */
            border-top: 1px solid rgba(255, 215, 0, 0.3); /* Subtle gold border top */
            border-radius: 15px; /* Keep some rounding */
        }}
        
        /* Sidebar Styling */
        .st-emotion-cache-vk33gh {{ /* Target the sidebar container */
            background: rgba(10, 0, 20, 0.8); /* Darker, more solid sidebar */
            border-right: 1px solid rgba(255, 215, 0, 0.3);
            box-shadow: 2px 0 15px rgba(0,0,0,0.4);
        }}
        .st-emotion-cache-vk33gh h2 {{
            color: #FFD700; /* Gold sidebar header */
            text-shadow: none;
            text-align: left;
            margin-bottom: 1rem;
        }}
        .st-emotion-cache-vk33gh .stButton>button {{
            background: linear-gradient(135deg, #7B1FA2, #6A1B9A);
            color: white;
            box-shadow: none; 
            display: inline-block; 
            margin: 0.5rem 0;
            width: 100%;
        }}
        .st-emotion-cache-vk33gh .stButton>button:hover {{
            background: linear-gradient(135deg, #6A1B9A, #4A148C);
            transform: none;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# ------------------- Load LLM -------------------
llm = ChatGoogleGenerativeAI(
    model="models/gemini-1.5-flash",
    google_api_key=GOOGLE_API_KEY,
)

# ------------------- Load and Embed PDF -------------------
@st.cache_resource
def create_vectorstore(pdf_path):
    # Ensure an asyncio event loop is available for GoogleGenerativeAIEmbeddings
    try:
        asyncio.get_event_loop()
    except RuntimeError:
        asyncio.set_event_loop(asyncio.new_event_loop())

    if not os.path.exists(pdf_path):
        st.error(f"Error: PDF file not found at {pdf_path}. Please ensure '{pdf_path}' is in the same directory as your app.")
        return None # Indicate failure
    try:
        loader = PyPDFLoader(pdf_path)
        pages = loader.load()
        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        docs = splitter.split_documents(pages)

        if not docs:
            raise ValueError("Text splitting failed. No chunks were created from the PDF.")

        embeddings = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001",
            google_api_key=GOOGLE_API_KEY,
        )

        # Persist directory for faster loading on subsequent runs
        persist_directory = "./gita_chroma"
        if os.path.exists(persist_directory) and os.listdir(persist_directory):
            vectorstore = Chroma(persist_directory=persist_directory, embedding_function=embeddings)
        else:
            vectorstore = Chroma.from_documents(
                docs, embedding=embeddings, persist_directory=persist_directory
            )
        return vectorstore
    except Exception as e:
        st.error(f"Failed to load or process PDF for embeddings: {e}")
        return None # Indicate failure

# Load background image once and pass its base64 to CSS
background_b64 = ""
try:
    with open("krishna_ji.jpeg", "rb") as img: # Ensure this is the correct filename
        background_b64 = base64.b64encode(img.read()).decode()
    set_custom_css(background_b64) # Pass the base64 string here
except FileNotFoundError:
    st.error("Background image 'krishna_ji.jpg' not found. Please ensure it's in the same directory.")
    st.stop()
except Exception as e:
    st.error(f"Error loading background image: {e}")
    st.stop()

# Initialize vectorstore and QA chain
qa_chain = None
vectorstore_initialized = False
try:
    vectorstore = create_vectorstore("gita_book.pdf")
    if vectorstore:
        qa_chain = RetrievalQA.from_chain_type(llm=llm, retriever=vectorstore.as_retriever(), return_source_documents=False)
        vectorstore_initialized = True
    else:
        st.warning("Could not initialize the spiritual wisdom repository (vector store). I will answer as Kanha based on my general knowledge.")
except Exception as e:
    st.warning(f"An error occurred during vector store initialization: {e}. I will answer as Kanha based on my general knowledge.")


# ------------------- Intro Screen (Modal-like) -------------------
if "name" not in st.session_state or not st.session_state.name:
    st.session_state.name = ""
    st.session_state.age = ""

    # This div contains the intro form and applies the new styling
    st.markdown("<div class='intro-container'>", unsafe_allow_html=True)
    st.subheader("🙏 Welcome, Seeker! Let's embark on this spiritual journey.")
    st.markdown("---") # Visual separator
    
    with st.form("intro_form", clear_on_submit=True):
        name = st.text_input("What is your sacred name?", max_chars=50, placeholder="Your Devotional Name...")
        age = st.text_input("How many springs have you witnessed?", max_chars=3, placeholder="Your Age in Years...")
        
        # Use a more thematic button text
        submitted = st.form_submit_button("🕊️ Enter the Realm of Gita's Wisdom")

        if submitted:
            if name.strip() and age.strip().isdigit():
                st.session_state.name = name.strip()
                st.session_state.age = int(age.strip())
                st.rerun() # Rerun to switch to chat interface
            else:
                st.warning("Please gracefully provide a valid name and numeric age to proceed on this path.")
    st.markdown("</div>", unsafe_allow_html=True)

# ------------------- Chat Interface -------------------
else:
    # Main content wrapper (replaces the 'glass-effect' for the whole chat area)
    st.markdown("<div class='main-content-container'>", unsafe_allow_html=True)
    st.markdown(f"### 🌸 Namaste, **{st.session_state.name}** (Age: {st.session_state.age})")
    st.markdown("*Seek guidance, and let Lord Krishna illuminate your path through the timeless wisdom of the Bhagavad Gita.*")

    if "messages" not in st.session_state:
        st.session_state.messages = []
        st.session_state.chat_history = []

    # Display chat messages from history on app rerun
    chat_container = st.container(height=500, border=False) # border=False because we apply custom styling
    
    with chat_container:
        for message in st.session_state.messages:
            if message["role"] == "user":
                with st.chat_message("user", avatar="🧍‍♂️"): # Using emoji as avatar
                    st.write(message["content"])
            else:
                with st.chat_message("assistant", avatar="🧘"): # Using emoji as avatar
                    st.write(message["content"])

    user_input = st.chat_input("🙏 Offer your question to Krishna...")

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        # Process AI response
        with st.spinner("Krishna is contemplating your profound question..."):
            if vectorstore_initialized and qa_chain:
                # Original prompt with added persona instruction
                prompt_with_persona = (
                    f"You are Lord Krishna from the Bhagavad Gita, addressing {st.session_state.name}, a seeker aged {st.session_state.age}. "
                    "Your responses should be imbued with the wisdom, compassion, and authority of the Gita. "
                    "Answer the following question as if I am Arjuna seeking guidance, always drawing upon the principles and teachings of the Bhagavad Gita. "
                    "Do not break character. Do not mention that you are an AI or a language model. "
                    f"Here is the seeker's query: {user_input}"
                )
                # Correct way to invoke a RetrievalQA chain
                response_dict = qa_chain.invoke({"query": prompt_with_persona})
                response = response_dict.get("result", "My dear devotee, I cannot find a direct answer in the scriptures for this. Please ask another question.")
            else:
                # Fallback to direct LLM if vector store not available
                fallback_prompt = (
                    f"You are Lord Krishna, addressing {st.session_state.name}, a seeker aged {st.session_state.age}. "
                    "Though my sacred texts are momentarily beyond reach, I shall share wisdom based on the eternal truths I embody. "
                    "Answer the following question as if I am Arjuna seeking guidance. "
                    "Do not break character. Do not mention that you are an AI or a language model. "
                    f"Here is the seeker's query: {user_input}"
                )
                response = llm.invoke(fallback_prompt).content
            
            # Append assistant's response to messages for immediate display after processing
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.session_state.chat_history.append((user_input, response))
            
            # Re-run the app to update the chat display with both new messages
            st.rerun() 

    st.markdown("</div>", unsafe_allow_html=True) # Close the main-content-container

    # ------------------- Sidebar (Applying glass-effect) -------------------
    with st.sidebar:
        st.header("🗂️ Sacred Options")
        st.markdown("<div class='sidebar-options-container'>", unsafe_allow_html=True) # New wrapper for sidebar options
        if st.button("🔄 Clear Our Dialogue"):
            st.session_state.messages = []
            st.session_state.chat_history = []
            st.success("Your dialogue with Krishna has been cleared. A fresh start awaits!")
            st.rerun() 
        
        def save_transcript(chat):
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.set_text_color(255, 215, 0) # Gold text for PDF for elegance
            
            pdf.cell(0, 15, txt=f"Bhagavad Gita GPT - Conversation with {st.session_state.name}", ln=True, align="C")
            pdf.ln(10) 

            for q, a in chat:
                pdf.set_font("Arial", "B", 10) 
                pdf.multi_cell(0, 8, f"You: {q}")
                pdf.ln(2) 

                pdf.set_font("Arial", "", 10) 
                pdf.set_text_color(173, 216, 230) # Light blue for Krishna's words in PDF
                pdf.multi_cell(0, 8, f"Krishna: {a}")
                pdf.set_text_color(255, 215, 0) # Reset to gold
                pdf.ln(8) 
            
            pdf.ln(10)
            pdf.set_font("Arial", "I", 8) 
            pdf.set_text_color(150, 150, 150) 
            pdf.cell(0, 10, "Generated by Gita GPT, your spiritual companion.", 0, 1, 'C')
            
            return pdf.output(dest='S').encode('latin-1')


        if st.button("📄 Preserve This Wisdom (Download Transcript)"):
            if st.session_state.chat_history:
                pdf_output = save_transcript(st.session_state.chat_history)
                st.download_button(
                    label="⬇️ Download PDF of Our Dialogue",
                    data=pdf_output,
                    file_name=f"gita_chat_{st.session_state.name.replace(' ', '_')}.pdf",
                    mime="application/pdf",
                    help="Download your conversation as a PDF file to cherish the wisdom."
                )
            else:
                st.warning("There is no divine conversation to preserve yet.")
        st.markdown("</div>", unsafe_allow_html=True)


    # ------------------- Footer -------------------
    st.markdown('<div class="footer">🌼 May Krishna’s wisdom ever guide your path. <br>Created with ❤️ and devotion by <strong>Anish K</strong></div>', unsafe_allow_html=True)
