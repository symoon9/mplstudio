"""Opacity (alpha) section builder."""

from __future__ import annotations

import ipywidgets as widgets

from .._ctx import _PanelCtx
from .._helpers import _section, _per_btn, _mk_slider
from ... import style as S


def build(ctx: _PanelCtx) -> widgets.VBox:
    alphas = S.get_series_alpha(ctx.fig)
    a_labels = S.get_line_labels(ctx.fig)
    init_global = (sum(alphas) / len(alphas)) if alphas else 1.0

    global_alpha = _mk_slider(widgets.FloatSlider, "All series", "82px",
                              value=init_global, min=0.0, max=1.0, step=0.05)

    alpha_sliders = [
        _mk_slider(widgets.FloatSlider,
                   (lbl[:13] + "…" if len(lbl) > 13 else lbl), "82px",
                   value=a, min=0.0, max=1.0, step=0.05,
                   layout=widgets.Layout(width="95%"))
        for a, lbl in zip(alphas, a_labels)
    ]

    def _on_global_alpha(c):
        if ctx.ab[0]:
            return
        ctx.ab[0] = True
        for s in alpha_sliders:
            s.value = c["new"]
        ctx.ab[0] = False
        S.set_series_alpha(ctx.fig, [c["new"]] * len(alpha_sliders))
        ctx.refresh()

    def _on_per_alpha(_):
        if ctx.ab[0]:
            return
        S.set_series_alpha(ctx.fig, [s.value for s in alpha_sliders])
        ctx.refresh()

    global_alpha.observe(_on_global_alpha, names="value")
    for s in alpha_sliders:
        s.observe(_on_per_alpha, names="value")

    alpha_children: list[widgets.Widget] = [global_alpha]
    if alpha_sliders:
        per_btn, per_box, _ = _per_btn("Per series", ctx.pid)
        per_box.children = tuple(alpha_sliders)
        alpha_children += [per_btn, per_box]
    else:
        alpha_children.append(
            widgets.HTML("<i style='color:#888'>No labeled series.</i>"))

    return _section("Opacity", ctx.pid, *alpha_children)
