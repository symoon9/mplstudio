"""Shared widget-builder helpers used by section builders and _studio."""

from __future__ import annotations

import ipywidgets as widgets


# ── layout helpers ────────────────────────────────────────────────────────────

def _section(title: str, pid: str, *children) -> widgets.VBox:
    """Wrap *children* in a themed card with a section title label."""
    vbox = widgets.VBox(
        [widgets.HTML(f"<span class='mpl-t-{pid}'>{title}</span>"), *children],
        layout=widgets.Layout(padding="10px 12px", overflow="hidden"),
    )
    vbox.add_class(f"mpl-c-{pid}")
    return vbox


def _per_btn(label: str, pid: str) -> tuple[widgets.Button, widgets.VBox, list]:
    """Return (button, hidden_box, open_flag). Caller appends children to hidden_box.

    Uses flag=[False] mutable list because Python closures cannot rebind a bare bool.
    """
    box = widgets.VBox([], layout=widgets.Layout(width="100%", display="none", padding="4px 0 0 0"))
    flag = [False]
    btn = widgets.Button(description=f"{label}  ▾", button_style="",
                         layout=widgets.Layout(width="100%"))
    btn.add_class(f"mpl-per-{pid}")
    btn.add_class(f"mpl-per-btn")

    def _toggle(_):
        flag[0] = not flag[0]
        box.layout.display = "" if flag[0] else "none"
        btn.description = f"{label}  {'▴' if flag[0] else '▾'}"

    btn.on_click(_toggle)
    return btn, box, flag


def _mk_slider(cls, description: str, dw: str = "82px", **kw) -> widgets.Widget:
    """Return a themed Int/FloatSlider with consistent style.

    Args:
        cls: widgets.IntSlider or widgets.FloatSlider
        description: label text
        dw: description_width (CSS string)
        **kw: forwarded to the slider constructor
    """
    kw.setdefault("layout", widgets.Layout(width="100%"))
    kw.setdefault("continuous_update", False)
    kw.setdefault("readout", True)
    return cls(description=description, style={"description_width": dw}, **kw)


def _lim_sliders(lo_init: float, hi_init: float):
    """Return (lo_sl, hi_sl) FloatSlider pair for xlim/ylim blocks.

    readout=True makes the readout box directly editable as a text field.
    """
    r = max(abs(hi_init - lo_init), 1e-9)
    kw = dict(min=lo_init - r * 2, max=hi_init + r * 2, step=r / 100,
              continuous_update=False, readout=True,
              layout=widgets.Layout(width="100%"))
    lo_sl = widgets.FloatSlider(value=lo_init, description="min",
                                style={"description_width": "28px"}, **kw)
    hi_sl = widgets.FloatSlider(value=hi_init, description="max",
                                style={"description_width": "28px"}, **kw)
    return lo_sl, hi_sl


# ── visual preview helpers ────────────────────────────────────────────────────

def _swatches_div(colors: list[str]) -> str:
    spans = "".join(
        f"<span style='background:{c};display:inline-block;width:16px;height:16px;"
        f"margin:2px 2px 0 0;border-radius:3px;border:1px solid #ccc'></span>"
        for c in colors)
    return f"<div style='display:flex;flex-wrap:wrap;margin-top:4px'>{spans}</div>"


def _build_palette_preview(name: str) -> widgets.HTML:
    from ..palettes import get_palette
    return widgets.HTML(value=_swatches_div(get_palette(name)))


def _build_colormap_gradient(cmap_name: str, steps: int = 24) -> widgets.HTML:
    import matplotlib.cm as cm
    import matplotlib.colors as mcolors
    try:
        cmap = cm.get_cmap(cmap_name)
    except ValueError:
        return widgets.HTML(value="")
    stops = ", ".join(mcolors.to_hex(cmap(i / (steps - 1))) for i in range(steps))
    return widgets.HTML(value=(
        f"<div style='background:linear-gradient(to right,{stops});"
        f"height:14px;border-radius:6px;margin-top:4px;border:1px solid #ccc'></div>"))
