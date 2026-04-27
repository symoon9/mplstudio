"""Grid and spine style functions."""

from __future__ import annotations

from matplotlib.figure import Figure


SPINE_STYLES = ["Box", "2-Side", "None"]


def set_grid(fig: Figure, visible: bool, alpha: float = 0.3) -> None:
    for ax in fig.axes:
        ax.grid(visible)
        if visible:
            ax.grid(alpha=alpha)


def set_spine_style(fig: Figure, style: str) -> None:
    """style: 'Box' | '2-Side' | 'None '"""
    for ax in fig.axes:
        if style == "Box":
            for spine in ax.spines.values():
                spine.set_visible(True)
        elif style == "2-Side":
            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)
            ax.spines["left"].set_visible(True)
            ax.spines["bottom"].set_visible(True)
        elif style == "None":
            for spine in ax.spines.values():
                spine.set_visible(False)
