"""Render the diagrams for Topic 04: Networking & Request Lifecycle.

Run from the system-design directory (optionally pass figure names):

    uv run --with matplotlib \
      --index-url https://pypi.ci.artifacts.walmart.com/artifactory/api/pypi/external-pypi/simple \
      --allow-insecure-host pypi.ci.artifacts.walmart.com \
      python _support/tools/plot_topic_04_figures.py
"""

from __future__ import annotations

import sys

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Rectangle

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
    SKY,
    WHITE,
    arrow,
    badge,
    box,
    canvas,
    heading,
    render,
)

TOPIC = "topic-04"


# ---------- small local helpers ------------------------------------------------

def caps(ax: plt.Axes, x: float, y: float, text: str, *, color: str = GREY,
         ha: str = "center") -> None:
    """Grey ALL-CAPS column or zone label, as used across the curriculum."""
    ax.text(x, y, text, ha=ha, va="center", fontsize=8.5, fontweight="bold",
            color=color)


def note(ax: plt.Axes, x: float, y: float, text: str, *, color: str = INK,
         size: float = 8.6, ha: str = "left") -> None:
    ax.text(x, y, text, ha=ha, va="center", fontsize=size, color=color,
            linespacing=1.45)


def two_way(ax: plt.Axes, start: tuple[float, float], end: tuple[float, float],
            color: str = GREY) -> None:
    ax.add_patch(FancyArrowPatch(start, end, arrowstyle="<|-|>", mutation_scale=12,
                                 linewidth=1.6, color=color))


def bar(ax: plt.Axes, x: float, y: float, width: float, height: float, color: str,
        label: str = "", *, text_color: str = WHITE, hatch: str = "") -> None:
    ax.add_patch(Rectangle((x, y), width, height, facecolor=color, edgecolor=WHITE,
                           linewidth=1.2, hatch=hatch))
    if label:
        ax.text(x + width / 2, y + height / 2, label, ha="center", va="center",
                fontsize=8, fontweight="bold", color=text_color)


# ---------- figures --------------------------------------------------------------

def network_layers() -> plt.Figure:
    fig, ax = canvas(15, 7.5)
    heading(ax, "The Network, One Layer at a Time",
            "Each layer does one job, and wraps the layer above it before sending")
    layers = [
        # tag, name, protocol, job, example, edge colour, face colour, wrapper label
        ("L7", "Application", "HTTP", "Says what the request means",
         "GET /summer-sale  ->  302 Found", BLUE, PALE, "HTTP request"),
        ("*", "Security", "TLS", "Keeps it secret; proves the server is real",
         "certificate for go.example.com checked", NAVY, MIST,
         "TLS: everything inside is encrypted"),
        ("L4", "Transport", "TCP / UDP", "Delivers it to the right program",
         "port 443, nothing lost or out of order", GREEN, GREEN_FACE,
         "TCP header: port 443, sequence numbers"),
        ("L3", "Network", "IP", "Moves packets between machines",
         "to 203.0.113.10, router by router", AMBER, AMBER_FACE,
         "IP header: to 203.0.113.10"),
    ]

    caps(ax, 26, 81, "THE STACK  (TOP = CLOSEST TO YOUR CODE)")
    caps(ax, 76, 81, "ONE REQUEST, WRAPPED FOR SENDING")
    ax.plot([52, 52], [4, 84], color=LINE, linewidth=1.2)

    for index, (tag, name, protocol, job, example, edge, face, _) in enumerate(layers):
        y = 63 - index * 16
        box(ax, 2, y, 6, 11, tag, face=WHITE, edge=edge,
            title_color=GREY if tag == "*" else NAVY)
        box(ax, 11, y, 14, 11, name, protocol, face=face, edge=edge)
        note(ax, 28, y + 7.3, job, size=9.2)
        note(ax, 28, y + 3.2, example, size=8.2, color=GREY)

    # The same layers as nested envelopes: the outermost wrapper is the lowest layer.
    for depth, (*_, edge, face, label) in enumerate(reversed(layers)):
        inset = depth * 3
        x, y = 54 + inset, 14 + inset
        width, height = 44 - 2 * inset, 62 - 2 * inset - depth * 3
        ax.add_patch(Rectangle((x, y), width, height, facecolor=face, edgecolor=edge,
                               linewidth=2))
        ax.text(x + 1.3, y + height - 2.6, label, va="center", fontsize=8.4,
                fontweight="bold", color=edge)
    note(ax, 76, 43, "GET /summer-sale", size=10.5, color=NAVY, ha="center")
    note(ax, 76, 37, "Host: go.example.com", size=8.6, color=GREY, ha="center")

    note(ax, 26, 6.5, "* TLS has no clean OSI layer number, so people just call it TLS.",
         size=8.2, color=GREY, ha="center")
    note(ax, 76, 7, "The receiver unwraps in reverse order. A Layer 4 load balancer\n"
         "reads only up to TCP; a Layer 7 one unwraps TLS to read HTTP.",
         size=8.2, color=GREY, ha="center")
    return fig


