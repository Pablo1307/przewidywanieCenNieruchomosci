"""Run from backend: python -m scripts.train"""
import argparse
import hashlib
import json
import platform
from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import sklearn
from sklearn.model_selection import KFold, train_test_split

from app.config import DATA_DIR, MODEL_DIR
from app.ml.data import load_data
from app.ml.eda import analyze
from app.ml.pipelines import FEATURES, build_pipeline, metrics

MODEL_NAMES = ["LinearRegression", "RandomForestRegressor", "HistGradientBoostingRegressor"]


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False), encoding="utf-8")


def train(data_path, model_dir, output_dir):
    frame = load_data(data_path)
    train_frame, test_frame = train_test_split(frame, test_size=0.2, random_state=42)
    X, y = train_frame[FEATURES], train_frame.SalePrice
    cv = KFold(n_splits=5, shuffle=True, random_state=42)
    comparisons, pipelines, fold_rows = [], {}, []
    for name in MODEL_NAMES:
        scores = []
        for fold, (fit_idx, val_idx) in enumerate(cv.split(X), start=1):
            pipeline = build_pipeline(name)
            pipeline.fit(X.iloc[fit_idx], y.iloc[fit_idx])
            score = metrics(y.iloc[val_idx], pipeline.predict(X.iloc[val_idx]))
            scores.append(score)
            fold_rows.append({"model": name, "fold": fold, **score})
        summary = {key: float(np.mean([row[key] for row in scores])) for key in scores[0]}
        std = {key: float(np.std([row[key] for row in scores], ddof=1)) for key in scores[0]}
        comparisons.append({"model": name, "cv_mean": summary, "cv_std": std})
        pipeline = build_pipeline(name)
        pipeline.fit(X, y)
        pipelines[name] = pipeline
        print(f"{name}: CV RMSE = {summary['RMSE']:.2f} USD", flush=True)
    best_name = min(comparisons, key=lambda row: row["cv_mean"]["RMSE"])["model"]
    # The test partition is evaluated once, for the CV winner only.
    test_metrics = metrics(test_frame.SalePrice, pipelines[best_name].predict(test_frame[FEATURES]))
    version = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    run_dir = model_dir / version
    run_dir.mkdir(parents=True, exist_ok=False)
    output_dir.mkdir(parents=True, exist_ok=True)
    result = {
        "version": version, "selected_model": best_name, "selection_metric": "minimum mean CV RMSE",
        "currency": "USD", "dataset": "Kaggle House Prices / Ames, Iowa", "features": FEATURES,
        "train_rows": len(X), "test_rows": len(test_frame), "random_state": 42, "folds": 5,
        "data_sha256": hashlib.sha256(data_path.read_bytes()).hexdigest(),
        "environment": {"python": platform.python_version(), "scikit_learn": sklearn.__version__, "numpy": np.__version__, "pandas": pd.__version__, "joblib": joblib.__version__},
        "parameters": {name: pipeline.named_steps["regressor"].get_params() for name, pipeline in pipelines.items()},
        "comparison": comparisons, "test": test_metrics,
        "split": {"train_indices": train_frame.index.tolist(), "test_indices": test_frame.index.tolist()},
    }
    for name, pipeline in pipelines.items():
        joblib.dump(pipeline, run_dir / f"{name}.joblib")
    write_json(run_dir / "metrics.json", result)
    eda = analyze(train_frame, run_dir)
    write_json(run_dir / "eda.json", eda)
    pd.DataFrame(fold_rows).to_csv(run_dir / "cv_folds.csv", index=False)
    pd.DataFrame([{"model": row["model"], **row["cv_mean"], **{f"{key}_std": value for key, value in row["cv_std"].items()}} for row in comparisons]).to_csv(run_dir / "comparison.csv", index=False)
    pd.DataFrame([{"model": best_name, **test_metrics}]).to_csv(run_dir / "test.csv", index=False)
    write_json(output_dir / "split.json", result["split"])
    # Switch only after all artifacts are complete. Existing API processes need a restart.
    temporary = model_dir / "current.tmp"
    write_json(temporary, {"version": version, "model_name": best_name})
    temporary.replace(model_dir / "current.json")
    print(f"Zapisano {run_dir}. Wybrano {best_name}. Test: {test_metrics}")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Trening i porównanie trzech modeli cen domów")
    parser.add_argument("--data", type=Path, default=DATA_DIR / "raw" / "train.csv")
    parser.add_argument("--models", type=Path, default=MODEL_DIR)
    parser.add_argument("--output", type=Path, default=DATA_DIR / "processed")
    args = parser.parse_args()
    try:
        train(args.data, args.models, args.output)
    except (FileNotFoundError, ValueError) as error:
        parser.exit(1, f"Błąd: {error}\n")
