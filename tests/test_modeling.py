import json

import numpy as np
import pandas as pd
import pytest
from sklearn.metrics import roc_auc_score

from src.modeling.evaluation import (
    auc_difference,
    calibration_table,
    choose_model,
    cv_splits,
    detractor_auc_from_score,
    error_by_group,
    out_of_fold,
    reference_criteria,
    roc_auc_rows,
)
from src.modeling.models import (
    BOOSTING,
    CANDIDATES,
    CHECKOUT_FEATURES,
    DELIVERY,
    EXCLUDED,
    FEATURE_LABELS,
    FEATURES,
    LINEAR,
    LOGISTIC,
    ORDER,
    PROFILE,
    SERVICE,
    TARGET,
    build_classifier,
    build_regressor,
    with_features,
)
from src.modeling.predict import (
    LONG_DELAY,
    NO_FAILURE,
    SHORT_DELAY,
    daily_list,
    registered_failure,
    risk_of,
)
from src.modeling.train import load_model, save_model, train_model


@pytest.fixture(scope="module")
def orders():
    """Trezentos pedidos simulados, em que o risco de detrator sobe com atraso e reclamações."""
    rng = np.random.default_rng(0)
    n = 300
    data = pd.DataFrame(
        {
            "order_id": np.arange(n),
            "customer_age": rng.integers(18, 70, n),
            "customer_region": rng.choice(["Norte", "Sul", "Sudeste"], n),
            "customer_tenure_months": rng.integers(1, 120, n),
            "order_value": rng.uniform(20, 500, n),
            "items_quantity": rng.integers(1, 5, n),
            "discount_value": rng.uniform(0, 30, n),
            "payment_installments": rng.integers(1, 10, n),
            "freight_value": rng.uniform(5, 40, n),
            "delivery_time_days": rng.integers(2, 12, n),
            "delivery_delay_days": rng.integers(0, 6, n),
            "delivery_attempts": rng.integers(1, 4, n),
            "customer_service_contacts": rng.integers(0, 4, n),
            "resolution_time_days": rng.integers(0, 12, n),
            "complaints_count": rng.integers(0, 6, n),
        }
    )
    logit = -2 + 0.8 * data["delivery_delay_days"] + 0.5 * data["complaints_count"]
    data[TARGET] = (rng.random(n) < 1 / (1 + np.exp(-logit))).astype(int)
    detractor_score = rng.uniform(0, 6.9, n)
    data["nps_score"] = np.where(data[TARGET] == 1, detractor_score, detractor_score + 3.1)
    return data


def test_model_variables_leave_out_target_csat_repurchase_and_ids():
    # D-06: só dados que existem logo após a entrega
    assert not set(FEATURES) & set(EXCLUDED)
    assert TARGET not in FEATURES
    assert FEATURES == PROFILE + ORDER + DELIVERY + SERVICE
    assert len(set(FEATURES)) == len(FEATURES)
    assert set(FEATURE_LABELS) == set(FEATURES)


def test_checkout_scenario_uses_only_profile_and_order():
    # D-04: no checkout ainda não há entrega nem atendimento
    assert set(CHECKOUT_FEATURES) == set(PROFILE + ORDER)
    assert not set(CHECKOUT_FEATURES) & set(DELIVERY + SERVICE)


@pytest.mark.parametrize("kind", CANDIDATES)
def test_candidates_learn_the_risk(orders, kind):
    model = build_classifier(kind).fit(orders[FEATURES], orders[TARGET])
    risk = model.predict_proba(orders[FEATURES])[:, 1]
    assert ((risk >= 0) & (risk <= 1)).all()
    assert roc_auc_score(orders[TARGET], risk) > 0.7


def test_unknown_region_does_not_break_the_prediction(orders):
    model = build_classifier(LOGISTIC).fit(orders[FEATURES], orders[TARGET])
    new_order = orders[FEATURES].head(1).assign(customer_region="Exterior")
    assert model.predict_proba(new_order).shape == (1, 2)


def test_with_features_keeps_the_hyperparameters(orders):
    model = build_classifier(LOGISTIC).set_params(model__C=0.5)
    checkout = with_features(model, CHECKOUT_FEATURES).fit(
        orders[CHECKOUT_FEATURES], orders[TARGET]
    )
    assert checkout.named_steps["model"].C == 0.5
    assert list(checkout.named_steps["prep"].feature_names_in_) == CHECKOUT_FEATURES


def test_out_of_fold_predicts_each_order_once(orders):
    x, y = orders[FEATURES], orders[TARGET]
    splits = cv_splits(x, y)
    assert np.sort(np.concatenate([valid for _, valid in splits])).tolist() == list(range(len(x)))
    risk = out_of_fold(build_classifier(LOGISTIC), x, y, splits)
    assert risk.shape == (len(x),) and ((risk >= 0) & (risk <= 1)).all()
    predicted_score = out_of_fold(build_regressor(LINEAR), x, orders["nps_score"], splits)
    assert detractor_auc_from_score(orders["nps_score"], predicted_score) > 0.6


def test_choose_model_prefers_the_simpler_within_the_margin():
    # D-18: até 0,01 de diferença, vence o mais simples
    assert choose_model({LOGISTIC: 0.800, BOOSTING: 0.805}) == LOGISTIC
    assert choose_model({LOGISTIC: 0.800, BOOSTING: 0.820}) == BOOSTING
    assert choose_model({LOGISTIC: 0.830, BOOSTING: 0.820}) == LOGISTIC


def test_roc_auc_rows_matches_sklearn_with_ties():
    rng = np.random.default_rng(1)
    y = rng.integers(0, 2, size=(3, 200)).astype(float)
    score = rng.integers(0, 5, size=(3, 200)).astype(float)
    expected = [roc_auc_score(y[row], score[row]) for row in range(3)]
    np.testing.assert_allclose(roc_auc_rows(y, score), expected)
    assert np.isnan(roc_auc_rows(np.ones((1, 10)), score[:1, :10]))[0]


