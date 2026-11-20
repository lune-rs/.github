"""Generate lune-rs profile SVGs (dark/light banner, library cards) with RznSans text as outlines.

GitHub serves README images through <img>, which cannot load web fonts, so text is converted to paths.
"""
import random, sys, os
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

FONTS = "~/Projects/RznType/RznSans/fonts/desktop"
OUT = sys.argv[1]
_cache = {}

def font(w):
    if w not in _cache:
        _cache[w] = TTFont(f"{FONTS}/RznSans-{w}.ttf")
    return _cache[w]

def kern_pairs(f):
    pairs = {}
    if "kern" in f:
        for t in f["kern"].kernTables:
            pairs.update(t.kernTable)
    return pairs

def text(s, x, y, size, weight="Regular", fill="#fff", tracking=0.0, anchor="start", opacity=1):
    f = font(weight)
    upm = f["head"].unitsPerEm
    cmap = f.getBestCmap(); gs = f.getGlyphSet(); hmtx = f["hmtx"]
    sc = size / upm
    names = [cmap.get(ord(c), ".notdef") for c in s]
    adv = [hmtx[n][0] + tracking * upm for n in names]
    width = sum(adv) * sc
    if anchor == "middle": x -= width / 2
    elif anchor == "end": x -= width
    d = []; cx = 0
    for n, a in zip(names, adv):
        pen = SVGPathPen(gs)
        gs[n].draw(TransformPen(pen, (sc, 0, 0, -sc, x + cx * sc, y)))
        d.append(pen.getCommands()); cx += a
    return f'<path fill="{fill}" fill-opacity="{opacity}" d="{" ".join(d)}"/>', width

THEMES = {
    "dark": dict(bg0="#0d0f14", bg1="#1b1e27", ink="#f3f4f7", sub="#a9afbd", dim="#6b7285",
                 moon0="#f4f1e8", moon1="#c9cdd8", glow="#9fb4ff", star="#ffffff", rust="#f0743e",
                 ring="#ffffff", chip="#ffffff", chipo=0.06, chipb=0.14),
    "light": dict(bg0="#f7f8fb", bg1="#e6e9f1", ink="#14161c", sub="#4a5162", dim="#7a8194",
                  moon0="#2a2f3d", moon1="#4b5470", glow="#6d82d6", star="#3b4256", rust="#d4561f",
                  ring="#1b1f2a", chip="#14161c", chipo=0.04, chipb=0.12),
}

def moon(cx, cy, r, t, idp):
    # crescent: full disc minus an offset disc, with a soft halo
    return f'''
  <defs>
    <radialGradient id="{idp}halo" cx="{cx}" cy="{cy}" r="{r*2.6}" gradientUnits="userSpaceOnUse">
      <stop offset="0" stop-color="{t['glow']}" stop-opacity="0.32"/>
      <stop offset="0.45" stop-color="{t['glow']}" stop-opacity="0.08"/>
      <stop offset="1" stop-color="{t['glow']}" stop-opacity="0"/>
    </radialGradient>
    <linearGradient id="{idp}moon" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="{t['moon0']}"/><stop offset="1" stop-color="{t['moon1']}"/>
    </linearGradient>
    <mask id="{idp}cut"><rect x="{cx-r*2}" y="{cy-r*2}" width="{r*4}" height="{r*4}" fill="#fff"/>
      <circle cx="{cx+r*0.46}" cy="{cy-r*0.30}" r="{r*0.86}" fill="#000"/></mask>
  </defs>
  <circle cx="{cx}" cy="{cy}" r="{r*2.6}" fill="url(#{idp}halo)"/>
  <circle cx="{cx}" cy="{cy}" r="{r}" fill="url(#{idp}moon)" mask="url(#{idp}cut)"/>'''

def banner(theme):
    t = THEMES[theme]; W, H = 1280, 420; p = f"b{theme[0]}"
    rnd = random.Random(7)
    stars = []
    for _ in range(70):
        x, y = rnd.uniform(0, W), rnd.uniform(0, H)
        if 80 < x < 760 and 110 < y < 330:  # keep the text area clean
            continue
        stars.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rnd.uniform(0.6,1.7):.2f}" fill="{t["star"]}" opacity="{rnd.uniform(0.12,0.55):.2f}"/>')
    title, tw = text("lune-rs", 96, 222, 112, "Bold", t["ink"], tracking=-0.02)
    tag, _ = text("Pure-Rust libraries for building native apps and tools", 100, 278, 30, "Regular", t["sub"])
    # chips
    chips = []; cx = 100
    for label in ["100% Rust", "Native, no web engine", "MIT / Apache-2.0"]:
        lp, lw = text(label, cx + 18, 342, 19, "Medium", t["ink"], opacity=0.85)
        chips.append(f'<rect x="{cx}" y="315" width="{lw+36:.1f}" height="38" rx="19" fill="{t["chip"]}" fill-opacity="{t["chipo"]}" stroke="{t["chip"]}" stroke-opacity="{t["chipb"]}"/>{lp}')
        cx += lw + 36 + 12
    dot = f'<circle cx="{96+tw+14:.1f}" cy="214" r="9" fill="{t["rust"]}"/>'
    rings = "".join(
        f'<ellipse cx="1010" cy="210" rx="{rx}" ry="{rx*0.30:.1f}" fill="none" stroke="{t["ring"]}" stroke-opacity="{o}" transform="rotate(-14 1010 210)"/>'
        for rx, o in [(250, 0.07), (195, 0.10)])
    sat = f'<circle cx="{1010-250*0.97:.1f}" cy="{210+60:.1f}" r="5" fill="{t["rust"]}" transform="rotate(-14 1010 210)"/>'
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="lune-rs — pure-Rust libraries for building native apps and tools">
  <defs><linearGradient id="{p}bg" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="{t['bg0']}"/><stop offset="1" stop-color="{t['bg1']}"/></linearGradient>
    <clipPath id="{p}clip"><rect width="{W}" height="{H}" rx="24"/></clipPath></defs>
  <g clip-path="url(#{p}clip)">
  <rect width="{W}" height="{H}" fill="url(#{p}bg)"/>
  {''.join(stars)}
  {rings}
  {moon(1010, 210, 108, t, p)}
  {sat}
  {title}{dot}{tag}{''.join(chips)}
  </g>
