"""Renders every image on the profile README as hand-set SVG.

    python scripts/build.py                 # static pieces  -> assets/
    python scripts/build.py --stats DIR     # live numbers   -> DIR/stats-{dark,light}.svg

Fonts are subset per file and embedded, so each SVG renders identically on
GitHub's image proxy with no external requests. Requires fonttools + brotli.
"""
import base64
import datetime as dt
import io
import json
import math
import os
import subprocess
import sys
import urllib.request
from xml.sax.saxutils import escape

from fontTools import subset
from fontTools.ttLib import TTFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT_DIR = os.path.join(ROOT, "assets", "fonts")
OUT = os.path.join(ROOT, "assets")
W = 900
EASE = "cubic-bezier(.2,.72,.18,1)"

# ---------------------------------------------------------------- palette
# Mirrors the portfolio (saud-satopay.vercel.app): ink, parchment, vermilion.
THEMES = {
    "dark": dict(bg="#100e0a", card="#17140d", fg="#f1e6cd", dim="#b5aa8c", mute="#867c64",
                 hair="#2b2618", hair2="#443c28", accent="#ff4e1f", gilt="#c9a15a", grain=.07),
    "light": dict(bg="#f1e6cd", card="#e9dbb8", fg="#16120a", dim="#4d4633", mute="#857a5c",
                  hair="#d8c8a0", hair2="#c3ad7f", accent="#e2401a", gilt="#9a7630", grain=.10),
}

# ---------------------------------------------------------------- fonts
FONT_FILES = {
    "disp": "fraunces-black.ttf",          # display, heavy roman
    "ital": "fraunces-italic-light.ttf",   # display, light italic
    "italb": "fraunces-italic-bold.ttf",   # numerals & metrics
    "body": "archivo-regular.ttf",
    "caps": "archivo-expanded-bold.ttf",   # small tracked labels
    "mono": "jetbrains-mono.ttf",
}


class Font:
    def __init__(self, key):
        self.key = key
        self.path = os.path.join(FONT_DIR, FONT_FILES[key])
        self.tt = TTFont(self.path)
        self.cmap = self.tt.getBestCmap()
        self.hmtx = self.tt["hmtx"]
        self.upm = self.tt["head"].unitsPerEm

    def width(self, s, size, ls=0.0):
        units = 0
        for ch in s:
            g = self.cmap.get(ord(ch))
            if g is None:
                raise ValueError(f"{self.key} has no glyph for {ch!r} in {s!r}")
            units += self.hmtx[g][0]
        return units * size / self.upm + ls * max(len(s) - 1, 0)


FONTS = {k: Font(k) for k in FONT_FILES}


def woff2_b64(key, chars):
    f = TTFont(FONTS[key].path)
    opts = subset.Options()
    opts.flavor = "woff2"
    opts.layout_features = ["kern", "liga"]
    opts.name_IDs = []
    opts.notdef_outline = True
    ss = subset.Subsetter(opts)
    ss.populate(text="".join(sorted(chars)))
    ss.subset(f)
    buf = io.BytesIO()
    f.flavor = "woff2"
    f.save(buf)
    return base64.b64encode(buf.getvalue()).decode()


def wrap(s, font, size, max_w, ls=0.0):
    lines, cur = [], ""
    for word in s.split():
        trial = f"{cur} {word}".strip()
        if FONTS[font].width(trial, size, ls) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


# ---------------------------------------------------------------- document
class Svg:
    def __init__(self, w, h, theme, title):
        self.w, self.h, self.theme, self.title = w, h, theme, title
        self.p = THEMES[theme]
        self.used = {}
        self.body, self.defs, self.css = [], [], []

    def c(self, name):
        return self.p.get(name, name)

    def add(self, s):
        self.body.append(s)

    def text(self, x, y, s, font, size, fill="fg", anchor="start", ls=0.0, cls="", style="", opacity=None):
        FONTS[font].width(s, size, ls)  # validates glyph coverage
        self.used.setdefault(font, set()).update(s)
        attrs = [f'x="{x:.1f}"', f'y="{y:.1f}"', f'font-family="{font}"', f'font-size="{size}"',
                 f'fill="{self.c(fill)}"']
        if anchor != "start":
            attrs.append(f'text-anchor="{anchor}"')
        if ls:
            attrs.append(f'letter-spacing="{ls}"')
        if cls:
            attrs.append(f'class="{cls}"')
        if style:
            attrs.append(f'style="{style}"')
        if opacity is not None:
            attrs.append(f'opacity="{opacity}"')
        self.add(f"<text {' '.join(attrs)}>{escape(s)}</text>")
        return FONTS[font].width(s, size, ls)

    def runs(self, x, y, parts, anchor="start", cls="", style=""):
        """Mixed-face line. parts = [(text, font, size, fill), ...]"""
        total = sum(FONTS[f].width(t, s) for t, f, s, _ in parts)
        if anchor == "middle":
            x -= total / 2
        elif anchor == "end":
            x -= total
        self.add(f'<g class="{cls}" style="{style}">' if cls or style else "<g>")
        for t, f, s, fill in parts:
            x += self.text(x, y, t, f, s, fill)
        self.add("</g>")
        return total

    def rule(self, x1, y, x2, color="hair2", width=1, cls="", style=""):
        c = f' class="{cls}"' if cls else ""
        st = f' style="{style}"' if style else ""
        self.add(f'<line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" stroke="{self.c(color)}" '
                 f'stroke-width="{width}"{c}{st}/>')

    def frame(self, fill="bg", inset=None, grain=True, radius=0):
        self.add(f'<rect width="{self.w}" height="{self.h}" rx="{radius}" fill="{self.c(fill)}"/>')
        if grain:
            self.defs.append(
                '<filter id="grain" x="0" y="0" width="100%" height="100%">'
                '<feTurbulence type="fractalNoise" baseFrequency=".9" numOctaves="2" stitchTiles="stitch"/>'
                '<feColorMatrix type="saturate" values="0"/></filter>')
            self.add(f'<rect width="{self.w}" height="{self.h}" rx="{radius}" filter="url(#grain)" '
                     f'opacity="{self.p["grain"]}"/>')
        if inset is not None:
            a, b = inset, inset + 5
            self.add(f'<rect x="{a}" y="{a}" width="{self.w - 2 * a}" height="{self.h - 2 * a}" '
                     f'fill="none" stroke="{self.c("gilt")}" stroke-width="1.2" opacity=".75"/>')
            self.add(f'<rect x="{b}" y="{b}" width="{self.w - 2 * b}" height="{self.h - 2 * b}" '
                     f'fill="none" stroke="{self.c("gilt")}" stroke-width=".6" opacity=".45"/>')

    def render(self):
        faces = "".join(
            f"@font-face{{font-family:{k};src:url(data:font/woff2;base64,{woff2_b64(k, chars)}) format('woff2')}}"
            for k, chars in sorted(self.used.items()))
        base_css = f"""
text{{font-kerning:normal}}
.rise{{animation:rise 1.1s {EASE} both}}
.fade{{animation:fade 1.6s ease both}}
.draw{{transform-box:fill-box;transform-origin:left;animation:draw 1.5s {EASE} both}}
.grow{{transform-box:fill-box;transform-origin:bottom;animation:grow 1.2s {EASE} both}}
@keyframes rise{{from{{opacity:0;transform:translateY(22px)}}to{{opacity:1;transform:none}}}}
@keyframes fade{{from{{opacity:0}}to{{opacity:1}}}}
@keyframes draw{{from{{transform:scaleX(0)}}to{{transform:scaleX(1)}}}}
@keyframes grow{{from{{transform:scaleY(0)}}to{{transform:scaleY(1)}}}}
@media (prefers-reduced-motion:reduce){{*{{animation:none!important}}}}"""
        return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.w} {self.h}" '
                f'width="{self.w}" height="{self.h}" role="img" aria-label="{escape(self.title)}">'
                f"<title>{escape(self.title)}</title>"
                f"<style>{faces}{base_css}{''.join(self.css)}</style>"
                f"<defs>{''.join(self.defs)}</defs>{''.join(self.body)}</svg>")


