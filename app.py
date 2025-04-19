import streamlit as st
from groq import Groq
from gtts import gTTS
import tempfile
import pandas as pd
import fitz  # PyMuPDF
import os

# ---------- CONFIGURATION ----------
st.set_page_config(page_title="Translator & Speech Generator")

# Load environment variables
try:
    groq_api_key = st.secrets["GROQ_API_KEY"]
except Exception:
    from dotenv import load_dotenv
    load_dotenv()
    groq_api_key = os.getenv("GROQ_API_KEY")

if not groq_api_key:
    st.error("GROQ_API_KEY is not set. Please check your .env file.")
    st.stop()

client = Groq(api_key=groq_api_key)

# ---------- LANGUAGE MAP ----------
lang_code_map = {
    "French": "fr",
    "Spanish": "es",
    "Hindi": "hi",
    "German": "de",
    "Chinese": "zh-CN",
    "Nepali": "ne"
}

# ---------- FUNCTIONS ----------
def translate_text(text, target_language):
    prompt = f"Translate the following text to {target_language}:\n\n{text}"
    try:
        response = client.chat.completions.create(
            model="llama3-70b-8192",  # ✅ Updated model here
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=1000,
            top_p=1,
            stream=False,
            stop=None
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        raise RuntimeError(f"Error during translation: {e}")


def text_to_speech(text, lang_code='en'):
    tts = gTTS(text=text, lang=lang_code)
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tts.save(temp_file.name)
    return temp_file.name


def extract_text_from_file(uploaded_file):
    file_type = uploaded_file.name.split(".")[-1].lower()

    try:
        if file_type == "txt":
            return uploaded_file.read().decode("utf-8")

        elif file_type == "pdf":
            doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
            return "".join(page.get_text() for page in doc)

        elif file_type == "csv":
            df = pd.read_csv(uploaded_file)
            return df.to_string(index=False)

        elif file_type == "xlsx":
            df = pd.read_excel(uploaded_file)
            return df.to_string(index=False)
    except Exception as e:
        return f"Error reading file: {e}"

    return "Unsupported file format."


# ---------- UI ----------
st.title("Multilingual Text Translator & Speech Generator (Powered by Groq)")

with st.expander("How to use this app"):
    st.markdown("""
    1. Choose input method: type text or upload a file.
    2. Select the target language for translation.
    3. Click *Translate and Convert to Speech*.
    4. Download the generated audio file.
    """)

input_method = st.radio("Choose input method:", ("Enter text", "Upload file"))

text_input = ""
uploaded_file = None

if input_method == "Enter text":
    text_input = st.text_area("Enter the text you want to translate:")
else:
    uploaded_file = st.file_uploader("Upload a file (PDF, TXT, CSV, Excel)", type=["pdf", "txt", "csv", "xlsx"])

target_language = st.selectbox("Select target language:", list(lang_code_map.keys()))

if st.button("Translate and Convert to Speech"):
    final_text = None

    try:
        if input_method == "Enter text":
            if not text_input.strip():
                st.warning("Please enter some text.")
            else:
                final_text = text_input.strip()

        elif input_method == "Upload file":
            if uploaded_file is None:
                st.warning("Please upload a file.")
            else:
                final_text = extract_text_from_file(uploaded_file)

        if final_text:
            with st.spinner("Translating..."):
                translated_text = translate_text(final_text, target_language)
                st.success("Translation Complete:")
                st.write(translated_text)

            with st.spinner("Generating speech..."):
                lang_code = lang_code_map.get(target_language, "en")
                audio_path = text_to_speech(translated_text, lang_code)

            with open(audio_path, "rb") as f:
                st.download_button("Download Audio", f, file_name="speech.mp3", mime="audio/mpeg")

    except Exception as e:
        st.error(f"Something went wrong: {e}")