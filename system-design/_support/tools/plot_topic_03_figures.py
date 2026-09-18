"""Render visual diagrams for Topic 03: creational and structural design patterns."""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyBboxPatch

from figure_style import (
    AMBER,
    BLUE,
    DPI,
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
    box,
    canvas,
    heading,
)

ASSETS = Path(__file__).resolve().parent.parent.parent / "basics" / "assets" / "topic-03"


def save(name: str, fig: plt.Figure) -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    output = ASSETS / f"{name}.png"
    fig.savefig(output, dpi=DPI, bbox_inches="tight", facecolor=WHITE)
    plt.close(fig)
    print(f"wrote basics/assets/topic-03/{output.name}")


def patterns_mental_model() -> plt.Figure:
    fig, ax = canvas(14, 6.4)
    heading(ax, "Two Families, Two Kinds of Coupling",
            "Creational patterns decide what gets built; structural patterns decide how parts connect")
    lanes = [
        (52, "Creation coupling", "new Concrete() inside policy",
         "Creational", "who decides the concrete type?",
         "Swap the product", "callers stay unchanged", BLUE),
        (14, "Composition coupling", "client wired to internals",
         "Structural", "how are objects assembled?",
         "Swap the wiring", "neither side is edited", AMBER),
    ]
    for y, problem, problem_sub, family, family_sub, win, win_sub, color in lanes:
        box(ax, 3, y, 19, 23, problem, problem_sub, face="#FDEDEC", edge=RED,
            title_color=RED)
        box(ax, 28, y, 22, 23, family, family_sub, face=MIST, edge=color,
            title_color=NAVY)
        box(ax, 56, y, 20, 23, win, win_sub, face="#E9F7EF", edge=GREEN,
            title_color=GREEN)
        arrow(ax, (22.5, y + 11.5), (27.5, y + 11.5), color=GREY)
        arrow(ax, (50.5, y + 11.5), (55.5, y + 11.5), color=GREY)
        arrow(ax, (76.5, y + 11.5), (81.5, y + 11.5), color=color)
    box(ax, 82, 52, 15, 23, "Factory  Builder", "Singleton  Prototype",
        face=WHITE, edge=BLUE, title_color=BLUE)
    box(ax, 82, 14, 15, 23, "Adapter  Decorator", "Facade  Proxy",
        face=WHITE, edge=AMBER, title_color=AMBER)
    ax.text(50, 6, "A pattern is a named trade-off, not a design goal",
            ha="center", fontsize=10, fontweight="bold", color=NAVY)
    return fig


def creational_patterns() -> plt.Figure:
    fig, axes = plt.subplots(1, 5, figsize=(15, 4.4), facecolor=WHITE)
    fig.suptitle("Creational Patterns: Five Answers to \"Who Builds This Object?\"",
                 fontsize=18, fontweight="bold", color=NAVY, y=0.99)
    patterns = [
        ("Singleton", "One shared\ninstance", "Global access\nhides coupling", NAVY),
        ("Factory\nMethod", "Subclass picks\nthe product", "One product\nfamily member", BLUE),
        ("Abstract\nFactory", "Build a matched\nfamily", "Adding a product\ntouches all factories", GREEN),
        ("Builder", "Assemble step\nby step", "Extra type for\nsimple objects", AMBER),
        ("Prototype", "Clone an existing\ninstance", "Deep vs shallow\ncopy bugs", RED),
    ]
    for ax, (name, intent, cost, color) in zip(axes, patterns):
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 10)
        ax.axis("off")
        ax.add_patch(FancyBboxPatch((0.6, 0.8), 8.8, 8.4,
                                    boxstyle="round,pad=0.4,rounding_size=0.5",
                                    facecolor=PALE, edgecolor=color, linewidth=2))
        ax.text(5, 8.0, name, ha="center", va="center", fontsize=11.5,
                fontweight="bold", color=color, linespacing=1.3)
        ax.plot([1.6, 8.4], [6.6, 6.6], color=LINE, linewidth=1.5)
        ax.text(5, 5.2, intent, ha="center", va="center", fontsize=9,
                color=INK, linespacing=1.4)
        ax.plot([1.6, 8.4], [3.6, 3.6], color=LINE, linewidth=1.2)
        ax.text(5, 2.2, cost, ha="center", va="center", fontsize=7.8,
                color=GREY, style="italic", linespacing=1.4)
    fig.tight_layout(rect=[0, 0, 1, 0.88])
    return fig