def save(name, build, out=OUT):
    for theme in THEMES:
        svg = build(theme)
        path = os.path.join(out, f"{name}-{theme}.svg")
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(svg.render())
        print(f"  {os.path.relpath(path, ROOT):40s} {os.path.getsize(path) / 1024:6.1f} KB")


# ================================================================ pieces
def polar_path(fn, n=540):
    pts = []
    for k in range(n):
        t = 2 * math.pi * k / n
        r = fn(t)
        pts.append(f"{r * math.cos(t):.1f} {r * math.sin(t):.1f}")
    return "M" + "L".join(pts) + "Z"


def rosette(d, cx, cy):
    """Banknote-style guilloché: lobed curves repeated at small rotations until they weave."""
    bands = [  # (id, radius fn, lobes, copies, spin seconds)
        ("gA", lambda t: 168 + 5 * math.sin(40 * t), 40, 4, 240),
        ("gB", lambda t: 138 + 17 * math.sin(11 * t) + 4 * math.sin(33 * t), 11, 12, -160),
        ("gC", lambda t: 106 + 9 * math.sin(15 * t), 15, 9, 120),
    ]
    d.defs.append(f'<linearGradient id="foilStroke" x1="0" y1="0" x2="1" y2="1">'
                  f'<stop offset="0" stop-color="{d.c("gilt")}"/><stop offset=".5" stop-color="{d.c("fg")}"/>'
                  f'<stop offset="1" stop-color="{d.c("gilt")}"/></linearGradient>')
    op = .5 if d.theme == "dark" else .6
    d.add(f'<g transform="translate({cx} {cy})" fill="none" stroke="url(#foilStroke)" stroke-width=".55" '
          f'opacity="{op}"><g class="fade" style="animation-delay:.3s;animation-duration:2.6s">')
    for gid, fn, lobes, copies, spin in bands:
        d.defs.append(f'<path id="{gid}" d="{polar_path(fn)}"/>')
        d.css.append(f".{gid}{{animation:spin{gid} {abs(spin)}s linear infinite}}"
                     f"@keyframes spin{gid}{{to{{transform:rotate({360 if spin > 0 else -360}deg)}}}}")
        step = 360 / lobes / copies
        d.add(f'<g class="{gid}">' + "".join(
            f'<use href="#{gid}" transform="rotate({k * step:.2f})"/>' for k in range(copies)) + "</g>")
    for r in (84, 122, 186):
        d.add(f'<circle r="{r}" stroke-width=".4"/>')
    d.add("</g></g>")


def crop_marks(d, gap=6, ln=12):
    s = []
    for x, y, sx, sy in [(0, 0, 1, 1), (d.w, 0, -1, 1), (0, d.h, 1, -1), (d.w, d.h, -1, -1)]:
        ox, oy = x + sx * 16, y + sy * 16
        s.append(f"M{ox - sx * (gap + ln)} {oy}h{sx * ln}M{ox} {oy - sy * (gap + ln)}v{sy * ln}")
    d.add(f'<path d="{"".join(s)}" stroke="{d.c("gilt")}" stroke-width=".8" opacity=".8"/>')


FOIL = {"dark": ["#7a5a22", "#c9a15a", "#f6e2ae", "#fff6dc", "#d8b46a", "#8a6a2f", "#e6c77c"],
        "light": ["#4f3810", "#8a6420", "#c29a4c", "#e2c27e", "#9a7630", "#5e4312", "#a88235"]}


