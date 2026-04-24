"""Curated color palettes and recommendation helpers."""

from __future__ import annotations

# Each palette: {name, colors, tags, description}
PALETTES: list[dict] = [
    {
        "name": "Okabe-Ito",
        "colors": ["#E69F00", "#56B4E9", "#009E73", "#F0E442", "#0072B2", "#D55E00", "#CC79A7", "#000000"],
        "tags": ["colorblind-safe", "categorical"],
        "description": "Colorblind-friendly palette by Okabe & Ito (2008).",
    },
    {
        "name": "ColorBrewer Set2",
        "colors": ["#66C2A5", "#FC8D62", "#8DA0CB", "#E78AC3", "#A6D854", "#FFD92F", "#E5C494", "#B3B3B3"],
        "tags": ["colorblind-safe", "categorical", "print-safe"],
        "description": "Qualitative palette suitable for categorical data.",
    },
    {
        "name": "Tableau 10",
        "colors": ["#4E79A7", "#F28E2B", "#E15759", "#76B7B2", "#59A14F", "#EDC948", "#B07AA1", "#FF9DA7", "#9C755F", "#BAB0AC"],
        "tags": ["categorical"],
        "description": "Default Tableau palette, high contrast.",
    },
    {
        "name": "Viridis (5 steps)",
        "colors": ["#440154", "#3B528B", "#21908C", "#5DC963", "#FDE725"],
        "tags": ["sequential", "colorblind-safe", "perceptually-uniform"],
        "description": "5-step sample of the perceptually uniform Viridis colormap.",
    },
    {
        "name": "Coolwarm (diverging)",
        "colors": ["#3B4CC0", "#7B9FF9", "#DDDDDD", "#F4987A", "#B40426"],
        "tags": ["diverging"],
        "description": "5-step diverging palette for data centered around zero.",
    },
    {
        "name": "Pastel",
        "colors": ["#AEC6CF", "#FFD1DC", "#B5EAD7", "#FFDAC1", "#C7CEEA", "#FF9AA2"],
        "tags": ["categorical", "light-background"],
        "description": "Soft pastel tones, good for presentations.",
    },
    {
        "name": "High Contrast",
        "colors": ["#000000", "#FFFFFF", "#E69F00", "#56B4E9", "#009E73", "#D55E00"],
        "tags": ["colorblind-safe", "high-contrast"],
        "description": "Maximum contrast for accessibility.",
    },
    {
        "name": "Nord",
        "colors": ["#BF616A", "#D08770", "#EBCB8B", "#A3BE8C", "#88C0D0", "#81A1C1", "#5E81AC", "#B48EAD"],
        "tags": ["categorical", "muted", "dark-background"],
        "description": "Arctic, north-bluish accent colors from the Nord theme.",
    },
    {
        "name": "Catppuccin Latte",
        "colors": ["#D20F39", "#FE640B", "#DF8E1D", "#40A02B", "#04A5E5", "#8839EF", "#EA76CB", "#E64553"],
        "tags": ["categorical", "pastel", "light-background"],
        "description": "Warm pastel tones from the Catppuccin Latte theme.",
    },
    {
        "name": "Dracula",
        "colors": ["#FF5555", "#FFB86C", "#F1FA8C", "#50FA7B", "#8BE9FD", "#BD93F9", "#FF79C6", "#6272A4"],
        "tags": ["categorical", "dark-background", "vibrant"],
        "description": "Vivid accent colors from the Dracula dark theme.",
    },
    {
        "name": "Tokyo Night",
        "colors": ["#F7768E", "#FF9E64", "#E0AF68", "#9ECE6A", "#73DACA", "#7DCFFF", "#7AA2F7", "#BB9AF7"],
        "tags": ["categorical", "dark-background", "vibrant"],
        "description": "Neon-tinged accents from the Tokyo Night editor theme.",
    },
]


def get_palette(name: str) -> list[str]:
    for p in PALETTES:
        if p["name"] == name:
            return p["colors"]
    raise KeyError(f"Palette '{name}' not found.")


def recommend(n_colors: int, *, colorblind_safe: bool = False) -> list[dict]:
    """Return palettes with at least n_colors that match optional filters."""
    results = [p for p in PALETTES if len(p["colors"]) >= n_colors]
    if colorblind_safe:
        results = [p for p in results if "colorblind-safe" in p["tags"]]
    return results


def palette_names() -> list[str]:
    return [p["name"] for p in PALETTES]
