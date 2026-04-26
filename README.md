# mplstudio

[![PyPI version](https://img.shields.io/pypi/v/mplstudio)](https://pypi.org/project/mplstudio/)
[![Python](https://img.shields.io/pypi/pyversions/mplstudio)](https://pypi.org/project/mplstudio/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![CI](https://github.com/symoon9/mplstudio/actions/workflows/ci.yml/badge.svg)](https://github.com/symoon9/mplstudio/actions/workflows/ci.yml)

An **interactive GUI** for **styling matplotlib figures** directly in Jupyter.

Adjust colors, fonts, axes, legends, and more in real time **without touching your plot code.**


## Installation

```bash
pip install mplstudio
```

Requires `Python 3.9+`, Jupyter Notebook or JupyterLab, and `matplotlib ≥ 3.5`.


## Quick Start

```python
import matplotlib.pyplot as plt
import mplstudio

fig, ax = plt.subplots()
ax.plot([1, 2, 3], [1, 4, 9], label="y = x²")
ax.plot([1, 2, 3], [1, 2, 3], label="y = x")
ax.legend()

mplstudio.studio(fig)
```

![mplstudio control panel](docs/screenshot.png)

For detailed usage examples, see [`examples/demo.ipynb`](examples/demo.ipynb).


## API Reference

### `mplstudio.studio(fig, *, show=None, dark=False)`

Display the styling control panel for a matplotlib figure.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `fig` | `Figure \| None` | `plt.gcf()` | Target figure. Uses the current figure if omitted. |
| `show` | `list[str] \| None` | `None` | Section names to display. `None` shows all sections. |
| `dark` | `bool` | `False` | Use Catppuccin Mocha dark theme. |

```python
# Show only specific sections
mplstudio.studio(fig, show=["colors", "axes", "legend"])

# Dark theme
mplstudio.studio(fig, dark=True)
```

### `mplstudio.available_sections()`

Return a sorted list of all valid section names.

```python
mplstudio.available_sections()
# ['alpha', 'axes', 'colors', 'figure_size', 'grid_spines',
#  'legend', 'palette_suggestions', 'typography']
```


## Available Sections

| Section | Controls |
|---------|----------|
| `figure_size` | Width and height sliders |
| `typography` | Font size for all elements or individually (title, labels, ticks, legend) |
| `colors` | Palette picker, manual per-series color pickers, smart CIELAB palette, colormap selector, background color |
| `alpha` | Global opacity slider + per-series opacity |
| `axes` | Title, x/y axis labels, x/y limits — supports multi-axis figures |
| `legend` | Location dropdown, legend entry names, bbox position |
| `grid_spines` | Grid on/off, spine style (box / left-bottom / none) |
| `palette_suggestions` | Colorblind-safe palette recommendations filtered by use case and background |


## Palette Utilities

mplstudio ships a curated palette library and color science tools you can use independently of the GUI: `get_palette`, `smart_palette`, `recommend`, `palette_names`, and `delta_e`. See [`examples/demo.ipynb`](examples/demo.ipynb) for usage examples.

### Available Palettes

Palettes for categorical, and continuous variables (sequential and diverging color maps).

Following table shows palettes for **categorical** values. For **continuous** variables, mplstudio uses matplotlib's built-in colormaps. See the [matplotlib colormap reference](https://matplotlib.org/stable/gallery/color/colormap_reference.html) for the full list.

| Palette | Colors | Tags |
|---------|--------|------|
| Okabe-Ito | 8 | colorblind-safe |
| Paul Tol Bright | 7 | colorblind-safe |
| Paul Tol Vibrant | 7 | colorblind-safe |
| Paul Tol Muted | 10 | colorblind-safe |
| IBM Colorblind Safe | 6 | colorblind-safe |
| ColorBrewer Set1 | 9 | categorical |
| ColorBrewer Set2 | 8 | categorical |
| ColorBrewer Dark2 | 8 | categorical |
| ColorBrewer Paired | 12 | categorical |
| Tableau 10 | 10 | categorical |
| Matplotlib tab10 | 10 | categorical |
| Nord | 6 | dark background |
| Catppuccin Latte | 6 | light background |
| Dracula | 6 | dark background |
| Tokyo Night | 6 | dark background |
| Pastel | 6 | light background |
| High Contrast | 5 | light background |


## Requirements

- Python ≥ 3.9
- matplotlib ≥ 3.5
- ipywidgets ≥ 8.0
- ipykernel ≥ 6.0
- Jupyter Notebook or JupyterLab


## License

[MIT](LICENSE) © 2026 Seo-Yoon Moon
