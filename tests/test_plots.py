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
