"""Grid & Spines section builder."""

from __future__ import annotations

import ipywidgets as widgets

from .._ctx import _PanelCtx
from .._helpers import _section
from ... import style as S


def build(ctx: _PanelCtx) -> widgets.VBox:
    grid_toggle = widgets.ToggleButtons(
        options=["Off", "On"], value="Off",
        description="Grid",
        style={"description_width": "32px", "button_width": "52px"},
        layout=widgets.Layout(width="100%"))

    spine_header = widgets.HTML(
        "<span style='font-size:0.82em;color:#888'>Spines</span>")
    spine_style = widgets.ToggleButtons(
        options=S.SPINE_STYLES, value="box",
        description="",
        style={"button_width": "74px"},
        layout=widgets.Layout(width="100%"))

    def _on_grid(_):
        S.set_grid(ctx.fig, grid_toggle.value == "On")
        ctx.refresh()

    def _on_spine(_):
        S.set_spine_style(ctx.fig, spine_style.value)
        ctx.refresh()

    grid_toggle.observe(_on_grid, names="value")
    spine_style.observe(_on_spine, names="value")
    return _section("Grid & Spines", ctx.pid, grid_toggle, spine_header, spine_style)
