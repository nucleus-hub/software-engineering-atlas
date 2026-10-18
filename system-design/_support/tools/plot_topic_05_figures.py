"""Render the architecture-style, state, boundary, data, and discovery diagrams for topic 05.

Run from the system-design directory:

    uv run --with matplotlib \
      --index-url https://pypi.ci.artifacts.walmart.com/artifactory/api/pypi/external-pypi/simple \
      --allow-insecure-host pypi.ci.artifacts.walmart.com \
      python _support/tools/plot_topic_05_figures.py

Pass figure names to render only selected assets.
"""

from __future__ import annotations

import sys

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

from figure_style import (
    AMBER,
    AMBER_FACE,
    BLUE,
    DEAD,
    GREEN,
    GREEN_FACE,
    GREY,
    INK,
    MIST,
    NAVY,
    PALE,
    RED,
    RED_FACE,
    WHITE,
    arrow,
    badge,
    box,
    canvas,
    heading,
    render,
)

TOPIC = "topic-05"


def label(ax: plt.Axes, x: float, y: float, text: str, color: str = NAVY,
          size: float = 8.5, **kwargs) -> None:
    ax.text(x, y, text, fontsize=size, fontweight="bold", color=color, **kwargs)


def architecture_spectrum() -> plt.Figure:
    fig, ax = canvas(15, 7.2)
    heading(ax, "Three Architecture Styles: Independence Costs Moving Parts",
            "Move right only when a real need pays for the extra network calls and deploys")
    for x, title in ((17, "Layered monolith"), (50, "Modular monolith"), (83, "Microservices")):
        label(ax, x, 80, title, size=11, ha="center")
    # Layered monolith: one deployable sliced horizontally by technical role.
    box(ax, 3, 32, 28, 42, "", face=WHITE, edge=NAVY)
    for y, name in ((61, "API / controllers"), (49, "Business logic"), (37, "Data access")):
        box(ax, 5, y, 24, 8, name, face=PALE)
    # Modular monolith: one deployable sliced vertically by business capability.
    box(ax, 36, 32, 28, 42, "", face=WHITE, edge=NAVY)
    for index, name in enumerate(("Links", "Redirects", "Analytics", "Accounts")):
        x = 37.5 + index * 6.5
        ax.add_patch(Rectangle((x, 35), 5.6, 36, facecolor=MIST, edgecolor=BLUE, linewidth=1.4))
        ax.text(x + 2.8, 53, name, rotation=90, ha="center", va="center", fontsize=9,
                fontweight="bold", color=NAVY)
    for x in (10, 43):
        box(ax, x, 12, 14, 9, "One database", face=WHITE, edge=GREY, title_color=GREY)
        arrow(ax, (x + 7, 31.5), (x + 7, 21.5), color=GREY)
    # Microservices: separate deployables, each owning its data, talking over the network.
    for index, name in enumerate(("Links", "Redirects", "Analytics")):
        x = 68 + index * 10.5
        box(ax, x, 50, 7.5, 14, name, face=MIST)
        box(ax, x, 12, 7.5, 9, "own DB", face=WHITE, edge=GREY, title_color=GREY)
        arrow(ax, (x + 3.75, 49.5), (x + 3.75, 21.5), color=GREY)
    for x in (76, 86.5):
        arrow(ax, (x + 0.2, 57), (x + 2.3, 57), color=AMBER)
    ax.text(83, 70, "network calls between services", ha="center", fontsize=8, color=AMBER)
    for x, text in ((17, "1 deploy, in-process calls,\nlayers by technical role"),
                    (50, "1 deploy, enforced module\nboundaries by business area"),
                    (83, "N deploys, network calls,\neach service owns its data")):
        ax.text(x, 4, text, ha="center", va="center", fontsize=8.2, color=INK, linespacing=1.4)
    return fig


def stateless_vs_stateful() -> plt.Figure:
    fig, ax = canvas(15, 6.8)
    heading(ax, "Stateless Services Are Interchangeable; Stateful Ones Are Not",
            "Keep state in a few well-run stores so everything else can scale and fail freely")
    label(ax, 4, 80, "STATELESS: any instance can serve any request", BLUE)
    label(ax, 55, 80, "STATEFUL: each user is stuck to one instance", RED)
    box(ax, 3, 42, 9, 14, "LB", "any instance", face=WHITE, edge=NAVY)
    box(ax, 40, 38, 10, 22, "Shared store", "cache / DB", face=WHITE, edge=NAVY)
    for y in (64, 44, 24):
        box(ax, 20, y, 12, 11, "Link API", "no local state", face=MIST)
        arrow(ax, (12.5, 49), (19.5, y + 5.5))
        arrow(ax, (32.5, y + 5.5), (39.5, 49), color=GREY)
    box(ax, 55, 42, 9, 14, "LB", "sticky", face=WHITE, edge=NAVY)
    instances = [
        (64, "Instance 1", "sessions: Ana, Raj", MIST, BLUE, NAVY),
        (44, "Instance 2", "sessions: Li, Sam", MIST, BLUE, NAVY),
        (24, "Instance 3: DOWN", "Mo, Zoe logged out", DEAD, RED, RED),
    ]
    for y, title, sub, face, edge, color in instances:
        box(ax, 73, y, 17, 11, title, sub, face=face, edge=edge, title_color=color)
        arrow(ax, (64.5, 49), (72.5, y + 5.5), color=RED if color == RED else BLUE,
              dashed=color == RED)
    ax.text(55, 10, "Fix: move session data into a shared store or a signed token,\n"
            "and the stateful side becomes the stateless side.",
            fontsize=8.5, color=INK, linespacing=1.4)
    return fig


