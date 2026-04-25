"""Curated color palettes and smart recommendation helpers."""

from __future__ import annotations

import math

# ── palette registry ──────────────────────────────────────────────────────────
# Tags: categorical | sequential | diverging | colorblind-safe | print-safe |
#       light-background | dark-background | high-contrast | muted | vibrant |
#       pastel | perceptually-uniform

PALETTES: list[dict] = [
    # ── Colorblind-safe / scientific ─────────────────────────────────────────
    {
        "name": "Okabe-Ito",
        "colors": ["#E69F00", "#56B4E9", "#009E73", "#F0E442",
                   "#0072B2", "#D55E00", "#CC79A7", "#000000"],
        "tags": ["colorblind-safe", "categorical", "print-safe"],
        "description": "8-color colorblind-safe palette. Recommended by Nature Methods and IEEE.",
        "source": "Okabe & Ito (2008), Nature Methods",
    },
    {
        "name": "Paul Tol Bright",
        "colors": ["#4477AA", "#EE6677", "#228833", "#CCBB44", "#66CCEE", "#AA3377", "#BBBBBB"],
        "tags": ["colorblind-safe", "categorical"],
        "description": "7-color bright qualitative palette from SRON. Safe for all common color-vision deficiencies.",
        "source": "Paul Tol / SRON (personal.sron.nl/~pault)",
    },
    {
        "name": "Paul Tol Vibrant",
        "colors": ["#EE7733", "#0077BB", "#33BBEE", "#EE3377", "#CC3311", "#009988", "#BBBBBB"],
        "tags": ["colorblind-safe", "categorical", "vibrant"],
        "description": "7-color vibrant qualitative palette from SRON. High contrast, colorblind-safe.",
        "source": "Paul Tol / SRON (personal.sron.nl/~pault)",
    },
    {
        "name": "Paul Tol Muted",
        "colors": ["#332288", "#88CCEE", "#44AA99", "#117733",
                   "#999933", "#DDCC77", "#CC6677", "#882255", "#AA4499"],
        "tags": ["colorblind-safe", "categorical", "muted"],
        "description": "9-color muted qualitative palette from SRON. Good for dense figures.",
        "source": "Paul Tol / SRON (personal.sron.nl/~pault)",
    },
    {
        "name": "IBM Colorblind Safe",
        "colors": ["#648FFF", "#785EF0", "#DC267F", "#FE6100", "#FFB000"],
        "tags": ["colorblind-safe", "categorical", "high-contrast"],
        "description": "5-color accessible palette from IBM Design Language / Carbon Design System.",
        "source": "IBM Design Language (carbondesignsystem.com)",
    },
    # ── ColorBrewer qualitative ───────────────────────────────────────────────
    {
        "name": "ColorBrewer Set1",
        "colors": ["#E41A1C", "#377EB8", "#4DAF4A", "#984EA3",
                   "#FF7F00", "#FFFF33", "#A65628", "#F781BF", "#999999"],
        "tags": ["categorical", "high-contrast"],
        "description": "9-color high-contrast qualitative palette. Strong hue separation.",
        "source": "ColorBrewer 2.0 (colorbrewer2.org)",
    },
    {
        "name": "ColorBrewer Set2",
        "colors": ["#66C2A5", "#FC8D62", "#8DA0CB", "#E78AC3",
                   "#A6D854", "#FFD92F", "#E5C494", "#B3B3B3"],
        "tags": ["colorblind-safe", "categorical", "print-safe"],
        "description": "8-color soft qualitative palette. Print-safe and colorblind-friendly.",
        "source": "ColorBrewer 2.0 (colorbrewer2.org)",
    },
    {
        "name": "ColorBrewer Dark2",
        "colors": ["#1B9E77", "#D95F02", "#7570B3", "#E7298A",
                   "#66A61E", "#E6AB02", "#A6761D", "#666666"],
        "tags": ["colorblind-safe", "categorical", "print-safe", "muted"],
        "description": "8-color darker qualitative palette. Earthy tones, print-safe.",
        "source": "ColorBrewer 2.0 (colorbrewer2.org)",
    },
    {
        "name": "ColorBrewer Paired",
        "colors": ["#A6CEE3", "#1F78B4", "#B2DF8A", "#33A02C",
                   "#FB9A99", "#E31A1C", "#FDBF6F", "#FF7F00",
                   "#CAB2D6", "#6A3D9A", "#FFFF99", "#B15928"],
        "tags": ["categorical", "print-safe"],
        "description": "12-color paired palette (light+dark pairs). Great for 6 paired series.",
        "source": "ColorBrewer 2.0 (colorbrewer2.org)",
    },
    # ── Popular software defaults ─────────────────────────────────────────────
    {
        "name": "Tableau 10",
        "colors": ["#4E79A7", "#F28E2B", "#E15759", "#76B7B2", "#59A14F",
                   "#EDC948", "#B07AA1", "#FF9DA7", "#9C755F", "#BAB0AC"],
        "tags": ["categorical"],
        "description": "10-color Tableau default. Designed by Maureen Stone for high perceptual distinctiveness.",
        "source": "Tableau (Maureen Stone)",
    },
    {
        "name": "Matplotlib tab10",
        "colors": ["#1F77B4", "#FF7F0E", "#2CA02C", "#D62728", "#9467BD",
                   "#8C564B", "#E377C2", "#7F7F7F", "#BCBD22", "#17BECF"],
        "tags": ["categorical"],
        "description": "10-color matplotlib default (also D3 Category10 / Vega-Lite default).",
        "source": "Matplotlib / D3.js",
    },
    # ── Sequential ────────────────────────────────────────────────────────────
    {
        "name": "Viridis (5 steps)",
        "colors": ["#440154", "#3B528B", "#21908C", "#5DC963", "#FDE725"],
        "tags": ["sequential", "colorblind-safe", "perceptually-uniform"],
        "description": "5-step sample of the perceptually uniform Viridis colormap.",
        "source": "Matplotlib",
    },
    # ── Diverging ─────────────────────────────────────────────────────────────
    {
        "name": "Coolwarm (diverging)",
        "colors": ["#3B4CC0", "#7B9FF9", "#DDDDDD", "#F4987A", "#B40426"],
        "tags": ["diverging"],
        "description": "5-step diverging palette for data centered around zero.",
        "source": "Matplotlib",
    },
    # ── Presentation / light background ──────────────────────────────────────
    {
        "name": "Pastel",
        "colors": ["#AEC6CF", "#FFD1DC", "#B5EAD7", "#FFDAC1", "#C7CEEA", "#FF9AA2"],
        "tags": ["categorical", "light-background", "pastel"],
        "description": "Soft pastel tones. Good for slides and posters.",
        "source": "mplstudio curated",
    },
    {
        "name": "High Contrast",
        "colors": ["#000000", "#E69F00", "#56B4E9", "#009E73", "#D55E00", "#CC79A7"],
        "tags": ["colorblind-safe", "high-contrast", "categorical"],
        "description": "Maximum perceptual contrast. Subset of Okabe-Ito with black first.",
        "source": "mplstudio curated",
    },
    # ── Editor / dark-background themes ──────────────────────────────────────
    {
        "name": "Nord",
        "colors": ["#BF616A", "#D08770", "#EBCB8B", "#A3BE8C",
                   "#88C0D0", "#81A1C1", "#5E81AC", "#B48EAD"],
        "tags": ["categorical", "muted", "dark-background"],
        "description": "Arctic-inspired muted accent colors from the Nord editor theme.",
        "source": "Nord theme (nordtheme.com)",
    },
    {
        "name": "Catppuccin Latte",
        "colors": ["#D20F39", "#FE640B", "#DF8E1D", "#40A02B",
                   "#04A5E5", "#8839EF", "#EA76CB", "#E64553"],
        "tags": ["categorical", "pastel", "light-background"],
        "description": "Warm pastel tones from the Catppuccin Latte light theme.",
        "source": "Catppuccin (github.com/catppuccin)",
    },
    {
        "name": "Dracula",
        "colors": ["#FF5555", "#FFB86C", "#F1FA8C", "#50FA7B",
                   "#8BE9FD", "#BD93F9", "#FF79C6", "#6272A4"],
        "tags": ["categorical", "dark-background", "vibrant"],
        "description": "Vivid accent colors from the Dracula dark editor theme.",
        "source": "Dracula theme (draculatheme.com)",
    },
    {
        "name": "Tokyo Night",
        "colors": ["#F7768E", "#FF9E64", "#E0AF68", "#9ECE6A",
                   "#73DACA", "#7DCFFF", "#7AA2F7", "#BB9AF7"],
        "tags": ["categorical", "dark-background", "vibrant"],
        "description": "Neon-tinged accent colors from the Tokyo Night editor theme.",
        "source": "Tokyo Night theme",
    },
]


