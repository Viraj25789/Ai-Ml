# 🎓 RAG AI Teaching Assistant

An AI assistant that watches your course videos for you. Ask it a question, and it tells you **exactly which video and timestamp** covers that topic — like a smart search engine built specifically for your course content.

## Tech Stack

- **AI/ML:** OpenAI Whisper (speech-to-text) · Ollama (`bge-m3` embeddings, `llama3.2` LLM) · RAG architecture · Cosine similarity search · PyTorch

- **Backend:** Python · pandas · NumPy · joblib · Requests

- **Media:** FFmpeg · Tiktoken · Numba

- **Highlights:** Full offline AI pipeline· vector    search built from scratch· modular ETL-style design (video → audio → transcript → embeddings → answer)

## How it works

```
Videos → Audio (mp3) → Transcripts (JSON) → Embeddings → Ask Questions → Get Answers with Timestamps
```

1. **Transcribe** — Every video is converted to audio, then transcribed to text using OpenAI's Whisper (speech-to-text) model.
2. **Embed** — Each transcript chunk is turned into a vector (a numeric representation of meaning) using an embedding model, so the assistant can search by *meaning*, not just keywords.
3. **Retrieve & Answer** — When a student asks a question, the assistant finds the most relevant transcript chunks and asks a local LLM to answer in plain language, pointing to the right video and timestamp.

This is a classic **RAG (Retrieval-Augmented Generation)** pipeline

## What's included in this repo

| File | Purpose |
|---|---|
| `video_to_mp3.py` | Converts course videos into audio files |
| `mp3_to_json.py` | Transcribes audio into JSON using Whisper |
| `preprocess_json.py` | Converts transcripts into vector embeddings and saves them |
| `process_incoming.py` | Takes a student's question and returns an answer with video + timestamp |
| `jsons/`, `audios/`, `videos/` | Sample data (only one sample file included here to keep the download light — the full project processes an entire course) |
| `embeddings.joblib` | Pre-computed embeddings from the full course, ready to query |
| `whisper/` | The Whisper speech-to-text library (vendored locally) |

> **Note:** This repo includes only one sample audio + transcript file for demo purposes. The full pipeline is built to handle an entire course (dozens of videos) — the included scripts and `embeddings.joblib` reflect that scale.

## Prerequisites

Before you start, make sure you have:

- **Python 3.10+**
- **FFmpeg** (used to extract audio from video files)
  - Windows: `winget install ffmpeg` or download from [ffmpeg.org](https://ffmpeg.org/download.html)
  - Mac: `brew install ffmpeg`
  - Linux: `sudo apt install ffmpeg`
- **[Ollama](https://ollama.com/download)** (runs the AI models locally on your machine — free, no API key needed)
- A GPU is recommended for faster transcription, but not required (CPU works, just slower)

## Setup Instructions

### 1. Clone the project and install Python dependencies

```bash
pip install -r requirements.txt
```

This single command also installs **Whisper** (`openai-whisper`), the speech-to-text model used in `mp3_to_json.py` — it's listed in `requirements.txt`, so no separate install step is needed.

> **About the `whisper/` folder in this repo:** that's a local copy of the Whisper source code (included for reference/offline use). You don't need to install it separately — the `pip install -r requirements.txt` command above already gives you a working `whisper` package. If you'd rather use the local copy instead of the pip version, run `pip install ./whisper` instead of relying on the requirements.txt line.

### 2. Install Ollama and download the required models

After installing Ollama, pull the two models this project uses:

```bash
ollama pull bge-m3        # used for embeddings (search)
ollama pull llama3.2      # used for generating answers
```

Make sure Ollama is running in the background (it usually starts automatically after install).

### 3. Add your videos

Place your course video files inside the `videos/` folder.

### 4. Run the pipeline (one time setup)

```bash
python video_to_mp3.py       # Step 1: extract audio from videos
python mp3_to_json.py        # Step 2: transcribe audio to text (this uses Whisper and may take a while)
python preprocess_json.py    # Step 3: turn transcripts into searchable embeddings
```

### 5. Ask questions!

```bash
python process_incoming.py
```

You'll be prompted to type a question, for example:

```
Ask a Question: where is HTML concluded in this course
```

The assistant will reply with a natural-language answer telling you which video(s) cover that topic and at what timestamp.

## Notes for setup

- Everything runs **locally on your machine** — no external API keys or paid services are required. Ollama and Whisper both run offline once installed.
- Transcription speed depends on your hardware. A GPU will speed this up significantly; on CPU-only machines, expect it to take longer per video.
- If you're evaluating this project and just want to see it work, you can skip Steps 3–4 and go straight to Step 5 — a pre-built `embeddings.joblib` (from the full course) is already included.