def request_lifecycle() -> plt.Figure:
    fig, ax = canvas(15, 7)
    heading(ax, "One Click on a Short Link: The Request Lifecycle",
            "Follow the numbers: each one is a step in the table below the picture")
    ax.add_patch(Rectangle((1, 6), 38, 76, facecolor=WHITE, edgecolor=LINE,
                           linestyle="--", linewidth=1.4))
    ax.add_patch(Rectangle((41, 6), 58, 76, facecolor="#F6F9FF", edgecolor=LINE,
                           linewidth=1.4))
    caps(ax, 20, 78, "PUBLIC INTERNET  ·  ~30 ms PER ROUND TRIP")
    caps(ax, 70, 78, "INSIDE THE DATA CENTER  ·  ~0.5 ms PER ROUND TRIP")

    def step(x: float, y: float, number: str, text: str, color: str = NAVY) -> None:
        """A numbered badge with its label to the right, in the arrow's colour."""
        badge(ax, x, y, number, color=color)
        note(ax, x + 1.8, y, text, color=color, size=8.4)

    box(ax, 4, 44, 12, 18, "Browser", "user clicks", face=WHITE, edge=NAVY)
    box(ax, 4, 11, 12, 12, "DNS resolver", "name -> IP", face=WHITE, edge=GREY,
        title_color=GREY)
    box(ax, 44, 44, 13, 18, "Load balancer", "TLS ends here")
    box(ax, 65, 44, 12, 18, "Link API", "12 servers", face=MIST)
    box(ax, 85, 60, 12, 11, "Cache", "code -> URL")
    box(ax, 85, 22, 12, 11, "Link store", "database", face=WHITE, edge=NAVY)

    # 1: DNS lookup, before anything else.
    arrow(ax, (10, 43.3), (10, 23.8), color=GREY)
    step(12.5, 33.5, "1", "find the IP address", GREY)

    # 2, 3, 7: three separate trips between the browser and the load balancer.
    for y, number, text, color, outbound in (
        (58.5, "2", "open a secure connection (TCP + TLS)", BLUE, True),
        (52.5, "3", "send GET /summer-sale", BLUE, True),
        (46.5, "7", "302 redirect back to the browser", GREEN, False),
    ):
        start, end = ((16.6, y), (43.4, y)) if outbound else ((43.4, y), (16.6, y))
        arrow(ax, start, end, color=color)
        step(18.5, y + 2.6, number, text, color)

    # 4, 5, 6: inside the data center.
    arrow(ax, (57.6, 53), (64.4, 53))
    badge(ax, 61, 57.5, "4")
    note(ax, 61, 49.3, "forward", color=NAVY, size=8.4, ha="center")
    arrow(ax, (77.6, 57), (84.4, 65))
    badge(ax, 79.3, 67, "5")
    note(ax, 77.6, 67, "look up code", color=NAVY, size=8.4, ha="right")
    arrow(ax, (77.6, 49), (84.4, 29), color=RED, dashed=True)
    step(82.3, 41.5, "6", "only on a\ncache miss", RED)
    return fig


