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
    DEAD,
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


def fields(ax: plt.Axes, cx: float, top: float, items: list[str], *,
           columns: int = 1, gap: float = 4.2, col_width: float = 11) -> float:
    """A bulleted list of model fields, one per line, split into columns.

    Returns the y just below the last row, so callers can place text under it.
    """
    rows = math.ceil(len(items) / columns)
    left = cx - col_width * columns / 2 + 1.5
    for index, item in enumerate(items):
        col, row = divmod(index, rows)
        ax.text(left + col * col_width, top - row * gap, f"• {item}", ha="left",
                va="center", fontsize=8.8, color=INK)
    return top - rows * gap


def bounded_contexts() -> plt.Figure:
    fig, ax = canvas(15, 9)
    heading(ax, "Bounded Contexts: One Word, Four Meanings",
            "Each context keeps only the fields it needs, and only those fields cross "
            "its boundary")

    contexts = [
        (2, 46, 32, "Link management", "links team", NAVY, PALE,
         ["code", "long URL", "owner", "title", "tags", "expiry"], 2, ""),
        (38, 46, 32, "Redirect", "platform team", BLUE, MIST,
         ["code", "long URL"], 1, "all a redirect needs"),
        (74, 46, 32, "Analytics", "data team", GREEN, GREEN_FACE,
         ["code", "clicks per day", "country", "referrer"], 2, ""),
        (2, 4, 30, "Accounts & billing", "growth team", AMBER, AMBER_FACE,
         ["1 unit of the plan's quota"], 1, "URL and title don't matter here"),
    ]
    for x, y, height, name, team, color, face, items, columns, aside in contexts:
        top = y + height
        box(ax, x, y, 24, height, "", face=face, edge=color)
        ax.text(x + 12, top - 4, name, ha="center", va="center", fontsize=11,
                fontweight="bold", color=NAVY)
        ax.plot([x + 3, x + 21], [top - 7.5, top - 7.5], color=LINE, linewidth=1.2)
        caps(ax, x + 12, top - 11, "HERE, \"LINK\" MEANS", size=7.4)
        below = fields(ax, x + 12, top - 15.5, items, columns=columns,
                       col_width=11 if columns == 2 else 18)
        if aside:
            note(ax, x + 12, below + 0.5, f"({aside})", size=7.8, color=GREY)
        caps(ax, x + 12, y + 3.5, f"OWNED BY: {team.upper()}", color=color, size=7.4)

    # Events: the arrow says what happened, the text under it says what data travels.
    for x_start, name, payload in [
        (26.5, "LinkCreated\nLinkDeleted", "carries:\ncode, long URL"),
        (62.5, "LinkClicked", "carries: code, time,\ncountry, referrer"),
    ]:
        arrow(ax, (x_start, 62), (x_start + 11, 62), color=AMBER, dashed=True)
        ax.text(x_start + 5.5, 67.5, name, ha="center", va="center", fontsize=7.8,
                fontweight="bold", color=AMBER, linespacing=1.4)
        note(ax, x_start + 5.5, 56.5, payload, size=7.6, color=AMBER)

    # A synchronous call: a question goes down, an answer comes back up.
    arrow(ax, (10, 45.5), (10, 34.5), color=BLUE)
    arrow(ax, (14, 34.5), (14, 45.5), color=BLUE)
    note(ax, 16.5, 42, "↓ asks: may this owner create a link?", size=7.8, color=BLUE,
         ha="left")
    note(ax, 16.5, 38, "↑ answers: yes, 37 of 50 used", size=7.8, color=BLUE,
         ha="left")

    # The alternative these contexts replace.
    box(ax, 32, 4, 36, 30, "", face=RED_FACE, edge=RED)
    caps(ax, 50, 30, "WITHOUT BOUNDED CONTEXTS", color=RED, size=8)
    ax.text(50, 25.5, "one shared Link class", ha="center", va="center",
            fontsize=10.5, fontweight="bold", color=NAVY)
    note(ax, 50, 18.5, "code, long URL, owner, title, tags, expiry,\n"
                       "clicks per day, country, referrer, quota unit, ...", size=8.2)
    note(ax, 50, 9.5, "Every team edits it, and no team owns it.\n"
                      "An analytics change can break redirects.", size=8.4, color=RED)

    caps(ax, 74, 30, "HOW THE CONTEXTS TALK", ha="left", size=8)
    ax.plot([74, 79], [23.5, 23.5], color=BLUE, linewidth=1.8)
    note(ax, 81, 23.5, "call: the caller waits\nfor the answer", ha="left", size=8.2)
    ax.plot([74, 79], [15.5, 15.5], color=AMBER, linewidth=1.8, linestyle="--")
    note(ax, 81, 15.5, "event: \"this happened\";\nothers react in their own time",
         ha="left", size=8.2)
    note(ax, 74, 7.5, "No context reads another\ncontext's tables.", ha="left", size=8.4,
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


def _instance_row(ax: plt.Axes, left: float, *, upward: bool) -> list[float]:
    """Draw analytics-1..3 along the bottom (the third one crashed) and link each
    to the box above. Upward = heartbeats to a registry; downward = traffic from
    a load balancer. Returns the x centre of each instance."""
    centres = []
    for index in range(3):
        x = left + index * 10
        centre = x + 4
        centres.append(centre)
        crashed = index == 2
        box(ax, x, 21, 8, 9, f"analytics-{index + 1}", "crashed" if crashed else "healthy",
            face=DEAD if crashed else GREEN_FACE, edge=GREY if crashed else GREEN,
            title_color=GREY if crashed else NAVY)
        if crashed:
            ax.plot([centre, centre], [31, 63], color=LINE, linewidth=1.6, linestyle="--")
            ax.plot(centre, 47, marker="X", markersize=13, color=RED)
        elif upward:
            arrow(ax, (centre, 30.8), (centre, 63.2), color=GREY, dashed=True)
        else:
            arrow(ax, (centre, 63.2), (centre, 30.8), color=GREEN)
    return centres


def service_discovery() -> plt.Figure:
    fig, ax = canvas(15, 7.5)
    heading(ax, "Service Discovery: Finding a Healthy Instance",
            "Instances come and go, so callers look them up by name instead of "
            "hard-coding addresses")
    caps(ax, 25, 81, "CLIENT-SIDE DISCOVERY: THE CALLER LOOKS IT UP", color=NAVY, size=9.5)
    caps(ax, 76, 81, "SERVER-SIDE DISCOVERY: THE PLATFORM LOOKS IT UP", color=GREEN,
         size=9.5)
    ax.plot([50, 50], [6, 84], color=LINE, linewidth=1.2)

    # Client side: instances report to a registry; the caller asks, then calls directly.
    box(ax, 20, 64, 28, 9, "Registry", "keeps the list of healthy instances", face=MIST)
    box(ax, 2, 40, 11, 9, "Link API", "the caller", face=WHITE, edge=NAVY)
    first, second, _ = _instance_row(ax, 20, upward=True)
    badge(ax, (first + second) / 2, 54, "1", color=GREY)
    note(ax, (first + second) / 2, 46, "register and\nsend heartbeats", size=7.5, color=GREY)
    arrow(ax, (7.5, 49.8), (19.4, 68.5), color=NAVY)
    badge(ax, 13.5, 59, "2")
    note(ax, 11.6, 59, "ask where\nanalytics is", size=7.5, ha="right")
    arrow(ax, (13.6, 42), (19.4, 26), color=GREEN)
    badge(ax, 16.5, 34, "3", color=GREEN)
    note(ax, 14.6, 32, "call one\ndirectly", size=7.5, color=GREEN, ha="right")
    note(ax, 25, 11, "The caller uses a discovery library, such as Eureka or Consul.\n"
         "There is no extra network hop, but every language needs that library.", size=8.4)

    # Server side: the caller only knows the name; the load balancer picks an instance.
    box(ax, 71, 64, 28, 9, "Load balancer", "behind the name \"analytics\"", face=MIST)
    box(ax, 53, 40, 11, 9, "Link API", "the caller", face=WHITE, edge=NAVY)
    first, second, _ = _instance_row(ax, 71, upward=False)
    arrow(ax, (58.5, 49.8), (70.4, 68.5), color=NAVY)
    badge(ax, 64.5, 59, "1")
    note(ax, 62.6, 59, "call the name\n\"analytics\"", size=7.5, ha="right")
    badge(ax, (first + second) / 2, 54, "2", color=GREEN)
    note(ax, (first + second) / 2, 46, "forward to a\nhealthy instance", size=7.5,
         color=GREEN)
    note(ax, 76, 11, "The platform does the lookup, for example a Kubernetes Service.\n"
         "The caller stays simple, at the cost of one small extra network hop.", size=8.4)
    return fig


def _zone(ax: plt.Axes, x: float, y: float, width: float, height: float,
          title: str, detail: str, *, color: str) -> None:
    """A dashed box around one part that deploys on its own, labelled top-left
    with its name and the need that justifies it."""
    outline(ax, x, y, width, height, color=color)
    caps(ax, x + 1.5, y + height - 2.5, title, color=color, ha="left", size=8.8)
    note(ax, x + 1.5, y + height - 6, detail, ha="left", size=8.2)


def url_shortener_year_two() -> plt.Figure:
    """Two numbered trails: 1-4 (navy) create a link, A-D (green) follow one."""
    fig, ax = canvas(16, 10)
    heading(ax, "URL Shortener, Year Two: Split Only Where the Needs Differ",
            "Follow 1-4 to see a link being created, and A-D to see a short link "
            "being followed")

    def step(x: float, y: float, text: str) -> None:
        badge(ax, x, y, text, color=GREEN if text.isalpha() else NAVY, size=8)

    # Users reach a load balancer, which sends each request on by its URL path.
    box(ax, 1, 46, 8, 10, "Users", "browsers", face=WHITE, edge=NAVY)
    box(ax, 13, 46, 11, 10, "Load balancer", "routes by URL path")
    arrow(ax, (9.5, 51), (12.5, 51), color=NAVY)
    arrow(ax, (24.8, 54), (30.4, 68.5), color=BLUE)
    step(26.5, 58.4, "A")
    note(ax, 25.8, 66, "GET /abc123\n~20,000 requests/s", size=7.8, color=BLUE, ha="right")
    arrow(ax, (24.8, 47), (30.4, 28.5), color=NAVY)
    step(27.6, 37.8, "1")
    note(ax, 25.8, 33, "POST /app/links\nall /app pages:\n~250 requests/s", size=7.8,
         color=NAVY, ha="right")

    # The redirect path, extracted because it alone needs 99.99%.
    _zone(ax, 29, 62, 35, 22, "REDIRECT PATH", "its own service · needs 99.99%",
          color=BLUE)
    box(ax, 31, 64.5, 13, 9, "Redirect service", "replies with a 302", face=MIST)
    box(ax, 50, 64.5, 12, 9, "Redirect store", "short code → long URL", face=WHITE,
        edge=BLUE)
    arrow(ax, (44.6, 71.5), (49.4, 71.5), color=BLUE)
    step(47, 71.5, "B")
    arrow(ax, (44.6, 66.5), (49.4, 66.5), color=BLUE)
    step(47, 66.5, "4")

    # The event bus sits between the parts, so none of them waits on another.
    box(ax, 33, 46, 24, 9, "Event bus", "holds each event until it is read",
        face=AMBER_FACE, edge=AMBER, title_color=AMBER)
    arrow(ax, (34.5, 63.8), (34.5, 55.7), color=AMBER, dashed=True)
    step(34.5, 59.8, "C")
    note(ax, 32.8, 59.8, "LinkClicked", size=7.4, color=AMBER, ha="right")
    arrow(ax, (41, 55.7), (41, 63.8), color=AMBER, dashed=True)
    step(41, 59.8, "4")
    note(ax, 42.8, 59.8, "LinkCreated", size=7.4, color=AMBER, ha="left")

    # Everything else stays one modular monolith with one database.
    _zone(ax, 29, 2, 35, 41, "LINK MANAGEMENT APP",
          "one modular monolith · needs 99.9%", color=NAVY)
    box(ax, 31, 24, 13, 8, "Links module", "validates the link", face=MIST)
    box(ax, 50, 24, 12, 8, "Main database", "link + outbox row", face=WHITE, edge=NAVY)
    arrow(ax, (44.6, 28), (49.4, 28), color=NAVY)
    step(47, 32, "2")
    arrow(ax, (56, 32.7), (56, 45.3), color=AMBER, dashed=True)
    step(56, 39, "3")
    note(ax, 57.6, 39, "outbox relay\npublishes", size=7.4, color=AMBER, ha="left")
    for index, name in enumerate(("Accounts", "Billing", "Dashboards")):
        box(ax, 31 + index * 11, 6, 9, 6, name, face=PALE, edge=BLUE)
    note(ax, 46.5, 16.5, "other modules, each with its own schema", size=7.4, color=GREY)

    # Analytics, separate because recording clicks is background work.
    _zone(ax, 70.5, 3, 28.5, 81, "ANALYTICS", "runs separately, in the background",
          color=AMBER)
    box(ax, 72, 46, 24, 9, "Click workers", "count clicks in batches", face=AMBER_FACE,
        edge=AMBER, title_color=AMBER)
    arrow(ax, (57.6, 50.5), (71.4, 50.5), color=AMBER, dashed=True)
    step(64.5, 50.5, "D")
    note(ax, 64.5, 54, "LinkClicked", size=7.4, color=AMBER)
    box(ax, 72, 6, 24, 9, "Analytics store", "click totals per link", face=WHITE,
        edge=AMBER, title_color=AMBER)
    arrow(ax, (84, 45.3), (84, 15.7), color=AMBER)
    note(ax, 85.5, 30, "save click\ntotals", size=7.4, color=AMBER, ha="left")
    arrow(ax, (62.6, 9), (71.4, 10), color=BLUE)
    note(ax, 67.2, 15, "asks the\nanalytics API\nfor totals", size=7.4, color=BLUE)

    # Legend.
    caps(ax, 1.5, 27, "HOW TO READ IT", ha="left", size=8)
    ax.plot([1.5, 5.5], [22.5, 22.5], color=BLUE, linewidth=1.8)
    note(ax, 6.5, 22.5, "call: the caller\nwaits for the answer", ha="left", size=8)
    ax.plot([1.5, 5.5], [16.5, 16.5], color=AMBER, linewidth=1.8, linestyle="--")
    note(ax, 6.5, 16.5, "event: sent now,\nread later", ha="left", size=8)
    outline(ax, 1.5, 9, 4, 3.5)
    note(ax, 6.5, 10.75, "dashed box: one part\nthat deploys on its own", ha="left", size=8)
    step(2.5, 4, "1")
    step(4.5, 4, "A")
    note(ax, 6.5, 4, "1-4 create a link,\nA-D follow one", ha="left", size=8)
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
