import tempfile
import unittest
from pathlib import Path

import pandas as pd

from train import load_data


class HeartDiseaseDataTests(unittest.TestCase):
    def make_frame(self, targets=(0, 1, 0, 1)):
        rows = []
        for i, target in enumerate(targets):
            rows.append({
                "Age": 40 + i, "RestingBP": 120, "Cholesterol": 200,
                "FastingBS": 0, "MaxHR": 150, "Oldpeak": 0.5,
                "Sex": "M", "ChestPainType": "ATA", "RestingECG": "Normal",
                "ExerciseAngina": "N", "ST_Slope": "Up", "HeartDisease": target,
            })
        return pd.DataFrame(rows)

    def test_rejects_dataset_with_only_one_target_class(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "heart.csv"
            self.make_frame((0, 0, 0, 0)).to_csv(path, index=False)
            with self.assertRaisesRegex(ValueError, "both classes"):
                load_data(path)

    def test_rejects_class_with_only_one_row(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "heart.csv"
            self.make_frame((0, 0, 0, 1)).to_csv(path, index=False)
            with self.assertRaisesRegex(ValueError, "at least two rows"):
                load_data(path)

    def test_zero_measurements_become_missing(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "heart.csv"
            frame = self.make_frame()
            frame.loc[0, "RestingBP"] = 0
            frame.loc[1, "Cholesterol"] = 0
            frame.to_csv(path, index=False)
            result = load_data(path)
            self.assertTrue(pd.isna(result.loc[0, "RestingBP"]))
            self.assertTrue(pd.isna(result.loc[1, "Cholesterol"]))

    def test_rejects_unexpected_target_labels(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "heart.csv"
            self.make_frame((0, 1, 0, 1)).assign(HeartDisease=[0, 1, 2, 1]).to_csv(path, index=False)
            with self.assertRaisesRegex(ValueError, "invalid labels"):
                load_data(path)

    def test_infinite_measurements_are_treated_as_missing(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "heart.csv"
            frame = self.make_frame()
            frame["RestingBP"] = frame["RestingBP"].astype(float)
            frame.loc[0, "RestingBP"] = float("inf")
            frame.to_csv(path, index=False)
            result = load_data(path)
            self.assertTrue(pd.isna(result.loc[0, "RestingBP"]))


if __name__ == "__main__":
    unittest.main()
