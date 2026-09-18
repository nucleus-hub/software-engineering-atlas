"""Shared visual style and drawing helpers for system-design figures."""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch  # noqa: E402

NAVY = "#0B3D91"
BLUE = "#1E6FEB"
SKY = "#5B9BFF"
MIST = "#C9DCFF"
PALE = "#EAF1FF"
INK = "#12213D"
GREY = "#7183A3"
LINE = "#D5DEEC"
RED = "#C0392B"
GREEN = "#1E8449"
AMBER = "#D68910"
WHITE = "#FFFFFF"
DPI = 200


def canvas(width: float = 14, height: float = 6) -> tuple[plt.Figure, plt.Axes]:
    """Return a clean drawing surface using percentage-like coordinates."""
    fig, ax = plt.subplots(figsize=(width, height), facecolor=WHITE)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")
    return fig, ax


def heading(ax: plt.Axes, title: str, subtitle: str = "") -> None:
    """Draw the standard navy title and optional italic subtitle."""
    ax.text(50, 96, title, ha="center", va="top", fontsize=19,
            fontweight="bold", color=NAVY)
    if subtitle:
        ax.text(50, 89, subtitle, ha="center", va="top", fontsize=10.5,
                color=INK, style="italic")


def box(
    ax: plt.Axes,
    x: float,
    y: float,
    width: float,
    height: float,
    title: str,
    subtitle: str = "",
    *,
    face: str = PALE,
    edge: str = BLUE,
    title_color: str = NAVY,
    radius: float = 1.4,
    linewidth: float = 1.8,
) -> None:
    """Draw a rounded concept box with a title and optional subtitle."""
    patch = FancyBboxPatch(
        (x, y), width, height,
        boxstyle=f"round,pad=0.5,rounding_size={radius}",
        facecolor=face, edgecolor=edge, linewidth=linewidth,
    )
    ax.add_patch(patch)
    cy = y + height / 2
    ax.text(x + width / 2, cy + (2.2 if subtitle else 0), title,
            ha="center", va="center", fontsize=10.5, fontweight="bold",
            color=title_color)
    if subtitle:
        ax.text(x + width / 2, cy - 3.1, subtitle,
                ha="center", va="center", fontsize=8.2, color=INK)


def arrow(
    ax: plt.Axes,
    start: tuple[float, float],
    end: tuple[float, float],
    *,
    color: str = BLUE,
    label: str = "",
    curve: float = 0,
    dashed: bool = False,
) -> None:
    """Draw a directional arrow with an optional readable label."""
    patch = FancyArrowPatch(
        start, end, arrowstyle="-|>", mutation_scale=14,
        linewidth=1.8, color=color,
        connectionstyle=f"arc3,rad={curve}",
        linestyle="--" if dashed else "-",
    )
    ax.add_patch(patch)
    if label:
        mx, my = (start[0] + end[0]) / 2, (start[1] + end[1]) / 2
        ax.text(mx, my + 3, label, ha="center", va="center", fontsize=8,
                color=color, bbox=dict(facecolor=WHITE, edgecolor="none", pad=1))
