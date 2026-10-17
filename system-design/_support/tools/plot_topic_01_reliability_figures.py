"""Render the reliability charts for topic 01: availability, latency, timeouts, retries.

The framework, estimation, and worked-example diagrams live in
``plot_topic_01_figures.py``; both scripts write to ``basics/assets/topic-01``.

Run from the system-design directory:

    uv run --with matplotlib \
      --index-url https://pypi.ci.artifacts.walmart.com/artifactory/api/pypi/external-pypi/simple \
      --allow-insecure-host pypi.ci.artifacts.walmart.com \
      python _support/tools/plot_topic_01_reliability_figures.py

Pass figure names to render only selected assets.
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle

from figure_style import (
    AMBER,
    AMBER_FACE,
    BLUE,
    DPI,
    GREEN,
    GREEN_FACE,
    GREY,
    INK,
    LINE,
    NAVY,
    PALE,
    RED,
    RED_FACE,
    WHITE,
    arrow,
    box,
    canvas,
    heading,
)

ASSETS = Path(__file__).resolve().parent.parent.parent / "basics" / "assets" / "topic-01"


def save(name: str, fig: plt.Figure) -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    output = ASSETS / f"{name}.png"
    fig.savefig(output, dpi=DPI, bbox_inches="tight", facecolor=WHITE)
    plt.close(fig)
    print(f"wrote basics/assets/topic-01/{output.name}")


def style_chart(ax: plt.Axes, title: str, xlabel: str, ylabel: str) -> None:
    """Apply the house style to a real (data) chart."""
    ax.set_title(title, fontsize=15, fontweight="bold", color=NAVY, pad=14)
    ax.set_xlabel(xlabel, color=INK)
    ax.set_ylabel(ylabel, color=INK)
    ax.tick_params(colors=INK)
    ax.grid(color=LINE, linewidth=0.8)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(GREY)


def availability_composition() -> plt.Figure:
    fig, ax = canvas(14, 6.4)
    heading(ax, "Availability Composes: Chains Multiply, Redundancy Complements",
            "Your SLO is capped by your hard dependencies")
    ax.text(25, 78, "SERIAL - every hop must work", ha="center", fontsize=9,
            fontweight="bold", color=RED)
    for i, name in enumerate(["API", "Auth", "DB"]):
        x = 3 + i * 16
        box(ax, x, 52, 11, 14, name, "99.9%")
        if i < 2:
            arrow(ax, (x + 11.5, 59), (x + 15.5, 59), color=GREY)
    box(ax, 10, 22, 30, 14, "0.999^3 = 99.7%", "~26 h/year down, not 8.8 h",
        face=RED_FACE, edge=RED, title_color=RED)
    arrow(ax, (25, 51), (25, 36.5), color=RED)
    ax.plot([50, 50], [15, 82], color=LINE, linewidth=2)
    ax.text(75, 78, "PARALLEL - any replica works", ha="center", fontsize=9,
            fontweight="bold", color=GREEN)
    box(ax, 57, 60, 13, 10, "Replica A", "99%")
    box(ax, 57, 44, 13, 10, "Replica B", "99%")
    arrow(ax, (70.5, 65), (79.5, 57), color=GREY)
    arrow(ax, (70.5, 49), (79.5, 55), color=GREY)
    box(ax, 80, 50, 15, 12, "1 - 0.01^2", "= 99.99%", face=GREEN_FACE, edge=GREEN,
        title_color=GREEN)
    ax.text(76, 26, "...only if failures are independent.\nSame AZ, same config push, same "
            "bad deploy\n= shared fate, and the math collapses.", ha="center", va="center",
            fontsize=8.8, color=AMBER, fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.6", facecolor=AMBER_FACE, edgecolor=AMBER))
    return fig


def latency_percentiles() -> plt.Figure:
    rng = np.random.default_rng(7)
    samples = np.concatenate([rng.lognormal(3.0, 0.35, 9_500),
                              rng.lognormal(5.6, 0.45, 500)])  # 5% slow path
    fig, ax = plt.subplots(figsize=(13, 5.2), facecolor=WHITE)
    ax.hist(samples, bins=np.linspace(0, 700, 141), color=BLUE, alpha=0.8)
    marks = [("p50", np.percentile(samples, 50), GREEN),
             ("mean", samples.mean(), GREY),
             ("p95", np.percentile(samples, 95), AMBER),
             ("p99", np.percentile(samples, 99), RED)]
    # Log scale: on a linear axis the tail (the whole point) is invisible.
    ax.set_yscale("log")
    frac = ax.get_xaxis_transform()  # x in data units, y in axes fraction
    label_x = [60, 60, 110, 430]
    for i, (label, value, color) in enumerate(marks):
        ax.axvline(value, color=color, linewidth=2, linestyle="--")
        ax.text(label_x[i], 0.93 - i * 0.09, f"{label} ~ {value:.0f} ms",
                transform=frac, color=color, fontweight="bold", fontsize=10,
                bbox=dict(facecolor=WHITE, edgecolor="none", pad=1))
    ax.annotate("the long tail: 5% of requests,\n100% of the support tickets",
                xy=(300, 0.25), xycoords=frac, xytext=(470, 0.55), textcoords=frac,
                color=RED, fontsize=10, arrowprops=dict(arrowstyle="-|>", color=RED))
    style_chart(ax, "Averages Describe a System Nobody Experiences",
                "request latency (ms)", "requests (log scale)")
    return fig


def tail_amplification() -> plt.Figure:
    n = np.arange(1, 101)
    fig, ax = plt.subplots(figsize=(13, 5.2), facecolor=WHITE)
    ax.plot(n, 100 * 0.99 ** n, color=RED, linewidth=3, label="each dependency p99 slow (0.99^N)")
    ax.plot(n, 100 * 0.999 ** n, color=GREEN, linewidth=3,
            label="each dependency p99.9 slow (0.999^N)")
    for x in (10, 100):
        y = 100 * 0.99 ** x
        ax.scatter([x], [y], color=RED, zorder=3, s=50)
        offset = (-22, -12) if x == 100 else (-8, -18)
        ax.annotate(f"N={x}: {y:.0f}% fast", xy=(x, y), xytext=(x + offset[0], y + offset[1]),
                    color=RED, fontweight="bold",
                    bbox=dict(facecolor=WHITE, edgecolor="none", pad=1))
    ax.set_ylim(0, 105)
    ax.legend(frameon=False, loc="lower left")
    style_chart(ax, "Fan-out Turns a Dependency's p99 into Your Median",
                "number of services one request waits on (N)",
                "% of requests avoiding every slow path")
    return fig


def timeout_budget() -> plt.Figure:
    fig, ax = canvas(14, 6.4)
    heading(ax, "One Deadline, Propagated Down the Chain",
            "Each hop receives what is left - it never starts a fresh timeout")
    hops = [("Edge / LB", 0, 20), ("API + auth", 20, 50), ("Cache lookup", 50, 60),
            ("Store query", 60, 210), ("Serialize", 210, 230)]
    left, right, total = 18, 92, 500
    scale = (right - left) / total
    for i, (name, start, end) in enumerate(hops):
        y = 72 - i * 11
        ax.text(left - 2, y + 3, name, ha="right", va="center", fontsize=9, color=INK)
        ax.add_patch(Rectangle((left + start * scale, y), (total - start) * scale, 6,
                               facecolor=PALE, edgecolor=LINE))
        ax.add_patch(Rectangle((left + start * scale, y), (end - start) * scale, 6,
                               facecolor=BLUE, edgecolor=NAVY))
        ax.text(left + end * scale + 1, y + 3, f"receives {total - start} ms",
                va="center", fontsize=8, color=GREY)
    ax.plot([right, right], [12, 82], color=RED, linestyle="--", linewidth=2)
    ax.text(right, 84, "500 ms deadline", ha="center", fontsize=9, fontweight="bold", color=RED)
    for ms in range(0, total + 1, 100):
        ax.text(left + ms * scale, 13, f"{ms}", ha="center", fontsize=8, color=GREY)
    ax.text(55, 5, "Slack after 230 ms absorbs one retry - if the deadline allows it",
            ha="center", fontsize=9.5, fontweight="bold", color=NAVY)
    return fig


def retry_amplification() -> plt.Figure:
    fig, ax = canvas(14, 6)
    heading(ax, "Retry Amplification: 3 Attempts per Layer = 27x Load",
            "Retries at every layer multiply - and they arrive exactly when the database is weakest")
    layers = [("User", 1), ("Gateway", 3), ("Service", 9), ("Database", 27)]
    for i, (name, count) in enumerate(layers):
        x0 = 5 + i * 24
        color = RED if count == 27 else BLUE
        ax.text(x0 + 8, 76, name, ha="center", fontsize=11, fontweight="bold", color=NAVY)
        ax.text(x0 + 8, 20, f"{count} call{'s' if count > 1 else ''}", ha="center",
                fontsize=13, fontweight="bold", color=color)
        # Scatter markers stay round on a non-square canvas; patches do not.
        cells = [divmod(j, 5) for j in range(count)]
        ax.scatter([x0 + 1.5 + col * 3.3 for _, col in cells],
                   [66 - row * 7 for row, _ in cells],
                   s=160, color=color, edgecolors=NAVY, zorder=3)
        if i < len(layers) - 1:
            arrow(ax, (x0 + 18, 50), (x0 + 23, 50), color=GREY, label="x3")
    ax.text(50, 8, "Fix: retry at ONE layer, with exponential backoff + jitter and a retry budget",
            ha="center", fontsize=10, color=GREEN, fontweight="bold")
    return fig


def consistency_availability() -> plt.Figure:
    """Replaces v1's four identical sliders with a quadrant that encodes decisions."""
    fig, ax = canvas(12, 8)
    heading(ax, "Choose Per Operation: Consistency Need vs Availability Need",
            "Real operations land in different quadrants of the same product")
    x0, y0, size = 18, 10, 72
    quadrants = [
        (x0, y0 + size / 2, "Refuse rather than be wrong", RED_FACE, RED),
        (x0 + size / 2, y0 + size / 2, "Hardest: pay for consensus", AMBER_FACE, AMBER),
        (x0, y0, "Relax both: batch + approximate", PALE, BLUE),
        (x0 + size / 2, y0, "Serve stale, reconcile later", GREEN_FACE, GREEN),
    ]
    for x, y, label, face, edge in quadrants:
        ax.add_patch(Rectangle((x, y), size / 2, size / 2, facecolor=face, edgecolor=WHITE,
                               linewidth=3))
        ax.text(x + size / 4, y + size / 2 - 4, label, ha="center", fontsize=9.5,
                fontweight="bold", color=edge)
    points = [(26, 62, "Bank ledger"), (26, 48, "Inventory decrement"),
              (62, 62, "Seat reservation"), (64, 28, "Social feed"),
              (58, 18, "Shopping cart (merge)"), (28, 26, "View counter")]
    ax.scatter([x for x, _, _ in points], [y for _, y, _ in points], s=90,
               color=NAVY, edgecolors=WHITE, zorder=3)
    for x, y, label in points:
        ax.text(x + 2, y, label, va="center", fontsize=9, color=INK)
    arrow(ax, (x0, y0 - 3), (x0 + size, y0 - 3), color=GREY)
    ax.text(x0 + size / 2, y0 - 7, "availability need during a failure  ->",
            ha="center", fontsize=9, color=GREY)
    arrow(ax, (x0 - 3, y0), (x0 - 3, y0 + size), color=GREY)
    ax.text(x0 - 6, y0 + size / 2, "consistency need  ->", rotation=90, ha="center",
            va="center", fontsize=9, color=GREY)
    return fig


FIGURES = {
    "availability_composition": availability_composition,
    "latency_percentiles": latency_percentiles,
    "tail_amplification": tail_amplification,
    "timeout_budget": timeout_budget,
    "retry_amplification": retry_amplification,
    "consistency_availability": consistency_availability,
}


def main(names: list[str]) -> None:
    targets = names or list(FIGURES)
    unknown = sorted(set(targets) - set(FIGURES))
    if unknown:
        known = ", ".join(FIGURES)
        raise SystemExit(f"Unknown figure(s): {', '.join(unknown)}. Known: {known}")
    for name in targets:
        save(name, FIGURES[name]())


if __name__ == "__main__":
    main(sys.argv[1:])
