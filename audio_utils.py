import os
import soundfile as sf
import numpy as np

STEMS = ["bass", "drums", "guitar", "piano", "vocals", "other"]


# Get audio array and sample rate
def read_file(path):
    audio, sr = sf.read(path, always_2d=True)
    return audio, sr


# Write a normalized WAV
def write_wav(path, audio, sr):
    peak = np.max(np.abs(audio))
    if peak > 1.0:
        audio = audio / peak
    sf.write(path, audio, sr)


# Build instrumental track by combining all stems (except vocals)
def build_instrumental_from_stems (stem_dir, output_path = "instrumental.wav"):
    mix = None
    sample_rate = None

    for stem in STEMS:
        if stem == "vocals":
            continue
        
        # Try both mp3 and wav
        cand_wav = os.path.join(stem_dir, f"{stem}.wav")
        cand_mp3 = os.path.join(stem_dir, f"{stem}.mp3")
        if os.path.exists(cand_wav):
            cand = cand_wav
        elif os.path.exists(cand_mp3):
            cand = cand_mp3

        if not os.path.exists(cand):
            continue

        audio, sr = read_file(cand)

        # Init empty mix arr
        if mix is None:
            mix = np.zeros_like(audio)
            sample_rate = sr

        # Add stem to mix
        mix[: len(audio)] += audio
        
    if mix is None:
        raise RuntimeError("No non-vocal stems found.")
    
    write_wav(output_path, mix, sample_rate)
    return output_path


# Pick vocal stem path
def pick_vocal_path(stem_dir):
    vp_wav = os.path.join(stem_dir, "vocals.wav")
    vp_mp3 = os.path.join(stem_dir, "vocals.mp3")

    if os.path.exists(vp_wav):
        return vp_wav
    elif os.path.exists(vp_mp3):
        return vp_mp3
    else:
        raise FileNotFoundError("No vocal stem found.")