</svg>'''

def card(theme, name, kind, lines, accent):
    t = THEMES[theme]; W, H = 640, 200; p = f"c{name}{theme[0]}"
    n, nw = text(name, 36, 92, 52, "Bold", t["ink"], tracking=-0.015)
    k, kw = text(kind.upper(), 0, 0, 14, "Medium", accent, tracking=0.12)
    # place the kind chip right of the name
    k, kw = text(kind.upper(), 36 + nw + 34, 80, 14, "Medium", accent, tracking=0.12)
    chip = f'<rect x="{36+nw+20:.1f}" y="60" width="{kw+28:.1f}" height="30" rx="15" fill="{accent}" fill-opacity="0.12"/>'
    body = "".join(text(l, 36, 136 + i * 28, 20, "Regular", t["sub"])[0] for i, l in enumerate(lines))
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{name}: {kind}">
  <defs><linearGradient id="{p}bg" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="{t['bg0']}"/><stop offset="1" stop-color="{t['bg1']}"/></linearGradient></defs>
  <rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="18" fill="url(#{p}bg)" stroke="{t['chip']}" stroke-opacity="{t['chipb']}"/>
  <rect x="36" y="30" width="44" height="4" rx="2" fill="{accent}"/>
  {n}{chip}{k}{body}
</svg>'''

os.makedirs(OUT, exist_ok=True)
for th in THEMES:
    open(f"{OUT}/banner-{th}.svg", "w").write(banner(th))
    open(f"{OUT}/luneui-{th}.svg", "w").write(card(th, "luneui", "UI toolkit",
        ["Glass-style native UI on wgpu: painter, ~100 widgets,", "OS materials, themes and accessibility."], "#7c9cff" if th == "dark" else "#4762d1"))
    open(f"{OUT}/lunepack-{th}.svg", "w").write(card(th, "lunepack", "Installer + updater",
        ["Package releases, build installers, ship signed", "updates, then apply them and restart the app."], THEMES[th]["rust"]))
print("ok")

def flow(theme):
    t = THEMES[theme]; W, H = 1280, 300; acc = t["rust"]; p = f"f{theme[0]}"
    out = []
    groups = [("ON YOUR BUILD MACHINE", "lunepack CLI", 40, ["pack", "sign", "publish feed"]),
              ("IN YOUR APP", "lunepack crate + runtime", 660, ["check", "fetch + stage", "apply + restart"])]
    for gi, (lab, sub, gx, steps) in enumerate(groups):
        out.append(f'<rect x="{gx}" y="40" width="580" height="220" rx="18" fill="{t["chip"]}" fill-opacity="{t["chipo"]}" stroke="{t["chip"]}" stroke-opacity="{t["chipb"]}"/>')
        out.append(text(lab, gx + 28, 80, 14, "Medium", acc, tracking=0.12)[0])
        out.append(text(sub, gx + 28, 108, 20, "Medium", t["sub"])[0])
        bw, gap = 162, 17; by = 150
        for i, s in enumerate(steps):
            bx = gx + 28 + i * (bw + gap)
            out.append(f'<rect x="{bx}" y="{by}" width="{bw}" height="64" rx="12" fill="{t["bg0"]}" stroke="{t["chip"]}" stroke-opacity="{t["chipb"]+0.06}"/>')
            out.append(text(s, bx + bw / 2, by + 39, 19, "Medium", t["ink"], anchor="middle")[0])
            if i < len(steps) - 1:
                ax = bx + bw + 2
                out.append(f'<path d="M{ax} {by+32} h{gap-6} m-5 -5 l5 5 l-5 5" fill="none" stroke="{t["dim"]}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>')
    # bridge between groups
    out.append(f'<path d="M622 182 h34" stroke="{acc}" stroke-width="2.5" stroke-dasharray="5 5"/>'
               f'<path d="M650 176 l7 6 l-7 6" fill="none" stroke="{acc}" stroke-width="2.5" stroke-linecap="round"/>')
    out.append(text("signed feed + packs over HTTPS or file:", 640, 288, 15, "Regular", t["dim"], anchor="middle")[0])
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="lunepack flow: pack, sign, publish feed on the build machine; check, download and stage, apply and restart in the app">
  {''.join(out)}
</svg>'''

for th in THEMES:
    open(f"{OUT}/lunepack-flow-{th}.svg", "w").write(flow(th))
