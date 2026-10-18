"""Render the diagrams for Topic 02: OOP principles and clean code.

Run from the system-design directory (optionally pass figure names):

    uv run --with matplotlib \
      --index-url https://pypi.ci.artifacts.walmart.com/artifactory/api/pypi/external-pypi/simple \
      --allow-insecure-host pypi.ci.artifacts.walmart.com \
      python _support/tools/plot_topic_02_figures.py
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
    box,
    canvas,
    card_row,
    heading,
    stage_row,
)

ASSETS = Path(__file__).resolve().parent.parent.parent / "basics" / "assets" / "topic-02"


def save(name: str, fig: plt.Figure) -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    output = ASSETS / f"{name}.png"
    fig.savefig(output, dpi=DPI, bbox_inches="tight", facecolor=WHITE)
    plt.close(fig)
    print(f"wrote basics/assets/topic-02/{output.name}")


def panel_title(ax: plt.Axes, x: float, text: str, color: str = NAVY) -> None:
    ax.text(x, 79, text, ha="center", va="center", fontsize=10, fontweight="bold", color=color)


def policy_boundary(ax: plt.Axes, x0: float, x1: float, y: float) -> None:
    """Dashed line separating business logic (above) from swappable plug-ins (below)."""
    ax.plot([x0, x1], [y, y], color=GREY, linewidth=1.2, linestyle=(0, (5, 4)))
    ax.text(x0, y + 1.8, "BUSINESS LOGIC: changes rarely", ha="left", va="bottom",
            fontsize=7.5, fontweight="bold", color=NAVY)
    ax.text(x0, y - 1.8, "PLUG-INS: vendors and tools", ha="left", va="top",
            fontsize=7.5, fontweight="bold", color=NAVY)


def lld_interview_framework() -> plt.Figure:
    fig, ax = canvas(14, 5.4)
    heading(ax, "From Vague Prompt to Extensible Design",
            "Each stage leaves an artifact the interviewer can see and challenge")
    steps = [
        ("01", "Clarify", "use cases + scope"),
        ("02", "Model", "entities + roles"),
        ("03", "Contract", "interfaces + rules"),
        ("04", "Relate", "class diagram"),
        ("05", "Code", "core flow"),
        ("06", "Extend", "change + tests"),
    ]
    stage_row(ax, steps, [4, 20, 36, 52, 68, 84], y=39, width=12, height=24, highlight=(4, 5))
    ax.text(50, 25, "OUTPUT", ha="center", va="center", fontsize=8, fontweight="bold", color=GREY)
    box(ax, 21, 10, 58, 11, "A design where the next requirement is a new class, not an edit",
        face=WHITE, edge=NAVY)
    return fig


def oop_mental_model() -> plt.Figure:
    fig, ax = canvas(14, 5.4)
    heading(ax, "Object Design: Protect State, Expose Behavior, Compose Change",
            "Good boundaries keep invariants local and variation replaceable")
    stages = [
        ("1", "Encapsulate", "protect invariants"),
        ("2", "Abstract", "hide the how"),
        ("3", "Substitute", "one contract, many impls"),
        ("4", "Compose", "assemble capabilities"),
        ("5", "Evolve", "change stays local"),
    ]
    stage_row(ax, stages, [4, 23, 42, 61, 80], y=39, width=15, height=24, highlight=(4,))
    ax.text(50, 25, "DESIGN OUTCOME", ha="center", va="center", fontsize=8,
            fontweight="bold", color=GREY)
    box(ax, 23, 10, 54, 11, "A change affects the smallest reasonable set of classes",
        face=WHITE, edge=NAVY)
    return fig


def coupling_cohesion() -> plt.Figure:
    fig, ax = canvas(13, 7.6)
    heading(ax, "Coupling and Cohesion: The Two Dials of Every Boundary",
            "Things that change together live together; everything else talks through narrow contracts")
    quadrants = [
        (14, 45, "Modular", "the goal: a change stays local",
         "e.g. a Notification that validates itself", GREEN, GREEN_FACE),
        (55, 45, "Tangled modules", "right pieces, wired too tightly",
         "e.g. services sharing database tables", AMBER, AMBER_FACE),
        (14, 9, "Junk drawer", "unrelated code, loosely grouped",
         "e.g. StringUtils, CommonHelper", AMBER, AMBER_FACE),
        (55, 9, "Big ball of mud", "every change ripples everywhere",
         "e.g. an OrderManager that does it all", RED, RED_FACE),
    ]
    for x, y, title, subtitle, example, edge, face in quadrants:
        box(ax, x, y, 38, 31, title, subtitle, face=face, edge=edge)
        ax.text(x + 19, y + 6.5, example, ha="center", va="center", fontsize=8,
                color=INK, style="italic")
    arrow(ax, (14, 3), (93, 3), color=GREY)
    ax.text(53.5, 0.5, "COUPLING: how far a change here forces change elsewhere  \u2192",
            ha="center", va="top", fontsize=8.5, fontweight="bold", color=NAVY)
    arrow(ax, (9, 9), (9, 76), color=GREY)
    ax.text(6, 42.5, "COHESION: how related the code inside is  \u2192", rotation=90,
            ha="center", va="center", fontsize=8.5, fontweight="bold", color=NAVY)
    return fig


SOLID = [
    ("S", "Single Responsibility", "One class, one job:\none reason to change",
     "Different teams keep\nediting the same class", NAVY, PALE),
    ("O", "Open / Closed", "Add new behavior by\nadding a new class",
     "Every new case means\nediting an if or switch", BLUE, PALE),
    ("L", "Liskov Substitution", "A subclass must work\nwherever its parent does",
     "A subclass throws or\ndoes nothing instead", GREEN, GREEN_FACE),
    ("I", "Interface Segregation", "Keep interfaces small,\nshaped by their callers",
     "Classes forced to write\nmethods they never use", AMBER, AMBER_FACE),
    ("D", "Dependency Inversion", "Depend on interfaces,\nnot on vendors or tools",
     "Business code calls\nnew TwilioClient() itself", RED, RED_FACE),
]


def solid_principles() -> plt.Figure:
    fig, ax = canvas(15, 6.6)
    heading(ax, "SOLID: Five Rules That Keep Changes Small",
            "Each rule in plain words, and the warning sign that it is being broken")
    card_row(ax, SOLID, ("RULE", "WARNING SIGN"))
    return fig


def dependency_inversion() -> plt.Figure:
    fig, ax = canvas(14, 6.6)
    heading(ax, "Dependency Inversion: The Business Code Owns the Interface",
            "Vendors plug in from below, so they can be swapped, or faked in tests")
    ax.plot([46, 46], [4, 82], color=LINE, linewidth=1.5)
    panel_title(ax, 23, "BEFORE: business code depends on the vendor", RED)
    panel_title(ax, 73, "AFTER: the vendor plugs into an interface", GREEN)

    box(ax, 12, 52, 22, 13, "NotificationService", "business logic")
    box(ax, 12, 20, 22, 13, "TwilioClient", "SMS vendor's library", face=RED_FACE, edge=RED)
    arrow(ax, (23, 51.5), (23, 33.5), color=RED)
    ax.text(24.5, 42.5, "new TwilioClient(...)", ha="left", va="center", fontsize=8, color=RED)
    ax.text(23, 9, "Can't test without sending real texts;\nswitching vendor means editing the service",
            ha="center", va="center", fontsize=8.5, color=RED, linespacing=1.4)

    policy_boundary(ax, 49, 98, 43)
    box(ax, 50, 52, 18, 13, "NotificationService", "business logic")
    box(ax, 74, 52, 22, 13, "Sender", "interface the service owns", edge=NAVY)
    arrow(ax, (68.5, 58.5), (73.5, 58.5), color=NAVY, label="uses")
    box(ax, 58, 18, 17, 13, "SmsSender", "wraps Twilio", face=GREEN_FACE, edge=GREEN)
    box(ax, 80, 18, 16, 13, "FakeSender", "used in tests", face=WHITE)
    arrow(ax, (66.5, 31.5), (80, 51.5), color=GREEN, dashed=True)
    arrow(ax, (88, 31.5), (88, 51.5), color=BLUE, dashed=True)
    ax.text(89.5, 37, "implements", ha="left", va="center", fontsize=7.5, color=GREY)
    ax.text(73, 7, "Both plug-ins point UP at the interface: that flip is the \"inversion\"",
            ha="center", va="center", fontsize=8.5, fontweight="bold", color=GREEN)
    return fig


def composition_vs_inheritance() -> plt.Figure:
    fig, ax = canvas(14, 6.4)
    heading(ax, "Inheritance Reuses Identity; Composition Reuses Capability",
            "If a subclass must override a method to throw or do nothing, it was never an is-a")
    ax.plot([50, 50], [4, 82], color=LINE, linewidth=1.5)
    panel_title(ax, 25, "INHERITANCE: is-a, fixed at compile time")
    panel_title(ax, 75, "COMPOSITION: has-a, chosen at runtime")

    box(ax, 13, 56, 24, 13, "Bird", "promises fly()")
    box(ax, 13, 33, 24, 13, "Penguin extends Bird", "overrides fly() to throw")
    box(ax, 13, 10, 24, 13, "Runtime surprise", "bird.fly() crashes the caller",
        face=RED_FACE, edge=RED)
    arrow(ax, (25, 46.5), (25, 55.5))
    ax.text(26.5, 51, "extends", ha="left", va="center", fontsize=8, color=BLUE)
    arrow(ax, (25, 32.5), (25, 23.5), color=RED)
    ax.text(26.5, 28, "breaks callers", ha="left", va="center", fontsize=8, color=RED)

    box(ax, 55, 37, 16, 16, "Bird", "has a FlyBehavior", face=MIST)
    for y, title, subtitle, color, face in [
        (61, "WingedFlight", "sparrow", GREEN, GREEN_FACE),
        (39, "NoFlight", "penguin: no override", AMBER, AMBER_FACE),
        (17, "FakeFlight", "test double", BLUE, PALE),
    ]:
        box(ax, 79, y, 17, 12, title, subtitle, face=face, edge=color)
        arrow(ax, (71.5, 45), (78.5, y + 6), color=color)
    ax.text(75, 7, "A penguin is just new Bird(new NoFlight())", ha="center", va="center",
            fontsize=8.5, color=INK, style="italic")
    return fig


def clean_code_guardrails() -> plt.Figure:
    fig, ax = canvas(14, 5.2)
    heading(ax, "DRY, KISS, and YAGNI Pull From Opposite Ends",
            "Too little abstraction duplicates knowledge; too much buries it. Evidence picks the spot")
    zones = [
        (5, "Under-abstracted", "copy-pasted rules, type switches", RED, RED_FACE),
        (36.5, "Just enough", "one owner per rule; proven seams", GREEN, GREEN_FACE),
        (68, "Over-abstracted", "speculative interfaces, plugin frameworks", RED, RED_FACE),
    ]
    for x, title, subtitle, edge, face in zones:
        box(ax, x, 32, 27, 17, title, subtitle, face=face, edge=edge)
    arrow(ax, (8, 64), (36, 64), color=BLUE, label="DRY: give every rule one home")
    arrow(ax, (92, 64), (64, 64), color=AMBER, label="KISS + YAGNI: every layer must earn its place")
    for x, note in [(18.5, "DRY misused: merging code\nthat only looks alike"),
                    (81.5, "KISS/YAGNI misused: skipping\na cheap, obvious seam")]:
        ax.text(x, 22, note, ha="center", va="top", fontsize=8.5, color=INK,
                style="italic", linespacing=1.4)
    ax.text(50, 22, "Rule of three: abstract on the\nthird real case, not the first guess",
            ha="center", va="top", fontsize=9.5, fontweight="bold", color=GREEN, linespacing=1.4)
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
    fig, ax = canvas(15, 7.6)
    heading(ax, "Notification Service: Business Logic Above, Plug-ins Below",
            "New channels plug in below the line; nothing above it is edited")
    box(ax, 6, 60, 21, 13, "PreferencePolicy", "opt-outs, quiet hours")
    box(ax, 39.5, 60, 21, 13, "NotificationService", "orchestrates only", face=MIST)
    box(ax, 73, 60, 21, 13, "RetryPolicy", "bounded; retryable only", face=AMBER_FACE, edge=AMBER)
    arrow(ax, (39, 66.5), (27.5, 66.5), label="has-a")
    arrow(ax, (61, 66.5), (72.5, 66.5), color=AMBER, label="has-a")
    box(ax, 39.5, 37, 21, 12, "Sender", "interface: send() returns SendResult", edge=NAVY)
    arrow(ax, (50, 59.5), (50, 49.5), color=NAVY)
    ax.text(51.5, 54.5, "depends on", ha="left", va="center", fontsize=8, color=NAVY)

    policy_boundary(ax, 4, 96, 31)
    senders = [(5, "EmailSender", "SMTP provider"), (28.5, "SmsSender", "SMS gateway"),
               (52, "PushSender", "APNs / FCM")]
    for (x, title, subtitle), end_x in zip(senders, (44, 48, 52)):
        box(ax, x, 9, 19, 12, title, subtitle, face=WHITE)
        arrow(ax, (x + 9.5, 21.5), (end_x, 36.5), dashed=True)
    box(ax, 75.5, 9, 19, 12, "WhatsAppSender", "added later: one new class",
        face=GREEN_FACE, edge=GREEN)
    arrow(ax, (85, 21.5), (56, 36.5), color=GREEN, dashed=True)
    ax.text(50, 2.5, "Dashed arrows: implements.   Solid arrows: depends on / has-a.",
            ha="center", va="center", fontsize=8, color=INK, style="italic")
    return fig


FIGURES = {
    "lld_interview_framework": lld_interview_framework,
    "oop_mental_model": oop_mental_model,
    "coupling_cohesion": coupling_cohesion,
    "solid_principles": solid_principles,
    "dependency_inversion": dependency_inversion,
    "composition_vs_inheritance": composition_vs_inheritance,
    "clean_code_guardrails": clean_code_guardrails,
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
