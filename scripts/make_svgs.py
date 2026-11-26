"""Generate the Gotham-noir SVGs for the JcXplore profile README.

Usage:  python -I -X utf8 scripts/make_svgs.py assets
Seeds are fixed, so unchanged files regenerate byte-identical.
"""
import os
import random
import sys
from html import escape

# Palette
NIGHT = "#0b0d12"     # page-dark background
SKY_TOP = "#0f131b"
SKY_LOW = "#1c2230"
CITY = "#07080c"      # skyline silhouette
SLATE = "#2a303c"
STEEL = "#8a94a6"
FOG = "#c7ccd6"
SIGNAL = "#f5c518"    # searchlight yellow
AMBER = "#e0a800"

MONO = "'Courier New', Courier, monospace"
HEAVY = "Impact, 'Arial Black', 'Helvetica Neue', Arial, sans-serif"


def t(s):
    return escape(s, quote=False)


# ---------------------------------------------------------------- pieces

def skyline(rng, w, base, min_h, max_h, fill, windows=True, win_density=0.18):
    """Jagged gothic skyline: blocks, spires and lit windows."""
    out = []
    x = -10
    while x < w + 10:
        bw = rng.randint(22, 60)
        bh = rng.randint(min_h, max_h)
        top = base - bh
        out.append(f'<rect x="{x}" y="{top}" width="{bw}" height="{bh + 2}" fill="{fill}"/>')
        r = rng.random()
        if r < 0.25:  # spire
            cx = x + bw / 2
            sh = rng.randint(14, 40)
            out.append(f'<polygon points="{cx - bw * 0.22:.1f},{top} {cx:.1f},{top - sh} {cx + bw * 0.22:.1f},{top}" fill="{fill}"/>')
        elif r < 0.45:  # stepped top
            out.append(f'<rect x="{x + bw * 0.2:.1f}" y="{top - 10}" width="{bw * 0.6:.1f}" height="11" fill="{fill}"/>')
            out.append(f'<rect x="{x + bw * 0.4:.1f}" y="{top - 22}" width="2" height="12" fill="{fill}"/>')
        if windows:
            for wy in range(top + 8, base - 6, 9):
                for wx in range(int(x) + 5, int(x + bw) - 5, 8):
                    if rng.random() < win_density:
                        op = rng.choice([0.35, 0.55, 0.8])
                        out.append(f'<rect x="{wx}" y="{wy}" width="3" height="4" fill="{SIGNAL}" opacity="{op}"/>')
        x += bw - rng.randint(0, 6)
    return "".join(out)


def bat(cx, cy, s, fill=CITY, op=1.0):
    """Small generic bat silhouette (not any brand emblem)."""
    p = [(-10, 0), (-7, -3), (-4, -1), (-2, -4), (-1, -2), (0, -3), (1, -2), (2, -4), (4, -1),
         (7, -3), (10, 0), (7, 1), (5, 3), (3, 1), (0, 4), (-3, 1), (-5, 3), (-7, 1)]
    pts = " ".join(f"{cx + x * s:.1f},{cy + y * s:.1f}" for x, y in p)
    return f'<polygon points="{pts}" fill="{fill}" opacity="{op}"/>'


def rain(rng, w, h, n, op=0.18):
    out = []
    for _ in range(n):
        x = rng.uniform(0, w)
        y = rng.uniform(0, h)
        ln = rng.uniform(8, 18)
        out.append(f'<line x1="{x:.1f}" y1="{y:.1f}" x2="{x - ln * 0.25:.1f}" y2="{y + ln:.1f}" stroke="{FOG}" stroke-width="1" opacity="{op}"/>')
    return "".join(out)


def beam(x0, y0, x1, y1, spread, op):
    """Searchlight cone from (x0,y0) toward (x1,y1)."""
    return (f'<polygon points="{x0 - 3},{y0} {x1 - spread},{y1} {x1 + spread},{y1} {x0 + 3},{y0}" '
            f'fill="url(#beam)" opacity="{op}"/>')


