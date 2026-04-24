"""mplstudio — GUI styling tool for matplotlib figures in Jupyter."""

from .widget import studio
from .palettes import PALETTES, get_palette, recommend, palette_names

__version__ = "0.1.0"
__all__ = ["studio", "PALETTES", "get_palette", "recommend", "palette_names"]
