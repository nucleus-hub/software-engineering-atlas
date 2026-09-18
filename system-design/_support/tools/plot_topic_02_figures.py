"""Render visual diagrams for Topic 02: OOP principles and clean code."""

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

ASSETS = Path(__file__).resolve().parent.parent.parent / "basics" / "assets" / "topic-02"


def save(name: str, fig: plt.Figure) -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    output = ASSETS / f"{name}.png"
    fig.savefig(output, dpi=DPI, bbox_inches="tight", facecolor=WHITE)
    plt.close(fig)
    print(f"wrote basics/assets/topic-02/{output.name}")


def oop_mental_model() -> plt.Figure:
    fig, ax = canvas(14, 5.8)
    heading(ax, "Object Design: Protect State, Expose Behavior, Compose Change",
            "Good boundaries keep invariants local and variation replaceable")
    stages = [
        (4, "Encapsulate", "protect invariants", NAVY, PALE),
        (23, "Abstract", "small contracts", BLUE, PALE),
        (42, "Polymorphism", "swap behavior", GREEN, "#E9F7EF"),
        (61, "Compose", "assemble capabilities", AMBER, "#FFF5DC"),
        (80, "Evolve", "local change", NAVY, MIST),
    ]
    for index, (x, title, subtitle, color, face) in enumerate(stages):
        box(ax, x, 43, 15, 23, title, subtitle, face=face, edge=color,
            title_color=color)
        ax.add_patch(Circle((x + 7.5, 73), 3, facecolor=color, edgecolor=color))
        ax.text(x + 7.5, 73, str(index + 1), ha="center", va="center",
                fontsize=8, fontweight="bold", color=WHITE)
        if index < len(stages) - 1:
            arrow(ax, (x + 15.5, 54.5), (stages[index + 1][0] - 0.5, 54.5),
                  color=GREY)
    ax.text(50, 26, "DESIGN OUTCOME", ha="center", fontsize=8,
            fontweight="bold", color=GREY)
    box(ax, 29, 10, 42, 12,
        "A change affects the smallest reasonable set of classes",
        face=WHITE, edge=NAVY)
    return fig


def solid_principles() -> plt.Figure:
    fig, axes = plt.subplots(1, 5, figsize=(15, 5.2), facecolor=WHITE)
    fig.suptitle("SOLID: Five Questions About the Shape of Change",
                 fontsize=19, fontweight="bold", color=NAVY, y=0.98)
    principles = [
        ("S", "Single\nResponsibility", "One reason\nto change", NAVY),
        ("O", "Open / Closed", "Extend without\nediting stable code", BLUE),
        ("L", "Liskov\nSubstitution", "Subtypes preserve\nexpectations", GREEN),
        ("I", "Interface\nSegregation", "Depend only on\nwhat you use", AMBER),
        ("D", "Dependency\nInversion", "Policy depends on\nabstractions", RED),
    ]
    for ax, (letter, title, prompt, color) in zip(axes, principles):
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 10)
        ax.axis("off")
        ax.add_patch(FancyBboxPatch((0.6, 0.8), 8.8, 7.8,
                                   boxstyle="round,pad=0.4,rounding_size=0.5",
                                   facecolor=PALE, edgecolor=color, linewidth=2))
        ax.add_patch(Circle((5, 7.3), 1.15, facecolor=color, edgecolor=color))
        ax.text(5, 7.3, letter, ha="center", va="center", fontsize=18,
                fontweight="bold", color=WHITE)
        ax.text(5, 5.0, title, ha="center", va="center", fontsize=10,
                fontweight="bold", color=NAVY)
        ax.text(5, 2.5, prompt, ha="center", va="center", fontsize=8.5,
                color=INK, linespacing=1.4)
    fig.tight_layout(rect=[0, 0, 1, 0.9])
    return fig


