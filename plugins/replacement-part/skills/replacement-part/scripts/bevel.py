"""Round the sharp edges of a part (Blender bevel by angle), keeping curves alone.

Run headless with Blender (4.2+; 5.0 tested):
    "C:/Program Files/Blender Foundation/Blender 5.0/blender.exe" -b -P bevel.py -- in.stl out.stl [width_mm] [angle_deg]

- Only edges sharper than the angle get bevelled, so a revolved surface (faces
  1 degree apart) keeps its facets and only boolean-cut edges are rounded.
- Width defaults to 0.9 mm: two bevels must fit in the thinnest wall
  (2 x 0.9 < 2 mm), because the overlap clamp is OFF (see below).
- Coplanar sliver triangles from booleans are merged first (dissolve_limited
  at 0.5 degrees); with them, the bevel's overlap clamp shrinks the width
  to nothing and the part comes out unchanged.
Check the result is still one watertight body (trimesh) before using it.
"""
import math
import sys

import bpy

args = sys.argv[sys.argv.index("--") + 1:]
src, dst = args[:2]
WIDTH = float(args[2]) if len(args) > 2 else 0.9
ANGLE = float(args[3]) if len(args) > 3 else 25
SEGMENTS = 4

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.wm.stl_import(filepath=src)
obj = bpy.context.selected_objects[0]
bpy.context.view_layer.objects.active = obj

bpy.ops.object.mode_set(mode="EDIT")
bpy.ops.mesh.select_all(action="SELECT")
bpy.ops.mesh.remove_doubles(threshold=0.001)
bpy.ops.mesh.dissolve_limited(angle_limit=math.radians(0.5))
bpy.ops.object.mode_set(mode="OBJECT")

mod = obj.modifiers.new("round", "BEVEL")
mod.width = WIDTH
mod.segments = SEGMENTS
mod.limit_method = "ANGLE"
mod.angle_limit = math.radians(ANGLE)
mod.use_clamp_overlap = False
mod.miter_outer = "MITER_ARC"
bpy.ops.object.modifier_apply(modifier=mod.name)

bpy.ops.wm.stl_export(filepath=dst, export_selected_objects=True)
print("bevelled ->", dst)
