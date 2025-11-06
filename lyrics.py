import os 
import re 
import torch
import numpy as np
import soundfile as sf
from typing import List, Dict, Tuple
from faster_whisper import WhisperModel


# Split audio into 30 sec chunk
def chunk_audio (audio_path: str, chunk_len: float = 30.0) -> List[Tuple[np.ndarray, int]]:
    audio, sr = sf.read(audio_path)
    total_sample = len(audio)
    chunk_size = int(chunk_len * sr)
    chunks = []

    for i in range(0, total_sample, chunk_size):
        j = min(i + chunk_size, total_sample)
        chunks.append((audio[i:j], sr))
    
    return chunks


# Save temp chunk for Whisper to read
def save_temp_chunk (chunk: np.ndarray, sr: int, idx: int) -> str:
    path = f"temp_chunk_{idx}.wav"
    sf.write(path, chunk, sr)
    return path



# Transcription
def transcribe_word_with_timestamps (vocal_path: str, model_size: str = "medium", compute_type: str = "float16", chunk_len: float = 30.0) -> Tuple[List[Dict], List[Dict]]:
    # Use GPU or CPU
    if torch.cuda.is_available():
        device = "cuda"
    else:
        device = "cpu"

    # Load Whisper model
    model = WhisperModel(model_size, device=device, compute_type=compute_type)
    
    all_segments = []
    all_words = []
    offset_time = 0.0

    # Split audio into 30 sec chunk
    chunks = chunk_audio(vocal_path, chunk_len=chunk_len)

    for idx, (chunk, sr) in enumerate(chunks):
        temp_path = save_temp_chunk(chunk, sr, idx)

        # Transcript
        segments, info = model.transcribe(temp_path, vad_filter=False, word_timestamps=True)

        # Collect timestamps
        for seg in segments:
            start, end = seg.start + offset_time, seg.end + offset_time
            text = seg.text.strip()
            if text:
                all_segments.append({"start": start, "end": end, "text": text})
            
            for w in seg.words or []:
                wt = w.word.strip()
                if not wt:
                    continue
                wt = re.sub(r"(^\W+|\W+$)", "", wt)
                if not wt:
                    continue
                all_words.append({"start": w.start + offset_time, "end": w.end + offset_time, "text": wt})

        
        # Clean temp
        os.remove(temp_path)
        offset_time += len(chunk) / sr

    return all_segments, all_words


# Convert word timestamps to .lrc for karaoke format
def words_to_lrc (words: List[Dict]) -> str:
    def convert_time(time):
        mins = int(time // 60)
        sec = int(time % 60)
        centisec = int((time - int(time)) * 100)

        return f"[{mins:02d}:{sec:02d}.{centisec:02d}]"
    
    lines = []
    for w in words:
        line = f"{convert_time(w['start'])}{w['text']}"
        lines.append(line)

    return "\n".join(lines)
                 

# Group words into lyric lines based on Whisper segment boundaries
def group_by_segment (segments: List[Dict], words: List[Dict]) -> List[List[Dict]]:
    lines = []
    for seg in segments:
        seg_words = []
        for w in words:
            if seg["start"] <= w["start"] < seg["end"]:
                seg_words.append(w)
        
        if seg_words:
            lines.append(seg_words)
    
    return lines