def hero(theme):
    d = Svg(W, 540, theme, "Saud Satopay — AI/ML engineer")
    d.frame(inset=16)
    L, R = 58, W - 58
    cx, cy = 716, 236

    # ambient light: a gilt bloom behind the medallion, a vermilion ember low left
    d.defs.append(f'<radialGradient id="bloom" cx="{cx}" cy="{cy}" r="300" gradientUnits="userSpaceOnUse">'
                  f'<stop offset="0" stop-color="{d.c("gilt")}" stop-opacity="{.20 if theme == "dark" else .22}"/>'
                  f'<stop offset="1" stop-color="{d.c("gilt")}" stop-opacity="0"/></radialGradient>')
    d.defs.append(f'<radialGradient id="ember" cx="120" cy="520" r="360" gradientUnits="userSpaceOnUse">'
                  f'<stop offset="0" stop-color="{d.c("accent")}" stop-opacity="{.13 if theme == "dark" else .08}"/>'
                  f'<stop offset="1" stop-color="{d.c("accent")}" stop-opacity="0"/></radialGradient>')
    d.defs.append(f'<clipPath id="inner"><rect x="21" y="79" width="{W - 42}" height="346"/></clipPath>')
    d.add(f'<rect width="{W}" height="{d.h}" fill="url(#bloom)"/><rect width="{W}" height="{d.h}" fill="url(#ember)"/>')
    d.add('<g clip-path="url(#inner)">')
    rosette(d, cx, cy)
    d.add("</g>")
    crop_marks(d)

    d.text(L, 62, "SAUD SATOPAY — PORTFOLIO OF WORK", "mono", 10.5, "dim", ls=2.2, cls="fade")
    d.text(R, 62, "THANE, INDIA · NO. 2026", "mono", 10.5, "dim", "end", ls=2.2, cls="fade")
    d.rule(L, 78, R, "hair2", 1, cls="draw", style="animation-delay:.1s")

    # the name: gold foil over light italic, each line rising out of its own slot
    stops = FOIL[theme]
    d.defs.append('<linearGradient id="foil" gradientUnits="userSpaceOnUse" x1="50" y1="90" x2="430" y2="250">' +
                  "".join(f'<stop offset="{i / (len(stops) - 1):.2f}" stop-color="{c}"/>' for i, c in enumerate(stops)) +
                  "</linearGradient>")
    d.defs.append('<linearGradient id="glint" gradientUnits="userSpaceOnUse" x1="-260" y1="0" x2="-60" y2="60">'
                  '<stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff" stop-opacity=".85"/>'
                  '<stop offset="1" stop-color="#fff" stop-opacity="0"/>'
                  '<animateTransform attributeName="gradientTransform" type="translate" values="0 0;800 0;800 0" '
                  'keyTimes="0;.35;1" dur="6.5s" begin="1.6s" repeatCount="indefinite"/></linearGradient>')
    d.defs.append('<clipPath id="slot1"><rect x="0" y="84" width="900" height="178"/></clipPath>')
    d.defs.append('<clipPath id="slot2"><rect x="0" y="262" width="900" height="160"/></clipPath>')
    d.css.append(f".up{{animation:up 1.3s {EASE} both}}"
                 f"@keyframes up{{from{{transform:translateY(170px)}}to{{transform:none}}}}")
    d.add('<g clip-path="url(#slot1)"><g class="up" style="animation-delay:.1s">')
    d.text(L - 6, 238, "Saud", "disp", 172, "url(#foil)", ls=-5)
    d.text(L - 6, 238, "Saud", "disp", 172, "url(#glint)", ls=-5, opacity=.55 if theme == "dark" else .45)
    d.add("</g></g>")
    d.add('<g clip-path="url(#slot2)"><g class="up" style="animation-delay:.3s">')
    w = d.text(L - 2, 374, "Satopay", "ital", 150, "fg", ls=-3)
    d.text(L + w, 374, ".", "italb", 150, "accent")
    d.add("</g></g>")

    # medallion
    r = 72
    d.defs.append(f'<path id="ring" d="M {cx} {cy} m -{r - 14} 0 a {r - 14} {r - 14} 0 1 1 {2 * (r - 14)} 0 '
                  f'a {r - 14} {r - 14} 0 1 1 -{2 * (r - 14)} 0"/>')
    d.css.append(f".seal{{transform-origin:{cx}px {cy}px;animation:spin 38s linear infinite}}"
                 f"@keyframes spin{{to{{transform:rotate(360deg)}}}}")
    ring_txt = "NIRMAN 2026 · HACKATHON WINNER · FIRST PRIZE · "
    d.used.setdefault("caps", set()).update(ring_txt)
    circ = 2 * math.pi * (r - 14)
    d.add(f'<g class="fade" style="animation-delay:.6s">'
          f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{d.c("bg")}" stroke="{d.c("accent")}" stroke-width="1.4"/>'
          f'<circle cx="{cx}" cy="{cy}" r="{r - 27}" fill="none" stroke="{d.c("accent")}" stroke-width=".8"/>'
          f'<g class="seal"><text font-family="caps" font-size="9.2" fill="{d.c("accent")}">'
          f'<textPath href="#ring" textLength="{circ:.1f}" lengthAdjust="spacing">{escape(ring_txt)}</textPath>'
          f"</text></g>")
    d.text(cx, cy + 7, "No.1", "italb", 26, "accent", "middle")
    d.text(cx, cy + 23, "₹75,000", "caps", 7.5, "dim", "middle", ls=1.2)
    d.add("</g>")

    d.rule(L, 426, R, "hair2", 1, cls="draw", style="animation-delay:.7s")
    lede = "I build AI for the moments that can't afford a guess — retrieval that won't hallucinate, " \
           "risk engines that won't miss, and vision that runs where the internet doesn't."
    for i, line in enumerate(wrap(lede, "body", 15, 470)):
        d.text(L, 458 + i * 22, line, "body", 15, "dim", cls="rise", style=f"animation-delay:{.8 + i * .08:.2f}s")
    d.text(R, 458, "AI / ML ENGINEER", "caps", 11, "fg", "end", ls=2.4, cls="fade", style="animation-delay:1s")
    d.text(R, 480, "B.TECH COMPUTER ENGG. '27", "caps", 11, "dim", "end", ls=2.4, cls="fade",
           style="animation-delay:1.1s")
    d.text(R, 502, "Data → Model → API → Interface", "mono", 11, "accent", "end", cls="fade",
           style="animation-delay:1.2s")
    return d


def pill(theme, label):
    fw = FONTS["caps"].width(label, 10.5, 2.2)
    w = int(fw + 74)
    d = Svg(w, 44, theme, label)
    d.add(f'<rect x=".75" y=".75" width="{w - 1.5}" height="42.5" rx="21.25" fill="{d.c("bg")}" '
          f'stroke="{d.c("hair2")}" stroke-width="1.5"/>')
    d.add(f'<circle cx="24" cy="22" r="3.2" fill="{d.c("accent")}"/>')
    d.text(38, 26, label, "caps", 10.5, "fg", ls=2.2)
    d.text(w - 20, 27, "↗", "mono", 13, "accent", "end")
    return d


