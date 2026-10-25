"""Worked example: a replacement light lens (a round, hollow, screwed-on lid).

Measured on the original: outer Ø250, side wall from Ø240 in to Ø200 and 32
high above a ~20 mm rim, total height 52, wall 2, screw holes Ø5 on a 230 mm
circle through 14 mm tab blocks. A low dome with a flat top. EST values were
read from photos.

Chain (run with the bambu-studio-ai venv):
    python revolved_lid.py                       -> lid.stl (as fitted)
    blender -b -P ../scripts/bevel.py -- lid.stl lid_round.stl
    python revolved_lid.py --finish lid_round.stl  -> lid_print.stl (flipped)
Pass U, flat or V instead of nothing to keep the original's centre groove.
"""
import math
import sys
from pathlib import Path

import manifold3d as m3d
import numpy as np
import trimesh

OUT = Path(__file__).with_name("lid.stl")
SEG = 360

WALL = 2.0
R_OUT = 125.0          # Ø250
RIM_H = 20.0           # the rounded rim lip (side photo)
R_WALL = 120.0         # side wall starts at Ø240...
R_TOP = 100.0          # ...and reaches the flat top at Ø200
TOP_Z = 52.0           # total height; rim 20 + side wall 32
R_GROOVE_OUT = 60.0    # round groove from Ø120...
R_GROOVE_IN = 30.0     # ...to Ø60, where the centre is back at full height
GROOVE_D = 12.0        # groove depth
GROOVE = sys.argv[1] if len(sys.argv) > 1 else "none"   # none, U, flat or V
# none: the groove was dropped so the printed face has no support marks;
# the original's U groove stays available.


def groove():
    """The groove's cross-section, from Ø120 in to Ø60."""
    if GROOVE == "none":
        return []
    mid = (R_GROOVE_OUT + R_GROOVE_IN) / 2
    half_w = (R_GROOVE_OUT - R_GROOVE_IN) / 2
    if GROOVE == "V":
        return [(R_GROOVE_OUT, TOP_Z), (mid, TOP_Z - GROOVE_D), (R_GROOVE_IN, TOP_Z)]
    if GROOVE == "flat":
        slope = 5.0
        return [(R_GROOVE_OUT, TOP_Z), (R_GROOVE_OUT - slope, TOP_Z - GROOVE_D),
                (R_GROOVE_IN + slope, TOP_Z - GROOVE_D), (R_GROOVE_IN, TOP_Z)]
    return [(mid + half_w * math.cos(t), TOP_Z - GROOVE_D * math.sin(t))
            for t in (math.pi * k / 24 for k in range(25))]


# Outer surface, (radius, height), from the edge inwards
PROFILE = [
    (R_OUT, RIM_H - (R_OUT - R_WALL)),  # the rim meets the wall at 45°, so it
    (R_WALL, RIM_H),                    # prints upside down without supports
    (R_TOP + 3.0, TOP_Z - 2.0),   # EST rounded shoulder
    (R_TOP, TOP_Z),
    *groove(),
    (0.0, TOP_Z),
]

# 8 panels pressed into the side wall (flat faces). Inside the 4 that carry
# a tab, a narrower notch cuts down through the rim to a solid block with the
# hole (from a photo of the original).
N_NOTCH = 8
PANEL_W = 50.0         # measured
PANEL_D = 5.0          # EST, how far the panel face is pressed in
PANEL_Z = RIM_H + 1.0  # the panel runs from just above the rim up through
                       # the top edge, notching it
TAB_W = 25.0           # measured
TAB_X = 107.0          # EST, inner face of the tab pocket
TAB_H = 14.0           # measured: the hole is ~14 mm up, in a thick block
TAB_LIFT = 2.0         # measured: the block's underside is 2 mm up from the bottom edge
HOLE_D = 5.0
HOLE_R = 230.0 / 2

# A ring rib under the flat top stiffens it now the groove is gone. At the groove's outer edge, so it lights as a faint ring;
# upside down on the plate it grows straight up, no supports.
RIB_R = R_GROOVE_OUT
RIB_T = 2.0
RIB_H = 8.0

ROUND_OUT = 4.0        # radius on the outside corners of the profile
ROUND_IN = 3.0         # radius on the inside corners


def outline():
    # Mirror the profile and extend it below the table so a 2D inward offset
    # gives an even wall everywhere except the open bottom.
    full = PROFILE + [(-r, z) for r, z in reversed(PROFILE)]
    cs = m3d.CrossSection([[(R_OUT, -20.0)] + full + [(-R_OUT, -20.0)]],
                          m3d.FillRule.Positive)
    # Round every corner of the profile: a part the public touches gets no
    # sharp edges. Opening rounds the outside corners,
    # closing the inside ones.
    rnd = m3d.JoinType.Round
    cs = cs.offset(-ROUND_OUT, rnd, 2.0, 64).offset(ROUND_OUT, rnd, 2.0, 64)
    return cs.offset(ROUND_IN, rnd, 2.0, 64).offset(-ROUND_IN, rnd, 2.0, 64)


def half():
    return m3d.CrossSection.square([R_OUT + 1, TOP_Z + 5])


