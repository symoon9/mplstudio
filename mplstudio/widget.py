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

_PREVIEW_HEIGHT = 400

_KNOWN_SECTIONS = frozenset({
    "figure_size", "typography", "colors", "alpha",
    "axes", "legend", "grid_spines", "palette_suggestions",
})

_GITHUB_ISSUES = "https://github.com/symoon9/mplstudio/issues"


def available_sections() -> list[str]:
    return sorted(_KNOWN_SECTIONS)


# ── theme ─────────────────────────────────────────────────────────────────────

def _theme_css(pid: str, dark: bool) -> str:
    if dark:
        bg      = "#1e1e2e"; card    = "#181825"; border  = "#313244"
        text    = "#cdd6f4"; muted   = "#a6adc8"; accent  = "#89b4fa"
        tog_off = "#45475a"; hr_col  = "#313244"
        warn_bg = "#2a2030"; warn_bdr = "#f38ba8"; warn_txt = "#f38ba8"
        inp_bg  = "#232334"
    else:
        bg      = "#f4f4f9"; card    = "#ffffff"; border  = "#e4e4eb"
        text    = "#1e1e2e"; muted   = "#6b7280"; accent  = "#6366f1"
        tog_off = "#d1d5db"; hr_col  = "#e4e4eb"
        warn_bg = "#fffbf0"; warn_bdr = "#f5a623"; warn_txt = "#7a5300"
        inp_bg  = "#ffffff"

    accent_glow = accent + "33"  # 20 % opacity for focus ring

    return f"""<style>
/* ── mplstudio {pid} ── */
.mpl-s-{pid} {{
  --mpl-accent:{accent};
  background:{bg};border-radius:16px;box-sizing:border-box;overflow:hidden;
  font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;
  color:{text};
}}
.mpl-c-{pid} {{
  background:{card};border:1px solid {border};border-radius:12px;
  box-sizing:border-box;overflow:hidden;
}}
.mpl-t-{pid} {{
  display:block;margin-bottom:6px;font-size:0.75em;font-weight:700;
  letter-spacing:0.07em;text-transform:uppercase;color:{muted};
}}
/* sliders */
.mpl-s-{pid} .widget-slider .ui-slider {{
  background:{border};border:none;border-radius:4px;
}}
.mpl-s-{pid} .widget-slider .ui-slider .ui-slider-handle {{
  background:{accent};border:none;border-radius:50%;
  width:14px;height:14px;top:-4px;cursor:pointer;
  box-shadow:0 1px 4px rgba(0,0,0,.25);
}}
/* slider readout — styled like a text input so it's obviously editable */
.mpl-s-{pid} .widget-readout {{
  background:{inp_bg} !important;
  border:1.5px solid {border} !important;
  border-radius:6px !important;
  color:{text} !important;
  padding:1px 5px !important;
  min-width:58px !important;
  box-shadow:inset 0 1px 2px rgba(0,0,0,.07) !important;
  font-size:0.85em !important;
}}
/* text / number inputs */
.mpl-s-{pid} input[type=text],
.mpl-s-{pid} input[type=number] {{
  background:{inp_bg} !important;
  color:{text} !important;
  border:1.5px solid {border} !important;
  border-radius:6px !important;
  box-shadow:inset 0 1px 2px rgba(0,0,0,.07) !important;
}}
.mpl-s-{pid} input[type=text]:focus,
.mpl-s-{pid} input[type=number]:focus,
.mpl-s-{pid} .widget-readout:focus {{
  border-color:{accent} !important;
  box-shadow:0 0 0 3px {accent_glow},inset 0 1px 2px rgba(0,0,0,.07) !important;
  outline:none !important;
}}
/* dropdowns — appearance:none + ::after chevron */
.mpl-s-{pid} .widget-dropdown {{
  position:relative;
}}
.mpl-s-{pid} .widget-dropdown select {{
  -webkit-appearance:none;-moz-appearance:none;appearance:none;
  background:{card} !important;
  color:{text} !important;
  border:1.5px solid {border} !important;
  border-radius:8px !important;
  padding:3px 28px 3px 10px !important;
  cursor:pointer;
  font-size:0.88em;
  transition:border-color 0.15s;
}}
.mpl-s-{pid} .widget-dropdown select:focus {{
  border-color:{accent} !important;
  box-shadow:0 0 0 3px {accent_glow} !important;
  outline:none !important;
}}
.mpl-s-{pid} .widget-dropdown::after {{
  content:'▾';
  position:absolute;right:8px;top:50%;
  transform:translateY(-50%);
  color:{muted};pointer-events:none;
  font-size:11px;line-height:1;
}}
/* toggle buttons group */
.mpl-s-{pid} .widget-toggle-buttons .widget-toggle-button {{
  background:{card} !important;border-color:{border} !important;
  color:{text} !important;border-radius:8px !important;
  font-size:0.85em;transition:background 0.15s,color 0.15s;
}}
.mpl-s-{pid} .widget-toggle-buttons .widget-toggle-button.mod-active {{
  background:{accent} !important;border-color:{accent} !important;
  color:#fff !important;box-shadow:none;
}}
/* info/action button */
.mpl-s-{pid} .widget-button.mod-info {{
  background:{accent} !important;border-color:{accent} !important;
  color:#fff !important;border-radius:8px !important;box-shadow:none;
}}
/* collapsible per-* button */
.mpl-per-{pid} button {{
  background:{bg} !important;
  border:1.5px solid {border} !important;
  border-radius:8px !important;
  color:{muted} !important;
  font-size:0.82em !important;
  padding:4px 10px !important;
  width:100% !important;
  text-align:left !important;
  box-shadow:none !important;
  cursor:pointer !important;
}}
.mpl-per-{pid} button:hover {{
  background:{card} !important;
  border-color:{accent} !important;
}}
/* checkbox accent */
.mpl-s-{pid} .widget-checkbox input {{ accent-color:{accent}; }}
/* hr */
.mpl-s-{pid} hr {{ border-color:{hr_col}; }}
/* warning block */
.mpl-w-{pid} {{
  background:{warn_bg};border:1px solid {warn_bdr};color:{warn_txt};
  border-radius:12px;padding:8px 12px;font-size:0.9em;line-height:1.7;
}}
.mpl-w-{pid} .avail code {{
  background:{border};color:{muted};
  padding:1px 4px;border-radius:3px;font-size:0.88em;
}}
/* iOS-style actual-size toggle */
.mpl-ios-{pid} {{
  display:inline-flex;align-items:center;gap:7px;
  cursor:pointer;vertical-align:middle;user-select:none;
}}
.mpl-ios-{pid} .trk {{
  position:relative;width:40px;height:22px;
  background:{tog_off};border-radius:11px;
  transition:background 0.25s;flex-shrink:0;
}}
.mpl-ios-{pid} .thm {{
  position:absolute;width:18px;height:18px;
  background:#fff;border-radius:50%;top:2px;left:2px;
  transition:left 0.25s;box-shadow:0 1px 3px rgba(0,0,0,.3);
}}
.mpl-ios-{pid}.on .trk {{ background:{accent}; }}
.mpl-ios-{pid}.on .thm {{ left:20px; }}
.mpl-ios-{pid} .lbl {{ font-size:13px;color:{muted}; }}
</style>"""


