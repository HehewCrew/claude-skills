"""Text (+ an optional outline heart and a corner monogram) laid out for a printed plate.

Writes OUT.svg (outlined text, filled shapes only: slicers ignore SVG strokes),
OUT-preview.png (the plate and its hole drawn as a guide, not in the SVG) and, with
--grow, OUT-thick.svg + OUT-thick-preview.png. Units are mm.

    python build_plate.py --font GochiHand-Regular.ttf --text "Happy birthday, Sam" \
        --heart --mono S --plate 60 18 --hole-zone 10 --track 0.045 --out out/tag

Needs: uharfbuzz fonttools shapely pillow numpy. Install them into a scratch folder
(pip install --target lib ...) and run with --lib lib, rather than into a project venv.
"""

import argparse
import sys

ap = argparse.ArgumentParser()
ap.add_argument("--font", required=True)
ap.add_argument("--text", required=True)
ap.add_argument("--mono", default="", help="a monogram in the bottom-right corner")
ap.add_argument("--heart", action="store_true", help="an outline heart after the text, same line")
ap.add_argument("--plate", nargs=2, type=float, default=[60, 18], metavar=("W", "H"))
ap.add_argument("--hole-zone", type=float, default=10.0, help="left strip kept clear for the ring hole")
ap.add_argument("--margin", type=float, default=1.6)
ap.add_argument("--track", type=float, default=0.0, help="extra letter spacing, fraction of the em")
ap.add_argument("--max-cap", type=float, default=6.0, help="largest cap height to try, mm")
ap.add_argument("--base", type=float, default=None, help="baseline of the line, mm from the top")
ap.add_argument("--heart-stroke", type=float, default=0.8, help="the heart's outline, mm (2 x a 0.4 nozzle)")
ap.add_argument("--grow", type=float, default=0.0, help="also write a copy with every letter grown by this, mm")
ap.add_argument("--lib", default=None, help="folder the dependencies were pip-installed into")
ap.add_argument("--out", required=True)
a = ap.parse_args()
if a.lib:
    sys.path.insert(0, a.lib)

import numpy as np  # noqa: E402
import uharfbuzz as hb  # noqa: E402
from fontTools.pens.basePen import BasePen  # noqa: E402
from fontTools.pens.svgPathPen import SVGPathPen  # noqa: E402
from fontTools.pens.transformPen import TransformPen  # noqa: E402
from fontTools.ttLib import TTFont  # noqa: E402
from PIL import Image, ImageDraw  # noqa: E402
from shapely import affinity  # noqa: E402
from shapely.geometry import LineString, Polygon  # noqa: E402
from shapely.ops import unary_union  # noqa: E402

W, H = a.plate
tt = TTFont(a.font); gs = tt.getGlyphSet(); upem = tt["head"].unitsPerEm
hbfont = hb.Font(hb.Face(open(a.font, "rb").read())); order = tt.getGlyphOrder(); cmap = tt.getBestCmap()


def shape(text):
    buf = hb.Buffer(); buf.add_str(text); buf.guess_segment_properties()
    hb.shape(hbfont, buf, {"kern": True, "liga": True})
    out, x = [], 0
    for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
        out.append((order[info.codepoint], x + pos.x_offset)); x += pos.x_advance + a.track * upem
    return out, x - a.track * upem


class Flat(BasePen):
    """Flattens outlines to polygons, for checks, previews and thickening."""
    def __init__(self, g): super().__init__(g); self.rings, self.cur = [], []
    def _moveTo(self, p): self.cur = [p]
    def _lineTo(self, p): self.cur.append(p)
    def _curveToOne(self, b, c, d):
        p0 = self.cur[-1]
        for i in range(1, 13):
            t = i / 12; u = 1 - t
            self.cur.append(tuple(u**3*p+3*u*u*t*q+3*u*t*t*r+t**3*s for p, q, r, s in zip(p0, b, c, d)))
    def _qCurveToOne(self, b, c):
        p0 = self.cur[-1]
        for i in range(1, 9):
            t = i / 8; u = 1 - t
            self.cur.append(tuple(u*u*p+2*u*t*q+t*t*r for p, q, r in zip(p0, b, c)))
    def _closePath(self):
        if len(self.cur) > 2: self.rings.append(self.cur)
        self.cur = []
    _endPath = _closePath


