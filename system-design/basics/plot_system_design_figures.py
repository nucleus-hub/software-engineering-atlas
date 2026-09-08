"""Render visual diagrams for System Design topic 01.

Run from the system-design directory:

    uv run --with matplotlib \
      --index-url https://pypi.ci.artifacts.walmart.com/artifactory/api/pypi/external-pypi/simple \
      --allow-insecure-host pypi.ci.artifacts.walmart.com \
      python basics/plot_system_design_figures.py

Pass figure names to render only selected assets.
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch, Rectangle  # noqa: E402

ASSETS = Path(__file__).resolve().parent / "assets"
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
    """Return a clean, consistently styled drawing surface."""
    fig, ax = plt.subplots(figsize=(width, height), facecolor=WHITE)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")
    return fig, ax


def heading(ax: plt.Axes, title: str, subtitle: str = "") -> None:
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


def save(name: str, fig: plt.Figure) -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    output = ASSETS / f"{name}.png"
    fig.savefig(output, dpi=DPI, bbox_inches="tight", facecolor=WHITE)
    plt.close(fig)
    print(f"wrote basics/assets/{output.name}")


def interview_framework() -> plt.Figure:
    fig, ax = canvas(14, 5.4)
    heading(ax, "From Ambiguous Prompt to Defensible Design",
            "Each stage narrows the design space and supplies evidence for the next")
    steps = [
        ("01", "Clarify", "scope + goals"),
        ("02", "Quantify", "scale + SLOs"),
        ("03", "Contract", "APIs + data"),
        ("04", "Design", "critical paths"),
        ("05", "Stress", "risks + failures"),
        ("06", "Defend", "trade-offs"),
    ]
    xs = [4, 20, 36, 52, 68, 84]
    for index, ((number, title, subtitle), x) in enumerate(zip(steps, xs)):
        face = MIST if index in (3, 4) else PALE
        box(ax, x, 39, 12, 24, title, subtitle, face=face)
        ax.add_patch(Circle((x + 6, 69), 3.3, facecolor=NAVY, edgecolor=NAVY))
        ax.text(x + 6, 69, number, ha="center", va="center", fontsize=8,
                fontweight="bold", color=WHITE)
        if index < len(xs) - 1:
            arrow(ax, (x + 12.5, 51), (xs[index + 1] - 0.5, 51))
    ax.text(50, 25, "OUTPUT", ha="center", va="center", fontsize=8,
            fontweight="bold", color=GREY)
    box(ax, 34, 10, 32, 11, "A design whose assumptions and trade-offs are explicit",
        face=WHITE, edge=NAVY)
    return fig


def interview_timeline() -> plt.Figure:
    fig, ax = canvas(15, 7)
    heading(ax, "A Practical 45-Minute System Design Interview",
            "Spend most of the session designing and pressure-testing—not collecting trivia")
    phases = [
        (0, 5, "Clarify scope", "users + use cases", PALE),
        (5, 10, "Estimate scale", "QPS + storage", PALE),
        (10, 15, "Define contracts", "APIs + data", PALE),
        (15, 25, "High-level design", "critical paths", MIST),
        (25, 38, "Deep-dive risks", "bottlenecks", SKY),
        (38, 43, "Failures", "degradation", MIST),
        (43, 45, "Summarize", "trade-offs", PALE),
    ]
    left, right, y, height = 5, 95, 53, 14
    scale = (right - left) / 45
    for number, (start, end, title, subtitle, color) in enumerate(phases, start=1):
        x = left + start * scale
        width = (end - start) * scale
        ax.add_patch(Rectangle((x, y), width, height, facecolor=color,
                               edgecolor=NAVY, linewidth=1.5))
        text_color = WHITE if color == SKY else NAVY
        if width >= 9:
            ax.text(x + width / 2, y + 8.6, title, ha="center", va="center",
                    fontsize=8.2, fontweight="bold", color=text_color)
            ax.text(x + width / 2, y + 4.2, subtitle, ha="center", va="center",
                    fontsize=6.8, color=text_color)
        else:
            ax.text(x + width / 2, y + height / 2, "Wrap-up", ha="center",
                    va="center", rotation=90, fontsize=6.5,
                    fontweight="bold", color=text_color)
        ax.add_patch(Circle((x + width / 2, y + height + 7), 2.6,
                            facecolor=NAVY, edgecolor=NAVY))
        ax.text(x + width / 2, y + height + 7, str(number), ha="center",
                va="center", fontsize=7.5, fontweight="bold", color=WHITE)
        ax.text(x + width / 2, y - 5, f"{start}-{end} min", ha="center",
                va="center", fontsize=7.2, color=INK)
    ax.plot([left, right], [y - 10, y - 10], color=LINE, linewidth=2)
    for minute in range(0, 46, 5):
        x = left + minute * scale
        ax.plot([x, x], [y - 12, y - 8], color=GREY, linewidth=1)
        ax.text(x, y - 16, str(minute), ha="center", va="center", fontsize=7,
                color=GREY)
    ax.text(left, y - 23, "START", ha="left", fontsize=7, fontweight="bold", color=GREY)
    ax.text(right, y - 23, "FINISH", ha="right", fontsize=7, fontweight="bold", color=GREY)
    ax.add_patch(FancyBboxPatch((34, 10), 56, 12,
                               boxstyle="round,pad=0.5,rounding_size=2",
                               facecolor="#F3F7FF", edgecolor=BLUE, linewidth=1.5))
    ax.text(62, 16, "~62% of the interview: architecture, deep dives, and failure reasoning",
            ha="center", va="center", fontsize=9.5, fontweight="bold", color=NAVY)
    arrow(ax, (62, 23), (62, 49), color=BLUE)
    return fig


def critical_path() -> plt.Figure:
    fig, ax = canvas(14, 6.2)
    heading(ax, "Draw the Critical Path First",
            "Keep user-facing work synchronous; move optional fan-out off the latency path")
    box(ax, 3, 51, 12, 16, "Client", "request", face=WHITE, edge=NAVY)
    box(ax, 21, 51, 14, 16, "Edge", "DNS / CDN / LB")
    box(ax, 41, 51, 14, 16, "API", "stateless service", face=MIST)
    box(ax, 61, 51, 14, 16, "Cache", "fast lookup")
    box(ax, 81, 51, 14, 16, "Data store", "durable source")
    for start, end in [((15, 59), (21, 59)), ((35, 59), (41, 59)),
                       ((55, 59), (61, 59)), ((75, 59), (81, 59))]:
        arrow(ax, start, end)
    arrow(ax, (48, 50), (68, 33), color=AMBER, label="events", dashed=True)
    box(ax, 58, 17, 20, 15, "Queue", "buffer + decouple", face="#FFF5DC", edge=AMBER)
    arrow(ax, (78.5, 24.5), (84, 24.5), color=AMBER)
    box(ax, 84, 17, 12, 15, "Workers", "async fan-out", face="#FFF5DC", edge=AMBER)
    ax.text(49, 75, "SYNCHRONOUS USER PATH", ha="center", fontsize=8,
            fontweight="bold", color=BLUE)
    ax.text(77, 9, "ASYNCHRONOUS PATH", ha="center", fontsize=8,
            fontweight="bold", color=AMBER)
    return fig


def capacity_estimation() -> plt.Figure:
    fig, ax = canvas(14, 6)
    heading(ax, "Capacity Estimation: Derive Infrastructure from User Behavior",
            "Keep assumptions connected so one changed input can be propagated")
    box(ax, 4, 57, 14, 17, "Users", "DAU / MAU", face=WHITE, edge=NAVY)
    box(ax, 25, 57, 16, 17, "Operations", "actions per user")
    box(ax, 48, 57, 16, 17, "Traffic", "average + peak", face=MIST)
    arrow(ax, (18.5, 65.5), (24.5, 65.5))
    arrow(ax, (41.5, 65.5), (47.5, 65.5))
    branches = [
        (7, "Bandwidth", "QPS x payload", BLUE),
        (29, "Concurrency", "QPS x latency", NAVY),
        (51, "Compute", "safe QPS / host", GREEN),
        (73, "Storage", "records x bytes", AMBER),
    ]
    for x, title, subtitle, color in branches:
        box(ax, x, 20, 18, 17, title, subtitle, face=WHITE, edge=color,
            title_color=color)
        arrow(ax, (56, 56.5), (x + 9, 37.5), color=color, curve=(x - 40) / 180)
    ax.text(84, 65, "Peak factor\n+ headroom", ha="center", va="center",
            fontsize=10, fontweight="bold", color=RED,
            bbox=dict(boxstyle="round,pad=0.6", facecolor="#FDEDEC", edgecolor=RED))
    arrow(ax, (76, 65), (65, 65), color=RED)
    return fig


def decision_framework() -> plt.Figure:
    fig, ax = canvas(14, 5.7)
    heading(ax, "A Defensible Architecture Decision",
            "Connect every component choice to evidence, cost, and an evolution trigger")
    steps = [
        ("Requirement", "What must be true?", NAVY),
        ("Alternatives", "What could work?", BLUE),
        ("Trade-offs", "Benefit vs cost", AMBER),
        ("Decision", "Choose + explain", GREEN),
        ("Validate", "Metric or test", BLUE),
        ("Evolve", "Trigger + rollback", NAVY),
    ]
    xs = [3, 19.5, 36, 52.5, 69, 85.5]
    for i, ((title, subtitle, color), x) in enumerate(zip(steps, xs)):
        box(ax, x, 42, 11.5, 22, title, subtitle, face=WHITE, edge=color,
            title_color=color)
        if i < len(xs) - 1:
            arrow(ax, (x + 12, 53), (xs[i + 1] - 0.5, 53), color=GREY)
    ax.text(50, 26, "DECISION SENTENCE", ha="center", fontsize=8,
            fontweight="bold", color=GREY)
    ax.text(50, 17,
            '"Given X and Y, choose A over B; it improves C, costs D, and evolves when E."',
            ha="center", va="center", fontsize=10.5, color=NAVY,
            bbox=dict(boxstyle="round,pad=0.8", facecolor=PALE, edgecolor=BLUE))
    return fig


def quality_tradeoffs() -> plt.Figure:
    fig, axes = plt.subplots(1, 4, figsize=(15, 4.8), facecolor=WHITE)
    fig.suptitle("System Design Is the Management of Product-Specific Tensions",
                 fontsize=18, fontweight="bold", color=NAVY, y=0.98)
    pairs = [
        ("Consistency", "Availability", "coordination", BLUE),
        ("Reliability", "Cost", "redundancy", GREEN),
        ("Security", "Performance", "checks + crypto", RED),
        ("Simplicity", "Flexibility", "abstraction", AMBER),
    ]
    for ax, (left, right, cost, color) in zip(axes, pairs):
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 10)
        ax.axis("off")
        ax.set_title(f"{left}  vs  {right}", fontsize=11, fontweight="bold",
                     color=NAVY, pad=14)
        ax.plot([2.1, 7.9], [7.6, 2.8], color=color, linewidth=5,
                solid_capstyle="round")
        ax.add_patch(Circle((5, 5.2), 0.5, facecolor=color, edgecolor=NAVY))
        ax.add_patch(Circle((2.1, 7.6), 0.68, facecolor=PALE, edgecolor=color,
                            linewidth=2))
        ax.add_patch(Circle((7.9, 2.8), 0.68, facecolor=PALE, edgecolor=color,
                            linewidth=2))
        ax.text(2.1, 8.8, left, ha="center", fontsize=8.5, fontweight="bold",
                color=color)
        ax.text(7.9, 1.5, right, ha="center", fontsize=8.5, fontweight="bold",
                color=color)
        ax.text(5, 0.2, f"cost: {cost}", ha="center", fontsize=8,
                color=GREY, style="italic")
        for spine in ax.spines.values():
            spine.set_visible(True)
            spine.set_edgecolor(LINE)
    fig.tight_layout(rect=[0, 0, 1, 0.9])
    return fig


def failure_response() -> plt.Figure:
    fig, ax = canvas(14, 6.4)
    heading(ax, "Reason About Dependency Failure Before Choosing a Reaction",
            "Retries are one option—not a personality trait")
    box(ax, 4, 56, 15, 18, "Dependency fails", "slow / error / stale",
        face="#FDEDEC", edge=RED, title_color=RED)
    box(ax, 29, 56, 16, 18, "Critical path?", "user blocked?", face=PALE)
    arrow(ax, (19.5, 65), (28.5, 65), color=RED)
    box(ax, 55, 69, 17, 16, "No", "defer / queue / drop", face="#FFF5DC",
        edge=AMBER, title_color=AMBER)
    box(ax, 55, 39, 17, 16, "Yes", "is fallback valid?", face=MIST)
    arrow(ax, (45.5, 67), (54.5, 76), label="non-critical", color=AMBER)
    arrow(ax, (45.5, 61), (54.5, 47), label="critical", color=BLUE)
    box(ax, 81, 57, 15, 16, "Degrade", "serve safe fallback", face="#E9F7EF",
        edge=GREEN, title_color=GREEN)
    box(ax, 81, 28, 15, 16, "Fail fast", "respect timeout", face="#FDEDEC",
        edge=RED, title_color=RED)
    arrow(ax, (72.5, 48), (80.5, 65), label="yes", color=GREEN)
    arrow(ax, (72.5, 44), (80.5, 36), label="no", color=RED)
    ax.text(50, 16, "BOUND EVERYTHING", ha="center", fontsize=8,
            fontweight="bold", color=GREY)
    ax.text(50, 9, "timeouts  •  retries  •  queues  •  concurrency  •  recovery",
            ha="center", fontsize=10, color=NAVY)
    return fig


def url_shortener_architecture() -> plt.Figure:
    fig, ax = canvas(15, 7.4)
    heading(ax, "URL Shortener: Fast Redirects, Durable Writes, Async Analytics",
            "The redirect remains available even when analytics is delayed")
    box(ax, 3, 58, 11, 16, "Client", "create / redirect", face=WHITE, edge=NAVY)
    box(ax, 20, 58, 13, 16, "Load balancer", "route + health")
    box(ax, 39, 58, 13, 16, "Link API", "stateless", face=MIST)
    box(ax, 60, 66, 13, 15, "Cache", "short code lookup")
    box(ax, 60, 42, 13, 15, "Link store", "durable source", face=WHITE, edge=NAVY)
    for start, end in [((14.5, 66), (19.5, 66)), ((33.5, 66), (38.5, 66)),
                       ((52.5, 68), (59.5, 73.5))]:
        arrow(ax, start, end)
    arrow(ax, (66.5, 65.5), (66.5, 57.5), label="miss", color=RED)
    arrow(ax, (52.5, 62), (59.5, 49.5), label="create", color=NAVY)
    box(ax, 39, 20, 13, 15, "Event queue", "durable buffer", face="#FFF5DC",
        edge=AMBER, title_color=AMBER)
    box(ax, 60, 20, 13, 15, "Workers", "idempotent", face="#FFF5DC",
        edge=AMBER, title_color=AMBER)
    box(ax, 81, 20, 15, 15, "Analytics store", "query-optimized", face=WHITE,
        edge=AMBER, title_color=AMBER)
    arrow(ax, (45.5, 57.5), (45.5, 35.5), label="click event", color=AMBER,
          dashed=True)
    arrow(ax, (52.5, 27.5), (59.5, 27.5), color=AMBER)
    arrow(ax, (73.5, 27.5), (80.5, 27.5), color=AMBER)
    ax.text(83, 69, "REDIRECT PATH", fontsize=8, fontweight="bold", color=BLUE)
    ax.text(83, 63, "cache-first, low latency", fontsize=8, color=INK)
    ax.text(83, 48, "CREATE PATH", fontsize=8, fontweight="bold", color=NAVY)
    ax.text(83, 42, "durable before acknowledge", fontsize=8, color=INK)
    return fig


FIGURES = {
    "interview_framework": interview_framework,
    "interview_timeline": interview_timeline,
    "critical_path": critical_path,
    "capacity_estimation": capacity_estimation,
    "decision_framework": decision_framework,
    "quality_tradeoffs": quality_tradeoffs,
    "failure_response": failure_response,
    "url_shortener_architecture": url_shortener_architecture,
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
