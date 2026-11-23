"""Generate the geometric book covers shown on the site.

    python covers/make_covers.py

Writes covers/<book>.png (300x450) for the site, and full-size 1600x2400 PNGs
into covers/full/ (not committed) for use as EPUB covers. Needs Google Chrome
for rendering and the Source Sans 3 fonts from the compiled-books repo.
"""
import math
import random
import subprocess
import tempfile
from pathlib import Path

HERE = Path(__file__).parent
FONTS = Path(r"D:\my\books\compiled-books\fonts")
CHROME = Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe")
BG = "#121318"
DIM = "#3a3d48"


def head():
    f = FONTS.as_uri()
    return f"""<!doctype html><meta charset="utf-8"><style>
@font-face {{ font-family: S3; src: url({f}/SourceSans3-Regular.ttf); font-weight: 400; }}
@font-face {{ font-family: S3; src: url({f}/SourceSans3-Bold.ttf); font-weight: 700; }}
html, body {{ margin: 0; height: 100%; background: {BG}; overflow: hidden; }}
svg {{ display: block; width: 100vw; height: 100vh; }}
</style>"""


def cover(art, accent, glow_at, label, line1, line2, subtitle, size1=200, size2=200, note=""):
    gx, gy = glow_at
    # the title block hangs from line 2, so a smaller second line keeps the spacing tight
    y1 = 2120 - round(size2 * 0.93)
    note_svg = f'<text x="140" y="2340" font-size="28" fill="#6c707c">{note}</text>' if note else ""
    return head() + f"""
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 2400">
<defs>
  <radialGradient id="glow" cx="{gx}" cy="{gy}" r="1000" gradientUnits="userSpaceOnUse">
    <stop offset="0" stop-color="{accent}" stop-opacity=".5"/>
    <stop offset=".4" stop-color="{accent}" stop-opacity=".11"/>
    <stop offset="1" stop-color="{accent}" stop-opacity="0"/>
  </radialGradient>
  <linearGradient id="fade" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="{BG}" stop-opacity="0"/><stop offset="1" stop-color="{BG}"/>
  </linearGradient>
</defs>
<rect width="1600" height="2400" fill="{BG}"/>
<rect width="1600" height="2400" fill="url(#glow)"/>
{art}
<rect y="1300" width="1600" height="500" fill="url(#fade)"/>
<rect y="1800" width="1600" height="600" fill="{BG}"/>
<g font-family="S3">
  <text x="140" y="{y1 - 190}" font-size="40" font-weight="700" letter-spacing="9" fill="{accent}">{label}</text>
  <text x="130" y="{y1}" font-size="{size1}" font-weight="700" fill="#fff" letter-spacing="-4">{line1}</text>
  <text x="130" y="2120" font-size="{size2}" font-weight="400" fill="#fff" letter-spacing="-3">{line2}</text>
  <rect x="140" y="2170" width="180" height="10" fill="{accent}"/>
  <text x="140" y="2268" font-size="52" fill="#c4c7d0">{subtitle}</text>
  {note_svg}
</g>
</svg>"""


def pt(cx, cy, r, deg):
    return cx + r * math.cos(math.radians(deg)), cy + r * math.sin(math.radians(deg))


def arc(cx, cy, r, a0, a1):
    x0, y0 = pt(cx, cy, r, a0)
    x1, y1 = pt(cx, cy, r, a1)
    large = 1 if (a1 - a0) % 360 > 180 else 0
    return f"M{x0:.1f} {y0:.1f} A{r} {r} 0 {large} 1 {x1:.1f} {y1:.1f}"


