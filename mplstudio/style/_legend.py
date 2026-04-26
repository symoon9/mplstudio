"""Legend style functions."""

from __future__ import annotations

from matplotlib.figure import Figure


LEGEND_LOCATIONS = [
    "best", "upper right", "upper left", "lower left", "lower right",
    "right", "center left", "center right", "lower center", "upper center", "center",
]


def set_legend_position(fig: Figure, location: str) -> None:
    for ax in fig.axes:
        legend = ax.get_legend()
        if legend:
            # Preserve user-edited label text when recreating the legend
            handles = legend.legend_handles
            labels = [t.get_text() for t in legend.get_texts()]
            if handles:
                ax.legend(handles=handles, labels=labels, loc=location)


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
