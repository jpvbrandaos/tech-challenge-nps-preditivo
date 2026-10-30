import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd

from src import plots
from src.analysis import problem_impact, rate_table


def make_orders():
    data = pd.DataFrame({"group": ["a"] * 40 + ["b"] * 10, "is_detractor": [1, 0] * 20 + [1] * 10})
    data["nps_category"] = data["is_detractor"].map({1: "detrator", 0: "promotor"})
    return data


def test_plots_draw_rates_heatmaps_and_impact():
    data = make_orders()
    plots.plot_rate(rate_table(data, "group"))
    plots.plot_rate(rate_table(data, "group"), kind="line")
    plots.plot_rate_heatmap(data["group"], data["is_detractor"], data["is_detractor"])
    impact = problem_impact(data, pd.DataFrame({"falha": (data["group"] == "b").astype(int)}))
    plots.plot_impact_frequency(impact)
    fig = plots.plot_rates(
        {"a": rate_table(data, "group"), "b": rate_table(data, "group")}, ncols=2
    )
    assert len(fig.axes) == 2
    pairs = {"a": (data["group"], data["is_detractor"]), "b": (data["group"], data["group"])}
    fig = plots.plot_rate_heatmaps(pairs, data["is_detractor"])
    # Dois mapas e uma única barra de cor
    assert len(fig.axes) == 3
    plt.close("all")


def test_save_figure_writes_a_png(tmp_path, monkeypatch):
    monkeypatch.setattr(plots, "FIGURES_DIR", tmp_path)
    fig, _ = plt.subplots()
    plots.save_figure(fig, "teste")
    plt.close(fig)
    assert (tmp_path / "teste.png").exists()


def test_rate_limits_keep_every_point_in_view():
    data = make_orders()
    low, high = plots.rate_limits([rate_table(data, "group")])
    shares = rate_table(data, "group")["% detratores"]
    assert low <= shares.min() and shares.max() <= high


def test_plots_draw_roc_curves_and_calibration():
    y = [0, 0, 1, 1, 1, 0, 1, 1]
    scores = {
        "modelo": [0.1, 0.4, 0.35, 0.8, 0.7, 0.2, 0.9, 0.6],
        "regra": [0, 1, 1, 2, 2, 0, 3, 1],
    }
    ax = plots.plot_roc_curves(y, scores, reference="regra")
    # Uma curva por ordenação, mais a diagonal do sorteio
    assert len(ax.get_lines()) == 3
    table = pd.DataFrame(
        {
            "pedidos": [50, 50],
            "% previsto": [20.0, 60.0],
            "% detratores": [25.0, 55.0],
            "IC inferior": [15.0, 45.0],
            "IC superior": [35.0, 65.0],
        }
    )
    ax = plots.plot_calibration(table)
    assert ax.get_xlim() == ax.get_ylim()
    plt.close("all")