def bounded_contexts() -> plt.Figure:
    fig, ax = canvas(15, 6.6)
    heading(ax, "Same Words, Different Meanings: Boundaries Go Where Meanings Change",
            "Each context owns its own model and shares facts as events, not tables")
    contexts = [
        (3, "Links", "a link is:", "owner, destination,\nexpiry, tags", NAVY, PALE),
        (27, "Redirects", "a link is:", "code -> URL,\nnothing else", BLUE, MIST),
        (51, "Analytics", "a click is:", "time, country,\nreferrer, device", AMBER, AMBER_FACE),
        (75, "Billing", "a click is:", "one unit of usage\nagainst a plan", GREEN, GREEN_FACE),
    ]
    for x, name, prefix, meaning, color, face in contexts:
        box(ax, x, 30, 18, 38, "", face=face, edge=color)
        ax.text(x + 9, 61, name, ha="center", fontsize=11, fontweight="bold", color=color)
        ax.text(x + 9, 52, prefix, ha="center", fontsize=8, color=GREY, fontweight="bold")
        ax.text(x + 9, 43, meaning, ha="center", va="center", fontsize=9, color=INK,
                linespacing=1.45)
    for x, event in ((21.5, "LinkCreated"), (45.5, "Clicked"), (69.5, "usage total")):
        arrow(ax, (x, 49), (x + 5, 49), color=GREY)
        ax.text(x + 2.5, 74, event, ha="center", fontsize=8, color=GREY, style="italic")
        ax.plot([x + 2.5, x + 2.5], [72, 52], color=GREY, linewidth=0.8, linestyle=":")
    ax.text(50, 16, "One shared \"Link\" class used by all four would need every field,\n"
            "and every change to it would ripple through every team.",
            ha="center", fontsize=9, color=INK, linespacing=1.45)
    return fig


def database_ownership() -> plt.Figure:
    fig, ax = canvas(15, 7)
    heading(ax, "Shared Database vs Database per Service",
            "Sharing tables is the tightest coupling two services can have")
    label(ax, 25, 82, "SHARED DATABASE", RED, size=10, ha="center")
    label(ax, 75, 82, "DATABASE PER SERVICE", GREEN, size=10, ha="center")
    for index, name in enumerate(("Links", "Redirects", "Analytics")):
        x = 3 + index * 15
        box(ax, x, 50, 13, 12, name, face=MIST)
        arrow(ax, (x + 6.5, 49.5), (25, 34.5), color=GREY)
    box(ax, 10, 18, 30, 16, "Shared database", "links, clicks, accounts tables",
        face=WHITE, edge=RED, title_color=RED)
    ax.text(25, 6, "Links renames a column, and Analytics\nbreaks in production.",
            ha="center", fontsize=8.5, color=RED, linespacing=1.4)
    stores = ("links DB", "redirect store", "analytics DB")
    for index, (name, store) in enumerate(zip(("Links", "Redirects", "Analytics"), stores)):
        x = 53 + index * 15
        box(ax, x, 50, 13, 12, name, face=MIST)
        box(ax, x, 22, 13, 12, store, face=WHITE, edge=GREEN, title_color=GREEN)
        arrow(ax, (x + 6.5, 49.5), (x + 6.5, 34.5), color=GREEN)
    arrow(ax, (62, 62.5), (72, 62.5), color=AMBER, curve=-0.5, dashed=True)
    arrow(ax, (62, 62.5), (87, 62.5), color=AMBER, curve=-0.35, dashed=True)
    ax.text(75, 75, "LinkCreated events", ha="center", fontsize=8, color=AMBER, style="italic")
    ax.text(75, 6, "Each team changes its own schema freely;\n"
            "others get data through APIs or events.",
            ha="center", fontsize=8.5, color=GREEN, linespacing=1.4)
    return fig


