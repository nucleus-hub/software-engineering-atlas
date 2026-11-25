"""Render the diagrams for Topic 07: API Design & Service Communication.

Run from the system-design directory (optionally pass figure names):

    uv run --with matplotlib \
      --index-url https://pypi.ci.artifacts.walmart.com/artifactory/api/pypi/external-pypi/simple \
      --allow-insecure-host pypi.ci.artifacts.walmart.com \
      python _support/tools/plot_topic_07_figures.py
"""

from __future__ import annotations

import sys

import matplotlib.pyplot as plt

from figure_style import (
    AMBER,
    AMBER_FACE,
    BLUE,
    GREEN,
    GREEN_FACE,
    GREY,
    LINE,
    MIST,
    NAVY,
    PALE,
    RED,
    WHITE,
    arrow,
    badge,
    box,
    canvas,
    caps,
    heading,
    note,
    panel,
    render,
)

TOPIC = "topic-07"


def three_api_styles() -> plt.Figure:
    fig, ax = canvas(15, 8.5)
    heading(ax, "One Screen, Three API Styles",
            "The mobile app needs one link's target URL and its click total")
    styles = [
        ("REST", "2 requests, fixed shapes", BLUE, PALE,
         "GET /v1/links/summer-sale\nGET /v1/links/summer-sale/clicks",
         '{ "code": "summer-sale",\n  "targetUrl": "https://...",\n'
         '  "title": "...", "tags": [...],\n'
         '  ...12 more fields }\n{ "total": 1234, ... }',
         "Any client can call it, and\nHTTP caches understand it.\nCost: extra round trips\n"
         "and fields nobody asked for."),
        ("gRPC", "1 call, typed contract", NAVY, MIST,
         "LinkStats.GetSummary(\n  code: \"summer-sale\")\n\nprotobuf over HTTP/2",
         "binary message:\n  target_url = \"https://...\"\n  total_clicks = 1234\n\n"
         "(not human-readable)",
         "Generated clients, small\nmessages, built-in deadlines.\nCost: browsers need a proxy,\n"
         "and you cannot read it by eye."),
        ("GraphQL", "1 request, client picks fields", GREEN, GREEN_FACE,
         "POST /graphql\n{ link(code: \"summer-sale\") {\n    targetUrl\n"
         "    clicks { total } } }",
         '{ "data": { "link": {\n    "targetUrl": "https://...",\n'
         '    "clicks": { "total": 1234 }\n} } }',
         "Exactly the fields asked for,\nin one round trip.\nCost: hard to cache, and every\n"
         "query must be limited."),
    ]
    for index, (name, tagline, color, face, request, response, verdict) in enumerate(styles):
        x = 3 + index * 33
        caps(ax, x + 14, 82, name, color=color, size=12)
        note(ax, x + 14, 77.5, tagline, color=color, size=9)
        panel(ax, x, 53, 28, 20, "REQUEST", request, face=WHITE, edge=color,
              title_color=color, mono=True)
        arrow(ax, (x + 14, 52.3), (x + 14, 47.7), color=color)
        panel(ax, x, 24, 28, 23, "RESPONSE", response, face=face, edge=color,
              title_color=color, mono=True)
        note(ax, x + 14, 13, verdict, size=8.6)
    return fig


# Timeline geometry for push_options: 0 to 60 seconds drawn between x=30 and x=96.
_T0, _T1 = 30, 96
_EVENTS = (7, 23, 41)


def _tx(seconds: float) -> float:
    return _T0 + (_T1 - _T0) * seconds / 60


_LONG_POLL_GAP = 0.8   # seconds between an answer and the client's next request


def _bar(ax: plt.Axes, start: float, end: float, y: float, color: str) -> None:
    """An open connection or held request, drawn as a soft bar.

    box() pads 0.5 on each side, so shrink by that much to keep the bar's
    edges on its real start and end times.
    """
    box(ax, _tx(start) + 0.5, y - 1.6, _tx(end) - _tx(start) - 1.0, 3.2, "", face=PALE,
        edge=color, radius=0.6, linewidth=1.3)


