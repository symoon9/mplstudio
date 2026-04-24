"""ipywidgets control panel for mplstudio."""

from __future__ import annotations

import matplotlib.pyplot as plt
import ipywidgets as widgets
from IPython.display import display
from matplotlib.figure import Figure

import matplotlib.colors as mcolors

from . import style as S
from .palettes import PALETTES, palette_names


_RENDER_MODES = ["in-place (ipympl)", "re-render"]


def studio(fig: Figure | None = None, *, render_mode: str = "in-place (ipympl)") -> None:
    """Display the mplstudio control panel for *fig*.

    Parameters
    ----------
    fig:
        Target figure. Defaults to ``plt.gcf()``.
    render_mode:
        ``"in-place (ipympl)"`` mutates the live canvas; ``"re-render"``
        calls ``plt.show()`` after each change (works with any backend).
    """
    if fig is None:
        fig = plt.gcf()

    # ── render mode selector ──────────────────────────────────────────────
    render_toggle = widgets.ToggleButtons(
        options=_RENDER_MODES,
        value=render_mode,
        description="Render:",
        style={"button_width": "160px"},
        layout=widgets.Layout(margin="0 0 8px 0"),
    )

    # ── figure size ───────────────────────────────────────────────────────
    w_init, h_init = fig.get_size_inches()
    fig_width = widgets.FloatSlider(
        value=w_init, min=2, max=24, step=0.5,
        description="Width (in)", style={"description_width": "100px"},
        continuous_update=False,
    )
    fig_height = widgets.FloatSlider(
        value=h_init, min=2, max=24, step=0.5,
        description="Height (in)", style={"description_width": "100px"},
        continuous_update=False,
    )

    # ── font ──────────────────────────────────────────────────────────────
    font_size = widgets.IntSlider(
        value=12, min=6, max=32, step=1,
        description="Font size", style={"description_width": "100px"},
        continuous_update=False,
    )

    # ── colors ────────────────────────────────────────────────────────────
    color_mode = widgets.ToggleButtons(
        options=["Palette", "Manual"],
        value="Palette",
        description="Color mode:",
        style={"button_width": "80px"},
        layout=widgets.Layout(margin="0 0 4px 0"),
    )

    # palette sub-section
    palette_select = widgets.Dropdown(
        options=palette_names(),
        description="Palette",
        style={"description_width": "100px"},
    )
    palette_preview = _build_palette_preview(palette_names()[0])

    # manual sub-section — one ColorPicker per line, initialised to current color
    line_colors = S.get_line_colors(fig)
    line_labels = S.get_line_labels(fig)
    manual_pickers = [
        widgets.ColorPicker(
            value=color,
            description=(label[:14] + "…" if len(label) > 14 else label),
            style={"description_width": "90px"},
            concise=False,
            layout=widgets.Layout(width="340px"),
        )
        for color, label in zip(line_colors, line_labels)
    ]
    manual_section = widgets.VBox(
        manual_pickers if manual_pickers
        else [widgets.HTML("<i style='color:#888'>No lines found in figure.</i>")]
    )
    manual_section.layout.display = "none"

    bg_color = widgets.ColorPicker(
        value="#ffffff", description="Background",
        style={"description_width": "100px"},
        concise=False,
    )

    # ── legend ────────────────────────────────────────────────────────────
    legend_loc = widgets.Dropdown(
        options=S.LEGEND_LOCATIONS,
        value="best",
        description="Legend loc", style={"description_width": "100px"},
    )

    # ── grid & spines ─────────────────────────────────────────────────────
    grid_toggle = widgets.Checkbox(value=True, description="Show grid")
    spine_style = widgets.ToggleButtons(
        options=S.SPINE_STYLES,
        value="box",
        description="Spines:",
        style={"button_width": "100px"},
    )

    # ── colorblind recommendation ─────────────────────────────────────────
    cb_recommend = widgets.Button(
        description="Recommend colorblind-safe palette",
        button_style="info",
        layout=widgets.Layout(width="260px"),
    )
    recommend_out = widgets.Output()

    # ── re-render output widget (only used in re-render mode) ─────────────
    # Keeps the figure alive — plt.close() would destroy the canvas and break
    # subsequent apply calls.
    render_out = widgets.Output()

    # ── apply button ──────────────────────────────────────────────────────
    apply_btn = widgets.Button(
        description="Apply",
        button_style="success",
        icon="check",
        layout=widgets.Layout(width="120px"),
    )
    status = widgets.HTML(value="")

    # ── callbacks ─────────────────────────────────────────────────────────

    def _refresh():
        if render_toggle.value == "re-render":
            with render_out:
                render_out.clear_output(wait=True)
                display(fig)
        else:
            S.redraw(fig)
        status.value = "<span style='color:green'>✓ Applied</span>"

    def _on_color_mode_change(change):
        if change["new"] == "Manual":
            palette_box.layout.display = "none"
            manual_section.layout.display = ""
        else:
            palette_box.layout.display = ""
            manual_section.layout.display = "none"

    color_mode.observe(_on_color_mode_change, names="value")

    def _on_apply(_):
        S.set_figure_size(fig, fig_width.value, fig_height.value)
        S.set_font_size(fig, font_size.value)
        S.set_legend_position(fig, legend_loc.value)
        if color_mode.value == "Manual":
            S.set_line_colors_manual(fig, [p.value for p in manual_pickers])
        else:
            S.set_line_colors(fig, palette_select.value)
        S.set_background_color(fig, bg_color.value)
        S.set_grid(fig, grid_toggle.value)
        S.set_spine_style(fig, spine_style.value)
        _refresh()

    def _on_palette_change(change):
        nonlocal palette_preview
        new_preview = _build_palette_preview(change["new"])
        palette_box.children = (palette_select, new_preview)

    def _on_recommend(_):
        from .palettes import recommend
        n = sum(len(ax.get_lines()) for ax in fig.axes) or 3
        suggestions = recommend(n, colorblind_safe=True)
        with recommend_out:
            recommend_out.clear_output()
            for p in suggestions[:3]:
                swatch = "  ".join(
                    f"<span style='background:{c};padding:0 10px;border-radius:3px'>&nbsp;</span>"
                    for c in p["colors"][:n]
                )
                display(widgets.HTML(
                    f"<b>{p['name']}</b> — {p['description']}<br>{swatch}<br>"
                ))

    def _on_render_mode_change(change):
        render_out.layout.display = "" if change["new"] == "re-render" else "none"

    render_out.layout.display = "none" if render_mode == "in-place (ipympl)" else ""
    render_toggle.observe(_on_render_mode_change, names="value")

    apply_btn.on_click(_on_apply)
    palette_select.observe(_on_palette_change, names="value")
    cb_recommend.on_click(_on_recommend)

    # ── layout ────────────────────────────────────────────────────────────
    palette_box = widgets.HBox([palette_select, palette_preview])

    panel = widgets.VBox([
        widgets.HTML("<b style='font-size:1.1em'>mplstudio</b>"),
        render_toggle,
        render_out,
        widgets.HTML("<hr style='margin:4px 0'>"),
        widgets.HTML("<b>Figure size</b>"),
        fig_width, fig_height,
        widgets.HTML("<b>Typography</b>"),
        font_size,
        widgets.HTML("<b>Colors</b>"),
        color_mode,
        palette_box,
        manual_section,
        bg_color,
        widgets.HTML("<b>Legend</b>"),
        legend_loc,
        widgets.HTML("<b>Grid & Spines</b>"),
        grid_toggle, spine_style,
        widgets.HTML("<hr style='margin:4px 0'>"),
        cb_recommend, recommend_out,
        widgets.HBox([apply_btn, status]),
    ], layout=widgets.Layout(padding="12px", width="380px",
                              border="1px solid #ddd", border_radius="6px"))

    display(panel)


def _build_palette_preview(name: str) -> widgets.HTML:
    from .palettes import get_palette
    colors = get_palette(name)
    swatches = "".join(
        f"<span style='background:{c};display:inline-block;width:18px;height:18px;"
        f"margin:1px;border-radius:3px;border:1px solid #ccc'></span>"
        for c in colors
    )
    return widgets.HTML(value=f"<div style='margin-left:8px'>{swatches}</div>")
