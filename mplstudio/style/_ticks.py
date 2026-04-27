"""Tick label and locator style functions."""

from __future__ import annotations

import matplotlib.ticker as ticker
from matplotlib.figure import Figure


def set_tick_labels_visible(
    fig: Figure, x: bool = True, y: bool = True, ax_idx: int = 0
) -> None:
    """Show or hide x/y tick labels for the given axes."""
    if ax_idx >= len(fig.axes):
        return
    ax = fig.axes[ax_idx]
    ax.tick_params(axis="x", labelbottom=x, labeltop=False)
    ax.tick_params(axis="y", labelleft=y, labelright=False)


def set_xtick_rotation(fig: Figure, rotation: float, ax_idx: int = 0) -> None:
    """Rotate x-axis tick labels; set ha='right' when rotated."""
    if ax_idx >= len(fig.axes):
        return
    ha = "right" if rotation > 0 else "center"
    for label in fig.axes[ax_idx].get_xticklabels():
        label.set_rotation(rotation)
        label.set_ha(ha)
    # Also apply to future ticks via tick_params
    fig.axes[ax_idx].tick_params(axis="x", labelrotation=rotation)


def set_tick_interval(
    fig: Figure,
    x_interval: float | None,
    y_interval: float | None,
    ax_idx: int = 0,
) -> None:
    """Set major tick spacing; 0 or None resets to AutoLocator."""
    if ax_idx >= len(fig.axes):
        return
    ax = fig.axes[ax_idx]
    if x_interval:
        ax.xaxis.set_major_locator(ticker.MultipleLocator(x_interval))
    else:
        ax.xaxis.set_major_locator(ticker.AutoLocator())
    if y_interval:
        ax.yaxis.set_major_locator(ticker.MultipleLocator(y_interval))
    else:
        ax.yaxis.set_major_locator(ticker.AutoLocator())
