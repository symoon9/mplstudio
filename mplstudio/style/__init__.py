"""Pure functions that mutate a matplotlib Figure/Axes in-place."""

from ._artists import (
    _continuous_artists,
    _labeled_artists,
    _get_artist_color,
    _set_artist_color,
    _sync_legend_colors,
)
from ._figure import set_figure_size, set_background_color, redraw
from ._typography import set_font_size
from ._colors import (
    detect_plot_type,
    set_colormap,
    get_colormap,
    set_line_colors,
    set_line_colors_manual,
    get_line_colors,
    get_line_labels,
)
from ._opacity import set_series_alpha, get_series_alpha
from ._axes import set_title, set_xlabel, set_ylabel, set_xlim, set_ylim
from ._legend import (
    set_legend_position,
    set_legend_labels,
    set_legend_bbox,
    set_legend_title,
    LEGEND_LOCATIONS,
)
from ._grid_spines import set_grid, set_spine_style, SPINE_STYLES

__all__ = [
    # figure
    "set_figure_size", "set_background_color", "redraw",
    # typography
    "set_font_size",
    # colors
    "detect_plot_type", "set_colormap", "get_colormap",
    "set_line_colors", "set_line_colors_manual",
    "get_line_colors", "get_line_labels",
    # opacity
    "set_series_alpha", "get_series_alpha",
    # axes
    "set_title", "set_xlabel", "set_ylabel", "set_xlim", "set_ylim",
    # legend
    "set_legend_position", "set_legend_labels", "set_legend_bbox",
    "set_legend_title", "LEGEND_LOCATIONS",
    # grid & spines
    "set_grid", "set_spine_style", "SPINE_STYLES",
]
