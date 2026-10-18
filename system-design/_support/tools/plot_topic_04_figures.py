"""Render the request-lifecycle, DNS, connection, HTTP, and timeout diagrams for topic 04.

Run from the system-design directory:

    uv run --with matplotlib \
      --index-url https://pypi.ci.artifacts.walmart.com/artifactory/api/pypi/external-pypi/simple \
      --allow-insecure-host pypi.ci.artifacts.walmart.com \
      python _support/tools/plot_topic_04_figures.py

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
    GREEN,
    GREY,
    INK,
    LINE,
    MIST,
    NAVY,
    PALE,
    RED,
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


def side_note(ax: plt.Axes, x: float, y: float, title: str, body: str,
              color: str = NAVY) -> None:
    ax.text(x, y, title, fontsize=8, fontweight="bold", color=color)
    ax.text(x, y - 5, body, fontsize=8, color=INK, va="top", linespacing=1.45)


def request_lifecycle() -> plt.Figure:
    fig, ax = canvas(15, 7)
    heading(ax, "One Click on a Short Link: The Request Lifecycle",
            "Steps 1-3 happen before the request ever reaches your code")
    box(ax, 3, 56, 12, 16, "Browser", "clicks the link", face=WHITE, edge=NAVY)
    box(ax, 3, 16, 12, 16, "DNS resolver", "name -> IP address", face=WHITE, edge=GREY,
        title_color=GREY)
    box(ax, 24, 56, 15, 16, "Load balancer", "TLS ends here")
    box(ax, 48, 56, 13, 16, "Link API", "stateless", face=MIST)
    box(ax, 70, 66, 12, 13, "Cache", "code -> URL")
    box(ax, 70, 38, 12, 13, "Link store", "on a miss", face=WHITE, edge=NAVY)
    arrow(ax, (9, 55.5), (9, 32.5), color=GREY)
    badge(ax, 11.5, 44, "1", color=GREY)
    ax.text(13.5, 44, "resolve name", fontsize=8, color=GREY, va="center")
    arrow(ax, (15.5, 67), (23.5, 67))
    arrow(ax, (23.5, 60), (15.5, 60), color=GREEN)
    for x, label in ((17, "2"), (19.5, "3"), (22, "4")):
        badge(ax, x, 74.5, label)
    ax.text(19.5, 79, "TCP / TLS / GET", ha="center", fontsize=7.5, color=BLUE)
    badge(ax, 19.5, 53.5, "7", color=GREEN)
    ax.text(19.5, 49, "302 Found", ha="center", fontsize=7.5, color=GREEN)
    arrow(ax, (39.5, 64), (47.5, 64), label="pooled HTTP")
    arrow(ax, (61.5, 66), (69.5, 72.5))
    badge(ax, 65.5, 74, "5")
    arrow(ax, (61.5, 60), (69.5, 44.5), color=RED)
    badge(ax, 65.5, 47, "6", color=RED)
    side_note(ax, 86, 74, "NETWORK", "steps 1-4 and 7:\nround trips to\nthe user", BLUE)
    side_note(ax, 86, 50, "YOUR CODE", "steps 5-6:\na few ms in\nthe data center", GREEN)
    return fig


def dns_resolution() -> plt.Figure:
    fig, ax = canvas(14, 6.6)
    heading(ax, "DNS Resolution: Usually a Cache Hit, Occasionally a Walk",
            "Every layer caches the answer for the record's TTL")
    box(ax, 3, 42, 14, 16, "Browser + OS", "local cache", face=WHITE, edge=NAVY)
    box(ax, 29, 42, 16, 16, "Recursive resolver", "ISP or public, cached", face=MIST)
    box(ax, 62, 68, 18, 12, "Root servers", "who runs .com?")
    box(ax, 62, 44, 18, 12, "TLD servers (.com)", "who runs example.com?")
    box(ax, 62, 20, 18, 12, "Authoritative", "go.example.com = IP")
    arrow(ax, (17.5, 53), (28.5, 53), label="1 query")
    arrow(ax, (28.5, 46), (17.5, 46), color=GREEN, label="5 IP + TTL")
    arrow(ax, (45.5, 55), (61.5, 73), color=GREY, label="2")
    arrow(ax, (45.5, 50), (61.5, 50), color=GREY, label="3")
    arrow(ax, (45.5, 45), (61.5, 27), color=GREY, label="4")
    side_note(ax, 85, 72, "WARM", "answered from\na cache: ~0 ms")
    side_note(ax, 85, 50, "COLD", "steps 2-4 run:\n20-120 ms")
    side_note(ax, 85, 28, "TTL", "how long every\nlayer may cache", AMBER)
    return fig


def message(ax: plt.Axes, y: float, text: str, *, to_server: bool,
            color: str = BLUE) -> None:
    left, right = (22, 62) if to_server else (62, 22)
    arrow(ax, (left, y), (right, y - 4), color=color)
    ax.text(42, y + 0.5, text, ha="center", fontsize=8, color=color,
            bbox=dict(facecolor=WHITE, edgecolor="none", pad=1))


def connection_setup() -> plt.Figure:
    fig, ax = canvas(14, 7.6)
    heading(ax, "A New Connection Costs Round Trips Before Any Work Happens",
            "TCP, then TLS 1.3, then the actual request: three round trips on a cold start")
    for x, name in ((22, "Browser"), (62, "Load balancer")):
        ax.text(x, 82, name, ha="center", fontsize=10, fontweight="bold", color=NAVY)
        ax.plot([x, x], [79, 8], color=LINE, linewidth=2)
    phases = [
        (75, "TCP: 1 round trip", "SYN", "SYN-ACK", NAVY),
        (55, "TLS 1.3: 1 round trip", "ClientHello", "ServerHello + certificate", BLUE),
        (35, "HTTP: 1 round trip", "GET /x7Kp2Qa", "302 Found", GREEN),
    ]
    for top, label, request, reply, color in phases:
        message(ax, top, request, to_server=True, color=color)
        message(ax, top - 8, reply, to_server=False, color=color)
        ax.plot([16, 16], [top, top - 12], color=color, linewidth=3)
        ax.text(15, top - 6, label, ha="right", va="center", fontsize=8.2,
                fontweight="bold", color=color)
    side_note(ax, 70, 70, "COLD CONNECTION", "3 round trips before\nthe answer arrives")
    side_note(ax, 70, 46, "REUSED CONNECTION", "keep-alive skips TCP and\nTLS: 1 round trip", GREEN)
    side_note(ax, 70, 22, "TLS 1.2", "needs 2 round trips,\nso a cold start costs 4", AMBER)
    return fig


def latency_budget() -> plt.Figure:
    fig, ax = canvas(14, 6)
    heading(ax, "Cold vs Warm: Where One Redirect's Time Goes",
            "User 40 ms away (round trip); the server's own work is only 5 ms")
    left, scale = 24, 0.34
    segments = {"DNS": (GREY, "#E3E8F1"), "TCP": (NAVY, MIST), "TLS": (BLUE, PALE),
                "HTTP": (GREEN, "#E9F7EF"), "server": (AMBER, AMBER_FACE)}
    rows = [
        ("Cold, TLS 1.2", [("DNS", 30), ("TCP", 40), ("TLS", 80), ("HTTP", 40), ("server", 5)]),
        ("Cold, TLS 1.3", [("DNS", 30), ("TCP", 40), ("TLS", 40), ("HTTP", 40), ("server", 5)]),
        ("Warm, reused", [("HTTP", 40), ("server", 5)]),
    ]
    for index, (label, parts) in enumerate(rows):
        y = 64 - index * 17
        ax.text(left - 2, y + 4, label, ha="right", va="center", fontsize=9,
                fontweight="bold", color=NAVY)
        x = left
        for name, ms in parts:
            edge, face = segments[name]
            ax.add_patch(Rectangle((x, y), ms * scale, 8, facecolor=face,
                                   edgecolor=edge, linewidth=1.4))
            if ms >= 30:
                ax.text(x + ms * scale / 2, y + 4, f"{name} {ms}", ha="center",
                        va="center", fontsize=7.5, color=INK)
            x += ms * scale
        total = sum(ms for _, ms in parts)
        ax.text(x + 1.5, y + 4, f"{total} ms", va="center", fontsize=9,
                fontweight="bold", color=INK)
    target_x = left + 100 * scale
    ax.plot([target_x, target_x], [26, 78], color=RED, linewidth=1.5, linestyle="--")
    ax.text(target_x, 81, "100 ms target", ha="center", fontsize=8, color=RED)
    ax.text(left, 16, "Amber = server work (5 ms). Everything else is the network.",
            fontsize=8.5, color=INK)
    return fig


def lane(ax: plt.Axes, y: float, start: float, end: float, color: str, text: str) -> None:
    ax.add_patch(Rectangle((start, y), end - start, 3.6, facecolor=color,
                           edgecolor=WHITE, linewidth=1))
    ax.text((start + end) / 2, y + 1.8, text, ha="center", va="center",
            fontsize=7, color=WHITE, fontweight="bold")


def stall(ax: plt.Axes, y: float, start: float, end: float) -> None:
    ax.add_patch(Rectangle((start, y), end - start, 3.6, facecolor="#E6E9EF",
                           edgecolor=GREY, linewidth=0.8, hatch="///"))


def http_versions() -> plt.Figure:
    fig, ax = canvas(15, 7.4)
    heading(ax, "HTTP/1.1 vs HTTP/2 vs HTTP/3: Three Requests, One Lost Packet",
            "Grey hatching = waiting. Red mark = a lost packet being re-sent")
    labels = [
        (70, "HTTP/1.1", "one request at a time\non a connection"),
        (45, "HTTP/2", "many streams on\none TCP connection"),
        (20, "HTTP/3", "independent streams\nover QUIC (UDP)"),
    ]
    for y, title, sub in labels:
        ax.text(3, y + 7, title, fontsize=10.5, fontweight="bold", color=NAVY)
        ax.text(3, y + 3, sub, fontsize=7.8, color=INK, va="top", linespacing=1.35)
    lane(ax, 74, 24, 40, NAVY, "A")
    lane(ax, 74, 40, 56, BLUE, "B")
    lane(ax, 74, 56, 72, SKY, "C")
    for row, (y, lost_all) in enumerate(((45, True), (20, False))):
        for offset, (name, color) in enumerate((("A", NAVY), ("B", BLUE), ("C", SKY))):
            sub_y = y + 9 - offset * 4.6
            stalled = lost_all or name == "B"
            lane(ax, sub_y, 24, 36, color, name)
            if stalled:
                stall(ax, sub_y, 36, 48)
                lane(ax, sub_y, 48, 58, color, name)
            else:
                lane(ax, sub_y, 36, 46, color, name)
        ax.plot(36, y + 7.4 if row else y + 5, marker="X", markersize=11, color=RED)
    notes = [
        (76, "C waits for A and B, so browsers open\n~6 connections per site to compensate"),
        (51, "one lost TCP packet stalls every stream:\nTCP head-of-line blocking"),
        (26, "a lost packet stalls only its own stream;\nA and C finish early"),
    ]
    for y, text in notes:
        ax.text(76, y, text, fontsize=8, color=INK, va="center", linespacing=1.4)
    return fig


def nested(ax: plt.Axes, x: float, y: float, w: float, h: float, title: str,
           edge: str, face: str) -> None:
    box(ax, x, y, w, h, "", face=face, edge=edge)
    ax.text(x + 1.2, y + h - 3, title, fontsize=9, fontweight="bold", color=edge, va="top")


def timeout_budget() -> plt.Figure:
    fig, ax = canvas(14, 6.6)
    heading(ax, "Timeout Budgets Nest: Every Callee Gives Up Before Its Caller",
            "Not to scale. Normal times in brackets; timeouts are the ceilings")
    nested(ax, 3, 12, 94, 66, "Load balancer: 1,000 ms", NAVY, WHITE)
    nested(ax, 7, 16, 70, 50, "Link API request deadline: 200 ms", BLUE, PALE)
    box(ax, 11, 29, 14, 18, "Cache", "10 ms  (~1 ms)", face=WHITE, edge=GREEN, title_color=GREEN)
    box(ax, 29, 29, 14, 18, "Link store", "50 ms  (~5 ms)", face=WHITE, edge=GREEN,
        title_color=GREEN)
    box(ax, 47, 29, 14, 18, "One retry", "50 ms", face=AMBER_FACE, edge=AMBER,
        title_color=AMBER)
    arrow(ax, (25.5, 38), (28.5, 38), color=GREEN)
    arrow(ax, (43.5, 38), (46.5, 38), color=AMBER)
    ax.text(69, 38, "slack\n90 ms", ha="center", va="center", fontsize=8.5, color=GREY)
    ax.text(87, 48, "10 + 50 + 50\n= 110 ms\nfits inside 200",
            ha="center", va="center", fontsize=9, color=NAVY, fontweight="bold",
            linespacing=1.5)
    return fig


FIGURES = {
    "request_lifecycle": request_lifecycle,
    "dns_resolution": dns_resolution,
    "connection_setup": connection_setup,
    "latency_budget": latency_budget,
    "http_versions": http_versions,
    "timeout_budget": timeout_budget,
}


if __name__ == "__main__":
    render(FIGURES, TOPIC, sys.argv[1:])
