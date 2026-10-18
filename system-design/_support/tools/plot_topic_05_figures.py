"""Render the diagrams for Topic 05: Architecture Styles & Service Decomposition.

Run from the system-design directory (optionally pass figure names):

    uv run --with matplotlib \
      --index-url https://pypi.ci.artifacts.walmart.com/artifactory/api/pypi/external-pypi/simple \
      --allow-insecure-host pypi.ci.artifacts.walmart.com \
      python _support/tools/plot_topic_05_figures.py
"""

from __future__ import annotations

import math
import sys

import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Rectangle

from figure_style import (
    AMBER,
    AMBER_FACE,
    BLUE,
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
    WHITE,
    arrow,
    badge,
    box,
    canvas,
    heading,
    render,
)

TOPIC = "topic-05"


# ---------- small local helpers ------------------------------------------------

def caps(ax: plt.Axes, x: float, y: float, text: str, *, color: str = GREY,
         ha: str = "center", size: float = 8.5) -> None:
    ax.text(x, y, text, ha=ha, va="center", fontsize=size, fontweight="bold",
            color=color)


def note(ax: plt.Axes, x: float, y: float, text: str, *, color: str = INK,
         size: float = 8.6, ha: str = "center") -> None:
    ax.text(x, y, text, ha=ha, va="center", fontsize=size, color=color,
            linespacing=1.45)


def outline(ax: plt.Axes, x: float, y: float, width: float, height: float,
            label: str = "", *, color: str = GREY) -> None:
    """Dashed rectangle marking one deployable unit."""
    ax.add_patch(Rectangle((x, y), width, height, facecolor="none", edgecolor=color,
                           linestyle="--", linewidth=1.4))
    if label:
        ax.text(x + 1, y + height - 2.2, label, fontsize=7.5, color=color,
                style="italic", va="center")


def container(ax: plt.Axes, x: float, y: float, width: float, height: float,
              title: str, subtitle: str = "", *, face: str = WHITE,
              edge: str = NAVY) -> None:
    """A box whose title sits at the top, leaving room for boxes inside it."""
    box(ax, x, y, width, height, "", face=face, edge=edge)
    ax.text(x + width / 2, y + height - 3, title, ha="center", va="center",
            fontsize=10.5, fontweight="bold", color=NAVY)
    if subtitle:
        ax.text(x + width / 2, y + height - 7.5, subtitle, ha="center", va="center",
                fontsize=8.2, color=INK)


# ---------- figures --------------------------------------------------------------

def architecture_spectrum() -> plt.Figure:
    fig, ax = canvas(15, 8)
    heading(ax, "Three Ways to Structure the Same Application",
            "The code can be identical; what changes is where the boundaries are "
            "and what enforces them")
    columns = [(3, "Layered monolith", NAVY), (36, "Modular monolith", BLUE),
               (69, "Microservices", GREEN)]
    for x0, title, color in columns:
        caps(ax, x0 + 14, 82, title.upper(), color=color, size=9.5)

    # Layered monolith: horizontal slices, one database.
    x0 = 3
    outline(ax, x0, 50, 28, 28, "one deployable")
    for index, (name, sub) in enumerate((("Controllers", "web"), ("Services", "business rules"),
                                         ("Repositories", "data access"))):
        box(ax, x0 + 2.5, 67 - index * 7, 23, 3.6, f"{name}  ·  {sub}")
    box(ax, x0 + 6, 39, 16, 4, "One database", face=WHITE, edge=NAVY)
    arrow(ax, (x0 + 14, 52.5), (x0 + 14, 44), color=NAVY)

    # Modular monolith: vertical modules, schema per module.
    x0 = 36
    outline(ax, x0, 50, 28, 28, "one deployable")
    for index, name in enumerate(("Links", "Analytics", "Accounts")):
        mx = x0 + 1.5 + index * 9
        box(ax, mx, 54, 7, 15, name, "api +\ninternal", edge=BLUE)
        arrow(ax, (mx + 3.5, 53.3), (mx + 3.5, 44), color=BLUE)
    box(ax, x0 + 1.5, 39, 25, 4, "One DB, a schema per module", face=WHITE,
        edge=NAVY)

    # Microservices: separate deployables, each with its own data.
    x0 = 69
    caps(ax, x0 + 14, 76, "every arrow is a network call", color=GREY, size=7.5)
    for index, name in enumerate(("Links", "Analytics", "Accounts")):
        mx = x0 + 0.5 + index * 10
        outline(ax, mx - 0.8, 37.5, 8.6, 35.5, color=LINE)
        box(ax, mx, 58, 7, 11, name, "service", face=GREEN_FACE, edge=GREEN)
        box(ax, mx, 39, 7, 4, "own DB", face=WHITE, edge=NAVY)
        arrow(ax, (mx + 3.5, 57.3), (mx + 3.5, 44), color=GREEN)
    for index in range(2):
        mx = x0 + 0.5 + index * 10
        arrow(ax, (mx + 7.6, 63.5), (mx + 9.9, 63.5), color=GREY, dashed=True)

    rows = [
        ("DEPLOYS AS", ("one unit", "one unit", "one unit per service")),
        ("BOUNDARIES HELD BY", ("discipline only", "module rules + tests",
                                "the network itself")),
        ("FITS BEST", ("small app, one team", "most products, 1-5 teams",
                       "many teams that must\nrelease independently")),
    ]
    for index, (label, values) in enumerate(rows):
        y = 28 - index * 10
        for (x0, _, color), value in zip(columns, values):
            caps(ax, x0 + 14, y + 2.5, label, size=7.2)
            note(ax, x0 + 14, y - 1.8, value, size=8.8)
    return fig


