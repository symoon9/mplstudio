"""Opacity (alpha) style functions."""

from __future__ import annotations

from matplotlib.figure import Figure

from ._artists import _labeled_artists


def set_series_alpha(fig: Figure, alphas: list[float]) -> None:
    """Set opacity per labeled series; call _refresh() after."""
    idx = 0
    for ax in fig.axes:
        for artist, _ in _labeled_artists(ax):
            if idx < len(alphas):
                artist.set_alpha(float(alphas[idx]))
            idx += 1


def get_series_alpha(fig: Figure) -> list[float]:
    return [
        1.0 if artist.get_alpha() is None else float(artist.get_alpha())
        for ax in fig.axes
        for artist, _ in _labeled_artists(ax)
    ]
