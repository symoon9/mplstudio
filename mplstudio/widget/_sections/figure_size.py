"""Figure Size section builder."""

from __future__ import annotations

import ipywidgets as widgets

from .._ctx import _PanelCtx
from .._helpers import _section, _mk_slider
from ... import style as S


def build(ctx: _PanelCtx) -> widgets.VBox:
    w_init, h_init = ctx.fig.get_size_inches()
    fig_width  = _mk_slider(widgets.FloatSlider, "Width (in)",  "82px",
                            value=w_init, min=2, max=25, step=0.5)
    fig_height = _mk_slider(widgets.FloatSlider, "Height (in)", "82px",
                            value=h_init, min=2, max=25, step=0.5)

    def _on_size(_):
        S.set_figure_size(ctx.fig, fig_width.value, fig_height.value)
        ctx.refresh()

    fig_width.observe(_on_size, names="value")
    fig_height.observe(_on_size, names="value")
    return _section("Figure Size", ctx.pid, fig_width, fig_height)