def section(theme, num, parts, caption):
    d = Svg(W, 118, theme, " ".join(p[0] for p in parts).strip())
    d.rule(0, 20, W, "fg", 2.2, cls="draw")
    d.rule(0, 26, W, "fg", .7, cls="draw", style="animation-delay:.08s")
    d.text(0, 92, f"§ {num}", "mono", 13, "accent", ls=1.5, cls="fade", style="animation-delay:.2s")
    d.runs(72, 96, [(t, f, 50, c) for t, f, c in parts], cls="rise", style="animation-delay:.1s")
    d.text(W, 92, caption, "mono", 10.5, "mute", "end", ls=2, cls="fade", style="animation-delay:.35s")
    return d


MANIFESTO = [
    ("I", "Retrieval that can't hallucinate.",
     "Dense + sparse search, cross-encoder rerank, hard whitelist guards. If it isn't in the corpus, it isn't in the answer."),
    ("II", "Risk engines that can't miss.",
     "A deterministic core makes the call; LLM agents only explain it. Replayed against real disasters, timed in microseconds."),
    ("III", "Vision where the signal dies.",
     "TFLite, MobileFaceNet and YOLOv8 running fully on-device — for sites with zero connectivity and no second chances."),
    ("IV", "Patches in the plumbing.",
     "Memory-safety fixes merged into libheif and assimp — C/C++ that ships inside browsers, games and image pipelines."),
]


def manifesto(theme):
    d = Svg(W, 262, theme, "What I build: " + " ".join(m[1] for m in MANIFESTO))
    col, gap = (W - 3 * 28) / 4, 28
    for i, (num, head, body) in enumerate(MANIFESTO):
        x = i * (col + gap)
        dl = f"animation-delay:{.1 + i * .12:.2f}s"
        d.add(f'<g class="rise" style="{dl}">')
        d.text(x, 46, num, "italb", 34, "accent")
        d.rule(x, 64, x + col, "hair2", 1)
        for j, line in enumerate(wrap(head, "disp", 21, col)):
            d.text(x, 96 + j * 25, line, "disp", 21, "fg", ls=-.2)
        top = 96 + len(wrap(head, "disp", 21, col)) * 25 + 8
        for j, line in enumerate(wrap(body, "body", 13, col)):
            d.text(x, top + j * 20, line, "body", 13, "dim")
        d.add("</g>")
    return d


WORKS = {
    "trinetra": dict(n="01", name="trinetra", tag="INDUSTRIAL SAFETY · RISK ENGINE",
                     body="Fuses gas sensors, hot-work permits and CCTV into one deterministic risk score. "
                          "LangGraph agents explain the call — they never make it.",
                     metric="~50µs", label="P50 DECISION", sub="100% recall · 240 unseen scenarios",
                     stack="Python · FastAPI · LangGraph · NetworkX · YOLOv8"),
    "compass": dict(n="02", name="BIS-COMPASS", tag="HYBRID RAG · STANDARDS SEARCH",
                    body="Plain English in, Indian Standards codes out. FAISS + BM25, rank fusion, "
                         "cross-encoder rerank — and a whitelist guard so it can't invent a standard.",
                    metric="100%", label="HIT@3", sub="0.93 MRR@5 · fully offline",
                    stack="FAISS · bge-m3 · BM25 · cross-encoder · FastAPI"),
    "faceid": dict(n="03", name="Offline Face ID", tag="EDGE VISION · NHAI HACKATHON",
                   body="Face recognition and liveness detection that runs entirely on the phone, "
                        "for remote sites with zero connectivity. Syncs when a signal returns.",
                   metric="98.3%", label="LFW ACCURACY", sub="~13 ms per inference, on-device",
                   stack="React Native · TFLite · MobileFaceNet"),
    "crackwatch": dict(n="04", name="CrackWatch", tag="CIVIC INFRASTRUCTURE · WINNER",
                       body="An AI command center that spots structural damage in imagery and triages it "
                            "like an ops platform. Since rebuilt AI-native on the Lemma SDK.",
                       metric="₹75K", label="FIRST PRIZE", sub="NIRMAN 2026 hackathon",
                       stack="Vision AI · JavaScript · Lemma SDK", award=True),
    "orca": dict(n="05", name="ORCA", tag="MARINE AI · SMART INDIA HACKATHON",
                 body="Ten cooperating agents turn ocean data — chlorophyll, sea temperature, thermal "
                      "fronts, sea state — into one safe, explainable call for fishers.",
                 metric="10", label="AGENTS", sub="ISRO problem SIH26176",
                 stack="TypeScript · FastAPI · multi-agent reasoning"),
    "floodlight": dict(n="06", name="Floodlight", tag="URBAN FLOODS · MUSA CODEX 2026",
                       body="A ward-level flood nervous system: every street warned, every drain "
                            "diagnosed, with a ₹2k ESP32 level sensor feeding the live map.",
                       metric="32", label="CITIES ON WATCH", sub="live storm feed · 35 tests green",
                       stack="JavaScript · ESP32 · live weather"),
}


def star(r, points=5, inner=.42):
    pts = []
    for k in range(points * 2):
        rr = r if k % 2 == 0 else r * inner
        a = math.pi * k / points - math.pi / 2
        pts.append(f"{rr * math.cos(a):.2f},{rr * math.sin(a):.2f}")
    return "M" + " L".join(pts) + "Z"


def card(theme, key):
    w = WORKS[key]
    CW, CH = 440, 330
    d = Svg(CW, CH, theme, f"{w['name']} — {w['body']}")
    d.frame(fill="card", grain=True)
    d.add(f'<rect x=".5" y=".5" width="{CW - 1}" height="{CH - 1}" fill="none" stroke="{d.c("hair2")}"/>')
    P = 28
    d.text(P, 44, w["n"], "mono", 12, "accent", ls=1)
    d.text(CW - (84 if w.get("award") else P), 44, w["tag"], "mono", 9.5, "mute", "end", ls=1.6)
    d.rule(P, 58, CW - P, "hair2", 1, cls="draw", style="animation-delay:.2s")

    size = 40
    while FONTS["disp"].width(w["name"], size, -.6) > CW - 2 * P - 30:
        size -= 1
    d.text(P - 1, 106, w["name"], "disp", size, "fg", ls=-.6, cls="rise", style="animation-delay:.1s")
    d.text(CW - P, 104, "↗", "mono", 20, "accent", "end", cls="fade", style="animation-delay:.5s")
    for i, line in enumerate(wrap(w["body"], "body", 13.5, CW - 2 * P)[:3]):
        d.text(P, 138 + i * 21, line, "body", 13.5, "dim", cls="rise", style=f"animation-delay:{.2 + i * .06:.2f}s")

    d.rule(P, 222, CW - P, "hair", 1)
    mw = d.text(P - 1, 282, w["metric"], "italb", 54, "accent", cls="rise", style="animation-delay:.45s")
    mx = P + mw + 16
    d.text(mx, 258, w["label"], "caps", 10, "fg", ls=2, cls="fade", style="animation-delay:.6s")
    d.text(mx, 278, w["sub"], "body", 12.5, "dim", cls="fade", style="animation-delay:.65s")
    d.text(P, 312, w["stack"], "mono", 10, "mute", cls="fade", style="animation-delay:.7s")
    if w.get("award"):
        d.add(f'<g class="fade" style="animation-delay:.8s">'
              f'<polygon points="{CW - 74},0 {CW - 38},0 {CW - 38},46 {CW - 56},36 {CW - 74},46" '
              f'fill="{d.c("accent")}"/></g>')
        d.add(f'<path class="fade" style="animation-delay:.8s" transform="translate({CW - 56},20)" '
              f'd="{star(7.5)}" fill="{d.c("bg")}"/>')
    return d


