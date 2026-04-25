"""ipywidgets control panel for mplstudio."""

from __future__ import annotations

import base64
import io

import matplotlib.pyplot as plt
import ipywidgets as widgets
from IPython.display import display
from matplotlib.figure import Figure

from . import style as S
from .palettes import (
    PALETTES, palette_names, SEQUENTIAL_CMAPS, DIVERGING_CMAPS, smart_palette,
)

_PREVIEW_HEIGHT = 400  # px — fixed height for the fitted preview mode

_KNOWN_SECTIONS = frozenset({
    "figure_size",
    "typography",
    "colors",
    "alpha",
    "axes",
    "legend",
    "grid_spines",
    "palette_suggestions",
})

_GITHUB_ISSUES = "https://github.com/symoon9/mplstudio/issues"


def available_sections() -> list[str]:
    """Return the sorted list of valid section names for the ``show`` parameter of :func:`studio`."""
    return sorted(_KNOWN_SECTIONS)


def studio(fig: Figure | None = None, *, show: list[str] | None = None) -> None:
    """Display the mplstudio control panel for *fig*.

    Parameters
    ----------
    fig:
        Target figure. Defaults to ``plt.gcf()``.
    show:
        List of section names to display. ``None`` (default) shows all sections.
        Available sections: ``"figure_size"``, ``"typography"``, ``"colors"``,
        ``"alpha"``, ``"axes"``, ``"legend"``, ``"grid_spines"``,
        ``"palette_suggestions"``.
        Unknown names produce a warning with a link to open a GitHub issue.
    """
    if fig is None:
        fig = plt.gcf()

    if show is None:
        active = _KNOWN_SECTIONS
        unknown: frozenset[str] = frozenset()
    else:
        show_set = frozenset(show)
        unknown = show_set - _KNOWN_SECTIONS
        active = show_set & _KNOWN_SECTIONS

    # ── size toggle ───────────────────────────────────────────────────────
    _size_cb = widgets.Checkbox(value=False, indent=False, description="")
    _size_cb.layout.display = "none"
    _mid = _size_cb.model_id

    _toggle_html = widgets.HTML(f"""
<style>
.mpl-sw-{_mid[:8]} {{
    position: relative; display: inline-block;
    width: 60px; height: 34px; vertical-align: middle;
}}
.mpl-sw-{_mid[:8]} input {{ opacity: 0; width: 0; height: 0; }}
.mpl-sl-{_mid[:8]} {{
    position: absolute; cursor: pointer;
    top: 0; left: 0; right: 0; bottom: 0;
    background-color: #ccc; transition: .4s; border-radius: 34px;
}}
.mpl-sl-{_mid[:8]}:before {{
    position: absolute; content: "";
    height: 26px; width: 26px; left: 4px; bottom: 4px;
    background-color: white; transition: .4s; border-radius: 50%;
}}
.mpl-sw-{_mid[:8]} input:checked + .mpl-sl-{_mid[:8]} {{ background-color: #2196F3; }}
.mpl-sw-{_mid[:8]} input:checked + .mpl-sl-{_mid[:8]}:before {{ transform: translateX(26px); }}
</style>
<label class="mpl-sw-{_mid[:8]}" style="vertical-align:middle;cursor:pointer">
  <input type="checkbox" onchange="
    var cb = document.querySelector('[data-model-id=\\"{_mid}\\"] input[type=checkbox]');
    if (cb) {{ cb.checked = this.checked; cb.dispatchEvent(new Event('change', {{bubbles:true}})); }}
  ">
  <span class="mpl-sl-{_mid[:8]}"></span>
</label>
<span style="margin-left:8px;font-size:13px;color:#555;vertical-align:middle">Actual size</span>
""")

    toggle_row = widgets.HBox(
        [_toggle_html, _size_cb],
        layout=widgets.Layout(align_items="center"),
    )

    # ── rendered output ───────────────────────────────────────────────────
    render_out = widgets.Output(
        layout=widgets.Layout(width="100%", margin="0 0 4px 0")
    )

    def _refresh(*_):
        buf = io.BytesIO()
        fig.savefig(buf, format="png", bbox_inches="tight", dpi=fig.dpi)
        buf.seek(0)
        img_b64 = base64.b64encode(buf.read()).decode()

        if _size_cb.value:
            div_style = "text-align:center;overflow-x:auto;width:100%"
            img_style = "height:auto;display:inline-block;vertical-align:top"
        else:
            div_style = "text-align:center;width:100%"
            img_style = (
                f"max-height:{_PREVIEW_HEIGHT}px;width:auto;"
                "max-width:100%;display:inline-block;vertical-align:top"
            )
        img_html = (
            f'<div style="{div_style}">'
            f'<img src="data:image/png;base64,{img_b64}" style="{img_style}">'
            f'</div>'
        )
        with render_out:
            render_out.clear_output(wait=True)
            display(widgets.HTML(img_html))

    _size_cb.observe(lambda _: _refresh(), names="value")
    _refresh()

    # ── section builder ───────────────────────────────────────────────────
    def _section(title: str, *children) -> widgets.VBox:
        return widgets.VBox(
            [widgets.HTML(f"<b style='font-size:0.88em;color:#333'>{title}</b>"),
             *children],
            layout=widgets.Layout(
                padding="8px 10px",
                border="1px solid #e0e0e0",
                border_radius="6px",
                overflow="hidden",
            ),
        )

    # ── helper: FloatText pair (min/max) ──────────────────────────────────
    def _range_row(label: str, lo: float, hi: float,
                   on_change) -> tuple[widgets.HBox, widgets.FloatText, widgets.FloatText]:
        w_lo = widgets.FloatText(
            value=round(lo, 4), description=f"{label} min",
            style={"description_width": "50px"},
            layout=widgets.Layout(width="160px"),
        )
        w_hi = widgets.FloatText(
            value=round(hi, 4), description="max",
            style={"description_width": "30px"},
            layout=widgets.Layout(width="130px"),
        )
        w_lo.observe(on_change, names="value")
        w_hi.observe(on_change, names="value")
        return widgets.HBox([w_lo, w_hi]), w_lo, w_hi

    sections: list[widgets.Widget] = []

    # ══ Figure Size ═══════════════════════════════════════════════════════
    if "figure_size" in active:
        w_init, h_init = fig.get_size_inches()
        fig_width = widgets.FloatSlider(
            value=w_init, min=2, max=25, step=0.5,
            description="Width (in)", style={"description_width": "82px"},
            layout=widgets.Layout(width="100%"), continuous_update=False,
        )
        fig_height = widgets.FloatSlider(
            value=h_init, min=2, max=25, step=0.5,
            description="Height (in)", style={"description_width": "82px"},
            layout=widgets.Layout(width="100%"), continuous_update=False,
        )

        def _on_size(_):
            S.set_figure_size(fig, fig_width.value, fig_height.value)
            _refresh()

        fig_width.observe(_on_size, names="value")
        fig_height.observe(_on_size, names="value")
        sections.append(_section("Figure Size", fig_width, fig_height))

    # ══ Typography ════════════════════════════════════════════════════════
    if "typography" in active:
        font_size = widgets.IntSlider(
            value=12, min=6, max=32, step=1,
            description="Font size", style={"description_width": "82px"},
            layout=widgets.Layout(width="100%"), continuous_update=False,
        )

        def _on_font(_):
            S.set_font_size(fig, font_size.value)
            _refresh()

        font_size.observe(_on_font, names="value")
        sections.append(_section("Typography", font_size))

    # ══ Colors ════════════════════════════════════════════════════════════
    if "colors" in active:
        plot_type = S.detect_plot_type(fig)
        n_series = len(S.get_line_labels(fig))

        # Type badge
        _type_label = {
            "categorical": f"categorical · {n_series} series",
            "continuous": "continuous (colormap)",
            "mixed": f"mixed · {n_series} categorical series + colormap",
        }[plot_type]
        type_badge = widgets.HTML(
            f"<span style='font-size:0.78em;color:#888'>Detected: {_type_label}</span>"
        )

        # ── Categorical controls ──────────────────────────────────────────
        cat_box_children: list[widgets.Widget] = []

        if plot_type in ("categorical", "mixed"):
            color_mode = widgets.ToggleButtons(
                options=["Palette", "Manual", "Smart"], value="Palette",
                description="Mode:", style={"button_width": "62px"},
                layout=widgets.Layout(width="100%", margin="0 0 4px 0"),
            )
            # ── Palette sub-section ───────────────────────────────────────
            palette_select = widgets.Dropdown(
                options=palette_names(), description="Palette",
                style={"description_width": "58px"},
                layout=widgets.Layout(width="100%"),
            )
            palette_preview_w = _build_palette_preview(palette_names()[0])
            palette_col = widgets.VBox(
                [palette_select, palette_preview_w],
                layout=widgets.Layout(width="100%"),
            )
            # ── Manual sub-section ────────────────────────────────────────
            line_colors = S.get_line_colors(fig)
            line_labels = S.get_line_labels(fig)
            manual_pickers = [
                widgets.ColorPicker(
                    value=color,
                    description=(label[:13] + "…" if len(label) > 13 else label),
                    style={"description_width": "82px"}, concise=False,
                    layout=widgets.Layout(width="100%"),
                )
                for color, label in zip(line_colors, line_labels)
            ]
            manual_section = widgets.VBox(
                manual_pickers if manual_pickers
                else [widgets.HTML("<i style='color:#888'>No labeled series found.</i>")]
            )
            manual_section.layout.display = "none"
            # ── Smart sub-section ─────────────────────────────────────────
            _smart_init_n = max(2, min(n_series or 5, 10))
            smart_n = widgets.IntSlider(
                value=_smart_init_n, min=2, max=20, step=1,
                description="Colors (n)",
                style={"description_width": "78px"},
                layout=widgets.Layout(width="100%"),
                continuous_update=False,
            )
            smart_preview_w = widgets.HTML(
                value=_swatches_div(smart_palette(_smart_init_n))
            )
            smart_section = widgets.VBox(
                [smart_n, smart_preview_w],
                layout=widgets.Layout(width="100%"),
            )
            smart_section.layout.display = "none"

            def _apply_colors():
                mode = color_mode.value
                if mode == "Manual":
                    S.set_line_colors_manual(fig, [p.value for p in manual_pickers])
                elif mode == "Smart":
                    S.set_line_colors_manual(fig, smart_palette(smart_n.value))
                else:
                    S.set_line_colors(fig, palette_select.value)
                _refresh()

            def _on_palette_change(change):
                palette_preview_w.value = _build_palette_preview(change["new"]).value
                _apply_colors()

            def _on_smart_n(change):
                smart_preview_w.value = _swatches_div(smart_palette(change["new"]))
                _apply_colors()

            def _on_color_mode_change(change):
                palette_col.layout.display = "none"
                manual_section.layout.display = "none"
                smart_section.layout.display = "none"
                if change["new"] == "Manual":
                    manual_section.layout.display = ""
                elif change["new"] == "Smart":
                    smart_section.layout.display = ""
                else:
                    palette_col.layout.display = ""
                _apply_colors()

            palette_select.observe(_on_palette_change, names="value")
            color_mode.observe(_on_color_mode_change, names="value")
            smart_n.observe(_on_smart_n, names="value")
            for picker in manual_pickers:
                picker.observe(lambda _: _apply_colors(), names="value")

            cat_box_children = [color_mode, palette_col, manual_section, smart_section]

        # ── Continuous / colormap controls ────────────────────────────────
        cmap_box_children: list[widgets.Widget] = []

        if plot_type in ("continuous", "mixed"):
            if plot_type == "mixed":
                cmap_box_children.append(
                    widgets.HTML("<hr style='margin:4px 0;border-color:#e0e0e0'>")
                )
            cmap_type_tb = widgets.ToggleButtons(
                options=["Sequential", "Diverging"], value="Sequential",
                style={"button_width": "90px"},
                layout=widgets.Layout(width="100%"),
            )
            _init_cmap = S.get_colormap(fig) or "viridis"
            _init_type = "Sequential" if _init_cmap in SEQUENTIAL_CMAPS else "Diverging"
            cmap_type_tb.value = _init_type

            cmap_select = widgets.Dropdown(
                options=SEQUENTIAL_CMAPS if _init_type == "Sequential" else DIVERGING_CMAPS,
                value=_init_cmap if _init_cmap in (SEQUENTIAL_CMAPS + DIVERGING_CMAPS) else SEQUENTIAL_CMAPS[0],
                description="Colormap",
                style={"description_width": "68px"},
                layout=widgets.Layout(width="100%"),
            )
            cmap_grad_w = _build_colormap_gradient(cmap_select.value)

            def _on_cmap_type(change):
                opts = SEQUENTIAL_CMAPS if change["new"] == "Sequential" else DIVERGING_CMAPS
                cmap_select.options = opts
                cmap_select.value = opts[0]

            def _on_cmap(change):
                cmap_grad_w.value = _build_colormap_gradient(change["new"]).value
                S.set_colormap(fig, change["new"])
                _refresh()

            cmap_type_tb.observe(_on_cmap_type, names="value")
            cmap_select.observe(_on_cmap, names="value")
            cmap_box_children += [cmap_type_tb, cmap_select, cmap_grad_w]

        # ── Background ────────────────────────────────────────────────────
        bg_color = widgets.ColorPicker(
            value="#ffffff", description="Background",
            style={"description_width": "82px"}, concise=False,
            layout=widgets.Layout(width="100%"),
        )

        def _on_bg_change(change):
            if len(change["new"]) == 7:
                S.set_background_color(fig, change["new"])
                _refresh()

        bg_color.observe(_on_bg_change, names="value")

        sections.append(_section(
            "Colors", type_badge,
            *cat_box_children, *cmap_box_children, bg_color,
        ))

    # ══ Opacity (Alpha) ═══════════════════════════════════════════════════
    if "alpha" in active:
        alphas = S.get_series_alpha(fig)
        a_labels = S.get_line_labels(fig)

        init_global = (sum(alphas) / len(alphas)) if alphas else 1.0
        global_alpha = widgets.FloatSlider(
            value=init_global, min=0.0, max=1.0, step=0.05,
            description="All series",
            style={"description_width": "82px"},
            layout=widgets.Layout(width="100%"),
            continuous_update=False,
        )

        alpha_sliders = [
            widgets.FloatSlider(
                value=a, min=0.0, max=1.0, step=0.05,
                description=(lbl[:13] + "…" if len(lbl) > 13 else lbl),
                style={"description_width": "82px"},
                layout=widgets.Layout(width="100%"),
                continuous_update=False,
            )
            for a, lbl in zip(alphas, a_labels)
        ]

        _alpha_busy = [False]  # guard: prevent global→per-series loop

        def _on_global_alpha(change):
            if _alpha_busy[0]:
                return
            _alpha_busy[0] = True
            for s in alpha_sliders:
                s.value = change["new"]
            _alpha_busy[0] = False
            S.set_series_alpha(fig, [change["new"]] * len(alpha_sliders))
            _refresh()

        def _on_per_alpha(_):
            if _alpha_busy[0]:
                return
            S.set_series_alpha(fig, [s.value for s in alpha_sliders])
            _refresh()

        global_alpha.observe(_on_global_alpha, names="value")
        for s in alpha_sliders:
            s.observe(_on_per_alpha, names="value")

        alpha_children: list[widgets.Widget] = [global_alpha]
        if alpha_sliders:
            per_box = widgets.VBox(
                alpha_sliders,
                layout=widgets.Layout(width="100%"),
            )
            per_acc = widgets.Accordion(
                children=[per_box],
                selected_index=None,
                layout=widgets.Layout(width="100%"),
            )
            per_acc.set_title(0, "Per series")
            alpha_children.append(per_acc)
        else:
            alpha_children.append(
                widgets.HTML("<i style='color:#888'>No labeled series found.</i>")
            )

        sections.append(_section("Opacity", *alpha_children))

    # ══ Axes ══════════════════════════════════════════════════════════════
    if "axes" in active and fig.axes:
        ax_idx = [0]  # mutable ref so inner callbacks can update it

        ax_selector = None
        if len(fig.axes) > 1:
            ax_selector = widgets.Dropdown(
                options=[(f"Axes {i}", i) for i in range(len(fig.axes))],
                value=0, description="Axes:",
                style={"description_width": "40px"},
                layout=widgets.Layout(width="100%"),
            )

        def _cur_ax():
            return fig.axes[ax_idx[0]]

        title_input = widgets.Text(
            value=_cur_ax().get_title(), description="Title",
            style={"description_width": "50px"},
            layout=widgets.Layout(width="100%"),
            continuous_update=False,
        )
        xlabel_input = widgets.Text(
            value=_cur_ax().get_xlabel(), description="X label",
            style={"description_width": "50px"},
            layout=widgets.Layout(width="100%"),
            continuous_update=False,
        )
        ylabel_input = widgets.Text(
            value=_cur_ax().get_ylabel(), description="Y label",
            style={"description_width": "50px"},
            layout=widgets.Layout(width="100%"),
            continuous_update=False,
        )

        xlim = _cur_ax().get_xlim()
        ylim = _cur_ax().get_ylim()

        def _on_xlim(_):
            S.set_xlim(fig, xlim_lo.value, xlim_hi.value, ax_idx[0])
            _refresh()

        def _on_ylim(_):
            S.set_ylim(fig, ylim_lo.value, ylim_hi.value, ax_idx[0])
            _refresh()

        xlim_row, xlim_lo, xlim_hi = _range_row("X lim", xlim[0], xlim[1], _on_xlim)
        ylim_row, ylim_lo, ylim_hi = _range_row("Y lim", ylim[0], ylim[1], _on_ylim)

        def _on_title(_):
            S.set_title(fig, title_input.value, ax_idx[0])
            _refresh()

        def _on_xlabel(_):
            S.set_xlabel(fig, xlabel_input.value, ax_idx[0])
            _refresh()

        def _on_ylabel(_):
            S.set_ylabel(fig, ylabel_input.value, ax_idx[0])
            _refresh()

        title_input.observe(_on_title, names="value")
        xlabel_input.observe(_on_xlabel, names="value")
        ylabel_input.observe(_on_ylabel, names="value")

        def _on_ax_select(change):
            ax_idx[0] = change["new"]
            ax = fig.axes[ax_idx[0]]
            title_input.value = ax.get_title()
            xlabel_input.value = ax.get_xlabel()
            ylabel_input.value = ax.get_ylabel()
            xl = ax.get_xlim()
            yl = ax.get_ylim()
            xlim_lo.value, xlim_hi.value = round(xl[0], 4), round(xl[1], 4)
            ylim_lo.value, ylim_hi.value = round(yl[0], 4), round(yl[1], 4)

        if ax_selector:
            ax_selector.observe(_on_ax_select, names="value")

        axes_children = (
            ([ax_selector] if ax_selector else [])
            + [title_input, xlabel_input, ylabel_input, xlim_row, ylim_row]
        )
        sections.append(_section("Axes", *axes_children))

    # ══ Legend ════════════════════════════════════════════════════════════
    if "legend" in active:
        legend_loc = widgets.Dropdown(
            options=S.LEGEND_LOCATIONS, value="best",
            description="Location", style={"description_width": "68px"},
            layout=widgets.Layout(width="100%"),
        )

        def _on_legend_loc(_):
            S.set_legend_position(fig, legend_loc.value)
            _refresh()

        legend_loc.observe(_on_legend_loc, names="value")

        # ── legend label editing ──────────────────────────────────────────
        leg0 = fig.axes[0].get_legend() if fig.axes else None
        leg_texts = [t.get_text() for t in leg0.get_texts()] if leg0 else []
        name_inputs = [
            widgets.Text(
                value=txt,
                description=(txt[:12] + "…:" if len(txt) > 12 else f"{txt}:"),
                style={"description_width": "78px"},
                layout=widgets.Layout(width="100%"),
                continuous_update=False,
            )
            for txt in leg_texts
        ]

        def _on_legend_name(_):
            S.set_legend_labels(fig, [inp.value for inp in name_inputs])
            _refresh()

        for inp in name_inputs:
            inp.observe(_on_legend_name, names="value")

        # ── bbox fine control ─────────────────────────────────────────────
        bbox_header = widgets.HTML(
            "<span style='font-size:0.82em;color:#666'>BBox position (x, y)</span>"
        )
        bbox_x = widgets.FloatSlider(
            value=1.02, min=0.0, max=1.5, step=0.01,
            description="x", style={"description_width": "20px"},
            layout=widgets.Layout(width="100%"), continuous_update=False,
        )
        bbox_y = widgets.FloatSlider(
            value=1.0, min=0.0, max=1.5, step=0.01,
            description="y", style={"description_width": "20px"},
            layout=widgets.Layout(width="100%"), continuous_update=False,
        )

        def _on_bbox(_):
            S.set_legend_bbox(fig, bbox_x.value, bbox_y.value)
            _refresh()

        bbox_x.observe(_on_bbox, names="value")
        bbox_y.observe(_on_bbox, names="value")

        legend_children = (
            [legend_loc]
            + (name_inputs if name_inputs
               else [widgets.HTML("<i style='color:#888;font-size:0.85em'>No legend entries.</i>")])
            + [bbox_header, bbox_x, bbox_y]
        )
        sections.append(_section("Legend", *legend_children))

    # ══ Grid & Spines ═════════════════════════════════════════════════════
    if "grid_spines" in active:
        grid_toggle = widgets.Checkbox(value=False, description="Show grid")
        spine_style = widgets.ToggleButtons(
            options=S.SPINE_STYLES, value="box",
            description="Spines:", style={"button_width": "84px"},
            layout=widgets.Layout(width="100%"),
        )

        def _on_grid(_):
            S.set_grid(fig, grid_toggle.value)
            _refresh()

        def _on_spine(_):
            S.set_spine_style(fig, spine_style.value)
            _refresh()

        grid_toggle.observe(_on_grid, names="value")
        spine_style.observe(_on_spine, names="value")
        sections.append(_section("Grid & Spines", grid_toggle, spine_style))

    # ══ Palette Suggestions ═══════════════════════════════════════════════
    if "palette_suggestions" in active:
        suggest_use_case = widgets.Dropdown(
            options=[("Any", None), ("Categorical", "categorical"),
                     ("Sequential", "sequential"), ("Diverging", "diverging")],
            value=None, description="Use case",
            style={"description_width": "68px"},
            layout=widgets.Layout(width="100%"),
        )
        suggest_bg = widgets.Dropdown(
            options=[("Any", None), ("Light bg", "light"), ("Dark bg", "dark")],
            value=None, description="Background",
            style={"description_width": "68px"},
            layout=widgets.Layout(width="100%"),
        )
        suggest_cb = widgets.Checkbox(
            value=True, description="Colorblind-safe only",
            layout=widgets.Layout(width="100%"),
        )
        cb_recommend = widgets.Button(
            description="Find palettes",
            button_style="info", layout=widgets.Layout(width="100%"),
        )
        recommend_out = widgets.Output()

        def _on_recommend(_):
            from .palettes import recommend
            n = len(S.get_line_labels(fig)) or 3
            suggestions = recommend(
                n,
                colorblind_safe=suggest_cb.value,
                use_case=suggest_use_case.value,
                background=suggest_bg.value,
                top_k=4,
            )
            with recommend_out:
                recommend_out.clear_output()
                if not suggestions:
                    display(widgets.HTML(
                        "<i style='color:#888'>No palettes match the current filters.</i>"
                    ))
                    return
                for p in suggestions:
                    swatch = "".join(
                        f"<span style='background:{c};display:inline-block;"
                        f"width:14px;height:14px;margin:1px;border-radius:2px'></span>"
                        for c in p["colors"][:n]
                    )
                    display(widgets.HTML(
                        f"<b>{p['name']}</b> {swatch}<br>"
                        f"<span style='font-size:0.82em;color:#555'>{p['description']}</span><br>"
                        f"<span style='font-size:0.78em;color:#888'>{p['source']}</span><br>"
                    ))

        cb_recommend.on_click(_on_recommend)
        sections.append(_section(
            "Palette Suggestions",
            suggest_use_case, suggest_bg, suggest_cb, cb_recommend, recommend_out,
        ))

    # ══ Unknown section warning ════════════════════════════════════════════
    if unknown:
        names_str = ", ".join(f"<code>{n}</code>" for n in sorted(unknown))
        avail_str = ", ".join(f"<code>{n}</code>" for n in sorted(_KNOWN_SECTIONS))
        sections.append(widgets.HTML(f"""
<div style="padding:8px 10px;border:1px solid #f5a623;border-radius:6px;
            background:#fffbf0;font-size:1em;color:#7a5300;line-height:1.6">
  <style>
    .mplstudio-warn-{_mid[:8]} code {{
      background:#f0d080;color:#3d2800;padding:1px 4px;
      border-radius:3px;font-size:0.9em;
    }}
  </style>
  <div class="mplstudio-warn-{_mid[:8]}">
  <b>Unknown section(s):</b> {names_str}<br>
  <b>Available:</b> {avail_str}<br>
  <a href="{_GITHUB_ISSUES}/new" target="_blank" style="color:#1a73e8">Open a GitHub issue</a> to request a new section.
  </div>
</div>
"""))

    # ── layout ────────────────────────────────────────────────────────────
    grid = widgets.GridBox(
        sections,
        layout=widgets.Layout(
            grid_template_columns="repeat(auto-fill, minmax(260px, 1fr))",
            grid_gap="8px",
            width="100%",
            overflow="hidden",
        ),
    )

    header = widgets.HBox(
        [widgets.HTML("<b style='font-size:1.1em'>mplstudio</b>"), toggle_row],
        layout=widgets.Layout(
            justify_content="space-between", align_items="center",
            width="100%", margin="0 0 6px 0",
        ),
    )

    display(widgets.VBox(
        [header, render_out, widgets.HTML("<hr style='margin:4px 0'>"), grid],
        layout=widgets.Layout(width="100%", padding="10px", overflow="hidden"),
    ))


def _swatches_div(colors: list[str]) -> str:
    """Return an HTML string of flex-wrapped color swatches."""
    spans = "".join(
        f"<span style='background:{c};display:inline-block;width:16px;height:16px;"
        f"margin:2px 2px 0 0;border-radius:3px;border:1px solid #ccc'></span>"
        for c in colors
    )
    return f"<div style='display:flex;flex-wrap:wrap;margin-top:4px'>{spans}</div>"


def _build_palette_preview(name: str) -> widgets.HTML:
    from .palettes import get_palette
    return widgets.HTML(value=_swatches_div(get_palette(name)))


def _build_colormap_gradient(cmap_name: str, steps: int = 24) -> widgets.HTML:
    import matplotlib.cm as cm
    import matplotlib.colors as mcolors
    try:
        cmap = cm.get_cmap(cmap_name)
    except ValueError:
        return widgets.HTML(value="")
    stops = ", ".join(
        mcolors.to_hex(cmap(i / (steps - 1))) for i in range(steps)
    )
    return widgets.HTML(
        value=(
            f"<div style='background:linear-gradient(to right,{stops});"
            f"height:14px;border-radius:3px;margin-top:4px;"
            f"border:1px solid #ccc'></div>"
        )
    )
