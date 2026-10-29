"""Funções da análise exploratória: proporções com intervalo, efeitos e vereditos."""

from collections.abc import Callable

import numpy as np
from numpy.typing import ArrayLike
import pandas as pd
from scipy.stats import chi2_contingency
from scipy.stats.contingency import association
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, roc_auc_score
from sklearn.tree import DecisionTreeClassifier
import statsmodels.api as sm
from statsmodels.stats.multitest import multipletests
from statsmodels.stats.proportion import proportion_confint

from src.config import RANDOM_SEED
from src.features import LONG_RESOLUTION_DAYS

# Critérios fixados antes de olhar os dados da análise exploratória
MIN_EFFECT_PP = 5.0  # menor diferença que muda uma decisão de negócio, em pontos percentuais
MIN_GROUP_SIZE = 30  # abaixo disso, um grupo não sustenta conclusão
ALPHA = 0.05
N_BOOT = 2000

CONFIRMED = "confirmada"
REFUTED = "refutada"
INCONCLUSIVE = "inconclusiva"

QUARTILE_LABELS = ["Q1 (menor)", "Q2", "Q3", "Q4 (maior)"]
TARGET_LABELS = {"is_detractor": "% detratores", "repeat_purchase_30d": "% recompra"}


def nps_of(categories: pd.Series) -> float:
    """NPS de um grupo: percentual de promotores menos percentual de detratores."""
    shares = categories.value_counts(normalize=True)
    return 100 * (shares.get("promotor", 0.0) - shares.get("detrator", 0.0))


def counterfactual_nps(data: pd.DataFrame, affected: pd.Series, reference: pd.Series) -> float:
    """NPS se os pedidos afetados tivessem a mistura de categorias do grupo de referência."""
    mix = data.loc[reference, "nps_category"].value_counts(normalize=True)
    counts = (
        data.loc[~affected, "nps_category"].value_counts().add(mix * affected.sum(), fill_value=0)
    )
    shares = counts / counts.sum()
    return 100 * (shares.get("promotor", 0.0) - shares.get("detrator", 0.0))


def nps_gain(data: pd.DataFrame, affected: str, reference: str) -> float:
    """Pontos de NPS ganhos se os pedidos de `affected` tivessem a mistura de `reference`.

    As duas condições seguem o formato de `DataFrame.eval`, como em `estimate_contrast`.
    """
    new = counterfactual_nps(data, data.eval(affected), data.eval(reference))
    return new - nps_of(data["nps_category"])


def quartiles(values: pd.Series) -> pd.Series:
    """Faixas por quartil, do menor para o maior valor."""
    return pd.qcut(values, 4, labels=QUARTILE_LABELS)


def rate_table(
    data: pd.DataFrame, by: str | pd.Series, target: str = "is_detractor"
) -> pd.DataFrame:
    """Pedidos, percentual do alvo com intervalo de Wilson de 95% e NPS por grupo."""
    label = TARGET_LABELS.get(target, f"% {target}")
    grouped = data.groupby(by, observed=True)
    orders = grouped[target].size()
    cases = grouped[target].sum()
    low, high = proportion_confint(cases, orders, alpha=ALPHA, method="wilson")
    return pd.DataFrame(
        {
            "pedidos": orders,
            label: 100 * cases / orders,
            "IC inferior": 100 * low,
            "IC superior": 100 * high,
            "NPS": grouped["nps_category"].apply(nps_of),
        }
    )


def failure_flags(data: pd.DataFrame) -> pd.DataFrame:
    """As quatro falhas da jornada que compõem o friction_score, uma coluna 0 ou 1 cada."""
    long_resolution = (data["resolution_time_days"] > LONG_RESOLUTION_DAYS).astype(int)
    return pd.DataFrame(
        {
            "atraso": data["is_late"],
            "nova tentativa": data["multiple_attempts"],
            "contato com o atendimento": data["had_contact"],
            f"resolução acima de {LONG_RESOLUTION_DAYS} dias": long_resolution,
        }
    )


