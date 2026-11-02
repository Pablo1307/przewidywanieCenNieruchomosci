import json

import joblib
import numpy as np
import pandas as pd
import pytest

from app.ml.data import load_data
from scripts.train import train


def test_training_artifacts_and_selection(tmp_path, sample_frame):
    # Temporary synthetic input verifies plumbing, not academic model performance.
    data = sample_frame.copy()
    data["SalePrice"] = 100000 + np.arange(len(data)) * 2000
    path = tmp_path / "train.csv"
    data.to_csv(path, index=False)
    result = train(path, tmp_path / "models", tmp_path / "processed")
    expected = min(result["comparison"], key=lambda row: row["cv_mean"]["RMSE"])["model"]
    assert result["selected_model"] == expected
    assert result["train_rows"] == 32
    assert result["test_rows"] == 8
    assert not set(result["split"]["train_indices"]) & set(result["split"]["test_indices"])
    run = tmp_path / "models" / result["version"]
    assert len(pd.read_csv(run / "cv_folds.csv")) == 15
    assert len(pd.read_csv(run / "test.csv")) == 1
    assert json.loads((run / "eda.json").read_text(encoding="utf-8"))["rows"] == 32
    assert (run / "eda.png").is_file()
    model = joblib.load(run / f"{expected}.joblib")
    assert np.isfinite(model.predict(sample_frame.iloc[[0]])).all()


def test_missing_file_is_explained(tmp_path):
    with pytest.raises(FileNotFoundError, match="Pobierz train.csv"):
        load_data(tmp_path / "train.csv")


def test_negative_target_rejected(tmp_path, sample_frame):
    data = sample_frame.copy()
    data["SalePrice"] = -1
    path = tmp_path / "train.csv"
    data.to_csv(path, index=False)
    with pytest.raises(ValueError, match="nieujemne"):
        load_data(path)