UPSTREAM = [
    ("strukturag/libheif", "1840", "MERGED", "HEIF image decoder",
     "Enforces security limits on icef unit allocation — no unbounded memory from a crafted HEIF file."),
    ("assimp/assimp", "6705", "MERGED", "3D asset importer",
     "Validates B3D chunk sizes against the buffer and parent chunk — stops oversized allocations from malformed models."),
    ("AOMediaCodec/libavif", "3272", "IN REVIEW", "AV1 image format",
     "Adopts the __counted_by bounds-safety model on core data buffers, so overruns trap instead of leak."),
]


def upstream(theme, i):
    repo, pr, status, kind, body = UPSTREAM[i]
    d = Svg(W, 128, theme, f"{repo} #{pr} ({status.lower()}): {body}")
    d.rule(0, 1, W, "hair2", 1)
    # rubber stamp
    merged = status == "MERGED"
    col = "accent" if merged else "mute"
    sw = FONTS["caps"].width(status, 11, 2.4) + 28
    d.css.append(f".stamp{{transform-box:fill-box;transform-origin:center;"
                 f"animation:slam .55s cubic-bezier(.3,1.6,.5,1) both}}"
                 f"@keyframes slam{{from{{opacity:0;transform:rotate(-8deg) scale(1.9)}}"
                 f"to{{opacity:1;transform:rotate(-8deg) scale(1)}}}}")
    d.add(f'<g class="stamp" style="animation-delay:{.3 + i * .15:.2f}s">'
          f'<rect x="4" y="44" width="{sw:.0f}" height="34" rx="3" fill="none" stroke="{d.c(col)}" stroke-width="2"/>'
          f'<rect x="8" y="48" width="{sw - 8:.0f}" height="26" rx="2" fill="none" stroke="{d.c(col)}" stroke-width=".8"/>')
    d.text(4 + sw / 2, 66, status, "caps", 11, col, "middle", ls=2.4)
    d.add("</g>")
    X = 190
    nw = d.runs(X, 60, [(repo, "disp", 26, "fg"), ("  #" + pr, "italb", 26, "accent")], cls="rise")
    d.text(W, 58, kind.upper(), "mono", 9.5, "mute", "end", ls=1.6, cls="fade")
    for j, line in enumerate(wrap(body, "body", 14, W - X - 40)):
        d.text(X, 90 + j * 21, line, "body", 14, "dim", cls="fade", style="animation-delay:.2s")
    d.text(W, 92, "↗", "mono", 18, "accent", "end")
    return d


CIRCUIT = ["NIRMAN 2026 — Winner", "Smart India Hackathon 2026", "MUJ HackX 4.0", "SerpApi India Hackathon",
           "MUSA CodeX 2026", "SBI Hackathon @ GFF", "NABARD Hackathon @ GFF", "SEBI TechSprint @ GFF",
           "IDBI Innovate 2026", "Qwen Cloud Hackathon", "Slack Agent Builder", "FlowZint AI Hackathon",
           "Gappy AI Hackathon", "NHAI Hackathon 2025", "Tech Sagar FinTech"]


def circuit(theme):
    d = Svg(W, 96, theme, "Hackathons: " + ", ".join(CIRCUIT))
    d.defs.append(f'<linearGradient id="fadeL"><stop offset="0" stop-color="{d.c("bg")}"/>'
                  f'<stop offset="1" stop-color="{d.c("bg")}" stop-opacity="0"/></linearGradient>')
    d.defs.append(f'<linearGradient id="fadeR"><stop offset="0" stop-color="{d.c("bg")}" stop-opacity="0"/>'
                  f'<stop offset="1" stop-color="{d.c("bg")}"/></linearGradient>')
    d.frame(grain=True)
    d.rule(0, .5, W, "hair2", 1)
    d.rule(0, 95.5, W, "hair2", 1)
    SEP = 22
    x, items = 0.0, []
    for name in CIRCUIT:
        first = name.startswith("NIRMAN")
        items.append((x, name, first))
        x += FONTS["italb" if first else "ital"].width(name, 30) + SEP * 2 + 12
    loop = x
    d.css.append(f".track{{animation:marquee 60s linear infinite}}"
                 f"@keyframes marquee{{to{{transform:translateX(-{loop:.1f}px)}}}}")
    d.add('<g class="track">')
    for rep in (0, loop):
        for ix, name, first in items:
            d.text(rep + ix, 59, name, "italb" if first else "ital", 30, "accent" if first else "fg")
            d.add(f'<circle cx="{rep + ix + FONTS["italb" if first else "ital"].width(name, 30) + SEP + 6:.1f}" '
                  f'cy="49" r="3.4" fill="{d.c("accent")}"/>')
    d.add("</g>")
    d.add(f'<rect x="0" y="1" width="90" height="94" fill="url(#fadeL)"/>')
    d.add(f'<rect x="{W - 90}" y="1" width="90" height="94" fill="url(#fadeR)"/>')
    return d


