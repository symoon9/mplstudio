"""Axes section builder."""

from __future__ import annotations

import ipywidgets as widgets

from .._ctx import _PanelCtx
from .._helpers import _section, _lim_sliders
from ... import style as S


def build(ctx: _PanelCtx) -> widgets.VBox | None:
    if not ctx.fig.axes:
        return None

    ax_selector = None
    if len(ctx.fig.axes) > 1:
        ax_selector = widgets.Dropdown(
            options=[(f"Axes {i}", i) for i in range(len(ctx.fig.axes))],
            value=0, description="Axes:",
            style={"description_width": "40px"},
            layout=widgets.Layout(width="100%"))

    def _cur_ax():
        return ctx.fig.axes[ctx.ax_idx[0]]

    title_input = widgets.Text(
        value=_cur_ax().get_title(), description="Title",
        style={"description_width": "50px"},
        layout=widgets.Layout(width="100%"), continuous_update=False)
    xlabel_input = widgets.Text(
        value=_cur_ax().get_xlabel(), description="X label",
        style={"description_width": "50px"},
        layout=widgets.Layout(width="100%"), continuous_update=False)
    ylabel_input = widgets.Text(
        value=_cur_ax().get_ylabel(), description="Y label",
        style={"description_width": "50px"},
        layout=widgets.Layout(width="100%"), continuous_update=False)

    xlim = _cur_ax().get_xlim()
    ylim = _cur_ax().get_ylim()

    xlim_lo, xlim_hi = _lim_sliders(xlim[0], xlim[1])
    ylim_lo, ylim_hi = _lim_sliders(ylim[0], ylim[1])

    xlim_hdr = widgets.HTML(
        "<span style='font-size:0.8em;font-weight:600;color:#555;margin-top:4px;"
        "display:block'>xlim</span>")
    ylim_hdr = widgets.HTML(
        "<span style='font-size:0.8em;font-weight:600;color:#555;margin-top:4px;"
        "display:block'>ylim</span>")

    def _on_xlim(_):
        S.set_xlim(ctx.fig, xlim_lo.value, xlim_hi.value, ctx.ax_idx[0])
        ctx.refresh()

    def _on_ylim(_):
        S.set_ylim(ctx.fig, ylim_lo.value, ylim_hi.value, ctx.ax_idx[0])
        ctx.refresh()

    def _on_title(_):
        S.set_title(ctx.fig, title_input.value, ctx.ax_idx[0])
        ctx.refresh()

    def _on_xlabel(_):
        S.set_xlabel(ctx.fig, xlabel_input.value, ctx.ax_idx[0])
        ctx.refresh()

    def _on_ylabel(_):
        S.set_ylabel(ctx.fig, ylabel_input.value, ctx.ax_idx[0])
        ctx.refresh()

    xlim_lo.observe(_on_xlim, names="value")
    xlim_hi.observe(_on_xlim, names="value")
    ylim_lo.observe(_on_ylim, names="value")
    ylim_hi.observe(_on_ylim, names="value")
    title_input.observe(_on_title, names="value")
    xlabel_input.observe(_on_xlabel, names="value")
    ylabel_input.observe(_on_ylabel, names="value")

    def _on_ax_select(c):
        ctx.ax_idx[0] = c["new"]
        ax = ctx.fig.axes[ctx.ax_idx[0]]
        title_input.value = ax.get_title()
        xlabel_input.value = ax.get_xlabel()
        ylabel_input.value = ax.get_ylabel()
        xl = ax.get_xlim()
        yl = ax.get_ylim()
        # Clamp to slider range to avoid ipywidgets exception
        xlim_lo.value = max(xlim_lo.min, min(xlim_lo.max, xl[0]))
        xlim_hi.value = max(xlim_hi.min, min(xlim_hi.max, xl[1]))
        ylim_lo.value = max(ylim_lo.min, min(ylim_lo.max, yl[0]))
        ylim_hi.value = max(ylim_hi.min, min(ylim_hi.max, yl[1]))

    if ax_selector:
        ax_selector.observe(_on_ax_select, names="value")

    axes_children = (
        ([ax_selector] if ax_selector else [])
        + [title_input, xlabel_input, ylabel_input,
           xlim_hdr, xlim_lo, xlim_hi,
           ylim_hdr, ylim_lo, ylim_hi]
    )
    return _section("Axes", ctx.pid, *axes_children)
