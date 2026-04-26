"""Legend section builder."""

from __future__ import annotations

import ipywidgets as widgets

from .._ctx import _PanelCtx
from .._helpers import _section
from ... import style as S


def build(ctx: _PanelCtx) -> widgets.VBox:
    legend_loc = widgets.Dropdown(
        options=S.LEGEND_LOCATIONS, value="best",
        description="Location", style={"description_width": "68px"},
        layout=widgets.Layout(width="100%"))

    def _on_legend_loc(_):
        S.set_legend_position(ctx.fig, legend_loc.value)
        ctx.refresh()

    legend_loc.observe(_on_legend_loc, names="value")

    leg0 = ctx.fig.axes[0].get_legend() if ctx.fig.axes else None
    leg_texts = [t.get_text() for t in leg0.get_texts()] if leg0 else []
    name_inputs = [
        widgets.Text(value=txt,
                     description=(txt[:12] + "…:" if len(txt) > 12 else f"{txt}:"),
                     style={"description_width": "78px"},
                     layout=widgets.Layout(width="100%"), continuous_update=False)
        for txt in leg_texts
    ]

    def _on_legend_name(_):
        S.set_legend_labels(ctx.fig, [i.value for i in name_inputs])
        ctx.refresh()

    for inp in name_inputs:
        inp.observe(_on_legend_name, names="value")

    bbox_header = widgets.HTML(
        "<span style='font-size:0.82em;color:#888'>BBox position (x, y)</span>")
    bbox_x = widgets.FloatSlider(value=1.02, min=0.0, max=1.5, step=0.01,
                                 description="x", style={"description_width": "20px"},
                                 layout=widgets.Layout(width="100%"), continuous_update=False)
    bbox_y = widgets.FloatSlider(value=1.0, min=0.0, max=1.5, step=0.01,
                                 description="y", style={"description_width": "20px"},
                                 layout=widgets.Layout(width="100%"), continuous_update=False)

    def _on_bbox(_):
        S.set_legend_bbox(ctx.fig, bbox_x.value, bbox_y.value)
        ctx.refresh()

    bbox_x.observe(_on_bbox, names="value")
    bbox_y.observe(_on_bbox, names="value")

    legend_children = (
        [legend_loc]
        + (name_inputs or [widgets.HTML("<i style='color:#888;font-size:0.85em'>No entries.</i>")])
        + [bbox_header, bbox_x, bbox_y]
    )
    return _section("Legend", ctx.pid, *legend_children)
