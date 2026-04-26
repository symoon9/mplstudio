"""Figure-level style functions."""

from __future__ import annotations

from matplotlib.figure import Figure


def set_figure_size(fig: Figure, width: float, height: float) -> None:
    fig.set_size_inches(width, height)


def set_background_color(fig: Figure, color: str) -> None:
    fig.patch.set_facecolor(color)
    for ax in fig.axes:
        ax.set_facecolor(color)


def redraw(fig: Figure) -> None:
    """Force a synchronous canvas refresh."""
    canvas = fig.canvas
    canvas.draw()
    if hasattr(canvas, "flush_events"):
        canvas.flush_events()