def problem_impact(
    data: pd.DataFrame, flags: pd.DataFrame, target: str = "is_detractor"
) -> pd.DataFrame:
    """Frequência, impacto e presença entre os detratores de cada falha.

    O impacto é o risco relativo: percentual de detratores com a falha dividido pelo percentual
    sem ela. A presença é a parcela dos detratores que passou pela falha.
    """
    y = data[target]
    rows = {}
    for name, flag in flags.items():
        with_problem = y[flag == 1].mean()
        without_problem = y[flag == 0].mean()
        rows[name] = {
            "pedidos com a falha (%)": 100 * flag.mean(),
            "% detratores com": 100 * with_problem,
            "% detratores sem": 100 * without_problem,
            "impacto": with_problem / without_problem,
            "presença entre detratores (%)": 100 * flag[y == 1].mean(),
            "pedidos sem a falha": int((flag == 0).sum()),
        }
    return pd.DataFrame(rows).T


def factor_ranking(
    data: pd.DataFrame, factors: dict[str, pd.Series], target: str = "is_detractor"
) -> pd.DataFrame:
    """Ordena os fatores pelo tamanho do efeito sobre o alvo (V de Cramér).

    Cada fator é uma variável já em faixas. O p-valor do qui-quadrado é corrigido por Holm entre
    todos os fatores, e a faixa de maior e a de menor percentual consideram só grupos com pelo
    menos MIN_GROUP_SIZE pedidos.
    """
    rows = []
    for name, band in factors.items():
        table = pd.crosstab(band, data[target])
        _, p_value, _, _ = chi2_contingency(table)
        rates = data.groupby(band, observed=True)[target].agg(["mean", "size"])
        rates = rates[rates["size"] >= MIN_GROUP_SIZE]
        if rates.empty:
            raise ValueError(f"{name}: nenhuma faixa tem {MIN_GROUP_SIZE} pedidos ou mais")
        rows.append(
            {
                "fator": name,
                "V de Cramér": association(table, method="cramer"),
                "p-valor": p_value,
                "faixa com mais detratores": rates["mean"].idxmax(),
                "faixa com menos detratores": rates["mean"].idxmin(),
                "diferença (pontos)": 100 * (rates["mean"].max() - rates["mean"].min()),
            }
        )
    ranking = pd.DataFrame(rows).set_index("fator")
    ranking.insert(2, "p ajustado", multipletests(ranking["p-valor"], method="holm")[1])
    return ranking.drop(columns="p-valor").sort_values("V de Cramér", ascending=False)


def standardized_share(
    data: pd.DataFrame, group: str, stratum: str, target: str = "is_detractor"
) -> pd.Series:
    """Percentual do alvo por grupo como se todos tivessem a mesma distribuição de `stratum`.

    É a padronização direta: a taxa de cada estrato no grupo, ponderada pelo peso do estrato na
    base inteira. Diferenças que somem depois do ajuste vinham da composição dos grupos.
    """
    weights = data[stratum].value_counts(normalize=True)
    rates = data.groupby([group, stratum], observed=True)[target].mean().unstack(stratum)
    available = rates.notna().mul(weights, axis=1).sum(axis=1)
    return 100 * rates.mul(weights, axis=1).sum(axis=1) / available


def estimate_contrast(
    data: pd.DataFrame,
    groups: list[str],
    weights: list[float],
    target: str = "is_detractor",
    n_boot: int = N_BOOT,
    seed: int = RANDOM_SEED,
) -> dict:
    """Contraste entre grupos, em pontos percentuais, com intervalo bootstrap de 95%.

    Cada grupo é uma condição no formato de `DataFrame.eval`, e o contraste é a soma das
    proporções do alvo nos grupos, multiplicadas pelos pesos: [1, -1] compara dois grupos, e
    [1, -1, -1, 1] compara a diferença dentro de um estrato com a diferença dentro de outro.
    """
    masks = np.column_stack([data.eval(group).to_numpy(dtype=bool) for group in groups])
    y = data[target].to_numpy(dtype=float)
    w = np.asarray(weights, dtype=float)

    def contrast(rows):
        outcome = y[rows]
        shares = []
        for column in range(masks.shape[1]):
            member = masks[:, column][rows]
            with np.errstate(invalid="ignore", divide="ignore"):
                shares.append((member * outcome).sum(axis=-1) / member.sum(axis=-1))
        return 100 * np.stack(shares, axis=-1) @ w

    estimate = float(contrast(np.arange(len(y))))
    rng = np.random.default_rng(seed)
    draws = contrast(rng.integers(0, len(y), size=(n_boot, len(y))))
    draws = draws[np.isfinite(draws)]
    low, high = np.percentile(draws, [2.5, 97.5])
    p_value = 2 * min((draws <= 0).mean(), (draws >= 0).mean())
    return {
        "efeito": estimate,
        "IC inferior": low,
        "IC superior": high,
        "p-valor": min(1.0, max(p_value, 1 / n_boot)),
        "menor grupo": int(masks.sum(axis=0).min()),
    }


