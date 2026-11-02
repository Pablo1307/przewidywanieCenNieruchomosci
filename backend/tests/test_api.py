import json

import joblib
import numpy as np
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.ml.pipelines import build_pipeline
from app.services.model_service import ModelService, get_model_service


@pytest.fixture
def client(tmp_path):
    app.dependency_overrides[get_model_service] = lambda: ModelService(tmp_path)
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()


def test_health_and_features(client):
    assert client.get("/api/health").json() == {"status": "ok", "model_ready": False}
    assert "OverallQual" in client.get("/api/features").json()["schema"]["properties"]


@pytest.mark.parametrize("path", ["/api/model/info", "/api/model/metrics", "/api/data/eda"])
def test_missing_model(client, path):
    assert client.get(path).status_code == 503


def test_predict_missing_model(client):
    assert client.post("/api/predict", json={"OverallQual": 7, "GrLivArea": 1500, "YearBuilt": 2000}).status_code == 503


@pytest.mark.parametrize("payload", [{}, {"OverallQual": 11, "GrLivArea": 50, "YearBuilt": 2000}, {"OverallQual": 7, "GrLivArea": -1, "YearBuilt": 2000}, {"OverallQual": 7, "GrLivArea": 50, "YearBuilt": 2000, "SalePrice": 1}, {"OverallQual": 7, "GrLivArea": 50, "YearBuilt": 2000, "YearRemodAdd": 1990}])
def test_validation(client, payload):
    assert client.post("/api/predict", json=payload).status_code == 422


def test_prediction_from_saved_pipeline(client, tmp_path, sample_frame):
    run = tmp_path / "test-version"
    run.mkdir()
    model = build_pipeline("RandomForestRegressor").fit(sample_frame, np.arange(40) * 1000 + 100000)
    joblib.dump(model, run / "RandomForestRegressor.joblib")
    (tmp_path / "current.json").write_text(json.dumps({"version": "test-version", "model_name": "RandomForestRegressor"}))
    (run / "metrics.json").write_text(json.dumps({"version": "test-version", "selected_model": "RandomForestRegressor"}))
    (run / "eda.json").write_text("{}")
    response = client.post("/api/predict", json={"OverallQual": 7, "GrLivArea": 1500, "YearBuilt": 2000})
    assert response.status_code == 200
    assert response.json()["price_usd"] > 0
    assert response.json()["model_version"] == "test-version"


def test_cors(client):
    response = client.options("/api/predict", headers={"Origin": "http://localhost:5173", "Access-Control-Request-Method": "POST"})
    assert response.headers["access-control-allow-origin"] == "http://localhost:5173"


def test_corrupt_artifacts(client, tmp_path):
    (tmp_path / "current.json").write_text("invalid json")
    assert client.get("/api/model/info").status_code == 503
