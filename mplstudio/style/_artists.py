"""Private artist helpers shared across style sub-modules."""

from __future__ import annotations

import matplotlib.colors as mcolors
from matplotlib.collections import PathCollection
from matplotlib.figure import Figure
from matplotlib.lines import Line2D


_UNLABELED = {"", "_nolegend_"}


def _continuous_artists(fig: Figure):
    """Yield artists that carry a scalar colormap (AxesImage, QuadMesh, etc.).

    Covers scanpy continuous UMAP where a PathCollection uses set_array() for
    per-point values and has an empty or _nolegend_ label.
    """
    for ax in fig.axes:
        for img in ax.get_images():
            yield img
        for coll in ax.collections:
            lbl = getattr(coll, "get_label", lambda: "_")()
            has_scalar = hasattr(coll, "get_array") and coll.get_array() is not None
            if has_scalar and (lbl.startswith("_") or lbl in _UNLABELED):
                yield coll


def _labeled_artists(ax):
    """Yield (actual_artist, label) for every legend-visible series, in legend order.

    Works for Line2D (line plots) and PathCollection (scatter plots), including
    scanpy categorical UMAP where each category is a separate PathCollection.
    Falls back to direct collection scan when no legend exists.
    """
    handles, labels = ax.get_legend_handles_labels()
    candidates: dict[str, object] = {}
    for a in (*ax.get_lines(), *ax.collections):
        lbl = a.get_label()
        if lbl and not lbl.startswith("_") and lbl not in _UNLABELED and lbl not in candidates:
            candidates[lbl] = a

    if handles:
        for _, label in zip(handles, labels):
            if label in candidates:
                yield candidates[label], label
    else:
        # No legend (e.g. scanpy without legend_loc): yield in artist order
        for lbl, artist in candidates.items():
            yield artist, lbl


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
        # Preserve the existing facecolor alpha (scatter alpha lives in RGBA channel)
        fc = artist.get_facecolor()
        alpha = float(fc[0, 3]) if len(fc) else 1.0
        artist.set_facecolor((*mcolors.to_rgb(color), alpha))
        # Only sync edge colour if edges were originally visible
        ec = artist.get_edgecolor()
        if len(ec) and ec[0, 3] > 0.01:
            artist.set_edgecolor((*mcolors.to_rgb(color), float(ec[0, 3])))


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
