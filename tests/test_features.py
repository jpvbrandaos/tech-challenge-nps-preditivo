import pandas as pd
import pytest

from src.features import FEATURE_COLUMNS, build_features, classify_nps


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


@pytest.fixture
def orders():
    """Dois pedidos: o primeiro acumula todas as falhas, o segundo nenhuma."""
    return pd.DataFrame(
        {
            "customer_age": [24, 55],
            "customer_tenure_months": [12, 61],
            "order_value": [27.48, 500.00],
            "items_quantity": [1, 4],
            "discount_value": [35.83, 25.00],
            "delivery_time_days": [2, 10],
            "delivery_delay_days": [3, 0],
            "freight_value": [20.00, 40.00],
            "delivery_attempts": [2, 1],
            "customer_service_contacts": [1, 0],
            "resolution_time_days": [8, 7],
            "nps_score": [6.9, 9.0],
        }
    )


def test_features_keep_orders_and_original_columns(orders):
    features = build_features(orders)
    assert len(features) == len(orders)
    pd.testing.assert_frame_equal(features[orders.columns], orders)
    assert list(features.columns) == [*orders.columns, *FEATURE_COLUMNS]


def test_actual_delivery_adds_delay_to_forecast(orders):
    # D-07: o tempo de entrega é a previsão, e o atraso conta os dias além dela
    assert build_features(orders)["actual_delivery_days"].tolist() == [5, 10]


def test_discount_share_stays_below_one_when_discount_exceeds_order_value(orders):
    # D-08: o valor do pedido já vem com o desconto, então o preço cheio é a soma dos dois
    share = build_features(orders)["discount_pct"]
    assert share.iloc[0] == pytest.approx(35.83 / (27.48 + 35.83))
    assert share.lt(1).all()


def test_friction_counts_delay_extra_attempt_contact_and_long_resolution(orders):
    # Resolução em exatamente 7 dias não conta como longa
    assert build_features(orders)["friction_score"].tolist() == [4, 0]


def test_detractor_flag_follows_nps_category(orders):
    features = build_features(orders)
    assert features["is_detractor"].tolist() == [1, 0]
    assert features["nps_category"].astype(str).tolist() == ["detrator", "promotor"]


@pytest.mark.parametrize(
    ("delay", "bucket"),
    [
        (0, "sem atraso"),
        (1, "1 a 2 dias"),
        (2, "1 a 2 dias"),
        (4, "3 a 4 dias"),
        (5, "5 dias ou mais"),
    ],
)
def test_delay_buckets_close_on_the_right(orders, delay, bucket):
    orders["delivery_delay_days"] = delay
    assert build_features(orders)["delay_bucket"].iloc[0] == bucket


def test_tenure_and_age_buckets_include_the_upper_limit(orders):
    features = build_features(orders)
    assert features["tenure_bucket"].astype(str).tolist() == ["até 1 ano", "mais de 5 anos"]
    assert features["age_bucket"].astype(str).tolist() == ["18 a 24", "55 ou mais"]
