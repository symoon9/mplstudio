"""Ticks section builder."""

from __future__ import annotations

import ipywidgets as widgets

from .._ctx import _PanelCtx
from .._helpers import _section, _mk_slider
from ... import style as S


def build(ctx: _PanelCtx) -> widgets.VBox | None:
    if not ctx.fig.axes:
        return None

    def _cur_ax():
        return ctx.fig.axes[ctx.ax_idx[0]]

    # ── tick label visibility ─────────────────────────────────────────────
    x_vis = widgets.ToggleButtons(
        options=["On", "Off"],
        value="On" if _cur_ax().get_xticklabels() else "Off",
        description="X labels",
        style={"button_width": "42px"},
        layout=widgets.Layout(width="100%"),
    )
    y_vis = widgets.ToggleButtons(
        options=["On", "Off"],
        value="On" if _cur_ax().get_yticklabels() else "Off",
        description="Y labels",
        style={"button_width": "42px"},
        layout=widgets.Layout(width="100%"),
    )

    # ── x-tick rotation ───────────────────────────────────────────────────
    _init_rot = 0
    xlabels = _cur_ax().get_xticklabels()
    if xlabels:
        _init_rot = int(xlabels[0].get_rotation())

    x_rot = _mk_slider(
        widgets.IntSlider, "X rotation", "68px",
        value=_init_rot, min=0, max=90, step=15,
    )

    # ── tick intervals ────────────────────────────────────────────────────
    interval_hdr = widgets.HTML(
        "<span style='font-size:0.8em;font-weight:600;color:#555;"
        "margin-top:6px;display:block'>Interval &nbsp;"
        "<span style='font-weight:400'>(0 = auto)</span></span>"
    )
    x_interval = widgets.BoundedFloatText(
        value=0.0, min=0.0, step=0.5,
        description="X",
        style={"description_width": "20px"},
        layout=widgets.Layout(width="48%"),
    )
    y_interval = widgets.BoundedFloatText(
        value=0.0, min=0.0, step=0.5,
        description="Y",
        style={"description_width": "20px"},
        layout=widgets.Layout(width="48%"),
    )
    interval_row = widgets.HBox(
        [x_interval, y_interval],
        layout=widgets.Layout(width="100%", justify_content="space-between"),
    )

    # ── callbacks ─────────────────────────────────────────────────────────
    def _on_x_vis(c):
        S.set_tick_labels_visible(
            ctx.fig,
            x=(c["new"] == "On"),
            y=(y_vis.value == "On"),
            ax_idx=ctx.ax_idx[0],
        )
        ctx.refresh()

    def _on_y_vis(c):
        S.set_tick_labels_visible(
            ctx.fig,
            x=(x_vis.value == "On"),
            y=(c["new"] == "On"),
            ax_idx=ctx.ax_idx[0],
        )
        ctx.refresh()

    def _on_x_rot(c):
        S.set_xtick_rotation(ctx.fig, c["new"], ctx.ax_idx[0])
        ctx.refresh()

    def _on_interval(_):
        S.set_tick_interval(
            ctx.fig,
            x_interval.value or None,
            y_interval.value or None,
            ctx.ax_idx[0],
        )
        ctx.refresh()

    x_vis.observe(_on_x_vis, names="value")
    y_vis.observe(_on_y_vis, names="value")
    x_rot.observe(_on_x_rot, names="value")
    x_interval.observe(_on_interval, names="value")
    y_interval.observe(_on_interval, names="value")

    return _section(
        "Ticks", ctx.pid,
        x_vis, x_rot, y_vis,
        interval_hdr, interval_row,
    )
