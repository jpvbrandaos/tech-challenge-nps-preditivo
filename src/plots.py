"""Gráficos da análise exploratória e da modelagem, com o mesmo estilo em todas as figuras."""

from collections.abc import Iterable

from matplotlib.colors import TwoSlopeNorm
from matplotlib.patches import Rectangle
import matplotlib.pyplot as plt
import numpy as np
from numpy.typing import ArrayLike
import pandas as pd
import seaborn as sns
from sklearn.metrics import roc_auc_score, roc_curve

from src.analysis import MIN_GROUP_SIZE
from src.config import FIGURES_DIR

ACCENT = "#3164A8"
MUTED = "#B8C4D6"
INK = "#2B2B2B"
CATEGORY_COLORS = {"detrator": "#C0504D", "neutro": MUTED, "promotor": ACCENT}

# Séries de modelo, em ordem fixa; o par foi conferido para daltonismo
SERIES_COLORS = [ACCENT, "#EB6834"]
CHANCE = "#9A9A9A"

# Amplitude da escala de cor dos mapas de calor, em pontos acima e abaixo da média
HEATMAP_SPAN = 20


def set_style() -> None:
    """Estilo único das figuras: fundo limpo, grade leve e fontes legíveis em slides."""
    sns.set_theme(style="whitegrid", rc={"axes.spines.top": False, "axes.spines.right": False})
    plt.rcParams.update(
        {
            "figure.dpi": 100,
            "axes.titlesize": 12,
            "axes.titleweight": "bold",
            "axes.labelsize": 10,
            "xtick.labelsize": 9,
            "ytick.labelsize": 9,
            "grid.color": "#E6E6E6",
        }
    )


def rate_limits(tables: Iterable[pd.DataFrame]) -> tuple[float, float]:
    """Faixa do eixo que mostra todos os pontos e os intervalos dos grupos com pedidos suficientes.

    Intervalos de grupos pequenos ficam de fora do cálculo: são largos demais e achatariam o resto.
    A margem passa um pouco de 0 e de 100 para os pontos nos extremos não ficarem cortados.
    """
    lows, highs = [], []
    for table in tables:
        value = table.iloc[:, 1]
        large = table["pedidos"] >= MIN_GROUP_SIZE
        lows += [value.min(), table.loc[large, "IC inferior"].min()]
        highs += [value.max(), table.loc[large, "IC superior"].max()]
    return max(-4.0, np.nanmin(lows) - 5), min(104.0, np.nanmax(highs) + 5)


def plot_rate(
    table: pd.DataFrame,
    ax: plt.Axes | None = None,
    kind: str = "point",
    reference: float | None = None,
    title: str | None = None,
    xlabel: str | None = None,
    ylim: tuple[float, float] | None = None,
) -> plt.Axes:
    """Percentual por grupo com intervalo de 95%, a partir de `analysis.rate_table`.

    Pontos, e não barras, porque o eixo se ajusta à faixa dos intervalos: com uma proporção alta
    em todos os grupos, barras a partir de zero esconderiam as diferenças. A linha tracejada é a
    média de referência, e grupos com menos de MIN_GROUP_SIZE pedidos aparecem vazados.
    """
    ax = ax or plt.subplots(figsize=(7, 3.5))[1]
    label = table.columns[1]
    value = table[label]
    low, high = table["IC inferior"], table["IC superior"]
    positions = list(range(len(table)))
    small = (table["pedidos"] < MIN_GROUP_SIZE).to_numpy()
    if kind == "line":
        ax.plot(positions, value, color=ACCENT, zorder=2)
        ax.fill_between(positions, low, high, color=MUTED, alpha=0.5, zorder=1)
    else:
        # Arredondamento numérico pode deixar uma margem levemente negativa
        errors = [(value - low).clip(lower=0), (high - value).clip(lower=0)]
        ax.errorbar(positions, value, yerr=errors, fmt="none", ecolor=INK, capsize=3, lw=1)
    ax.scatter(
        positions,
        value,
        s=45,
        zorder=3,
        color=[("white" if is_small else ACCENT) for is_small in small],
        edgecolor=ACCENT,
        linewidth=1.5,
    )
    if reference is not None:
        ax.axhline(reference, color=INK, lw=0.8, ls="--", zorder=0)
    ax.set_xticks(positions, [str(group) for group in table.index])
    ax.set_ylim(ylim or rate_limits([table]))
    ax.set_ylabel(label)
    ax.set_xlabel(xlabel or "")
    if title:
        ax.set_title(title)
    return ax


