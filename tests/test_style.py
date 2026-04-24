import matplotlib
matplotlib.use("Agg")  # headless backend for CI
import matplotlib.pyplot as plt
import pytest

import mplstudio
from mplstudio import style as S
from mplstudio.palettes import get_palette, recommend


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


def test_studio_import():
    assert callable(mplstudio.studio)
