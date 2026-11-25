"""Render the diagrams for Topic 08: Load Balancing & Proxying.

Run from the system-design directory (optionally pass figure names):

    uv run --with matplotlib \
      --index-url https://pypi.ci.artifacts.walmart.com/artifactory/api/pypi/external-pypi/simple \
      --allow-insecure-host pypi.ci.artifacts.walmart.com \
      python _support/tools/plot_topic_08_figures.py
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
    WHITE,
    arrow,
    box,
    canvas,
    caps,
    heading,
    note,
    panel,
    render,
)

TOPIC = "topic-08"

# Numbers shared with the doc, so the pictures and the text cannot drift apart.
PEAK_LEDGER_CALLS = 55_000
POD_CAPACITY = 8_000
L4_CONNECTIONS = [10, 5, 8, 6, 9, 4]          # 42 Wallet API connections on the 6 old pods
NEW_PODS = 6
SLOW_POD = {"total": 3_000, "fast_ms": 10, "slow_ms": 50}


def _style_chart(ax: plt.Axes, title: str, ylabel: str) -> None:
    """Shared look for the bar charts: navy title, light grid, no box."""
    ax.set_title(title, fontsize=11.5, fontweight="bold", color=NAVY, pad=12)
    ax.set_ylabel(ylabel, fontsize=9.5, color=INK)
    ax.grid(axis="y", color=LINE, linewidth=0.8)
    ax.set_axisbelow(True)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(GREY)
    ax.tick_params(colors=INK, labelsize=8.5)


def _pod_stack(ax: plt.Axes, x: float, ys: tuple[float, ...], label: str, *,
               edge: str = BLUE, face: str = PALE, width: float = 16) -> None:
    """A column of small, identical pod boxes."""
    for index, y in enumerate(ys):
        box(ax, x, y, width, 5.5, f"{label} {index + 1}", face=face, edge=edge,
            radius=0.8, linewidth=1.4)


def l4_vs_l7() -> plt.Figure:
    fig, ax = canvas(15, 9.5)
    heading(ax, "What Each Load Balancer Sees",
            "The same transfer, from Asha's phone, through each kind of load balancer")

    # Layer 4 row.
    caps(ax, 2, 81, "LAYER 4  ·  BALANCES CONNECTIONS", ha="left", color=BLUE, size=10)
    box(ax, 2, 60, 11, 9, "Asha's phone")
    arrow(ax, (13.6, 64.5), (19.4, 64.5), color=BLUE)
    panel(ax, 20, 53, 28, 23, "WHAT IT SEES",
          "from  100.64.3.9 : 51234\nto    203.0.113.10 : 443\n\n"
          "#### encrypted bytes ####\n(it never reads them)",
          face=WHITE, edge=BLUE, title_color=BLUE, mono=True)
    arrow(ax, (48.6, 64.5), (53.4, 64.5), color=BLUE)
    box(ax, 54, 59, 15, 11, "L4 load balancer", "picks once per connection")
    _pod_stack(ax, 79, (71, 62, 53), "pod")
    arrow(ax, (69.6, 64.5), (78.4, 64.5), color=BLUE)
    note(ax, 74, 58.5, "requests 1, 2, 3...\nall go to pod 2", color=BLUE, size=8)

    ax.plot([2, 98], [47, 47], color=LINE, linewidth=1.2)

    # Layer 7 row.
    caps(ax, 2, 42, "LAYER 7  ·  BALANCES REQUESTS", ha="left", color=NAVY, size=10)
    box(ax, 2, 19, 11, 9, "Asha's phone")
    arrow(ax, (13.6, 23.5), (19.4, 23.5), color=NAVY)
    panel(ax, 20, 9, 28, 27, "WHAT IT SEES",
          "POST /v1/transfers\nHost: api.wallet.example\nAuthorization: Bearer eyJ...\n"
          "Idempotency-Key: 7f3a...\n\n{ \"to\": \"ravi\",\n  \"amount\": \"25.00\" }",
          face=MIST, edge=NAVY, mono=True)
    arrow(ax, (48.6, 23.5), (53.4, 23.5), color=NAVY)
    box(ax, 54, 18, 15, 11, "L7 load balancer", "ends TLS, reads HTTP", face=MIST,
        edge=NAVY)
    box(ax, 77, 28, 20, 9, "Wallet API pool", "least-busy of 42 pods")
    box(ax, 77, 8, 20, 9, "Webhook pool", "card network only", face=GREEN_FACE,
        edge=GREEN, title_color=GREEN)
    arrow(ax, (69.6, 26), (76.4, 32), color=NAVY)
    note(ax, 72.5, 33, "/v1/", color=NAVY, size=8.2)
    arrow(ax, (69.6, 21), (76.4, 13), color=GREEN)
    note(ax, 71.5, 12.5, "/webhooks/", color=GREEN, size=8.2)
    note(ax, 87, 3, "a new choice for every request", color=NAVY, size=8.2)
    return fig


def grpc_pinning() -> plt.Figure:
    fig, (left, right) = plt.subplots(1, 2, figsize=(14, 6.2), sharey=True,
                                      facecolor=WHITE)
    fig.suptitle("Why the Ledger's New Pods Sat Idle", fontsize=17, fontweight="bold",
                 color=NAVY, y=1.02)
    per_connection = PEAK_LEDGER_CALLS / sum(L4_CONNECTIONS)
    pods = [f"{n}" for n in range(1, len(L4_CONNECTIONS) + NEW_PODS + 1)]

    l4_load = [count * per_connection for count in L4_CONNECTIONS] + [0] * NEW_PODS
    colors = [RED if load > POD_CAPACITY else BLUE for load in l4_load]
    left.bar(pods, l4_load, color=colors, width=0.7)
    for index, count in enumerate(L4_CONNECTIONS):   # inside the bar, clear of the capacity line
        left.text(index, l4_load[index] - 900, f"{count}\nconn", ha="center", fontsize=8,
                  color=WHITE, fontweight="bold", linespacing=1.2)
    left.text(8.5, 1_800, "6 new pods:\nno connections,\nno traffic", ha="center",
              fontsize=9, color=GREY, linespacing=1.4)
    _style_chart(left, "Layer 4 (Kubernetes Service): one choice per connection",
                 "calls per second at peak")

    even = PEAK_LEDGER_CALLS / len(pods)
    right.bar(pods, [even] * len(pods), color=GREEN, width=0.7)
    right.text(5.5, even + 500, f"about {round(even, -2):,.0f} each", ha="center",
               fontsize=9, color=GREEN)
    _style_chart(right, "Per-call balancing (Envoy or client-side)", "")

    for ax in (left, right):
        ax.axhline(POD_CAPACITY, color=AMBER, linestyle="--", linewidth=1.6)
        ax.set_xlabel("Ledger pod", fontsize=9.5, color=INK)
        ax.set_ylim(0, 14_500)
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda value, _: f"{value:,.0f}"))
    left.text(11.4, POD_CAPACITY + 300, "pod capacity 8,000/s", ha="right", fontsize=8.5,
              color=AMBER)
    fig.text(0.5, -0.04, "Same 55,000 calls per second and the same 12 pods. Only the "
             "balancing changed.", ha="center", fontsize=10, color=INK, style="italic")
    fig.tight_layout()
    return fig


def forward_vs_reverse_proxy() -> plt.Figure:
    fig, ax = canvas(15, 6.6)
    ax.set_ylim(22, 100)        # nothing is drawn below y=24, so crop the empty band
    heading(ax, "Forward Proxy vs Reverse Proxy", "Same idea, a middleman. Different side.")
    ax.plot([50, 50], [24, 84], color=LINE, linewidth=1.2)

    # Forward proxy: acts for the wallet's own Payouts pods.
    caps(ax, 25, 82, "FORWARD (EGRESS) PROXY  ·  ACTS FOR THE CLIENTS", color=AMBER, size=9.5)
    for index, ip in enumerate(("10.0.3.21", "10.0.4.87", "10.0.5.12")):
        y = 64 - index * 13
        box(ax, 2, y, 12, 9, "Payouts pod", ip, face=PALE, radius=0.8)
        arrow(ax, (14.6, y + 4.5), (19.4, 52), color=AMBER)
    panel(ax, 20, 38, 14, 28, "Egress proxy ×2",
          "198.51.100.7\n198.51.100.8\n\nholds the wallet's\nclient certificate\n"
          "logs every call\nknown hosts only", face=AMBER_FACE, edge=AMBER, title_color=AMBER)
    box(ax, 39, 47, 9, 10, "Bank", "allowlist")
    arrow(ax, (34.6, 52), (38.4, 52), color=AMBER)
    note(ax, 25, 30, "The bank sees only two fixed addresses.\nPayouts pods can come and go "
         "with every deployment.", size=9)

    # Reverse proxy: acts for the Wallet API pods.
    caps(ax, 75, 82, "REVERSE PROXY  ·  ACTS FOR THE SERVERS", color=NAVY, size=9.5)
    for index, name in enumerate(("Asha's phone", "Ravi's phone")):
        y = 60 - index * 16
        box(ax, 52, y, 11, 7, name, radius=0.8)
        arrow(ax, (63.6, y + 3.5), (67.4, 52), color=NAVY)
    panel(ax, 68, 38, 14, 28, "Reverse proxy",
          "api.wallet.example\n\nends TLS\nsize and time limits\nbuffers slow phones\n"
          "routes by path", face=MIST, edge=NAVY)
    _pod_stack(ax, 87, (64, 52, 40), "pod", width=10)
    for y in (66.75, 54.75, 42.75):
        arrow(ax, (82.6, 52), (86.4, y), color=NAVY)
    note(ax, 75, 30, "Phones see only api.wallet.example.\nThey never learn how many pods "
         "are behind it.", size=9)
    return fig


def lb_strategies() -> plt.Figure:
    total, fast, slow = SLOW_POD["total"], SLOW_POD["fast_ms"], SLOW_POD["slow_ms"]
    round_robin = [total / 3] * 3
    # Least-request keeps in-flight calls equal, so each pod's rate is proportional to 1/latency.
    weights = [1 / fast, 1 / fast, 1 / slow]
    least_request = [total * weight / sum(weights) for weight in weights]

    def summary(rates: list[float]) -> tuple[float, float]:
        latencies = (fast, fast, slow)
        slow_share = rates[2] / total
        average = sum(rate * ms for rate, ms in zip(rates, latencies)) / total
        return slow_share, average

    fig, (left, right) = plt.subplots(1, 2, figsize=(14, 6), facecolor=WHITE,
                                      gridspec_kw={"width_ratios": [3, 2]})
    fig.suptitle("Pod C Becomes Five Times Slower", fontsize=17, fontweight="bold",
                 color=NAVY, y=1.03)
    fig.text(0.5, 0.955, "3 Ledger pods share 3,000 calls per second. A and B answer in "
             "10 ms; C now takes 50 ms.", ha="center", fontsize=10.5, color=INK,
             style="italic")

    positions = range(3)
    left.bar([p - 0.18 for p in positions], round_robin, width=0.34, color=GREY,
             label="round-robin")
    left.bar([p + 0.18 for p in positions], least_request, width=0.34, color=BLUE,
             label="least-request")
    for p in positions:
        left.text(p - 0.18, round_robin[p] + 25, f"{round_robin[p]:,.0f}", ha="center",
                  fontsize=8.5, color=GREY)
        left.text(p + 0.18, least_request[p] + 25, f"{least_request[p]:,.0f}", ha="center",
                  fontsize=8.5, color=BLUE)
    left.set_xticks(list(positions), ["pod A\n10 ms", "pod B\n10 ms", "pod C\n50 ms (slow)"])
    left.legend(frameon=False, fontsize=9)
    left.set_ylim(0, 1_650)
    left.yaxis.set_major_formatter(plt.FuncFormatter(lambda value, _: f"{value:,.0f}"))
    _style_chart(left, "Calls per second each pod receives", "calls per second")

    results = [("round-robin", round_robin, GREY), ("least-request", least_request, BLUE)]
    for index, (name, rates, color) in enumerate(results):
        slow_share, average = summary(rates)
        right.bar(index, slow_share * 100, width=0.55, color=color)
        right.text(index, slow_share * 100 + 2.2, f"{slow_share:.0%} of calls slow\n"
                   f"average {average:.0f} ms", ha="center", fontsize=9, color=color,
                   linespacing=1.4)
    right.set_xticks([0, 1], [name for name, _, _ in results])
    right.set_ylim(0, 45)
    _style_chart(right, "Share of calls that hit the slow pod", "% of all calls")
    right.yaxis.set_major_formatter(plt.FuncFormatter(lambda value, _: f"{value:.0f}%"))
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    return fig


def wallet_front_doors() -> plt.Figure:
    fig, ax = canvas(16, 9.5)
    heading(ax, "The Wallet's Front Doors",
            "Every hop uses the simplest balancing that does the job")

    box(ax, 1, 67, 13, 8, "Phones", "the wallet app")
    box(ax, 1, 54, 13, 8, "Merchants", "checkout pages")
    box(ax, 1, 24, 13, 8, "Card network", "top-up callbacks", face=GREEN_FACE, edge=GREEN,
        title_color=GREEN)

    box(ax, 19, 78, 15, 7, "DNS", "one address per zone", face=WHITE, edge=GREY,
        title_color=GREY)
    arrow(ax, (10, 75.6), (18.4, 81), color=GREY, dashed=True)
    note(ax, 9, 81, "look up first", color=GREY, size=8)

    panel(ax, 19, 20, 15, 52, "Layer 7 LB",
          "in all 3 zones\n\nends TLS\nbody ≤ 64 KB\n2 s timeout\nadds X-Request-Id\n"
          "and X-Forwarded-For\n\nnever retries\na POST", face=MIST, edge=NAVY)
    for y in (71, 58):
        arrow(ax, (14.6, y), (18.4, y), color=NAVY)
    arrow(ax, (14.6, 28), (18.4, 28), color=GREEN)

    panel(ax, 41, 50, 18, 22, "Wallet API ×42",
          "14 pods per zone\nleast-request\nslow start\n+ Envoy sidecar")
    arrow(ax, (34.6, 61), (40.4, 61), color=NAVY, label="/v1/")
    box(ax, 41, 23, 18, 10, "Webhook pods ×4", "round-robin, own pool", face=GREEN_FACE,
        edge=GREEN, title_color=GREEN)
    arrow(ax, (34.6, 28), (40.4, 28), color=GREEN, label="/webhooks/")
    note(ax, 26.5, 36, "/webhooks/ only\nfrom the card\nnetwork's\naddresses",
         color=GREEN, size=8)

    panel(ax, 67, 50, 17, 22, "Ledger ×12",
          "source of truth\nfor money\n\nnew version gets\n1% of calls (99 : 1)")
    arrow(ax, (59.6, 61), (66.4, 61), color=BLUE)
    note(ax, 63, 67.5, "gRPC,\nper call", color=BLUE, size=8)
    note(ax, 50, 44, "sidecar: least-request,\nremoves a pod after\n5 errors in a row",
         color=BLUE, size=8)
    arrow(ax, (59.6, 28), (69, 49.4), color=GREEN)
    note(ax, 67, 37, "credit\ntop-up", color=GREEN, size=8)

    box(ax, 68, 24, 15, 9, "Payouts", "withdrawals")
    arrow(ax, (75.5, 49.4), (75.5, 33.6), color=AMBER, dashed=True)
    note(ax, 79, 41.5, "queue", color=AMBER, size=8)
    box(ax, 88, 24, 10, 9, "Egress ×2", "2 fixed IPs", face=AMBER_FACE, edge=AMBER,
        title_color=AMBER)
    arrow(ax, (83.6, 28.5), (87.4, 28.5), color=AMBER)
    box(ax, 88, 6, 10, 8, "Bank", "allowlist", face=WHITE, edge=GREY, title_color=GREY)
    arrow(ax, (93, 23.4), (93, 14.6), color=AMBER)
    note(ax, 95.8, 19, "mTLS", color=AMBER, size=8)

    legend = [(NAVY, False, "public HTTP through the Layer 7 load balancer"),
              (BLUE, False, "internal gRPC, balanced per call"),
              (GREEN, False, "top-up callbacks: a separate pool"),
              (AMBER, False, "outgoing payout calls through fixed addresses")]
    for index, (color, dashed, label) in enumerate(legend):
        y = 14 - index * 3.6
        ax.plot([38, 42], [y, y], color=color, linewidth=2, linestyle="--" if dashed else "-")
        note(ax, 43.5, y, label, ha="left", size=8.2)
    return fig


FIGURES = {
    "l4_vs_l7": l4_vs_l7,
    "grpc_pinning": grpc_pinning,
    "forward_vs_reverse_proxy": forward_vs_reverse_proxy,
    "lb_strategies": lb_strategies,
    "wallet_front_doors": wallet_front_doors,
}


if __name__ == "__main__":
    render(FIGURES, TOPIC, sys.argv[1:])
