import matplotlib
matplotlib.use("Agg")  # headless backend for CI
import matplotlib.pyplot as plt
import pytest

import mplstudio
from mplstudio import style as S
from mplstudio.palettes import get_palette, recommend, palette_names


@pytest.fixture
def fig():
    f, ax = plt.subplots()
    ax.plot([1, 2, 3], label="line")
    ax.legend()
    yield f
    plt.close(f)


def test_set_figure_size(fig):
    S.set_figure_size(fig, 10, 5)
    assert fig.get_size_inches() == pytest.approx([10, 5])


def test_set_font_size(fig):
    S.set_font_size(fig, 18)
    ax = fig.axes[0]
    assert ax.xaxis.label.get_fontsize() == 18


def test_set_legend_position(fig):
    S.set_legend_position(fig, "upper left")
    legend = fig.axes[0].get_legend()
    assert legend is not None


def test_set_line_colors(fig):
    S.set_line_colors(fig, "Okabe-Ito")
    expected = get_palette("Okabe-Ito")[0]
    line_color = fig.axes[0].get_lines()[0].get_color()
    assert line_color.lower() == expected.lower()


def test_set_grid(fig):
    S.set_grid(fig, True)
    S.set_grid(fig, False)


def test_spine_styles(fig):
    for s in S.SPINE_STYLES:
        S.set_spine_style(fig, s)


def test_get_palette_unknown():
    with pytest.raises(KeyError):
        get_palette("DoesNotExist")


def test_recommend_colorblind():
    results = recommend(3, colorblind_safe=True)
    assert all("colorblind-safe" in p["tags"] for p in results)
    assert all(len(p["colors"]) >= 3 for p in results)


def test_recommend_use_case():
    results = recommend(3, use_case="categorical")
    assert all("categorical" in p["tags"] for p in results)


def test_recommend_background_light():
    results = recommend(3, background="light")
    assert all("dark-background" not in p["tags"] for p in results)


def test_recommend_top_k():
    results = recommend(3, top_k=2)
    assert len(results) <= 2


def test_recommend_ranked_by_distinctiveness():
    from mplstudio.palettes import _distinctiveness
    results = recommend(5)
    scores = [_distinctiveness(p["colors"], 5) for p in results]
    assert scores == sorted(scores, reverse=True)


def test_recommend_no_match_returns_empty():
    results = recommend(3, colorblind_safe=True, use_case="diverging")
    # diverging + colorblind-safe may or may not match; just ensure it's a list
    assert isinstance(results, list)


def test_palette_has_source():
    from mplstudio.palettes import PALETTES
    for p in PALETTES:
        assert "source" in p, f"Palette '{p['name']}' missing 'source' field"


def test_new_palettes_present():
    names = palette_names()
    for expected in ["Paul Tol Bright", "Paul Tol Vibrant", "Paul Tol Muted",
                     "IBM Colorblind Safe", "ColorBrewer Set1",
                     "ColorBrewer Dark2", "ColorBrewer Paired", "Matplotlib tab10"]:
        assert expected in names, f"Palette '{expected}' not found"


def test_legend_color_synced_after_palette_change(fig):
    import matplotlib.colors as mcolors
    S.set_line_colors(fig, "Okabe-Ito")
    expected = mcolors.to_hex(fig.axes[0].get_lines()[0].get_color())
    handle_color = mcolors.to_hex(
        fig.axes[0].get_legend().legend_handles[0].get_color()
    )
    assert handle_color.lower() == expected.lower()


def test_legend_color_synced_after_manual_change(fig):
    import matplotlib.colors as mcolors
    S.set_line_colors_manual(fig, ["#123456"])
    handle_color = mcolors.to_hex(
        fig.axes[0].get_legend().legend_handles[0].get_color()
    )
    assert handle_color.lower() == "#123456"


def test_set_line_colors_manual(fig):
    S.set_line_colors_manual(fig, ["#ff0000"])
    color = fig.axes[0].get_lines()[0].get_color()
    import matplotlib.colors as mcolors
    assert mcolors.to_hex(color).lower() == "#ff0000"


def test_get_line_colors(fig):
    S.set_line_colors(fig, "Okabe-Ito")
    colors = S.get_line_colors(fig)
    assert len(colors) == 1
    assert colors[0].startswith("#")


def test_get_line_labels(fig):
    labels = S.get_line_labels(fig)
    assert labels == ["line"]


def test_get_line_labels_fallback():
    f, ax = plt.subplots()
    ax.plot([1, 2])  # no label → internal label starting with "_"
    labels = S.get_line_labels(f)
    assert labels == []  # unlabelled artists are not in legend, so excluded
    plt.close(f)


@pytest.fixture
def scatter_fig():
    f, ax = plt.subplots()
    ax.scatter([1, 2, 3], [4, 5, 6], label="group A")
    ax.scatter([1, 2, 3], [1, 2, 3], label="group B")
    ax.legend()
    yield f
    plt.close(f)


def test_scatter_palette_change(scatter_fig):
    import matplotlib.colors as mcolors
    S.set_line_colors(scatter_fig, "Okabe-Ito")
    colors = S.get_line_colors(scatter_fig)
    assert len(colors) == 2
    assert colors[0].startswith("#")


def test_scatter_manual_colors(scatter_fig):
    import matplotlib.colors as mcolors
    S.set_line_colors_manual(scatter_fig, ["#aabbcc", "#112233"])
    colors = S.get_line_colors(scatter_fig)
    assert mcolors.to_hex(mcolors.to_rgb(colors[0])) == "#aabbcc"
    assert mcolors.to_hex(mcolors.to_rgb(colors[1])) == "#112233"


