import numpy as np
import pandas as pd

from app.ml.pipelines import FEATURES, NUMERIC


def load_data(path):
    if not path.is_file():
        raise FileNotFoundError(f"Brak {path}. Pobierz train.csv z Kaggle zgodnie z README.md.")
    frame = pd.read_csv(path)
    missing = set(FEATURES + ["SalePrice"]) - set(frame.columns)
    if missing:
        raise ValueError(f"Brak wymaganych kolumn: {sorted(missing)}")
    if len(frame) < 30:
        raise ValueError("Za mało wierszy do podziału i walidacji 5-fold (minimum 30).")
    for name in NUMERIC + ["SalePrice"]:
        frame[name] = pd.to_numeric(frame[name], errors="raise")
        if np.isinf(frame[name].to_numpy()).any():
            raise ValueError(f"Nieskończone wartości w kolumnie {name}.")
    if frame.SalePrice.isna().any() or (frame.SalePrice < 0).any():
        raise ValueError("SalePrice musi zawierać nieujemne liczby bez braków.")
    return frame