# Svelte 5: a signal rippling out through a dependency graph
def svelte_art(accent):
    rnd = random.Random(5)
    cx, cy = 1040, 820
    p = [f'<linearGradient id="ring" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#ffc078"/><stop offset="1" stop-color="{accent}"/></linearGradient>']
    for i, r in enumerate(range(90, 1500, 70)):
        dash = "" if i % 4 else ' stroke-dasharray="4 18"'
        p.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="url(#ring)" stroke-width="{max(1.5, 9 - i * .35):.1f}" opacity="{max(.06, .85 - i * .045):.2f}"{dash}/>')
    for i in range(7):
        r = 220 + i * 140
        a0 = rnd.uniform(0, 360)
        p.append(f'<path d="{arc(cx, cy, r, a0, a0 + rnd.uniform(40, 110))}" fill="none" stroke="#ffd2a8" stroke-width="22" stroke-linecap="round" opacity="{.75 - i * .08:.2f}"/>')
    nodes = []
    while len(nodes) < 46:
        x, y = rnd.uniform(80, 1520), rnd.uniform(90, 1560)
        if all(math.dist((x, y), n) > 120 for n in nodes):
            nodes.append((x, y))
    for a in nodes:
        for b in sorted(nodes, key=lambda n: math.dist(a, n))[1:3]:
            hot = math.dist(a, (cx, cy)) < 620 and math.dist(b, (cx, cy)) < 620
            p.append(f'<line x1="{a[0]:.0f}" y1="{a[1]:.0f}" x2="{b[0]:.0f}" y2="{b[1]:.0f}" stroke="{accent if hot else DIM}" stroke-width="{3 if hot else 2}" opacity=".85"/>')
    for x, y in nodes:
        if math.dist((x, y), (cx, cy)) < 620:
            p.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="13" fill="{accent}"/><circle cx="{x:.0f}" cy="{y:.0f}" r="26" fill="none" stroke="{accent}" stroke-width="2" opacity=".5"/>')
        else:
            p.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="9" fill="{BG}" stroke="#5a5e6b" stroke-width="3"/>')
    p.append(f'<circle cx="{cx}" cy="{cy}" r="74" fill="{accent}"/><circle cx="{cx}" cy="{cy}" r="22" fill="#fff"/>')
    return "\n".join(p), (cx, cy)


# SvelteKit 3: a route tree drawn like a transit map, one request lit up
def sveltekit_art(accent):
    levels = [
        [("/", 780)],
        [("/blog", 360), ("/shop", 780), ("/api", 1220)],
        [("[slug]", 200), ("+layout", 470), ("[id]", 690), ("cart", 900), ("+server", 1110), ("auth", 1360)],
        [("+page", 140), ("+page", 300), ("load", 560), ("+page", 690), ("form", 860), ("+page", 1010), ("GET", 1160), ("POST", 1300), ("hooks", 1460)],
    ]
    xs = [180, 560, 940, 1320]
    parents = {1: [0, 0, 0], 2: [0, 0, 1, 1, 2, 2], 3: [0, 0, 1, 2, 3, 3, 4, 4, 5]}
    lit = {(0, 0), (1, 1), (2, 3), (3, 4)}
    # the tree runs top to bottom: swap roles so levels go down the page
    pos = {(li, i): (y, 180 + xs[li] * 0.98) for li, lv in enumerate(levels) for i, (_, y) in enumerate(lv)}
    p = []
    for li in range(1, 4):
        for i, par in enumerate(parents[li]):
            (x0, y0), (x1, y1) = pos[(li - 1, par)], pos[(li, i)]
            mid = (y0 + y1) / 2
            on = (li - 1, par) in lit and (li, i) in lit
            d = f"M{x0:.0f} {y0:.0f} V{mid:.0f} H{x1:.0f} V{y1:.0f}"
            if on:
                p.append(f'<path d="{d}" fill="none" stroke="{accent}" stroke-width="34" opacity=".18" stroke-linejoin="round"/>')
            p.append(f'<path d="{d}" fill="none" stroke="{accent if on else DIM}" stroke-width="{12 if on else 7}" stroke-linejoin="round" stroke-linecap="round"/>')
    for (li, i), (x, y) in pos.items():
        name = levels[li][i][0]
        on = (li, i) in lit
        if name in ("+server", "GET", "POST", "hooks"):
            p.append(f'<rect x="{x - 24}" y="{y - 24}" width="48" height="48" rx="8" fill="{accent if on else BG}" stroke="{accent if on else "#5a5e6b"}" stroke-width="5"/>')
        else:
            p.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{30 if on else 22}" fill="{"#fff" if on else BG}" stroke="{accent if on else "#5a5e6b"}" stroke-width="{10 if on else 5}"/>')
        p.append(f'<text x="{x + 44:.0f}" y="{y + 12:.0f}" font-family="Consolas, monospace" font-size="34" fill="{accent if on else "#6c707c"}" transform="rotate(-35 {x + 44:.0f} {y + 12:.0f})">{name}</text>')
    # pulses travelling along the lit route
    for (li, i) in lit:
        x, y = pos[(li, i)]
        p.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="70" fill="none" stroke="{accent}" stroke-width="2" opacity=".45"/><circle cx="{x:.0f}" cy="{y:.0f}" r="110" fill="none" stroke="{accent}" stroke-width="1.5" opacity=".2"/>')
    return "\n".join(p), pos[(2, 3)]