def layered_vs_hexagonal() -> plt.Figure:
    fig, ax = canvas(15, 7.5)
    heading(ax, "Layered vs Hexagonal: Which Way Do the Dependencies Point?",
            "Hexagonal architecture is dependency inversion (Basics 2) applied to the "
            "whole application")
    caps(ax, 20, 81, "LAYERED", color=NAVY, size=9.5)
    caps(ax, 71, 81, "HEXAGONAL (PORTS AND ADAPTERS)", color=GREEN, size=9.5)
    ax.plot([41, 41], [8, 84], color=LINE, linewidth=1.2)

    stack = [("Controllers", "HTTP in", PALE, BLUE), ("Services", "business rules", MIST, BLUE),
             ("Repositories", "SQL queries", PALE, BLUE), ("Database", "Postgres", WHITE, NAVY)]
    for index, (name, sub, face, edge) in enumerate(stack):
        y = 66 - index * 15
        box(ax, 8, y, 24, 8, name, sub, face=face, edge=edge)
        if index < len(stack) - 1:
            arrow(ax, (20, y - 0.6), (20, y - 6.4), color=NAVY)
    note(ax, 20, 12, "Business rules depend on the data-access code below them.\n"
         "Testing a rule needs a database; switching storage edits the services.",
         size=8.2, color=RED)

    cx, cy, radius = 71, 46, 9.5
    points = [(cx + radius * math.cos(math.radians(a)),
               cy + 2 * radius * math.sin(math.radians(a))) for a in range(0, 360, 60)]
    ax.add_patch(Polygon(points, closed=True, facecolor=MIST, edgecolor=GREEN,
                         linewidth=2))
    note(ax, cx, cy + 6, "Domain", size=11, color=NAVY)
    note(ax, cx, cy, "Link rules\nLinkService", size=8.4)
    note(ax, cx, cy - 8, "no framework or\ndatabase imports", size=7.4, color=GREY)

    caps(ax, 50, 72, "DRIVING ADAPTERS", size=7.5)
    caps(ax, 91, 72, "DRIVEN ADAPTERS", size=7.5)
    box(ax, 44, 56, 12, 8, "REST controller", "calls a port", face=WHITE, edge=BLUE)
    box(ax, 44, 30, 12, 8, "Scheduled job", "calls a port", face=WHITE, edge=BLUE)
    box(ax, 84, 56, 14, 8, "PostgresLinkRepo", "implements a port", face=WHITE, edge=NAVY)
    box(ax, 84, 30, 14, 8, "FakeLinkRepo", "tests, in memory", face=GREEN_FACE, edge=GREEN)
    arrow(ax, (56.5, 60), (63.5, 54), color=BLUE)
    arrow(ax, (56.5, 34), (63.5, 39), color=BLUE)
    arrow(ax, (83.5, 60), (78.5, 54), color=NAVY)
    arrow(ax, (83.5, 34), (78.5, 39), color=GREEN)
    note(ax, 71, 12, "Every arrow points inward. The domain owns the port interfaces;\n"
         "adapters plug into them, so a fake can replace Postgres in tests.",
         size=8.2, color=GREEN)
    return fig


