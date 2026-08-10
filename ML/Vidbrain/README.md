# 🧠 VidBrain: YouTube Transcript Analyzer

VidBrain is a Retrieval-Augmented Generation (RAG) application that allows users to instantly chat with hours-long YouTube tutorials. It extracts the video transcript, stores it in an ephemeral vector database, and uses LLMs to answer highly specific questions based *strictly* on the video's content.

## 🚀 Features

* **Zero-Cost In-Memory Vector Search:** Utilizes FAISS to store vector embeddings strictly in RAM, bypassing the need for expensive cloud database hosting.
* **Hallucination Prevention:** strict prompt engineering keeps answers grounded in the retrieved transcript context.
* **Ephemeral architecture** — no persistent storage, well suited to free-tier deployments with limited memory.

## 🛠️ Tech Stack

* **Frontend:** Streamlit
* **Orchestration:** LangChain
* **Embeddings:** HuggingFace (`paraphrase-multilingual-MiniLM-L12-v2`)
* **Vector Database:** FAISS (Facebook AI Similarity Search)
* **LLM:** Groq API (llama-3.1-8b-instant)
* **Data Extraction:** `youtube-transcript-api`

## 💻 Local Setup Instructions

1. **Clone the repository**

   ```bash
   git clone https://github.com/yourusername/vidbrain-youtube-rag.git
   cd vidbrain-youtube-rag
   ```

2. **Create and activate a virtual environment**

   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Add your Groq API key**

   create secrets file and fill your key:

   ```bash
   cp .streamlit/secrets.toml.example .streamlit/secrets.toml
   ```

   Then edit `.streamlit/secrets.toml`:

   ```toml
   GROQ_API_KEY = "your-groq-api-key-here"
   ```

   Get a free key at [console.groq.com](https://console.groq.com).

5. **Run the app**

   ```bash
   streamlit run app.py
   ```

   The app opens at `http://localhost:8501`.

## ⚠️ Limitations

* Only works on videos that have captions (manual or auto-generated) available.
* Vector store is per-session and in-memory — it's rebuilt if the app restarts or a new video is loaded.
* Answer quality depends on transcript quality; auto-generated captions can be noisy on some videos.
