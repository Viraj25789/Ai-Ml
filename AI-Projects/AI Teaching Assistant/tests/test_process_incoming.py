import unittest
from unittest.mock import patch

import numpy as np
import pandas as pd

from process_incoming import build_prompt, load_embeddings, retrieve


class RetrievalTests(unittest.TestCase):
    def setUp(self):
        self.frame = pd.DataFrame([
            {"title": "HTML Basics", "number": "1", "start": 10, "end": 20,
             "text": "HTML structures a web page", "embedding": [1.0, 0.0]},
            {"title": "CSS Basics", "number": "2", "start": 30, "end": 40,
             "text": "CSS styles a web page", "embedding": [0.0, 1.0]},
        ])

    @patch("process_incoming.create_embedding", return_value=np.array([1.0, 0.0]))
    def test_retrieve_ranks_most_similar_chunk_first(self, _):
        result = retrieve(self.frame, "What is HTML?")
        self.assertEqual(result.iloc[0]["title"], "HTML Basics")
        self.assertGreater(result.iloc[0]["similarity"], result.iloc[1]["similarity"])

    def test_prompt_requires_grounded_answers(self):
        prompt = build_prompt("Where is HTML explained?", self.frame.iloc[[0]])
        self.assertIn("Never invent", prompt)
        self.assertIn("HTML Basics", prompt)
        self.assertIn("Where is HTML explained?", prompt)

    def test_load_rejects_missing_index(self):
        with self.assertRaises(FileNotFoundError):
            load_embeddings("this-index-does-not-exist.joblib")


if __name__ == "__main__":
    unittest.main()