# Astro 7: a starfield with a few lit islands and their orbits
def astro_art(accent):
    rnd = random.Random(7)
    p = [f'<radialGradient id="isl" cx=".35" cy=".35" r=".75"><stop offset="0" stop-color="#ffd1f5"/><stop offset=".45" stop-color="{accent}"/><stop offset="1" stop-color="#3b1a6b"/></radialGradient>']
    for _ in range(420):
        x, y = rnd.uniform(0, 1600), rnd.uniform(0, 1750)
        p.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{rnd.choice([1.5, 2, 2.5, 3.5])}" fill="#e9dcff" opacity="{rnd.uniform(.15, .8):.2f}"/>')
    islands = [(1060, 640, 170), (420, 380, 90), (330, 1180, 120), (1250, 1320, 70), (760, 1000, 55)]
    for (a, b) in [(0, 1), (0, 4), (4, 2), (4, 3), (0, 3)]:
        (x0, y0, _), (x1, y1, _) = islands[a], islands[b]
        p.append(f'<line x1="{x0}" y1="{y0}" x2="{x1}" y2="{y1}" stroke="{accent}" stroke-width="2" stroke-dasharray="6 14" opacity=".55"/>')
    for i, (x, y, r) in enumerate(islands):
        for k in range(1, 4):
            p.append(f'<ellipse cx="{x}" cy="{y}" rx="{r * (1.5 + k * .55):.0f}" ry="{r * (0.55 + k * .2):.0f}" fill="none" stroke="{accent}" stroke-width="{3 - k * .6:.1f}" opacity="{.6 - k * .14:.2f}" transform="rotate({-18 + i * 9} {x} {y})"/>')
        p.append(f'<circle cx="{x}" cy="{y}" r="{r * 1.6:.0f}" fill="{accent}" opacity=".12"/><circle cx="{x}" cy="{y}" r="{r}" fill="url(#isl)"/>')
    return "\n".join(p), islands[0][:2]


# SvelteKit Interview Prep: nine days as nine progress rings
def prep_art(accent):
    p = []
    size, gap, x0, y0 = 380, 40, 190, 200
    for d in range(9):
        col, row = d % 3, d // 3
        x, y = x0 + col * (size + gap), y0 + row * (size + gap)
        cx, cy = x + size / 2, y + size / 2
        done = d == 8
        p.append(f'<rect x="{x}" y="{y}" width="{size}" height="{size}" rx="28" fill="{"#17223a" if done else "#181b23"}" stroke="{accent if done else "#262a35"}" stroke-width="{4 if done else 2}"/>')
        p.append(f'<circle cx="{cx}" cy="{cy}" r="120" fill="none" stroke="#2a2f3c" stroke-width="22"/>')
        frac = (d + 1) / 9
        if frac >= 1:
            p.append(f'<circle cx="{cx}" cy="{cy}" r="120" fill="none" stroke="{accent}" stroke-width="22"/>')
            p.append(f'<circle cx="{cx}" cy="{cy}" r="52" fill="{accent}"/><path d="M{cx - 24} {cy + 2} l16 16 l32 -34" fill="none" stroke="#fff" stroke-width="10" stroke-linecap="round" stroke-linejoin="round"/>')
        else:
            p.append(f'<path d="{arc(cx, cy, 120, -90, -90 + 360 * frac)}" fill="none" stroke="{accent}" stroke-width="22" stroke-linecap="round" opacity="{.45 + frac * .5:.2f}"/>')
            p.append(f'<circle cx="{cx}" cy="{cy}" r="10" fill="{accent}" opacity="{.4 + frac * .5:.2f}"/>')
        p.append(f'<text x="{x + 28}" y="{y + 56}" font-family="S3" font-weight="700" font-size="36" fill="{accent if done else "#6c707c"}" letter-spacing="2">{d + 1:02d}</text>')
    last = (x0 + 2 * (size + gap) + size / 2, y0 + 2 * (size + gap) + size / 2)
    return "\n".join(p), last


