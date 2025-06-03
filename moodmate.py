import streamlit as st
from textblob import TextBlob
import pandas as pd
from datetime import datetime
import os
import time

# Page config must be first Streamlit command
st.set_page_config(page_title="MoodMate – Your Virtual Companion", layout="centered")

# Inject custom fonts and styling with black text for inputs and radios
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap');

    html, body, [class*="css"]  {
        font-family: 'Poppins', sans-serif;
        background-color: #F9FAFB;
    }
    h1, h2, h3 {
        color: #7D8AFF;
    }
    .stButton button {
        background-color: #7D8AFF;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5em 1.2em;
        font-weight: 600;
        transition: 0.3s;
    }
    .stButton button:hover {
        background-color: #6C77E5;
        transform: scale(1.02);
    }
    /* Text input styles */
    .stTextInput > div > div > input {
        background-color: #ffffff;
        border-radius: 8px;
        padding: 0.6em;
        color: #000000;   /* black text */
    }
    /* Text area styles */
    .stTextArea textarea {
        border-radius: 8px;
        padding: 0.6em;
        color: #000000;   /* black text */
        background-color: #ffffff;
    }
    /* Radio buttons container */
    .stRadio > div {
        background-color: #ffffff !important;
        border-radius: 8px;
        padding: 1em;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        color: #000000 !important;   /* black text */
    }
    /* Radio button label text */
    .stRadio > div label, 
    .stRadio > div label span,
    .stRadio > div label > div {
        color: #000000 !important; /* ensure black text for all label parts */
    }
    </style>
""", unsafe_allow_html=True)

st.title("🤖 MoodMate – Your Virtual Companion")
st.markdown("#### Let me listen to your thoughts and cheer you up ✨")

# Initialize logs CSV if not exists
csv_path = "mood_logs.csv"
if not os.path.exists(csv_path):
    df_init = pd.DataFrame(columns=["timestamp", "user_input", "polarity", "mood"])
    df_init.to_csv(csv_path, index=False)

if "show_breathing" not in st.session_state:
    st.session_state.show_breathing = False
if "show_feedback" not in st.session_state:
    st.session_state.show_feedback = False
if "detected_mood" not in st.session_state:
    st.session_state.detected_mood = ""

# Input form with text_input inside
with st.form(key="mood_form", clear_on_submit=False):
    user_input = st.text_input("Type a sentence about your mood:", "", key="user_input")
    submit = st.form_submit_button("Submit")

if submit and user_input.strip() != "":
    analysis = TextBlob(user_input)
    polarity = analysis.sentiment.polarity
    mood = ""
    message = ""

    if polarity > 0.2:
        mood = "happy"
        message = "😊 Glad that you're in a happy mood. Keep it that way!"
        st.success(message)

    elif polarity < -0.2:
        mood = "sad"
        message = "🤗 I hope you feel better soon. You got this."
        st.info(message)
        st.session_state.show_breathing = True

    elif -0.2 <= polarity <= 0.2:
        stress_keywords = ["tired", "overwhelmed", "stressed", "anxious", "nervous", "worried", "burned out"]
        if any(word in user_input.lower() for word in stress_keywords):
            mood = "stressed"
            message = "😣 You will figure it all out. Close your eyes and take a deep breath."
            st.info(message)
            st.session_state.show_breathing = True
        else:
            mood = "neutral"
            message = "🌸 Hey, look around, the world is such a beautiful place with you in it."
            st.success(message)

    # Save mood log
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = pd.DataFrame([[timestamp, user_input, polarity, mood]],
                             columns=["timestamp", "user_input", "polarity", "mood"])
    log_entry.to_csv(csv_path, mode="a", header=False, index=False)

    st.session_state.detected_mood = mood
    st.session_state.show_feedback = False  # Wait for feedback button

# Breathing exercise section (repeat 3 times)
if st.session_state.show_breathing:
    if st.button("Start Breathing Exercise"):
        st.markdown("### 🧘 Breathe with Me. Repeat 3 times.")

        phases = [("Inhale... 🌬️", 4), ("Hold... ✋", 2), ("Exhale... 😌", 4)]
        progress_bar = st.empty()
        label = st.empty()

        for cycle in range(3):  # Repeat 3 times
            label.markdown(f"### Cycle {cycle + 1} of 3")
            for label_text, duration in phases:
                label.markdown(f"### {label_text}")
                for i in range(100):
                    time.sleep(duration / 100)
                    progress_bar.progress(i + 1)

        st.session_state.show_breathing = False

        # Reflection prompt
        st.markdown("### ✍️ Take a moment to reflect")
        reflection = st.text_area("Write how you feel now after the breathing:")

        if st.button("Save Reflection"):
            try:
                with open("reflections.txt", "a") as f:
                    f.write(f"{datetime.now()} – {reflection}\n")
                st.success("Reflection saved ✅")
                st.session_state.show_feedback = True
            except Exception as e:
                st.error(f"Failed to save reflection: {e}")

# Feedback button
if not st.session_state.show_feedback and st.session_state.detected_mood:
    if st.button("Give Feedback"):
        st.session_state.show_feedback = True

# Feedback form
if st.session_state.show_feedback:
    st.markdown("### 💬 We'd love your feedback")
    post_mood = st.slider("How do you feel now (1 = very bad, 5 = very good)?", 1, 5, 3)
    supported = st.radio("Did you feel supported by MoodMate?", ["Yes", "No"])
    comment = st.text_area("Any feedback or suggestions?")

    if st.button("Submit Feedback"):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        feedback_entry = pd.DataFrame(
            [[timestamp, st.session_state.detected_mood, post_mood, supported, comment]],
            columns=["timestamp", "detected_mood", "post_mood_rating", "supported", "user_comment"]
        )
        feedback_file = "user_feedback.csv"
        feedback_entry.to_csv(feedback_file, mode="a", header=not os.path.exists(feedback_file), index=False)
        st.success("✅ Thank you for your feedback!")

# Reset button with fallback if experimental_rerun missing
if st.button("Reset"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    try:
        st.experimental_rerun()
    except AttributeError:
        st.write("Please refresh the page to complete the reset.")
