import json

import joblib
import pytest

import preprocess_json


def write_transcript(folder, filename, chunks):
    folder.mkdir(parents=True, exist_ok=True)
    (folder / filename).write_text(
        json.dumps({"chunks": chunks}),
        encoding="utf-8",
    )


def test_build_index_batches_chunks_and_assigns_unique_ids(tmp_path, monkeypatch):
    source = tmp_path / "jsons"
    output = tmp_path / "index" / "embeddings.joblib"
    write_transcript(source, "lesson.json", [
        {"title": "Lesson", "number": "1", "start": 0, "end": 1, "text": "first"},
        {"title": "Lesson", "number": "1", "start": 1, "end": 2, "text": "second"},
        {"title": "Lesson", "number": "1", "start": 2, "end": 3, "text": "third"},
    ])

    calls = []

    def fake_embed(texts):
        calls.append(list(texts))
        return [[float(len(calls)), float(i)] for i, _ in enumerate(texts)]

    monkeypatch.setattr(preprocess_json, "create_embedding", fake_embed)
    result = preprocess_json.build_index(source, output, batch_size=2)

    assert calls == [["first", "second"], ["third"]]
    assert result["chunk_id"].tolist() == [0, 1, 2]
    assert output.exists()
    saved = joblib.load(output)
    assert saved["text"].tolist() == ["first", "second", "third"]
    assert len(saved["embedding"]) == 3


def test_build_index_rejects_empty_transcript_directory(tmp_path):
    source = tmp_path / "jsons"
    source.mkdir()

    with pytest.raises(ValueError, match="No transcript chunks"):
        preprocess_json.build_index(source, tmp_path / "index.joblib")


def test_build_index_rejects_malformed_chunk_before_embedding(tmp_path, monkeypatch):
    source = tmp_path / "jsons"
    write_transcript(source, "bad.json", [{"title": "Missing text"}])
    monkeypatch.setattr(
        preprocess_json,
        "create_embedding",
        lambda texts: pytest.fail("Embedding should not be requested"),
    )

    with pytest.raises(ValueError, match="without valid text"):
        preprocess_json.build_index(source, tmp_path / "index.joblib")


def test_create_embedding_checks_response_count(monkeypatch):
    class Response:
        def raise_for_status(self):
            pass

        def json(self):
            return {"embeddings": [[0.1, 0.2]]}

    monkeypatch.setattr(preprocess_json.requests, "post", lambda *args, **kwargs: Response())

    with pytest.raises(RuntimeError, match="unexpected number"):
        preprocess_json.create_embedding(["one", "two"])