def pill(x, y, w, h, label, fill="none", stroke=SIGNAL, color=SIGNAL, size=10):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="2" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>'
            f'<text x="{x + w / 2:.1f}" y="{y + h / 2 + size * 0.36:.1f}" font-family="{MONO}" font-size="{size}" '
            f'font-weight="bold" fill="{color}" text-anchor="middle">{t(label)}</text>')


def text_w(s, size):
    return len(s) * size * 0.6


# ---------------------------------------------------------------- banner

def banner():
    rng = random.Random(7)
    W, H = 1200, 340
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" '
         f'aria-label="John Christian Austria, junior developer, BSIT at Tarlac State University">',
         '<defs>',
         f'<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{SKY_TOP}"/><stop offset="1" stop-color="{SKY_LOW}"/></linearGradient>',
         f'<linearGradient id="beam" x1="0" y1="1" x2="0" y2="0"><stop offset="0" stop-color="{SIGNAL}" stop-opacity="0.55"/><stop offset="1" stop-color="{SIGNAL}" stop-opacity="0"/></linearGradient>',
         f'<radialGradient id="moon"><stop offset="0" stop-color="{FOG}" stop-opacity="0.9"/><stop offset="0.55" stop-color="{FOG}" stop-opacity="0.25"/><stop offset="1" stop-color="{FOG}" stop-opacity="0"/></radialGradient>',
         f'<radialGradient id="spot"><stop offset="0" stop-color="{SIGNAL}" stop-opacity="0.35"/><stop offset="1" stop-color="{SIGNAL}" stop-opacity="0"/></radialGradient>',
         f'<linearGradient id="fade" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{NIGHT}" stop-opacity="0.92"/><stop offset="0.55" stop-color="{NIGHT}" stop-opacity="0.55"/><stop offset="1" stop-color="{NIGHT}" stop-opacity="0"/></linearGradient>',
         f'<clipPath id="clip"><rect width="{W}" height="{H}" rx="10"/></clipPath>',
         '</defs><g clip-path="url(#clip)">',
         f'<rect width="{W}" height="{H}" fill="url(#sky)"/>',
         f'<circle cx="1040" cy="78" r="120" fill="url(#moon)" opacity="0.5"/>',
         f'<circle cx="1040" cy="78" r="34" fill="{FOG}" opacity="0.85"/>',
         # searchlight beams + the glow they hit on the clouds
         beam(860, 300, 1010, -10, 70, 0.8),
         beam(1110, 300, 930, -10, 55, 0.45),
         f'<ellipse cx="985" cy="40" rx="140" ry="48" fill="url(#spot)"/>',
         ]
    # cloud bands
    for i in range(6):
        cy = rng.randint(30, 120)
        cx = rng.randint(0, W)
        o.append(f'<ellipse cx="{cx}" cy="{cy}" rx="{rng.randint(120, 260)}" ry="{rng.randint(8, 16)}" fill="{SLATE}" opacity="0.35"/>')
    # bats circling the moon
    for cx, cy, s in [(985, 120, 1.4), (1090, 140, 1.0), (930, 165, 0.8), (1150, 100, 0.7), (1015, 175, 0.6)]:
        o.append(bat(cx, cy, s))
    o.append(skyline(rng, W, H, 70, 150, "#11151d", windows=True, win_density=0.08))
    o.append(skyline(rng, W, H, 30, 95, CITY, windows=True, win_density=0.14))
    o.append(rain(rng, W, H, 140, 0.13))
    o.append(f'<rect width="760" height="{H}" fill="url(#fade)"/>')
    # text
    o.append(f'<text x="56" y="86" font-family="{MONO}" font-size="14" letter-spacing="3" fill="{STEEL}">&gt; CASE FILE: TARLAC CITY, PH · NIGHT SHIFT</text>')
    o.append(f'<text x="54" y="160" font-family="{HEAVY}" font-weight="bold" font-size="60" letter-spacing="2" fill="{FOG}">JOHN CHRISTIAN</text>')
    o.append(f'<text x="54" y="222" font-family="{HEAVY}" font-weight="bold" font-size="60" letter-spacing="2" fill="{SIGNAL}">AUSTRIA</text>')
    o.append(f'<rect x="56" y="240" width="64" height="3" fill="{SIGNAL}"/>')
    o.append(f'<text x="56" y="270" font-family="{MONO}" font-size="15" letter-spacing="2" fill="{FOG}">JUNIOR DEVELOPER · BSIT @ TARLAC STATE UNIVERSITY</text>')
    x = 56
    for label in ["Mobile Dev", "Full Stack", "AI / ML"]:
        w = text_w(label, 12) + 26
        o.append(pill(x, 288, w, 24, label, fill=NIGHT, size=12))
        x += w + 10
    o.append('</g>')
    o.append(f'<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="10" fill="none" stroke="{SLATE}" stroke-width="2"/>')
    o.append('</svg>')
    return "".join(o)