def structural_patterns() -> plt.Figure:
    fig, axes = plt.subplots(1, 4, figsize=(14.5, 4.2), facecolor=WHITE)
    fig.suptitle("Structural Patterns: Four Reasons to Put an Object in Front of Another",
                 fontsize=18, fontweight="bold", color=NAVY, y=0.99)
    patterns = [
        ("Adapter", "Convert an\nincompatible interface", "translate", BLUE),
        ("Decorator", "Add behavior,\nkeep the interface", "augment", GREEN),
        ("Facade", "Simplify a\nmulti-part subsystem", "simplify", AMBER),
        ("Proxy", "Control access to\nthe real object", "guard", RED),
    ]
    for ax, (name, intent, verb, color) in zip(axes, patterns):
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 10)
        ax.axis("off")
        ax.add_patch(FancyBboxPatch((0.5, 0.9), 9.0, 8.3,
                                    boxstyle="round,pad=0.4,rounding_size=0.5",
                                    facecolor=WHITE, edgecolor=color, linewidth=2))
        ax.text(5, 8.1, name, ha="center", va="center", fontsize=13,
                fontweight="bold", color=color)
        ax.text(5, 6.0, intent, ha="center", va="center", fontsize=9,
                color=INK, linespacing=1.4)
        ax.add_patch(FancyBboxPatch((2.2, 3.1), 5.6, 1.5,
                                    boxstyle="round,pad=0.2,rounding_size=0.3",
                                    facecolor=PALE, edgecolor=color, linewidth=1.4))
        ax.text(5, 3.85, verb, ha="center", va="center", fontsize=10,
                fontweight="bold", color=color)
        ax.text(5, 1.7, "same shape, different intent", ha="center",
                va="center", fontsize=7.5, color=GREY, style="italic")
    fig.tight_layout(rect=[0, 0, 1, 0.88])
    return fig


def builder_vs_telescoping() -> plt.Figure:
    fig, axes = plt.subplots(1, 2, figsize=(14, 4.8), facecolor=WHITE)
    fig.suptitle("Builder Replaces Constructor Guesswork with Readable Assembly",
                 fontsize=18, fontweight="bold", color=NAVY, y=1.0)
    left, right = axes
    for ax in axes:
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 10)
        ax.axis("off")

    left.set_title("Telescoping constructors", fontsize=12, fontweight="bold",
                   color=RED, pad=10)
    signatures = [
        "Report(String title)",
        "Report(String, Format)",
        "Report(String, Format, boolean)",
        "Report(String, Format, boolean, int)",
    ]
    for index, signature in enumerate(signatures):
        y = 7.9 - index * 1.55
        left.add_patch(FancyBboxPatch((0.7, y), 8.6, 1.0,
                                      boxstyle="round,pad=0.16,rounding_size=0.25",
                                      facecolor="#FDEDEC", edgecolor=RED,
                                      linewidth=1.5))
        left.text(5, y + 0.5, signature, ha="center", va="center",
                  fontsize=8.5, color=INK, family="monospace")
    left.text(5, 1.15, 'new Report("Q3", PDF, true, 2)', ha="center",
              fontsize=9, color=RED, family="monospace")
    left.text(5, 0.35, "What do true and 2 mean at the call site?",
              ha="center", fontsize=8.5, color=GREY, style="italic")

    right.set_title("Builder with validated build()", fontsize=12,
                    fontweight="bold", color=GREEN, pad=10)
    steps = [
        ("Report.builder()", BLUE),
        ('.title("Q3")', BLUE),
        (".format(PDF)", BLUE),
        (".includeCharts(true)", BLUE),
        (".build()", GREEN),
    ]
    for index, (step, color) in enumerate(steps):
        y = 8.0 - index * 1.42
        right.add_patch(FancyBboxPatch((1.5, y), 7.0, 0.92,
                                       boxstyle="round,pad=0.14,rounding_size=0.25",
                                       facecolor="#E9F7EF" if color == GREEN else PALE,
                                       edgecolor=color, linewidth=1.5))
        right.text(5, y + 0.46, step, ha="center", va="center", fontsize=8.5,
                   color=INK, family="monospace")
        if index < len(steps) - 1:
            right.annotate("", xy=(5, y - 0.44), xytext=(5, y - 0.12),
                           arrowprops=dict(arrowstyle="-|>", color=GREY, lw=1.3))
    right.text(5, 0.5, "build() enforces invariants once, before the object exists",
               ha="center", fontsize=8.5, color=GREEN, style="italic")
    fig.tight_layout(rect=[0, 0, 1, 0.92])
    return fig