def test_auc_difference_detects_a_better_ordering():
    rng = np.random.default_rng(2)
    y = rng.integers(0, 2, 400)
    informative = y + rng.normal(0, 0.8, 400)
    noise = rng.normal(0, 1, 400)
    better = auc_difference(y, informative, noise, n_boot=500)
    assert better["diferença"] > 0 and better["IC inferior"] > 0
    same = auc_difference(y, informative, informative, n_boot=500)
    assert same["diferença"] == same["IC inferior"] == same["IC superior"] == 0


def test_reference_criteria_need_margin_interval_and_pr_auc():
    # D-15: os três critérios precisam ser atendidos juntos
    passing = {"diferença": 0.06, "IC inferior": 0.01, "IC superior": 0.11}
    assert reference_criteria(passing, pr_auc=0.95, reference_pr_auc=0.94).all()
    small_gain = {**passing, "diferença": 0.04}
    assert not reference_criteria(small_gain, pr_auc=0.95, reference_pr_auc=0.94).all()
    uncertain = {**passing, "IC inferior": -0.01}
    assert not reference_criteria(uncertain, pr_auc=0.95, reference_pr_auc=0.94).all()
    assert not reference_criteria(passing, pr_auc=0.93, reference_pr_auc=0.94).all()


def test_error_by_group_compares_predicted_and_observed():
    groups = pd.Series(["a"] * 4 + ["b"] * 4, index=range(10, 18))
    y = [1, 1, 0, 0, 1, 1, 1, 0]
    risk = [0.9, 0.8, 0.2, 0.1, 0.5, 0.5, 0.5, 0.5]
    table = error_by_group(y, risk, groups)
    assert table.loc["a", "pedidos"] == 4
    assert table.loc["a", "ROC-AUC"] == 1
    assert table.loc["b", "% detratores"] == 75
    assert table.loc["b", "diferença (pontos)"] == pytest.approx(-25)


def test_calibration_table_splits_orders_into_equal_bands():
    rng = np.random.default_rng(3)
    risk = rng.uniform(0, 1, 1000)
    y = (rng.uniform(0, 1, 1000) < risk).astype(int)
    table = calibration_table(y, risk)
    assert len(table) == 10 and (table["pedidos"] == 100).all()
    assert table["% previsto"].is_monotonic_increasing
    assert (table["IC inferior"] <= table["% detratores"]).all()


def test_train_model_returns_the_chosen_candidate_fitted(orders):
    model, summary, risk = train_model(orders, n_iter=2)
    assert summary["escolhido"].sum() == 1
    chosen = summary.index[summary["escolhido"]][0]
    assert chosen == choose_model(summary["ROC-AUC"].to_dict())
    assert set(risk) == set(CANDIDATES) and all(len(r) == len(orders) for r in risk.values())
    assert model.predict_proba(orders[FEATURES]).shape == (len(orders), 2)


def test_saved_model_predicts_the_same(orders, tmp_path):
    model, summary, _ = train_model(orders, n_iter=2)
    path = save_model(model, summary, tmp_path / "modelo.joblib")
    np.testing.assert_allclose(
        load_model(path).predict_proba(orders[FEATURES]), model.predict_proba(orders[FEATURES])
    )
    record = json.loads(path.with_suffix(".json").read_text(encoding="utf-8"))
    assert record["variaveis"] == FEATURES
    assert record["modelo"] in CANDIDATES


def test_missing_model_points_to_the_command(tmp_path):
    with pytest.raises(FileNotFoundError, match="python -m src.modeling.train"):
        load_model(tmp_path / "ausente.joblib")


def test_registered_failure_follows_the_impact_order():
    orders = pd.DataFrame(
        {
            "delivery_delay_days": [2, 0, 0, 0],
            "customer_service_contacts": [1, 0, 0, 0],
            "complaints_count": [3, 2, 0, 0],
            "resolution_time_days": [9, 9, 8, 7],
        }
    )
    assert registered_failure(orders).tolist() == [
        "atraso",
        "contato ou reclamação",
        "resolução acima de 7 dias",
        NO_FAILURE,
    ]


def test_daily_list_splits_the_capacity_between_delay_segments():
    orders = pd.DataFrame(
        {
            "order_id": range(10),
            "delivery_delay_days": [5, 3, 4, 3, 0, 1, 2, 0, 1, 2],
            "customer_service_contacts": 0,
            "complaints_count": 1,
            "resolution_time_days": 0,
        }
    )
    risk = np.array([0.9, 0.99, 0.5, 0.8, 0.3, 0.7, 0.6, 0.95, 0.2, 0.4])
    result = daily_list(orders, risk, capacity=0.4).set_index("order_id")
    # Duas vagas por segmento: atraso longo pelos dias de atraso, curto pelo risco
    assert result.index[result["na lista"]].tolist() == [0, 2, 7, 5]
    assert result.loc[[0, 2, 1, 3], "posição"].tolist() == [1, 2, 3, 4]
    assert set(result.loc[[0, 1, 2, 3], "segmento"]) == {LONG_DELAY}
    assert set(result.loc[[4, 5, 6, 7, 8, 9], "segmento"]) == {SHORT_DELAY}
    assert result.loc[7, "falha"] == "contato ou reclamação"


def test_risk_of_requires_the_model_variables(orders):
    model = build_classifier(LOGISTIC).fit(orders[FEATURES], orders[TARGET])
    assert risk_of(model, orders).shape == (len(orders),)
    with pytest.raises(ValueError, match="complaints_count"):
        risk_of(model, orders.drop(columns="complaints_count"))