def grid(
    n_panels: int, ncols: int, panel_size: tuple[float, float], **kwargs
) -> tuple[plt.Figure, np.ndarray]:
    """Figura com um painel por gráfico; os painéis que sobram na última linha ficam ocultos."""
    nrows = -(-n_panels // ncols)
    fig, axes = plt.subplots(
        nrows,
        ncols,
        figsize=(panel_size[0] * ncols, panel_size[1] * nrows),
        squeeze=False,
        **kwargs,
    )
    for ax in axes.flat[n_panels:]:
        ax.set_visible(False)
    return fig, axes


def plot_rates(
    tables: dict[str, pd.DataFrame],
    ncols: int = 3,
    kind: str = "point",
    reference: float | None = None,
    rotation: int = 0,
    panel_size: tuple[float, float] = (5, 3.5),
) -> plt.Figure:
    """Um painel de `plot_rate` por tabela, todos na mesma escala para comparar os efeitos."""
    fig, axes = grid(len(tables), ncols, panel_size)
    ylim = rate_limits(tables.values())
    for ax, (title, table) in zip(axes.flat, tables.items()):
        plot_rate(table, ax=ax, kind=kind, reference=reference, title=title, ylim=ylim)
        if rotation:
            plt.setp(ax.get_xticklabels(), rotation=rotation, ha="right", rotation_mode="anchor")
    fig.tight_layout()
    return fig


def plot_rate_heatmap(
    rows: pd.Series,
    columns: pd.Series,
    target: pd.Series,
    ax: plt.Axes | None = None,
    title: str | None = None,
    colorbar: bool = True,
) -> plt.Axes:
    """Mapa de calor do percentual do alvo por duas variáveis, com os pedidos de cada célula.

    A cor mostra a distância para a média: vermelho acima, azul abaixo. Células com menos de
    MIN_GROUP_SIZE pedidos ficam hachuradas, porque não sustentam conclusão.
    """
    ax = ax or plt.subplots(figsize=(6, 4))[1]
    frame = pd.DataFrame({"linha": rows, "coluna": columns, "alvo": target})
    cells = frame.groupby(["linha", "coluna"], observed=True)["alvo"].agg(["mean", "size"])
    share = (100 * cells["mean"]).unstack("coluna")
    orders = cells["size"].unstack("coluna")
    annotation = (
        share.round().astype("Int64").astype(str)
        + "%\n("
        + orders.astype("Int64").astype(str)
        + ")"
    )
    center = 100 * target.mean()
    sns.heatmap(
        share,
        annot=annotation,
        fmt="",
        cmap="RdBu_r",
        norm=TwoSlopeNorm(
            vcenter=center,
            vmin=max(0, center - HEATMAP_SPAN),
            vmax=min(100, center + HEATMAP_SPAN),
        ),
        linewidths=0.5,
        cbar=colorbar,
        cbar_kws={"label": "% detratores"},
        ax=ax,
    )
    for i, row in enumerate(orders.index):
        for j, column in enumerate(orders.columns):
            if pd.isna(orders.loc[row, column]) or orders.loc[row, column] < MIN_GROUP_SIZE:
                ax.add_patch(
                    Rectangle((j, i), 1, 1, fill=False, hatch="///", edgecolor="#9A9A9A", lw=0)
                )
    ax.tick_params(axis="y", rotation=0)
    ax.set_xlabel(columns.name or "")
    ax.set_ylabel(rows.name or "")
    if title:
        ax.set_title(title)
    return ax


def plot_rate_heatmaps(
    pairs: dict[str, tuple[pd.Series, pd.Series]],
    target: pd.Series,
    ncols: int = 2,
    panel_size: tuple[float, float] = (7, 4.5),
) -> plt.Figure:
    """Um mapa de calor por par de variáveis, com uma escala de cor única para todos.

    Todos os mapas usam o mesmo alvo e, portanto, o mesmo centro de cor: uma barra basta.
    """
    fig, axes = grid(len(pairs), ncols, panel_size, layout="constrained")
    for ax, (title, (rows, columns)) in zip(axes.flat, pairs.items()):
        plot_rate_heatmap(rows, columns, target, ax=ax, title=title, colorbar=False)
    fig.colorbar(axes.flat[0].collections[0], ax=axes, shrink=0.5, label="% detratores")
    return fig


def plot_impact_frequency(
    impact: pd.DataFrame, ax: plt.Axes | None = None, title: str | None = None
) -> plt.Axes:
    """Cada falha num plano de presença entre os detratores contra impacto (risco relativo).

    As linhas tracejadas dividem o plano em quadrantes: à direita, falhas que a maioria dos
    detratores viveu; acima, falhas que aumentam a chance de detrator.
    """
    ax = ax or plt.subplots(figsize=(6, 4))[1]
    x = impact["presença entre detratores (%)"]
    y = impact["impacto"]
    ax.scatter(x, y, s=80, color=ACCENT, zorder=3)
    for name in impact.index:
        # Rótulos dos pontos mais à direita vão para a esquerda, para não sair do gráfico
        right_side = x[name] > 70
        ax.annotate(
            name,
            (x[name], y[name]),
            xytext=(-8 if right_side else 8, 6),
            textcoords="offset points",
            ha="right" if right_side else "left",
            fontsize=9,
            bbox={"boxstyle": "round,pad=0.2", "fc": "white", "ec": "none", "alpha": 0.8},
        )
    ax.axhline(1, color=INK, lw=0.8, ls="--")
    ax.axvline(50, color=INK, lw=0.8, ls="--")
    ax.set_xlim(0, 100)
    ax.set_xlabel("Presença entre os detratores (%)")
    ax.set_ylabel("Impacto (risco relativo)")
    if title:
        ax.set_title(title)
    return ax


def save_figure(fig: plt.Figure, name: str) -> None:
    """Salva a figura em reports/figures/, pronta para os slides."""
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIGURES_DIR / f"{name}.png", dpi=150, bbox_inches="tight")


