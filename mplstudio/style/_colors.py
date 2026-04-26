"""Color and colormap style functions."""

from __future__ import annotations

from matplotlib.figure import Figure

from ._artists import (
    _continuous_artists,
    _labeled_artists,
    _get_artist_color,
    _set_artist_color,
    _sync_legend_colors,
)
from ..palettes import get_palette


def detect_plot_type(fig: Figure) -> str:
    """Return ``'categorical'``, ``'continuous'``, or ``'mixed'`` based on figure contents."""
    has_categorical = bool(get_line_labels(fig))
    has_continuous = any(True for _ in _continuous_artists(fig))
    if has_categorical and has_continuous:
        return "mixed"
    if has_continuous:
        return "continuous"
    return "categorical"


def set_colormap(fig: Figure, cmap_name: str) -> None:
    """Apply *cmap_name* to all image and scalar-mapped collection artists."""
    for artist in _continuous_artists(fig):
        artist.set_cmap(cmap_name)


def get_colormap(fig: Figure) -> str | None:
    """Return the colormap name of the first continuous artist, or ``None``."""
    for artist in _continuous_artists(fig):
        return artist.get_cmap().name
    return None


def set_line_colors(fig: Figure, palette_name: str) -> None:
    colors = get_palette(palette_name)
    idx = 0
    for ax in fig.axes:
        for artist, _ in _labeled_artists(ax):
            _set_artist_color(artist, colors[idx % len(colors)])
            idx += 1
        _sync_legend_colors(ax)


def set_line_colors_manual(fig: Figure, colors: list[str]) -> None:
    """Apply per-series colors from a list of hex strings, matching legend order."""
    idx = 0
    for ax in fig.axes:
        for artist, _ in _labeled_artists(ax):
            if idx < len(colors):
                _set_artist_color(artist, colors[idx])
            idx += 1
        _sync_legend_colors(ax)


def get_line_colors(fig: Figure) -> list[str]:
    """Return current hex color of every labeled series, in legend order."""
    return [
        _get_artist_color(artist)
        for ax in fig.axes
        for artist, _ in _labeled_artists(ax)
    ]


def get_line_labels(fig: Figure) -> list[str]:
    """Return legend labels for every labeled series, in legend order."""
    return [
        label
        for ax in fig.axes
        for _, label in _labeled_artists(ax)
    ]
