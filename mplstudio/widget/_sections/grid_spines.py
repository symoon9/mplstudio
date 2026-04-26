"""Grid & Spines section builder."""

from __future__ import annotations

import ipywidgets as widgets

from .._ctx import _PanelCtx
from .._helpers import _section
from ... import style as S


def build(ctx: _PanelCtx) -> widgets.VBox:
    grid_toggle = widgets.Checkbox(value=False, description="Show grid")
    spine_style = widgets.ToggleButtons(
        options=S.SPINE_STYLES, value="box",
        description="Spines:", style={"button_width": "84px"},
        layout=widgets.Layout(width="100%"))

    def _on_grid(_):
        S.set_grid(ctx.fig, grid_toggle.value)
        ctx.refresh()

    def _on_spine(_):
        S.set_spine_style(ctx.fig, spine_style.value)
        ctx.refresh()

    grid_toggle.observe(_on_grid, names="value")
    spine_style.observe(_on_spine, names="value")
    return _section("Grid & Spines", ctx.pid, grid_toggle, spine_style)
