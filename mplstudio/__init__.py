"""mplstudio — GUI styling tool for matplotlib figures in Jupyter."""

from .widget import studio, available_sections
from .palettes import PALETTES, get_palette, recommend, palette_names, SEQUENTIAL_CMAPS, DIVERGING_CMAPS

__version__ = "0.1.0"
__all__ = [
    "studio", "available_sections",
    "PALETTES", "get_palette", "recommend", "palette_names",
    "SEQUENTIAL_CMAPS", "DIVERGING_CMAPS",
]
