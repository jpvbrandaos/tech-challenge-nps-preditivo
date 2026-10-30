"""Risco de detrator dos pedidos entregues e lista do dia, pelos segmentos de atraso da D-19."""

from pathlib import Path

from loguru import logger
import numpy as np
import pandas as pd
from sklearn.pipeline import Pipeline
import typer

from src.config import DAILY_LIST_FILE
from src.features import LONG_RESOLUTION_DAYS
from src.modeling.models import FEATURES
from src.modeling.train import load_model

app = typer.Typer()

# A partir de 3 dias de atraso, a lista segue a regra de dias de atraso, e não o modelo (D-19)
LONG_DELAY_DAYS = 3
LONG_DELAY = "atraso de 3 dias ou mais"
SHORT_DELAY = "atraso de até 2 dias"

# Parcela dos pedidos do dia que o atendimento consegue contatar; estimativa ainda a validar
CAPACITY = 0.2

# Ação ligada à falha registrada, na ordem de impacto da análise exploratória (D-19)
ACTIONS = {
    "atraso": "contato de recuperação; causa do atraso enviada à logística da rota",
    "contato ou reclamação": "resolver no mesmo dia a falha que originou o contato",
    f"resolução acima de {LONG_RESOLUTION_DAYS} dias": "fechar o chamado e confirmar a solução",
}
NO_FAILURE = "sem falha registrada"


def registered_failure(orders: pd.DataFrame) -> pd.Series:
    """Primeira falha do pedido na ordem de impacto: atraso, contato ou reclamação, resolução."""
    conditions = [
        orders["delivery_delay_days"] > 0,
        (orders["customer_service_contacts"] > 0) | (orders["complaints_count"] > 0),
        orders["resolution_time_days"] > LONG_RESOLUTION_DAYS,
    ]
    return pd.Series(
        np.select(conditions, list(ACTIONS), default=NO_FAILURE), index=orders.index, dtype=str
    )


def risk_of(model: Pipeline, orders: pd.DataFrame) -> np.ndarray:
    """Probabilidade de detrator de cada pedido, com as variáveis do modelo (D-06)."""
    missing = sorted(set(FEATURES) - set(orders.columns))
    if missing:
        raise ValueError(f"Faltam colunas do modelo: {', '.join(missing)}")
    return model.predict_proba(orders[FEATURES])[:, 1]


def daily_list(orders: pd.DataFrame, risk: np.ndarray, capacity: float = CAPACITY) -> pd.DataFrame:
    """Lista do dia: cada segmento de atraso na sua ordem, com metade da capacidade (D-19).

    Com 3 dias de atraso ou mais, a ordem segue os dias de atraso, e o risco do modelo só desfaz
    empates; com até 2 dias, segue o risco do modelo. Cada segmento recebe metade das vagas, e uma
    vaga que sobra num segmento não passa para o outro, como no piloto.
    """
    failure = registered_failure(orders)
    table = pd.DataFrame(
        {
            "order_id": orders["order_id"].to_numpy(),
            "segmento": np.where(
                orders["delivery_delay_days"] >= LONG_DELAY_DAYS, LONG_DELAY, SHORT_DELAY
            ),
            "dias de atraso": orders["delivery_delay_days"].to_numpy(),
            "risco": np.asarray(risk, dtype=float),
            "falha": failure.to_numpy(),
            "ação": failure.map(ACTIONS).fillna("").to_numpy(),
        }
    )
    slots = round(capacity * len(table) / 2)
    parts = []
    for segment, order in [(LONG_DELAY, ["dias de atraso", "risco"]), (SHORT_DELAY, ["risco"])]:
        part = table[table["segmento"] == segment].sort_values(
            order, ascending=False, kind="stable"
        )
        part.insert(2, "posição", np.arange(1, len(part) + 1))
        parts.append(part)
    result = pd.concat(parts, ignore_index=True)
    result.insert(3, "na lista", result["posição"] <= slots)
    return result


@app.command()
def main(
    orders_path: Path, output_path: Path = DAILY_LIST_FILE, capacity: float = CAPACITY
) -> None:
    """Calcula o risco dos pedidos entregues e grava a lista do dia."""
    orders = pd.read_csv(orders_path)
    result = daily_list(orders, risk_of(load_model(), orders), capacity)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(output_path, index=False)
    logger.success(
        f"{result['na lista'].sum()} de {len(result)} pedidos na lista do dia, em {output_path}"
    )


if __name__ == "__main__":
    app()
