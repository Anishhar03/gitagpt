This project, "Gita GPT - Your Spiritual Companion," is a sophisticated Streamlit web application designed to provide wisdom and guidance based on the Bhagavad Gita. It acts as a conversational AI, allowing users to ask questions and receive answers imbued with the persona of Lord Krishna, drawing insights directly from the sacred text.

The application leverages several modern AI and web development technologies to achieve its functionality, focusing on Retrieval-Augmented Generation (RAG) to provide accurate and contextually relevant responses.

Project Overview: Gita GPT - Your Spiritual Companion
Title: Gita GPT - Your Spiritual Companion
Tagline: Seek guidance, and let Lord Krishna illuminate your path through the timeless wisdom of the Bhagavad Gita.

Gita GPT is an interactive web application that serves as a digital spiritual guide. Users can engage in a dialogue with an AI persona of Lord Krishna, asking questions about life, dharma, duty, and spiritual concepts. The AI's responses are not merely generated from its general knowledge; they are specifically grounded in the teachings of the Bhagavad Gita.

Core Functionality:
Personalized Welcome: Users are greeted with a personalized welcome screen where they enter their name and age, setting a devotional tone for the interaction.

Conversational Interface: A chat-like interface allows users to type their questions to "Lord Krishna."

Bhagavad Gita Wisdom Retrieval: The core of the application lies in its ability to search and retrieve relevant passages from the Bhagavad Gita PDF. This ensures that the AI's answers are directly informed by the scripture.

Lord Krishna Persona: The AI is instructed to maintain the persona of Lord Krishna, providing compassionate, authoritative, and wise guidance consistent with the Gita's teachings.

Conversation Transcript Download: Users can download their entire conversation with Lord Krishna as a PDF transcript for future reflection.

Thematic UI: A custom-designed, devotional user interface enhances the spiritual experience.

Technologies Used (In-Depth Explanation)
This project integrates several powerful Python libraries and frameworks:

Streamlit (streamlit>=1.36.0)

What it is: An open-source Python library that turns data scripts into shareable web apps in minutes. It simplifies front-end development, allowing Python developers to create interactive UIs without needing HTML, CSS, or JavaScript expertise.

Why it's used here: It's the backbone of the entire user interface. All the interactive elements (text inputs, buttons, chat messages, sidebars) are built using Streamlit's intuitive API. Its rapid prototyping capabilities make it ideal for quickly building and iterating on AI applications.

Python-dotenv (python-dotenv>=1.0.0)

What it is: A library that reads key-value pairs from a .env file and sets them as environment variables.

Why it's used here: Crucial for securely managing sensitive information like API keys (GOOGLE_API_KEY). Instead of hardcoding the API key directly into the script (which is a security risk), it's stored in a .env file. python-dotenv loads this variable at runtime, keeping credentials out of the main codebase, especially important for version control systems like Git.

LangChain (langchain>=0.2.11, langchain-community>=0.2.11, langchain-google-genai>=1.1.0, langchain-chroma>=0.2.2)

What it is: A powerful framework for developing applications powered by Large Language Models (LLMs). It provides a structured way to combine LLMs with other components (like data sources, tools, and agents) to build complex, intelligent applications.

Why it's used here: LangChain orchestrates the entire AI interaction flow:

langchain (Core): Provides the fundamental abstractions for building LLM applications (Chains, Prompts, etc.).

langchain-community: Offers common integrations and utilities within the LangChain ecosystem that are not provider-specific.

langchain-google-genai: This specific integration allows the application to connect to and use Google's Generative AI models, such as Gemini (for text generation) and embedding-001 (for creating numerical representations of text).

langchain-chroma: This integration facilitates the use of ChromaDB (a vector database) with LangChain, enabling efficient storage and retrieval of document embeddings.

Google Generative AI (via langchain-google-genai)

What it is: Google's suite of powerful Large Language Models (LLMs) and embedding models.

Why it's used here:

models/gemini-1.5-flash (LLM): This is the conversational AI model that generates the human-like responses. It's chosen for its balance of performance and cost-effectiveness.