def _caption(ax: plt.Axes, y: float, text: str, color: str) -> None:
    """Row caption on a white background, so the dotted event lines do not cut it."""
    ax.text(63, y, text, ha="center", va="center", fontsize=8.2, color=color, zorder=6,
            bbox=dict(facecolor=WHITE, edgecolor="none", pad=1.5))


def _dot(ax: plt.Axes, seconds: float, y: float, *, filled: bool) -> None:
    """A response: green and filled when it carries new data, hollow when empty."""
    ax.plot(_tx(seconds), y, marker="o", markersize=8, zorder=5,
            markerfacecolor=GREEN if filled else WHITE,
            markeredgecolor=GREEN if filled else GREY, markeredgewidth=1.6)


def _ask(ax: plt.Axes, seconds: float, y: float) -> None:
    """A message from the client to the server."""
    ax.plot(_tx(seconds), y - 4.2, marker="^", markersize=7, color=BLUE, zorder=5)


def push_options() -> plt.Figure:
    fig, ax = canvas(15, 8)
    heading(ax, "Four Ways to Get New Data From the Server",
            "New data appears on the server at 7 s, 23 s, and 41 s. "
            "How soon does the client see it, and at what cost?")
    caps(ax, 2, 82, "NEW DATA ON THE SERVER", color=AMBER, ha="left", size=8.5)
    for seconds in _EVENTS:
        ax.plot(_tx(seconds), 82, marker="D", markersize=8, color=AMBER)
        ax.plot([_tx(seconds)] * 2, [10, 79], color=AMBER, linewidth=1, linestyle=":")
    for seconds in range(0, 61, 10):
        note(ax, _tx(seconds), 7, f"{seconds} s", color=GREY, size=7.8)

    rows = [
        (68, "SHORT POLLING", "ask every 10 s;\nmost answers are empty", RED),
        (51, "LONG POLLING", "the server holds each\nrequest until data arrives", AMBER),
        (34, "SERVER-SENT EVENTS", "one long response;\nserver to client only", GREEN),
        (17, "WEBSOCKET", "one open connection;\nboth sides send at any time", NAVY),
    ]
    for y, title, detail, color in rows:
        caps(ax, 2, y + 2.6, title, color=color, ha="left", size=9)
        note(ax, 2, y - 3, detail, ha="left", size=8.2)
        ax.plot([_T0, _T1], [y, y], color=LINE, linewidth=1)

    for seconds in range(0, 61, 10):                     # short polling
        _ask(ax, seconds, 68)
        _dot(ax, seconds + 0.6, 68, filled=seconds in (10, 30, 50))
    _caption(ax, 75, "data waits up to 10 s; 4 of 7 requests were wasted", RED)

    starts = (0,) + tuple(event + _LONG_POLL_GAP for event in _EVENTS)   # long polling
    for start, end in zip(starts, _EVENTS + (60,)):
        _ask(ax, start, 51)
        _bar(ax, start, end, 51, AMBER)
        if end in _EVENTS:
            _dot(ax, end, 51, filled=True)
    _caption(ax, 58, "no delay, but one new request after every answer", AMBER)

    _ask(ax, 0, 34)                                       # SSE
    _bar(ax, 0, 60, 34, GREEN)
    for seconds in _EVENTS:
        _dot(ax, seconds, 34, filled=True)
    _caption(ax, 41, "no delay, one request; the client cannot reply on it", GREEN)

    _ask(ax, 0, 17)                                       # WebSocket
    _bar(ax, 0, 60, 17, NAVY)
    for seconds in _EVENTS:
        _dot(ax, seconds, 17, filled=True)
    for seconds in (15, 33, 52):
        _ask(ax, seconds, 17)
    _caption(ax, 24, "no delay, and the client can send too (blue triangles)", NAVY)
    return fig


