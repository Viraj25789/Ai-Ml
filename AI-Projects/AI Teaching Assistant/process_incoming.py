"""Ask course questions against precomputed transcript embeddings.

Requires Ollama with bge-m3 and llama3.2 running locally.
"""
from pathlib import Path
import argparse

import joblib
import numpy as np
import pandas as pd
import requests
from sklearn.metrics.pairwise import cosine_similarity

ROOT = Path(__file__).resolve().parent
EMBEDDINGS_PATH = ROOT / "embeddings.joblib"
OLLAMA_URL = "http://localhost:11434"
EMBED_MODEL = "bge-m3"
CHAT_MODEL = "llama3.2"
REQUIRED_COLUMNS = {"title", "number", "start", "end", "text", "embedding"}


def ollama_post(endpoint, payload):
    try:
        response = requests.post(
            f"{OLLAMA_URL}{endpoint}", json=payload, timeout=(10, 180)
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as exc:
        raise RuntimeError(
            "Could not reach Ollama. Start Ollama and pull the required models."
        ) from exc
    except ValueError as exc:
        raise RuntimeError("Ollama returned an invalid JSON response.") from exc


def create_embedding(text):
    result = ollama_post("/api/embed", {"model": EMBED_MODEL, "input": [text]})
    embeddings = result.get("embeddings")
    if not embeddings or not embeddings[0]:
        raise RuntimeError("Ollama returned no query embedding.")
    return np.asarray(embeddings[0], dtype=float)


def load_embeddings(path=EMBEDDINGS_PATH):
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(
            f"Missing {path.name}. Run preprocess_json.py to build the search index."
        )
    frame = joblib.load(path)
    if not isinstance(frame, pd.DataFrame) or frame.empty:
        raise ValueError("The embedding index is empty or has an invalid format.")
    missing = REQUIRED_COLUMNS - set(frame.columns)
    if missing:
        raise ValueError(f"Embedding index is missing columns: {sorted(missing)}")
    frame = frame.dropna(subset=["text", "embedding"]).reset_index(drop=True)
    if frame.empty:
        raise ValueError("The embedding index contains no usable transcript chunks.")
    return frame


def retrieve(frame, query, top_k=5):
    if not isinstance(query, str) or not query.strip():
        raise ValueError("Please enter a non-empty question.")
    if not isinstance(top_k, int) or top_k < 1:
        raise ValueError("top_k must be a positive integer.")

    query_vector = create_embedding(query)
    try:
        vectors = np.vstack(frame["embedding"].map(
            lambda value: np.asarray(value, dtype=float)
        ).to_list())
    except (TypeError, ValueError) as exc:
        raise ValueError("Stored transcript embeddings are invalid.") from exc

    if (
        vectors.ndim != 2
        or vectors.shape[1] != len(query_vector)
        or not np.isfinite(vectors).all()
        or not np.isfinite(query_vector).all()
    ):
        raise ValueError("Stored embeddings do not match the Ollama embedding model.")

    scores = cosine_similarity(vectors, query_vector.reshape(1, -1)).ravel()
    indices = np.argsort(scores)[::-1][:top_k]
    results = frame.iloc[indices].copy()
    results["similarity"] = scores[indices]
    return results


def build_prompt(query, chunks):
    records = chunks[["title", "number", "start", "end", "text"]].to_dict("records")
    context = "\n".join(
        f"Video {item['number']} — {item['title']} "
        f"({float(item['start']):.1f}s–{float(item['end']):.1f}s): "
        f"{str(item['text'])}"
        for item in records
    )
    return f"""You are a course-content assistant. Answer only using the transcript excerpts below.
If the excerpts do not contain the answer, say that the topic was not found in the available course transcripts.
Never invent a video number, title, timestamp, or lesson detail.
Explain briefly and cite the relevant video title/number and timestamp in minutes:seconds.
If the question is unrelated to this course, politely say you can only answer questions about this course.

TRANSCRIPT EXCERPTS:
{context}

STUDENT QUESTION:
{query}

Answer:"""


def answer_question(query, index, top_k=5):
    chunks = retrieve(index, query, top_k=top_k)
    result = ollama_post(
        "/api/generate",
        {"model": CHAT_MODEL, "prompt": build_prompt(query, chunks), "stream": False},
    )
    answer = result.get("response", "").strip()
    if not answer:
        raise RuntimeError("The language model returned an empty answer.")
    return answer


def main():
    parser = argparse.ArgumentParser(description="Search course video transcripts.")
    parser.add_argument("--top-k", type=int, default=5, help="Transcript chunks to retrieve (default: 5).")
    args = parser.parse_args()
    if args.top_k < 1:
        parser.error("--top-k must be at least 1")
    query = input("Ask a course question: ").strip()
    if not query:
        parser.error("Please enter a non-empty question.")
    index = load_embeddings()
    print("\n" + answer_question(query, index, top_k=args.top_k))


if __name__ == "__main__":
    main()
