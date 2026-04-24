"""Pure functions that mutate a matplotlib Figure/Axes in-place."""

from __future__ import annotations

import matplotlib
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
from matplotlib.figure import Figure

from .palettes import get_palette


def set_figure_size(fig: Figure, width: float, height: float) -> None:
    fig.set_size_inches(width, height)


def set_font_size(fig: Figure, size: float) -> None:
    for ax in fig.axes:
        ax.title.set_fontsize(size)
        ax.xaxis.label.set_fontsize(size)
        ax.yaxis.label.set_fontsize(size)
        ax.tick_params(labelsize=max(size - 2, 6))
        legend = ax.get_legend()
        if legend:
            for text in legend.get_texts():
                text.set_fontsize(size)


def set_legend_position(fig: Figure, location: str) -> None:
    for ax in fig.axes:
        legend = ax.get_legend()
        if legend:
            handles, labels = ax.get_legend_handles_labels()
            if handles:
                ax.legend(handles, labels, loc=location)


def set_line_colors(fig: Figure, palette_name: str) -> None:
    colors = get_palette(palette_name)
    for ax in fig.axes:
        lines = ax.get_lines()
        for i, line in enumerate(lines):
            line.set_color(colors[i % len(colors)])


def set_line_colors_manual(fig: Figure, colors: list[str]) -> None:
    """Apply per-line colors from a list of hex strings, one entry per line."""
    all_lines = [line for ax in fig.axes for line in ax.get_lines()]
    for line, color in zip(all_lines, colors):
        line.set_color(color)


def get_line_colors(fig: Figure) -> list[str]:
    """Return current hex color of every line in the figure, in draw order."""
    return [
        mcolors.to_hex(line.get_color())
        for ax in fig.axes
        for line in ax.get_lines()
    ]


def get_line_labels(fig: Figure) -> list[str]:
    """Return display labels for every line (falls back to 'Line N')."""
    labels = []
    n = 0
    for ax in fig.axes:
        for line in ax.get_lines():
            n += 1
            lbl = line.get_label()
            labels.append(lbl if lbl and not lbl.startswith("_") else f"Line {n}")
    return labels


def set_background_color(fig: Figure, color: str) -> None:
    fig.patch.set_facecolor(color)
    for ax in fig.axes:
        ax.set_facecolor(color)


def set_grid(fig: Figure, visible: bool, alpha: float = 0.3) -> None:
    for ax in fig.axes:
        ax.grid(visible)
        if visible:
            ax.grid(alpha=alpha)


def set_spine_style(fig: Figure, style: str) -> None:
    """style: 'box' | 'left-bottom' | 'none'"""
    for ax in fig.axes:
        if style == "box":
            for spine in ax.spines.values():
                spine.set_visible(True)
        elif style == "left-bottom":
            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)
            ax.spines["left"].set_visible(True)
            ax.spines["bottom"].set_visible(True)
        elif style == "none":
            for spine in ax.spines.values():
                spine.set_visible(False)


def redraw(fig: Figure) -> None:
    """Force a synchronous canvas refresh for both ipympl and inline backends.

    draw_idle() is async and ipympl may deduplicate or skip repeated calls,
    so we use the synchronous draw() followed by flush_events() instead.
    """
    canvas = fig.canvas
    canvas.draw()
    if hasattr(canvas, "flush_events"):
        canvas.flush_events()


LEGEND_LOCATIONS = [
    "best", "upper right", "upper left", "lower left", "lower right",
    "right", "center left", "center right", "lower center", "upper center", "center",
]

SPINE_STYLES = ["box", "left-bottom", "none"]