def test_scatter_labels(scatter_fig):
    labels = S.get_line_labels(scatter_fig)
    assert labels == ["group A", "group B"]


def test_scatter_legend_sync(scatter_fig):
    import matplotlib.colors as mcolors
    S.set_line_colors(scatter_fig, "Okabe-Ito")
    # legend handles should have been synced
    legend = scatter_fig.axes[0].get_legend()
    assert legend is not None


def test_studio_import():
    assert callable(mplstudio.studio)


def test_available_sections():
    sections = mplstudio.available_sections()
    assert isinstance(sections, list)
    assert "colors" in sections
    assert "alpha" in sections
    assert "axes" in sections
    assert sections == sorted(sections)


def test_set_series_alpha(fig):
    S.set_series_alpha(fig, [0.4])
    artist = fig.axes[0].get_lines()[0]
    assert artist.get_alpha() == pytest.approx(0.4)


def test_get_series_alpha(fig):
    alphas = S.get_series_alpha(fig)
    assert len(alphas) == 1
    assert alphas[0] == pytest.approx(1.0)


def test_set_series_alpha_updates_value(fig):
    S.set_series_alpha(fig, [0.25])
    alphas = S.get_series_alpha(fig)
    assert alphas[0] == pytest.approx(0.25)


def test_set_title(fig):
    S.set_title(fig, "My Title")
    assert fig.axes[0].get_title() == "My Title"


def test_set_xlabel(fig):
    S.set_xlabel(fig, "X axis")
    assert fig.axes[0].get_xlabel() == "X axis"


def test_set_ylabel(fig):
    S.set_ylabel(fig, "Y axis")
    assert fig.axes[0].get_ylabel() == "Y axis"


def test_set_xlim(fig):
    S.set_xlim(fig, 0.5, 2.5)
    lo, hi = fig.axes[0].get_xlim()
    assert lo == pytest.approx(0.5)
    assert hi == pytest.approx(2.5)


def test_set_xlim_ignored_when_inverted(fig):
    before = fig.axes[0].get_xlim()
    S.set_xlim(fig, 5.0, 1.0)  # vmin > vmax → no-op
    assert fig.axes[0].get_xlim() == before


def test_set_ylim(fig):
    S.set_ylim(fig, -2.0, 2.0)
    lo, hi = fig.axes[0].get_ylim()
    assert lo == pytest.approx(-2.0)
    assert hi == pytest.approx(2.0)


def test_set_legend_labels(fig):
    S.set_legend_labels(fig, ["renamed"])
    texts = [t.get_text() for t in fig.axes[0].get_legend().get_texts()]
    assert texts == ["renamed"]


def test_set_legend_bbox(fig):
    S.set_legend_bbox(fig, 0.8, 0.9)
    legend = fig.axes[0].get_legend()
    assert legend is not None  # smoke test — bbox_to_anchor set without error


# ── continuous colormap tests ─────────────────────────────────────────────────

@pytest.fixture
def heatmap_fig():
    import numpy as np
    f, ax = plt.subplots()
    data = np.arange(16).reshape(4, 4)
    ax.imshow(data, cmap="viridis")
    yield f
    plt.close(f)


@pytest.fixture
def pcolormesh_fig():
    import numpy as np
    f, ax = plt.subplots()
    x = np.linspace(0, 1, 5)
    y = np.linspace(0, 1, 5)
    X, Y = np.meshgrid(x, y)
    ax.pcolormesh(X, Y, X * Y, cmap="coolwarm")
    yield f
    plt.close(f)


def test_detect_categorical(fig):
    assert S.detect_plot_type(fig) == "categorical"


def test_detect_continuous_imshow(heatmap_fig):
    assert S.detect_plot_type(heatmap_fig) == "continuous"


def test_detect_continuous_pcolormesh(pcolormesh_fig):
    assert S.detect_plot_type(pcolormesh_fig) == "continuous"


def test_detect_mixed():
    import numpy as np
    f, ax = plt.subplots()
    ax.plot([1, 2, 3], label="series")
    ax.legend()
    ax.imshow(np.zeros((3, 3)), cmap="viridis", aspect="auto", extent=[0, 3, 0, 3])
    assert S.detect_plot_type(f) == "mixed"
    plt.close(f)


def test_get_colormap_imshow(heatmap_fig):
    cmap = S.get_colormap(heatmap_fig)
    assert cmap == "viridis"


def test_set_colormap_imshow(heatmap_fig):
    S.set_colormap(heatmap_fig, "plasma")
    assert S.get_colormap(heatmap_fig) == "plasma"


def test_set_colormap_pcolormesh(pcolormesh_fig):
    S.set_colormap(pcolormesh_fig, "inferno")
    assert S.get_colormap(pcolormesh_fig) == "inferno"


def test_get_colormap_returns_none_for_categorical(fig):
    assert S.get_colormap(fig) is None


def test_sequential_cmaps_list():
    from mplstudio.palettes import SEQUENTIAL_CMAPS
    assert "viridis" in SEQUENTIAL_CMAPS
    assert "plasma" in SEQUENTIAL_CMAPS
    assert len(SEQUENTIAL_CMAPS) >= 5


def test_diverging_cmaps_list():
    from mplstudio.palettes import DIVERGING_CMAPS
    assert "coolwarm" in DIVERGING_CMAPS
    assert len(DIVERGING_CMAPS) >= 3