def dns_resolution() -> plt.Figure:
    fig, ax = canvas(15, 7)
    heading(ax, "DNS: Turning go.example.com Into an IP Address",
            "A full walk takes several round trips, so every step caches the answer")
    box(ax, 3, 42, 15, 16, "Browser + OS", "check local caches", face=WHITE, edge=NAVY)
    box(ax, 30, 42, 17, 16, "Recursive resolver", "ISP or 8.8.8.8", face=MIST)
    box(ax, 66, 68, 22, 10, "Root servers", "\"ask the .com servers\"")
    box(ax, 66, 45, 22, 10, ".com TLD servers", "\"ask ns1.example.com\"")
    box(ax, 66, 22, 22, 10, "example.com authoritative",
        "\"203.0.113.10, TTL 300 s\"", face=WHITE, edge=NAVY)

    arrow(ax, (18.5, 54), (29.5, 54))
    badge(ax, 24, 59.5, "1")
    arrow(ax, (29.5, 46), (18.5, 46), color=GREEN)
    badge(ax, 24, 40.5, "8", color=GREEN)
    note(ax, 24, 35, "IP + TTL", color=GREEN, ha="center", size=8.2)

    for (start, end, first, second, bx, by) in (
        ((47.5, 56), (65.5, 72), "2", "3", 50, 67),
        ((47.5, 50), (65.5, 50), "4", "5", 55, 54.5),
        ((47.5, 44), (65.5, 28), "6", "7", 50, 31),
    ):
        two_way(ax, start, end)
        badge(ax, bx, by, first, color=GREY)
        badge(ax, bx + 3.2, by, second, color=GREY)

    caps(ax, 94, 62, "STEPS 2-7", color=GREY)
    note(ax, 94, 53, "are skipped\nwhen the resolver\nalready has the\nanswer cached:\n"
         "the usual case", ha="center", color=GREY, size=8.2)

    ax.plot([3, 97], [15, 15], color=LINE, linewidth=1)
    note(ax, 50, 8, "Cached at every step (browser, OS, resolver) for the record's TTL. "
         "A changed record can take up to one TTL to reach everyone.",
         ha="center", size=9)
    return fig


def connection_setup() -> plt.Figure:
    fig, ax = canvas(15, 8)
    heading(ax, "What a New Connection Costs, in Round Trips",
            "With TLS 1.3, a cold request needs three round trips before the answer arrives")
    client_x, server_x = 18, 52
    box(ax, client_x - 6, 78, 12, 5, "Browser", face=WHITE, edge=NAVY)
    box(ax, server_x - 7, 78, 14, 5, "Load balancer")
    for x in (client_x, server_x):
        ax.plot([x, x], [77, 17], color=LINE, linewidth=2)

    messages = [
        (74, "SYN", True, SKY),
        (69, "SYN-ACK", False, SKY),
        (62, "ACK + ClientHello", True, NAVY),
        (57, "ServerHello, certificate, Finished", False, NAVY),
        (50, "Finished + GET /summer-sale", True, GREEN),
        (45, "302 Found", False, GREEN),
        (30, "GET /spring-sale (same connection)", True, GREEN),
        (25, "302 Found", False, GREEN),
    ]
    for y, label, outbound, color in messages:
        start, end = ((client_x, y), (server_x, y - 3.5)) if outbound else \
            ((server_x, y), (client_x, y - 3.5))
        ax.add_patch(FancyArrowPatch(start, end, arrowstyle="-|>", mutation_scale=12,
                                     linewidth=1.6, color=color))
        ax.text((client_x + server_x) / 2, y - 0.6, label, ha="center", va="bottom",
                fontsize=7.8, color=color,
                bbox=dict(facecolor=WHITE, edgecolor="none", pad=0.6))

    for top, bottom, label, color in (
        (75, 65, "RTT 1\nTCP", SKY),
        (63, 53, "RTT 2\nTLS 1.3", NAVY),
        (51, 41, "RTT 3\nHTTP", GREEN),
        (31, 21, "warm\nrequest", GREEN),
    ):
        ax.plot([9, 9], [bottom, top], color=color, linewidth=3,
                solid_capstyle="round")
        ax.text(7.5, (top + bottom) / 2, label, ha="right", va="center", fontsize=8,
                fontweight="bold", color=color, linespacing=1.3)
    ax.text((client_x + server_x) / 2, 36, "connection kept open (keep-alive)",
            ha="center", fontsize=8, style="italic", color=GREY)

    caps(ax, 79, 80, "ROUND TRIPS BEFORE THE ANSWER")
    summary = [
        ("Cold, TLS 1.3: 3", "TCP + TLS + HTTP", WHITE, NAVY),
        ("Cold, TLS 1.2: 4", "its handshake needs two round trips", WHITE, GREY),
        ("Cold, HTTP/3 (QUIC): 2", "transport and TLS share one round trip", PALE, BLUE),
        ("Warm (reused): 1", "only the HTTP request itself", GREEN_FACE, GREEN),
    ]
    for index, (title, subtitle, face, edge) in enumerate(summary):
        box(ax, 63, 64 - index * 14, 32, 9, title, subtitle, face=face, edge=edge,
            title_color=NAVY if edge != GREEN else GREEN)
    note(ax, 79, 12, "At 30 ms per round trip: cold ≈ 90 ms, warm ≈ 30 ms",
         ha="center", size=9, color=NAVY)
    return fig


