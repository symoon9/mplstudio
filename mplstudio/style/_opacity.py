"""Opacity (alpha) style functions."""

from __future__ import annotations

from matplotlib.collections import PathCollection
from matplotlib.figure import Figure

from ._artists import _labeled_artists


def _get_artist_alpha(artist) -> float:
    """Return effective alpha for an artist.

    For PathCollection, alpha is stored in the facecolor RGBA channel (set by
    scatter's alpha= kwarg).  The artist-level alpha (get_alpha()) may ALSO be
    set to the same value, which would cause double-multiplication during
    rendering.  We use the facecolor channel as the single source of truth.
    """
    if isinstance(artist, PathCollection):
        fc = artist.get_facecolor()
        return float(fc[0, 3]) if len(fc) else 1.0
    return 1.0 if artist.get_alpha() is None else float(artist.get_alpha())


def _set_artist_alpha(artist, alpha: float) -> None:
    """Set alpha without double-multiplication for PathCollection artists."""
    if isinstance(artist, PathCollection):
        # Drive opacity via the facecolor RGBA channel; clear artist-level alpha
        fc = artist.get_facecolor().copy()
        fc[:, 3] = alpha
        artist.set_facecolor(fc)
        ec = artist.get_edgecolor().copy()
        if len(ec) and ec[0, 3] > 0.01:  # only update visible edges
            ec[:, 3] = alpha
            artist.set_edgecolor(ec)
        artist.set_alpha(None)            # prevent double-alpha multiplication
    else:
        artist.set_alpha(alpha)


def set_series_alpha(fig: Figure, alphas: list[float]) -> None:
    """Set opacity per labeled series; call _refresh() after."""
    idx = 0
    for ax in fig.axes:
        for artist, _ in _labeled_artists(ax):
            if idx < len(alphas):
                _set_artist_alpha(artist, float(alphas[idx]))
            idx += 1


def get_series_alpha(fig: Figure) -> list[float]:
    return [
        _get_artist_alpha(artist)
        for ax in fig.axes
        for artist, _ in _labeled_artists(ax)
    ]
