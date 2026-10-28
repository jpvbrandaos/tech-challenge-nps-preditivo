"""Regras de qualidade da base tratada, gerada pelo notebook 01."""

import pandas as pd
import pytest

from src.config import PROCESSED_DATA_FILE
from src.features import FEATURE_COLUMNS

MONETARY = ["order_value", "discount_value", "freight_value"]
COUNTS_AND_DAYS = [
    "customer_tenure_months",
    "delivery_time_days",
    "delivery_delay_days",
    "customer_service_contacts",
    "resolution_time_days",
    "complaints_count",
]
AT_LEAST_ONE = ["items_quantity", "delivery_attempts", "payment_installments"]


@pytest.fixture(scope="module")
def processed():
    if not PROCESSED_DATA_FILE.exists():
        pytest.skip("Base tratada ausente: rode o notebook 01 para gerá-la")
    return pd.read_csv(PROCESSED_DATA_FILE)


def test_one_row_per_order_without_missing_values(processed):
    assert processed["order_id"].is_unique
    assert not processed.isna().any().any()
    assert set(FEATURE_COLUMNS) <= set(processed.columns)


def test_original_columns_respect_valid_ranges(processed):
    score = processed["nps_score"]
    assert score.between(0, 10).all()
    assert score.round(1).eq(score).all()
    assert processed["repeat_purchase_30d"].isin([0, 1]).all()
    assert processed["customer_age"].between(18, 100).all()
    assert processed[MONETARY].ge(0).all().all()
    assert processed[COUNTS_AND_DAYS].ge(0).all().all()
    assert processed[AT_LEAST_ONE].ge(1).all().all()


def test_attributes_follow_the_decisions(processed):
    # D-08: com o valor líquido, o desconto é uma fração do preço cheio
    assert processed["discount_pct"].between(0, 1, inclusive="left").all()
    # D-07: a entrega real nunca é mais curta que a previsão
    assert processed["actual_delivery_days"].ge(processed["delivery_time_days"]).all()
    # D-05: o alvo do modelo segue a categoria do NPS
    assert processed["is_detractor"].eq(processed["nps_category"].eq("detrator")).all()
    assert processed["friction_score"].between(0, 4).all()
