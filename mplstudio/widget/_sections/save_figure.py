"""Save Figure section builder."""

from __future__ import annotations

import os
import threading

import ipywidgets as widgets

from .._ctx import _PanelCtx
from .._helpers import _section


def build(ctx: _PanelCtx) -> widgets.VBox:
    filename = widgets.Text(
        value="figure", description="Name",
        style={"description_width": "52px"},
        layout=widgets.Layout(width="100%"), continuous_update=False)

    save_path = widgets.Text(
        value=".", description="Path",
        style={"description_width": "52px"},
        layout=widgets.Layout(width="100%"), continuous_update=False)

    dpi_in = widgets.BoundedIntText(
        value=int(ctx.fig.dpi), min=72, max=600, step=1,
        description="DPI",
        style={"description_width": "52px"},
        layout=widgets.Layout(width="100%"))

    fmt = widgets.Dropdown(
        options=["png", "jpg", "pdf", "svg", "eps"],
        value="png", description="Format",
        style={"description_width": "52px"},
        layout=widgets.Layout(width="100%"))

    save_btn = widgets.Button(
        description="Save", button_style="info",
        layout=widgets.Layout(width="100%"))

    status = widgets.HTML(value="")

    def _on_save(_):
        name = filename.value.strip() or "figure"
        directory = save_path.value.strip() or "."
        path = os.path.join(directory, f"{name}.{fmt.value}")
        try:
            ctx.fig.savefig(path, dpi=dpi_in.value, bbox_inches="tight")
            status.value = (
                f"<span style='color:#22c55e;font-size:0.82em'>✓ Saved: {path}</span>")
        except Exception as e:
            status.value = (
                f"<span style='color:#ef4444;font-size:0.82em'>✗ {e}</span>")
        threading.Timer(3.0, lambda: setattr(status, "value", "")).start()

    save_btn.on_click(_on_save)
    return _section("Save Figure", ctx.pid, filename, save_path, dpi_in, fmt, save_btn, status)
