"""Main studio() entry point."""

from __future__ import annotations

import base64
import io
import threading

import ipywidgets as widgets
import matplotlib.pyplot as plt
from IPython.display import Javascript
from IPython.display import display
from matplotlib.figure import Figure

from ._constants import _PREVIEW_HEIGHT, _KNOWN_SECTIONS, _GITHUB_ISSUES
from ._theme import _theme_css
from ._ctx import _PanelCtx
from ._sections import (
    figure_size as _sec_figure_size,
    typography as _sec_typography,
    colors as _sec_colors,
    opacity as _sec_opacity,
    axes as _sec_axes,
    ticks as _sec_ticks,
    legend as _sec_legend,
    grid_spines as _sec_grid_spines,
    palette_suggestions as _sec_palette_suggestions,
    save as _sec_save,
)

# Ordered list of (section_name, builder_module) pairs
_SECTION_BUILDERS = [
    ("save",                _sec_save),
    ("figure_size",         _sec_figure_size),
    ("typography",          _sec_typography),
    ("legend",              _sec_legend),
    ("colors",              _sec_colors),
    ("alpha",               _sec_opacity),
    ("axes",                _sec_axes),
    ("ticks",               _sec_ticks),
    ("grid_spines",         _sec_grid_spines),
    ("palette_suggestions", _sec_palette_suggestions),
]


def available_sections() -> list[str]:
    return sorted(_KNOWN_SECTIONS)


def studio(
    fig: Figure | None = None,
    *,
    show: list[str] | None = None,
    dark: bool = False,
    palette: dict[str, str] | None = None,
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
    palette : dict[str, str], optional
        Label → hex color mapping (e.g. ``adata.uns["cell_type_colors"]``).
        When provided, a "Custom" color mode is added to the Colors section.
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

    # ── pid (unique per panel) ────────────────────────────────────────────
    # Use a hidden Label as the pid source — model_id is unique per widget.
    _anchor = widgets.Label("", layout=widgets.Layout(display="none"))
    _pid = _anchor.model_id[:8]

    css_w = widgets.HTML(value=_theme_css(_pid, dark))

    # ── Copy button (ipywidgets.Button — works in all environments)
    # HTML onclick is stripped by VSCode's sanitizer; Python callbacks are not.
    copy_btn = widgets.Button(
        description="Copy",
        button_style="info",
        layout=widgets.Layout(width="auto"),
    )

    # Hidden Output used to execute clipboard JS without polluting the preview.
    _js_out = widgets.Output(layout=widgets.Layout(display="none"))

    def _fig_png() -> bytes:
        buf = io.BytesIO()
        fig.savefig(buf, format="png", bbox_inches="tight", dpi=fig.dpi)
        buf.seek(0)
        return buf.read()

    def _on_copy(_):
        png = _fig_png()
        img_b64 = base64.b64encode(png).decode()
        # Try clipboard via JS. Works in Jupyter / JupyterLab (Chrome-based).
        # May not work in VSCode webview due to clipboard-write permission policy.
        js = (
            'fetch("data:image/png;base64,' + img_b64 + '")'
            ".then(r=>r.blob())"
            '.then(b=>navigator.clipboard.write([new ClipboardItem({"image/png":b})]))'
            ".catch(e=>console.warn('clipboard write failed:',e));"
        )
        with _js_out:
            _js_out.clear_output()
            display(Javascript(js))
        copy_btn.description = "✓ Copied"
        threading.Timer(1.5, lambda: setattr(copy_btn, "description", "Copy")).start()

    copy_btn.on_click(_on_copy)

    # ── render output ─────────────────────────────────────────────────────
    render_out = widgets.Output(layout=widgets.Layout(width="100%", margin="0 0 4px 0"))

    def _refresh(*_):
        png = _fig_png()
        data_url = "data:image/png;base64," + base64.b64encode(png).decode()
        is_ = (
            f"max-height:{_PREVIEW_HEIGHT}px;width:auto;"
            "max-width:100%;display:inline-block;vertical-align:top"
        )
        with render_out:
            render_out.clear_output(wait=True)
            display(widgets.HTML(
                f'<div style="text-align:center;width:100%">'
                f'<img src="{data_url}" style="{is_}"></div>'
            ))

    _refresh()

    # ── build shared context ──────────────────────────────────────────────
    ctx = _PanelCtx(fig=fig, pid=_pid, dark=dark, refresh=_refresh, palette=palette)

    # ── build sections ────────────────────────────────────────────────────
    sections: list[widgets.Widget] = []
    for name, builder in _SECTION_BUILDERS:
        if name in active:
            result = builder.build(ctx)
            if result is not None:
                sections.append(result)

    # ── unknown section warning ───────────────────────────────────────────
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

    # ── assemble and display ──────────────────────────────────────────────
    grid = widgets.GridBox(
        sections,
        layout=widgets.Layout(
            grid_template_columns="repeat(auto-fill, minmax(260px, 1fr))",
            grid_gap="8px", width="100%", overflow="hidden"))

    logo = widgets.HTML(
        "<span style='font-size:20px;font-weight:700;letter-spacing:-0.02em'>"
        "mpl<span style='color:var(--mpl-accent,#6366f1)'>studio</span></span>")

    header = widgets.HBox(
        [logo, copy_btn],
        layout=widgets.Layout(
            justify_content="space-between", align_items="center",
            width="100%", margin="0 0 6px 0",
        ),
    )

    divider = widgets.HTML(
        "<hr style='margin:6px 0;border:none;border-top:1px solid #e4e4eb'>")

    panel = widgets.VBox(
        [css_w, _anchor, header, render_out, divider, grid, _js_out],
        layout=widgets.Layout(width="100%", padding="14px", overflow="hidden"))
    panel.add_class(f"mpl-s-{_pid}")
    display(panel)