def wrapper_family() -> plt.Figure:
    fig, ax = canvas(14, 7)
    heading(ax, "Four Wrappers, One Shape: Tell Them Apart by Intent",
            "Every structural pattern below sits between a client and a target")
    rows = [
        (63, "Adapter", "translates calls", "Target has the\nwrong interface",
         "interface differs", BLUE),
        (45, "Decorator", "adds behavior", "Same interface,\nextra responsibility",
         "interface identical", GREEN),
        (27, "Facade", "narrows surface", "Many parts behind\none entry point",
         "interface simplified", AMBER),
        (9, "Proxy", "controls access", "Same interface,\ngated or deferred",
         "interface identical", RED),
    ]
    for y, name, verb, purpose, note, color in rows:
        box(ax, 4, y, 12, 13, "Client", "", face=WHITE, edge=NAVY)
        box(ax, 26, y, 18, 13, name, verb, face=PALE, edge=color,
            title_color=color)
        arrow(ax, (16.5, y + 6.5), (25.5, y + 6.5), color=GREY)
        if name == "Facade":
            for offset, part in enumerate(["Tax", "Stock", "Ship"]):
                py = y + 9.8 - offset * 4.9
                box(ax, 54, py, 14, 2.4, part, "", face=MIST, edge=NAVY)
                arrow(ax, (44.5, y + 6.5), (53.5, py + 1.2), color=color)
        else:
            box(ax, 54, y, 14, 13, "Target", "", face=MIST, edge=NAVY)
            arrow(ax, (44.5, y + 6.5), (53.5, y + 6.5), color=color)
        ax.text(70, y + 9.5, purpose, ha="left", va="top", fontsize=8.4,
                color=INK, linespacing=1.4)
        ax.text(70, y + 1.5, note, ha="left", va="bottom", fontsize=7.6,
                color=color, style="italic")
    ax.text(50, 2, "Decorator and Proxy look identical in code; intent and lifecycle separate them",
            ha="center", fontsize=9.5, fontweight="bold", color=NAVY)
    return fig


def payment_gateway_architecture() -> plt.Figure:
    fig, ax = canvas(15, 7.4)
    heading(ax, "Payment Gateway: Patterns Earn Their Place at a Volatile Boundary",
            "Each wrapper exists because a specific change was expected")
    box(ax, 3, 62, 13, 15, "Checkout", "calls one entry point", face=WHITE,
        edge=NAVY)
    box(ax, 22, 62, 16, 15, "PaymentFacade", "facade", face=MIST, edge=AMBER,
        title_color=AMBER)
    box(ax, 44, 62, 16, 15, "ChargeRequest", "builder + validation",
        face=WHITE, edge=BLUE, title_color=BLUE)
    arrow(ax, (16.5, 69.5), (21.5, 69.5))
    arrow(ax, (38.5, 69.5), (43.5, 69.5), label="builds")

    box(ax, 22, 36, 16, 15, "ProviderFactory", "picks by country", face=WHITE,
        edge=GREEN, title_color=GREEN)
    arrow(ax, (30, 61.5), (30, 51.5), color=GREEN, label="resolve")

    box(ax, 46, 36, 15, 15, "RetryDecorator", "decorator", face="#E9F7EF",
        edge=GREEN, title_color=GREEN)
    box(ax, 67, 36, 15, 15, "AuditProxy", "proxy", face="#FDEDEC", edge=RED,
        title_color=RED)
    box(ax, 87, 36, 11, 15, "Adapter", "per SDK", face=PALE, edge=BLUE,
        title_color=BLUE)
    arrow(ax, (38.5, 43.5), (45.5, 43.5), color=GREY)
    arrow(ax, (61.5, 43.5), (66.5, 43.5), color=GREY)
    arrow(ax, (82.5, 43.5), (86.5, 43.5), color=GREY)

    box(ax, 80, 8, 18, 15, "Provider SDK", "third-party detail", face=WHITE,
        edge=GREY, title_color=GREY)
    arrow(ax, (92, 35.5), (92, 23.5), color=BLUE)

    ax.text(3, 28, "PaymentGateway interface", fontsize=9, fontweight="bold",
            color=NAVY)
    ax.text(3, 22, "One contract shared by every\nwrapper in the chain",
            fontsize=8.2, color=INK, linespacing=1.4)
    ax.text(3, 11, "Substitution stays safe only if\nevery link preserves error\nsemantics",
            fontsize=8.2, color=RED, linespacing=1.4)
    ax.text(72, 57, "decorate  →  guard  →  translate", ha="center",
            fontsize=9.5, fontweight="bold", color=NAVY)
    return fig


FIGURES = {
    "patterns_mental_model": patterns_mental_model,
    "creational_patterns": creational_patterns,
    "structural_patterns": structural_patterns,
    "builder_vs_telescoping": builder_vs_telescoping,
    "wrapper_family": wrapper_family,
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
