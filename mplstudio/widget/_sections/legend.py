"""Legend section builder."""

from __future__ import annotations

import ipywidgets as widgets

from .._ctx import _PanelCtx
from .._helpers import _section, _per_btn, _mk_slider
from ... import style as S


def build(ctx: _PanelCtx) -> widgets.VBox:
    # ── Legend title ──────────────────────────────────────────────────────
    leg0 = ctx.fig.axes[0].get_legend() if ctx.fig.axes else None
    init_title = leg0.get_title().get_text() if leg0 else ""

    title_input = widgets.Text(
        value=init_title, description="Title",
        placeholder="Legend title",
        style={"description_width": "46px"},
        layout=widgets.Layout(width="100%"), continuous_update=False)

    def _on_title(_):
        S.set_legend_title(ctx.fig, title_input.value)
        ctx.refresh()

    title_input.observe(_on_title, names="value")

    # ── Location dropdown ─────────────────────────────────────────────────
    legend_loc = widgets.Dropdown(
        options=S.LEGEND_LOCATIONS, value="best",
        description="Location", style={"description_width": "68px"},
        layout=widgets.Layout(width="100%"))

    def _on_legend_loc(_):
        S.set_legend_position(ctx.fig, legend_loc.value)
        ctx.refresh()

    legend_loc.observe(_on_legend_loc, names="value")

    # ── BBox position ─────────────────────────────────────────────────────
    bbox_header = widgets.HTML(
        "<span style='font-size:0.82em;color:#888'>BBox position (x, y)</span>")
    bbox_x = _mk_slider(widgets.FloatSlider, "x", "20px",
                        value=1.02, min=0.0, max=1.5, step=0.01)
    bbox_y = _mk_slider(widgets.FloatSlider, "y", "20px",
                        value=1.0, min=0.0, max=1.5, step=0.01)

    def _on_bbox(_):
        S.set_legend_bbox(ctx.fig, bbox_x.value, bbox_y.value)
        ctx.refresh()

    bbox_x.observe(_on_bbox, names="value")
    bbox_y.observe(_on_bbox, names="value")

    # ── Collapsible series labels ─────────────────────────────────────────
    leg_texts = [t.get_text() for t in leg0.get_texts()] if leg0 else []
    name_inputs = [
        widgets.Text(value=txt,
                     description=(txt[:12] + "…:" if len(txt) > 12 else f"{txt}:"),
                     style={"description_width": "78px"},
                     layout=widgets.Layout(width="90%"), continuous_update=False)
        for txt in leg_texts
    ]

    def _on_legend_name(_):
        S.set_legend_labels(ctx.fig, [i.value for i in name_inputs])
        ctx.refresh()

    for inp in name_inputs:
        inp.observe(_on_legend_name, names="value")

    if name_inputs:
        labels_btn, labels_box, _ = _per_btn("Series labels", ctx.pid)
        labels_box.children = tuple(name_inputs)
        labels_section = [labels_btn, labels_box]
    else:
        labels_section = [
            widgets.HTML("<i style='color:#888;font-size:0.85em'>No entries.</i>")]

    # ── Layout: title → location → bbox → labels toggle ──────────────────
    children = [
        title_input,
        legend_loc,
        bbox_header, bbox_x, bbox_y,
        *labels_section,
    ]
    return _section("Legend", ctx.pid, *children)