# ---------------------------------------------------------------- badges

def badge(left, right, aria=None):
    size = 11
    lw = int(text_w(left, size) + 20)
    rw = int(text_w(right, size) + 20)
    w = lw + rw
    a = t(aria or f"{left}: {right}")
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} 24" width="{w}" height="24" role="img" aria-label="{a}">'
            f'<rect x="0.75" y="0.75" width="{w - 1.5}" height="22.5" rx="2" fill="{NIGHT}" stroke="{SIGNAL}" stroke-width="1.5"/>'
            f'<rect x="0.75" y="0.75" width="{lw}" height="22.5" rx="2" fill="{SIGNAL}"/>'
            f'<text x="{lw / 2 + 0.75:.1f}" y="16" font-family="{MONO}" font-size="{size}" font-weight="bold" fill="{NIGHT}" text-anchor="middle">{t(left)}</text>'
            f'<text x="{lw + rw / 2:.1f}" y="16" font-family="{MONO}" font-size="{size}" font-weight="bold" fill="{FOG}" text-anchor="middle">{t(right)}</text>'
            '</svg>')


# ---------------------------------------------------------------- cards

def icon_hand(cx, cy):
    c = SIGNAL
    return (f'<g fill="{c}">'
            f'<rect x="{cx - 22}" y="{cy - 6}" width="44" height="40" rx="10"/>'
            + "".join(f'<rect x="{cx - 22 + i * 11.5:.1f}" y="{cy - 38 + abs(i - 1.5) * 6:.1f}" width="9" height="40" rx="4.5"/>' for i in range(4))
            + f'<rect x="{cx + 14}" y="{cy}" width="9" height="30" rx="4.5" transform="rotate(-40 {cx + 18} {cy + 26})"/>'
            '</g>')


def icon_chair(cx, cy):
    c = SIGNAL
    return (f'<g fill="{c}">'
            f'<rect x="{cx - 30}" y="{cy - 34}" width="60" height="38" rx="10"/>'
            f'<rect x="{cx - 42}" y="{cy - 12}" width="16" height="36" rx="7"/>'
            f'<rect x="{cx + 26}" y="{cy - 12}" width="16" height="36" rx="7"/>'
            f'<rect x="{cx - 28}" y="{cy + 4}" width="56" height="18" rx="5"/>'
            f'<rect x="{cx - 36}" y="{cy + 22}" width="6" height="12"/><rect x="{cx + 30}" y="{cy + 22}" width="6" height="12"/>'
            '</g>')