def plot_roc_curves(
    y: ArrayLike,
    scores: dict[str, ArrayLike],
    reference: str | None = None,
    ax: plt.Axes | None = None,
    title: str | None = None,
) -> plt.Axes:
    """Curva ROC de cada ordenação dos mesmos pedidos, com a ROC-AUC na legenda.

    Cada ponto da curva é uma lista: a fração dos detratores e a dos não detratores que entram
    nela. Os modelos ganham as cores de SERIES_COLORS, na ordem; a ordenação `reference`, como a
    regra de dias de atraso, vem tracejada, como as linhas de referência dos outros gráficos. A
    diagonal pontilhada é o sorteio.
    """
    if len([name for name in scores if name != reference]) > len(SERIES_COLORS):
        raise ValueError(f"No máximo {len(SERIES_COLORS)} modelos por gráfico, além da referência")
    ax = ax or plt.subplots(figsize=(5, 5))[1]
    colors = iter(SERIES_COLORS)
    for name, score in scores.items():
        fpr, tpr, _ = roc_curve(y, score)
        style = {"color": INK, "ls": "--"} if name == reference else {"color": next(colors)}
        ax.plot(fpr, tpr, lw=2, label=f"{name}: {roc_auc_score(y, score):.3f}", **style)
    ax.plot([0, 1], [0, 1], color=CHANCE, lw=1, ls=":")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1.01)
    ax.set_aspect("equal")
    ax.set_xlabel("Fração dos não detratores na lista")
    ax.set_ylabel("Fração dos detratores na lista")
    ax.legend(title="ROC-AUC", frameon=False, loc="lower right")
    if title:
        ax.set_title(title)
    return ax


def plot_calibration(
    table: pd.DataFrame, ax: plt.Axes | None = None, title: str | None = None
) -> plt.Axes:
    """Proporção observada de detratores contra o risco médio previsto, por faixa de risco.

    Recebe a tabela de `evaluation.calibration_table`. Pontos sobre a diagonal indicam
    probabilidades fiéis; acima dela, o modelo subestima o risco. As barras são o intervalo de
    Wilson de 95% de cada faixa, e os eixos começam um pouco abaixo da menor faixa.
    """
    ax = ax or plt.subplots(figsize=(5, 5))[1]
    predicted = table["% previsto"]
    observed = table["% detratores"]
    errors = [
        (observed - table["IC inferior"]).clip(lower=0),
        (table["IC superior"] - observed).clip(lower=0),
    ]
    low = max(0.0, min(predicted.min(), table["IC inferior"].min()) - 5)
    ax.plot([low, 100], [low, 100], color=CHANCE, lw=1, ls=":")
    ax.errorbar(predicted, observed, yerr=errors, fmt="none", ecolor=INK, capsize=3, lw=1)
    ax.scatter(predicted, observed, s=45, color=ACCENT, zorder=3)
    ax.set_xlim(low, 101)
    ax.set_ylim(low, 101)
    ax.set_aspect("equal")
    ax.set_xlabel("Risco médio previsto (%)")
    ax.set_ylabel("% detratores observados")
    if title:
        ax.set_title(title)
    return ax
