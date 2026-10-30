"""Variáveis, preparação e candidatos do modelo de risco de detrator (D-06 e D-18)."""

from collections.abc import Callable

import pandas as pd
from scipy.stats import loguniform, randint
from sklearn.base import clone
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingClassifier, HistGradientBoostingRegressor
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.model_selection import RandomizedSearchCV
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from src.config import RANDOM_SEED

TARGET = "is_detractor"

# Variáveis permitidas, agrupadas pelo momento em que o dado existe (D-06)
PROFILE = ["customer_age", "customer_region", "customer_tenure_months"]
ORDER = [
    "order_value",
    "items_quantity",
    "discount_value",
    "payment_installments",
    "freight_value",
]
DELIVERY = ["delivery_time_days", "delivery_delay_days", "delivery_attempts"]
SERVICE = ["customer_service_contacts", "resolution_time_days", "complaints_count"]
FEATURES = PROFILE + ORDER + DELIVERY + SERVICE
CATEGORICAL = ["customer_region"]

# Fora do modelo: a nota que define o alvo, o CSAT, a recompra e os identificadores (D-06)
EXCLUDED = ["nps_score", "csat_internal_score", "repeat_purchase_30d", "customer_id", "order_id"]

# Cenário de comparação: só o que já existe no checkout (D-04)
CHECKOUT_FEATURES = PROFILE + ORDER

# Nomes das variáveis nos gráficos, em linguagem de negócio
FEATURE_LABELS = {
    "customer_age": "idade",
    "customer_region": "região",
    "customer_tenure_months": "tempo de relacionamento",
    "order_value": "valor do pedido",
    "items_quantity": "itens",
    "discount_value": "desconto",
    "payment_installments": "parcelas",
    "freight_value": "frete",
    "delivery_time_days": "previsão de entrega",
    "delivery_delay_days": "dias de atraso",
    "delivery_attempts": "tentativas de entrega",
    "customer_service_contacts": "contatos com o atendimento",
    "resolution_time_days": "tempo de resolução",
    "complaints_count": "reclamações",
}

LOGISTIC = "regressão logística"
BOOSTING = "gradient boosting"
LINEAR = "regressão linear"

# Do mais simples para o mais complexo: é a ordem do desempate da D-18
CANDIDATES = [LOGISTIC, BOOSTING]

# Busca aleatória pequena (D-18): o mesmo número de combinações para cada candidato
N_ITER = 20
SEARCH_SPACES = {
    LOGISTIC: {"model__C": loguniform(1e-3, 1e2)},
    LINEAR: {"model__alpha": loguniform(1e-2, 1e3)},
    BOOSTING: {
        "model__learning_rate": loguniform(0.01, 0.3),
        "model__max_iter": randint(50, 500),
        "model__max_leaf_nodes": randint(4, 32),
        "model__min_samples_leaf": randint(20, 200),
        "model__l2_regularization": loguniform(1e-3, 10),
    },
}


def build_preprocessor(features: list[str]) -> ColumnTransformer:
    """Padroniza as variáveis numéricas e cria uma coluna para cada região.

    A mesma preparação serve aos dois candidatos: a padronização deixa a penalidade da regressão
    logística igual para todas as variáveis e não muda as árvores. Uma região ausente do treino
    fica com todas as colunas zeradas, sem erro.
    """
    categorical = [column for column in features if column in CATEGORICAL]
    numeric = [column for column in features if column not in CATEGORICAL]
    return ColumnTransformer(
        [
            ("numeric", StandardScaler(), numeric),
            (
                "categorical",
                OneHotEncoder(handle_unknown="ignore", sparse_output=False),
                categorical,
            ),
        ],
        verbose_feature_names_out=False,
    )


def build_classifier(kind: str, features: list[str] = FEATURES) -> Pipeline:
    """Preparação e classificador num único objeto: a preparação aprende só com os pedidos
    usados em cada ajuste, e nada da parte de validação vaza para ele."""
    estimators = {
        LOGISTIC: LogisticRegression(max_iter=1000),
        BOOSTING: HistGradientBoostingClassifier(random_state=RANDOM_SEED),
    }
    return Pipeline([("prep", build_preprocessor(features)), ("model", estimators[kind])])


def build_regressor(kind: str, features: list[str] = FEATURES) -> Pipeline:
    """Preparação e regressor da nota, para a comparação da D-17."""
    estimators = {
        LINEAR: Ridge(),
        BOOSTING: HistGradientBoostingRegressor(random_state=RANDOM_SEED),
    }
    return Pipeline([("prep", build_preprocessor(features)), ("model", estimators[kind])])


def with_features(model: Pipeline, features: list[str]) -> Pipeline:
    """O mesmo estimador, com os mesmos hiperparâmetros, preparado para outras variáveis."""
    return Pipeline(
        [("prep", build_preprocessor(features)), ("model", clone(model.named_steps["model"]))]
    )


def tune(
    model: Pipeline,
    space: dict,
    x: pd.DataFrame,
    target: pd.Series,
    splits: list,
    scoring: str | Callable = "roc_auc",
    n_iter: int = N_ITER,
    seed: int = RANDOM_SEED,
) -> RandomizedSearchCV:
    """Busca aleatória de hiperparâmetros, medida nas partes da validação cruzada do treino.

    Cada combinação sorteada é avaliada nas mesmas partes, e a melhor é reajustada com o treino
    inteiro, em `best_estimator_`.
    """
    search = RandomizedSearchCV(
        model, space, n_iter=n_iter, scoring=scoring, cv=splits, random_state=seed
    )
    return search.fit(x, target)
