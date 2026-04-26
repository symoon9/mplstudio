"""Private artist helpers shared across style sub-modules."""

from __future__ import annotations

import matplotlib.colors as mcolors
from matplotlib.collections import PathCollection
from matplotlib.figure import Figure
from matplotlib.lines import Line2D


def _continuous_artists(fig: Figure):
    """Yield artists that carry a scalar colormap (AxesImage, QuadMesh, etc.)."""
    for ax in fig.axes:
        for img in ax.get_images():
            yield img
        for coll in ax.collections:
            lbl = getattr(coll, "get_label", lambda: "_")()
            # Unlabeled collections with scalar data → continuous (pcolormesh, contourf…)
            if lbl.startswith("_") and hasattr(coll, "get_array") and coll.get_array() is not None:
                yield coll


def _labeled_artists(ax):
    """Yield (actual_artist, label) for every legend-visible series, in legend order.

    Works for both Line2D (line plots) and PathCollection (scatter plots).
    Matches legend labels to actual axes artists so both can be coloured.
    """
    handles, labels = ax.get_legend_handles_labels()
    # Build label→actual-artist lookup (first occurrence wins)
    candidates: dict[str, object] = {}
    for a in (*ax.get_lines(), *ax.collections):
        lbl = a.get_label()
        if lbl and not lbl.startswith("_") and lbl not in candidates:
            candidates[lbl] = a
    for _, label in zip(handles, labels):
        if label in candidates:
            yield candidates[label], label


def _get_artist_color(artist) -> str:
    if isinstance(artist, Line2D):
        return mcolors.to_hex(artist.get_color())
    if isinstance(artist, PathCollection):
        fc = artist.get_facecolor()
        if len(fc):
            return mcolors.to_hex(fc[0, :3])
    return "#000000"


def _set_artist_color(artist, color: str) -> None:
    if isinstance(artist, Line2D):
        artist.set_color(color)
    elif isinstance(artist, PathCollection):
        artist.set_facecolor(color)
        artist.set_edgecolor(color)


def _sync_legend_colors(ax) -> None:
    """Update legend handle colors to match the current artist colors.

    ax.get_legend_handles_labels() returns the original axes artists, not the
    legend's internal handle copies. We must iterate legend.legend_handles
    directly and match by label from legend.get_texts().
    """
    legend = ax.get_legend()
    if legend is None:
        return
    legend_handles = legend.legend_handles
    legend_labels = [t.get_text() for t in legend.get_texts()]
    candidates: dict[str, object] = {}
    for a in (*ax.get_lines(), *ax.collections):
        lbl = a.get_label()
        if lbl and not lbl.startswith("_") and lbl not in candidates:
            candidates[lbl] = a
    for handle, label in zip(legend_handles, legend_labels):
        artist = candidates.get(label)
        if artist is None:
            continue
        color = _get_artist_color(artist)
        try:
            handle.set_color(color)
        except AttributeError:
            try:
                handle.set_facecolor(color)
                handle.set_edgecolor(color)
            except AttributeError:
                pass