def http_versions() -> plt.Figure:
    fig, ax = canvas(15, 7.5)
    heading(ax, "HTTP/1.1 vs HTTP/2 vs HTTP/3",
            "Three requests (A, B, C) to one server, and what one lost packet does")
    colors = {"A": BLUE, "B": GREEN, "C": AMBER}
    caps(ax, 46, 82, "ONE CONNECTION, OVER TIME  →")
    caps(ax, 87, 82, "WHAT TO REMEMBER")

    def lane(y: float, height: float = 6) -> None:
        ax.add_patch(Rectangle((20, y), 52, height, facecolor=WHITE, edgecolor=LINE,
                               linewidth=1.2))

    def lost(x: float, y: float, size: float = 1.1) -> None:
        """Draw a red X marking a lost packet (two strokes, no glyph needed)."""
        dy = size * 15 / 7.5          # keep the X square on this aspect ratio
        for sign in (1, -1):
            ax.plot([x - size, x + size], [y - sign * dy, y + sign * dy],
                    color=RED, linewidth=2.6, solid_capstyle="round")

    # HTTP/1.1: one request at a time.
    box(ax, 2, 64, 13, 11, "HTTP/1.1", "1997", face=WHITE, edge=GREY)
    lane(66.5)
    for index, name in enumerate("ABC"):
        bar(ax, 21 + index * 16.5, 67, 15.5, 5, colors[name], f"request {name}")
    note(ax, 76, 72.5, "One request at a time per connection.")
    note(ax, 76, 67.5, "A slow A delays B and C, so browsers\nopen about 6 connections per host.",
         size=8.2, color=GREY)

    # HTTP/2: frames interleaved on one TCP connection; one loss stalls all.
    box(ax, 2, 38, 13, 11, "HTTP/2", "2015, over TCP", face=PALE, edge=BLUE)
    lane(40.5)
    sequence = "ABCABCABCABC"
    for index, name in enumerate(sequence):
        stalled = index > 3
        bar(ax, 21 + index * 4.25, 41, 3.9, 5, DEAD if stalled else colors[name],
            name, text_color=GREY if stalled else WHITE)
    lost(21 + 4 * 4.25 + 1.95, 49.5)
    note(ax, 76, 46.5, "Many streams share one TCP connection.")
    note(ax, 76, 41.5, "TCP delivers bytes in order, so one lost\npacket stalls every stream.",
         size=8.2, color=GREY)

    # HTTP/3: QUIC streams recover independently.
    box(ax, 2, 12, 13, 11, "HTTP/3", "2022, QUIC over UDP", face=MIST, edge=NAVY)
    for row, name in enumerate("ABC"):
        y = 22 - row * 6
        lane(y, 5)
        for index in range(4):
            stalled = name == "B" and index > 0
            bar(ax, 21 + index * 12.5, y + 0.5, 11.8, 4,
                DEAD if stalled else colors[name], name,
                text_color=GREY if stalled else WHITE)
    lost(21 + 12.5 + 2.2, 18.5, size=0.7)
    note(ax, 76, 20, "Each stream recovers on its own.")
    note(ax, 76, 13.5, "Only B waits. QUIC also combines the\ntransport and TLS handshakes, and\n"
         "survives a Wi-Fi to mobile switch.", size=8.2, color=GREY)
    ax.add_patch(Rectangle((52, 2), 2.5, 2.5, facecolor=DEAD, edgecolor=LINE))
    note(ax, 55.5, 3.3, "waiting for the lost packet to be resent", size=8, color=GREY)
    lost(48.5, 3.3, size=0.7)
    return fig


