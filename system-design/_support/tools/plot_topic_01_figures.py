"""Render the framework, estimation, decision, and worked-example diagrams for topic 01.

The reliability charts (availability, latency, timeouts, retries, consistency) live in
``plot_topic_01_reliability_figures.py``; both scripts write to ``basics/assets/topic-01``.

Run from the system-design directory:

    uv run --with matplotlib \
      --index-url https://pypi.ci.artifacts.walmart.com/artifactory/api/pypi/external-pypi/simple \
      --allow-insecure-host pypi.ci.artifacts.walmart.com \
      python _support/tools/plot_topic_01_figures.py

Pass figure names to render only selected assets.
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyBboxPatch, Rectangle

from figure_style import (
    AMBER,
    AMBER_FACE,
    BLUE,
    DEAD,
    DPI,
    GREEN,
    GREEN_FACE,
    GREY,
    INK,
    LINE,
    MIST,
    NAVY,
    PALE,
    RED,
    RED_FACE,
    SKY,
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
    box(ax, 58, 17, 20, 15, "Queue", "buffer + decouple", face=AMBER_FACE, edge=AMBER)
    arrow(ax, (78.5, 24.5), (84, 24.5), color=AMBER)
    box(ax, 84, 17, 12, 15, "Workers", "async fan-out", face=AMBER_FACE, edge=AMBER)
    ax.text(49, 75, "SYNCHRONOUS USER PATH", ha="center", fontsize=8,
            fontweight="bold", color=BLUE)
    ax.text(77, 9, "ASYNCHRONOUS PATH", ha="center", fontsize=8,
            fontweight="bold", color=AMBER)
    return fig


def capacity_estimation() -> plt.Figure:
    """Every branch descends from its true parent: writes drive storage."""
    fig, ax = canvas(14, 6.4)
    heading(ax, "Capacity Estimation: Derive Infrastructure from User Behavior",
            "Writes drive storage; peak traffic drives bandwidth, concurrency, and compute")
    box(ax, 4, 60, 14, 15, "Users", "DAU / MAU", face=WHITE, edge=NAVY)
    box(ax, 26, 60, 16, 15, "Operations", "actions per user")
    box(ax, 50, 60, 16, 15, "Traffic", "average + peak QPS", face=MIST)
    arrow(ax, (18.5, 67.5), (25.5, 67.5))
    arrow(ax, (42.5, 67.5), (49.5, 67.5))
    ax.text(85, 67.5, "Peak factor\n+ headroom", ha="center", va="center",
            fontsize=10, fontweight="bold", color=RED,
            bbox=dict(boxstyle="round,pad=0.6", facecolor=RED_FACE, edgecolor=RED))
    arrow(ax, (77, 67.5), (66.5, 67.5), color=RED)
    # Storage hangs off write operations, not off read traffic.
    box(ax, 3, 14, 21, 15, "Storage", "writes x size x retention x copies",
        face=WHITE, edge=AMBER, title_color=AMBER)
    arrow(ax, (34, 59.5), (13.5, 29.5), color=AMBER, label="writes")
    # Traffic feeds a bus so each branch visibly shares one parent.
    ax.plot([58, 58], [59.5, 45], color=BLUE, linewidth=1.8)
    ax.plot([39, 83], [45, 45], color=BLUE, linewidth=1.8)
    for x, title, subtitle, color in [
        (30, "Bandwidth", "QPS x payload", BLUE),
        (52, "Concurrency", "QPS x latency", NAVY),
        (74, "Compute", "QPS / safe QPS per host", GREEN),
    ]:
        box(ax, x, 14, 18, 15, title, subtitle, face=WHITE, edge=color, title_color=color)
        arrow(ax, (x + 9, 45), (x + 9, 29.5), color=color)
    return fig


def estimate_to_decision() -> plt.Figure:
    fig, ax = canvas(14, 8)
    heading(ax, "Every Estimate Must Terminate in a Decision",
            "If a number cannot move one of these arrows, do not compute it")
    rows = [
        ("Read:write >= 10:1", "Cache-aside or read replicas"),
        ("Working set > one node's RAM", "Shard the cache, or cache only the hot set"),
        ("Data > ~10 TB, or growing without bound", "Partition, tier to cold storage, or add TTL"),
        ("Write QPS near one primary's limit", "Shard writes, or buffer via a queue"),
        ("Peak >> average", "Autoscale + queue + load shedding"),
        ("Distant users with a tight p99", "CDN / edge cache, then multi-region"),
    ]
    for i, (estimate, decision) in enumerate(rows):
        y = 70 - i * 12
        box(ax, 5, y, 36, 8, estimate, face=PALE)
        box(ax, 59, y, 36, 8, decision, face=GREEN_FACE, edge=GREEN, title_color=GREEN)
        arrow(ax, (41.5, y + 4), (58.5, y + 4), color=GREY)
    ax.text(23, 81, "IF THE ESTIMATE SAYS...", ha="center", fontsize=8,
            fontweight="bold", color=GREY)
    ax.text(77, 81, "...THEN CONSIDER", ha="center", fontsize=8,
            fontweight="bold", color=GREY)
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


def failure_response() -> plt.Figure:
    fig, ax = canvas(14, 6.4)
    heading(ax, "Reason About Dependency Failure Before Choosing a Reaction",
            "Retries are one option—not a personality trait")
    box(ax, 4, 56, 15, 18, "Dependency fails", "slow / error / stale",
        face=RED_FACE, edge=RED, title_color=RED)
    box(ax, 29, 56, 16, 18, "Critical path?", "user blocked?", face=PALE)
    arrow(ax, (19.5, 65), (28.5, 65), color=RED)
    box(ax, 55, 69, 17, 16, "No", "defer / queue / drop", face=AMBER_FACE,
        edge=AMBER, title_color=AMBER)
    box(ax, 55, 39, 17, 16, "Yes", "is fallback valid?", face=MIST)
    arrow(ax, (45.5, 67), (54.5, 76), label="non-critical", color=AMBER)
    arrow(ax, (45.5, 61), (54.5, 47), label="critical", color=BLUE)
    box(ax, 81, 57, 15, 16, "Degrade", "serve safe fallback", face=GREEN_FACE,
        edge=GREEN, title_color=GREEN)
    box(ax, 81, 28, 15, 16, "Fail fast", "respect timeout", face=RED_FACE,
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
    box(ax, 39, 20, 13, 15, "Event queue", "durable buffer", face=AMBER_FACE,
        edge=AMBER, title_color=AMBER)
    box(ax, 60, 20, 13, 15, "Workers", "idempotent", face=AMBER_FACE,
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


def url_shortener_degraded() -> plt.Figure:
    fig, ax = canvas(15, 7.4)
    heading(ax, "URL Shortener, Degraded Mode: Link Store Down",
            "Warm redirects keep working; creates fail loudly; analytics buffers")
    box(ax, 3, 58, 11, 16, "Client", "create / redirect", face=WHITE, edge=NAVY)
    box(ax, 20, 58, 13, 16, "Load balancer", "route + health")
    box(ax, 39, 58, 13, 16, "Link API", "stateless", face=MIST)
    box(ax, 60, 66, 13, 15, "Cache", "warm codes: HIT", face=GREEN_FACE, edge=GREEN,
        title_color=GREEN)
    box(ax, 60, 40, 13, 15, "Link store: DOWN", "unavailable", face=DEAD, edge=RED,
        title_color=RED)
    for start, end in [((14.5, 66), (19.5, 66)), ((33.5, 66), (38.5, 66))]:
        arrow(ax, start, end)
    arrow(ax, (52.5, 68), (59.5, 73.5), color=GREEN, label="hit")
    arrow(ax, (52.5, 62), (59.5, 48), color=RED, label="create -> 503", dashed=True)
    box(ax, 39, 18, 13, 14, "Event queue", "buffering", face=AMBER_FACE, edge=AMBER,
        title_color=AMBER)
    arrow(ax, (45.5, 57.5), (45.5, 32.5), color=AMBER, dashed=True, label="click event")
    ax.text(80, 76, "WARM REDIRECTS", fontsize=8, fontweight="bold", color=GREEN)
    ax.text(80, 71, "served from cache", fontsize=8, color=INK)
    ax.text(80, 55, "COLD REDIRECTS", fontsize=8, fontweight="bold", color=AMBER)
    ax.text(80, 50, "miss -> fail fast, bounded", fontsize=8, color=INK)
    ax.text(80, 40, "CREATES", fontsize=8, fontweight="bold", color=RED)
    ax.text(80, 35, "never ack an unsaved code", fontsize=8, color=INK)
    return fig


FIGURES = {
    "interview_framework": interview_framework,
    "interview_timeline": interview_timeline,
    "critical_path": critical_path,
    "capacity_estimation": capacity_estimation,
    "estimate_to_decision": estimate_to_decision,
    "decision_framework": decision_framework,
    "failure_response": failure_response,
    "url_shortener_architecture": url_shortener_architecture,
    "url_shortener_degraded": url_shortener_degraded,
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
