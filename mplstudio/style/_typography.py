"""Typography (font size) style functions."""

from __future__ import annotations

from matplotlib.figure import Figure


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