TOOLKIT = [
    ("Intelligence", ["PyTorch", "TensorFlow Lite", "Hugging Face", "FAISS · BM25 · rerankers",
                      "LangGraph agents", "OpenCV · YOLOv8", "Gemini · Groq · Whisper"]),
    ("Systems", ["Python", "C / C++", "FastAPI", "Node.js · Express", "Supabase · Postgres",
                 "Firebase", "GitHub Actions"]),
    ("Interface", ["TypeScript", "React · Next.js", "Tailwind CSS", "Framer Motion", "Three.js",
                   "React Native · Expo", "Flutter · Dart"]),
]


def toolkit(theme):
    d = Svg(W, 300, theme, "Toolkit — " + "; ".join(f"{h}: {', '.join(xs)}" for h, xs in TOOLKIT))
    col, gap = (W - 2 * 40) / 3, 40
    for i, (head, items) in enumerate(TOOLKIT):
        x = i * (col + gap)
        d.add(f'<g class="rise" style="animation-delay:{.1 + i * .12:.2f}s">')
        d.text(x, 22, head.upper(), "caps", 10.5, "accent", ls=2.6)
        d.rule(x, 36, x + col, "fg", 1.4)
        for j, item in enumerate(items):
            y = 70 + j * 34
            d.text(x, y, item, "ital", 20, "fg")
            d.text(x + col, y, f"{j + 1:02d}", "mono", 9.5, "mute", "end")
            d.rule(x, y + 12, x + col, "hair", 1)
        d.add("</g>")
    return d


def footer(theme):
    d = Svg(W, 330, theme, "Got a problem that can't afford a guess? Write to satopaysaud@gmail.com")
    d.frame(inset=16)
    L, R = 58, W - 58
    d.text(W / 2, 70, "FIN · OPEN TO AI / ML ROLES & COLLABORATIONS", "mono", 10.5, "dim", "middle", ls=2.2,
           cls="fade")
    d.runs(W / 2, 148, [("Got a problem that ", "ital", 46, "fg"), ("can't", "disp", 46, "fg")], "middle",
           cls="rise", style="animation-delay:.1s")
    d.runs(W / 2, 204, [("afford a ", "ital", 46, "fg"), ("guess", "disp", 46, "fg"), ("?", "italb", 46, "accent")],
           "middle", cls="rise", style="animation-delay:.22s")
    ew = FONTS["italb"].width("satopaysaud@gmail.com", 24)
    d.text(W / 2, 256, "satopaysaud@gmail.com", "italb", 24, "accent", "middle", cls="fade",
           style="animation-delay:.5s")
    d.rule(W / 2 - ew / 2, 266, W / 2 + ew / 2, "accent", 1.2, cls="draw", style="animation-delay:.8s")
    d.text(L, 294, "SET IN FRAUNCES, ARCHIVO & JETBRAINS MONO", "mono", 9, "mute", ls=1.8)
    d.text(R, 294, "HAND-BUILT SVG · ZERO WIDGETS", "mono", 9, "mute", "end", ls=1.8)
    return d


# ================================================================ live stats
QUERY = """query($login:String!){user(login:$login){
  repositories(ownerAffiliations:OWNER,privacy:PUBLIC,isFork:false){totalCount}
  contributionsCollection{totalCommitContributions contributionCalendar{totalContributions
    weeks{contributionDays{date contributionCount}}}}}}"""


def fetch_stats(login):
    token = os.environ.get("GITHUB_TOKEN") or subprocess.run(
        ["gh", "auth", "token"], capture_output=True, text=True).stdout.strip()
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": login}}).encode(),
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json"})
    u = json.load(urllib.request.urlopen(req))["data"]["user"]
    cal = u["contributionsCollection"]["contributionCalendar"]
    days = [dd for wk in cal["weeks"] for dd in wk["contributionDays"]]
    best, run = 0, 0
    for dd in days:
        run = run + 1 if dd["contributionCount"] else 0
        best = max(best, run)
    active = sum(1 for dd in days if dd["contributionCount"])
    return dict(total=cal["totalContributions"], active=active, repos=u["repositories"]["totalCount"],
                commits=u["contributionsCollection"]["totalCommitContributions"], best=best,
                days=[(dd["date"], dd["contributionCount"]) for dd in days],
                weeks=[(wk["contributionDays"][0]["date"], sum(x["contributionCount"] for x in wk["contributionDays"]))
                       for wk in cal["weeks"]])


def stats(theme, data):
    d = Svg(W, 330, theme, f"{data['total']} contributions in the last year, {data['repos']} public repositories, "
                           f"{data['commits']} commits, {data['active']} active days")
    figs = [(f"{data['total']:,}", "CONTRIBUTIONS", "last twelve months"),
            (f"{data['commits']:,}", "COMMITS", "pushed in the same window"),
            (str(data["repos"]), "REPOSITORIES", "public, original work"),
            (str(data["active"]), "DAYS SHIPPING", f"longest run: {data['best']} days")]
    col = W / 4
    for i, (num, lab, sub) in enumerate(figs):
        x = i * col
        dl = f"animation-delay:{.1 + i * .1:.2f}s"
        if i:
            d.add(f'<line x1="{x - 1}" y1="8" x2="{x - 1}" y2="118" stroke="{d.c("hair2")}"/>')
        xx = x + (22 if i else 0)
        d.text(xx, 76, num, "disp", 60, "accent" if i == 0 else "fg", ls=-1.5, cls="rise", style=dl)
        d.text(xx, 100, lab, "caps", 9.5, "fg", ls=2, cls="fade", style=dl)
        d.text(xx, 118, sub, "body", 12, "mute", cls="fade", style=dl)

    # 52-week ledger
    weeks = data["weeks"][-53:]
    top, base = 158, 290
    peak = max(c for _, c in weeks) or 1
    step = W / len(weeks)
    bw = step * .62
    d.rule(0, base + .5, W, "hair2", 1)
    last_month = None
    for i, (date, count) in enumerate(weeks):
        x = i * step + (step - bw) / 2
        h = max(2.0, (base - top) * count / peak)
        fill = "accent" if count == peak else ("fg" if count else "hair2")
        op = 1 if count == peak else (.25 + .75 * count / peak if count else 1)
        d.add(f'<rect class="grow" style="animation-delay:{.3 + i * .015:.3f}s" x="{x:.1f}" y="{base - h:.1f}" '
              f'width="{bw:.1f}" height="{h:.1f}" fill="{d.c(fill)}" opacity="{op:.2f}"/>')
        m = date[:7]
        if m != last_month and i > 0 and i < len(weeks) - 2:
            mon = dt.date.fromisoformat(date).strftime("%b").upper()
            d.text(i * step, base + 22, mon, "mono", 9, "mute", ls=1)
        last_month = m
    pi = max(range(len(weeks)), key=lambda k: weeks[k][1])
    px = pi * step + step / 2
    ph = (base - top)
    d.text(min(max(px, 60), W - 60), base - ph - 10, f"peak week · {peak}", "mono", 9.5, "accent", "middle",
           cls="fade", style="animation-delay:1.3s")
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%d %b %Y").upper()
    d.text(W, base + 36, f"WEEKLY CONTRIBUTIONS · UPDATED DAILY · {stamp}", "mono", 9, "mute", "end", ls=1.4)
    return d


