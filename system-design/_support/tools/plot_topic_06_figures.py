"""Render the diagrams for Topic 06: API Correctness, Security & Resource Design.

Run from the system-design directory (optionally pass figure names):

    uv run --with matplotlib \
      --index-url https://pypi.ci.artifacts.walmart.com/artifactory/api/pypi/external-pypi/simple \
      --allow-insecure-host pypi.ci.artifacts.walmart.com \
      python _support/tools/plot_topic_06_figures.py
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
    caps,
    heading,
    note,
    panel,
    render,
)

TOPIC = "topic-06"


# ---------- figures --------------------------------------------------------------

def request_checkpoints() -> plt.Figure:
    fig, ax = canvas(15, 6.5)
    heading(ax, "Every Request Passes a Series of Checkpoints",
            "Cheap checks run first, so a bad request is turned away before it "
            "costs a database query")
    stages = [
        ("Gateway limits", "TLS, body size,\nslow-client timeout", "413", "too large"),
        ("Authenticate", "who is calling?", "401", "no valid identity"),
        ("Rate limit", "too many requests\nfrom this caller?", "429", "slow down"),
        ("Validate", "is the request\nwell formed?", "400 / 422", "fix the request"),
        ("Authorize", "may this caller touch\nthis resource?", "403 / 404", "not yours"),
        ("Handle", "business logic,\nwithin a deadline", "503 / 504", "overloaded or too slow"),
    ]
    width, margin = 12.5, 3
    step = width + (100 - 2 * margin - len(stages) * width) / (len(stages) - 1)
    arrow(ax, (margin, 80), (100 - margin, 80), color=GREY)
    caps(ax, margin, 83.5, "CHEAP: NO DATABASE NEEDED", ha="left", size=7.5)
    caps(ax, 100 - margin, 83.5, "COSTLY: NEEDS THE DATA", ha="right", size=7.5)
    for index, (title, subtitle, code, reason) in enumerate(stages):
        x = margin + index * step
        centre = x + width / 2
        box(ax, x, 46, width, 18, title, subtitle,
            face=MIST if index == len(stages) - 1 else PALE)
        badge(ax, centre, 70.5, str(index + 1), size=9)
        if index < len(stages) - 1:
            arrow(ax, (x + width + 0.6, 55), (x + step - 0.6, 55))
        arrow(ax, (centre, 45.3), (centre, 33.5), color=RED, dashed=True)
        box(ax, x, 23, width, 9.5, code, reason, face=RED_FACE, edge=RED,
            title_color=RED)
    note(ax, 50, 11, "Only a request that passes every checkpoint reaches the business "
         "logic. Every rejection uses the same error format (section 4).",
         color=GREEN, size=9)
    return fig


_SLOT_X0, _SLOT_STEP, _CARD_W = 27, 5.3, 3.9   # box() pads 0.5 per side, so gap = 0.4


def _slot_x(slot: int) -> float:
    """Left edge of card `slot` in a pagination row (slot 0 = newest link)."""
    return _SLOT_X0 + slot * _SLOT_STEP


def _card_row(ax: plt.Axes, y: float, numbers: range, style_of) -> None:
    """Draw one row of link cards centred on y; style_of(slot) -> (face, edge, text)."""
    for slot, number in enumerate(numbers):
        face, edge, text = style_of(slot)
        box(ax, _slot_x(slot), y - 4, _CARD_W, 8, str(number), face=face, edge=edge,
            title_color=text, linewidth=1.4)


def _span(ax: plt.Axes, first: int, last: int, y: float, *, below: bool, color: str,
          label: str) -> None:
    """A thin bracket over (or under) cards first..last, with a label outside it."""
    left, right = _slot_x(first) - 0.3, _slot_x(last) + _CARD_W + 0.3
    tick = 1.5 if below else -1.5
    ax.plot([left, left, right, right], [y + tick, y, y, y + tick], color=color,
            linewidth=1.6)
    note(ax, (left + right) / 2, y - 3 if below else y + 3, label, color=color, size=8.6)


def _row_label(ax: plt.Axes, y: float, title: str, detail: str, color: str) -> None:
    caps(ax, 2, y + 2.6, title, color=color, ha="left", size=9)
    note(ax, 2, y - 2.6, detail, ha="left", size=8.4)


def offset_vs_cursor() -> plt.Figure:
    fig, ax = canvas(14, 7)
    heading(ax, "Offset vs Cursor: Asking for Page 2 After New Links Arrive",
            "Links are listed newest first, 5 per page. Three new links arrive after "
            "the user has seen page 1")
    faded = (WHITE, LINE, GREY)
    new = (AMBER_FACE, AMBER, AMBER)

    # Row 1: page 1, before the new links exist.
    _row_label(ax, 70, "PAGE 1", "the user sees\nlinks 50 to 46", NAVY)
    _card_row(ax, 70, range(50, 45, -1), lambda slot: (PALE, BLUE, NAVY))
    note(ax, 75, 70, "then 3 new links (51, 52, 53)\nare added at the top of the list",
         color=AMBER, size=9)

    # Row 2: offset counts positions, so it lands three places too early.
    _row_label(ax, 45, "PAGE 2 BY OFFSET", "?offset=5&limit=5\nskip 5 links, take 5", RED)
    _card_row(ax, 45, range(53, 40, -1), lambda slot: new if slot < 3 else
              (RED_FACE, RED, RED) if 5 <= slot <= 9 else faded)
    _span(ax, 0, 4, 51.5, below=False, color=GREY, label="skipped")
    _span(ax, 5, 7, 38.5, below=True, color=RED, label="already seen on page 1")

    # Row 3: the cursor remembers link 46, so it starts in the right place.
    _row_label(ax, 20, "PAGE 2 BY CURSOR", "?after=<link 46>&limit=5\ntake 5 after link 46",
               GREEN)
    _card_row(ax, 20, range(53, 40, -1), lambda slot: new if slot < 3 else
              (GREEN_FACE, GREEN, GREEN) if slot >= 8 else faded)
    gap_x = _slot_x(8) - (_SLOT_STEP - _CARD_W) / 2
    arrow(ax, (gap_x, 6.5), (gap_x, 14.8), color=GREEN)
    note(ax, gap_x, 3.5, "the cursor points here, right after link 46", color=GREEN,
         size=8.6)
    return fig


def session_vs_jwt() -> plt.Figure:
    fig, ax = canvas(15, 7.5)
    heading(ax, "Server-Side Session vs Signed Token (JWT)",
            "Both prove who the caller is. They differ in where the proof is "
            "kept and how it is checked")
    caps(ax, 25, 83, "SESSION: THE SERVER LOOKS THE CALLER UP", color=NAVY, size=9)
    caps(ax, 75, 83, "JWT: THE SERVER CHECKS A SIGNATURE", color=GREEN, size=9)
    ax.plot([50, 50], [8, 86], color=LINE, linewidth=1.2)

    box(ax, 3, 62, 12, 9, "Browser", "holds a random ID")
    box(ax, 33, 62, 13, 9, "API instance", "any instance")
    arrow(ax, (15.6, 66.5), (32.4, 66.5), label="Cookie: session=8f3a...")
    box(ax, 31.5, 34, 16, 11, "Session store", "8f3a... -> user 42,\nplan pro", face=WHITE,
        edge=NAVY)
    arrow(ax, (39.5, 61.3), (39.5, 45.8), color=NAVY, label="look up 8f3a...")
    note(ax, 25, 18, "Log out or ban: delete one row, and it takes effect at once.\n"
         "Cost: one fast lookup on every request.", color=NAVY, size=8.6)

    box(ax, 53, 62, 12, 9, "Client", "holds the token")
    box(ax, 83, 62, 14, 9, "API instance", "any instance")
    arrow(ax, (65.6, 66.5), (82.4, 66.5), color=GREEN,
          label="Authorization: Bearer eyJhb...")
    box(ax, 82, 34, 16, 11, "Public key", "already in memory,\nno network call",
        face=WHITE, edge=GREEN, title_color=GREEN)
    arrow(ax, (90, 61.3), (90, 45.8), color=GREEN, label="check the\nsignature")
    note(ax, 75, 18, "No lookup: any instance can verify it with a public key.\n"
         "Cost: hard to cancel before it expires, so keep it short-lived.",
         color=GREEN, size=8.6)
    return fig


def jwt_how_it_works() -> plt.Figure:
    fig, ax = canvas(15, 8.5)
    heading(ax, "How a JWT Is Made and Checked",
            "The login service seals the token with its private key. "
            "The API checks the seal with the matching public key")

    # Row 1: who makes the token, the token itself, and who checks it.
    box(ax, 2, 66, 17, 11, "Login service", "holds the private key", face=MIST, edge=NAVY)
    box(ax, 81, 66, 17, 11, "Link API", "holds only the public key", face=MIST, edge=NAVY)
    caps(ax, 50, 82, "THE TOKEN: THREE PARTS, JOINED BY DOTS", size=9)
    parts = [(25, 11, "eyJhbGci...", PALE, BLUE),
             (38, 21, "eyJzdWIiOiI0Mi...", AMBER_FACE, AMBER),
             (61, 14, "SflKxwRJSM...", GREEN_FACE, GREEN)]
    for x, width, text, face, edge in parts:
        box(ax, x, 68.5, width, 6, text, face=face, edge=edge, title_color=edge,
            radius=0.4)
    for x in (37, 60):
        ax.text(x, 70.5, ".", ha="center", va="center", fontsize=22, fontweight="bold",
                color=INK)
    arrow(ax, (19.6, 71.5), (24.4, 71.5), color=NAVY)
    note(ax, 22, 75, "issues", size=7.8, color=NAVY)
    arrow(ax, (75.6, 71.5), (80.4, 71.5), color=NAVY)
    note(ax, 78, 75, "sent", size=7.8, color=NAVY)

    # Row 2: what each part says once decoded, and what the API checks.
    panel(ax, 3, 34, 20, 19, "HEADER", '{ "alg": "RS256" }\n\nwhich algorithm\nmade the seal')
    panel(ax, 27, 34, 26, 19, "PAYLOAD (THE CLAIMS)",
          "sub: 42 → the user\niss: login service → who made it\n"
          "aud: link-api → who it is for\nexp: 10:15 → when it expires",
          face=AMBER_FACE, edge=AMBER, title_color=AMBER)
    panel(ax, 57, 34, 20, 19, "SIGNATURE (THE SEAL)",
          "made from the header\nand the payload,\nusing the private key",
          face=GREEN_FACE, edge=GREEN, title_color=GREEN)
    for start, end in (((30.5, 67.8), (13, 53.7)), ((48.5, 67.8), (40, 53.7)),
                       ((68, 67.8), (67, 53.7))):
        ax.plot(*zip(start, end), color=GREY, linewidth=1.2, linestyle="--")
    panel(ax, 81, 34, 17, 19, "THE API CHECKS",
          "1. the seal matches\n2. iss is our login service\n3. aud is link-api\n"
          "4. exp has not passed", face=WHITE, edge=GREEN, title_color=GREEN)
    arrow(ax, (89.5, 65.3), (89.5, 53.8), color=GREEN)

    # Row 3: the two facts people get wrong.
    note(ax, 50, 24, "Change one character, such as sub: 42 → 43, and the seal no longer "
         "matches, so the API rejects the token.\nOnly the login service can make a new "
         "seal, because only it has the private key.", color=RED, size=9)
    note(ax, 50, 15, "The payload is only base64-encoded, not encrypted: anyone holding "
         "the token can read it.", color=AMBER, size=9)
    return fig


def oauth_code_flow() -> plt.Figure:
    fig, ax = canvas(15, 8.5)
    heading(ax, "OAuth 2.0: How MailBlast Gets Limited Access to Asha's Links",
            "The authorization code flow with PKCE. MailBlast never sees Asha's password")
    lanes = [(14, "Asha", "resource owner"), (38, "MailBlast", "client"),
             (63, "go.example login", "authorization server"),
             (87, "Link API", "resource server")]
    for x, title, subtitle in lanes:
        box(ax, x - 8, 75, 16, 8, title, subtitle,
            face=MIST if title == "Link API" else PALE)
        ax.plot([x, x], [10, 74], color=LINE, linewidth=1.4, linestyle="--", zorder=0)

    steps = [
        (38, 63, "send Asha to the login page,\nasking for links:write (+ PKCE hash)", BLUE),
        (14, 63, "Asha logs in there and clicks Allow", NAVY),
        (63, 38, "send Asha back with a one-time code", BLUE),
        (38, 63, "swap the code (+ PKCE secret) for a token", BLUE),
        (63, 38, "access token (15 min) + refresh token", GREEN),
        (38, 87, "POST /v1/links\nAuthorization: Bearer <token>", BLUE),
        (87, 38, "201 Created: links:write allows this", GREEN),
    ]
    for index, (start, end, label, color) in enumerate(steps):
        y = 66 - index * 8.3
        badge(ax, 3.5, y, str(index + 1), size=8)
        arrow(ax, (start, y), (end, y), color=color)
        ax.text((start + end) / 2, y + 2.6, label, ha="center", va="center",
                fontsize=7.8, color=color, linespacing=1.25,
                bbox=dict(facecolor=WHITE, edgecolor="none", pad=0.8))
    note(ax, 50, 4.5, "PKCE: MailBlast made up a secret at step 1 and sent only its hash. "
         "A stolen one-time code is useless without that secret.", color=GREY, size=8.4)
    return fig


def url_shortener_public_api() -> plt.Figure:
    fig, ax = canvas(15, 8.5)
    heading(ax, "URL Shortener, Year Two: The Public API",
            "Each check from this page has one home, so no service has to "
            "repeat or forget it")
    clients = [("Dashboard", "browser, session cookie", 66),
               ("Mobile app", "OAuth code + PKCE", 47),
               ("Partner tool", "API key", 28)]
    caps(ax, 11, 82, "CALLERS", size=8)
    for title, subtitle, y in clients:
        box(ax, 3, y, 16, 10, title, subtitle)
        arrow(ax, (19.6, y + 5), (26.4, y + 5), color=BLUE)

    panel(ax, 27, 24, 17, 54, "API gateway",
          "TLS ends here\n1 MB body limit\nslow-client timeout\n\nauthenticate:\n"
          "session, token,\nor API key hash\n\nrate limit per caller", face=MIST, edge=NAVY)
    box(ax, 27, 6, 17, 9, "Session store", "Redis", face=WHITE, edge=NAVY)
    arrow(ax, (35.5, 23.3), (35.5, 15.7), color=GREY, dashed=True)

    box(ax, 53, 72, 20, 9, "Identity provider", "OAuth / OIDC, issues tokens",
        face=WHITE, edge=NAVY)
    arrow(ax, (44.6, 72), (52.4, 76.5), color=GREY, dashed=True)
    note(ax, 48.5, 66, "signing keys\n(cached)", color=GREY, size=7.8)
    panel(ax, 53, 34, 20, 30, "Link management",
          "validate the request\nauthorize: owner check\non every link\n"
          "Problem Details errors\n5 s deadline", face=GREEN_FACE, edge=GREEN)
    arrow(ax, (44.6, 49), (52.4, 49), color=BLUE, label="mTLS")

    panel(ax, 81, 34, 16, 30, "Links database",
          "encrypted at rest\n\nemails: field-level\nencryption\n\nAPI keys stored\n"
          "as hashes only", face=WHITE, edge=NAVY)
    arrow(ax, (73.6, 49), (80.4, 49), color=BLUE, label="TLS")
    box(ax, 81, 10, 16, 10, "Secrets manager", "DB password,\nencryption keys",
        face=AMBER_FACE, edge=AMBER, title_color=AMBER)
    arrow(ax, (80.4, 15), (63, 33.3), color=AMBER, dashed=True,
          label="read at startup")
    return fig


FIGURES = {
    "request_checkpoints": request_checkpoints,
    "offset_vs_cursor": offset_vs_cursor,
    "session_vs_jwt": session_vs_jwt,
    "jwt_how_it_works": jwt_how_it_works,
    "oauth_code_flow": oauth_code_flow,
    "url_shortener_public_api": url_shortener_public_api,
}


if __name__ == "__main__":
    render(FIGURES, TOPIC, sys.argv[1:])