models/embedding-001 (Embedding Model): This model converts text (from the Bhagavad Gita PDF and user queries) into high-dimensional numerical vectors (embeddings). These embeddings capture the semantic meaning of the text, allowing for efficient similarity searches in the vector database.

ChromaDB (via langchain-chroma)

What it is: An open-source vector database designed for AI applications. It stores numerical vector embeddings and allows for fast similarity searches.

Why it's used here: It serves as the "spiritual wisdom repository." When the Bhagavad Gita PDF is processed, its text is converted into embeddings and stored in ChromaDB. When a user asks a question, the question is also converted into an embedding, and ChromaDB quickly finds the most semantically similar passages from the Gita. This retrieved context is then fed to the LLM, enabling it to answer questions based on the specific text of the Gita (RAG).

PyPDFLoader (pypdf>=4.2.0)

What it is: A Python library for working with PDF files, specifically for extracting text content.

Why it's used here: It's used to load the gita_book.pdf file and extract all its textual content. This raw text is the foundation upon which the embeddings are created.

fpdf2 (fpdf2>=2.7.9)

What it is: A powerful Python library for generating PDF documents from scratch. It's a modern fork of the original FPDF library.

Why it's used here: It's utilized to create the downloadable PDF transcript of the user's conversation with Lord Krishna. It allows for precise control over text, fonts, colors, and layout within the generated PDF.

Pysqlite3-binary (pysqlite3-binary)

What it is: A pre-compiled binary distribution of sqlite3 for Python.

Why it's used here: This is a critical dependency for ChromaDB. Chroma requires a relatively recent version of sqlite3 (3.35.0 or newer). Standard Python installations, especially on some cloud environments like Streamlit Community Cloud, might come with an older sqlite3 version. pysqlite3-binary bypasses this by providing a compatible sqlite3 library that can be installed via pip, ensuring ChromaDB functions correctly in the deployment environment. The module swap (sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')) forces Python to use this binary version.

Python asyncio

What it is: Python's built-in library for writing concurrent code using the async/await syntax.

Why it's used here: GoogleGenerativeAIEmbeddings might internally use asynchronous operations. The try-except RuntimeError block around asyncio.get_event_loop() ensures that an event loop is available and set up correctly, preventing potential errors related to asynchronous execution in certain environments.

Key AI/NLP Concepts Explained
To understand how Gita GPT works, it's essential to grasp these concepts:

Large Language Models (LLMs):

Concept: These are deep learning models trained on vast amounts of text data, enabling them to understand, generate, and process human language. They can perform tasks like translation, summarization, question-answering, and creative writing.

In Gita GPT: models/gemini-1.5-flash is the LLM that powers the conversational aspect, generating responses based on the input query and the retrieved context.

Embeddings:

Concept: Embeddings are numerical representations (vectors) of text (words, sentences, paragraphs, or entire documents). Texts with similar meanings are mapped to vectors that are close to each other in a multi-dimensional space.

In Gita GPT: models/embedding-001 converts chunks of the Bhagavad Gita and user queries into these numerical vectors. This allows the system to mathematically compare the "meaning" of a user's question with the "meaning" of different parts of the Gita.

Vector Databases (Vector Stores):

Concept: Specialized databases designed to store and efficiently query vector embeddings. They use algorithms to quickly find vectors that are "closest" (most similar) to a given query vector.

In Gita GPT: ChromaDB is the vector store. It stores the embeddings of the Bhagavad Gita's text. When a user asks a question, the question's embedding is used to query ChromaDB, which then returns the most relevant text chunks from the Gita.

Retrieval-Augmented Generation (RAG):

Concept: A technique that enhances LLM capabilities by giving them access to external, up-to-date, and specific knowledge bases. Instead of relying solely on the LLM's pre-trained knowledge, RAG first retrieves relevant information from a data source and then augments the LLM's prompt with this information, leading to more accurate and contextually relevant generations.

