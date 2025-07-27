📚 Gita GPT - Developer Guide
This document provides an in-depth look into the architecture, components, and design choices behind the Gita GPT application. It is intended for developers who wish to understand, modify, or extend the project.

1. Introduction
Gita GPT is a Streamlit-based application that leverages Google's Generative AI models and LangChain to provide conversational answers from the Bhagavad Gita. Its core purpose is to offer spiritual guidance in the persona of Lord Krishna.

2. Architecture Overview
The application follows a standard RAG (Retrieval-Augmented Generation) architecture when the PDF knowledge base is available, with a direct LLM fallback for general spiritual queries.

Frontend (UI): Built entirely with Streamlit, providing a simple yet powerful way to create interactive web applications in Python. Custom CSS is heavily used for thematic styling.

Backend (Logic):

LangChain: Orchestrates the AI workflow, including document loading, text splitting, embedding, vector store creation, and the RetrievalQA chain.

Google Generative AI: Provides the large language model (gemini-1.5-flash) for generating responses and the embedding model (embedding-001) for converting text into numerical vectors.

ChromaDB: Used as the vector store to efficiently store and retrieve document embeddings. It's configured for persistence to speed up subsequent loads.

FPDF: A Python library used for generating PDF transcripts of the chat history.

python-dotenv: Manages environment variables, specifically for securely loading the Google API Key.

3. Core Components Explained
3.1. set_custom_css(background_b64)
This function is responsible for injecting custom CSS into the Streamlit application to achieve the desired devotional and vibrant UI.

Purpose: Overrides Streamlit's default styling to apply a custom theme.

Key Styling Decisions:

Background: Uses a base64 encoded image (krishna_ji.jpg) for the entire app background, set to cover to ensure it fills the screen.

