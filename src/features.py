"""Atributos de negócio da base de pedidos."""

import numpy as np
import pandas as pd

# Faixas do NPS aplicadas direto sobre a nota, sem arredondar (D-05)
DETRACTOR_BELOW = 7
PROMOTER_FROM = 9
NPS_CATEGORIES = ["detrator", "neutro", "promotor"]


def classify_nps(score: pd.Series) -> pd.Series:
    """Classifica cada nota em detrator, neutro ou promotor, sem arredondar (D-05)."""
    return pd.cut(
        score,
        bins=[-np.inf, DETRACTOR_BELOW, PROMOTER_FROM, np.inf],
        labels=NPS_CATEGORIES,
        right=False,  # faixas fechadas à esquerda: 7,0 já é neutro e 9,0 já é promotor
    )
