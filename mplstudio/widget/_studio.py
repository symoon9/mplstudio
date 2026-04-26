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
    _img_id = f"mpl-img-{_pid}"   # unique id for the preview <img> element

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
                f'<div style="{ds}"><img id="{_img_id}" src="data:image/png;base64,{img_b64}" style="{is_}"></div>'
            ))

    _size_cb.observe(lambda _: _refresh(), names="value")
    _refresh()

    # ── copy / save toolbar ───────────────────────────────────────────────
    # Single-quoted onclick so double-quotes work freely inside the JS.
    _ibtn = (
        "cursor:pointer;background:transparent;"
        "border:1.5px solid var(--mpl-accent,#6366f1);"
        "color:var(--mpl-accent,#6366f1);border-radius:6px;"
        "padding:2px 9px;font-size:0.78em;font-family:inherit;"
        "transition:opacity 0.15s;"
    )
    _copy_js = (
        f'var img=document.getElementById("{_img_id}");'
        f'var btn=this;'
        f'fetch(img.src).then(r=>r.blob())'
        f'.then(b=>navigator.clipboard.write([new ClipboardItem({{"image/png":b}})]))'
        f'.then(()=>{{btn.textContent="✓ Copied";setTimeout(()=>btn.textContent="Copy",1500)}})'
        f'.catch(()=>{{btn.textContent="Failed";setTimeout(()=>btn.textContent="Copy",1500)}})'
    )
    _save_js = (
        f'var a=document.createElement("a");'
        f'a.href=document.getElementById("{_img_id}").src;'
        f'a.download="figure.png";a.click()'
    )
    img_toolbar = widgets.HTML(
        f'<span style="display:inline-flex;gap:5px;align-items:center">'
        f'<button style="{_ibtn}" onclick=\'{_copy_js}\'>Copy</button>'
        f'<button style="{_ibtn}" onclick=\'{_save_js}\'>Save</button>'
        f'</span>'
    )

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
        [logo, widgets.HBox([img_toolbar, size_toggle, _size_cb],
                            layout=widgets.Layout(align_items="center", gap="10px"))],
        layout=widgets.Layout(justify_content="space-between", align_items="center",
                              width="100%", margin="0 0 6px 0"))

    divider = widgets.HTML(
        "<hr style='margin:6px 0;border:none;border-top:1px solid #e4e4eb'>")

    panel = widgets.VBox(
        [css_w, header, render_out, divider, grid],
        layout=widgets.Layout(width="100%", padding="14px", overflow="hidden"))
    panel.add_class(f"mpl-s-{_pid}")
    display(panel)