In Gita GPT: This is the core AI architecture.

The gita_book.pdf is loaded and split into smaller docs (chunks).

These docs are converted into embeddings and stored in ChromaDB.

When a user asks a query, that query is also embedded.

ChromaDB is queried to find the most relevant docs (Gita passages) to the user's query.

These retrieved docs are then passed to the gemini-1.5-flash LLM along with the original query and the "Lord Krishna" persona instruction.

The LLM generates a response, ensuring it's grounded in the actual text of the Bhagavad Gita.

Text Splitting/Chunking:

Concept: LLMs have a limited "context window" (the amount of text they can process at once). Large documents like PDFs need to be broken down into smaller, manageable chunks. Text splitters ensure these chunks are of a suitable size and often have some overlap to maintain context across boundaries.

In Gita GPT: RecursiveCharacterTextSplitter is used to divide the entire Bhagavad Gita text into smaller chunk_size=1000 characters with chunk_overlap=100. This ensures that relevant information is captured within a chunk and that context isn't lost at the boundaries when searching.

Project Setup & Local Development
To run this project locally or deploy it, follow these steps:

1. Prerequisites:
Python 3.9+: Ensure you have a compatible Python version installed.

Git: For cloning the repository.

Google Cloud Project & API Key:

Go to the Google Cloud Console: https://console.cloud.google.com/

Create a new project (or select an existing one).

Enable the "Generative Language API" for your project.

Go to "APIs & Services" -> "Credentials" -> "Create Credentials" -> "API Key".

Copy your generated API key.

2. Project Files:
Ensure you have the following files in your project directory:

app.py (the main Streamlit application code)

requirements.txt (lists all Python dependencies)

.env (for local API key storage, not to be committed to Git)

gita_book.pdf (the Bhagavad Gita PDF file)

krishna_ji.jpeg (the background image for the UI)

3. Setup Steps:
Clone the Repository (if applicable):

Bash

git clone <your-repository-url>
cd <your-repository-name>
Create a Virtual Environment (Highly Recommended):
This isolates your project's dependencies from your system's Python packages.

Bash

python -m venv venv
Activate the Virtual Environment:

On Windows:

Bash

.\venv\Scripts\activate
On macOS/Linux:

Bash

source venv/bin/activate
Create .env File:
In the root of your project directory, create a file named .env and add your Google API Key:

GOOGLE_API_KEY="YOUR_ACTUAL_GOOGLE_API_KEY_HERE"
Remember: Do NOT commit this .env file to your Git repository! Add /.env to your .gitignore file.

Install Dependencies:
The requirements.txt file should contain:

streamlit>=1.36.0
python-dotenv>=1.0.0
langchain>=0.2.11
langchain-community>=0.2.11
langchain-google-genai>=1.1.0
langchain-chroma>=0.2.2
pypdf>=4.2.0
fpdf2>=2.7.9
pysqlite3-binary # Crucial for ChromaDB compatibility
Install them using pip:

Bash

pip install -r requirements.txt
Place gita_book.pdf and krishna_ji.jpeg:
Ensure these files are in the same directory as your app.py script.

Run the Application Locally:

Bash

streamlit run app.py
This will open the application in your web browser, typically at http://localhost:8501.

Code Walkthrough (app.py Deep Dive)
Let's break down the app.py script section by section:

SQLite3 Fix for Chroma (Lines 1-4):

Python

__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
Purpose: This is the most crucial part for deployment on environments like Streamlit Cloud. ChromaDB (used for vector storage) requires a specific, newer version of the sqlite3 library. Many system Python installations might have an older version.

Mechanism: pysqlite3-binary provides a pre-compiled, compatible sqlite3 library. These lines effectively tell Python: "Whenever any module tries to import sqlite3, instead give them the pysqlite3 module that we've installed." This ensures ChromaDB uses the correct sqlite3 version and prevents sqlite3 version errors. This must be at the very top of your script.

