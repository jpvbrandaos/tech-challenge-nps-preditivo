"""Avaliação do modelo de risco: validação cruzada, comparação com a regra e diagnósticos."""

import numpy as np
from numpy.typing import ArrayLike
import pandas as pd
from scipy.stats import rankdata
from sklearn.base import clone, is_classifier
from sklearn.inspection import permutation_importance
from sklearn.metrics import make_scorer, roc_auc_score
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.pipeline import Pipeline
from statsmodels.stats.proportion import proportion_confint

from src.analysis import ALPHA, N_BOOT
from src.config import RANDOM_SEED
from src.features import DETRACTOR_BELOW
from src.modeling.models import CANDIDATES

# Critérios fixados antes do treino
N_FOLDS = 5
SIMPLICITY_MARGIN = 0.01  # D-18: até esta diferença de ROC-AUC, vence o candidato mais simples
MIN_AUC_GAIN = 0.05  # D-15: ganho mínimo de ROC-AUC sobre a regra de dias de atraso, no teste


def cv_splits(
    x: pd.DataFrame, y: pd.Series, n_folds: int = N_FOLDS, seed: int = RANDOM_SEED
) -> list[tuple[np.ndarray, np.ndarray]]:
    """Partes da validação cruzada estratificada, as mesmas em todas as comparações.

    Com as mesmas partes, a diferença entre dois modelos vem dos modelos, e não do sorteio.
    """
    folds = StratifiedKFold(n_splits=n_folds, shuffle=True, random_state=seed)
    return list(folds.split(x, y))


def out_of_fold(model: Pipeline, x: pd.DataFrame, target: pd.Series, splits: list) -> np.ndarray:
    """Previsão de cada pedido por um modelo ajustado sem ele, nas partes da validação cruzada.

    Para um classificador, devolve a probabilidade de detrator; para um regressor, a nota prevista.
    """
    method = "predict_proba" if is_classifier(model) else "predict"
    prediction = cross_val_predict(model, x, target, cv=splits, method=method)
    return prediction[:, 1] if prediction.ndim == 2 else prediction


def detractor_auc_from_score(nps_score: ArrayLike, predicted_score: ArrayLike) -> float:
    """ROC-AUC de uma nota prevista usada como ordem de risco: nota menor, risco maior (D-17)."""
    is_detractor = np.asarray(nps_score) < DETRACTOR_BELOW
    return roc_auc_score(is_detractor, -np.asarray(predicted_score))


# A busca da regressão usa a mesma régua do classificador, para a comparação não favorecê-lo
SCORE_RANKING = make_scorer(detractor_auc_from_score)


def choose_model(auc: dict[str, float], margin: float = SIMPLICITY_MARGIN) -> str:
    """Candidato escolhido pela regra da D-18, a partir da ROC-AUC de cada um.

    Vence o de maior ROC-AUC; se outro ficar a até `margin` dele, vence o mais simples, na ordem
    de CANDIDATES.
    """
    best = max(auc.values())
    return next(name for name in CANDIDATES if name in auc and best - auc[name] <= margin)


def roc_auc_rows(y: np.ndarray, score: np.ndarray) -> np.ndarray:
    """ROC-AUC de cada linha, pela soma dos postos, com os empates divididos ao meio.

    É a mesma conta do `roc_auc_score`, feita de uma vez para milhares de reamostragens. Linhas
    com uma classe só não têm ROC-AUC e saem como NaN.
    """
    ranks = rankdata(score, axis=-1)
    positives = y.sum(axis=-1)
    negatives = y.shape[-1] - positives
    with np.errstate(invalid="ignore", divide="ignore"):
        return ((ranks * y).sum(axis=-1) - positives * (positives + 1) / 2) / (
            positives * negatives
        )


def auc_difference(
    y: ArrayLike,
    score: ArrayLike,
    reference: ArrayLike,
    n_boot: int = N_BOOT,
    seed: int = RANDOM_SEED,
) -> dict:
    """Diferença de ROC-AUC entre duas ordenações dos mesmos pedidos, com intervalo bootstrap.

    Cada reamostragem sorteia os pedidos com reposição e mede as duas ordenações nos mesmos
    pedidos: o que as duas têm de variação em comum se cancela, e o intervalo de 95% costuma
    ficar mais estreito do que o de cada ROC-AUC isolada.
    """
    y = np.asarray(y, dtype=float)
    score = np.asarray(score, dtype=float)
    reference = np.asarray(reference, dtype=float)
    rows = np.random.default_rng(seed).integers(0, len(y), size=(n_boot, len(y)))
    draws = roc_auc_rows(y[rows], score[rows]) - roc_auc_rows(y[rows], reference[rows])
    low, high = np.percentile(draws[np.isfinite(draws)], [2.5, 97.5])
    return {
        "diferença": roc_auc_score(y, score) - roc_auc_score(y, reference),
        "IC inferior": low,
        "IC superior": high,
    }