def timeout_budget() -> plt.Figure:
    fig, ax = canvas(15, 7.5)
    heading(ax, "Timeout Budgets: Inner Timeouts Must End First",
            "Every call gets a timeout, and each one is shorter than its caller's")
    origin, scale = 30, 60 / 600     # 600 ms of time across 60 units

    def span(start_ms: float, length_ms: float, y: float, color: str, label: str,
             *, text_color: str = WHITE) -> None:
        bar(ax, origin + start_ms * scale, y, length_ms * scale, 5, color, label,
            text_color=text_color)

    caps(ax, 4, 80, "GOOD", color=GREEN, ha="left")
    rows = [(73, "Load balancer -> API"), (65, "API request deadline"), (57, "Calls inside the API")]
    for y, label in rows:
        note(ax, origin - 1.5, y + 2.5, label, ha="right", size=8.8)
    span(0, 500, 73, NAVY, "500 ms")
    span(0, 300, 65, BLUE, "300 ms")
    span(0, 20, 57, AMBER, "")
    span(20, 100, 57, GREEN, "DB 100 ms")
    span(120, 100, 57, SKY, "retry 100 ms")
    span(220, 80, 57, DEAD, "spare", text_color=GREY)
    note(ax, origin + 0.2, 54.5, "cache 20 ms", size=7.6, color=AMBER)
    note(ax, 93, 65, "The API answers\n(or fails cleanly)\nbefore the load\nbalancer gives up.",
         size=8.4, color=GREEN)

    ax.plot([3, 97], [47, 47], color=LINE, linewidth=1)

    caps(ax, 4, 41, "BAD", color=RED, ha="left")
    note(ax, origin - 1.5, 36.5, "Load balancer -> API", ha="right", size=8.8)
    note(ax, origin - 1.5, 28.5, "API database call", ha="right", size=8.8)
    span(0, 500, 34, NAVY, "500 ms")
    bar(ax, origin, 26, 62, 5, RED_FACE)
    ax.text(origin + 31, 28.5, "DB call with a 30-second timeout  →", ha="center",
            va="center", fontsize=8, fontweight="bold", color=RED)
    ax.plot([origin + 50, origin + 50], [22, 42], color=RED, linewidth=1.6, linestyle="--")
    note(ax, origin + 50.8, 21, "504 sent to the user at 500 ms", size=8, color=RED)
    note(ax, 50, 12, "The user already has an error, but the API thread and its database "
         "connection stay busy for 30 seconds.\nUnder load, these abandoned calls fill "
         "every pool and take the whole service down.", ha="center", size=8.8)

    for ms in (0, 100, 200, 300, 400, 500, 600):
        ax.text(origin + ms * scale, 50.5, f"{ms}", ha="center", fontsize=7, color=GREY)
    return fig


def latency_budget() -> plt.Figure:
    fig, ax = canvas(15, 6.5)
    heading(ax, "One Redirect: Cold vs Warm Latency",
            "The user is about 30 ms (one round trip) from the data center")
    origin, scale = 30, 0.48        # milliseconds -> canvas units
    parts = {
        "DNS": GREY, "TCP": SKY, "TLS": NAVY, "HTTP": BLUE,
        "edge -> origin": AMBER, "server": GREEN,
    }
    rows = [
        (62, "Cold connection", [("DNS", 30), ("TCP", 30), ("TLS", 30), ("HTTP", 30),
                                 ("server", 3)]),
        (42, "Cold, TLS ends at a\nnearby edge (5 ms away)",
         [("DNS", 5), ("TCP", 5), ("TLS", 5), ("HTTP", 5), ("edge -> origin", 30),
          ("server", 3)]),
        (22, "Warm (reused) connection", [("HTTP", 30), ("server", 3)]),
    ]
    for y, label, segments in rows:
        note(ax, origin - 1.5, y + 4, label, ha="right", size=9)
        x = origin
        for name, ms in segments:
            width = ms * scale
            bar(ax, x, y, width, 8, parts[name], name if width > 7 else "")
            x += width
        total = sum(ms for _, ms in segments)
        ax.text(x + 1.2, y + 4, f"{total} ms", va="center", fontsize=10,
                fontweight="bold", color=NAVY)
    for index, (name, color) in enumerate(parts.items()):
        x = 14 + index * 13.5
        ax.add_patch(Rectangle((x, 79), 2.4, 3.5, facecolor=color, edgecolor=WHITE))
        note(ax, x + 3.2, 80.8, name, size=8.4)
    note(ax, 50, 9, "Your code is the 3 ms green sliver. Reusing connections and ending "
         "TLS close to the user save far more than tuning the server.",
         ha="center", size=9, color=NAVY)
    return fig


FIGURES = {
    "network_layers": network_layers,
    "request_lifecycle": request_lifecycle,
    "dns_resolution": dns_resolution,
    "connection_setup": connection_setup,
    "http_versions": http_versions,
    "timeout_budget": timeout_budget,
    "latency_budget": latency_budget,
}


if __name__ == "__main__":
    render(FIGURES, TOPIC, sys.argv[1:])