Imports (Lines 6-17):
Imports all necessary libraries: streamlit for UI, os for environment variables, base64 for image embedding, dotenv for .env loading, various langchain components for LLM and RAG, PyPDFLoader for PDF reading, FPDF from fpdf2 for PDF generation, XPos, YPos for fpdf2 positioning, time for potential streaming effects (though not heavily used in final version), and asyncio for event loop management.

Load API Key (Lines 20-25):

Python

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    st.error("🚨 Google API Key not found! Please set the GOOGLE_API_KEY environment variable in your `.env` file.")
    st.stop()
Loads environment variables from .env.

Retrieves GOOGLE_API_KEY.

Includes a safety check: if the API key isn't found, it displays an error and stops the app, preventing further issues.

Configure Streamlit Page (Lines 28-33):
st.set_page_config customizes the browser tab title, icon, layout (centered), and initial sidebar state.

Custom CSS (set_custom_css function) (Lines 36-224):

Purpose: This extensive function defines the visual theme of the application. It uses Streamlit's st.markdown(..., unsafe_allow_html=True) to inject custom CSS directly into the web page.

Styling: It sets background image, font families (Merriweather, Open Sans, Playfair Display), colors (gold, deep purples, blues), shadows, rounded corners, and animations (fadeInScale, textGlowGold).

Chat Bubbles: It specifically targets Streamlit's internal CSS classes (.st-emotion-cache-...) to style the user and assistant chat messages with distinct colors and shapes, creating a more engaging conversation experience.

Responsive Design: While not explicitly using media queries here, Streamlit's default components and relative sizing in the CSS (e.g., max-width: 900px, margin: auto) contribute to a reasonably responsive layout.

Load LLM (Lines 227-231):

Python

llm = ChatGoogleGenerativeAI(
    model="models/gemini-1.5-flash",
    google_api_key=GOOGLE_API_KEY,
)
Initializes the Google Generative AI model (gemini-1.5-flash) that will be used for generating responses.

Load and Embed PDF (create_vectorstore function) (Lines 234-290):

Python

@st.cache_resource
def create_vectorstore(pdf_path):
    # ... asyncio event loop setup ...
    if not os.path.exists(pdf_path): # Check if PDF exists
        # ... error handling ...
    try:
        loader = PyPDFLoader(pdf_path)
        pages = loader.load()
        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        docs = splitter.split_documents(pages)
        if not docs: # Check if splitting produced chunks
            # ... error handling ...
        embeddings = GoogleGenerativeAIEmbeddings(...)
        persist_directory = "./gita_chroma"
        if os.path.exists(persist_directory) and os.listdir(persist_directory):
            vectorstore = Chroma(persist_directory=persist_directory, embedding_function=embeddings)
        else:
            vectorstore = Chroma.from_documents(docs, embedding=embeddings, persist_directory=persist_directory)
        return vectorstore
    except Exception as e:
        # ... specific sqlite3 error handling and general error handling ...
@st.cache_resource: This Streamlit decorator is crucial. It tells Streamlit to run this function only once and cache its result (the vectorstore). This prevents the expensive PDF loading, text splitting, and embedding process from re-running every time the Streamlit app reruns (which happens frequently due to user interactions).

asyncio setup: Ensures a proper event loop for GoogleGenerativeAIEmbeddings.

PDF Loading: PyPDFLoader reads the gita_book.pdf.

Text Splitting: RecursiveCharacterTextSplitter breaks the PDF content into smaller docs (chunks) suitable for embedding and LLM context.

Embeddings: GoogleGenerativeAIEmbeddings converts these docs into numerical vectors.

ChromaDB Initialization:

It checks if a persistent ChromaDB directory (./gita_chroma) already exists. If it does, it loads the existing vector store, saving time.

If not, it creates a new ChromaDB from the docs and persists it to disk.

Error Handling: Includes robust error handling for missing PDF files and the specific sqlite3 version error.

Background Image Loading (Lines 293-301):
Loads the krishna_ji.jpeg image, converts it to Base64, and passes it to the set_custom_css function for use as the page background. Includes error handling for FileNotFoundError.

