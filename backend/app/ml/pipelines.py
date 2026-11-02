import numpy as np
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingRegressor, RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, mean_squared_log_error, r2_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

NUMERIC = ["OverallQual", "GrLivArea", "YearBuilt", "LotArea", "TotalBsmtSF", "GarageCars", "FullBath", "BedroomAbvGr", "TotRmsAbvGrd", "YearRemodAdd"]
CATEGORICAL = ["Neighborhood", "HouseStyle", "BldgType"]
FEATURES = NUMERIC + CATEGORICAL


def build_pipeline(name):
    estimators = {
        "LinearRegression": LinearRegression(),
        "RandomForestRegressor": RandomForestRegressor(n_estimators=300, min_samples_leaf=2, random_state=42, n_jobs=1),
        "HistGradientBoostingRegressor": HistGradientBoostingRegressor(max_iter=200, learning_rate=0.08, random_state=42, early_stopping=False),
    }
    numeric_steps = [("imputer", SimpleImputer(strategy="median", keep_empty_features=True))]
    if name == "LinearRegression":
        numeric_steps.append(("scaler", StandardScaler()))
    categorical = Pipeline([
        ("imputer", SimpleImputer(strategy="constant", fill_value="Missing", keep_empty_features=True)),
        # Dense output also works with HistGradientBoosting; only 3 categorical features.
        ("encoder", OneHotEncoder(handle_unknown="ignore", sparse_output=False, drop="first" if name == "LinearRegression" else None)),
    ])
    preprocess = ColumnTransformer([
        ("numeric", Pipeline(numeric_steps), NUMERIC),
        ("categorical", categorical, CATEGORICAL),
    ], sparse_threshold=0)
    return Pipeline([("preprocess", preprocess), ("regressor", estimators[name])])


def rmsle(y_true, y_pred):
    return float(np.sqrt(mean_squared_log_error(y_true, np.maximum(0, y_pred))))


def metrics(y_true, y_pred):
    # Same nonnegative price policy in CV, test and API.
    predicted = np.maximum(0, y_pred)
    return {
        "MAE": float(mean_absolute_error(y_true, predicted)),
        "RMSE": float(np.sqrt(mean_squared_error(y_true, predicted))),
        "R2": float(r2_score(y_true, predicted)),
        "RMSLE": rmsle(y_true, predicted),
    }
