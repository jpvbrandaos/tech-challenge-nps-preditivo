import pandas as pd
import pytest

from src.split import TEST, TRAIN, split_train_test


@pytest.fixture
def orders():
    """Mil pedidos, 30% deles de detratores."""
    return pd.DataFrame({"is_detractor": [1] * 300 + [0] * 700})


def test_split_reserves_a_fifth_for_test(orders):
    split = split_train_test(orders)
    assert set(split.unique()) == {TRAIN, TEST}
    assert (split == TEST).sum() == 200


def test_split_keeps_the_detractor_share_in_both_sides(orders):
    split = split_train_test(orders)
    assert orders.loc[split == TRAIN, "is_detractor"].mean() == pytest.approx(0.3)
    assert orders.loc[split == TEST, "is_detractor"].mean() == pytest.approx(0.3)


def test_split_is_the_same_on_every_run(orders):
    pd.testing.assert_series_equal(split_train_test(orders), split_train_test(orders))
