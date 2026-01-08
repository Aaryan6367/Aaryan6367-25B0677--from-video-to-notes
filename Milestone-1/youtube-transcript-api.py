from youtube_transcript_api import YouTubeTranscriptApi
import json

url = str(input("Provide the url of video : "))

def get_youtube_id(url):
    if "youtube.com/watch?v=" in url:
        return url.split("v=")[1].split("&")[0]

    if "youtu.be/" in url:
        return url.split("youtu.be/")[1].split("?")[0].split("&")[0]

    if "youtube.com/embed/" in url:
        return url.split("embed/")[1].split("?")[0].split("&")[0]

    if "youtube.com/shorts/" in url:
        return url.split("shorts/")[1].split("?")[0].split("&")[0]
    else:
        raise ValueError("Could not extract YouTube video ID")

video_id=get_youtube_id(url)


def get_transcript(video_id):
    preferred_langs = ["en", "en-US", "en-GB"]
    api = YouTubeTranscriptApi()

    try:
        print("Trying manual English transcript...")
        return api.fetch(video_id, languages=preferred_langs)  # returns list of dicts
    except:
        pass

    try:
        print("Trying auto-generated English transcript...")
        transcripts = api.list(video_id)
        auto = transcripts.find_generated_transcript(preferred_langs)
        return auto.fetch()  # returns list of dicts
    except:
        pass

    print("Trying any available transcript...")
    return api.fetch(video_id)


def clean_text(transcript):
    text = " ".join([item.text for item in transcript])  # use attribute access
    text = text.replace("\n", " ")
    while "  " in text:
        text = text.replace("  ", " ")
    return text.strip()


try:
    video_id = get_youtube_id(url)
    transcript = get_transcript(video_id)
    cleaned_text = clean_text(transcript)

    with open(f"Milestone-1/outputs/{get_youtube_id(url)}.txt", "w", encoding="utf-8") as f:
        f.write(cleaned_text)

    with open(f"Milestone-1/outputs/{get_youtube_id(url)}.json", "w", encoding="utf-8") as f:
        def serialize_transcript(transcript):
            if isinstance(transcript, list):
                return transcript
            return [vars(item) for item in transcript]
        json.dump(serialize_transcript(transcript), f, indent=4, ensure_ascii=False)


    print("\nDone!")
    print("Saved:")
    print(f"{get_youtube_id(url)}.txt  -> clean transcript")
    print(f"{get_youtube_id(url)}.json    -> raw transcript data")

except Exception as e:
    print("Error:", e)


# fetched=ytapi.fetch(get_youtube_id(url))
# for snippet in fetched:
#     print(snippet.text)