import pandas as pd
import pytest

from src.features import classify_nps


@pytest.mark.parametrize(
    ("score", "category"),
    [
        (0.0, "detrator"),
        (6.9, "detrator"),
        (7.0, "neutro"),
        (8.9, "neutro"),
        (9.0, "promotor"),
        (10.0, "promotor"),
    ],
)
def test_nps_bands_without_rounding(score, category):
    assert classify_nps(pd.Series([score])).iloc[0] == category
