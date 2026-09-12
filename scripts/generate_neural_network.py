#!/usr/bin/env python3
"""Generate an animated neural-network-style contribution graph SVG."""

import json
import math
import sys
from pathlib import Path


def esc(value: str) -> str:
    return (value.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;"))


def contribution_data(path: str):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    days = []
    for week in data["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]:
        for day in week["contributionDays"]:
            days.append((day["date"], int(day["contributionCount"])))
    return days


def make_svg(days, dark=True):
    width, height = 1000, 330
    bg = "#0d1117" if dark else "#ffffff"
    panel = "#161b22" if dark else "#f6f8fa"
    text = "#f0f6fc" if dark else "#24292f"
    muted = "#8b949e" if dark else "#57606a"
    edge = "#30363d" if dark else "#d0d7de"
    low = "#58a6ff" if dark else "#0969da"
    mid = "#bc8cff" if dark else "#8250df"
    high = "#ff7b72" if dark else "#cf222e"

    counts = [c for _, c in days]
    max_count = max(counts or [1])
    # Keep the visualization compact and readable: 84 nodes, grouped by week.
    sample = days[-84:] if len(days) > 84 else days
    n = len(sample)
    cols = 14
    rows = math.ceil(n / cols)
    x0, y0 = 145, 98
    dx, dy = 58, 36
    nodes = []
    for i, (date, count) in enumerate(sample):
        col, row = i % cols, i // cols
        x = x0 + col * dx + (row % 2) * 10
        y = y0 + row * dy
        intensity = count / max_count if max_count else 0
        radius = 3.5 + intensity * 8.5
        if intensity >= 0.66:
            fill = high
        elif intensity >= 0.25:
            fill = mid
        elif intensity > 0:
            fill = low
        else:
            fill = edge
        nodes.append((x, y, radius, fill, date, count))

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
        f'<title id="title">Chenthurr GitHub Contribution Neural Network</title>',
        f'<desc id="desc">A neural-network visualization of recent GitHub contribution activity. Node size represents contribution intensity.</desc>',
        '<defs>',
        f'<linearGradient id="glow" x1="0" y1="0" x2="1" y2="1"><stop offset="0%" stop-color="{low}"/><stop offset="55%" stop-color="{mid}"/><stop offset="100%" stop-color="{high}"/></linearGradient>',
        '<filter id="softGlow" x="-100%" y="-100%" width="300%" height="300%"><feGaussianBlur stdDeviation="3" result="blur"/><feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge></filter>',
        '<style>@keyframes pulse{0%,100%{opacity:.35}50%{opacity:.9}} @keyframes flow{to{stroke-dashoffset:-36}} .edge{stroke-dasharray:6 12;animation:flow 3s linear infinite}.node{filter:url(#softGlow)}</style>',
        '</defs>',
        f'<rect x="0" y="0" width="{width}" height="{height}" rx="18" fill="{bg}"/>',
        f'<rect x="1" y="1" width="{width-2}" height="{height-2}" rx="17" fill="none" stroke="{edge}"/>',
        f'<text x="34" y="42" fill="{text}" font-family="Segoe UI,Ubuntu,sans-serif" font-size="22" font-weight="700">CONTRIBUTION NEURAL NETWORK</text>',
        f'<text x="34" y="66" fill="{muted}" font-family="Segoe UI,Ubuntu,sans-serif" font-size="13">Every commit strengthens the network • recent GitHub activity</text>',
        f'<text x="34" y="292" fill="{muted}" font-family="Segoe UI,Ubuntu,sans-serif" font-size="11">LOW</text>',
        f'<text x="34" y="310" fill="{muted}" font-family="Segoe UI,Ubuntu,sans-serif" font-size="11">activity</text>',
        f'<circle cx="88" cy="288" r="4" fill="{low}"/><circle cx="88" cy="304" r="6" fill="{mid}"/><circle cx="88" cy="324" r="9" fill="{high}"/>',
        f'<text x="900" y="42" fill="{muted}" font-family="Segoe UI,Ubuntu,sans-serif" font-size="12" text-anchor="end">@Chenthurr</text>',
    ]

    # Connect each node to nearby nodes, creating a neural-network lattice.
    for i, (x, y, *_rest) in enumerate(nodes):
        for j in (i + 1, i + cols, i + cols + 1):
            if j < n:
                x2, y2 = nodes[j][0], nodes[j][1]
                parts.append(f'<line class="edge" x1="{x:.1f}" y1="{y:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{edge}" stroke-width="1" opacity=".8"/>')

    for x, y, r, fill, date, count in nodes:
        parts.append(f'<circle class="node" cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="{fill}" data-date="{esc(date)}" data-contributions="{count}"/>')

    parts.append('</svg>')
    return "".join(parts)


def main():
    if len(sys.argv) != 2:
        raise SystemExit("usage: generate_neural_network.py contributions.json")
    days = contribution_data(sys.argv[1])
    out = Path("dist")
    out.mkdir(exist_ok=True)
    (out / "github-contribution-neural-network.svg").write_text(make_svg(days, True), encoding="utf-8")
    (out / "github-contribution-neural-network-light.svg").write_text(make_svg(days, False), encoding="utf-8")


if __name__ == "__main__":
    main()
