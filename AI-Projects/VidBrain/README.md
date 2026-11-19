
# VidBrain — YouTube Video AI Assistant

VidBrain is a Retrieval-Augmented Generation (RAG) application that lets users ask questions about YouTube videos. It extracts the video transcript, converts it into searchable chunks, and uses AI to generate answers based on the video content.

## Features

- Extracts transcripts from YouTube videos.
- Splits transcripts into smaller searchable chunks.
- Uses Hugging Face embeddings and FAISS for semantic search.
- Uses Groq LLM to answer questions from retrieved transcript content.
- Maintains chat history during the session.
- Uses an in-memory vector store; no external database required.

## How It Works

```text
YouTube Video URL
       |
       v
Extract Transcript
       |
       v
Split into Text Chunks
       |
       v
Generate Embeddings
       |
       v
Store in FAISS
       |
       v
Retrieve Relevant Chunks
       |
       v
Groq LLM
       |
       v
Generate Answer
```

## Tech Stack

| Component | Technology |
|---|---|
| Application | Streamlit |
| Programming Language | Python |
| RAG Framework | LangChain |
| Embeddings | Hugging Face |
| Vector Database | FAISS |
| LLM Provider | Groq |
| Transcript Extraction | YouTube Transcript API |

**Embedding Model:** `paraphrase-multilingual-MiniLM-L12-v2`

**LLM Model:** `openai/gpt-oss-20b`

## Project Structure

```text
VidBrain/
├── app.py
├── rag_engine.py
├── requirements.txt
├── README.md
└── utils/
    ├── extract_vid_id.py
    └── transcript.py
```

## Run Locally

### 1. Clone the repository

```bash
git clone https://github.com/Viraj25789/Ai-Ml.git
cd Ai-Ml/AI-Projects/VidBrain
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure the Groq API key

Get an API key from [Groq Console](https://console.groq.com/).

In PowerShell, create the Streamlit configuration folder and file:

```powershell
New-Item -ItemType Directory -Force .streamlit
notepad .streamlit/secrets.toml
```

Add this line to the file:

```toml
GROQ_API_KEY = "your-groq-api-key"
```

Save the file.

**Important:** Never commit your real API key to GitHub.

### 5. Run the application

```bash
streamlit run app.py
```

Open the local address shown in your terminal, usually:

`http://localhost:8501`

## Streamlit Cloud Deployment

1. Push the project to GitHub.
2. Create a new app on [Streamlit Community Cloud](https://share.streamlit.io/).
3. Select the repository and branch.
4. Set the main file path to:

   `AI-Projects/VidBrain/app.py`

5. Open the app's settings and add this under Secrets:

```toml
GROQ_API_KEY = "your-groq-api-key"
```

6. Deploy the application.

Do not upload your local `secrets.toml` file to GitHub.

## Limitations

- Videos must have accessible captions or transcripts.
- Transcript quality affects answer quality.
- Answers are based on retrieved transcript sections and may not cover every detail in the video.
- The FAISS vector store is held in memory and is rebuilt when a new video is processed or the application session restarts.
- A working Groq API key is required.
