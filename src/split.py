"""Separação de treino e teste da base tratada (D-11)."""

import pandas as pd
from sklearn.model_selection import train_test_split

from src.config import RANDOM_SEED, TEST_SIZE

TRAIN = "treino"
TEST = "teste"


def split_train_test(
    data: pd.DataFrame, test_size: float = TEST_SIZE, seed: int = RANDOM_SEED
) -> pd.Series:
    """Marca cada pedido como treino ou teste, estratificado pela variável-alvo.

    A mesma base, na mesma ordem e com a mesma semente, gera sempre a mesma separação. Assim a
    análise exploratória e a modelagem reservam exatamente os mesmos pedidos para o teste.
    """
    _, test_index = train_test_split(
        data.index, test_size=test_size, stratify=data["is_detractor"], random_state=seed
    )
    split = pd.Series(TRAIN, index=data.index, name="split")
    split[data.index.isin(test_index)] = TEST
    return split