def glyph_shape(rings):
    """Contours to one shape, counters cut out (even-odd: holes in o, e, a survive)."""
    cur = None
    for r in rings:
        p = Polygon(r).buffer(0)
        cur = p if cur is None else cur.symmetric_difference(p)
    return cur


def bounds(name):
    p = Flat(gs); gs[name].draw(p)
    xs = [x for r in p.rings for x, _ in r]; ys = [y for r in p.rings for _, y in r]
    return min(xs), min(ys), max(xs), max(ys)


def stroke_ratio():
    """Real stroke width / cap height, as 2 x area / perimeter over plain letters.
    Never the bounding box of 'l': a slanted l reads twice too wide."""
    ws = []
    for ch in "lrivn":
        if ord(ch) not in cmap: continue
        p = Flat(gs); gs[cmap[ord(ch)]].draw(p)
        g = glyph_shape(p.rings)
        if g and g.length: ws.append(2 * g.area / g.length)
    cap = bounds(cmap[ord("H")] if ord("H") in cmap else cmap[ord(a.text[0])])[3]
    return (sum(ws) / len(ws)) / cap


def place(glyphs, s, x0, base):
    d, rings = [], []
    for name, gx in glyphs:
        m = (s, 0, 0, -s, x0 + gx * s, base)
        sp = SVGPathPen(gs); gs[name].draw(TransformPen(sp, m)); d.append(sp.getCommands())
        fp = Flat(gs); gs[name].draw(TransformPen(fp, m)); rings += fp.rings
    return " ".join(x for x in d if x), rings


def heart_ring(h, stroke):
    """A hand-stamped outline heart (lopsided lobes, a 10 degree tilt) as a FILLED ring."""
    def cub(p0, p1, p2, p3, n=60):
        return [tuple((1-t)**3*p+3*(1-t)**2*t*q+3*(1-t)*t**2*r+t**3*e for p, q, r, e in zip(p0, p1, p2, p3))
                for t in [i/n for i in range(n+1)]]
    segs = [((49, 27), (40, 8), (9, 11), (10, 37)), ((10, 37), (11, 58), (37, 71), (52, 91)),
            ((52, 91), (63, 73), (91, 60), (89, 35)), ((89, 35), (87, 10), (57, 9), (49, 27))]
    pts = []
    for sg in segs: pts += cub(*sg)[:-1]
    line = affinity.rotate(LineString(pts + [pts[0]]), -10, origin=(50, 50))
    x0, y0, _, y1 = line.bounds
    k = (h - stroke) / (y1 - y0)
    line = affinity.scale(affinity.translate(line, -x0, -y0), k, k, origin=(0, 0))
    return line.buffer(stroke / 2, join_style=1, cap_style=1, resolution=16).simplify(0.01)


def ring_d(poly):
    def one(c): c = list(c); return "M" + " L".join(f"{x:.3f},{y:.3f}" for x, y in c[:-1]) + " Z"
    return " ".join([one(poly.exterior.coords)] + [one(i.coords) for i in poly.interiors])


# --- fit the line (and the heart) between the hole zone and the right margin
g1, adv1 = shape(a.text)
cap_u = bounds(cmap[ord("H")] if ord("H") in cmap else g1[0][0])[3]
avail = W - a.hole_zone - a.margin
cap = a.max_cap
while True:
    s = cap / cap_u
    heart_h, gap = cap * 1.4, cap * 0.7
    hw = heart_ring(heart_h, a.heart_stroke).bounds[2] + gap if a.heart else 0
    if adv1 * s + hw <= avail or cap < 1: break
    cap -= 0.05
