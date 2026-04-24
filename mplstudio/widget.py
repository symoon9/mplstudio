"""ipywidgets control panel for mplstudio."""

from __future__ import annotations

import base64
import io

import matplotlib.pyplot as plt
import ipywidgets as widgets
from IPython.display import display
from matplotlib.figure import Figure

from . import style as S
from .palettes import PALETTES, palette_names

_PREVIEW_HEIGHT = 400  # px — fixed height for the fitted preview mode


def studio(fig: Figure | None = None) -> None:
    """Display the mplstudio control panel for *fig*.

    The panel embeds a live-rendered image at the top and a responsive
    grid of controls below. Every widget change auto-refreshes the figure
    immediately — no Apply button needed.

    Parameters
    ----------
    fig:
        Target figure. Defaults to ``plt.gcf()``.
    """
    if fig is None:
        fig = plt.gcf()

    # ── size toggle (fitted preview vs actual size) ───────────────────────
    size_toggle = widgets.ToggleButton(
        value=False,
        description="Fitted",
        icon="expand",
        button_style="",
        layout=widgets.Layout(width="110px", height="28px"),
        tooltip="Currently fitted — click to show at actual rendered size",
    )

    def _on_size_toggle(change):
        if change["new"]:
            size_toggle.description = "Actual size"
            size_toggle.icon = "compress"
            size_toggle.button_style = "info"
            size_toggle.tooltip = "Currently actual size — click to fit to panel"
        else:
            size_toggle.description = "Fitted"
            size_toggle.icon = "expand"
            size_toggle.button_style = ""
            size_toggle.tooltip = "Currently fitted — click to show at actual rendered size"
        _refresh()

    size_toggle.observe(_on_size_toggle, names="value")

    # ── rendered output ───────────────────────────────────────────────────
    render_out = widgets.Output(
        layout=widgets.Layout(width="100%", margin="0 0 4px 0")
    )

    def _refresh(*_):
        buf = io.BytesIO()
        fig.savefig(buf, format="png", bbox_inches="tight", dpi=fig.dpi)
        buf.seek(0)
        img_b64 = base64.b64encode(buf.read()).decode()

        if size_toggle.value:
            # actual size — natural pixel dimensions; wrapper scrolls horizontally
            # if the figure is wider than the notebook
            img_style = "height:auto;display:block"
            div_style = "overflow-x:auto;width:100%"
        else:
            # fitted preview — capped height keeps the control panel in place
            img_style = (
                f"max-height:{_PREVIEW_HEIGHT}px;width:auto;"
                "max-width:100%;display:block;margin:0 auto"
            )
            div_style = "width:100%"

        img_html = (
            f'<div style="{div_style}">'
            f'<img src="data:image/png;base64,{img_b64}" style="{img_style}">'
            f'</div>'
        )
        with render_out:
            render_out.clear_output(wait=True)
            display(widgets.HTML(img_html))
    _refresh()  # initial render

    # ── figure size ───────────────────────────────────────────────────────
    w_init, h_init = fig.get_size_inches()
    fig_width = widgets.FloatSlider(
        value=w_init, min=2, max=24, step=0.5,
        description="Width (in)", style={"description_width": "82px"},
        layout=widgets.Layout(width="100%"),
        continuous_update=False,
    )
    fig_height = widgets.FloatSlider(
        value=h_init, min=2, max=24, step=0.5,
        description="Height (in)", style={"description_width": "82px"},
        layout=widgets.Layout(width="100%"),
        continuous_update=False,
    )

    def _on_size(_):
        S.set_figure_size(fig, fig_width.value, fig_height.value)
        _refresh()

    fig_width.observe(_on_size, names="value")
    fig_height.observe(_on_size, names="value")

    # ── font ──────────────────────────────────────────────────────────────
    font_size = widgets.IntSlider(
        value=12, min=6, max=32, step=1,
        description="Font size", style={"description_width": "82px"},
        layout=widgets.Layout(width="100%"),
        continuous_update=False,
    )

    def _on_font(_):
        S.set_font_size(fig, font_size.value)
        _refresh()

    font_size.observe(_on_font, names="value")

    # ── colors ────────────────────────────────────────────────────────────
    color_mode = widgets.ToggleButtons(
        options=["Palette", "Manual"],
        value="Palette",
        description="Mode:",
        style={"button_width": "72px"},
        layout=widgets.Layout(margin="0 0 4px 0"),
    )

    palette_select = widgets.Dropdown(
        options=palette_names(),
        description="Palette",
        style={"description_width": "58px"},
        layout=widgets.Layout(width="100%"),
    )
    palette_preview = _build_palette_preview(palette_names()[0])

    line_colors = S.get_line_colors(fig)
    line_labels = S.get_line_labels(fig)
    manual_pickers = [
        widgets.ColorPicker(
            value=color,
            description=(label[:13] + "…" if len(label) > 13 else label),
            style={"description_width": "82px"},
            concise=False,
            layout=widgets.Layout(width="100%"),
        )
        for color, label in zip(line_colors, line_labels)
    ]
    manual_section = widgets.VBox(
        manual_pickers if manual_pickers
        else [widgets.HTML("<i style='color:#888'>No labeled series found.</i>")]
    )
    manual_section.layout.display = "none"

    palette_row = widgets.HBox(
        [palette_select, palette_preview],
        layout=widgets.Layout(width="100%"),
    )

    bg_color = widgets.ColorPicker(
        value="#ffffff", description="Background",
        style={"description_width": "82px"},
        concise=False,
        layout=widgets.Layout(width="100%"),
    )

    def _apply_colors():
        if color_mode.value == "Manual":
            S.set_line_colors_manual(fig, [p.value for p in manual_pickers])
        else:
            S.set_line_colors(fig, palette_select.value)
        _refresh()

    def _on_palette_change(change):
        palette_row.children = (palette_select, _build_palette_preview(change["new"]))
        _apply_colors()

    def _on_color_mode_change(change):
        if change["new"] == "Manual":
            palette_row.layout.display = "none"
            manual_section.layout.display = ""
        else:
            palette_row.layout.display = ""
            manual_section.layout.display = "none"
        _apply_colors()

    def _on_bg_change(change):
        if len(change["new"]) == 7:  # valid #rrggbb
            S.set_background_color(fig, change["new"])
            _refresh()

    palette_select.observe(_on_palette_change, names="value")
    color_mode.observe(_on_color_mode_change, names="value")
    bg_color.observe(_on_bg_change, names="value")
    for picker in manual_pickers:
        picker.observe(lambda _: _apply_colors(), names="value")

    # ── legend ────────────────────────────────────────────────────────────
    legend_loc = widgets.Dropdown(
        options=S.LEGEND_LOCATIONS,
        value="best",
        description="Location",
        style={"description_width": "68px"},
        layout=widgets.Layout(width="100%"),
    )

    def _on_legend(_):
        S.set_legend_position(fig, legend_loc.value)
        _refresh()

    legend_loc.observe(_on_legend, names="value")

    # ── grid & spines ─────────────────────────────────────────────────────
    grid_toggle = widgets.Checkbox(value=False, description="Show grid")
    spine_style = widgets.ToggleButtons(
        options=S.SPINE_STYLES,
        value="box",
        description="Spines:",
        style={"button_width": "84px"},
    )

    def _on_grid(_):
        S.set_grid(fig, grid_toggle.value)
        _refresh()

    def _on_spine(_):
        S.set_spine_style(fig, spine_style.value)
        _refresh()

    grid_toggle.observe(_on_grid, names="value")
    spine_style.observe(_on_spine, names="value")

    # ── palette recommendation ─────────────────────────────────────────────
    cb_recommend = widgets.Button(
        description="Suggest colorblind-safe palette",
        button_style="info",
        layout=widgets.Layout(width="100%"),
    )
    recommend_out = widgets.Output()

    def _on_recommend(_):
        from .palettes import recommend
        n = len(S.get_line_labels(fig)) or 3
        suggestions = recommend(n, colorblind_safe=True)
        with recommend_out:
            recommend_out.clear_output()
            for p in suggestions[:3]:
                swatch = "".join(
                    f"<span style='background:{c};display:inline-block;"
                    f"width:16px;height:16px;margin:1px;border-radius:2px'></span>"
                    for c in p["colors"][:n]
                )
                display(widgets.HTML(
                    f"<b>{p['name']}</b> — {p['description']}<br>{swatch}<br>"
                ))

    cb_recommend.on_click(_on_recommend)

    # ── responsive grid layout ─────────────────────────────────────────────

    def _section(title: str, *children) -> widgets.VBox:
        return widgets.VBox(
            [widgets.HTML(f"<b style='font-size:0.88em;color:#333'>{title}</b>"),
             *children],
            layout=widgets.Layout(
                padding="8px 10px",
                border="1px solid #e0e0e0",
                border_radius="6px",
            ),
        )

    grid = widgets.GridBox(
        [
            _section("Figure Size", fig_width, fig_height),
            _section("Typography", font_size),
            _section(
                "Colors",
                color_mode, palette_row, manual_section, bg_color,
            ),
            _section("Legend", legend_loc),
            _section("Grid & Spines", grid_toggle, spine_style),
            _section("Palette Suggestions", cb_recommend, recommend_out),
        ],
        layout=widgets.Layout(
            grid_template_columns="repeat(auto-fill, minmax(280px, 1fr))",
            grid_gap="8px",
            width="100%",
        ),
    )

    header = widgets.HBox(
        [
            widgets.HTML("<b style='font-size:1.1em'>mplstudio</b>"),
            size_toggle,
        ],
        layout=widgets.Layout(
            justify_content="space-between",
            align_items="center",
            width="100%",
            margin="0 0 6px 0",
        ),
    )

    panel = widgets.VBox(
        [
            header,
            render_out,
            widgets.HTML("<hr style='margin:4px 0'>"),
            grid,
        ],
        layout=widgets.Layout(width="100%", padding="10px"),
    )

    display(panel)


def _build_palette_preview(name: str) -> widgets.HTML:
    from .palettes import get_palette
    colors = get_palette(name)
    swatches = "".join(
        f"<span style='background:{c};display:inline-block;width:16px;height:16px;"
        f"margin:1px;border-radius:2px;border:1px solid #ccc'></span>"
        for c in colors
    )
    return widgets.HTML(
        value=f"<div style='margin-left:6px;line-height:18px'>{swatches}</div>"
    )
