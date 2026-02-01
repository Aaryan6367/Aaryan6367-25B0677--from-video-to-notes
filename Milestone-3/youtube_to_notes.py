import os
import re
import json
import torch
import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

MODEL_NAME = "facebook/bart-large-cnn"
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
OUTPUT_DIR = "Milestone-3/outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

KEYWORDS = [
    "introduction", "overview", "definition", "example", "conclusion",
    "summary", "key points", "steps", "important", "concept", "note"
]

def get_youtube_id(url):
    if "youtube.com/watch?v=" in url:
        return url.split("v=")[1].split("&")[0]
    if "youtu.be/" in url:
        return url.split("youtu.be/")[1].split("?")[0]
    if "youtube.com/embed/" in url:
        return url.split("embed/")[1].split("?")[0]
    if "youtube.com/shorts/" in url:
        return url.split("shorts/")[1].split("?")[0]
    raise ValueError("Invalid YouTube URL")

def get_transcript(video_id):
    api = YouTubeTranscriptApi()
    try:
        return api.fetch(video_id)
    except:
        transcripts = api.list(video_id)
        auto = transcripts.find_generated_transcript(["en"])
        return auto.fetch()

def clean_text(transcript):
    return " ".join([t.text for t in transcript])

def serialize_transcript(transcript):
    return [{"text": t.text, "start": t.start, "duration": t.duration} for t in transcript]

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME).to(DEVICE)

def chunk_text(text, max_tokens=900, overlap=150):
    tokens = tokenizer(text)["input_ids"]
    chunks = []
    start = 0
    while start < len(tokens):
        end = min(start + max_tokens, len(tokens))
        chunk = tokenizer.decode(tokens[start:end], skip_special_tokens=True)
        chunks.append(chunk)
        start += max_tokens - overlap
    return chunks

def summarize_chunk(text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=1024).to(DEVICE)
    ids = model.generate(inputs["input_ids"], max_length=180, min_length=80)
    return tokenizer.decode(ids[0], skip_special_tokens=True)

def hierarchical_summarize(text):
    summaries = [summarize_chunk(c) for c in chunk_text(text)]
    return summarize_chunk(" ".join(summaries))

def generate_smart_notes(summary):
    sentences = re.split(r'(?<=[.!?])\s+', summary)
    notes = []
    buffer = []
    section = 1

    for s in sentences:
        if any(k in s.lower() for k in KEYWORDS):
            if buffer:
                notes.append(f"## Section {section}")
                notes.extend([f"- {b}" for b in buffer])
                buffer = []
                section += 1
            notes.append(f"## {s.title()}")
        else:
            buffer.append(s)

    if buffer:
        notes.append(f"## Section {section}")
        notes.extend([f"- {b}" for b in buffer])

    return "\n".join(notes)

st.set_page_config(page_title="From Video to Notes", layout="centered")

st.title("🎥 From YouTube Video to Notes")
st.write("Paste a YouTube link and get structured study notes.")

url = st.text_input("Enter YouTube Video URL")

if st.button("Generate Notes"):
    if not url:
        st.error("Please enter a YouTube URL")
    else:
        with st.spinner("Processing video..."):
            try:
                vid = get_youtube_id(url)
                transcript = get_transcript(vid)
                text = clean_text(transcript)

                summary = hierarchical_summarize(text)
                notes = generate_smart_notes(summary)

                st.success("Done!")
                st.subheader("📄 Summary")
                st.write(summary)

                st.subheader("📝 Structured Notes")
                st.markdown(notes)

                st.download_button(
                    "Download Notes",
                    notes,
                    file_name=f"{vid}_notes.md"
                )

            except Exception as e:
                st.error(str(e))