import streamlit as st
import pytesseract
from PIL import Image
import speech_recognition as sr
import pyttsx3
import openai
import io
import requests

# === SETUP ===
openai.api_key = "YOUR_OPENAI_API_KEY"  # Replace with your key
engine = pyttsx3.init()

# === FUNCTIONS ===
def speak(text):
    engine.say(text)
    engine.runAndWait()

def extract_text_from_image(uploaded_file):
    image = Image.open(uploaded_file)
    text = pytesseract.image_to_string(image)
    return text

def transcribe_speech():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("Listening...")
        audio = r.listen(source)
    try:
        query = r.recognize_google(audio)
        return query
    except:
        return "Sorry, I could not understand."

def ask_chatgpt(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return response['choices'][0]['message']['content']

def describe_image(uploaded_file):
    # Placeholder description
    return "This appears to be an image. Image description from AI can be added using external APIs."

# === STREAMLIT UI ===
st.title("👁️ VisionMate - Smart Assistant for the Visually Impaired")
st.markdown("Helps you read, listen, understand, and interact with the world around you.")

option = st.sidebar.selectbox("Choose a feature:", [
    "📄 Read Text from Image",
    "🖼️ Describe Image",
    "🎤 Voice Assistant",
    "📝 Formal Message Generator"
])

if option == "📄 Read Text from Image":
    uploaded_file = st.file_uploader("Upload an image with text", type=["jpg", "png", "jpeg"])
    if uploaded_file:
        text = extract_text_from_image(uploaded_file)
        st.subheader("Extracted Text:")
        st.write(text)
        if st.button("🔊 Read Aloud"):
            speak(text)

elif option == "🖼️ Describe Image":
    uploaded_file = st.file_uploader("Upload an image to describe", type=["jpg", "png", "jpeg"])
    if uploaded_file:
        description = describe_image(uploaded_file)
        st.subheader("Image Description:")
        st.write(description)
        if st.button("🔊 Read Aloud"):
            speak(description)

elif option == "🎤 Voice Assistant":
    if st.button("🎙️ Speak Now"):
        query = transcribe_speech()
        st.write("You said:", query)
        response = ask_chatgpt(query)
        st.subheader("Response:")
        st.write(response)
        speak(response)

elif option == "📝 Formal Message Generator":
    input_text = st.text_area("Describe your issue or message casually")
    if st.button("Generate Formal Message") and input_text:
        prompt = f"Convert this into a professional and polite message:\n{input_text}"
        response = ask_chatgpt(prompt)
        st.subheader("Formal Version:")
        st.write(response)
        if st.button("🔊 Read Aloud"):
            speak(response)

# === END ===
