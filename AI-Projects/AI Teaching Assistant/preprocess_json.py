"""Build a searchable transcript index using local Ollama embeddings."""
import json
import logging
import os
from pathlib import Path
import tempfile

import joblib
import pandas as pd
import requests

OLLAMA_URL = "http://localhost:11434"
EMBED_MODEL = "bge-m3"
BATCH_SIZE = 64
logger = logging.getLogger(__name__)


def create_embedding(text_list):
    """Create embeddings for a non-empty batch of transcript text."""
    if not text_list or any(not isinstance(text, str) or not text.strip() for text in text_list):
        raise ValueError("Embedding input must contain non-empty text strings.")

    try:
        response = requests.post(
            f"{OLLAMA_URL}/api/embed",
            json={"model": EMBED_MODEL, "input": text_list},
            timeout=(10, 180),
        )
        response.raise_for_status()
        payload = response.json()
    except requests.RequestException as exc:
        raise RuntimeError(
            "Could not reach Ollama. Start Ollama and pull the bge-m3 model."
        ) from exc
    except ValueError as exc:
        raise RuntimeError("Ollama returned an invalid JSON response.") from exc

    embeddings = payload.get("embeddings") if isinstance(payload, dict) else None
    if not isinstance(embeddings, list) or len(embeddings) != len(text_list):
        raise RuntimeError("Ollama returned an unexpected number of embeddings.")
    if any(not isinstance(vector, list) or not vector for vector in embeddings):
        raise RuntimeError("Ollama returned an empty or invalid embedding.")
    return embeddings


def build_index(json_dir="jsons", output_path="embeddings.joblib", batch_size=BATCH_SIZE):
    """Read transcript JSON files, embed chunks in batches and save atomically."""
    json_dir = Path(json_dir)
    output_path = Path(output_path)
    if not isinstance(batch_size, int) or batch_size < 1:
        raise ValueError("batch_size must be a positive integer.")
    if not json_dir.is_dir():
        raise FileNotFoundError(f"Transcript directory not found: {json_dir}")

    chunks = []
    for json_path in sorted(json_dir.glob("*.json")):
        try:
            with json_path.open(encoding="utf-8") as source:
                payload = json.load(source)
        except (OSError, json.JSONDecodeError) as exc:
            raise ValueError(f"Could not read transcript file: {json_path.name}") from exc

        file_chunks = payload.get("chunks") if isinstance(payload, dict) else None
        if not isinstance(file_chunks, list):
            raise ValueError(f"{json_path.name} must contain a 'chunks' list.")
        for chunk in file_chunks:
            if not isinstance(chunk, dict) or not isinstance(chunk.get("text"), str):
                raise ValueError(f"{json_path.name} contains a chunk without valid text.")
            if chunk["text"].strip():
                chunks.append(dict(chunk))

    if not chunks:
        raise ValueError(f"No transcript chunks found in {json_dir}.")

    for start in range(0, len(chunks), batch_size):
        batch = chunks[start:start + batch_size]
        vectors = create_embedding([chunk["text"] for chunk in batch])
        for chunk, vector in zip(batch, vectors):
            chunk["embedding"] = vector
            chunk["chunk_id"] = len(
                [item for item in chunks[:start] if "embedding" in item]
            ) + batch.index(chunk)

    frame = pd.DataFrame.from_records(chunks)
    if frame.empty or frame["embedding"].isna().any():
        raise RuntimeError("Index creation produced missing embeddings.")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = None
    try:
        with tempfile.NamedTemporaryFile(
            dir=output_path.parent,
            prefix=output_path.name + ".",
            suffix=".tmp",
            delete=False,
        ) as temporary:
            temporary_path = Path(temporary.name)
        joblib.dump(frame, temporary_path)
        os.replace(temporary_path, output_path)
    finally:
        if temporary_path is not None and temporary_path.exists():
            temporary_path.unlink()

    logger.info("Saved %s transcript chunks to %s.", len(frame), output_path)
    return frame


def main():
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    build_index()


if __name__ == "__main__":
    main()