Initialize Vectorstore and QA Chain (Lines 304-315):

Python

qa_chain = None
vectorstore_initialized = False
try:
    vectorstore = create_vectorstore("gita_book.pdf")
    if vectorstore:
        qa_chain = RetrievalQA.from_chain_type(llm=llm, retriever=vectorstore.as_retriever(), return_source_documents=False)
        vectorstore_initialized = True
    # ... fallback message if vectorstore fails ...
except Exception as e:
    # ... warning message if vectorstore initialization fails ...
Calls create_vectorstore to get the ChromaDB instance.

If successful, it initializes a RetrievalQA chain from LangChain. This chain connects the LLM (gemini-1.5-flash) with the vectorstore (as a retriever), allowing the LLM to answer questions by first retrieving relevant context from the Gita.

A vectorstore_initialized flag is used to control whether the RAG chain is used or a general LLM fallback.

Intro Screen (Lines 318-348):

Python

if "name" not in st.session_state or not st.session_state.name:
    # ... form for name and age input ...
    # ... update session state and rerun on submission ...
Uses st.session_state to manage the user's name and age. If these are not set, it displays an introductory form.

st.form is used for input fields and a submit button.

st.rerun() is called after successful submission to switch to the chat interface.

Chat Interface (Lines 351-447):

Python

else: # If name and age are set
    # ... display welcome message ...
    if "messages" not in st.session_state:
        st.session_state.messages = []
        st.session_state.chat_history = []
    # ... display past messages ...
    user_input = st.chat_input(...)
    if user_input:
        # ... append user message ...
        with st.spinner(...):
            if vectorstore_initialized and qa_chain:
                # ... construct prompt with persona ...
                response_dict = qa_chain.invoke({"query": prompt_with_persona})
                response = response_dict.get("result", "...")
            else:
                # ... fallback LLM response ...
            # ... append assistant message and rerun ...
This is the main chat UI, displayed after the intro screen.

st.session_state.messages stores the messages for display in the chat history.

st.session_state.chat_history stores (user_query, ai_response) tuples for the PDF transcript.

st.chat_input provides the input box for user questions.

When a user asks a question:

It's added to st.session_state.messages.

A st.spinner shows a loading indicator.

If the vectorstore is initialized, the qa_chain is invoked with a persona-infused prompt that includes the user's name, age, and the question. This ensures the AI responds as Lord Krishna, grounded in the Gita.

If the vectorstore failed to initialize, a fallback prompt is sent directly to the LLM, indicating that it will answer from general knowledge.

The AI's response is appended to st.session_state.messages and st.session_state.chat_history.

st.rerun() updates the chat display.

Sidebar (Lines 450-508):

Python

with st.sidebar:
    st.header("🗂️ Sacred Options")
    if st.button("🔄 Clear Our Dialogue"):
        # ... clear session state and rerun ...
    def save_transcript(chat):
        pdf = FPDF()
        pdf.add_page() # CRITICAL FIX: Ensure a page is added
        # ... fpdf2 styling and content adding (with deprecation fixes) ...
        return bytes(pdf.output()) # CRITICAL FIX: Convert bytearray to bytes
    if st.button("📄 Preserve This Wisdom (Download Transcript)"):
        if st.session_state.chat_history:
            pdf_output = save_transcript(st.session_state.chat_history)
            st.download_button(...) # Download PDF
        else:
            st.warning(...)
Provides "Clear Dialogue" and "Download Transcript" options.

The save_transcript function uses fpdf2 to dynamically create a PDF of the chat history.

pdf.add_page(): This line is essential and was the cause of the FPDFException. You must add a page to the PDF document before you can add any content (like text cells).

pdf.set_font("helvetica", ...): Uses "helvetica" to avoid "Arial" deprecation warnings.

pdf.cell(..., text=..., new_x=XPos.LMARGIN, new_y=YPos.NEXT): Updates cell and multi_cell calls to use the modern text parameter and XPos/YPos enums instead of deprecated txt and ln parameters.