def stateless_vs_stateful() -> plt.Figure:
    fig, ax = canvas(15, 7.5)
    heading(ax, "Stateless vs Stateful Services",
            "Where the user's session lives decides how easily you can scale, deploy, "
            "and survive a crash")
    caps(ax, 24, 82, "STATELESS: STATE LIVES IN A SHARED STORE", color=GREEN, size=9)
    caps(ax, 75, 82, "STATEFUL: STATE LIVES IN ONE INSTANCE'S MEMORY", color=RED, size=9)
    ax.plot([50, 50], [8, 85], color=LINE, linewidth=1.2)

    box(ax, 17, 66, 14, 7, "Load balancer", "any instance")
    for index in range(3):
        x = 5 + index * 14
        box(ax, x, 44, 10, 8, f"API {index + 1}", "holds nothing", face=GREEN_FACE,
            edge=GREEN)
        arrow(ax, (24, 65.3), (x + 5, 52.8), color=BLUE)
        arrow(ax, (x + 5, 43.3), (24, 32.8), color=GREY)
    box(ax, 15, 24, 18, 8, "Session store", "Redis or database", face=WHITE, edge=NAVY)
    note(ax, 24, 13, "Any instance can serve any request.\nLose one, and nobody notices.",
         color=GREEN, size=8.8)

    box(ax, 68, 66, 14, 7, "Load balancer", "sticky sessions")
    users = [("API 1", "sessions:\nAsha, Ben", GREEN_FACE, GREEN),
             ("API 2", "CRASHED, lost:\nChen, Dev", RED_FACE, RED),
             ("API 3", "sessions:\nEli, Fatima", GREEN_FACE, GREEN)]
    for index, (name, sessions, face, edge) in enumerate(users):
        x = 56 + index * 14
        box(ax, x, 40, 10, 12, name, sessions, face=face, edge=edge,
            title_color=RED if edge == RED else NAVY)
        arrow(ax, (75, 65.3), (x + 5, 52.8), color=RED if edge == RED else BLUE,
              dashed=edge == RED)
    note(ax, 75, 24, "Each user is pinned to one instance.\nIf it crashes, Chen and Dev "
         "are logged out.\nScaling in and deploying both drop sessions.",
         color=RED, size=8.8)
    return fig


def bounded_contexts() -> plt.Figure:
    fig, ax = canvas(15, 8)
    heading(ax, "Bounded Contexts: One Word, Four Models",
            "Each context keeps only the fields it needs, and one team owns it")
    contexts = [
        (3, 50, "Link management", "code, long URL, owner,\ntitle, tags, expiry",
         "links team", NAVY, PALE),
        (37, 50, "Redirect", "code -> long URL\n(nothing else)", "platform team", BLUE,
         MIST),
        (71, 50, "Analytics", "code + clicks per day,\ncountry, referrer", "data team",
         GREEN, GREEN_FACE),
        (3, 6, "Accounts & billing", "one unit of the\nplan's link quota",
         "growth team", AMBER, AMBER_FACE),
    ]
    for x, y, name, model, team, color, face in contexts:
        box(ax, x, y, 26, 28, "", face=face, edge=color)
        ax.text(x + 13, y + 24, name, ha="center", va="center", fontsize=11,
                fontweight="bold", color=NAVY)
        ax.plot([x + 3, x + 23], [y + 20, y + 20], color=LINE, linewidth=1.2)
        caps(ax, x + 13, y + 16.5, "\"LINK\" MEANS", size=7.4)
        note(ax, x + 13, y + 10.5, model, size=8.8)
        caps(ax, x + 13, y + 3.5, f"OWNED BY: {team.upper()}", color=color, size=7.4)

    arrow(ax, (29.5, 68), (36.5, 68), color=AMBER, dashed=True)
    note(ax, 33, 73.5, "LinkCreated\nLinkDeleted", size=7.6, color=AMBER)
    arrow(ax, (63.5, 68), (70.5, 68), color=AMBER, dashed=True)
    note(ax, 67, 73.5, "LinkClicked", size=7.6, color=AMBER)
    arrow(ax, (16, 49.5), (16, 34.5), color=BLUE)
    note(ax, 17.2, 42, "\"may this user create a link?\"", size=7.8, color=BLUE, ha="left")

    caps(ax, 66, 30, "HOW THE CONTEXTS TALK", size=8)
    ax.plot([45, 51], [23, 23], color=BLUE, linewidth=1.8)
    note(ax, 53, 23, "synchronous API call: the caller needs the answer now", ha="left")
    ax.plot([45, 51], [16, 16], color=AMBER, linewidth=1.8, linestyle="--")
    note(ax, 53, 16, "event: \"this happened\", consumers react in their own time",
         ha="left")
    note(ax, 45, 8, "No context reads another context's tables.", ha="left", size=8.8,
         color=NAVY)
    return fig


