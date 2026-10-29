import numpy as np
import pandas as pd
import pytest
from sklearn.tree import DecisionTreeClassifier

from src.analysis import (
    CONFIRMED,
    INCONCLUSIVE,
    REFUTED,
    breakpoint_test,
    counterfactual_nps,
    estimate_contrast,
    excess_over_additive,
    factor_ranking,
    failure_flags,
    invert_verdict,
    nps_gain,
    nps_of,
    problem_impact,
    ranking_metrics,
    rate_table,
    standardized_share,
    tree_leaves,
    verdict_adjustment,
    verdict_breakpoint,
    verdict_effect,
    verdict_share,
    within_strata,
)

CATEGORY = {1: "detrator", 0: "promotor"}


def make_orders(groups: dict[str, list[int]]) -> pd.DataFrame:
    """Pedidos por grupo, cada um com a lista de alvos 0 ou 1."""
    rows = [(group, target) for group, targets in groups.items() for target in targets]
    data = pd.DataFrame(rows, columns=["group", "is_detractor"])
    data["nps_category"] = data["is_detractor"].map(CATEGORY)
    return data


def test_nps_is_promoters_minus_detractors():
    categories = pd.Series(["promotor", "promotor", "neutro", "detrator"])
    assert nps_of(categories) == pytest.approx(25.0)


def test_rate_table_counts_and_wraps_each_share_in_its_interval():
    data = make_orders({"a": [1] * 30 + [0] * 10, "b": [1] * 5 + [0] * 35})
    table = rate_table(data, "group")
    assert table["pedidos"].tolist() == [40, 40]
    assert table["% detratores"].tolist() == pytest.approx([75.0, 12.5])
    assert (table["IC inferior"] < table["% detratores"]).all()
    assert (table["% detratores"] < table["IC superior"]).all()
    assert table["NPS"].tolist() == pytest.approx([-50.0, 75.0])


def test_failure_flags_count_resolution_above_a_week():
    data = pd.DataFrame(
        {
            "is_late": [1, 0],
            "multiple_attempts": [0, 1],
            "had_contact": [1, 0],
            "resolution_time_days": [8, 7],
        }
    )
    assert failure_flags(data).iloc[:, 3].tolist() == [1, 0]


def test_problem_impact_is_the_ratio_of_detractor_shares():
    data = pd.DataFrame({"is_detractor": [1, 1, 1, 0, 1, 0, 0, 0]})
    flags = pd.DataFrame({"falha": [1, 1, 1, 1, 0, 0, 0, 0]})
    row = problem_impact(data, flags).loc["falha"]
    assert row["% detratores com"] == pytest.approx(75.0)
    assert row["% detratores sem"] == pytest.approx(25.0)
    assert row["impacto"] == pytest.approx(3.0)
    assert row["presença entre detratores (%)"] == pytest.approx(75.0)


def test_factor_ranking_orders_by_effect_size_and_adjusts_p_values():
    data = make_orders({"a": [1] * 40 + [0] * 10, "b": [1] * 10 + [0] * 40})
    data["noise"] = np.tile(["x", "y"], 50)
    ranking = factor_ranking(data, {"grupo": data["group"], "ruído": data["noise"]})
    assert ranking.index.tolist() == ["grupo", "ruído"]
    assert ranking.loc["grupo", "diferença (pontos)"] == pytest.approx(60.0)
    assert ranking["V de Cramér"].between(0, 1).all()


def test_standardized_share_removes_the_effect_of_composition():
    # Mesma taxa por estrato nos dois grupos; só a composição muda
    data = pd.DataFrame(
        {
            "group": ["a"] * 10 + ["b"] * 10,
            "stratum": ["s1"] * 8 + ["s2"] * 2 + ["s1"] * 2 + ["s2"] * 8,
            "is_detractor": [1] * 8 + [0] * 2 + [1] * 2 + [0] * 8,
        }
    )
    adjusted = standardized_share(data, "group", "stratum")
    assert adjusted["a"] == pytest.approx(adjusted["b"])


def test_contrast_estimates_the_difference_and_its_uncertainty():
    data = make_orders({"a": [1] * 80 + [0] * 20, "b": [1] * 40 + [0] * 60})
    result = estimate_contrast(data, ["group == 'a'", "group == 'b'"], [1, -1], n_boot=500)
    assert result["efeito"] == pytest.approx(40.0)
    assert result["IC inferior"] < 40.0 < result["IC superior"]
    assert result["p-valor"] < 0.01
    assert result["menor grupo"] == 100


def test_excess_over_additive_detects_failures_that_compound():
    rng = np.random.default_rng(0)
    flags = pd.DataFrame(rng.integers(0, 2, size=(4000, 2)), columns=["f1", "f2"])
    both = flags.sum(axis=1) == 2
    probability = np.where(both, 0.9, 0.3)
    data = pd.DataFrame({"is_detractor": rng.random(4000) < probability}).astype(int)
    assert excess_over_additive(data, flags) > 5


