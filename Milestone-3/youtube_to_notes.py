"""
Milestone 3 / Week 3 - From Video to Structured Notes
------------------------------------------------------
- Week 1: YouTube transcript fetching (unchanged)
- Week 2: Hierarchical summarization (unchanged)
- Week 3: Smart structured notes with headings & bullets
- Fixed JSON serialization for FetchedTranscriptSnippet objects
"""

import os
import re
import json
import torch
from youtube_transcript_api import YouTubeTranscriptApi
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

# ---------------------------
# CONFIG
# ---------------------------
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
        return url.split("youtu.be/")[1].split("?")[0].split("&")[0]
    if "youtube.com/embed/" in url:
        return url.split("embed/")[1].split("?")[0].split("&")[0]
    if "youtube.com/shorts/" in url:
        return url.split("shorts/")[1].split("?")[0].split("&")[0]
    raise ValueError("Could not extract YouTube video ID")

def get_transcript(video_id):
    preferred_langs = ["en", "en-US", "en-GB"]
    api = YouTubeTranscriptApi()
    try:
        print("Trying manual English transcript...")
        return api.fetch(video_id)
    except:
        pass
    try:
        print("Trying auto-generated English transcript...")
        transcripts = api.list(video_id)
        auto = transcripts.find_generated_transcript(preferred_langs)
        return auto.fetch()
    except:
        pass
    print("Trying any available transcript...")
    return api.fetch(video_id)

def clean_text(transcript):
    text = " ".join([item['text'] if isinstance(item, dict) else item.text for item in transcript])
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def serialize_transcript(transcript):
    """
    Convert FetchedTranscriptSnippet objects into serializable dicts
    """
    serialized = []
    for t in transcript:
        serialized.append({
            "text": t.text,
            "start": t.start,
            "duration": t.duration
        })
    return serialized

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME).to(DEVICE)

def chunk_text(text, max_tokens=900, overlap=150):
    tokens = tokenizer(text)["input_ids"]
    chunks = []
    start = 0
    while start < len(tokens):
        end = min(start + max_tokens, len(tokens))
        chunk_tokens = tokens[start:end]
        chunk_text = tokenizer.decode(chunk_tokens, skip_special_tokens=True)
        chunks.append(chunk_text)
        if end == len(tokens):
            break
        start += max_tokens - overlap
    return chunks

def summarize_chunk(text, max_length=180, min_length=80):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=1024).to(DEVICE)
    summary_ids = model.generate(
        inputs["input_ids"],
        max_length=max_length,
        min_length=min_length,
        length_penalty=2.0,
        num_beams=4,
        early_stopping=True
    )
    return tokenizer.decode(summary_ids[0].cpu(), skip_special_tokens=True)

def hierarchical_summarize(text):
    chunks = chunk_text(text)
    print(f"Total chunks: {len(chunks)}")
    intermediate_summaries = [summarize_chunk(c) for c in chunks]
    merged_summary = " ".join(intermediate_summaries)
    final_summary = summarize_chunk(merged_summary, max_length=300, min_length=120)
    return intermediate_summaries, final_summary

def generate_smart_notes(summary, filename_prefix="notes"):
    sentences = re.split(r'(?<=[.!?])\s+', summary)
    notes = []
    section_count = 1
    section_buffer = []

    for i, sentence in enumerate(sentences):
        lower = sentence.lower()
        if any(kw in lower for kw in KEYWORDS):
            if section_buffer:
                notes.append(f"## Section {section_count}")
                notes.extend([f"- {s.strip()}" for s in section_buffer])
                section_count += 1
                section_buffer = []
            notes.append(f"## Section {section_count}: {sentence.strip().title()}")
            section_count += 1
        else:
            section_buffer.append(sentence.strip())
        if len(section_buffer) >= 5:
            notes.append(f"## Section {section_count}")
            notes.extend([f"- {s.strip()}" for s in section_buffer])
            section_count += 1
            section_buffer = []

    if section_buffer:
        notes.append(f"## Section {section_count}")
        notes.extend([f"- {s.strip()}" for s in section_buffer])

    notes_path = os.path.join(OUTPUT_DIR, f"{filename_prefix}.md")
    with open(notes_path, "w", encoding="utf-8") as f:
        f.write("\n".join(notes))
    print(f"Structured notes saved: {notes_path}")
    return notes_path

if __name__ == "__main__":
    video_url = input("Provide the YouTube video URL: ").strip()
    try:
        vid_id = get_youtube_id(video_url)
        transcript = get_transcript(vid_id)
        cleaned_text = clean_text(transcript)

        txt_path = os.path.join(OUTPUT_DIR, f"{vid_id}_transcript.txt")
        json_path = os.path.join(OUTPUT_DIR, f"{vid_id}_transcript.json")
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(cleaned_text)
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(serialize_transcript(transcript), f, indent=4, ensure_ascii=False)
        print(f"Transcript saved: {txt_path}")

        print("\nSummarizing transcript...")
        _, final_summary = hierarchical_summarize(cleaned_text)
        summary_path = os.path.join(OUTPUT_DIR, f"{vid_id}_summary.txt")
        with open(summary_path, "w", encoding="utf-8") as f:
            f.write(final_summary)
        print(f"Summary saved: {summary_path}")

        print("\nGenerating structured notes...")
        generate_smart_notes(final_summary, filename_prefix=f"{vid_id}_notes")

        print("\n✅ All done! Check the Milestone-3/outputs folder.")

    except Exception as e:
        print("Error:", e)