def vinyl(theme, data):
    """The year in commits, pressed to vinyl: one groove-dot per day, outermost = oldest."""
    days = data["days"][-364:]
    total = sum(c for _, c in days)
    d = Svg(W, 560, theme, f"The year in commits, pressed to vinyl: {total} contributions across "
                           f"{len(days)} days, one groove per day")
    V = THEMES["dark"]  # the record itself is always black shellac
    cx, cy, R = 272, 280, 250
    r_out, r_in, turns = 236, 112, 6.21

    d.defs.append('<radialGradient id="shellac" cx=".5" cy=".5" r=".5">'
                  '<stop offset=".40" stop-color="#15120e"/><stop offset=".97" stop-color="#0b0a08"/>'
                  '<stop offset="1" stop-color="#1e1a14"/></radialGradient>')
    d.defs.append('<linearGradient id="gleam" x1="0" y1="0" x2="1" y2="1">'
                  '<stop offset="0" stop-color="#fff" stop-opacity="0"/>'
                  '<stop offset=".5" stop-color="#fff" stop-opacity=".16"/>'
                  '<stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>')
    d.defs.append(f'<radialGradient id="halo" cx="{cx}" cy="{cy}" r="{R + 40}" gradientUnits="userSpaceOnUse">'
                  f'<stop offset=".82" stop-color="{d.c("accent")}" stop-opacity=".22"/>'
                  f'<stop offset="1" stop-color="{d.c("accent")}" stop-opacity="0"/></radialGradient>')
    d.css.append(f".disc{{transform-origin:{cx}px {cy}px;animation:turn 14s linear infinite}}"
                 f"@keyframes turn{{to{{transform:rotate(360deg)}}}}"
                 f".arm{{transform-origin:{cx + 232}px {cy - 218}px;animation:drop 2.4s {EASE} .4s both}}"
                 f"@keyframes drop{{from{{transform:rotate(-24deg)}}to{{transform:none}}}}"
                 f".glow{{animation:pulse 3.2s ease-in-out infinite}}"
                 f"@keyframes pulse{{50%{{opacity:.35}}}}")

    d.add(f'<circle cx="{cx}" cy="{cy}" r="{R + 40}" fill="url(#halo)" class="fade"/>')
    d.add(f'<g class="disc"><circle cx="{cx}" cy="{cy}" r="{R}" fill="url(#shellac)"/>')
    for gr in range(118, 246, 4):  # fine pressed grooves
        d.add(f'<circle cx="{cx}" cy="{cy}" r="{gr}" fill="none" stroke="#fff" stroke-opacity=".05" stroke-width=".6"/>')

    peak = max(c for _, c in days) or 1
    n = len(days)
    pts = []
    for i, (date, count) in enumerate(days):
        f = i / (n - 1)
        rad = r_out - (r_out - r_in) * f
        a = -math.pi / 2 + 2 * math.pi * turns * f
        x, y = cx + rad * math.cos(a), cy + rad * math.sin(a)
        pts.append((x, y))
        if count:
            k = (count / peak) ** .5
            col = V["accent"] if count == peak or k > .8 else (V["gilt"] if k > .35 else V["fg"])
            d.add(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{1.7 + 4.2 * k:.2f}" fill="{col}" '
                  f'opacity="{.55 + .45 * k:.2f}"/>')
        else:
            d.add(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="1" fill="#fff" opacity=".2"/>')
    d.add(f'<path d="M{"L".join(f"{x:.1f} {y:.1f}" for x, y in pts)}" fill="none" stroke="#fff" '
          f'stroke-opacity=".07" stroke-width=".7"/>')

    # centre label
    lr = 96
    d.add(f'<circle cx="{cx}" cy="{cy}" r="{lr}" fill="{V["accent"]}"/>')
    d.add(f'<circle cx="{cx}" cy="{cy}" r="{lr - 6}" fill="none" stroke="#100e0a" stroke-opacity=".35" stroke-width=".8"/>')
    d.defs.append(f'<path id="lbl" d="M {cx} {cy} m -{lr - 18} 0 a {lr - 18} {lr - 18} 0 1 1 {2 * (lr - 18)} 0 '
                  f'a {lr - 18} {lr - 18} 0 1 1 -{2 * (lr - 18)} 0"/>')
    ring = "SAUD SATOPAY RECORDS · PRESSED DAILY FROM THE GITHUB API · SIDE A · "
    d.used.setdefault("caps", set()).update(ring)
    d.add(f'<text font-family="caps" font-size="7.4" fill="#100e0a" letter-spacing="1">'
          f'<textPath href="#lbl" textLength="{2 * math.pi * (lr - 18):.1f}" lengthAdjust="spacing">'
          f'{escape(ring)}</textPath></text>')
    d.text(cx, cy - 12, "The Year", "ital", 22, "#100e0a", "middle")
    d.text(cx, cy + 12, "in Commits", "italb", 22, "#100e0a", "middle")
    d.text(cx, cy + 32, f"{total:,} · 33⅓".replace("⅓", "1/3"), "mono", 8.5, "#100e0a", "middle", ls=1)
    d.add(f'<circle cx="{cx}" cy="{cy}" r="5" fill="{d.c("bg") if theme == "dark" else "#f1e6cd"}"/>')
    d.add("</g>")
    # static light across the spinning disc sells the rotation
    d.add(f'<path d="M{cx} {cy} L{cx - R * .35:.1f} {cy - R * .94:.1f} A{R} {R} 0 0 1 {cx + R * .35:.1f} '
          f'{cy - R * .94:.1f}Z" fill="url(#gleam)" opacity=".6"/>')
    d.add(f'<path d="M{cx} {cy} L{cx + R * .35:.1f} {cy + R * .94:.1f} A{R} {R} 0 0 1 {cx - R * .35:.1f} '
          f'{cy + R * .94:.1f}Z" fill="url(#gleam)" opacity=".35"/>')

    # tonearm, resting on today's groove
    px, py = cx + 232, cy - 218
    nx, ny = pts[-1]
    metal = "#d9cfb8" if theme == "dark" else "#3b3326"
    d.add(f'<circle cx="{px}" cy="{py}" r="22" fill="none" stroke="{metal}" stroke-opacity=".5" stroke-width="1"/>')
    d.add(f'<circle cx="{px}" cy="{py}" r="13" fill="{metal}" opacity=".85"/>')
    d.add(f'<g class="arm">')
    ang = math.atan2(ny - py, nx - px)
    ln = math.hypot(nx - px, ny - py)
    bx, by = px + (ln - 34) * math.cos(ang), py + (ln - 34) * math.sin(ang)
    back = (px - 34 * math.cos(ang), py - 34 * math.sin(ang))
    d.add(f'<line x1="{back[0]:.1f}" y1="{back[1]:.1f}" x2="{bx:.1f}" y2="{by:.1f}" stroke="{metal}" '
          f'stroke-width="5" stroke-linecap="round"/>')
    d.add(f'<circle cx="{back[0]:.1f}" cy="{back[1]:.1f}" r="11" fill="{metal}"/>')
    deg = math.degrees(ang)
    d.add(f'<g transform="translate({bx:.1f} {by:.1f}) rotate({deg + 18:.1f})">'
          f'<rect x="-4" y="-9" width="40" height="18" rx="3" fill="{metal}"/>'
          f'<rect x="30" y="-4" width="8" height="8" fill="{V["accent"]}"/></g>')
    d.add("</g>")
    d.add(f'<circle class="glow" cx="{nx:.1f}" cy="{ny:.1f}" r="6" fill="{V["accent"]}" opacity=".9"/>')

    # the sleeve: tracklist
    X, XR = 580, W
    d.text(X, 58, "NOW PLAYING", "caps", 10, "accent", ls=2.6, cls="fade")
    d.text(X, 104, "Side A", "ital", 44, "fg", cls="rise")
    d.text(X, 134, "The year in commits", "disp", 20, "fg", cls="rise", style="animation-delay:.1s")
    d.rule(X, 154, XR, "fg", 1.4)
    months = {}
    for date, count in days:
        months[date[:7]] = months.get(date[:7], 0) + count
    items = list(months.items())[-12:]
    top = max(c for _, c in items)
    for i, (ym, count) in enumerate(items):
        y = 184 + i * 27
        name = dt.date.fromisoformat(ym + "-01").strftime("%B %Y")
        hot = count == top
        dl = f"animation-delay:{.2 + i * .05:.2f}s"
        d.add(f'<g class="fade" style="{dl}">')
        d.text(X, y, f"{i + 1:02d}", "mono", 9.5, "accent" if hot else "mute")
        nw = d.text(X + 28, y, name, "italb" if hot else "ital", 16, "accent" if hot else "fg")
        num = f"{count}"
        numw = FONTS["mono"].width(num, 10.5)
        d.add(f'<line x1="{X + 34 + nw:.1f}" y1="{y - 3}" x2="{XR - numw - 8:.1f}" y2="{y - 3}" '
              f'stroke="{d.c("hair2")}" stroke-dasharray="1 4"/>')
        d.text(XR, y, num, "mono", 10.5, "accent" if hot else "dim", "end")
        d.add("</g>")
    yb = 184 + 12 * 27 + 4
    d.rule(X, yb - 14, XR, "hair2", 1)
    d.text(X, yb + 8, "Every groove is a day; every glint, a commit.", "ital", 13.5, "dim")
    d.text(X, yb + 28, "The needle sits on today.", "ital", 13.5, "dim")
    return d


# ================================================================ main
def build_static():
    for f in os.listdir(OUT):
        if f.endswith(".svg"):
            os.remove(os.path.join(OUT, f))
    save("hero", hero)
    for label, slug in [("PORTFOLIO", "portfolio"), ("RÉSUMÉ", "resume"), ("LINKEDIN", "linkedin"),
                        ("EMAIL", "email")]:
        save(f"pill-{slug}", lambda t, label=label: pill(t, label))
    sections = {
        "brief": ("I", [("The ", "ital", "fg"), ("brief", "disp", "fg")], "WHAT I BUILD, AND WHY"),
        "works": ("II", [("Selected ", "ital", "fg"), ("works", "disp", "fg")], "SIX SYSTEMS · SHIPPED & MEASURED"),
        "upstream": ("III", [("Up", "disp", "fg"), ("stream", "ital", "fg")], "SECURITY PATCHES IN C / C++"),
        "circuit": ("IV", [("The ", "ital", "fg"), ("circuit", "disp", "fg")], "15 HACKATHONS · 2025 — 26"),
        "toolkit": ("V", [("The ", "ital", "fg"), ("toolkit", "disp", "fg")], "WHAT'S ON THE BENCH"),
        "numbers": ("VI", [("By the ", "ital", "fg"), ("numbers", "disp", "fg")], "LIVE FROM THE GITHUB API"),
        "record": ("VII", [("On ", "ital", "fg"), ("record", "disp", "fg")], "THE YEAR IN COMMITS · PRESSED DAILY"),
    }
    for slug, (num, parts, cap) in sections.items():
        save(f"sec-{slug}", lambda t, a=num, b=parts, c=cap: section(t, a, b, c))
    save("manifesto", manifesto)
    for key in WORKS:
        save(f"work-{key}", lambda t, k=key: card(t, k))
    for i in range(len(UPSTREAM)):
        save(f"upstream-{i + 1}", lambda t, i=i: upstream(t, i))
    save("circuit", circuit)
    save("toolkit", toolkit)
    save("footer", footer)


if __name__ == "__main__":
    if "--stats" in sys.argv:
        out = sys.argv[sys.argv.index("--stats") + 1]
        os.makedirs(out, exist_ok=True)
        data = fetch_stats(os.environ.get("PROFILE_LOGIN", "SaudSatopay"))
        save("stats", lambda t: stats(t, data), out)
        save("vinyl", lambda t: vinyl(t, data), out)
    else:
        build_static()
