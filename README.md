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
