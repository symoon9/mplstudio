"""Figure Size section builder."""

from __future__ import annotations

import ipywidgets as widgets

from .._ctx import _PanelCtx
from .._helpers import _section
from ... import style as S


def build(ctx: _PanelCtx) -> widgets.VBox:
    w_init, h_init = ctx.fig.get_size_inches()
    fig_width = widgets.FloatSlider(
        value=w_init, min=2, max=25, step=0.5, description="Width (in)",
        style={"description_width": "82px"},
        layout=widgets.Layout(width="100%"), continuous_update=False)
    fig_height = widgets.FloatSlider(
        value=h_init, min=2, max=25, step=0.5, description="Height (in)",
        style={"description_width": "82px"},
        layout=widgets.Layout(width="100%"), continuous_update=False)

    def _on_size(_):
        S.set_figure_size(ctx.fig, fig_width.value, fig_height.value)
        ctx.refresh()

    fig_width.observe(_on_size, names="value")
    fig_height.observe(_on_size, names="value")
    return _section("Figure Size", ctx.pid, fig_width, fig_height)