def box(x0, x1, y0, y1, z0, z1):
    return m3d.Manifold.cube([x1 - x0, y1 - y0, z1 - z0]).translate([x0, y0, z0])


def slab(inset, z0, w, floor_drop=0.0):
    """Everything beyond a plane parallel to the side wall, set `inset` in,
    above a 45° floor starting at height z0, `w` wide: the panel cut (x-z
    section, extruded along y). The 45° floor prints upside down without
    supports; `floor_drop` lowers it, to keep the wall even under it."""
    k = (R_WALL - R_TOP) / (TOP_Z - RIM_H)

    def x_at(z):  # the side wall's straight line, Ø240 at the rim to Ø200 at the top
        return R_WALL - (z - RIM_H) * k - inset
    c = z0 - x_at(z0) - floor_drop          # the floor: z = x + c
    x0 = (R_WALL - (c - RIM_H) * k - inset) / (1 + k)
    z1 = TOP_Z + 5
    cs = m3d.CrossSection([[(x0, x0 + c), (R_OUT + 5, R_OUT + 5 + c), (R_OUT + 5, z1),
                            (x_at(z1), z1)]], m3d.FillRule.Positive)
    return m3d.Manifold.extrude(cs, w).rotate([90, 0, 0]).translate([0, w / 2, 0])


def build():
    solid = m3d.Manifold.revolve(outline() ^ half(), SEG)
    cavity = m3d.Manifold.revolve(outline().offset(-WALL, m3d.JoinType.Miter) ^ half(), SEG)
    for i in range(N_NOTCH):
        a = 360.0 * i / N_NOTCH + 22.5
        # pressed panel: the outside is cut flat, the cavity follows 2 mm in
        w = PANEL_W / 2
        cuts = [slab(PANEL_D, PANEL_Z, 2 * w)]
        inners = [slab(PANEL_D + WALL, PANEL_Z, 2 * w + 2 * WALL, WALL * math.sqrt(2))]
        if i % 2 == 0:
            # tab: open above the block, solid block below, walls round the pocket
            w = TAB_W / 2
            cuts.append(box(TAB_X, R_OUT + 5, -w, w, TAB_H, TOP_Z + 5))
            inners.append(box(TAB_X - WALL, R_OUT + 5, -w - WALL, w + WALL, -1, TOP_Z + 5))
        for cut in cuts:
            solid = solid - cut.rotate([0, 0, a])
        for inner in inners:
            cavity = cavity - inner.rotate([0, 0, a])
    body = solid - cavity
    if GROOVE == "none":
        ceiling = TOP_Z - WALL
        rib = (m3d.Manifold.cylinder(RIB_H + 1, RIB_R + RIB_T / 2, RIB_R + RIB_T / 2, SEG)
               - m3d.Manifold.cylinder(RIB_H + 3, RIB_R - RIB_T / 2, RIB_R - RIB_T / 2, SEG)
               .translate([0, 0, -1]))
        body = body + rib.translate([0, 0, ceiling - RIB_H])
    for i in range(0, N_NOTCH, 2):
        a = 360.0 * i / N_NOTCH + 22.5
        hole = m3d.Manifold.cylinder(TAB_H + 4, HOLE_D / 2, HOLE_D / 2, 48)
        body = body - hole.translate([HOLE_R, 0, -2]).rotate([0, 0, a])
    return body


def finish(path):
    """After bevel.py: lift the tab blocks' underside TAB_LIFT above the lid's
    bottom edge, then flip the lid onto its top for printing. Done
    after the bevel because the bevel breaks on this thin step; it's on the
    underside, against the mounting, so its edges needn't be rounded."""
    tm = trimesh.load(path)
    mesh = m3d.Mesh(vert_properties=np.asarray(tm.vertices, np.float32),
                    tri_verts=np.asarray(tm.faces, np.uint32))
    mesh.merge()
    body = m3d.Manifold(mesh)
    if body.status() != m3d.Error.NoError:
        raise SystemExit(f"{path} is not a clean solid: {body.status()}")
    w = TAB_W / 2 + WALL
    for i in range(0, N_NOTCH, 2):
        a = 360.0 * i / N_NOTCH + 22.5
        lift = box(TAB_X - WALL - 1, R_OUT - WALL - 1.5, -w, w, -1, TAB_LIFT)
        body = body - lift.rotate([0, 0, a])
    return body.rotate([180, 0, 0]).translate([0, 0, TOP_Z])


def save(manifold, out):
    mesh = manifold.to_mesh()
    tm = trimesh.Trimesh(np.asarray(mesh.vert_properties)[:, :3], np.asarray(mesh.tri_verts))
    # The cut after the bevel can leave a few loose zero-volume faces; keep
    # the solid only.
    tm = max(tm.split(only_watertight=False), key=lambda b: len(b.faces))
    tm.export(out)
    print(f"watertight={tm.is_watertight} extents={tm.extents.round(1)} "
          f"volume={tm.volume/1000:.1f} cm3 (~{tm.volume/1000*1.27:.0f} g PETG) -> {out}")


if __name__ == "__main__":
    if GROOVE == "--finish":   # python revolved_lid.py --finish lid_round.stl
        save(finish(sys.argv[2]), OUT.with_name("lid_print.stl"))
    else:
        save(build(), OUT)