def reference_criteria(
    difference: dict, pr_auc: float, reference_pr_auc: float, margin: float = MIN_AUC_GAIN
) -> pd.Series:
    """Os três critérios da D-15 para o modelo superar a regra, cada um atendido ou não."""
    return pd.Series(
        {
            f"ROC-AUC pelo menos {margin} acima da regra": difference["diferença"] >= margin,
            "intervalo da diferença acima de zero": difference["IC inferior"] > 0,
            "PR-AUC não menor que a da regra": pr_auc >= reference_pr_auc,
        }
    )


def error_by_group(y: ArrayLike, risk: ArrayLike, groups: pd.Series) -> pd.DataFrame:
    """Risco médio previsto contra a proporção observada de detratores, e ROC-AUC, por grupo.

    Diferença positiva indica risco superestimado no grupo. A ROC-AUC mostra se o modelo ordena
    os clientes de cada grupo tão bem quanto os dos demais.
    """
    frame = pd.DataFrame(
        {
            "group": groups.reset_index(drop=True),
            "y": np.asarray(y),
            "risk": np.asarray(risk, dtype=float),
        }
    )
    rows = {}
    for group, part in frame.groupby("group", observed=True):
        both_classes = part["y"].nunique() == 2
        rows[group] = {
            "pedidos": len(part),
            "% detratores": 100 * part["y"].mean(),
            "% previsto": 100 * part["risk"].mean(),
            "diferença (pontos)": 100 * (part["risk"].mean() - part["y"].mean()),
            "ROC-AUC": roc_auc_score(part["y"], part["risk"]) if both_classes else np.nan,
        }
    return pd.DataFrame(rows).T.astype({"pedidos": int})


def calibration_table(y: ArrayLike, risk: ArrayLike, n_bins: int = 10) -> pd.DataFrame:
    """Risco médio previsto e proporção observada de detratores por faixa de risco.

    As faixas têm o mesmo número de pedidos, e a proporção observada vem com o intervalo de
    Wilson de 95%, como em `analysis.rate_table`.
    """
    frame = pd.DataFrame({"y": np.asarray(y), "risk": np.asarray(risk, dtype=float)})
    bands = pd.qcut(frame["risk"], n_bins, labels=False, duplicates="drop") + 1
    grouped = frame.groupby(bands.rename("faixa de risco"))
    orders = grouped["y"].size()
    cases = grouped["y"].sum()
    low, high = proportion_confint(cases, orders, alpha=ALPHA, method="wilson")
    return pd.DataFrame(
        {
            "pedidos": orders,
            "% previsto": 100 * grouped["risk"].mean(),
            "% detratores": 100 * cases / orders,
            "IC inferior": 100 * low,
            "IC superior": 100 * high,
        }
    )


def permutation_importance_cv(
    model: Pipeline,
    x: pd.DataFrame,
    y: pd.Series,
    splits: list,
    n_repeats: int = 10,
    seed: int = RANDOM_SEED,
) -> pd.DataFrame:
    """Queda da ROC-AUC quando cada variável é embaralhada, medida nas partes de validação.

    Em cada parte, o modelo é ajustado sem ela e avaliado nela, com cada variável embaralhada
    `n_repeats` vezes. Variáveis que carregam a mesma informação dividem a importância entre si.
    """
    drops = []
    for train_rows, valid_rows in splits:
        fitted = clone(model).fit(x.iloc[train_rows], y.iloc[train_rows])
        result = permutation_importance(
            fitted,
            x.iloc[valid_rows],
            y.iloc[valid_rows],
            scoring="roc_auc",
            n_repeats=n_repeats,
            random_state=seed,
        )
        drops.append(result.importances_mean)
    drops = np.array(drops)
    return pd.DataFrame(
        {"queda da ROC-AUC": drops.mean(axis=0), "desvio entre as partes": drops.std(axis=0)},
        index=x.columns,
    ).sort_values("queda da ROC-AUC", ascending=False)