def icon_reel(cx, cy):
    c = SIGNAL
    o = [f'<rect x="{cx - 50}" y="{cy - 26}" width="56" height="52" rx="3" fill="none" stroke="{c}" stroke-width="4"/>']
    for i in range(5):
        o.append(f'<rect x="{cx - 46 + i * 10}" y="{cy - 22}" width="5" height="5" fill="{c}"/>')
        o.append(f'<rect x="{cx - 46 + i * 10}" y="{cy + 17}" width="5" height="5" fill="{c}"/>')
    o.append(f'<path d="M{cx + 12} {cy} l12 0" stroke="{c}" stroke-width="4"/><polygon points="{cx + 22},{cy - 8} {cx + 32},{cy} {cx + 22},{cy + 8}" fill="{c}"/>')
    o.append(f'<rect x="{cx + 36}" y="{cy - 36}" width="30" height="56" rx="5" fill="{c}"/>')
    o.append(f'<polygon points="{cx + 46},{cy - 14} {cx + 58},{cy - 8} {cx + 46},{cy - 2}" fill="{NIGHT}"/>')
    return "".join(o)


def icon_fox(cx, cy):
    c = SIGNAL
    return (f'<path d="M{cx - 36} {cy - 24} h72 a10 10 0 0 1 10 10 v36 a10 10 0 0 1 -10 10 h-46 l-14 14 v-14 h-12 '
            f'a10 10 0 0 1 -10 -10 v-36 a10 10 0 0 1 10 -10z" fill="{c}"/>'
            f'<polygon points="{cx - 28},{cy - 24} {cx - 20},{cy - 40} {cx - 12},{cy - 24}" fill="{c}"/>'
            f'<polygon points="{cx + 12},{cy - 24} {cx + 20},{cy - 40} {cx + 28},{cy - 24}" fill="{c}"/>'
            + "".join(f'<circle cx="{cx + d}" cy="{cy + 4}" r="5" fill="{NIGHT}"/>' for d in (-16, 0, 16)))


def icon_flow(cx, cy):
    """Workflow nodes: trigger -> switch -> three branches."""
    c = SIGNAL
    o = [f'<g stroke="{c}" stroke-width="3" fill="none">',
         f'<path d="M{cx - 44} {cy} H{cx - 8}"/>',
         f'<path d="M{cx + 8} {cy} C{cx + 24} {cy} {cx + 22} {cy - 26} {cx + 38} {cy - 26}"/>',
         f'<path d="M{cx + 8} {cy} H{cx + 38}"/>',
         f'<path d="M{cx + 8} {cy} C{cx + 24} {cy} {cx + 22} {cy + 26} {cx + 38} {cy + 26}"/>',
         '</g>',
         f'<rect x="{cx - 62}" y="{cy - 12}" width="24" height="24" rx="6" fill="{c}"/>',
         f'<rect x="{cx - 12}" y="{cy - 14}" width="28" height="28" rx="6" fill="{c}"/>',
         f'<path d="M{cx - 4} {cy - 6} h12 M{cx - 4} {cy} h12 M{cx - 4} {cy + 6} h12" stroke="{NIGHT}" stroke-width="2.5"/>']
    for dy in (-26, 0, 26):
        o.append(f'<rect x="{cx + 38}" y="{cy + dy - 9}" width="18" height="18" rx="5" fill="{c}"/>')
    return "".join(o)


CARDS = [
    ("signbridge", 1, "SignBridge", "REACT NATIVE · MEDIAPIPE",
     ["Reads Filipino Sign Language from the", "camera into text and speech, offline."],
     ["EXPO", "MEDIAPIPE", "ON-DEVICE ML"], icon_hand, True),
    ("furnitune", 2, "FurniTune", "REACT NATIVE · FASTAPI",
     ["Furniture shopping app with an AI", "recommender (embeddings + FAISS)."],
     ["FIRESTORE", "FASTAPI", "FAISS"], icon_chair, True),
    ("openshorts", 3, "OpenShorts", "PYTHON · DOCKER",
     ["Cuts long videos into vertical Shorts,", "TikToks and Reels. MIT, self-hostable."],
     ["WHISPER", "FFMPEG", "DOCKER"], icon_reel, True),
    ("chatfox", 4, "ChatFox", "REACT NATIVE · EXPRESS",
     ["University AI assistant that answers", "from TSU's own documents (RAG)."],
     ["MONGODB", "OPENAI", "RAG"], icon_fox, False),
    ("n8n", 5, "n8n Idea Pipeline", "N8N · GEMINI · OPENAI",
     ["AI organizes creator notes into ideas;", "admin approves, rejects or revises."],
     ["SHEETS", "CALENDAR", "GMAIL"], icon_flow, False),
]


