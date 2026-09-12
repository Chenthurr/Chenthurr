#!/usr/bin/env python3
"""Generate a contribution city SVG from GitHub contribution calendar data."""

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
    skyline = "#21262d" if dark else "#d0d7de"
    window = "#58a6ff" if dark else "#0969da"
    window2 = "#bc8cff" if dark else "#8250df"
    window3 = "#f2cc60" if dark else "#bf8700"

    recent = days[-364:] if len(days) > 364 else days
    weeks = []
    for i in range(0, len(recent), 7):
        weeks.append(recent[i:i + 7])
    counts = [c for _, c in recent]
    max_count = max(counts or [1])

    buildings = []
    city_x0, city_x1 = 80, 920
    for i, week in enumerate(weeks):
        count = sum(c for _, c in week)
        intensity = count / max(1, max_count * 7)
        h = 55 + intensity * 180
        # Week-to-building mapping makes the city visibly reflect the whole year.
        x = city_x0 + (i / max(1, len(weeks) - 1)) * (city_x1 - city_x0)
        w = max(10, (city_x1 - city_x0) / len(weeks) - 4)
        y = 340 - h
        buildings.append((x, y, w, h, intensity, week))

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
        '<title id="title">Chenthurr GitHub Contribution City</title>',
        '<desc id="desc">A city skyline visualization of the latest year of GitHub contributions. Building height represents weekly activity.</desc>',
        '<defs>',
        '<filter id="glow" x="-100%" y="-100%" width="300%" height="300%"><feGaussianBlur stdDeviation="2" result="blur"/><feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge></filter>',
        '<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#111827"/><stop offset="100%" stop-color="#0d1117"/></linearGradient>',
        '<style>@keyframes blink{0%,92%,100%{opacity:.45}95%{opacity:1}} @keyframes rise{0%{transform:translateY(8px);opacity:.2}100%{transform:translateY(0);opacity:1}} .building{animation:rise .9s ease-out both}.window{animation:blink 4s ease-in-out infinite}</style>',
        '</defs>',
        f'<rect width="{width}" height="{height}" rx="20" fill="{bg}"/>',
        f'<rect x="1" y="1" width="{width-2}" height="{height-2}" rx="19" fill="none" stroke="{skyline}"/>',
        f'<text x="34" y="42" fill="{text}" font-family="Segoe UI,Ubuntu,sans-serif" font-size="22" font-weight="700">CONTRIBUTION CITY</text>',
        f'<text x="34" y="66" fill="{muted}" font-family="Segoe UI,Ubuntu,sans-serif" font-size="13">Every commit builds the skyline • taller buildings mean stronger weekly activity</text>',
        f'<text x="966" y="42" fill="{muted}" font-family="Segoe UI,Ubuntu,sans-serif" font-size="12" text-anchor="end">@Chenthurr</text>',
        f'<line x1="55" y1="340" x2="945" y2="340" stroke="{skyline}" stroke-width="2"/>',
    ]

    for i, (x, y, w, h, intensity, week) in enumerate(buildings):
        fill = "#30363d" if intensity == 0 else ("#161b22" if dark else "#f6f8fa")
        stroke = window if intensity < .35 else (window2 if intensity < .7 else window3)
        parts.append(f'<g class="building" style="animation-delay:{(i % 18) * .035:.2f}s">')
        parts.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="2" fill="{fill}" stroke="{stroke}" stroke-width="1" opacity=".95"/>')
        # Add windows based on the seven contribution days in the week.
        rows = max(2, int(h // 22))
        cols = 2 if w < 22 else 3
        for r in range(rows):
            for c in range(cols):
                day_index = (r * cols + c) % max(1, len(week))
                count = week[day_index][1] if week else 0
                if count:
                    wx = x + 4 + c * max(5, (w - 8) / max(1, cols - 1))
                    wy = y + 8 + r * 19
                    color = window if count < max_count * .33 else (window2 if count < max_count * .66 else window3)
                    parts.append(f'<rect class="window" x="{wx:.1f}" y="{wy:.1f}" width="3" height="5" rx="1" fill="{color}" filter="url(#glow)" style="animation-delay:{((i+r+c) % 13) * .12:.2f}s"/>')
        # A high-activity week gets a small rooftop antenna.
        if intensity > .72:
            cx = x + w / 2
            parts.append(f'<line x1="{cx:.1f}" y1="{y:.1f}" x2="{cx:.1f}" y2="{y-18:.1f}" stroke="{window3}" stroke-width="1.5"/>')
            parts.append(f'<circle cx="{cx:.1f}" cy="{y-20:.1f}" r="2.5" fill="{window3}" filter="url(#glow)"/>')
        parts.append('</g>')

    parts += [
        f'<text x="500" y="382" fill="{muted}" font-family="Segoe UI,Ubuntu,sans-serif" font-size="12" text-anchor="middle">JANUARY  ·  APRIL  ·  JULY  ·  OCTOBER  ·  DECEMBER</text>',
        f'<text x="500" y="407" fill="{text}" font-family="Segoe UI,Ubuntu,sans-serif" font-size="13" text-anchor="middle" font-style="italic">Building a better tomorrow, one commit at a time.</text>',
        '</svg>',
    ]
    return "".join(parts)


def main():
    if len(sys.argv) != 2:
        raise SystemExit("usage: generate_contribution_tree.py contributions.json")
    days = contribution_data(sys.argv[1])
    out = Path("dist")
    out.mkdir(exist_ok=True)
    (out / "github-contribution-city.svg").write_text(make_svg(days, True), encoding="utf-8")
    (out / "github-contribution-city-light.svg").write_text(make_svg(days, False), encoding="utf-8")


if __name__ == "__main__":
    main()
