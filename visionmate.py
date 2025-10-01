import streamlit as st
import requests
from PIL import Image
from gtts import gTTS
import tempfile
import os
import openai
from audio_recorder_streamlit import audio_recorder

# === SETUP ===
openai.api_key = st.secrets["openai_key"]  # Load from Streamlit Secrets

# === FUNCTIONS ===
def speak(text):
    """Convert text to speech and return an audio file path"""
    tts = gTTS(text)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
        tts.save(tmp_file.name)
        return tmp_file.name

def extract_text_from_image(uploaded_file):
    """Extract text from an uploaded image using OCR.Space"""
    api_key = "helloworld"  # Free test key from ocr.space
    image_bytes = uploaded_file.read()

    response = requests.post(
        'https://api.ocr.space/parse/image',
        files={"filename": image_bytes},
        data={"apikey": api_key, "language": "eng"},
    )

    result = response.json()
    try:
        return result['ParsedResults'][0]['ParsedText']
    except Exception:
        return "Text could not be extracted."

def ask_chatgpt(prompt):
    """Send prompt to ChatGPT and return response"""
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return response['choices'][0]['message']['content']

def transcribe_audio(audio_bytes):
    """Transcribe recorded audio using Whisper API"""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
        f.write(audio_bytes)
        file_path = f.name

    with open(file_path, "rb") as audio_file:
        transcript = openai.Audio.transcriptions.create(
            model="whisper-1",
            file=audio_file
        )
    return transcript.text

def describe_image(uploaded_file):
    """Placeholder for image description (replace with Vision model if needed)"""
    return "Image description placeholder. Add real model if needed."


# === STREAMLIT UI ===
st.title("👁️ VisionMate - Smart Assistant for the Visually Impaired")
st.markdown("Helps you read, listen, understand, and interact with the world around you.")

option = st.sidebar.selectbox("Choose a feature:", [
    "📄 Read Text from Image",
    "🖼️ Describe Image",
    "🎤 Voice Assistant",
    "📝 Formal Message Generator"
])

# --- 📄 Read Text from Image ---
if option == "📄 Read Text from Image":
    uploaded_file = st.file_uploader("Upload an image with text", type=["jpg", "png", "jpeg"])
    if uploaded_file:
        text = extract_text_from_image(uploaded_file)
        st.subheader("Extracted Text:")
        st.write(text)
        if st.button("🔊 Read Aloud"):
            audio_path = speak(text)
            st.audio(audio_path, format="audio/mp3")

# --- 🖼️ Describe Image ---
elif option == "🖼️ Describe Image":
    uploaded_file = st.file_uploader("Upload an image to describe", type=["jpg", "png", "jpeg"])
    if uploaded_file:
        description = describe_image(uploaded_file)
        st.subheader("Image Description:")
        st.write(description)
        if st.button("🔊 Read Aloud"):
            audio_path = speak(description)
            st.audio(audio_path, format="audio/mp3")

# --- 🎤 Voice Assistant ---
elif option == "🎤 Voice Assistant":
    st.markdown("🎙️ Record your voice and let VisionMate respond.")
    audio_bytes = audio_recorder(pause_threshold=2.0, sample_rate=16000)
    
    if audio_bytes:
        st.success("Audio recorded! Processing...")
        query = transcribe_audio(audio_bytes)
        st.write("You said:", query)

        response = ask_chatgpt(query)
        st.subheader("Response:")
        st.write(response)

        audio_path = speak(response)
        st.audio(audio_path, format="audio/mp3")

# --- 📝 Formal Message Generator ---
elif option == "📝 Formal Message Generator":
    input_text = st.text_area("Describe your issue or message casually")
    if st.button("Generate Formal Message") and input_text:
        prompt = f"Convert this into a professional and polite message:\n{input_text}"
        response = ask_chatgpt(prompt)
        st.subheader("Formal Version:")
        st.write(response)
        if st.button("🔊 Read Aloud"):
            audio_path = speak(response)
            st.audio(audio_path, format="audio/mp3")
