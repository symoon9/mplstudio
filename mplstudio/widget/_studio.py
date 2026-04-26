"""Main studio() entry point."""

from __future__ import annotations

import base64
import io

import ipywidgets as widgets
import matplotlib.pyplot as plt
from IPython.display import display
from matplotlib.figure import Figure

from ._constants import _PREVIEW_HEIGHT, _KNOWN_SECTIONS, _GITHUB_ISSUES
from ._theme import _theme_css, _ios_toggle
from ._ctx import _PanelCtx
from ._sections import (
    figure_size as _sec_figure_size,
    typography as _sec_typography,
    colors as _sec_colors,
    opacity as _sec_opacity,
    axes as _sec_axes,
    legend as _sec_legend,
    grid_spines as _sec_grid_spines,
    palette_suggestions as _sec_palette_suggestions,
)

# Ordered list of (section_name, builder_module) pairs
_SECTION_BUILDERS = [
    ("figure_size",         _sec_figure_size),
    ("typography",          _sec_typography),
    ("colors",              _sec_colors),
    ("alpha",               _sec_opacity),
    ("axes",                _sec_axes),
    ("legend",              _sec_legend),
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

    # Accent color for toolbar buttons — matches the active theme.
    _accent = "#89b4fa" if dark else "#6366f1"
    _btn_style = (
        f"cursor:pointer;background:transparent;"
        f"border:1.5px solid {_accent};color:{_accent};"
        f"border-radius:6px;padding:2px 9px;font-size:0.78em;"
        f"font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;"
        f"margin-left:4px;"
    )

    def _refresh(*_):
        buf = io.BytesIO()
        fig.savefig(buf, format="png", bbox_inches="tight", dpi=fig.dpi)
        buf.seek(0)
        img_b64 = base64.b64encode(buf.read()).decode()
        data_url = f"data:image/png;base64,{img_b64}"

        if _size_cb.value:
            ds = "text-align:center;overflow-x:auto;width:100%"
            is_ = "height:auto;display:inline-block;vertical-align:top"
        else:
            ds = "text-align:center;width:100%"
            is_ = (f"max-height:{_PREVIEW_HEIGHT}px;width:auto;"
                   "max-width:100%;display:inline-block;vertical-align:top")

        # Buttons and image share the same HTML widget so they are always
        # in the same DOM context — works in Jupyter, JupyterLab, and VSCode.
        # The data URL is embedded directly in the JS so no getElementById is needed.
        # Single-quoted onclick so double-quotes work freely inside the JS.
        copy_js = (
            f'var btn=this;'
            f'fetch("{data_url}").then(r=>r.blob())'
            f'.then(b=>navigator.clipboard.write([new ClipboardItem({{"image/png":b}})]))'
            f'.then(()=>{{btn.textContent="✓ Copied";setTimeout(()=>btn.textContent="Copy",1500)}})'
            f'.catch(()=>{{btn.textContent="⚠ Not supported";setTimeout(()=>btn.textContent="Copy",2000)}})'
        )
        save_js = (
            f'var a=document.createElement("a");'
            f'a.href="{data_url}";a.download="figure.png";a.click()'
        )
        toolbar = (
            f'<div style="text-align:right;margin-bottom:3px">'
            f'<button style="{_btn_style}" onclick=\'{copy_js}\'>Copy</button>'
            f'<button style="{_btn_style}" onclick=\'{save_js}\'>Save</button>'
            f'</div>'
        )
        with render_out:
            render_out.clear_output(wait=True)
            display(widgets.HTML(
                toolbar + f'<div style="{ds}"><img src="{data_url}" style="{is_}"></div>'
            ))

    _size_cb.observe(lambda _: _refresh(), names="value")
    _refresh()

    # ── build shared context ──────────────────────────────────────────────
    ctx = _PanelCtx(fig=fig, pid=_pid, dark=dark, refresh=_refresh)

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
