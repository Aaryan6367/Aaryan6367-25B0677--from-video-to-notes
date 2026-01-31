from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch

MODEL_NAME = "facebook/bart-large-cnn"

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

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
    inputs = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        max_length=1024
    ).to(device)

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

    intermediate_summaries = []
    for i, chunk in enumerate(chunks):
        print(f"Summarizing chunk {i + 1}/{len(chunks)}...")
        summary = summarize_chunk(chunk)
        intermediate_summaries.append(summary)

    merged_summary = " ".join(intermediate_summaries)

    print("Generating final summary...")
    final_summary = summarize_chunk(
        merged_summary,
        max_length=300,
        min_length=120
    )

    return intermediate_summaries, final_summary

if __name__ == "__main__":
    with open("Milestone-2/long_text.txt", "r", encoding="utf-8") as f:
        long_text = f.read()

    _, final = hierarchical_summarize(long_text)

    print("\n================ FINAL SUMMARY ================\n")
    print(final)