def within_strata(
    data: pd.DataFrame, exposed: str, unexposed: str, strata: list[str]
) -> tuple[list[str], list[float]]:
    """Grupos e pesos do efeito de `exposed` contra `unexposed` dentro de cada estrato.

    Cada estrato pesa pela sua parcela dos pedidos, como na padronização direta. O resultado vai
    para `estimate_contrast`, que soma a diferença de cada estrato com o seu peso.
    """
    groups, weights = [], []
    for stratum in strata:
        share = float(data.eval(stratum).mean())
        groups += [f"({exposed}) and ({stratum})", f"({unexposed}) and ({stratum})"]
        weights += [share, -share]
    return groups, weights


def excess_over_additive(
    data: pd.DataFrame, flags: pd.DataFrame, target: str = "is_detractor", threshold: int = 2
) -> float:
    """Detratores observados menos esperados entre pedidos com `threshold` falhas ou mais.

    O esperado vem de uma regressão logística em que cada falha soma seu efeito, sem interação.
    Um excesso positivo indica que falhas acumuladas pesam mais que a soma das isoladas.
    """
    x = flags.to_numpy(dtype=float)
    y = data[target].to_numpy()
    model = LogisticRegression(C=np.inf, max_iter=1000).fit(x, y)
    many = x.sum(axis=1) >= threshold
    return 100 * (y[many].mean() - model.predict_proba(x[many])[:, 1].mean())


def bootstrap_statistic(
    data: pd.DataFrame,
    statistic: Callable[[pd.DataFrame], float],
    n_boot: int = N_BOOT,
    seed: int = RANDOM_SEED,
) -> dict:
    """Estatística qualquer da base com intervalo bootstrap de 95% e p-valor bicaudal."""
    rng = np.random.default_rng(seed)
    estimate = statistic(data)
    draws = np.array(
        [statistic(data.iloc[rng.integers(0, len(data), len(data))]) for _ in range(n_boot)]
    )
    draws = draws[np.isfinite(draws)]
    low, high = np.percentile(draws, [2.5, 97.5])
    p_value = 2 * min((draws <= 0).mean(), (draws >= 0).mean())
    return {
        "efeito": estimate,
        "IC inferior": low,
        "IC superior": high,
        "p-valor": min(1.0, max(p_value, 1 / n_boot)),
    }


def breakpoint_test(data: pd.DataFrame, column: str, target: str = "is_detractor") -> dict:
    """Compara um modelo com um único corte na variável a um modelo linear nela.

    O corte vem de uma árvore de profundidade 1. Como foi escolhido nos próprios dados, conta como
    um parâmetro a mais no AIC do modelo com corte. Um ganho de 2 pontos ou mais indica salto, e
    não crescimento gradual.
    """
    x = data[column].to_numpy(dtype=float)
    y = data[target].to_numpy()
    stump = DecisionTreeClassifier(
        max_depth=1, min_samples_leaf=MIN_GROUP_SIZE, random_state=RANDOM_SEED
    ).fit(x.reshape(-1, 1), y)
    if stump.tree_.node_count == 1:
        return {"a partir de": np.nan, "AIC linear": np.nan, "AIC com corte": np.nan, "ganho": 0.0}
    cut = stump.tree_.threshold[0]
    above = x > cut
    aic_linear = sm.Logit(y, sm.add_constant(x)).fit(disp=0).aic
    aic_step = sm.Logit(y, sm.add_constant(above.astype(float))).fit(disp=0).aic + 2
    return {
        "a partir de": x[above].min(),
        "AIC linear": aic_linear,
        "AIC com corte": aic_step,
        "ganho": aic_linear - aic_step,
    }


