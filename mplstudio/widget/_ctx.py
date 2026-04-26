"""Shared panel context passed to every section builder."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

from matplotlib.figure import Figure


@dataclass
class _PanelCtx:
    """All mutable state shared across section builders inside one studio() call.

    Mutable list pattern is preserved intentionally — Python closures can't
    rebind bare booleans/ints, so single-element lists act as mutable cells.
    """
    fig: Figure
    pid: str
    dark: bool
    refresh: Callable[[], None]
    ax_idx: list = field(default_factory=lambda: [0])   # [int]
    fb: list = field(default_factory=lambda: [False])   # font busy guard
    ab: list = field(default_factory=lambda: [False])   # alpha busy guard
