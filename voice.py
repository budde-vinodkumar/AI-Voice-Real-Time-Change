import streamlit as st
from pydub import AudioSegment
import librosa
import soundfile as sf
import numpy as np
import io

st.set_page_config(page_title="AI Voice Changer", layout="centered")
st.title("🎙️ Real-Time Voice Changer using AI Filters")
st.markdown("🎧 Upload or **record your voice** and apply filters like **Male**, **Female**, **Child**, or **Alien**")

# Choose mode
mode = st.radio("Choose input method", ["Upload", "Record"])
filter_type = st.selectbox("Select Voice Filter", ["Original", "Male", "Female", "Child", "Alien"])

# --------- FILTER FUNCTIONS ---------
def change_pitch(audio_array, sr, n_steps):
    return librosa.effects.pitch_shift(audio_array, sr=sr, n_steps=n_steps)

def alien_filter(audio_array, sr):
    alien_sound = change_pitch(audio_array, sr, 6)
    echo = np.roll(alien_sound, 2000)
    return (alien_sound + 0.5 * echo) / 1.5

def apply_filter(audio_data, sr, filter_type):
    if filter_type == "Male":
        return change_pitch(audio_data, sr, -4)
    elif filter_type == "Female":
        return change_pitch(audio_data, sr, 4)
    elif filter_type == "Child":
        return change_pitch(audio_data, sr, 6)
    elif filter_type == "Alien":
        return alien_filter(audio_data, sr)
    return audio_data

sr = 22050
y = None

# --------- UPLOAD ---------
if mode == "Upload":
    uploaded_file = st.file_uploader("Upload a WAV/MP3 file", type=["wav", "mp3"])
    if uploaded_file:
        st.audio(uploaded_file)
        audio = AudioSegment.from_file(uploaded_file)
        audio = audio.set_channels(1).set_frame_rate(sr)
        with io.BytesIO() as wav_io:
            audio.export(wav_io, format="wav")
            wav_io.seek(0)
            y, sr = librosa.load(wav_io, sr=sr)

# --------- RECORD ---------
else:
    st.caption("🎤 Tap the button below and record your voice:")
    audio_file = st.audio_input("Record your voice", key="mic_input")
    if audio_file:
        st.audio(audio_file)
        y, sr = librosa.load(audio_file, sr=sr)

# --------- FILTER & DOWNLOAD ---------
if y is not None:
    y_filtered = apply_filter(y, sr, filter_type)

    output_buffer = io.BytesIO()
    sf.write(output_buffer, y_filtered, sr, format="WAV")
    output_buffer.seek(0)

    st.success("✅ Voice filter applied successfully!")
    st.audio(output_buffer, format='audio/wav')

    st.download_button(
        label="⬇️ Download Filtered Audio",
        data=output_buffer,
        file_name=f"{filter_type}_voice.wav",
        mime="audio/wav"
    )
