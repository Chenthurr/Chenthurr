#!/usr/bin/env python3
"""Generate a contribution tree SVG from GitHub contribution calendar data."""

import json
import math
import sys
from pathlib import Path


def esc(value: str) -> str:
    return value.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def contribution_data(path: str):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    days = []
    for week in data["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]:
        for day in week["contributionDays"]:
            days.append((day["date"], int(day["contributionCount"])))
    return days


def make_svg(days, dark=True):
    width, height = 1000, 430
    bg = "#0d1117" if dark else "#ffffff"
    text = "#f0f6fc" if dark else "#24292f"
    muted = "#8b949e" if dark else "#57606a"
    trunk = "#8b6f47" if dark else "#825c2d"
    branch = "#6f5739" if dark else "#9a6b35"
    empty = "#30363d" if dark else "#d0d7de"
    leaf_low = "#39d353" if dark else "#1a7f37"
    leaf_mid = "#7ee787" if dark else "#40a02b"
    leaf_high = "#f2cc60" if dark else "#bf8700"

    counts = [c for _, c in days]
    max_count = max(counts or [1])
    # Map the latest year onto a stylized canopy: 52 weeks x 7 days.
    recent = days[-364:] if len(days) > 364 else days
    leaves = []
    for i, (date, count) in enumerate(recent):
        week = i // 7
        dow = i % 7
        angle = (week / 52.0) * math.pi * 2.0 - math.pi
        radius = 55 + (week % 8) * 6 + dow * 2
        x = 500 + math.cos(angle) * (radius + week * 3.0) + (dow - 3) * 9
        y = 225 + math.sin(angle) * (105 + week * 0.35) - dow * 5
        # Pull sparse/older points inward for a natural canopy shape.
        x = 500 + (x - 500) * 0.72
        y = 220 + (y - 220) * 0.70
        intensity = count / max_count if max_count else 0
        r = 2.0 + intensity * 5.0
        if count == 0:
            fill = empty
            opacity = 0.22
        elif intensity >= 0.66:
            fill = leaf_high
            opacity = 1
        elif intensity >= 0.25:
            fill = leaf_mid
            opacity = 0.95
        else:
            fill = leaf_low
            opacity = 0.9
        leaves.append((x, y, r, fill, opacity, date, count))

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
        '<title id="title">Chenthurr GitHub Contribution Tree</title>',
        '<desc id="desc">A living tree visualization of the latest year of GitHub contributions. Leaf size and brightness represent activity.</desc>',
        '<defs>',
        '<filter id="glow" x="-100%" y="-100%" width="300%" height="300%"><feGaussianBlur stdDeviation="2.2" result="blur"/><feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge></filter>',
        '<linearGradient id="trunkGradient" x1="0" y1="0" x2="1" y2="1"><stop offset="0%" stop-color="#b08b57"/><stop offset="100%" stop-color="#5c4228"/></linearGradient>',
        '<style>@keyframes sway{0%,100%{transform:rotate(-0.25deg)}50%{transform:rotate(0.25deg)}} @keyframes shimmer{0%,100%{opacity:.7}50%{opacity:1}} .tree{transform-origin:500px 360px;animation:sway 7s ease-in-out infinite}.leaf{filter:url(#glow);animation:shimmer 4s ease-in-out infinite}</style>',
        '</defs>',
        f'<rect width="{width}" height="{height}" rx="20" fill="{bg}"/>',
        f'<text x="34" y="42" fill="{text}" font-family="Segoe UI,Ubuntu,sans-serif" font-size="22" font-weight="700">CONTRIBUTION TREE</text>',
        f'<text x="34" y="66" fill="{muted}" font-family="Segoe UI,Ubuntu,sans-serif" font-size="13">Every contribution grows the tree • the brighter the leaf, the stronger the activity</text>',
        f'<text x="966" y="42" fill="{muted}" font-family="Segoe UI,Ubuntu,sans-serif" font-size="12" text-anchor="end">@Chenthurr</text>',
        '<g class="tree">',
        # Ground glow and trunk.
        '<ellipse cx="500" cy="365" rx="205" ry="17" fill="#39d353" opacity=".10"/>',
        f'<path d="M500 365 C492 325 490 290 505 250 C518 215 500 185 514 150" fill="none" stroke="url(#trunkGradient)" stroke-width="25" stroke-linecap="round"/>',
        f'<path d="M503 300 C455 270 405 245 350 225 M498 287 C548 250 595 230 655 215 M505 250 C470 220 448 190 430 155 M508 238 C548 205 572 174 590 140" fill="none" stroke="{branch}" stroke-width="10" stroke-linecap="round" opacity=".95"/>',
        f'<path d="M468 325 C430 305 390 290 355 278 M535 320 C575 295 615 280 655 270 M482 275 C450 250 425 230 405 205 M525 270 C555 245 590 220 620 190" fill="none" stroke="{branch}" stroke-width="6" stroke-linecap="round" opacity=".9"/>',
    ]

    for idx, (x, y, r, fill, opacity, date, count) in enumerate(leaves):
        delay = (idx % 19) * 0.08
        parts.append(f'<circle class="leaf" cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="{fill}" opacity="{opacity}" style="animation-delay:{delay:.2f}s" data-date="{esc(date)}" data-contributions="{count}"/>')

    parts += [
        '</g>',
        f'<text x="500" y="407" fill="{muted}" font-family="Segoe UI,Ubuntu,sans-serif" font-size="12" text-anchor="middle">LOWER ACTIVITY  ·  GROWTH  ·  HIGH ACTIVITY</text>',
        f'<circle cx="390" cy="404" r="3" fill="{leaf_low}"/><circle cx="610" cy="404" r="4" fill="{leaf_high}"/>',
        '</svg>',
    ]
    return "".join(parts)


def main():
    if len(sys.argv) != 2:
        raise SystemExit("usage: generate_contribution_tree.py contributions.json")
    days = contribution_data(sys.argv[1])
    out = Path("dist")
    out.mkdir(exist_ok=True)
    (out / "github-contribution-tree.svg").write_text(make_svg(days, True), encoding="utf-8")
    (out / "github-contribution-tree-light.svg").write_text(make_svg(days, False), encoding="utf-8")


if __name__ == "__main__":
    main()