base = a.base if a.base is not None else (H / 2 + cap / 2 if not a.mono else H / 2)
d1, r1 = place(g1, s, a.hole_zone, base)
parts = [f'  <path id="text" fill="#000" d="{d1}"/>']
shapes = [glyph_shape(r1)]
heart = None
if a.heart:
    heart = affinity.translate(heart_ring(heart_h, a.heart_stroke), a.hole_zone + adv1 * s + gap, base - heart_h + 0.25)
    parts.append(f'  <path id="heart" fill="#000" fill-rule="evenodd" d="{ring_d(heart)}"/>')
rS = []
if a.mono:
    gS, _ = shape(a.mono)
    sS = cap * 0.9 / cap_u
    b = bounds(gS[0][0])
    dS, rS = place(gS, sS, W - a.margin - b[2] * sS, H - a.margin + b[1] * sS)
    parts.append(f'  <path id="monogram" fill="#000" d="{dS}"/>')

head = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W:g} {H:g}" width="{W:g}mm" height="{H:g}mm">\n'
open(a.out + ".svg", "w", encoding="utf-8").write(
    head + f"  <!-- {a.text} · laid out for a {W:g} x {H:g} mm plate, ring hole on the left -->\n"
    + "\n".join(parts) + "\n</svg>\n")

stroke = stroke_ratio() * cap
print(f"cap height {cap:.2f} mm · real stroke {stroke:.2f} mm"
      + (f" · heart {heart.bounds[2]-heart.bounds[0]:.2f} mm, outline {a.heart_stroke} mm" if heart else ""))
if stroke < 0.8:
    print(f"  ⚠ strokes under 0.8 mm (two 0.4-nozzle lines): print flush in a second colour, use a 0.2 nozzle, or --grow")


def preview(geoms, path):
    K, o = 20, 20
    im = Image.new("RGB", (int(W*K) + 2*o, int(H*K) + 2*o), "#2b2b2b"); dr = ImageDraw.Draw(im)
    dr.rounded_rectangle([o, o, o + W*K, o + H*K], radius=2.5*K, fill="#cfd1d4")
    dr.ellipse([o + 3*K, o + (H/2 - 2.5)*K, o + 8*K, o + (H/2 + 2.5)*K], fill="#2b2b2b")
    for g in geoms:
        for poly in getattr(g, "geoms", [g]):
            dr.polygon([(o + x*K, o + y*K) for x, y in poly.exterior.coords], fill="#1e1e1e")
            for i in poly.interiors: dr.polygon([(o + x*K, o + y*K) for x, y in i.coords], fill="#cfd1d4")
    im.save(path)


letters = [g for g in (glyph_shape(r1), glyph_shape(rS) if rS else None) if g]
preview(letters + ([heart] if heart else []), a.out + "-preview.png")

if a.grow:
    # Grow the letters only: the heart is already at its printable outline. Too much
    # growth closes counters (a 0.15 mm grow on a heavy font turned S into 8):
    # check the holes count and the preview.
    grown = unary_union([unary_union(letters).buffer(a.grow, join_style=1, resolution=8)] + ([heart] if heart else []))
    geoms = list(getattr(grown, "geoms", [grown]))
    before = sum(len(p.interiors) for g in letters + ([heart] if heart else []) for p in getattr(g, "geoms", [g]))
    after = sum(len(g.interiors) for g in geoms)
    open(a.out + "-thick.svg", "w", encoding="utf-8").write(
        head + f'  <!-- every letter grown by {a.grow} mm for raised printing -->\n'
        f'  <path fill="#000" fill-rule="evenodd" d="{" ".join(ring_d(g) for g in geoms)}"/>\n</svg>\n')
    preview(geoms, a.out + "-thick-preview.png")
    print(f"thick: stroke ~{stroke + 2*a.grow:.2f} mm · counters {before} → {after}"
          + ("  ⚠ some closed up: grow less" if after < before else ""))
