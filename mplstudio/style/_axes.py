"""Per-axis label and limit style functions."""

from __future__ import annotations

from matplotlib.figure import Figure


def set_title(fig: Figure, title: str, ax_idx: int = 0) -> None:
    if ax_idx < len(fig.axes):
        fig.axes[ax_idx].set_title(title)


def set_xlabel(fig: Figure, label: str, ax_idx: int = 0) -> None:
    if ax_idx < len(fig.axes):
        fig.axes[ax_idx].set_xlabel(label)


def set_ylabel(fig: Figure, label: str, ax_idx: int = 0) -> None:
    if ax_idx < len(fig.axes):
        fig.axes[ax_idx].set_ylabel(label)


def set_xlim(fig: Figure, vmin: float, vmax: float, ax_idx: int = 0) -> None:
    if ax_idx < len(fig.axes) and vmin < vmax:
        fig.axes[ax_idx].set_xlim(vmin, vmax)


def set_ylim(fig: Figure, vmin: float, vmax: float, ax_idx: int = 0) -> None:
    if ax_idx < len(fig.axes) and vmin < vmax:
        fig.axes[ax_idx].set_ylim(vmin, vmax)
