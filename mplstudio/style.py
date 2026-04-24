"""Pure functions that mutate a matplotlib Figure/Axes in-place."""

from __future__ import annotations

import matplotlib.colors as mcolors
from matplotlib.collections import PathCollection
from matplotlib.figure import Figure
from matplotlib.lines import Line2D

from .palettes import get_palette


# ── artist helpers ────────────────────────────────────────────────────────────

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


# ── public style functions ────────────────────────────────────────────────────

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
            # Preserve user-edited label text when recreating the legend
            handles = legend.legend_handles
            labels = [t.get_text() for t in legend.get_texts()]
            if handles:
                ax.legend(handles=handles, labels=labels, loc=location)


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


def set_legend_labels(fig: Figure, labels: list[str], ax_idx: int = 0) -> None:
    """Edit legend entry text in-place without recreating the legend."""
    if ax_idx >= len(fig.axes):
        return
    legend = fig.axes[ax_idx].get_legend()
    if legend is None:
        return
    for text, new_label in zip(legend.get_texts(), labels):
        text.set_text(new_label)


def set_legend_bbox(fig: Figure, x: float, y: float, ax_idx: int = 0) -> None:
    """Move the legend by adjusting bbox_to_anchor in-place."""
    if ax_idx >= len(fig.axes):
        return
    legend = fig.axes[ax_idx].get_legend()
    if legend:
        legend.set_bbox_to_anchor((x, y))


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
    """Force a synchronous canvas refresh."""
    canvas = fig.canvas
    canvas.draw()
    if hasattr(canvas, "flush_events"):
        canvas.flush_events()


LEGEND_LOCATIONS = [
    "best", "upper right", "upper left", "lower left", "lower right",
    "right", "center left", "center right", "lower center", "upper center", "center",
]

SPINE_STYLES = ["box", "left-bottom", "none"]