# ── perceptual scoring ────────────────────────────────────────────────────────

def _hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    h = hex_color.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def _distinctiveness(colors: list[str], n: int) -> float:
    """Minimum pairwise Euclidean distance in RGB space for the first *n* colors.

    Higher = more perceptually distinct. Used to rank palette recommendations.
    """
    subset = [_hex_to_rgb(c) for c in colors[:n]]
    if len(subset) < 2:
        return 0.0
    min_dist = math.inf
    for i in range(len(subset)):
        for j in range(i + 1, len(subset)):
            d = math.sqrt(sum((a - b) ** 2 for a, b in zip(subset[i], subset[j])))
            if d < min_dist:
                min_dist = d
    return min_dist


# ── public API ────────────────────────────────────────────────────────────────

def get_palette(name: str) -> list[str]:
    """Return the hex color list for *name*. Raises ``KeyError`` if not found."""
    for p in PALETTES:
        if p["name"] == name:
            return p["colors"]
    raise KeyError(f"Palette '{name}' not found.")


def recommend(
    n_colors: int,
    *,
    colorblind_safe: bool = False,
    use_case: str | None = None,
    background: str | None = None,
    top_k: int | None = None,
) -> list[dict]:
    """Return palettes ranked by perceptual distinctiveness.

    Parameters
    ----------
    n_colors:
        Only palettes with at least this many colors are returned.
    colorblind_safe:
        If ``True``, restrict to palettes tagged ``"colorblind-safe"``.
    use_case:
        ``"categorical"``, ``"sequential"``, or ``"diverging"``.
        Filters to palettes that carry the matching tag.
    background:
        ``"light"`` or ``"dark"``. Excludes palettes designed for the
        opposite background when alternatives exist.
    top_k:
        Return at most this many results. ``None`` returns all matches.
    """
    results = [p for p in PALETTES if len(p["colors"]) >= n_colors]

    if colorblind_safe:
        results = [p for p in results if "colorblind-safe" in p["tags"]]
    if use_case:
        results = [p for p in results if use_case in p["tags"]]
    if background == "light":
        filtered = [p for p in results if "dark-background" not in p["tags"]]
        if filtered:
            results = filtered
    elif background == "dark":
        filtered = [p for p in results if "light-background" not in p["tags"]]
        if filtered:
            results = filtered

    results.sort(key=lambda p: _distinctiveness(p["colors"], n_colors), reverse=True)

    if top_k is not None:
        results = results[:top_k]
    return results


def palette_names() -> list[str]:
    """Return all palette names in registry order."""
    return [p["name"] for p in PALETTES]