def card(slug, n, name, stack, lines, tags, icon, has_repo):
    rng = random.Random(100 + n)
    W, H = 400, 300
    aria = t(f"{name}: {' '.join(lines)}")
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="{aria}">',
         '<defs>',
         f'<linearGradient id="sk{n}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{SKY_TOP}"/><stop offset="1" stop-color="{SKY_LOW}"/></linearGradient>',
         f'<radialGradient id="gl{n}"><stop offset="0" stop-color="{SIGNAL}" stop-opacity="0.28"/><stop offset="1" stop-color="{SIGNAL}" stop-opacity="0"/></radialGradient>',
         f'<clipPath id="c{n}"><rect x="2" y="2" width="396" height="296" rx="6"/></clipPath>',
         f'</defs><g clip-path="url(#c{n})">',
         f'<rect width="{W}" height="{H}" fill="{NIGHT}"/>',
         f'<rect width="{W}" height="132" fill="url(#sk{n})"/>',
         f'<circle cx="200" cy="68" r="90" fill="url(#gl{n})"/>',
         skyline(rng, W, 132, 12, 42, CITY, windows=True, win_density=0.12),
         rain(rng, W, 132, 30, 0.12),
         icon(200, 70),
         bat(330, 34, 0.9, fill=STEEL, op=0.6),
         bat(355, 50, 0.6, fill=STEEL, op=0.45),
         f'<rect y="131" width="{W}" height="2" fill="{SIGNAL}" opacity="0.8"/>',
         '</g>',
         f'<rect x="2" y="2" width="396" height="296" rx="6" fill="none" stroke="{SLATE}" stroke-width="2"/>',
         pill(14, 14, 110, 18, f"CASE FILE / {n:02d}", fill=NIGHT, size=10),
         f'<text x="20" y="166" font-family="{HEAVY}" font-weight="bold" font-size="24" letter-spacing="1" fill="{FOG}">{t(name)}</text>',
         f'<text x="20" y="186" font-family="{MONO}" font-size="11" letter-spacing="1.5" fill="{SIGNAL}">{t(stack)}</text>',
         ]
    for i, line in enumerate(lines):
        o.append(f'<text x="20" y="{208 + i * 16}" font-family="{MONO}" font-size="12" fill="{STEEL}">{t(line)}</text>')
    x = 20
    for tag in tags:
        w = text_w(tag, 10) + 16
        o.append(pill(x, 236, w, 18, tag, stroke=SLATE, color=FOG, size=10))
        x += w + 8
    if has_repo:
        o.append(pill(20, 264, 150, 24, "View repository ↗", fill=SIGNAL, color=NIGHT, size=12))
    else:
        o.append(pill(20, 264, 150, 24, "Repo coming soon", size=12))
    o.append('</svg>')
    return "".join(o)


# ---------------------------------------------------------------- main

def main(out):
    os.makedirs(out, exist_ok=True)
    files = {
        "banner.svg": banner(),
        "badge-bsit.svg": badge("BSIT", "Tarlac State University"),
        "badge-cumlaude.svg": badge("Cum Laude", "2026"),
        "badge-open.svg": badge("Open to", "junior dev roles"),
        "badge-linkedin.svg": badge("in", "LinkedIn"),
        "badge-email.svg": badge("@", "Email"),
        "badge-github.svg": badge("</>", "Repositories"),
    }
    for c in CARDS:
        files[f"card-{c[0]}.svg"] = card(*c)
    for name, svg in files.items():
        with open(os.path.join(out, name), "w", encoding="utf-8", newline="\n") as f:
            f.write(svg + "\n")
    print(f"wrote {len(files)} files to {out}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "assets")
