"""Render visual diagrams for Topic 03: creational and structural design patterns.

Run from this directory:
    python plot_topic_03_figures.py                  # every figure
    python plot_topic_03_figures.py wrapper_family   # just one
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt

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
    card_row,
    heading,
)

ASSETS = Path(__file__).resolve().parent.parent.parent / "basics" / "assets" / "topic-03"


def save(name: str, fig: plt.Figure) -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    output = ASSETS / f"{name}.png"
    fig.savefig(output, dpi=DPI, bbox_inches="tight", facecolor=WHITE)
    plt.close(fig)
    print(f"wrote basics/assets/topic-03/{output.name}")


def panel_title(ax: plt.Axes, x: float, text: str, color: str) -> None:
    """Small bold caption heading one half of a split figure."""
    ax.text(x, 80, text, ha="center", va="center", fontsize=11.5,
            fontweight="bold", color=color)


def pattern_selection() -> plt.Figure:
    fig, ax = canvas(14, 5.8)
    heading(ax, "Start From the Change, Not the Pattern",
            "Three questions to ask before adding any design pattern")
    steps = [
        ("What will change?", "name a real, expected change",
         "A second provider", "Adyen is signed for next quarter"),
        ("Where would it spread?", "find the code it would touch",
         "Every Stripe call", "spread through the checkout code"),
        ("What is the smallest fix?", "keep the change in one place",
         "One Adapter per provider", "behind a PaymentGateway interface"),
    ]
    for index, (question, hint, answer, detail) in enumerate(steps):
        x = 5 + index * 32
        centre = x + 13
        badge(ax, centre, 76, str(index + 1), size=9)
        box(ax, x, 56, 26, 14, question, hint, face=PALE, edge=BLUE)
        arrow(ax, (centre, 55.5), (centre, 43.5), color=GREY)
        box(ax, x, 28, 26, 15, answer, detail, face=WHITE, edge=GREEN)
        if index < 2:
            arrow(ax, (x + 26.5, 63), (x + 31.5, 63), color=BLUE)
    ax.text(50, 23.5, "Green: example answers, from the payment gateway in section 8",
            ha="center", va="center", fontsize=8, fontweight="bold", color=GREEN)
    box(ax, 22, 8, 56, 11, "Can't name a change? Then you don't need a pattern yet.",
        face=AMBER_FACE, edge=AMBER)
    return fig


def patterns_mental_model() -> plt.Figure:
    fig, ax = canvas(14, 6.4)
    heading(ax, "Two Families, Two Kinds of Coupling",
            "Creational patterns decide what gets built; structural patterns decide how parts connect")
    lanes = [
        (52, "Creation coupling", "new Concrete() inside policy", "Creational",
         "who picks the concrete type?", "Swap the product", "callers stay unchanged",
         "Factory · Builder", "Prototype · Singleton", BLUE),
        (14, "Composition coupling", "client wired to internals", "Structural",
         "how are objects connected?", "Swap the wiring", "neither side is edited",
         "Adapter · Decorator", "Facade · Proxy", AMBER),
    ]
    for (y, problem, problem_sub, family, family_sub, win, win_sub,
         members, members_sub, color) in lanes:
        box(ax, 3, y, 19, 23, problem, problem_sub, face=RED_FACE, edge=RED)
        box(ax, 28, y, 22, 23, family, family_sub, face=PALE, edge=color)
        box(ax, 56, y, 20, 23, win, win_sub, face=GREEN_FACE, edge=GREEN)
        box(ax, 82, y, 16, 23, members, members_sub, face=WHITE, edge=color)
        for start, end in ((22.5, 27.5), (50.5, 55.5), (76.5, 81.5)):
            arrow(ax, (start, y + 11.5), (end, y + 11.5), color=GREY)
    ax.text(50, 6, "A pattern is a named trade-off, not a design goal",
            ha="center", fontsize=10, fontweight="bold", color=NAVY)
    return fig


CREATIONAL = [
    ("FM", "Factory Method", "A subclass must\nchoose the product", "One subclass\nper variant",
     NAVY, PALE),
    ("AF", "Abstract Factory", "Products must\nmatch as a family", "A new product type\nedits every factory",
     BLUE, PALE),
    ("B", "Builder", "Many optional fields,\nor cross-field rules", "An extra class\nfor simple objects",
     GREEN, GREEN_FACE),
    ("P", "Prototype", "Copying is cheaper\nthan constructing", "Shallow copies share\nmutable state",
     AMBER, AMBER_FACE),
    ("S", "Singleton", "A second instance\nwould be a bug", "Hidden global state,\nhard to test",
     RED, RED_FACE),
]


def creational_patterns() -> plt.Figure:
    fig, ax = canvas(15, 6.6)
    heading(ax, "Creational Patterns: Five Answers to \"Who Builds This Object?\"",
            "Each one moves the new-ConcreteThing() decision somewhere safer, and charges for it")
    card_row(ax, CREATIONAL, ("USE WHEN", "COST"))
    return fig


def builder_vs_telescoping() -> plt.Figure:
    fig, ax = canvas(14, 6.4)
    heading(ax, "Builder Replaces Constructor Guesswork with Readable Assembly",
            "Named steps at the call site, and one validation gate before the object exists")
    ax.plot([50, 50], [6, 84], color=LINE, linewidth=1.5)

    panel_title(ax, 25, "Telescoping constructors", RED)
    signatures = ["Report(String title)", "Report(String, Format)",
                  "Report(String, Format, boolean)", "Report(String, Format, boolean, int)"]
    for index, signature in enumerate(signatures):
        y = 64 - index * 11
        box(ax, 5, y, 40, 7, "", face=RED_FACE, edge=RED)
        ax.text(25, y + 3.5, signature, ha="center", va="center", fontsize=9,
                color=INK, family="monospace")
    ax.text(25, 18, 'new Report("Q3", PDF, true, 2)', ha="center", fontsize=10,
            fontweight="bold", color=RED, family="monospace")
    ax.text(25, 10, "What do true and 2 mean at the call site?", ha="center",
            fontsize=9, color=INK, style="italic")

    panel_title(ax, 75, "Builder with a validated build()", GREEN)
    steps = ["Report.builder()", '.title("Q3")', ".format(PDF)",
             ".includeCharts(true)", ".build()"]
    for index, step in enumerate(steps):
        y = 66 - index * 10
        last = index == len(steps) - 1
        box(ax, 60, y, 30, 6, "", face=GREEN_FACE if last else PALE,
            edge=GREEN if last else BLUE)
        ax.text(75, y + 3, step, ha="center", va="center", fontsize=9,
                color=INK, family="monospace")
        if not last:
            arrow(ax, (75, y - 0.6), (75, y - 3.4), color=GREY)
    ax.text(75, 12, "build() checks every rule once, before the object exists",
            ha="center", fontsize=9, color=GREEN, fontweight="bold")
    return fig


def wrapper_family() -> plt.Figure:
    fig, ax = canvas(14, 7.4)
    heading(ax, "Four Wrappers, One Shape: Tell Them Apart by Intent",
            "Every structural pattern below sits between a client and a target")
    rows = [
        (63, "Adapter", "translates calls", "The target has the\nwrong interface",
         "interface changes", BLUE),
        (45, "Decorator", "adds behavior", "Same interface,\nextra responsibility",
         "interface identical", GREEN),
        (27, "Facade", "narrows the surface", "Many parts behind\none entry point",
         "interface simplified", AMBER),
        (9, "Proxy", "controls access", "Same interface,\nguarded or deferred",
         "interface identical", RED),
    ]
    for y, name, verb, purpose, note, color in rows:
        box(ax, 4, y, 12, 13, "Client", face=WHITE, edge=NAVY)
        box(ax, 26, y, 18, 13, name, verb, face=PALE, edge=color)
        arrow(ax, (16.5, y + 6.5), (25.5, y + 6.5), color=GREY)
        if name == "Facade":
            for offset, part in enumerate(["Tax", "Stock", "Shipping"]):
                part_y = y + 9.6 - offset * 4.8
                box(ax, 54, part_y, 14, 3.4, part, face=MIST, edge=NAVY, radius=0.8)
                arrow(ax, (44.5, y + 6.5), (53.5, part_y + 1.7), color=color)
        else:
            box(ax, 54, y, 14, 13, "Target", face=MIST, edge=NAVY)
            arrow(ax, (44.5, y + 6.5), (53.5, y + 6.5), color=color)
        ax.text(72, y + 10, purpose, ha="left", va="top", fontsize=9,
                color=INK, linespacing=1.4)
        ax.text(72, y + 1.5, note, ha="left", va="bottom", fontsize=8.5,
                color=INK, style="italic")
    ax.text(50, 2, "Decorator and Proxy have the same code shape; intent and lifecycle separate them",
            ha="center", fontsize=9.5, fontweight="bold", color=NAVY)
    return fig


def onion(ax: plt.Axes, x: float, outer: str, middle: str, outer_color: str,
          middle_color: str, outer_face: str, middle_face: str) -> None:
    """Three nested wrappers: outer(middle(StripeAdapter))."""
    box(ax, x, 26, 40, 46, "", face=outer_face, edge=outer_color)
    ax.text(x + 2, 69, outer, ha="left", va="top", fontsize=10,
            fontweight="bold", color=NAVY)
    box(ax, x + 4, 30, 32, 32, "", face=middle_face, edge=middle_color)
    ax.text(x + 6, 59, middle, ha="left", va="top", fontsize=10,
            fontweight="bold", color=NAVY)
    box(ax, x + 8, 34, 24, 14, "StripeAdapter", "talks to the SDK", face=WHITE, edge=BLUE)


def decorator_ordering() -> plt.Figure:
    fig, ax = canvas(14, 6.6)
    heading(ax, "Decorator Order Changes Behavior",
            "The same three objects, wrapped two ways, produce two different audit trails")
    ax.plot([50, 50], [4, 84], color=LINE, linewidth=1.5)

    panel_title(ax, 25, "Audit( Retry( Adapter ) )", NAVY)
    onion(ax, 5, "AuditingGateway", "RetryingGateway", NAVY, GREEN, PALE, GREEN_FACE)
    ax.text(25, 16, "Audit sees one call per charge", ha="center", fontsize=10,
            fontweight="bold", color=INK)
    ax.text(25, 9, "3 attempts  →  1 audit entry (the final outcome)",
            ha="center", fontsize=9, color=INK, style="italic")

    panel_title(ax, 75, "Retry( Audit( Adapter ) )", NAVY)
    onion(ax, 55, "RetryingGateway", "AuditingGateway", GREEN, NAVY, GREEN_FACE, PALE)
    ax.text(75, 16, "Audit sees every attempt", ha="center", fontsize=10,
            fontweight="bold", color=INK)
    ax.text(75, 9, "3 attempts  →  3 audit entries (one per try)",
            ha="center", fontsize=9, color=INK, style="italic")
    return fig


def payment_gateway_architecture() -> plt.Figure:
    fig, ax = canvas(15, 7.6)
    heading(ax, "Payment Gateway: Each Pattern Absorbs One Expected Change",
            "Checkout depends on one interface; everything volatile sits behind it")
    creational = dict(face=PALE, edge=BLUE)
    structural = dict(face=AMBER_FACE, edge=AMBER)

    box(ax, 3, 60, 15, 13, "Checkout", "calls pay(order)", face=WHITE, edge=NAVY)
    box(ax, 24, 60, 20, 13, "PaymentService", "facade", **structural)
    box(ax, 51, 60, 20, 13, "ChargeRequest", "builder, validated once", **creational)
    arrow(ax, (18.5, 66.5), (23.5, 66.5), color=GREY)
    arrow(ax, (44.5, 66.5), (50.5, 66.5), color=GREY, label="builds")

    box(ax, 24, 34, 20, 13, "GatewayRegistry", "simple factory, by country", **creational)
    arrow(ax, (34, 59.5), (34, 47.5), color=GREY)
    ax.text(35.5, 53.5, "resolves", ha="left", va="center", fontsize=8, color=INK)

    box(ax, 51, 34, 14, 13, "RetryingGateway", "decorator", **structural)
    box(ax, 68, 34, 14, 13, "AuditingGateway", "decorator", **structural)
    box(ax, 85, 34, 12, 13, "StripeAdapter", "adapter", **structural)
    arrow(ax, (44.5, 40.5), (50.5, 40.5), color=GREY, label="returns")
    arrow(ax, (65.5, 40.5), (67.5, 40.5), color=GREY)
    arrow(ax, (82.5, 40.5), (84.5, 40.5), color=GREY)
    ax.text(66, 28.5, "Every link implements PaymentGateway", ha="center",
            fontsize=9, fontweight="bold", color=NAVY)

    box(ax, 83, 8, 14, 13, "Stripe SDK", "third-party code", face=WHITE, edge=GREY)
    arrow(ax, (91, 33.5), (91, 21.5), color=GREY)

    ax.text(3, 25, "Why is there no Proxy?", fontsize=9.5, fontweight="bold", color=NAVY)
    ax.text(3, 21, "Nothing here controls access or\nlifecycle. Adding one just to use\n"
            "the name would be pattern worship.", va="top", fontsize=8.6,
            color=INK, linespacing=1.45)
    ax.text(50, 3, "Blue border: creational pattern     Amber border: structural pattern",
            ha="center", fontsize=8.5, color=INK)
    return fig


FIGURES = {
    "pattern_selection": pattern_selection,
    "patterns_mental_model": patterns_mental_model,
    "creational_patterns": creational_patterns,
    "builder_vs_telescoping": builder_vs_telescoping,
    "wrapper_family": wrapper_family,
    "decorator_ordering": decorator_ordering,
    "payment_gateway_architecture": payment_gateway_architecture,
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
