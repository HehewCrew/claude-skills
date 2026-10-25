"""Lay out models on one print plate at a scale, as a 3MF (STL plates of detailed meshes pass 100 MB).

Run with the bambu-studio-ai venv (trimesh, numpy):
    python plate.py out.3mf --scale 1.257 --bed 256 --gap 4 --cols 5 \
        rook.stl:2 knight.stl:2 bishop.stl:2 queen.stl king.stl pawn.stl:8

Each model is centred, dropped onto z=0 and scaled by --scale (per file: name.stl:count:scale overrides it).
Prints each part's size and the plate width; warns when the plate passes the bed minus a 10 mm margin.
"""
import argparse
import re
import trimesh

ap = argparse.ArgumentParser()
ap.add_argument("out")
ap.add_argument("parts", nargs="+", help="file.stl[:count[:scale]]")
ap.add_argument("--scale", type=float, default=1.0)
ap.add_argument("--bed", type=float, default=256.0)
ap.add_argument("--gap", type=float, default=4.0)
ap.add_argument("--cols", type=int, default=0, help="0 = square-ish grid")
a = ap.parse_args()

meshes = []
for spec in a.parts:
    mt = re.match(r"^(.*?\.(?:stl|3mf|obj))(?::(\d*))?(?::([\d.]+))?$", spec, re.I)  # "c:/..." keeps its drive colon
    if not mt:
        ap.error(f"can't read {spec!r}: use file.stl[:count[:scale]]")
    path, n = mt.group(1), int(mt.group(2) or 1)
    k = float(mt.group(3)) if mt.group(3) else a.scale
    m = trimesh.load(path, force="mesh"); m.apply_scale(k)
    b = m.bounds; m.apply_translation([-(b[0][0] + b[1][0]) / 2, -(b[0][1] + b[1][1]) / 2, -b[0][2]])
    print(f"{path}: {m.extents[0]:.1f} x {m.extents[1]:.1f} x {m.extents[2]:.1f} mm, {m.volume / 1000:.2f} cm3 x{n}")
    meshes += [m] * n

cols = a.cols or max(1, round(len(meshes) ** 0.5 + 0.49))
rows = (len(meshes) + cols - 1) // cols
pitch = max(max(m.extents[0], m.extents[1]) for m in meshes) + a.gap
out = []
for i, m in enumerate(meshes):
    c = m.copy(); r, q = divmod(i, cols)
    c.apply_translation([(q - (cols - 1) / 2) * pitch, ((rows - 1) / 2 - r) * pitch, 0])
    out.append(c)
w, h = pitch * cols, pitch * rows
trimesh.util.concatenate(out).export(a.out)
print(f"plate {w:.0f} x {h:.0f} mm ({len(meshes)} parts, {cols} x {rows})")
if max(w, h) > a.bed - 10:
    print(f"WARNING: wider than the bed minus a 10 mm margin ({a.bed - 10:.0f} mm): lower --gap, change --cols, or split the plate")