Color Palette: Employs deep purples, blues, and gold (#7B1FA2, #4A148C, #1A237E, #FFD700) to evoke a spiritual and regal feel.

Typography: Imports Google Fonts (Merriweather, Open Sans, Playfair Display) for a more elegant and readable text presentation.

Animations: Includes @keyframes for subtle fadeInScale (for main containers) and textGlowGold (for titles) to add dynamism.

Component Overrides: Targets specific Streamlit internal classes (e.g., .stTextInput, .stButton, .st-emotion-cache-eczf16 > div for chat bubbles) to apply custom backgrounds, borders, shadows, and text colors.

Chat Bubbles: Each chat message bubble (user-bubble, krishna-bubble) has distinct background colors and rounded corners, with a slight "tail" effect on one side. The previous glassmorphism effects (backdrop-filter) have been removed in favor of solid, thematic colors.

3.2. create_vectorstore(pdf_path)
This function handles the crucial step of loading, processing, and embedding the Bhagavad Gita PDF.

PyPDFLoader: Loads the content from the specified PDF file.

RecursiveCharacterTextSplitter: Divides the loaded PDF pages into smaller, manageable chunks (chunk_size=1000, chunk_overlap=100). This is vital for effective retrieval, as LLMs have token limits and smaller chunks allow for more precise context.

GoogleGenerativeAIEmbeddings: Converts the text chunks into numerical vector representations (embeddings) using Google's embedding-001 model.

Chroma: Initializes or loads a persistent ChromaDB vector store.

persist_directory="./gita_chroma": Saves the vector store to disk, so embeddings don't need to be re-generated on every app restart, significantly speeding up loading times.

Error Handling: Includes try-except blocks to gracefully handle FileNotFoundError for the PDF or other exceptions during processing, returning None to signal failure.

3.3. LLM and Embeddings Initialization
llm = ChatGoogleGenerativeAI(...): Initializes the main language model (gemini-1.5-flash) used for generating conversational responses.

qa_chain = RetrievalQA.from_chain_type(...): Sets up the LangChain RetrievalQA chain. This chain takes a user query, retrieves relevant documents from the vectorstore using embeddings, and then passes both the query and the retrieved documents to the LLM to formulate an answer.

vectorstore_initialized flag: A boolean flag is used to track the successful initialization of the vector store. This is key for implementing the fallback mechanism.

3.4. Chat Logic and Persona Management
The core interaction logic resides in the else: block after the intro screen.

Session State (st.session_state):

st.session_state.name, st.session_state.age: Stores user's name and age from the intro screen.

st.session_state.messages: A list of dictionaries {"role": "user" | "assistant", "content": "message"} to maintain the full chat history for display.

st.session_state.chat_history: A list of tuples (user_query, assistant_response) specifically for PDF export.

st.chat_input: Captures user queries.

Response Generation:

Persona Prompt Engineering: The prompt_with_persona string is carefully crafted to instruct the LLM to adopt the persona of Lord Krishna, addressing the user by their name and age, and emphasizing responses based on Gita principles.

RAG (Retrieval-Augmented Generation): If vectorstore_initialized is True, qa_chain.invoke({"query": prompt_with_persona}) is used. This is the correct and modern way to call LangChain chains, replacing the deprecated .run() method. The result is extracted from the response_dict.get("result", ...).

Fallback Mechanism: If vectorstore_initialized is False (due to PDF issues), a fallback_prompt is used directly with llm.invoke(). This prompt still maintains the Krishna persona but acknowledges the temporary unavailability of the specific scriptures, allowing the LLM to generate a general spiritual response.

Streaming Effect: A simple time.sleep(0.05) loop within the st.chat_message block simulates a typing effect for the assistant's response, enhancing user experience.

st.rerun(): Called after both user and assistant messages are processed and added to st.session_state.messages to trigger a full Streamlit re-render, updating the chat display.

3.5. PDF Transcript Generation (save_transcript(chat))
FPDF: This function uses the FPDF library to create a PDF document from the st.session_state.chat_history.

Styling: Sets fonts, sizes, and text colors within the PDF itself, using thematic colors (Gold for user/header, Light Blue for Krishna's words) for a pleasant reading experience.

pdf.output(dest='S').encode('latin-1'): Returns the PDF as a byte string, which is then used by st.download_button.

4. UI Structure and Responsiveness
The UI is designed to be responsive, adapting to different screen sizes.

main-content-container: A new div wrapping the main chat area provides a distinct, semi-transparent background and shadow, separating the interactive elements from the background image.

Chat Container (st.container): Manages the scrollable area for chat messages.

Streamlit's Internal Flexbox: Streamlit's st.chat_message components inherently use flexbox for layout (avatar next to message). The custom CSS further refines this by adjusting flex-direction, justify-content, and margin to ensure proper alignment and spacing of the custom-styled bubbles.

Relative Units: While not explicitly using vw/vh for all elements, Streamlit's default behavior combined with max-width on containers and width: 100% on inputs/buttons helps maintain responsiveness.

5. Error Handling and Robustness
PDF Loading: Explicit checks for gita_book.pdf existence and try-except blocks around PDF loading and embedding.

Vector Store Initialization: The vectorstore_initialized flag and the if-else logic for qa_chain.invoke ensure the app doesn't crash if the knowledge base isn't ready.

API Key: Relies on python-dotenv for secure loading, but the app will warn and stop if the key is missing or invalid.

6. Future Enhancements
Persistent Chat History: Implement a database (e.g., SQLite, Firebase Firestore) to save and load chat history across sessions.

Multiple Knowledge Bases: Allow users to upload and switch between different spiritual texts (e.g., Upanishads, Yoga Sutras).

Advanced Persona Control: Offer options for users to select different "Gurus" or aspects of Krishna for varied conversational styles.

Source Citation: Display which verses or chapters from the Gita were used to formulate an answer (requires modifying RetrievalQA to return source documents and processing them).

User Authentication: For personalized experiences and persistent history.

More Interactive UI Elements: Add features like voice input, image generation (e.g., visualizing concepts from the Gita), or interactive quizzes.

Deployment: Instructions for deploying to platforms like Streamlit Community Cloud, Hugging Face Spaces, or a custom server.

This guide should provide a solid foundation for anyone looking to understand and build upon the Gita GPT application.

🕉️ Gita GPT - Your Spiritual Companion
🙏 Overview
Gita GPT is an AI-powered conversational application designed to provide spiritual guidance and answers based on the timeless wisdom of the Bhagavad Gita. Acting as Lord Krishna himself, this companion offers insights, clarifies doubts, and illuminates the path of dharma, karma, and devotion, drawing directly from the sacred text.

Whether you seek profound philosophical understanding or practical advice for daily life, Gita GPT aims to be a serene and insightful guide on your spiritual journey.

✨ Features
Divine Persona: Interact with an AI embodying the wisdom and compassion of Lord Krishna, delivering responses in a devotional and authoritative tone.

Bhagavad Gita Knowledge Base: Answers are primarily retrieved from a provided PDF version of the Bhagavad Gita, ensuring authenticity and depth.

Intelligent Fallback: If the specific answer is not found within the loaded scriptures, Lord Krishna will still provide general spiritual wisdom based on his inherent knowledge.

Interactive Chat Interface: A clean, responsive, and aesthetically pleasing chat interface built with Streamlit.

Thematic UI Design: Features a custom devotional theme with vibrant colors, subtle animations, and a captivating background image of the divine flute and peacock feather.

Chat History Management: Clear your conversation to start anew.

Downloadable Transcripts: Preserve your sacred dialogues by downloading them as PDF documents.

Personalized Welcome: A brief introductory screen to greet you by your sacred name and age.

🚀 Getting Started
Follow these steps to set up and run Gita GPT on your local machine.

Prerequisites
Python 3.8 or higher

pip (Python package installer)

1. Clone the Repository
First, clone this repository to your local machine:

git clone https://github.com/your-username/gita-gpt.git
cd gita-gpt

2. Set up a Virtual Environment (Recommended)
It's good practice to use a virtual environment to manage dependencies:

python -m venv venv
# On Windows
.\venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate

3. Install Dependencies
Install the required Python packages using pip:

pip install -r requirements.txt

requirements.txt content:

streamlit
python-dotenv
langchain
langchain-community
langchain-google-genai
pypdf
chromadb
fpdf

(Note: The fpdf package is used, which might trigger a warning if fpdf2 is also installed. You can resolve this by running pip uninstall --yes pypdf && pip install --upgrade fpdf2 as suggested in the warning, but the app will still function.)

4. Obtain Google API Key
Gita GPT uses Google's Generative AI models (Gemini 1.5 Flash for chat, Embedding-001 for embeddings). You need a Google API Key:

Go to the Google AI Studio and create a new API key.

Create a file named .env in the root directory of your project (the same directory as app.py).

Add your API key to this file in the following format:

GOOGLE_API_KEY="YOUR_API_KEY_HERE"

Replace "YOUR_API_KEY_HERE" with your actual API key.

5. Prepare the Sacred Texts and Image
Bhagavad Gita PDF: Place your PDF file of the Bhagavad Gita named gita_book.pdf in the root directory of your project. This is crucial for the AI's knowledge base.

Background Image: Ensure the background image krishna_ji.jpg (the flute and peacock feather image) is also in the root directory.

6. Run the Application
Once all prerequisites are met, run the Streamlit application from your terminal:

streamlit run app.py

Your browser will automatically open to the Streamlit application.

💡 Usage
Welcome Screen: Upon launching, you'll be greeted by an introductory screen. Enter your sacred name and age to begin your spiritual journey.

Ask Krishna: In the chat interface, type your questions or seek guidance in the input box at the bottom and press Enter.

Receive Wisdom: Lord Krishna will respond with insights drawn from the Bhagavad Gita or general spiritual principles.

Clear Dialogue: Use the "Clear Our Dialogue" button in the sidebar to reset the conversation.

Preserve Wisdom: Click "Preserve This Wisdom (Download Transcript)" in the sidebar to download your entire conversation as a PDF.

🎨 Customization
Bhagavad Gita PDF: You can replace gita_book.pdf with another version of the Gita, or even a different spiritual text, as long as it's a PDF. Remember to rename it to gita_book.pdf or update the filename in app.py.

Background Image: Change krishna_ji.jpg to any other .jpg or .png image. Update the filename in app.py if different.

Persona: Modify the prompt_with_persona and fallback_prompt strings in app.py to adjust Krishna's tone or role.

UI Colors/Fonts: Dive into the set_custom_css function in app.py to tweak colors, fonts, and animations to your liking.

🤝 Contributing
Contributions are welcome! If you have suggestions for improvements, bug fixes, or new features, please feel free to open an issue or submit a pull request.

📜 License
This project is licensed under the MIT License - see the LICENSE file for details.

🙏 Acknowledgements
Created with ❤️ and devotion by Anish K.
