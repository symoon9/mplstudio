"""Palette Suggestions section builder."""

from __future__ import annotations

import ipywidgets as widgets
from IPython.display import display

from .._ctx import _PanelCtx
from .._helpers import _section
from ... import style as S


def build(ctx: _PanelCtx) -> widgets.VBox:
    suggest_use_case = widgets.Dropdown(
        options=[("Any", None), ("Categorical", "categorical"),
                 ("Sequential", "sequential"), ("Diverging", "diverging")],
        value=None, description="Use case",
        style={"description_width": "68px"}, layout=widgets.Layout(width="100%"))
    suggest_bg = widgets.Dropdown(
        options=[("Any", None), ("Light bg", "light"), ("Dark bg", "dark")],
        value=None, description="Background",
        style={"description_width": "68px"}, layout=widgets.Layout(width="100%"))
    suggest_cb = widgets.Checkbox(value=True, description="Colorblind-safe only",
                                  layout=widgets.Layout(width="100%"))
    cb_recommend = widgets.Button(description="Find palettes", button_style="info",
                                  layout=widgets.Layout(width="100%"))
    recommend_out = widgets.Output()

    def _on_recommend(_):
        from ...palettes import recommend
        n = len(S.get_line_labels(ctx.fig)) or 3
        suggestions = recommend(n, colorblind_safe=suggest_cb.value,
                                use_case=suggest_use_case.value,
                                background=suggest_bg.value, top_k=4)
        with recommend_out:
            recommend_out.clear_output()
            if not suggestions:
                display(widgets.HTML("<i style='color:#888'>No matches.</i>"))
                return
            for p in suggestions:
                sw = "".join(
                    f"<span style='background:{c};display:inline-block;width:14px;"
                    f"height:14px;margin:1px;border-radius:2px'></span>"
                    for c in p["colors"][:n])
                display(widgets.HTML(
                    f"<b>{p['name']}</b> {sw}<br>"
                    f"<span style='font-size:0.82em;color:#555'>{p['description']}</span><br>"
                    f"<span style='font-size:0.78em;color:#888'>{p['source']}</span><br>"))

    cb_recommend.on_click(_on_recommend)
    return _section("Palette Suggestions", ctx.pid,
                    suggest_use_case, suggest_bg, suggest_cb,
                    cb_recommend, recommend_out)