def sync_vs_async() -> plt.Figure:
    fig, ax = canvas(15, 8)
    heading(ax, "Creating a Link: Synchronous Calls vs One Published Event",
            "The same three follow-up jobs, done while the user waits, "
            "or after the user has their answer")
    caps(ax, 25, 82, "SYNCHRONOUS: THE USER WAITS FOR EVERY CALL", color=RED, size=9)
    caps(ax, 75, 82, "ASYNCHRONOUS: THE USER WAITS FOR ONE SAVE", color=GREEN, size=9)
    ax.plot([50, 50], [6, 85], color=LINE, linewidth=1.2)
    jobs = [("Redirect service", "copy the link", "20 ms"),
            ("Malware scanner", "check the target", "120 ms"),
            ("Analytics", "start a counter", "25 ms")]

    box(ax, 2, 46, 13, 12, "Links module", "save: 30 ms", face=MIST, edge=NAVY)
    for index, (title, subtitle, cost) in enumerate(jobs):
        y = 66 - index * 18
        box(ax, 32, y, 15, 10, title, f"{subtitle}: {cost}")
        arrow(ax, (15.6, 52), (31.4, y + 5), color=RED)
        badge(ax, 23.5, (52 + y + 5) / 2 + 1.5, str(index + 1), color=RED, size=7)
    note(ax, 25, 20, "Time the user waits: 30 + 20 + 120 + 25 = 195 ms\n"
         "Availability: 99.9% × 4 parts ≈ 99.6%\n"
         "Scanner down = nobody can create a link", color=RED, size=8.8)

    box(ax, 52, 46, 13, 12, "Links module", "save: 30 ms", face=MIST, edge=NAVY)
    box(ax, 69, 47, 9, 10, "Event bus", "", face=AMBER_FACE, edge=AMBER, title_color=AMBER)
    arrow(ax, (65.6, 52), (68.4, 52), color=AMBER)
    note(ax, 73.5, 42, "publishes\nLinkCreated", color=AMBER, size=8)
    for index, (title, subtitle, _) in enumerate(jobs):
        y = 66 - index * 18
        box(ax, 83, y, 15, 10, title, subtitle)
        arrow(ax, (78.6, 52), (82.4, y + 5), color=AMBER, dashed=True)
    note(ax, 75, 20, "Time the user waits: 30 ms\n"
         "Scanner down = its events wait in the bus\n"
         "Cost: the jobs finish a moment later, and\n"
         "each consumer may see an event twice", color=GREEN, size=8.8)
    return fig


def expand_and_contract() -> plt.Figure:
    fig, ax = canvas(15, 6.5)
    heading(ax, "Changing a Field Without Breaking Anyone: Expand, Migrate, Contract",
            "Links can now have several weighted targets, so targetUrl (one string) "
            "must give way to targets (a list)")
    arrow(ax, (3, 80), (97, 80), color=GREY)
    phases = [
        ("1", "EXPAND", "week 0", "WHAT CLIENTS SEE", BLUE, PALE,
         '{ "targetUrl": "https://a.example",\n  "targets": [\n'
         '    { "url": "https://a.example",\n      "weight": 100 } ] }',
         "Add the new field next to the old one.\nWrites accept either field.\n"
         "No client has to change."),
        ("2", "MIGRATE", "weeks 1 to 12", "WHAT YOU PUBLISH AND MEASURE", AMBER, AMBER_FACE,
         "docs and changelog:\n  targetUrl is deprecated;\n  removal not before 2027-04-01\n\n"
         "API keys still writing targetUrl:\n  week 1: 41    week 8: 3",
         "Mark the old field deprecated, publish\na date, and measure who still writes it.\n"
         "Contact the last few callers directly."),
        ("3", "CONTRACT", "only when usage is zero", "WHAT CLIENTS SEE", GREEN, GREEN_FACE,
         '{ "targets": [\n    { "url": "https://a.example",\n'
         '      "weight": 100 } ] }',
         "Remove the old field only when nobody\nuses it. In a public v1 you may keep it\n"
         "forever, or drop it only in v2."),
    ]
    for index, (number, title, when, label, color, face, body, verdict) in enumerate(phases):
        x = 3 + index * 32.5
        badge(ax, x + 14, 80, number, color=color, size=10)
        caps(ax, x + 14, 73, f"{title}  ({when})", color=color, size=9.5)
        panel(ax, x, 37, 29, 28, label, body, face=face, edge=color,
              title_color=color, mono=True)
        note(ax, x + 14.5, 24, verdict, size=8.6)
    return fig