def clean_code_guardrails() -> plt.Figure:
    fig, axes = plt.subplots(1, 3, figsize=(14, 5), facecolor=WHITE)
    fig.suptitle("DRY, KISS, and YAGNI Guard Different Failure Modes",
                 fontsize=19, fontweight="bold", color=NAVY, y=0.98)
    cards = [
        ("DRY", "Knowledge duplicated", "One rule, one source",
         "Do not merge code that merely looks alike", BLUE),
        ("KISS", "Accidental complexity", "Simplest clear design",
         "Simple is not simplistic", GREEN),
        ("YAGNI", "Speculative capability", "Build proven needs",
         "Keep an evolution path, not unused machinery", AMBER),
    ]
    for ax, (name, smell, action, caution, color) in zip(axes, cards):
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 10)
        ax.axis("off")
        ax.add_patch(FancyBboxPatch((0.5, 0.8), 9, 7.6,
                                   boxstyle="round,pad=0.5,rounding_size=0.5",
                                   facecolor=WHITE, edgecolor=color, linewidth=2))
        ax.text(5, 7.2, name, ha="center", fontsize=18, fontweight="bold",
                color=color)
        ax.text(5, 5.6, f"Prevents: {smell}", ha="center", fontsize=9,
                fontweight="bold", color=NAVY)
        ax.text(5, 4.0, action, ha="center", fontsize=10, color=INK)
        ax.plot([2, 8], [3.1, 3.1], color=LINE, linewidth=1.5)
        ax.text(5, 2.0, caution, ha="center", va="center", fontsize=8,
                color=GREY, style="italic", wrap=True)
    fig.tight_layout(rect=[0, 0, 1, 0.9])
    return fig


def composition_vs_inheritance() -> plt.Figure:
    fig, axes = plt.subplots(1, 2, figsize=(14, 6), facecolor=WHITE)
    fig.suptitle("Inheritance Reuses Identity; Composition Reuses Capability",
                 fontsize=19, fontweight="bold", color=NAVY, y=0.98)

    left, right = axes
    for ax in axes:
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 10)
        ax.axis("off")

    left.set_title("Inheritance — stable 'is-a' relationship", fontsize=12,
                   fontweight="bold", color=NAVY, pad=12)
    for y, title, subtitle in [
        (7.2, "Bird", "fly()"),
        (4.6, "Penguin", "inherits fly()?"),
        (2.0, "Runtime surprise", "contract is broken"),
    ]:
        color = RED if y == 2.0 else BLUE
        face = "#FDEDEC" if y == 2.0 else PALE
        left.add_patch(FancyBboxPatch((2.5, y), 5, 1.25,
                                     boxstyle="round,pad=0.25,rounding_size=0.25",
                                     facecolor=face, edgecolor=color, linewidth=1.8))
        left.text(5, y + 0.82, title, ha="center", fontsize=9.5,
                  fontweight="bold", color=color)
        left.text(5, y + 0.3, subtitle, ha="center", fontsize=7.5, color=INK)
    left.annotate("inherits", xy=(5, 7.15), xytext=(5, 5.9), ha="center",
                  arrowprops=dict(arrowstyle="-|>", color=BLUE, lw=1.6),
                  fontsize=7.5, color=BLUE)
    left.annotate("violates expectation", xy=(5, 3.35), xytext=(5, 4.55),
                  ha="center", arrowprops=dict(arrowstyle="-|>", color=RED, lw=1.6),
                  fontsize=7.5, color=RED)

    right.set_title("Composition — replaceable 'has-a' capability", fontsize=12,
                    fontweight="bold", color=NAVY, pad=12)
    right.add_patch(FancyBboxPatch((0.7, 4.2), 3.2, 2,
                                  boxstyle="round,pad=0.3,rounding_size=0.3",
                                  facecolor=MIST, edgecolor=BLUE, linewidth=1.8))
    right.text(2.3, 5.35, "Bird", ha="center", fontsize=10,
               fontweight="bold", color=NAVY)
    right.text(2.3, 4.7, "has FlyBehavior", ha="center", fontsize=8, color=INK)
    for y, title, color in [(6.8, "WingedFlight", GREEN), (3.9, "NoFlight", AMBER),
                            (1.0, "RocketFlight", RED)]:
        right.add_patch(FancyBboxPatch((6.0, y), 3.3, 1.35,
                                      boxstyle="round,pad=0.25,rounding_size=0.25",
                                      facecolor=WHITE, edgecolor=color, linewidth=1.8))
        right.text(7.65, y + 0.68, title, ha="center", va="center",
                   fontsize=8.5, fontweight="bold", color=color)
        right.annotate("", xy=(5.9, y + 0.68), xytext=(4.0, 5.2),
                       arrowprops=dict(arrowstyle="-|>", color=color, lw=1.5))
    right.text(5, 0.2, "Behavior changes without changing Bird's identity",
               ha="center", fontsize=8.5, color=GREY, style="italic")
    fig.tight_layout(rect=[0, 0, 1, 0.9])
    return fig


