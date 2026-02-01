# From Video to Notes

From Video to Notes is an AI-powered application that converts YouTube lecture videos into clean, structured study notes.  
The system automatically extracts video transcripts, summarizes long content using transformer models, and generates readable notes through a simple web interface.

The project is developed in three milestones, each adding a new layer of functionality.

--------------------------------------------------

PROJECT MOTIVATION

Students often struggle to:
- Watch long lecture videos repeatedly
- Identify important concepts efficiently
- Manually convert spoken explanations into notes

This project automates the entire process by:
- Extracting transcripts from YouTube videos
- Summarizing long-form text intelligently
- Generating structured notes
- Providing a user-friendly frontend

--------------------------------------------------

HIGH LEVEL ARCHITECTURE

YouTube Video  
→ Transcript Extraction  
→ Text Cleaning  
→ Hierarchical Summarization  
→ Structured Notes Generation  
→ Streamlit Web Interface  

--------------------------------------------------

MILESTONE 1: YouTube Transcript Extraction

Objective:
Build a tool that extracts and cleans transcripts from YouTube videos.

Features:
- Supports multiple YouTube URL formats
- Fetches manual English transcripts when available
- Falls back to auto-generated transcripts
- Cleans transcript text for NLP processing
- Saves outputs in text and JSON formats

Technologies Used:
- Python
- youtube-transcript-api

Output Structure:
Milestone-1/outputs/
- <video_id>.txt
- <video_id>.json

--------------------------------------------------

MILESTONE 2: Long Text Summarization Pipeline

Objective:
Summarize long transcripts while respecting transformer context length limits.

Problem:
Transformer models cannot process very long text directly.

Solution:
- Token-based chunking with overlap
- Hierarchical summarization approach
  - Summarize individual chunks
  - Merge and summarize again to generate a final summary

Technologies Used:
- HuggingFace Transformers
- facebook/bart-large-cnn
- PyTorch

Output:
Milestone-2/
- final_summary.txt

--------------------------------------------------

MILESTONE 3: End-to-End Web Application

Objective:
Build a complete AI-powered application with frontend and backend integration.

Features:
- Streamlit-based web interface
- Input field for YouTube video URL
- Automatic transcript extraction
- Intelligent summarization pipeline
- Structured note generation
- Automatic saving of all outputs

User Flow:
1. User enters a YouTube video URL
2. Transcript is fetched and cleaned
3. Text is summarized using transformer models
4. Structured notes are generated
5. Results are displayed and saved

Technologies Used:
- Streamlit
- HuggingFace Transformers
- PyTorch
- YouTube Transcript API

Output Structure:
Milestone-3/outputs/
- <video_id>_transcript.txt
- <video_id>_transcript.json
- <video_id>_summary.txt
- <video_id>_notes.md

--------------------------------------------------

RUNNING THE APPLICATION

Python Version Requirement:
This project uses HuggingFace Transformers which are most stable on:
- Python 3.10 or Python 3.11

Python 3.13 may cause runtime issues.

Setup Instructions (Windows):

1. Create a virtual environment
   python -3.10 -m venv venv

2. Activate the virtual environment
   venv\Scripts\activate

3. Install dependencies
   pip install streamlit torch transformers youtube-transcript-api

4. Run the Streamlit application
   python -m streamlit run Milestone-3/youtube_to_notes.py

--------------------------------------------------

KEY LEARNINGS

- Working with real-world APIs
- Handling long-context NLP problems
- Designing scalable summarization pipelines
- Integrating ML models with web interfaces
- Managing Python environment compatibility


AUTHOR

Aaryan  
B.Tech Student