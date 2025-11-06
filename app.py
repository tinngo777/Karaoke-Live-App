import os
import streamlit as st
import ffmpeg
from demucs_runner import run_demucs
from audio_utils import build_instrumental_from_stems, pick_vocal_path
from lyrics import transcribe_word_with_timestamps, group_by_segment, words_to_lrc
from website import audio_to_url, karaoke_player


# Save upload file from user to disk
def save_upload(uploaded_file):
    file_path = uploaded_file.name
    with open(file_path, "wb") as f:
        f.write(uploaded_file.read())

    # Handle video (.mp4 or .mov)
    file_type = os.path.splitext(file_path)[1].lower()
    if file_type in [".mp4", ".mov"]:
        wav_path = "converted.wav"
        (
            ffmpeg
            .input(file_path)
            .output(wav_path, acodec="pcm_s16le", ac=2, ar="44100")
            .overwrite_output()
            .run(quiet=True)
        )
        return wav_path
    return file_path


# Main App
st.set_page_config (page_title="Karaoke Live App", layout="centered")

st.title("Karaoke Live App")
st.caption("Feel like singing? Upload any song for an instant sing-along experience!")

uploaded_file = st.file_uploader("Upload audio or video file", type=["mp3", "wav", "flac", "m4a", "mp4", "mov"])

col1, col2 = st.columns(2)
with col1:
    model_size = st.selectbox("Whisper Model Size", ["tiny", "base", "small", "medium"], index = 2)
with col2:
    precision = st.selectbox("Precision", ["float32", "float16"], index = 0)


# Run pipeline
if uploaded_file and st.button("Generate Karaoke"):
    with st.spinner("Saving file..."):
        file_path = save_upload(uploaded_file)
    
    with st.spinner("Separating vocal using Demucs..."):
        stem_folder = run_demucs(file_path)
    
    with st.spinner("Building instrumental track..."):
        instrumental_path = build_instrumental_from_stems(stem_folder, output_path = "instrumental.wav")

    with st.spinner("Extracting lyrics..."):
        vocal_path = pick_vocal_path(stem_folder)
        segments, words = transcribe_word_with_timestamps(vocal_path, model_size=model_size, compute_type=precision)

    # Group lyrics into lines 
    lines = group_by_segment(segments, words)

    st.success("Karaoke is Ready!")


    st.subheader("Sing Along!")
    data_url = audio_to_url(instrumental_path)
    karaoke_player(data_url, lines)

    lrc_content = words_to_lrc(words)
    


    # Debug 
    with st.expander("Show Segments (Debug only)"):
        for seg in segments:
            st.write(f"{seg['start']:.2f}-{seg['end']:.2f} | {seg['text']}")