def test_breakpoint_test_prefers_the_cut_when_risk_jumps():
    days = np.repeat(np.arange(9), 200)
    data = pd.DataFrame({"days": days, "is_detractor": (days >= 4).astype(int)})
    data.loc[data.index % 10 == 0, "is_detractor"] = 1 - data["is_detractor"]
    result = breakpoint_test(data, "days")
    assert result["a partir de"] == 4
    assert result["ganho"] > 2


def test_tree_leaves_cover_every_order_with_readable_rules():
    x = pd.DataFrame({"days": np.repeat(np.arange(9), 20)})
    y = pd.Series((x["days"] >= 4).astype(int))
    tree = DecisionTreeClassifier(max_depth=1).fit(x, y)
    leaves = tree_leaves(tree, x, y)
    assert leaves["pedidos"].sum() == len(x)
    assert leaves["regra"].tolist() == ["days ≥ 4", "days ≤ 3"]


def test_ranking_metrics_reward_a_perfect_order():
    y = np.array([1] * 30 + [0] * 70)
    perfect = ranking_metrics(y, y)
    assert perfect["PR-AUC"] == pytest.approx(1.0)
    assert perfect["precisão no topo"] == pytest.approx(1.0)
    assert perfect["captura no topo"] == pytest.approx(20 / 30)
    naive = ranking_metrics(y, np.zeros(100))
    assert naive["PR-AUC"] == pytest.approx(0.3)


@pytest.mark.parametrize(
    ("estimate", "low", "high", "p_adjusted", "smallest", "expected"),
    [
        (8.0, 3.0, 13.0, 0.01, 100, CONFIRMED),
        (8.0, -1.0, 17.0, 0.20, 100, INCONCLUSIVE),
        (2.0, -1.0, 4.5, 0.30, 100, REFUTED),
        (-3.0, -6.0, -0.5, 0.04, 100, REFUTED),
        (8.0, 3.0, 13.0, 0.01, 20, INCONCLUSIVE),
    ],
)
def test_verdict_effect_follows_the_fixed_rule(
    estimate, low, high, p_adjusted, smallest, expected
):
    assert verdict_effect(estimate, low, high, p_adjusted, smallest) == expected


def test_other_verdict_rules():
    assert invert_verdict(CONFIRMED) == REFUTED
    assert invert_verdict(INCONCLUSIVE) == INCONCLUSIVE
    assert verdict_share(low=12.0, high=20.0, minimum=10.0) == CONFIRMED
    assert verdict_share(low=2.0, high=8.0, minimum=10.0) == REFUTED
    assert verdict_breakpoint(5.0) == CONFIRMED
    assert verdict_breakpoint(-3.0) == REFUTED
    assert verdict_breakpoint(0.5) == INCONCLUSIVE
    assert verdict_adjustment(p_crude=0.01, p_adjusted=0.30) == CONFIRMED
    assert verdict_adjustment(p_crude=0.01, p_adjusted=0.01) == REFUTED
    assert verdict_adjustment(p_crude=0.40, p_adjusted=0.50) == INCONCLUSIVE


def test_counterfactual_nps_swaps_the_mix_of_the_affected_orders():
    data = make_orders({"late": [1] * 10, "on_time": [0] * 10})
    affected = data["group"] == "late"
    assert nps_of(data["nps_category"]) == pytest.approx(0.0)
    assert counterfactual_nps(data, affected, ~affected) == pytest.approx(100.0)


def test_nps_gain_is_the_change_from_the_current_nps():
    data = make_orders({"late": [1] * 10, "on_time": [0] * 10})
    assert nps_gain(data, "group == 'late'", "group == 'on_time'") == pytest.approx(100.0)


def test_breakpoint_test_charges_the_chosen_cut_as_a_parameter():
    # Risco que cresce aos poucos, sem salto: o corte não compensa o parâmetro a mais
    days = np.repeat(np.arange(9), 300)
    rng = np.random.default_rng(1)
    data = pd.DataFrame({"days": days, "is_detractor": rng.random(len(days)) < 0.1 + 0.08 * days})
    data["is_detractor"] = data["is_detractor"].astype(int)
    assert breakpoint_test(data, "days")["ganho"] < 2


def test_within_strata_removes_the_effect_of_the_stratum():
    # Exposição concentrada no estrato a; dentro de cada estrato, o risco não muda com ela
    data = make_orders(
        {
            "a1": [1] * 80 + [0] * 20,
            "a0": [1] * 8 + [0] * 2,
            "b1": [1] * 2 + [0] * 8,
            "b0": [1] * 20 + [0] * 80,
        }
    )
    data["stratum"], data["exposed"] = data["group"].str[0], data["group"].str[1].astype(int)
    groups, weights = within_strata(
        data, "exposed == 1", "exposed == 0", ["stratum == 'a'", "stratum == 'b'"]
    )
    assert weights == pytest.approx([0.5, -0.5, 0.5, -0.5])
    crude = estimate_contrast(data, ["exposed == 1", "exposed == 0"], [1, -1], n_boot=200)
    adjusted = estimate_contrast(data, groups, weights, n_boot=200)
    assert crude["efeito"] > 40
    assert adjusted["efeito"] == pytest.approx(0.0)