def service_discovery() -> plt.Figure:
    fig, ax = canvas(14, 6.8)
    heading(ax, "Service Discovery: Find Healthy Instances by Name, Not by Address",
            "Instances come and go; the registry keeps the current list")
    box(ax, 3, 42, 15, 16, "Redirect service", "the caller", face=WHITE, edge=NAVY)
    box(ax, 34, 62, 20, 14, "Service registry", "name -> healthy addresses", face=MIST)
    instances = [
        (66, "analytics-1", "10.0.1.7: healthy", PALE, BLUE, NAVY),
        (44, "analytics-2", "10.0.2.4: healthy", PALE, BLUE, NAVY),
        (22, "analytics-3", "failed health check", RED_FACE, RED, RED),
    ]
    for y, name, sub, face, edge, color in instances:
        box(ax, 72, y, 18, 12, name, sub, face=face, edge=edge, title_color=color)
        arrow(ax, (71.5, y + 6), (54.5, 69), color=GREY if color != RED else RED, dashed=True)
    ax.text(63, 76, "register + heartbeat", ha="center", fontsize=8, color=GREY)
    arrow(ax, (18.5, 55), (33.5, 66))
    badge(ax, 20, 68, "1")
    ax.text(22, 68, "where is analytics?", fontsize=8, color=BLUE, va="center")
    arrow(ax, (33.5, 62), (18.5, 51), color=GREEN)
    badge(ax, 27, 53.5, "2", color=GREEN)
    ax.text(29, 53.5, "2 healthy addresses", fontsize=8, color=GREEN, va="center")
    arrow(ax, (18.5, 46), (71.5, 50))
    badge(ax, 45, 45, "3")
    ax.text(47, 45, "call one directly", fontsize=8, color=BLUE, va="center")
    ax.text(3, 12, "Same idea, other shapes: a DNS name that resolves to healthy instances "
            "(as in Kubernetes),\nor a load balancer or sidecar proxy that does the lookup "
            "for the caller.", fontsize=8.5, color=INK, linespacing=1.45)
    return fig


def url_shortener_year_two() -> plt.Figure:
    fig, ax = canvas(15, 7.6)
    heading(ax, "URL Shortener, Year Two: Split Only Where the Numbers Disagree",
            "One modular monolith, plus the two parts that scale and fail differently")
    box(ax, 2, 40, 9, 14, "Client", face=WHITE, edge=NAVY)
    box(ax, 15, 40, 11, 14, "Load balancer", "routes by path")
    box(ax, 32, 64, 17, 14, "Core monolith", "links, accounts, billing", face=MIST)
    box(ax, 56, 64, 15, 14, "Core database", "source of truth", face=WHITE, edge=NAVY)
    box(ax, 32, 40, 17, 14, "Redirect service", "read-only, stateless", face=MIST)
    box(ax, 56, 40, 15, 14, "Redirect store", "code -> URL copy")
    box(ax, 32, 12, 17, 12, "Click events", "queue", face=AMBER_FACE, edge=AMBER,
        title_color=AMBER)
    box(ax, 56, 12, 15, 12, "Analytics", "service", face=AMBER_FACE, edge=AMBER,
        title_color=AMBER)
    box(ax, 78, 12, 17, 12, "Analytics store", "query-optimized", face=WHITE, edge=AMBER,
        title_color=AMBER)
    arrow(ax, (11.5, 47), (14.5, 47))
    arrow(ax, (26.5, 47), (31.5, 47))
    ax.text(29, 42.5, "/{code}", ha="center", fontsize=7.5, color=BLUE)
    arrow(ax, (26.5, 51), (31.5, 69), color=NAVY, label="manage")
    arrow(ax, (49.5, 71), (55.5, 71), color=NAVY)
    arrow(ax, (49.5, 47), (55.5, 47))
    arrow(ax, (46, 63.5), (60, 54.5), color=AMBER, dashed=True, label="LinkCreated")
    arrow(ax, (40.5, 39.5), (40.5, 24.5), color=AMBER, dashed=True, label="click")
    arrow(ax, (49.5, 18), (55.5, 18), color=AMBER)
    arrow(ax, (71.5, 18), (77.5, 18), color=AMBER)
    label(ax, 76, 74, "CORE")
    ax.text(76, 69, "~80 writes/s, changes\nweekly, one team", fontsize=8, color=INK,
            va="top", linespacing=1.4)
    label(ax, 76, 50, "REDIRECT", BLUE)
    ax.text(76, 45, "~8,000 reads/s, must\nnot fail, rarely changes", fontsize=8, color=INK,
            va="top", linespacing=1.4)
    return fig


FIGURES = {
    "architecture_spectrum": architecture_spectrum,
    "stateless_vs_stateful": stateless_vs_stateful,
    "bounded_contexts": bounded_contexts,
    "database_ownership": database_ownership,
    "service_discovery": service_discovery,
    "url_shortener_year_two": url_shortener_year_two,
}


if __name__ == "__main__":
    render(FIGURES, TOPIC, sys.argv[1:])