# Living Well with Type 2 Diabetes: restless curves settling into calm ones
def diabetes_art(accent):
    rnd = random.Random(2)
    p = [f'<linearGradient id="calm" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ff8a65"/><stop offset=".45" stop-color="#ffd166"/><stop offset="1" stop-color="{accent}"/></linearGradient>']
    p.append(f'<circle cx="1180" cy="430" r="230" fill="#ffd166" opacity=".14"/><circle cx="1180" cy="430" r="150" fill="none" stroke="#ffd166" stroke-width="6" opacity=".8"/>')
    for k in range(10):
        p.append(f'<path d="{arc(1180, 430, 190 + k * 28, 200 + k * 9, 260 + k * 9)}" fill="none" stroke="#ffd166" stroke-width="5" stroke-linecap="round" opacity="{.6 - k * .05:.2f}"/>')
    rows = 22
    for i in range(rows):
        base = 300 + i * 62
        calm = i / (rows - 1)
        amp = 150 * (1 - calm) ** 1.6 + 6
        freq = rnd.uniform(2.2, 3.4)
        phase = rnd.uniform(0, math.tau)
        pts = []
        for s in range(0, 81):
            x = -40 + s * 21
            y = base + amp * math.sin(phase + s / 80 * math.tau * freq) * (0.6 + 0.4 * math.sin(s / 13 + i))
            pts.append(f"{x:.0f},{y:.0f}")
        p.append(f'<polyline points="{" ".join(pts)}" fill="none" stroke="url(#calm)" stroke-width="{3 + 4 * calm:.1f}" stroke-linecap="round" stroke-linejoin="round" opacity="{.35 + .55 * calm:.2f}"/>')
    return "\n".join(p), (800, 1300)


# CCDV-F handbook: the eight exam domains as a ring, one look per volume
def ccdv_art(accent, vol):
    cx, cy = 800, 820
    p = [f'<linearGradient id="seg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#b9c2ff"/><stop offset="1" stop-color="{accent}"/></linearGradient>']
    for r in range(640, 1500, 90):
        p.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{accent}" stroke-width="1.5" opacity="{max(.05, .3 - (r - 640) / 3000):.2f}"/>')
    heavy = {0, 3, 5}
    for s in range(8):
        a0 = -90 + s * 45 + 3
        a1 = a0 + 39
        if vol == 2:
            on = s in heavy
            p.append(f'<path d="{arc(cx, cy, 520, a0, a1)}" fill="none" stroke="{"url(#seg)" if on else DIM}" stroke-width="{120 if on else 40}"/>')
        else:
            p.append(f'<path d="{arc(cx, cy, 520, a0, a1)}" fill="none" stroke="url(#seg)" stroke-width="70" opacity="{.45 + s * .07:.2f}"/>')
    if vol == 1:
        for t in range(12):
            a = -90 + t * 30
            x0, y0 = pt(cx, cy, 380, a)
            x1, y1 = pt(cx, cy, 420, a)
            p.append(f'<line x1="{x0:.0f}" y1="{y0:.0f}" x2="{x1:.0f}" y2="{y1:.0f}" stroke="#d6dbff" stroke-width="8" stroke-linecap="round"/>')
    if vol == 3:
        for t in range(12):
            x, y = pt(cx, cy, 380, -90 + t * 30)
            p.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="44" fill="{BG}" stroke="#2f3446" stroke-width="10"/>')
            p.append(f'<path d="{arc(x, y, 44, -90, -90 + 330)}" fill="none" stroke="{accent}" stroke-width="10" stroke-linecap="round" opacity="{.4 + t * .05:.2f}"/>')
    if vol == 2:
        for t in range(5):
            x0, y0 = pt(cx, cy, 300, -90 + t * 72)
            p.append(f'<circle cx="{x0:.0f}" cy="{y0:.0f}" r="18" fill="#d6dbff"/>')
    numeral = {1: "I", 2: "II", 3: "III"}[vol]
    p.append(f'<circle cx="{cx}" cy="{cy}" r="{230 if vol != 1 else 300}" fill="{accent}" opacity=".12"/>')
    p.append(f'<text x="{cx}" y="{cy + 95}" text-anchor="middle" font-family="S3" font-weight="700" font-size="270" fill="#fff" letter-spacing="-6">{numeral}</text>')
    return "\n".join(p), (cx, cy)


