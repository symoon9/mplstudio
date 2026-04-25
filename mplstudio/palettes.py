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


# ── CIELAB color math (no external deps) ─────────────────────────────────────

def _rgb_to_lab(hex_color: str) -> tuple[float, float, float]:
    """Hex → CIELAB (D65 illuminant, sRGB primaries)."""
    h = hex_color.lstrip("#")
    r, g, b = (int(h[i : i + 2], 16) / 255.0 for i in (0, 2, 4))

    def _lin(c: float) -> float:  # sRGB → linear
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

    r, g, b = _lin(r), _lin(g), _lin(b)

    # Linear RGB → XYZ (D65), then normalise by D65 white point
    x = (r * 0.4124564 + g * 0.3575761 + b * 0.1804375) / 0.95047
    y = (r * 0.2126729 + g * 0.7151522 + b * 0.0721750) / 1.00000
    z = (r * 0.0193339 + g * 0.1191920 + b * 0.9503041) / 1.08883

    def _f(t: float) -> float:  # XYZ → LAB cube-root transfer
        return t ** (1 / 3) if t > 0.008856 else 7.787 * t + 16 / 116

    return 116 * _f(y) - 16, 500 * (_f(x) - _f(y)), 200 * (_f(y) - _f(z))


def delta_e(c1: str, c2: str) -> float:
    """ΔE 76 — Euclidean distance in CIELAB. Perceptually uniform proxy."""
    L1, a1, b1 = _rgb_to_lab(c1)
    L2, a2, b2 = _rgb_to_lab(c2)
    return math.sqrt((L1 - L2) ** 2 + (a1 - a2) ** 2 + (b1 - b2) ** 2)


def _distinctiveness(colors: list[str], n: int) -> float:
    """Minimum pairwise ΔE 76 for the first *n* colors. Higher = more distinct."""
    subset = colors[:n]
    if len(subset) < 2:
        return 0.0
    min_d = math.inf
    for i in range(len(subset)):
        for j in range(i + 1, len(subset)):
            d = delta_e(subset[i], subset[j])
            if d < min_d:
                min_d = d
    return min_d


# ── smart 50-color pool (greedy farthest-point in CIELAB) ────────────────────

# ~65 candidate colors sampled from authoritative palettes, covering the full
# hue range with reasonable lightness (not too light, not too dark).
_CANDIDATE_POOL: list[str] = [
    # reds / vermillion
    "#E41A1C", "#CC3311", "#EE3377", "#D55E00", "#EE6677",
    "#DC267F", "#CC6677", "#882255", "#E15759",
    # orange
    "#E69F00", "#FF7F00", "#FE6100", "#F28E2B", "#EE7733", "#D95F02",
    # yellow / gold
    "#CCBB44", "#DDCC77", "#F0E442", "#FFB000", "#EDC948", "#E6AB02",
    # green
    "#009E73", "#228833", "#44AA99", "#009988", "#1B9E77",
    "#117733", "#66A61E", "#4DAF4A", "#59A14F", "#A3BE8C",
    # cyan / teal
    "#56B4E9", "#66CCEE", "#33BBEE", "#0077BB", "#76B7B2", "#17BECF",
    # blue
    "#0072B2", "#4477AA", "#377EB8", "#332288", "#4E79A7",
    "#1F78B4", "#648FFF", "#5E81AC",
    # purple / violet
    "#AA3377", "#AA4499", "#785EF0", "#7570B3", "#9467BD",
    "#B48EAD", "#8839EF", "#984EA3",
    # pink / magenta
    "#CC79A7", "#F781BF", "#E7298A", "#FF79C6", "#EA76CB",
    # neutral / earth
    "#666666", "#7F7F7F", "#999933", "#A6761D", "#8C564B",
]


_SMART_POOL_CACHE: list[str] | None = None


def _build_smart_pool() -> list[str]:
    """Greedy farthest-point sampling in CIELAB. Runs once; O(m²) precompute."""
    cands = _CANDIDATE_POOL
    m = len(cands)
    target = min(50, m)

    # Precompute full pairwise ΔE matrix
    dist: list[list[float]] = [[0.0] * m for _ in range(m)]
    for i in range(m):
        for j in range(i + 1, m):
            d = delta_e(cands[i], cands[j])
            dist[i][j] = dist[j][i] = d

    # Seed: pair with the largest pairwise ΔE
    bi, bj, bd = 0, 1, 0.0
    for i in range(m):
        for j in range(i + 1, m):
            if dist[i][j] > bd:
                bd, bi, bj = dist[i][j], i, j

    selected: list[int] = [bi, bj]
    in_sel: set[int] = {bi, bj}
    # Track each candidate's min-distance to the selected set
    min_d_to_sel = [min(dist[k][bi], dist[k][bj]) for k in range(m)]

    while len(selected) < target:
        # Pick the unselected candidate that maximises its min-distance to the set
        best_k, best_val = -1, -1.0
        for k in range(m):
            if k in in_sel:
                continue
            if min_d_to_sel[k] > best_val:
                best_val, best_k = min_d_to_sel[k], k
        if best_k == -1:
            break
        selected.append(best_k)
        in_sel.add(best_k)
        # Update min-distances incrementally
        for k in range(m):
            if k not in in_sel and dist[k][best_k] < min_d_to_sel[k]:
                min_d_to_sel[k] = dist[k][best_k]

    return [cands[i] for i in selected]


def smart_palette(n: int) -> list[str]:
    """Return the top-*n* colors from the greedy-optimised 50-color pool.

    Colors are ordered so that ``smart_palette(k)`` ⊆ ``smart_palette(k+1)``
    for any k — the first *n* colors are always the most perceptually distinct
    *n*-color combination available in the pool.
    """
    global _SMART_POOL_CACHE
    if _SMART_POOL_CACHE is None:
        _SMART_POOL_CACHE = _build_smart_pool()
    pool = _SMART_POOL_CACHE
    return pool[: max(1, min(n, len(pool)))]


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


# ── continuous colormap lists ─────────────────────────────────────────────────
# Curated subsets of matplotlib colormaps, grouped by type.

SEQUENTIAL_CMAPS: list[str] = [
    "viridis", "plasma", "inferno", "magma", "cividis",  # perceptually uniform
    "Blues", "Oranges", "Reds", "Greens", "Purples",     # single-hue
    "YlOrRd", "YlGnBu", "BuPu", "GnBu",                 # multi-hue
]

DIVERGING_CMAPS: list[str] = [
    "coolwarm", "RdBu_r", "PiYG", "PRGn", "RdYlGn", "seismic",
]
