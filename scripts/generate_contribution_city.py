#!/usr/bin/env python3
"""Generate a cinematic contribution-city SVG from GitHub contribution data."""
import json, sys
from pathlib import Path

def esc(s):
    return str(s).replace('&','&amp;').replace('<','&lt;').replace('>','&gt;').replace('"','&quot;')

def load(path):
    data=json.loads(Path(path).read_text())
    days=[]
    for week in data['data']['user']['contributionsCollection']['contributionCalendar']['weeks']:
        for d in week['contributionDays']:
            days.append((d['date'],int(d['contributionCount'])))
    return days[-364:]

def svg(days,dark=True):
    W,H=1200,430
    bg='#070b14' if dark else '#f5f7fb'; sky='#0b1220' if dark else '#eaf0f8'; ground='#070a0f' if dark else '#dce3ec'
    text='#f5f7ff' if dark else '#18212f'; muted='#8b98ad' if dark else '#657184'; grid='#243044' if dark else '#c6cfdb'
    building='#111a29' if dark else '#b9c5d3'; building2='#162235' if dark else '#aebaca'; window='#5eead4' if dark else '#087f78'; hot='#fbbf24' if dark else '#b45309'
    parts=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" role="img" aria-labelledby="t d">',
           '<title id="t">Chenthurr Contribution City</title>',
           '<desc id="d">A cinematic city skyline generated from the latest year of GitHub contributions. Building height and illuminated windows represent activity.</desc>',
           '<defs>',
           f'<linearGradient id="sky" x2="0" y2="1"><stop stop-color="{sky}"/><stop offset="1" stop-color="{bg}"/></linearGradient>',
           f'<linearGradient id="glass" x2="0" y2="1"><stop stop-color="{building2}"/><stop offset="1" stop-color="{building}"/></linearGradient>',
           f'<filter id="glow"><feGaussianBlur stdDeviation="3" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>',
           '<style>@keyframes twinkle{0%,100%{opacity:.25}50%{opacity:1}} @keyframes traffic{to{transform:translateX(1200px)}} .light{animation:twinkle 3s ease-in-out infinite}.car{animation:traffic 9s linear infinite}</style>',
           '</defs>',f'<rect width="{W}" height="{H}" fill="url(#sky)"/>']
    for i in range(45):
        x=(i*83)%1180+10; y=(i*47)%130+18; r=1+(i%3)*.45
        parts.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{muted}" opacity="{0.18+(i%5)*.08}"/>')
    parts += [f'<circle cx="1030" cy="75" r="30" fill="{hot}" opacity=".92" filter="url(#glow)"/>',
              f'<text x="42" y="42" fill="{text}" font-family="Segoe UI,Ubuntu,sans-serif" font-size="23" font-weight="700">CONTRIBUTION CITY</text>',
              f'<text x="42" y="67" fill="{muted}" font-family="Segoe UI,Ubuntu,sans-serif" font-size="13">365 days of building • every contribution lights the city</text>',
              f'<text x="1155" y="42" fill="{muted}" text-anchor="end" font-family="Segoe UI,Ubuntu,sans-serif" font-size="12">@Chenthurr</text>']
    weeks=[]
    for w in range(52):
        chunk=days[w*7:(w+1)*7]
        weeks.append((chunk[-1][0] if chunk else '',sum(c for _,c in chunk)))
    max_week=max((total for _,total in weeks),default=1)
    x0=35; bw=19; gap=3; base=350
    for w,(date,total) in enumerate(weeks):
        intensity=total/max_week if max_week else 0
        h=45+intensity*220
        x=x0+w*(bw+gap); y=base-h
        fill='url(#glass)' if w%3 else building2
        edge=window if intensity<.35 else hot
        parts.append(f'<rect x="{x}" y="{y:.1f}" width="{bw}" height="{h:.1f}" rx="3" fill="{fill}" stroke="{edge}" stroke-width=".8"/>')
        win_rows=max(2,int(h/16)); win_cols=3
        lit=min(win_rows*win_cols,max(0,round((total/max_week)*win_rows*win_cols)))
        for rr in range(win_rows):
            for cc in range(win_cols):
                idx=rr*win_cols+cc
                wx=x+3+cc*5.2; wy=y+9+rr*13
                if wy>base-4: continue
                col=window if idx<lit else grid
                op=.9 if idx<lit else .25
                delay=(w*3+idx)%20
                parts.append(f'<rect class="light" x="{wx:.1f}" y="{wy:.1f}" width="2.8" height="5" rx=".7" fill="{col}" opacity="{op}" style="animation-delay:{delay/10:.1f}s"/>')
        if intensity>.72:
            cx=x+bw/2
            parts.append(f'<line x1="{cx}" y1="{y}" x2="{cx}" y2="{y-18}" stroke="{hot}" stroke-width="1.5"/>')
            parts.append(f'<circle cx="{cx}" cy="{y-20}" r="2.5" fill="{hot}" filter="url(#glow)"/>')
    parts += [f'<rect y="350" width="{W}" height="80" fill="{ground}" opacity=".97"/>',
              f'<line x1="0" y1="382" x2="{W}" y2="382" stroke="{grid}" stroke-width="2" stroke-dasharray="24 20"/>',
              f'<text x="42" y="410" fill="{muted}" font-family="Segoe UI,Ubuntu,sans-serif" font-size="11">QUIET</text>',
              f'<text x="600" y="410" fill="{muted}" text-anchor="middle" font-family="Segoe UI,Ubuntu,sans-serif" font-size="11">BUILD DISTRICTS</text>',
              f'<text x="1158" y="410" fill="{muted}" text-anchor="end" font-family="Segoe UI,Ubuntu,sans-serif" font-size="11">PEAK ACTIVITY</text>']
    for i in range(5):
        parts.append(f'<rect class="car" x="{-180+i*250}" y="390" width="70" height="3" rx="2" fill="{window}" opacity=".45" style="animation-delay:{-i*1.4}s"/>')
    parts.append('</svg>')
    return ''.join(parts)

def main():
    if len(sys.argv)!=2: raise SystemExit('usage: generate_contribution_city.py contributions.json')
    days=load(sys.argv[1]); out=Path('dist'); out.mkdir(exist_ok=True)
    (out/'github-contribution-city.svg').write_text(svg(days,True))
    (out/'github-contribution-city-light.svg').write_text(svg(days,False))
if __name__=='__main__': main()