def database_ownership() -> plt.Figure:
    fig, ax = canvas(15, 7.5)
    heading(ax, "Shared Database vs Database per Service",
            "A shared database couples teams through its tables; separate stores "
            "trade that for copied data")
    caps(ax, 24, 82, "SHARED DATABASE", color=RED, size=9.5)
    caps(ax, 75, 82, "DATABASE PER SERVICE", color=GREEN, size=9.5)
    ax.plot([50, 50], [8, 85], color=LINE, linewidth=1.2)

    names = ("Links", "Redirect", "Analytics")
    for index, name in enumerate(names):
        x = 4 + index * 14.5
        box(ax, x, 64, 11, 8, name, "service")
    box(ax, 8, 36, 32, 13, "", face=WHITE, edge=NAVY)
    note(ax, 24, 45.5, "One database", size=10.5, color=NAVY)
    note(ax, 24, 39.5, "links table   ·   clicks table", size=8.4)
    for index in range(3):
        x = 9.5 + index * 14.5
        arrow(ax, (x, 63.3), (x + (24 - x) * 0.35, 49.8), color=GREY)
    for index, text in enumerate(("A column rename in links breaks two other teams.",
                                  "One heavy analytics query slows every redirect.",
                                  "Nobody can say who owns the schema.")):
        note(ax, 24, 27 - index * 6.5, text, size=8.6, color=RED)

    stores = [("Links DB", "relational"), ("Redirect store", "key-value"),
              ("Clicks store", "columnar")]
    for index, (name, (store, kind)) in enumerate(zip(names, stores)):
        x = 54 + index * 15
        box(ax, x, 64, 12, 8, name, "service", face=GREEN_FACE, edge=GREEN)
        box(ax, x, 40, 12, 8, store, kind, face=WHITE, edge=NAVY)
        arrow(ax, (x + 6, 63.3), (x + 6, 48.8), color=GREEN)
    for index, label in enumerate(("LinkCreated", "LinkClicked")):
        x = 54 + index * 15
        arrow(ax, (x + 12.6, 68), (x + 14.4, 68), color=AMBER, dashed=True)
        note(ax, x + 13.5, 76.5, label, size=7.4, color=AMBER)
    for index, (text, color) in enumerate((
        ("Each team changes its own schema freely.", GREEN),
        ("Each store fits its own access pattern.", GREEN),
        ("Cost: copies are briefly out of date.", AMBER),
    )):
        note(ax, 75, 27 - index * 6.5, text, size=8.6, color=color)
    return fig


def service_discovery() -> plt.Figure:
    fig, ax = canvas(15, 7.5)
    heading(ax, "Service Discovery: Finding a Healthy Instance",
            "Instances come and go, so callers look them up by name instead of "
            "hard-coding addresses")
    caps(ax, 24, 82, "CLIENT-SIDE DISCOVERY", color=NAVY, size=9.5)
    caps(ax, 75, 82, "SERVER-SIDE DISCOVERY", color=GREEN, size=9.5)
    ax.plot([50, 50], [8, 85], color=LINE, linewidth=1.2)

    box(ax, 16, 62, 16, 8, "Registry", "Eureka, Consul", face=MIST)
    box(ax, 2, 32, 12, 9, "Link API", "the caller", face=WHITE, edge=NAVY)
    for index in range(3):
        y = 50 - index * 13
        box(ax, 36, y, 11, 7, f"analytics-{index + 1}", "instance", face=GREEN_FACE,
            edge=GREEN)
        arrow(ax, (37, y + 7.5), (31 - index * 2.5, 61.5), color=GREY, dashed=True)
    note(ax, 41.5, 66, "register +\nheartbeat", size=7.5, color=GREY)
    arrow(ax, (9, 41.8), (16, 61.5), color=NAVY)
    badge(ax, 15, 50, "1")
    note(ax, 16.6, 50, "where is\nanalytics?", size=7.5, ha="left")
    arrow(ax, (14.6, 36.5), (35.5, 40.5), color=GREEN)
    badge(ax, 24, 41.5, "2", color=GREEN)
    note(ax, 24, 32, "pick one from the list,\ncall it directly", size=7.6, color=GREEN)
    note(ax, 24, 14, "The caller needs a discovery library.\nNo extra hop, but every "
         "language must implement it.", size=8.4)

    box(ax, 53, 40, 12, 9, "Link API", "calls a name", face=WHITE, edge=NAVY)
    box(ax, 70, 40, 12, 9, "analytics", "stable name / LB", face=MIST)
    arrow(ax, (65.6, 44.5), (69.4, 44.5), color=NAVY)
    for index in range(3):
        y = 56 - index * 13
        box(ax, 87, y, 11, 7, f"pod {index + 1}", "instance", face=GREEN_FACE, edge=GREEN)
        arrow(ax, (82.6, 44.5), (86.4, y + 3.5), color=GREEN)
    box(ax, 70, 64, 12, 7, "Control plane", "tracks healthy pods", face=WHITE, edge=GREY,
        title_color=GREY)
    arrow(ax, (76, 63.3), (76, 49.8), color=GREY, dashed=True)
    note(ax, 75, 14, "The platform keeps the name pointing at healthy instances.\n"
         "Examples: a Kubernetes Service, or a cloud load balancer.", size=8.4)
    return fig