def _ios_toggle(cb_model_id: str, label: str, pid: str, sfx: str) -> widgets.HTML:
    """iOS toggle wired to a hidden Checkbox. Uses single-quoted onclick to avoid attribute termination."""
    eid = f"mpl-ios-{pid}-{sfx}"
    # Single-quoted onclick so double-quotes work freely inside the JS.
    # \\\" in the f-string becomes \" in the HTML → escaped double-quote inside JS string.
    return widgets.HTML(
        f'<span id="{eid}" class="mpl-ios-{pid}" '
        f'onclick=\'var el=document.getElementById("{eid}");'
        f'el.classList.toggle("on");'
        f'var on=el.classList.contains("on");'
        f'var cb=document.querySelector("[data-model-id=\\"{cb_model_id}\\"] input[type=checkbox]");'
        f'if(cb){{cb.checked=on;cb.dispatchEvent(new Event("change",{{bubbles:true}}))}}'
        f'\'>'
        f'<span class="trk"><span class="thm"></span></span>'
        f'<span class="lbl">{label}</span></span>'
    )


# ── studio ────────────────────────────────────────────────────────────────────

def studio(
    fig: Figure | None = None,
    *,
    show: list[str] | None = None,
    dark: bool = False,
) -> None:
    """Display the mplstudio control panel.

    Parameters
    ----------
    fig : Figure, optional
        Target figure. Defaults to ``plt.gcf()``.
    show : list[str], optional
        Section names to display; ``None`` shows all.
    dark : bool
        Use Catppuccin Mocha dark theme (default: light/indigo).
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

    # ── actual-size toggle → provides _pid ───────────────────────────────
    _size_cb = widgets.Checkbox(value=False, indent=False, description="")
    _size_cb.layout.display = "none"
    _pid = _size_cb.model_id[:8]

    css_w = widgets.HTML(value=_theme_css(_pid, dark))
    size_toggle = _ios_toggle(_size_cb.model_id, "Actual size", _pid, "size")

    # ── render output ─────────────────────────────────────────────────────
    render_out = widgets.Output(layout=widgets.Layout(width="100%", margin="0 0 4px 0"))

    def _refresh(*_):
        buf = io.BytesIO()
        fig.savefig(buf, format="png", bbox_inches="tight", dpi=fig.dpi)
        buf.seek(0)
        img_b64 = base64.b64encode(buf.read()).decode()
        if _size_cb.value:
            ds = "text-align:center;overflow-x:auto;width:100%"
            is_ = "height:auto;display:inline-block;vertical-align:top"
        else:
            ds = "text-align:center;width:100%"
            is_ = (f"max-height:{_PREVIEW_HEIGHT}px;width:auto;"
                   "max-width:100%;display:inline-block;vertical-align:top")
        with render_out:
            render_out.clear_output(wait=True)
            display(widgets.HTML(
                f'<div style="{ds}"><img src="data:image/png;base64,{img_b64}" style="{is_}"></div>'
            ))

    _size_cb.observe(lambda _: _refresh(), names="value")
    _refresh()

    # ── section builder ───────────────────────────────────────────────────
    def _section(title: str, *children) -> widgets.VBox:
        vbox = widgets.VBox(
            [widgets.HTML(f"<span class='mpl-t-{_pid}'>{title}</span>"), *children],
            layout=widgets.Layout(padding="10px 12px", overflow="hidden"),
        )
        vbox.add_class(f"mpl-c-{_pid}")
        return vbox

    def _per_btn(label: str) -> tuple[widgets.Button, widgets.VBox, list]:
        """Return (button, hidden_box, open_flag). Caller appends children to hidden_box."""
        box = widgets.VBox([], layout=widgets.Layout(width="100%", display="none", padding="4px 0 0 0"))
        flag = [False]
        btn = widgets.Button(description=f"{label}  ▾", button_style="",
                             layout=widgets.Layout(width="100%"))
        btn.add_class(f"mpl-per-{_pid}")
        def _toggle(_):
            flag[0] = not flag[0]
            box.layout.display = "" if flag[0] else "none"
            btn.description = f"{label}  {'▴' if flag[0] else '▾'}"
        btn.on_click(_toggle)
        return btn, box, flag

    def _lim_sliders(lo_init: float, hi_init: float):
        """Return (lo_sl, hi_sl, header_lo_row, header_hi_row) for xlim/ylim blocks."""
        r = max(abs(hi_init - lo_init), 1e-9)
        kw = dict(min=lo_init - r * 2, max=hi_init + r * 2, step=r / 100,
                  continuous_update=False, readout=True,
                  layout=widgets.Layout(width="100%"))
        lo_sl = widgets.FloatSlider(value=lo_init, description="min",
                                    style={"description_width": "28px"}, **kw)
        hi_sl = widgets.FloatSlider(value=hi_init, description="max",
                                    style={"description_width": "28px"}, **kw)
        return lo_sl, hi_sl

    sections: list[widgets.Widget] = []

    # ══ Figure Size ════════════════════════════════════════════════════════
    if "figure_size" in active:
        w_init, h_init = fig.get_size_inches()
        fig_width = widgets.FloatSlider(
            value=w_init, min=2, max=25, step=0.5, description="Width (in)",
            style={"description_width": "82px"},
            layout=widgets.Layout(width="100%"), continuous_update=False)
        fig_height = widgets.FloatSlider(
            value=h_init, min=2, max=25, step=0.5, description="Height (in)",
            style={"description_width": "82px"},
            layout=widgets.Layout(width="100%"), continuous_update=False)

        def _on_size(_):
            S.set_figure_size(fig, fig_width.value, fig_height.value); _refresh()

        fig_width.observe(_on_size, names="value")
        fig_height.observe(_on_size, names="value")
        sections.append(_section("Figure Size", fig_width, fig_height))

    # ══ Typography ════════════════════════════════════════════════════════
    if "typography" in active:
        _ax0 = fig.axes[0] if fig.axes else None

        def _fs(fn, default=12):
            try: return int(round(fn()))
            except: return default

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

        _fb = [False]

        def _on_font_all(change):
            if _fb[0]: return
            _fb[0] = True
            v = change["new"]
            for s, vv in [(font_title, v), (font_xlabel, v), (font_ylabel, v),
                           (font_ticks, max(v - 2, 6)), (font_legend, v)]:
                s.value = vv
            _fb[0] = False
            S.set_font_size(fig, v); _refresh()

        def _on_font_title(c):
            if _fb[0]: return
            [ax.title.set_fontsize(c["new"]) for ax in fig.axes]; _refresh()

        def _on_font_xlabel(c):
            if _fb[0]: return
            [ax.xaxis.label.set_fontsize(c["new"]) for ax in fig.axes]; _refresh()

        def _on_font_ylabel(c):
            if _fb[0]: return
            [ax.yaxis.label.set_fontsize(c["new"]) for ax in fig.axes]; _refresh()

        def _on_font_ticks(c):
            if _fb[0]: return
            [ax.tick_params(labelsize=c["new"]) for ax in fig.axes]; _refresh()

        def _on_font_legend(c):
            if _fb[0]: return
            for ax in fig.axes:
                lg = ax.get_legend()
                if lg:
                    [t.set_fontsize(c["new"]) for t in lg.get_texts()]
            _refresh()

        font_all.observe(_on_font_all, names="value")
        font_title.observe(_on_font_title, names="value")
        font_xlabel.observe(_on_font_xlabel, names="value")
        font_ylabel.observe(_on_font_ylabel, names="value")
        font_ticks.observe(_on_font_ticks, names="value")
        font_legend.observe(_on_font_legend, names="value")

        per_btn, per_box, _ = _per_btn("Per element")
        per_box.children = (font_title, font_xlabel, font_ylabel, font_ticks, font_legend)
        sections.append(_section("Typography", font_all, per_btn, per_box))

    # ══ Colors ════════════════════════════════════════════════════════════
    if "colors" in active:
        plot_type = S.detect_plot_type(fig)
        n_series = len(S.get_line_labels(fig))

        _type_label = {
            "categorical": f"categorical · {n_series} series",
            "continuous":  "continuous (colormap)",
            "mixed":       f"mixed · {n_series} categorical + colormap",
        }[plot_type]
        type_badge = widgets.HTML(
            f"<span style='font-size:0.78em;color:#888'>Detected: {_type_label}</span>")

        cat_box_children: list[widgets.Widget] = []

        if plot_type in ("categorical", "mixed"):
            color_mode = widgets.ToggleButtons(
                options=["Palette", "Manual", "Smart"], value="Palette",
                description="Mode:", style={"button_width": "62px"},
                layout=widgets.Layout(width="100%", margin="0 0 4px 0"))

            palette_select = widgets.Dropdown(
                options=palette_names(), description="Palette",
                style={"description_width": "58px"},
                layout=widgets.Layout(width="100%"))
            palette_preview_w = _build_palette_preview(palette_names()[0])
            palette_col = widgets.VBox([palette_select, palette_preview_w],
                                        layout=widgets.Layout(width="100%"))

            line_colors = S.get_line_colors(fig)
            line_labels = S.get_line_labels(fig)
            manual_pickers = [
                widgets.ColorPicker(
                    value=c,
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

            def _apply_colors():
                m = color_mode.value
                if m == "Manual":
                    S.set_line_colors_manual(fig, [p.value for p in manual_pickers])
                elif m == "Smart":
                    S.set_line_colors_manual(fig, smart_palette(smart_n.value))
                else:
                    S.set_line_colors(fig, palette_select.value)
                _refresh()

            def _on_palette_change(c):
                palette_preview_w.value = _build_palette_preview(c["new"]).value
                _apply_colors()

            def _on_smart_n(c):
                smart_preview_w.value = _swatches_div(smart_palette(c["new"]))
                _apply_colors()

            def _on_color_mode_change(c):
                palette_col.layout.display = "none"
                manual_section.layout.display = "none"
                smart_section.layout.display = "none"
                if c["new"] == "Manual":   manual_section.layout.display = ""
                elif c["new"] == "Smart":  smart_section.layout.display = ""
                else:                      palette_col.layout.display = ""
                _apply_colors()

            palette_select.observe(_on_palette_change, names="value")
            color_mode.observe(_on_color_mode_change, names="value")
            smart_n.observe(_on_smart_n, names="value")
            for p in manual_pickers:
                p.observe(lambda _: _apply_colors(), names="value")

            cat_box_children = [color_mode, palette_col, manual_section, smart_section]

        cmap_box_children: list[widgets.Widget] = []

        if plot_type in ("continuous", "mixed"):
            if plot_type == "mixed":
                cmap_box_children.append(widgets.HTML("<hr style='margin:4px 0'>"))
            cmap_type_tb = widgets.ToggleButtons(
                options=["Sequential", "Diverging"], value="Sequential",
                style={"button_width": "90px"}, layout=widgets.Layout(width="100%"))
            _init_cmap = S.get_colormap(fig) or "viridis"
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
                cmap_select.options = opts; cmap_select.value = opts[0]

            def _on_cmap(c):
                cmap_grad_w.value = _build_colormap_gradient(c["new"]).value
                S.set_colormap(fig, c["new"]); _refresh()

            cmap_type_tb.observe(_on_cmap_type, names="value")
            cmap_select.observe(_on_cmap, names="value")
            cmap_box_children += [cmap_type_tb, cmap_select, cmap_grad_w]

        bg_color = widgets.ColorPicker(
            value="#ffffff", description="Background",
            style={"description_width": "82px"}, concise=False,
            layout=widgets.Layout(width="100%"))

        def _on_bg(c):
            if len(c["new"]) == 7:
                S.set_background_color(fig, c["new"]); _refresh()

        bg_color.observe(_on_bg, names="value")
        sections.append(_section("Colors", type_badge,
                                  *cat_box_children, *cmap_box_children, bg_color))

    # ══ Opacity ════════════════════════════════════════════════════════════
    if "alpha" in active:
        alphas = S.get_series_alpha(fig)
        a_labels = S.get_line_labels(fig)
        init_global = (sum(alphas) / len(alphas)) if alphas else 1.0

        global_alpha = widgets.FloatSlider(
            value=init_global, min=0.0, max=1.0, step=0.05,
            description="All series", style={"description_width": "82px"},
            layout=widgets.Layout(width="100%"), continuous_update=False)

        alpha_sliders = [
            widgets.FloatSlider(
                value=a, min=0.0, max=1.0, step=0.05,
                description=(lbl[:13] + "…" if len(lbl) > 13 else lbl),
                style={"description_width": "82px"},
                layout=widgets.Layout(width="100%"), continuous_update=False)
            for a, lbl in zip(alphas, a_labels)
        ]

        _ab = [False]

        def _on_global_alpha(c):
            if _ab[0]: return
            _ab[0] = True
            for s in alpha_sliders: s.value = c["new"]
            _ab[0] = False
            S.set_series_alpha(fig, [c["new"]] * len(alpha_sliders)); _refresh()

        def _on_per_alpha(_):
            if _ab[0]: return
            S.set_series_alpha(fig, [s.value for s in alpha_sliders]); _refresh()

        global_alpha.observe(_on_global_alpha, names="value")
        for s in alpha_sliders:
            s.observe(_on_per_alpha, names="value")

        alpha_children: list[widgets.Widget] = [global_alpha]
        if alpha_sliders:
            per_btn, per_box, _ = _per_btn("Per series")
            per_box.children = tuple(alpha_sliders)
            alpha_children += [per_btn, per_box]
        else:
            alpha_children.append(
                widgets.HTML("<i style='color:#888'>No labeled series.</i>"))

        sections.append(_section("Opacity", *alpha_children))

    # ══ Axes ═══════════════════════════════════════════════════════════════
    if "axes" in active and fig.axes:
        ax_idx = [0]

        ax_selector = None
        if len(fig.axes) > 1:
            ax_selector = widgets.Dropdown(
                options=[(f"Axes {i}", i) for i in range(len(fig.axes))],
                value=0, description="Axes:",
                style={"description_width": "40px"},
                layout=widgets.Layout(width="100%"))

        def _cur_ax(): return fig.axes[ax_idx[0]]

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

        def _on_xlim(_): S.set_xlim(fig, xlim_lo.value, xlim_hi.value, ax_idx[0]); _refresh()
        def _on_ylim(_): S.set_ylim(fig, ylim_lo.value, ylim_hi.value, ax_idx[0]); _refresh()
        def _on_title(_): S.set_title(fig, title_input.value, ax_idx[0]); _refresh()
        def _on_xlabel(_): S.set_xlabel(fig, xlabel_input.value, ax_idx[0]); _refresh()
        def _on_ylabel(_): S.set_ylabel(fig, ylabel_input.value, ax_idx[0]); _refresh()

        xlim_lo.observe(_on_xlim, names="value")
        xlim_hi.observe(_on_xlim, names="value")
        ylim_lo.observe(_on_ylim, names="value")
        ylim_hi.observe(_on_ylim, names="value")
        title_input.observe(_on_title, names="value")
        xlabel_input.observe(_on_xlabel, names="value")
        ylabel_input.observe(_on_ylabel, names="value")

        def _on_ax_select(c):
            ax_idx[0] = c["new"]
            ax = fig.axes[ax_idx[0]]
            title_input.value = ax.get_title()
            xlabel_input.value = ax.get_xlabel()
            ylabel_input.value = ax.get_ylabel()
            xl = ax.get_xlim(); yl = ax.get_ylim()
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
        sections.append(_section("Axes", *axes_children))

    # ══ Legend ══════════════════════════════════════════════════════════════
    if "legend" in active:
        legend_loc = widgets.Dropdown(
            options=S.LEGEND_LOCATIONS, value="best",
            description="Location", style={"description_width": "68px"},
            layout=widgets.Layout(width="100%"))

        def _on_legend_loc(_): S.set_legend_position(fig, legend_loc.value); _refresh()
        legend_loc.observe(_on_legend_loc, names="value")

        leg0 = fig.axes[0].get_legend() if fig.axes else None
        leg_texts = [t.get_text() for t in leg0.get_texts()] if leg0 else []
        name_inputs = [
            widgets.Text(value=txt,
                          description=(txt[:12] + "…:" if len(txt) > 12 else f"{txt}:"),
                          style={"description_width": "78px"},
                          layout=widgets.Layout(width="100%"), continuous_update=False)
            for txt in leg_texts
        ]

        def _on_legend_name(_):
            S.set_legend_labels(fig, [i.value for i in name_inputs]); _refresh()

        for inp in name_inputs:
            inp.observe(_on_legend_name, names="value")

        bbox_header = widgets.HTML(
            "<span style='font-size:0.82em;color:#888'>BBox position (x, y)</span>")
        bbox_x = widgets.FloatSlider(value=1.02, min=0.0, max=1.5, step=0.01,
                                      description="x", style={"description_width": "20px"},
                                      layout=widgets.Layout(width="100%"), continuous_update=False)
        bbox_y = widgets.FloatSlider(value=1.0, min=0.0, max=1.5, step=0.01,
                                      description="y", style={"description_width": "20px"},
                                      layout=widgets.Layout(width="100%"), continuous_update=False)

        def _on_bbox(_): S.set_legend_bbox(fig, bbox_x.value, bbox_y.value); _refresh()

        bbox_x.observe(_on_bbox, names="value")
        bbox_y.observe(_on_bbox, names="value")

        legend_children = (
            [legend_loc]
            + (name_inputs or [widgets.HTML("<i style='color:#888;font-size:0.85em'>No entries.</i>")])
            + [bbox_header, bbox_x, bbox_y]
        )
        sections.append(_section("Legend", *legend_children))

    # ══ Grid & Spines ══════════════════════════════════════════════════════
    if "grid_spines" in active:
        grid_toggle = widgets.Checkbox(value=False, description="Show grid")
        spine_style = widgets.ToggleButtons(
            options=S.SPINE_STYLES, value="box",
            description="Spines:", style={"button_width": "84px"},
            layout=widgets.Layout(width="100%"))

        def _on_grid(_): S.set_grid(fig, grid_toggle.value); _refresh()
        def _on_spine(_): S.set_spine_style(fig, spine_style.value); _refresh()

        grid_toggle.observe(_on_grid, names="value")
        spine_style.observe(_on_spine, names="value")
        sections.append(_section("Grid & Spines", grid_toggle, spine_style))

    # ══ Palette Suggestions ════════════════════════════════════════════════
    if "palette_suggestions" in active:
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
            from .palettes import recommend
            n = len(S.get_line_labels(fig)) or 3
            suggestions = recommend(n, colorblind_safe=suggest_cb.value,
                                    use_case=suggest_use_case.value,
                                    background=suggest_bg.value, top_k=4)
            with recommend_out:
                recommend_out.clear_output()
                if not suggestions:
                    display(widgets.HTML("<i style='color:#888'>No matches.</i>")); return
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
        sections.append(_section("Palette Suggestions",
                                  suggest_use_case, suggest_bg, suggest_cb,
                                  cb_recommend, recommend_out))

    # ══ Unknown section warning ════════════════════════════════════════════
    if unknown:
        names_str = ", ".join(
            "<code style='background:#fee2d5;color:#c0390b;"
            f"padding:1px 5px;border-radius:4px;font-size:0.88em'>{n}</code>"
            for n in sorted(unknown))
        avail_str = ", ".join(f"<code>{n}</code>" for n in sorted(_KNOWN_SECTIONS))
        sections.append(widgets.HTML(
            f'<div class="mpl-w-{_pid}">'
            f"<b>Unknown section(s):</b> {names_str}<br>"
            f'<span class="avail"><b>Available:</b> {avail_str}</span><br>'
            f'<a href="{_GITHUB_ISSUES}/new" target="_blank" style="color:#1a73e8">'
            f"Open a GitHub issue</a> to request a new section.</div>"))

    # ── assemble ──────────────────────────────────────────────────────────
    grid = widgets.GridBox(
        sections,
        layout=widgets.Layout(
            grid_template_columns="repeat(auto-fill, minmax(260px, 1fr))",
            grid_gap="8px", width="100%", overflow="hidden"))

    logo = widgets.HTML(
        "<span style='font-size:1.1em;font-weight:700;letter-spacing:-0.02em'>"
        "mpl<span style='color:var(--mpl-accent,#6366f1)'>studio</span></span>")

    header = widgets.HBox(
        [logo, widgets.HBox([size_toggle, _size_cb],
                             layout=widgets.Layout(align_items="center"))],
        layout=widgets.Layout(justify_content="space-between", align_items="center",
                               width="100%", margin="0 0 6px 0"))

    divider = widgets.HTML(
        "<hr style='margin:6px 0;border:none;border-top:1px solid #e4e4eb'>")

    panel = widgets.VBox(
        [css_w, header, render_out, divider, grid],
        layout=widgets.Layout(width="100%", padding="14px", overflow="hidden"))
    panel.add_class(f"mpl-s-{_pid}")
    display(panel)


# ── helpers ───────────────────────────────────────────────────────────────────

def _swatches_div(colors: list[str]) -> str:
    spans = "".join(
        f"<span style='background:{c};display:inline-block;width:16px;height:16px;"
        f"margin:2px 2px 0 0;border-radius:3px;border:1px solid #ccc'></span>"
        for c in colors)
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
    stops = ", ".join(mcolors.to_hex(cmap(i / (steps - 1))) for i in range(steps))
    return widgets.HTML(value=(
        f"<div style='background:linear-gradient(to right,{stops});"
        f"height:14px;border-radius:6px;margin-top:4px;border:1px solid #ccc'></div>"))
