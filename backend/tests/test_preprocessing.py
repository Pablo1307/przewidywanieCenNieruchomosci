import numpy as np
import pytest

from app.ml.pipelines import build_pipeline, metrics


@pytest.mark.parametrize("name", ["LinearRegression", "RandomForestRegressor", "HistGradientBoostingRegressor"])
def test_unknown_category_and_missing_values(name, sample_frame):
    model = build_pipeline(name).fit(sample_frame, np.arange(40) * 1000 + 100000)
    row = sample_frame.iloc[[0]].copy()
    row["Neighborhood"] = "UNKNOWN"
    row["TotalBsmtSF"] = np.nan
    assert np.isfinite(model.predict(row)).all()
    assert isinstance(model.named_steps["preprocess"].transform(row), np.ndarray)


def test_imputation_fits_training_only(sample_frame):
    train = sample_frame.iloc[:30]
    pipeline = build_pipeline("LinearRegression").fit(train, np.arange(30))
    imputer = pipeline.named_steps["preprocess"].named_transformers_["numeric"].named_steps["imputer"]
    before = imputer.statistics_.copy()
    unseen = sample_frame.iloc[30:].copy()
    unseen["LotArea"] = 999999
    pipeline.predict(unseen)
    np.testing.assert_equal(before, imputer.statistics_)
    assert before[3] == train.LotArea.median()


def test_metrics_clip_negative_predictions():
    result = metrics([0, 100], [-50, 100])
    assert result == {"MAE": 0, "RMSE": 0, "R2": 1, "RMSLE": 0}
