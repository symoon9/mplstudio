"""Typography section builder."""

from __future__ import annotations

import ipywidgets as widgets

from .._ctx import _PanelCtx
from .._helpers import _section, _per_btn
from ... import style as S


def build(ctx: _PanelCtx) -> widgets.VBox:
    _ax0 = ctx.fig.axes[0] if ctx.fig.axes else None

    def _fs(fn, default=12):
        try:
            return int(round(fn()))
        except Exception:
            return default

    _i_all    = _fs(lambda: _ax0.xaxis.label.get_fontsize())
    _i_title  = _fs(lambda: _ax0.title.get_fontsize())
    _i_xlabel = _fs(lambda: _ax0.xaxis.label.get_fontsize())
    _i_ylabel = _fs(lambda: _ax0.yaxis.label.get_fontsize())
    _i_ticks  = _fs(lambda: _ax0.xaxis.get_ticklabels()[0].get_fontsize()
                    if _ax0 and _ax0.xaxis.get_ticklabels() else max(_i_all - 2, 6))
    _i_legend = _fs(lambda: _ax0.get_legend().get_texts()[0].get_fontsize()
                    if _ax0 and _ax0.get_legend() else _i_all)

    def _fsl(desc, init, dw="78px"):
        return widgets.IntSlider(value=init, min=6, max=40, step=1,
                                 description=desc, style={"description_width": dw},
                                 layout=widgets.Layout(width="100%"),
                                 continuous_update=False)

    font_all    = _fsl("All",     _i_all,    "82px")
    font_title  = _fsl("Title",   _i_title)
    font_xlabel = _fsl("X label", _i_xlabel)
    font_ylabel = _fsl("Y label", _i_ylabel)
    font_ticks  = _fsl("Ticks",   _i_ticks)
    font_legend = _fsl("Legend",  _i_legend)

    def _on_font_all(change):
        if ctx.fb[0]:
            return
        ctx.fb[0] = True
        v = change["new"]
        for s, vv in [(font_title, v), (font_xlabel, v), (font_ylabel, v),
                      (font_ticks, max(v - 2, 6)), (font_legend, v)]:
            s.value = vv
        ctx.fb[0] = False
        S.set_font_size(ctx.fig, v)
        ctx.refresh()

    def _on_font_title(c):
        if ctx.fb[0]:
            return
        [ax.title.set_fontsize(c["new"]) for ax in ctx.fig.axes]
        ctx.refresh()

    def _on_font_xlabel(c):
        if ctx.fb[0]:
            return
        [ax.xaxis.label.set_fontsize(c["new"]) for ax in ctx.fig.axes]
        ctx.refresh()

    def _on_font_ylabel(c):
        if ctx.fb[0]:
            return
        [ax.yaxis.label.set_fontsize(c["new"]) for ax in ctx.fig.axes]
        ctx.refresh()

    def _on_font_ticks(c):
        if ctx.fb[0]:
            return
        [ax.tick_params(labelsize=c["new"]) for ax in ctx.fig.axes]
        ctx.refresh()

    def _on_font_legend(c):
        if ctx.fb[0]:
            return
        for ax in ctx.fig.axes:
            lg = ax.get_legend()
            if lg:
                [t.set_fontsize(c["new"]) for t in lg.get_texts()]
        ctx.refresh()

    font_all.observe(_on_font_all, names="value")
    font_title.observe(_on_font_title, names="value")
    font_xlabel.observe(_on_font_xlabel, names="value")
    font_ylabel.observe(_on_font_ylabel, names="value")
    font_ticks.observe(_on_font_ticks, names="value")
    font_legend.observe(_on_font_legend, names="value")

    per_btn, per_box, _ = _per_btn("Per element", ctx.pid)
    per_box.children = (font_title, font_xlabel, font_ylabel, font_ticks, font_legend)
    return _section("Typography", ctx.pid, font_all, per_btn, per_box)