def url_shortener_year_two() -> plt.Figure:
    fig, ax = canvas(16, 8.5)
    heading(ax, "URL Shortener, Year Two: Split Only Where the Needs Differ",
            "One service extracted for the redirect path; everything else stays a "
            "modular monolith")
    box(ax, 2, 44, 9, 12, "Users", "browsers", face=WHITE, edge=NAVY)
    box(ax, 15, 44, 11, 12, "Edge + LB", "routes by path")
    arrow(ax, (11.5, 50), (14.5, 50), color=NAVY)

    box(ax, 32, 66, 17, 12, "Redirect service", "stateless · 99.99%", face=MIST)
    box(ax, 64, 66, 15, 12, "Redirect store", "code -> URL, key-value", face=WHITE,
        edge=BLUE)
    arrow(ax, (49.5, 72), (63.5, 72), color=BLUE, label="read")
    arrow(ax, (26.5, 54), (31.5, 70), color=BLUE, label="GET /{code}")

    container(ax, 32, 10, 28, 40, "Link management app",
              "one deployable · 99.9%", edge=NAVY)
    for index, name in enumerate(("Links", "Accounts", "Billing", "Dashboards")):
        mx = 33.5 + (index % 2) * 13
        my = 26 - (index // 2) * 12
        box(ax, mx, my, 11, 7, name, "module", face=PALE, edge=BLUE)
    arrow(ax, (26.5, 47), (31.5, 40), color=NAVY, label="/app")
    box(ax, 64, 14, 15, 11, "Main database", "a schema per module", face=WHITE, edge=NAVY)
    arrow(ax, (60.5, 19.5), (63.5, 19.5), color=NAVY)

    box(ax, 64, 42, 15, 10, "Event bus", "durable queue", face=AMBER_FACE, edge=AMBER,
        title_color=AMBER)
    arrow(ax, (60.5, 44), (63.5, 46), color=AMBER, dashed=True)
    note(ax, 62, 39.5, "LinkCreated", size=7.4, color=AMBER)
    arrow(ax, (42, 65.3), (66, 52.8), color=AMBER, dashed=True)
    note(ax, 49, 56.5, "LinkClicked", size=7.4, color=AMBER)
    arrow(ax, (75, 52.8), (75, 65.3), color=AMBER)
    note(ax, 79, 59, "keep the\ncopy fresh", size=7.4, color=AMBER, ha="left")

    box(ax, 85, 42, 13, 10, "Click workers", "batch + aggregate", face=AMBER_FACE,
        edge=AMBER, title_color=AMBER)
    arrow(ax, (79.5, 47), (84.5, 47), color=AMBER)
    box(ax, 85, 14, 13, 11, "Analytics store", "columnar", face=WHITE, edge=AMBER,
        title_color=AMBER)
    arrow(ax, (91.5, 41.3), (91.5, 25.8), color=AMBER)
    arrow(ax, (86, 13), (60.8, 11.5), color=GREY, dashed=True)
    note(ax, 72, 8.5, "dashboards query", size=7.4, color=GREY)
    return fig


FIGURES = {
    "architecture_spectrum": architecture_spectrum,
    "layered_vs_hexagonal": layered_vs_hexagonal,
    "stateless_vs_stateful": stateless_vs_stateful,
    "bounded_contexts": bounded_contexts,
    "database_ownership": database_ownership,
    "service_discovery": service_discovery,
    "url_shortener_year_two": url_shortener_year_two,
}


if __name__ == "__main__":
    render(FIGURES, TOPIC, sys.argv[1:])
