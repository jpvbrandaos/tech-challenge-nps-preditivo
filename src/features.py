"""Atributos de negócio da base de pedidos e geração da base tratada."""

from pathlib import Path

from loguru import logger
import numpy as np
import pandas as pd
import typer

from src.config import PROCESSED_DATA_FILE
from src.dataset import download_raw_data

app = typer.Typer()

# Faixas do NPS aplicadas direto sobre a nota, sem arredondar (D-05)
DETRACTOR_BELOW = 7
PROMOTER_FROM = 9
NPS_CATEGORIES = ["detrator", "neutro", "promotor"]

# Faixas de negócio, fechadas à direita: 2 dias de atraso caem em "1 a 2 dias"
DELAY_BINS = [-np.inf, 0, 2, 4, np.inf]
DELAY_LABELS = ["sem atraso", "1 a 2 dias", "3 a 4 dias", "5 dias ou mais"]
TENURE_BINS = [-np.inf, 12, 36, 60, np.inf]
TENURE_LABELS = ["até 1 ano", "1 a 3 anos", "3 a 5 anos", "mais de 5 anos"]
AGE_BINS = [17, 24, 34, 44, 54, np.inf]
AGE_LABELS = ["18 a 24", "25 a 34", "35 a 44", "45 a 54", "55 ou mais"]

# Resolução acima de uma semana conta como falha no friction_score
LONG_RESOLUTION_DAYS = 7

FEATURE_COLUMNS = [
    "nps_category",
    "is_detractor",
    "is_late",
    "delay_bucket",
    "actual_delivery_days",
    "discount_pct",
    "freight_pct",
    "avg_item_value",
    "had_contact",
    "multiple_attempts",
    "tenure_bucket",
    "age_bucket",
    "friction_score",
]

# Ordem das faixas, que o CSV não guarda
CATEGORY_ORDERS = {
    "nps_category": NPS_CATEGORIES,
    "delay_bucket": DELAY_LABELS,
    "tenure_bucket": TENURE_LABELS,
    "age_bucket": AGE_LABELS,
}


def classify_nps(score: pd.Series) -> pd.Series:
    """Classifica cada nota em detrator, neutro ou promotor, sem arredondar (D-05)."""
    return pd.cut(
        score,
        bins=[-np.inf, DETRACTOR_BELOW, PROMOTER_FROM, np.inf],
        labels=NPS_CATEGORIES,
        right=False,  # faixas fechadas à esquerda: 7,0 já é neutro e 9,0 já é promotor
    )


def build_features(raw: pd.DataFrame) -> pd.DataFrame:
    """Acrescenta os atributos de negócio, sem excluir pedidos nem alterar as colunas originais."""
    data = raw.copy()

    data["nps_category"] = classify_nps(data["nps_score"])
    data["is_detractor"] = (data["nps_category"] == "detrator").astype(int)

    # O tempo de entrega é a previsão informada ao cliente, e o atraso, os dias além dela (D-07)
    data["is_late"] = (data["delivery_delay_days"] > 0).astype(int)
    data["delay_bucket"] = pd.cut(data["delivery_delay_days"], DELAY_BINS, labels=DELAY_LABELS)
    data["actual_delivery_days"] = data["delivery_time_days"] + data["delivery_delay_days"]

    # O valor do pedido já vem com o desconto aplicado (D-08)
    data["discount_pct"] = data["discount_value"] / (data["order_value"] + data["discount_value"])
    data["freight_pct"] = data["freight_value"] / data["order_value"]
    data["avg_item_value"] = data["order_value"] / data["items_quantity"]

    data["had_contact"] = (data["customer_service_contacts"] > 0).astype(int)
    data["multiple_attempts"] = (data["delivery_attempts"] > 1).astype(int)
    data["tenure_bucket"] = pd.cut(
        data["customer_tenure_months"], TENURE_BINS, labels=TENURE_LABELS
    )
    data["age_bucket"] = pd.cut(data["customer_age"], AGE_BINS, labels=AGE_LABELS)

    # Falhas da jornada; a reclamação fica de fora porque quase todo cliente tem uma (D-09)
    long_resolution = (data["resolution_time_days"] > LONG_RESOLUTION_DAYS).astype(int)
    data["friction_score"] = (
        data["is_late"] + data["multiple_attempts"] + data["had_contact"] + long_resolution
    )
    return data


def load_processed_data(path: Path = PROCESSED_DATA_FILE) -> pd.DataFrame:
    """Lê a base tratada e devolve as faixas como categorias ordenadas."""
    if not path.exists():
        raise FileNotFoundError("Base tratada ausente: rode python -m src.features")
    data = pd.read_csv(path)
    for column, order in CATEGORY_ORDERS.items():
        data[column] = pd.Categorical(data[column], categories=order, ordered=True)
    return data


@app.command()
def main() -> None:
    """Gera a base tratada a partir da base bruta conferida."""
    processed = build_features(pd.read_csv(download_raw_data()))
    PROCESSED_DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    processed.to_csv(PROCESSED_DATA_FILE, index=False)
    logger.success(f"Base tratada salva com {len(processed)} pedidos")


if __name__ == "__main__":
    app()