return bytes(pdf.output()): This is the final and correct way to get the PDF content as bytes for st.download_button. fpdf2.output() (without dest='S') returns a bytearray by default, which needs to be explicitly converted to bytes.

Footer (Lines 511-512):
A simple footer with a devotional message and creator credit.

Deployment on Streamlit Community Cloud
Deploying this app to Streamlit Community Cloud is straightforward, assuming your project is on GitHub:

GitHub Repository: Ensure your project (app.py, requirements.txt, gita_book.pdf, krishna_ji.jpeg) is pushed to a public GitHub repository.

Important: Do NOT push your .env file containing your GOOGLE_API_KEY to GitHub. Add it to .gitignore.

Streamlit Cloud Account: Go to https://share.streamlit.io/ and sign in.

New App: Click "New app" or "Deploy an app."

Connect Repository:

Select your GitHub repository.

Choose the branch (e.g., main).

Set the main file path (e.g., app.py).

Set Secrets: This is CRITICAL for your API key.

Before deploying, click on "Advanced settings" or "Secrets" in the deployment dialog.

Add a new secret:

Key: GOOGLE_API_KEY

Value: YOUR_ACTUAL_GOOGLE_API_KEY_HERE (paste your API key directly, no quotes).

Streamlit Cloud will automatically make this environment variable available to your app.

Deploy: Click "Deploy!" Streamlit will install your dependencies from requirements.txt, build your app, and provide you with a public URL.

Troubleshooting Common Issues (Recap)
Failed to load or process PDF for embeddings: Your system has an unsupported version of sqlite3. Chroma requires sqlite3 ≥ 3.35.0.

Cause: The sqlite3 library on the system (or in the Python environment) is too old for ChromaDB.

Solution: Ensure pysqlite3-binary is in your requirements.txt and the module swap code (__import__('pysqlite3'); import sys; sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')) is at the very top of your app.py.

StreamlitAPIException: Invalid binary data format: <class 'str'> (and similar AttributeError: 'bytearray' object has no attribute 'encode')

Cause: st.download_button expects bytes data. fpdf2.output() returns a bytearray. If it was somehow interpreted as a str or if you tried to encode() a bytearray, these errors occur.

Solution: The final solution is return bytes(pdf.output()) in your save_transcript function. This explicitly converts the bytearray to bytes.

FPDFException: No page open, you need to call add_page() first

Cause: You attempted to add content (like pdf.cell or pdf.multi_cell) to an fpdf2 document before calling pdf.add_page().

Solution: Ensure pdf.add_page() is called right after pdf = FPDF() within your save_transcript function.

Google API Key not found!

Cause: The GOOGLE_API_KEY environment variable is not set.

Solution: For local development, create a .env file. For Streamlit Cloud, set it as a secret in the app settings.

PDF file not found at 'gita_book.pdf' or Background image 'krishna_ji.jpeg' not found.

Cause: The specified files are not in the expected location (same directory as app.py).

Solution: Ensure gita_book.pdf and krishna_ji.jpeg are correctly placed in your project's root directory before deploying.

Future Enhancements
This project can be expanded in many ways:

Multiple Sacred Texts: Allow users to upload and query multiple spiritual texts, creating a broader knowledge base.

Advanced RAG Techniques: Implement more sophisticated retrieval methods (e.g., re-ranking retrieved documents, using different chunking strategies, or hybrid search).

User Authentication: Integrate Firebase or another authentication system to allow users to save their chat history across sessions.

Feedback Mechanism: Add a way for users to provide feedback on the AI's responses, helping to improve the model or persona.

Voice Interaction: Integrate speech-to-text and text-to-speech for a more immersive conversational experience.

Thematic Animations/Interactions: Add more subtle animations or interactive elements to the UI that align with the spiritual theme.

More Persona Customization: Allow users to choose different spiritual personas or adjust the AI's tone.

Contextual Memory: Implement a more robust chat memory that allows the AI to remember previous turns in the conversation more effectively for longer dialogues.
