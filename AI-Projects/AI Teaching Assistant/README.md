# AI Teaching Assistant

A local Retrieval-Augmented Generation (RAG) project that searches course-video transcripts and answers student questions with relevant video titles and timestamps.

## How it works

```text
Course videos → MP3 audio → Whisper transcripts → Ollama embeddings
                                                    ↓
Student question → query embedding → similarity search → local LLM answer
```

1. Extract audio from videos with FFmpeg.
2. Transcribe audio into timestamped JSON chunks using Whisper.
3. Embed transcript chunks using Ollama's `bge-m3` model.
4. Retrieve the most similar chunks for a student question.
5. Ask the local `llama3.2` model to answer using only retrieved transcript context.

## Requirements

- Python 3.10+
- FFmpeg installed and available on PATH
- [Ollama](https://ollama.com/download) installed and running
- Models downloaded locally:

```bash
ollama pull bge-m3
ollama pull llama3.2
```

Install Python packages:

```bash
pip install -r requirements.txt
```

## Folder layout

```text
AI Teaching Assistant/
├── videos/                 # Input course videos
├── audios/                 # Generated MP3 files
├── jsons/                  # Generated timestamped transcripts
├── video_to_mp3.py         # Video-to-audio step
├── mp3_to_json.py          # Audio transcription step
├── preprocess_json.py      # Transcript embedding/index step
├── process_incoming.py     # Question answering
├── tests/
│   └── test_process_incoming.py
├── requirements.txt
└── README.md
```

Generated audio, transcript JSON and embedding-index files are local pipeline outputs. Build the index before asking questions; do not assume a prebuilt index is included in a fresh clone.

## Run the pipeline

Run each command from this project directory.

### 1. Add course videos

Put supported video files into `videos/`.

### 2. Extract audio

```bash
python video_to_mp3.py
```

### 3. Transcribe audio

```bash
python mp3_to_json.py
```

Whisper downloads its model the first time it runs. Transcription can be slow on CPU-only systems.

### 4. Build the searchable index

Make sure Ollama is running:

```bash
python preprocess_json.py
```

This creates `embeddings.joblib` from the transcript JSON files.

### 5. Ask questions

```bash
python process_incoming.py
```

Example question:

```text
Where does the course explain HTML forms?
```

The assistant retrieves relevant transcript excerpts and asks the local language model to answer with source video and timestamp details. If the transcript context does not support an answer, it is instructed to say the topic was not found.

## Tests

Run the retrieval tests:

```bash
python -m unittest discover -s tests -v
```

The tests cover similarity ranking, grounded prompt construction and missing-index handling. They do not require Ollama to be running.

## Important implementation notes

- Ollama runs locally at `http://localhost:11434` by default.
- The embedding index must be rebuilt if the transcript content or embedding model changes.
- Keep the same embedding model (`bge-m3`) for indexing and question queries.
- Model answers are generated text and may still be inaccurate. Check the cited video and timestamp against the original lesson.
- This project is intended as a learning/demo application, not as a source of authoritative educational assessment.

## Tech stack

Python, OpenAI Whisper, FFmpeg, Ollama, bge-m3, llama3.2, Pandas, NumPy, Scikit-learn, Joblib and Requests.
