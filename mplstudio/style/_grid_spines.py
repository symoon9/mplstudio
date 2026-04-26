"""Grid and spine style functions."""

from __future__ import annotations

from matplotlib.figure import Figure


SPINE_STYLES = ["box", "left-bottom", "none"]


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