def url_shortener_communication() -> plt.Figure:
    fig, ax = canvas(15, 9)
    heading(ax, "URL Shortener, Year Two: How Every Part Talks",
            "Each connection uses the style that fits who is talking, "
            "and whether anyone is waiting")
    caps(ax, 9, 83, "CALLERS", size=8)
    for title, subtitle, y in (("Dashboard", "browser", 68), ("Mobile app", "phone", 50),
                               ("Partner tool", "e.g. MailBlast", 32)):
        box(ax, 2, y, 14, 9, title, subtitle)
        arrow(ax, (16.6, y + 5.5), (23.4, y + 5.5), color=BLUE)
    arrow(ax, (23.4, 70.5), (16.6, 70.5), color=GREEN)
    note(ax, 20, 66.5, "SSE", color=GREEN, size=7.8)

    panel(ax, 24, 28, 12, 52, "API gateway", "REST + JSON\nfor every\ncaller\n\n"
          "(Basics 6:\nauth, limits)", face=MIST, edge=NAVY)
    panel(ax, 44, 52, 20, 28, "Link management",
          "Links module\nDashboards module\n\nholds open SSE\nstreams for live\nclick counts",
          face=GREEN_FACE, edge=GREEN, title_color=GREEN)
    arrow(ax, (36.6, 70), (43.4, 70), color=BLUE, label="REST")
    arrow(ax, (43.4, 61), (36.6, 61), color=GREEN, label="SSE")

    box(ax, 76, 63, 20, 10, "Redirect service", "own redirect store")
    note(ax, 86, 81, "visitors: GET /abc123", color=GREY, size=8)
    arrow(ax, (86, 79), (86, 73.7), color=GREY)
    arrow(ax, (75.4, 70), (64.6, 70), color=NAVY, dashed=True)
    note(ax, 70, 76, "gRPC, miss only\n50 ms deadline", color=NAVY, size=7.8)

    box(ax, 70, 37, 26, 9, "Event bus", "", face=AMBER_FACE, edge=AMBER,
        title_color=AMBER)
    arrow(ax, (64.6, 56), (73, 46.6), color=AMBER, dashed=True)
    note(ax, 76.5, 53, "LinkCreated\nLinkChanged", color=AMBER, size=7.8)
    arrow(ax, (69.4, 41.5), (59, 51.4), color=AMBER, dashed=True)
    note(ax, 60, 44.5, "ClicksCounted", color=AMBER, size=7.8)
    arrow(ax, (82, 46.6), (82, 62.4), color=AMBER, dashed=True)
    arrow(ax, (91, 62.4), (91, 46.6), color=AMBER, dashed=True)
    note(ax, 95.5, 55, "Link\nClicked", color=AMBER, size=7.8)

    box(ax, 78, 12, 18, 10, "Click workers", "count per second")
    arrow(ax, (87, 36.4), (87, 22.6), color=AMBER, dashed=True)
    box(ax, 44, 12, 20, 10, "Analytics", "click totals API")
    arrow(ax, (77.4, 17), (64.6, 17), color=GREY, label="save totals")
    arrow(ax, (52, 51.4), (52, 22.6), color=NAVY)
    note(ax, 46, 37, "gRPC\n300 ms\ndeadline", color=NAVY, size=7.8)

    legend = [(BLUE, False, "REST + JSON: public, anyone can call it"),
              (GREEN, False, "SSE: live updates pushed to the browser"),
              (NAVY, False, "gRPC: internal call with a deadline"),
              (AMBER, True, "event: nobody waits for the reply")]
    for index, (color, dashed, label) in enumerate(legend):
        y = 21 - index * 4.5
        ax.plot([2, 7], [y, y], color=color, linewidth=2, linestyle="--" if dashed else "-")
        note(ax, 8.5, y, label, ha="left", size=8.2)
    return fig


FIGURES = {
    "three_api_styles": three_api_styles,
    "push_options": push_options,
    "sync_vs_async": sync_vs_async,
    "expand_and_contract": expand_and_contract,
    "url_shortener_communication": url_shortener_communication,
}


if __name__ == "__main__":
    render(FIGURES, TOPIC, sys.argv[1:])
