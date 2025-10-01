import streamlit as st
import requests
from PIL import Image
from gtts import gTTS
import tempfile
import os
from audio_recorder_streamlit import audio_recorder

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

def describe_image(uploaded_file):
    """Placeholder for image description (replace with Vision model if needed)"""
    return "Image description placeholder. Add real model if needed."

# === STREAMLIT UI ===
st.title("👁️ VisionMate - Smart Assistant for the Visually Impaired")
st.markdown("Helps you read, listen, understand, and interact with the world around you.")

option = st.sidebar.selectbox("Choose a feature:", [
    "📄 Read Text from Image",
    "🖼️ Describe Image",
    "🎤 Voice Recorder"
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

# --- 🎤 Voice Recorder ---
elif option == "🎤 Voice Recorder":
    st.markdown("🎙️ Record your voice and play it back.")
    audio_bytes = audio_recorder(pause_threshold=2.0, sample_rate=16000)
    
    if audio_bytes:
        st.success("Audio recorded!")
        # Save temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
            f.write(audio_bytes)
            file_path = f.name
        st.audio(file_path, format="audio/wav")
