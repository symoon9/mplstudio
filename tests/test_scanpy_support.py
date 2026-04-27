"""Tests for scanpy UMAP support — categorical and continuous plots."""

import matplotlib
matplotlib.use("Agg")
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import pytest

from mplstudio import style as S
from mplstudio.style._artists import _continuous_artists, _labeled_artists


# ── fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def categorical_umap_fig():
    """Mimics scanpy pl.umap with a categorical obs column.

    Each category is a separate PathCollection with no ax.legend() call
    (scanpy draws its own legend via AnchoredOffsetbox).
    """
    f, ax = plt.subplots()
    rng = np.random.default_rng(0)
    categories = ["T cell", "B cell", "NK cell"]
    colors = ["#e41a1c", "#377eb8", "#4daf4a"]
    for cat, col in zip(categories, colors):
        xy = rng.standard_normal((30, 2))
        sc = ax.scatter(xy[:, 0], xy[:, 1], c=col, label=cat, s=10)
    # No ax.legend() — scanpy draws its own legend externally
    yield f
    plt.close(f)


@pytest.fixture
def continuous_umap_fig():
    """Mimics scanpy pl.umap with a continuous obs column (e.g. gene expression).

    Single PathCollection with set_array() for per-point values and
    label="" (default matplotlib label for unlabeled artists).
    """
    f, ax = plt.subplots()
    rng = np.random.default_rng(1)
    xy = rng.standard_normal((50, 2))
    values = rng.random(50)
    sc = ax.scatter(xy[:, 0], xy[:, 1], c=values, cmap="viridis", s=10)
    # sc.get_label() == "" by default; set_array() already called by scatter
    yield f
    plt.close(f)


@pytest.fixture
def categorical_with_legend_fig():
    """Standard plot: PathCollections with an explicit ax.legend()."""
    f, ax = plt.subplots()
    rng = np.random.default_rng(2)
    categories = ["Alpha", "Beta"]
    colors = ["#ff7f00", "#984ea3"]
    for cat, col in zip(categories, colors):
        xy = rng.standard_normal((20, 2))
        ax.scatter(xy[:, 0], xy[:, 1], c=col, label=cat)
    ax.legend()
    yield f
    plt.close(f)


# ── _continuous_artists ───────────────────────────────────────────────────────

def test_continuous_artists_detects_unlabeled_scatter(continuous_umap_fig):
    artists = list(_continuous_artists(continuous_umap_fig))
    assert len(artists) == 1


def test_continuous_artists_ignores_categorical_scatter(categorical_umap_fig):
    artists = list(_continuous_artists(categorical_umap_fig))
    assert len(artists) == 0


def test_continuous_artists_nolegend_label(continuous_umap_fig):
    ax = continuous_umap_fig.axes[0]
    ax.collections[0].set_label("_nolegend_")
    artists = list(_continuous_artists(continuous_umap_fig))
    assert len(artists) == 1


# ── _labeled_artists ──────────────────────────────────────────────────────────

def test_labeled_artists_no_legend_fallback(categorical_umap_fig):
    ax = categorical_umap_fig.axes[0]
    result = list(_labeled_artists(ax))
    labels = [lbl for _, lbl in result]
    assert labels == ["T cell", "B cell", "NK cell"]


def test_labeled_artists_with_legend(categorical_with_legend_fig):
    ax = categorical_with_legend_fig.axes[0]
    result = list(_labeled_artists(ax))
    labels = [lbl for _, lbl in result]
    assert set(labels) == {"Alpha", "Beta"}


def test_labeled_artists_empty_on_continuous(continuous_umap_fig):
    ax = continuous_umap_fig.axes[0]
    result = list(_labeled_artists(ax))
    assert result == []


# ── detect_plot_type / get_line_labels / get_line_colors ─────────────────────

def test_detect_categorical_umap(categorical_umap_fig):
    assert S.detect_plot_type(categorical_umap_fig) == "categorical"


def test_detect_continuous_umap(continuous_umap_fig):
    assert S.detect_plot_type(continuous_umap_fig) == "continuous"


def test_get_line_labels_categorical(categorical_umap_fig):
    labels = S.get_line_labels(categorical_umap_fig)
    assert labels == ["T cell", "B cell", "NK cell"]


def test_get_line_colors_categorical(categorical_umap_fig):
    colors = S.get_line_colors(categorical_umap_fig)
    assert len(colors) == 3
    for c in colors:
        assert c.startswith("#")


def test_get_line_labels_continuous(continuous_umap_fig):
    assert S.get_line_labels(continuous_umap_fig) == []


# ── set_line_colors_manual ────────────────────────────────────────────────────

def test_set_line_colors_manual_categorical(categorical_umap_fig):
    new_colors = ["#111111", "#222222", "#333333"]
    S.set_line_colors_manual(categorical_umap_fig, new_colors)
    result = S.get_line_colors(categorical_umap_fig)
    assert result == new_colors


# ── palette= kwarg on studio() ────────────────────────────────────────────────

def test_studio_palette_kwarg(categorical_umap_fig):
    """studio() must accept palette= without raising."""
    import ipywidgets as widgets
    from unittest.mock import patch
    from IPython.display import display as ipy_display

    palette = {"T cell": "#e41a1c", "B cell": "#377eb8", "NK cell": "#4daf4a"}
    with patch("IPython.display.display"):
        import mplstudio
        mplstudio.studio(categorical_umap_fig, palette=palette)