def tree_leaves(tree: DecisionTreeClassifier, x: pd.DataFrame, y: pd.Series) -> pd.DataFrame:
    """Uma linha por folha da árvore: a regra em texto, os pedidos e o percentual do alvo."""
    structure = tree.tree_
    integer = {column: bool((x[column] % 1 == 0).all()) for column in x.columns}
    rules = {}

    def walk(node: int, conditions: list[str]) -> None:
        if structure.children_left[node] == -1:
            rules[node] = " e ".join(conditions) or "todos os pedidos"
            return
        name = x.columns[structure.feature[node]]
        cut = structure.threshold[node]
        if integer[name]:
            left, right = f"{name} ≤ {int(np.floor(cut))}", f"{name} ≥ {int(np.floor(cut)) + 1}"
        else:
            left, right = f"{name} ≤ {cut:.2f}", f"{name} > {cut:.2f}"
        walk(structure.children_left[node], [*conditions, left])
        walk(structure.children_right[node], [*conditions, right])

    walk(0, [])
    leaves = pd.Series(tree.apply(x), index=x.index)
    summary = y.groupby(leaves).agg(["size", "mean"])
    return (
        pd.DataFrame(
            {
                "regra": [rules[leaf] for leaf in summary.index],
                "pedidos": summary["size"].to_numpy(),
                "% detratores": 100 * summary["mean"].to_numpy(),
            }
        )
        .sort_values("% detratores", ascending=False)
        .reset_index(drop=True)
    )


def ranking_metrics(
    y: ArrayLike, score: ArrayLike, share: float = 0.2, seed: int = RANDOM_SEED
) -> dict:
    """Qualidade de uma ordenação de risco: PR-AUC, ROC-AUC e o resultado de agir no topo.

    O topo são os `share` pedidos de maior pontuação; empates são desfeitos ao acaso, com semente.
    A precisão no topo é a parcela de detratores na lista, e a captura é a parcela de todos os
    detratores que a lista alcança.
    """
    y = np.asarray(y)
    score = np.asarray(score, dtype=float)
    order = np.lexsort((np.random.default_rng(seed).random(len(score)), -score))
    top = order[: round(share * len(score))]
    return {
        "PR-AUC": average_precision_score(y, score),
        "ROC-AUC": roc_auc_score(y, score),
        "precisão no topo": y[top].mean(),
        "captura no topo": y[top].sum() / y.sum(),
    }


def verdict_effect(
    estimate: float,
    low: float,
    high: float,
    p_adjusted: float,
    smallest_group: int,
    minimum: float = MIN_EFFECT_PP,
) -> str:
    """Veredito de uma hipótese que prevê um efeito positivo de pelo menos `minimum` pontos."""
    if smallest_group < MIN_GROUP_SIZE:
        return INCONCLUSIVE
    if estimate >= minimum and low > 0 and p_adjusted < ALPHA:
        return CONFIRMED
    if high < minimum:
        return REFUTED
    return INCONCLUSIVE


def invert_verdict(verdict: str) -> str:
    """Veredito da hipótese contrária: o que confirma uma refuta a outra."""
    return {CONFIRMED: REFUTED, REFUTED: CONFIRMED}.get(verdict, INCONCLUSIVE)


def verdict_share(low: float, high: float, minimum: float) -> str:
    """Veredito de uma hipótese que prevê uma parcela de pelo menos `minimum` por cento."""
    if low >= minimum:
        return CONFIRMED
    if high < minimum:
        return REFUTED
    return INCONCLUSIVE


def verdict_breakpoint(gain: float, margin: float = 2.0) -> str:
    """Veredito sobre a existência de salto, pelo ganho de AIC do modelo com corte."""
    if gain >= margin:
        return CONFIRMED
    if gain <= -margin:
        return REFUTED
    return INCONCLUSIVE


def verdict_adjustment(p_crude: float, p_adjusted: float) -> str:
    """Veredito de que uma diferença entre grupos se explica por outra variável.

    Sem diferença bruta não há o que explicar; se a diferença some depois do ajuste, a hipótese
    se confirma; se persiste, é refutada.
    """
    if p_crude >= ALPHA:
        return INCONCLUSIVE
    if p_adjusted >= ALPHA:
        return CONFIRMED
    return REFUTED
