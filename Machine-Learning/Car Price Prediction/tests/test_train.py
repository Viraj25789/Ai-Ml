import tempfile
import unittest
from pathlib import Path

import pandas as pd

from train import build_pipeline, evaluate, load_data


class CarPricePipelineTests(unittest.TestCase):
    def test_pipeline_fits_and_predicts_unseen_categories(self):
        frame = pd.DataFrame({
            "year": [2017, 2018, 2019, 2016, 2020, 2015],
            "mileage": [30000, 20000, 10000, 45000, 5000, 60000],
            "tax": [145, 150, 145, 125, 150, 0],
            "mpg": [55.0, 50.0, 60.0, 45.0, 62.0, 40.0],
            "engineSize": [1.0, 1.5, 1.0, 2.0, 1.2, 1.6],
            "model": ["Fiesta", "Focus", "Fiesta", "Kuga", "Puma", "Focus"],
            "transmission": ["Manual", "Automatic", "Manual", "Manual", "Automatic", "Manual"],
            "fuelType": ["Petrol", "Diesel", "Petrol", "Diesel", "Petrol", "Diesel"],
        })
        target = pd.Series([9000, 12000, 14000, 8000, 18000, 6500])
        model = build_pipeline().fit(frame.iloc[:5], target.iloc[:5])
        prediction = model.predict(pd.DataFrame([{
            **frame.iloc[5].to_dict(), "model": "New Model"
        }]))
        self.assertEqual(len(prediction), 1)
        self.assertGreater(float(prediction[0]), 0)

    def test_load_data_checks_required_columns(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "bad.csv"
            pd.DataFrame({"price": [1000]}).to_csv(path, index=False)
            with self.assertRaisesRegex(ValueError, "missing required columns"):
                load_data(path)

    def test_load_data_coerces_numeric_features_and_drops_invalid_targets(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "cars.csv"
            frame = pd.DataFrame({
                "year": ["2018", "not-a-year"],
                "mileage": ["12000", "bad"],
                "tax": ["145", "145"],
                "mpg": ["55.0", "50.0"],
                "engineSize": ["1.0", "1.2"],
                "model": ["Fiesta", "Focus"],
                "transmission": ["Manual", "Manual"],
                "fuelType": ["Petrol", "Petrol"],
                "price": ["9000", "-1"],
            })
            frame.to_csv(path, index=False)
            result = load_data(path)
            self.assertEqual(len(result), 1)
            self.assertEqual(result.iloc[0]["mileage"], 12000)

    def test_metrics_include_mae_rmse_and_r2(self):
        result = evaluate([100, 200, 300, 400], [110, 190, 310, 390], 2)
        self.assertEqual(set(result), {"mae", "rmse", "r2", "adjusted_r2"})
        self.assertGreater(result["mae"], 0)
        self.assertIsNotNone(result["adjusted_r2"])

    def test_load_data_treats_infinite_features_as_missing_and_drops_infinite_prices(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "cars.csv"
            frame = pd.DataFrame({
                "year": [2018, 2019],
                "mileage": [12000, float("inf")],
                "tax": [145, 145],
                "mpg": [55.0, 50.0],
                "engineSize": [1.0, 1.2],
                "model": ["Fiesta", "Focus"],
                "transmission": ["Manual", "Manual"],
                "fuelType": ["Petrol", "Petrol"],
                "price": [9000, float("inf")],
            })
            frame.to_csv(path, index=False)
            result = load_data(path)
            self.assertEqual(len(result), 1)
            self.assertTrue(pd.isna(result.iloc[0]["mileage"]))


if __name__ == "__main__":
    unittest.main()