def design_smells() -> plt.Figure:
    fig, ax = canvas(14, 6.5)
    heading(ax, "Design Smells Point to Boundary Problems",
            "Use principles as diagnostic tools—not compliance badges")
    box(ax, 38, 39, 24, 22, "Change is expensive", "large blast radius",
        face=MIST, edge=NAVY)
    smells = [
        (4, 63, "God class", "split responsibilities", RED),
        (4, 18, "Shotgun surgery", "centralize knowledge", AMBER),
        (76, 63, "Fat interface", "segregate clients", BLUE),
        (76, 18, "Concrete coupling", "invert dependency", GREEN),
    ]
    for x, y, title, remedy, color in smells:
        box(ax, x, y, 20, 16, title, remedy, face=WHITE, edge=color,
            title_color=color)
        start = (x + 20.5, y + 8) if x < 50 else (x - 0.5, y + 8)
        end = (37.5, 50) if x < 50 else (62.5, 50)
        arrow(ax, start, end, color=color)
    ax.text(50, 24, "Ask: which future change forces unrelated code to move?",
            ha="center", fontsize=10, fontweight="bold", color=NAVY)
    ax.text(50, 16, "Refactor only when the pressure is real and understood.",
            ha="center", fontsize=9, color=GREY, style="italic")
    return fig


def notification_architecture() -> plt.Figure:
    fig, ax = canvas(15, 7)
    heading(ax, "Notification Service: Policy Depends on Small Contracts",
            "Composition adds channels without editing orchestration")
    box(ax, 3, 58, 13, 17, "Caller", "send(request)", face=WHITE, edge=NAVY)
    box(ax, 23, 58, 17, 17, "NotificationService", "validate + orchestrate", face=MIST)
    box(ax, 47, 58, 15, 17, "Sender", "interface / port", face=PALE, edge=NAVY)
    arrow(ax, (16.5, 66.5), (22.5, 66.5))
    arrow(ax, (40.5, 66.5), (46.5, 66.5), label="depends on")

    adapters = [
        (72, "EmailSender", BLUE),
        (49, "SmsSender", GREEN),
        (26, "PushSender", AMBER),
    ]
    for y, title, color in adapters:
        box(ax, 71, y, 17, 14, title, "adapter", face=WHITE, edge=color,
            title_color=color)
        arrow(ax, (62.5, 66.5), (70.5, y + 7), color=color,
              label="implemented by" if y == 72 else "", curve=(59 - y) / 90)

    box(ax, 23, 27, 17, 14, "Template", "encapsulated data", face=WHITE, edge=BLUE)
    box(ax, 47, 27, 15, 14, "RetryPolicy", "composed behavior", face=WHITE, edge=AMBER)
    arrow(ax, (31.5, 57.5), (31.5, 41.5), color=BLUE, label="has-a")
    arrow(ax, (40.5, 62), (54.5, 41.5), color=AMBER, label="has-a")

    ax.text(50, 12, "New channel = new Sender implementation; stable policy stays closed to edits",
            ha="center", fontsize=10, fontweight="bold", color=NAVY)
    return fig


FIGURES = {
    "oop_mental_model": oop_mental_model,
    "solid_principles": solid_principles,
    "clean_code_guardrails": clean_code_guardrails,
    "composition_vs_inheritance": composition_vs_inheritance,
    "design_smells": design_smells,
    "notification_architecture": notification_architecture,
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