# BraceML: nested braces, each pair one level of markup, over faint template code
def braceml_art(accent):
    cx, cy = 800, 820
    code = ["nav.menu > ul {", "  li > a href=/ 'Home'", "  li > a href=/shop 'Shop'", "}",
            "if users.length == 0 {", "  p.muted 'No users yet'", "} else {", "  ul {",
            "    each users as user (user.id) {", "      li > a '{user.name}'", "    }", "  }", "}"]
    p = [f'<linearGradient id="brace" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#b8f5dc"/><stop offset="1" stop-color="{accent}"/></linearGradient>']
    for i, line in enumerate(code * 2):
        p.append(f'<text x="90" y="{140 + i * 62}" font-family="Consolas, monospace" font-size="38" fill="#9aa0ad" opacity=".11" xml:space="preserve">{line.replace(">", "&gt;")}</text>')
    levels = 6
    for k in range(levels):
        size = 1500 - k * 210
        half = 620 - k * 95
        op = 0.18 + 0.82 * (k + 1) / levels
        fill = "url(#brace)" if k >= levels - 3 else accent
        for ch, x in (("{", cx - half), ("}", cx + half)):
            p.append(f'<text x="{x}" y="{cy}" text-anchor="middle" dominant-baseline="central" font-family="S3" font-weight="400" font-size="{size}" fill="{fill}" opacity="{op:.2f}">{ch}</text>')
    p.append(f'<circle cx="{cx}" cy="{cy}" r="120" fill="{accent}" opacity=".16"/><circle cx="{cx}" cy="{cy}" r="34" fill="{accent}"/><circle cx="{cx}" cy="{cy}" r="11" fill="#fff"/>')
    return "\n".join(p), (cx, cy)


NOTE = "Not affiliated with or endorsed by Anthropic."
CCDV = "#7c8cff"


def build():
    specs = [
        ("svelte-5-in-depth", svelte_art, "#ff3e00", "A SENIOR ENGINEER'S GUIDE", "Svelte 5", "in Depth", "Runes, the compiler and reactivity internals", {}),
        ("sveltekit-3-in-depth", sveltekit_art, "#ff9a1f", "A SENIOR ENGINEER'S GUIDE", "SvelteKit 3", "in Depth", "Routing, data, remote functions and deployment", {}),
        ("astro-7-in-depth", astro_art, "#b45cff", "A SENIOR ENGINEER'S GUIDE", "Astro 7", "in Depth", "Islands, content and the server with Svelte 5", {}),
        ("sveltekit-interview-prep", prep_art, "#3d9bff", "NINE DAYS · TWO HOURS A DAY", "SvelteKit", "Interview Prep", "Svelte 5, SvelteKit 3 and testing", {}),
        ("living-well-with-type-2-diabetes", diabetes_art, "#2bc4a6", "A PRACTICAL GUIDE", "Living Well", "with Type 2 Diabetes", "The things that matter most", {"size2": 140}),
        ("ccdv-f-vol1", lambda a: ccdv_art(a, 1), CCDV, "STUDY HANDBOOK · VOLUME I", "CCDV-F", "A Study Handbook", "Claude Certified Developer – Foundations", {"note": NOTE, "size2": 130}),
        ("ccdv-f-vol2", lambda a: ccdv_art(a, 2), CCDV, "STUDY HANDBOOK · VOLUME II", "CCDV-F", "Depth in the Heavy Domains", "Claude Certified Developer – Foundations", {"note": NOTE, "size2": 112}),
        ("ccdv-f-vol3", lambda a: ccdv_art(a, 3), CCDV, "STUDY HANDBOOK · VOLUME III", "CCDV-F", "Twelve Advanced Mock Exams", "Claude Certified Developer – Foundations", {"note": NOTE, "size2": 112}),
        ("braceml", braceml_art, "#3ddc97", "A BRACE-BASED TEMPLATE LANGUAGE", "BraceML", "No closing tags", "Compiles to HTML, Svelte 5 and React", {"size2": 150}),
    ]
    full = HERE / "full"
    full.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        for name, art_fn, accent, label, l1, l2, sub, extra in specs:
            art, glow = art_fn(accent)
            page = Path(tmp) / f"{name}.html"
            page.write_text(cover(art, accent, glow, label, l1, l2, sub, **extra), encoding="utf-8")
            for out, size in ((HERE / f"{name}.png", "300,450"), (full / f"{name}.png", "1600,2400")):
                subprocess.run([str(CHROME), "--headless=new", "--disable-gpu", "--hide-scrollbars",
                                "--allow-file-access-from-files", "--force-device-scale-factor=1",
                                f"--window-size={size}", "--virtual-time-budget=3000",
                                f"--screenshot={out}", page.as_uri()],
                               check=True, capture_output=True)
            print(name)


if __name__ == "__main__":
    build()
