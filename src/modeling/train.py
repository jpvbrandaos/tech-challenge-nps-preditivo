"""Treino do modelo de risco de detrator: busca, escolha pela D-18 e gravação em models/."""

from datetime import datetime
import json
from pathlib import Path

import joblib
from loguru import logger
import numpy as np
import pandas as pd
import sklearn
from sklearn.metrics import average_precision_score, roc_auc_score
from sklearn.pipeline import Pipeline
import typer

from src.config import MODEL_FILE, RAW_DATA_SHA256
from src.features import load_processed_data
from src.modeling.evaluation import choose_model, cv_splits, out_of_fold
from src.modeling.models import (
    CANDIDATES,
    FEATURES,
    N_ITER,
    SEARCH_SPACES,
    TARGET,
    build_classifier,
    tune,
)
from src.split import TRAIN, split_train_test

app = typer.Typer()


def readable_params(params: dict) -> dict:
    """Hiperparâmetros sem o prefixo do pipeline, com quatro algarismos significativos."""
    readable = {}
    for name, value in params.items():
        value = value.item() if isinstance(value, np.generic) else value
        if isinstance(value, float):
            value = float(f"{value:.4g}")
        readable[name.removeprefix("model__")] = value
    return readable


def train_model(
    train: pd.DataFrame, n_iter: int = N_ITER
) -> tuple[Pipeline, pd.DataFrame, dict[str, np.ndarray]]:
    """Ajusta os candidatos na validação cruzada do treino e escolhe um deles pela D-18.

    Devolve o candidato escolhido, já reajustado com o treino inteiro; uma tabela com ROC-AUC,
    PR-AUC e hiperparâmetros de cada candidato; e, por candidato, o risco de cada pedido de treino
    previsto fora da amostra, a base das comparações.
    """
    x, y = train[FEATURES], train[TARGET]
    splits = cv_splits(x, y)
    searches, risk = {}, {}
    for kind in CANDIDATES:
        searches[kind] = tune(
            build_classifier(kind), SEARCH_SPACES[kind], x, y, splits, n_iter=n_iter
        )
        risk[kind] = out_of_fold(searches[kind].best_estimator_, x, y, splits)
    auc = {kind: roc_auc_score(y, risk[kind]) for kind in CANDIDATES}
    chosen = choose_model(auc)
    summary = pd.DataFrame(
        {
            "ROC-AUC": auc,
            "PR-AUC": {kind: average_precision_score(y, risk[kind]) for kind in CANDIDATES},
            "hiperparâmetros": {
                kind: readable_params(searches[kind].best_params_) for kind in CANDIDATES
            },
            "escolhido": {kind: kind == chosen for kind in CANDIDATES},
        }
    )
    return searches[chosen].best_estimator_, summary, risk


def save_model(model: Pipeline, summary: pd.DataFrame, path: Path = MODEL_FILE) -> Path:
    """Grava o modelo com joblib e, ao lado, um JSON com o necessário para rastreá-lo."""
    path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, path)
    chosen = summary.index[summary["escolhido"]][0]
    record = {
        "modelo": chosen,
        "hiperparametros": summary.loc[chosen, "hiperparâmetros"],
        "variaveis": FEATURES,
        "roc_auc_validacao_cruzada": round(float(summary.loc[chosen, "ROC-AUC"]), 4),
        "sha256_da_base": RAW_DATA_SHA256,
        "versao_scikit_learn": sklearn.__version__,
        "treinado_em": datetime.now().isoformat(timespec="seconds"),
    }
    path.with_suffix(".json").write_text(
        json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return path


def load_model(path: Path = MODEL_FILE) -> Pipeline:
    """Lê o modelo gravado por python -m src.modeling.train."""
    if not path.exists():
        raise FileNotFoundError("Modelo ausente: rode python -m src.modeling.train")
    return joblib.load(path)


@app.command()
def main() -> None:
    """Treina o modelo com os pedidos de treino e grava em models/."""
    processed = load_processed_data()
    train = processed[split_train_test(processed) == TRAIN]
    model, summary, _ = train_model(train)
    path = save_model(model, summary)
    chosen = summary.index[summary["escolhido"]][0]
    logger.success(
        f"Modelo salvo em {path}: {chosen}, com ROC-AUC de "
        f"{summary.loc[chosen, 'ROC-AUC']:.3f} na validação cruzada"
    )


if __name__ == "__main__":
    app()
