"""Colors section builder."""

from __future__ import annotations

import ipywidgets as widgets

from .._ctx import _PanelCtx
from .._helpers import _section, _swatches_div, _build_palette_preview, _build_colormap_gradient
from ... import style as S
from ...palettes import palette_names, get_palette, SEQUENTIAL_CMAPS, DIVERGING_CMAPS, smart_palette


def build(ctx: _PanelCtx) -> widgets.VBox:
    plot_type = S.detect_plot_type(ctx.fig)
    n_series = len(S.get_line_labels(ctx.fig))

    _type_label = {
        "categorical": f"categorical · {n_series} series",
        "continuous":  "continuous (colormap)",
        "mixed":       f"mixed · {n_series} categorical + colormap",
    }[plot_type]
    type_badge = widgets.HTML(
        f"<span style='font-size:0.9em;color:#888'>Detected: {_type_label}</span>")

    cat_box_children: list[widgets.Widget] = []

    if plot_type in ("categorical", "mixed"):
        _has_palette = ctx.palette is not None
        # Smart mode is kept in code but hidden from UI (#28)
        _mode_options = ["Palette", "Manual"]
        if _has_palette:
            _mode_options = ["Custom"] + _mode_options
        color_mode = widgets.ToggleButtons(
            options=_mode_options, value=_mode_options[0],
            description="Mode:", style={"button_width": "62px"},
            layout=widgets.Layout(width="100%", margin="4px 4px"))

        _pal_names = palette_names()
        _pal_options = [(f"{n}  ({len(get_palette(n))})", n) for n in _pal_names]
        palette_select = widgets.Dropdown(
            options=_pal_options, description="Palette",
            style={"description_width": "58px"},
            layout=widgets.Layout(width="95%"))
        palette_preview_w = _build_palette_preview(_pal_names[0])
        palette_col = widgets.VBox([palette_select, palette_preview_w],
                                   layout=widgets.Layout(width="95%"))
        palette_col.layout.display = "none" if _has_palette else ""

        line_colors = S.get_line_colors(ctx.fig)
        line_labels = S.get_line_labels(ctx.fig)

        # Pre-fill Manual pickers from ctx.palette when available
        def _picker_color(lbl: str, default: str) -> str:
            if ctx.palette and lbl in ctx.palette:
                return ctx.palette[lbl]
            return default

        manual_pickers = [
            widgets.ColorPicker(
                value=_picker_color(lbl, c),
                description=(lbl[:13] + "…" if len(lbl) > 13 else lbl),
                style={"description_width": "82px"}, concise=False,
                layout=widgets.Layout(width="90%"))
            for c, lbl in zip(line_colors, line_labels)
        ]
        manual_section = widgets.VBox(
            manual_pickers or [widgets.HTML("<i style='color:#888'>No labeled series.</i>")])
        manual_section.layout.display = "none"

        _smart_init_n = max(2, min(n_series or 5, 10))
        smart_n = widgets.IntSlider(
            value=_smart_init_n, min=2, max=20, step=1,
            description="Colors (n)", style={"description_width": "78px"},
            layout=widgets.Layout(width="100%"), continuous_update=False)
        smart_preview_w = widgets.HTML(value=_swatches_div(smart_palette(_smart_init_n)))
        smart_section = widgets.VBox([smart_n, smart_preview_w],
                                     layout=widgets.Layout(width="100%"))
        smart_section.layout.display = "none"

        # Custom section: read-only swatches from ctx.palette
        if _has_palette:
            _custom_colors = [ctx.palette.get(lbl, c) for c, lbl in zip(line_colors, line_labels)]
            custom_section = widgets.VBox(
                [widgets.HTML(_swatches_div(_custom_colors))] if _custom_colors
                else [widgets.HTML("<i style='color:#888'>No matching labels.</i>")],
                layout=widgets.Layout(width="100%"))
        else:
            custom_section = widgets.VBox([])
            custom_section.layout.display = "none"

        def _apply_colors():
            m = color_mode.value
            if m == "Custom":
                S.set_line_colors_manual(ctx.fig, [ctx.palette.get(lbl, c)
                                                    for c, lbl in zip(line_colors, line_labels)])
            elif m == "Manual":
                S.set_line_colors_manual(ctx.fig, [p.value for p in manual_pickers])
            elif m == "Smart":
                S.set_line_colors_manual(ctx.fig, smart_palette(smart_n.value))
            else:
                S.set_line_colors(ctx.fig, palette_select.value)
            ctx.refresh()

        def _on_palette_change(c):
            palette_preview_w.value = _build_palette_preview(c["new"]).value
            _apply_colors()

        def _on_smart_n(c):
            smart_preview_w.value = _swatches_div(smart_palette(c["new"]))
            _apply_colors()

        def _on_color_mode_change(c):
            custom_section.layout.display = "none"
            palette_col.layout.display = "none"
            manual_section.layout.display = "none"
            smart_section.layout.display = "none"
            if c["new"] == "Custom":
                custom_section.layout.display = ""
            elif c["new"] == "Manual":
                manual_section.layout.display = ""
            elif c["new"] == "Smart":
                smart_section.layout.display = ""
            else:
                palette_col.layout.display = ""
            _apply_colors()

        palette_select.observe(_on_palette_change, names="value")
        color_mode.observe(_on_color_mode_change, names="value")
        smart_n.observe(_on_smart_n, names="value")
        for p in manual_pickers:
            p.observe(lambda _: _apply_colors(), names="value")

        cat_box_children = [color_mode, custom_section, palette_col, manual_section, smart_section]

    cmap_box_children: list[widgets.Widget] = []

    if plot_type in ("continuous", "mixed"):
        if plot_type == "mixed":
            cmap_box_children.append(widgets.HTML("<hr style='margin:4px 0'>"))
        cmap_type_tb = widgets.ToggleButtons(
            options=["Sequential", "Diverging"], value="Sequential",
            style={"button_width": "90px"}, layout=widgets.Layout(width="100%"))
        _init_cmap = S.get_colormap(ctx.fig) or "viridis"
        _init_type = "Sequential" if _init_cmap in SEQUENTIAL_CMAPS else "Diverging"
        cmap_type_tb.value = _init_type
        cmap_select = widgets.Dropdown(
            options=SEQUENTIAL_CMAPS if _init_type == "Sequential" else DIVERGING_CMAPS,
            value=_init_cmap if _init_cmap in (SEQUENTIAL_CMAPS + DIVERGING_CMAPS) else SEQUENTIAL_CMAPS[0],
            description="Colormap", style={"description_width": "68px"},
            layout=widgets.Layout(width="100%"))
        cmap_grad_w = _build_colormap_gradient(cmap_select.value)

        def _on_cmap_type(c):
            opts = SEQUENTIAL_CMAPS if c["new"] == "Sequential" else DIVERGING_CMAPS
            cmap_select.options = opts
            cmap_select.value = opts[0]

        def _on_cmap(c):
            cmap_grad_w.value = _build_colormap_gradient(c["new"]).value
            S.set_colormap(ctx.fig, c["new"])
            ctx.refresh()

        cmap_type_tb.observe(_on_cmap_type, names="value")
        cmap_select.observe(_on_cmap, names="value")
        cmap_box_children += [cmap_type_tb, cmap_select, cmap_grad_w]

    bg_color = widgets.ColorPicker(
        value="#ffffff", description="Background",
        style={"description_width": "82px"}, concise=False,
        layout=widgets.Layout(width="100%"))

    def _on_bg(c):
        if len(c["new"]) == 7:
            S.set_background_color(ctx.fig, c["new"])
            ctx.refresh()

    bg_color.observe(_on_bg, names="value")
    return _section("Colors", ctx.pid, type_badge,
                    *cat_box_children, *cmap_box_children, bg_color)
