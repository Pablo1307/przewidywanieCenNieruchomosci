import numpy as np
import pandas as pd
import pytest

from app.ml.pipelines import FEATURES, NUMERIC


@pytest.fixture
def sample_frame():
    # Synthetic unit-test fixture only; never exported as experiment results.
    frame = pd.DataFrame({name: np.arange(40, dtype=float) + 1 for name in NUMERIC})
    frame["Neighborhood"] = ["NAmes", "CollgCr"] * 20
    frame["HouseStyle"] = "1Story"
    frame["BldgType"] = "1Fam"
    frame.loc[0, "LotArea"] = np.nan
    return frame[FEATURES]
