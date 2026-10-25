---
name: replacement-part
description: Copy a broken or missing real-world part (a lid, cover, lens, bracket, knob, shell) into a printable 3D model from the user's photos and tape measurements - getting the measurements out of someone who isn't a CAD person (labelled diagrams, annotated renders, option renders), a parametric model (revolved profile + cuts), rounded edges for parts the public touches, printing a part close to the plate's size (no tree supports, no brim, 45° ledges), slicing with supports, and a cheap fit test before the real material. Use when the user sends photos of an object and asks for "a 3D model of this", "make a replacement", "copy this part", "print a new one of these", or for any client repair job; works with the bambu-studio-ai skill (manifold3d CAD, analyze, preview, slice).
---

# Replacement part

Turns photos and a tape measure into a part that fits where the old one did. Every trap below cost a round on a real job: a 250 mm light lens whose profile was read upside down twice, a bevel that silently did nothing, tree supports refused off the plate. Model code: [examples/revolved_lid.py](examples/revolved_lid.py), the worked example.

Tools: the **bambu-studio-ai** skill's venv (`manifold3d`, `trimesh`, its `preview.py`, `analyze.py`, `slice.py`), Blender for the bevel ([scripts/bevel.py](scripts/bevel.py)), and [scripts/slice_with.py](scripts/slice_with.py) for slicing with supports.

## Steps

1. **Fit first, shape second.** Ask only for the dimensions that decide the fit: the outer size, the hole-to-hole distance (centre to centre, across), the hole diameter or screw, and the wall thickness. Then ask what the part does (light through it? heat? touched by children? outdoors?), because that picks the material:
   - a light shines through it: translucent PETG or basic PLA, solid walls with no infill (5 walls), never a matte PLA;
   - LEDs or a closed housing: PETG (PLA softens around 55 °C);
   - kids or the public: PETG (tougher), and every edge rounded (step 5).
   Check the size against the plate at once. Over the usable size, the part must be split.
2. **Get the shape from photos, and confirm the reading.** The commonest mistake is reading the profile upside down: a dome for a bowl, a dish for a groove. Before modelling, show 2–3 **side-section sketches** as AskUserQuestion previews ("which one is yours?"). Ask for photos that answer questions:
   - **a side photo at table height**, with the tape standing upright and zero on the table: it gives heights;
   - a top photo with the tape across: it gives widths;
   - **the underside**: it shows how the shell follows the outside, ribs and tab blocks.
   A photo from above gives no heights, and a low-res video won't read millimetres; say so and ask for a sharp photo instead.
3. **Name the features the way the user can see them.** When a word doesn't land (groove, panel, recess), render the current model and **draw arrows and labels on it** (Pillow), in the user's language. For a choice of shape (U, flat-bottomed or V), render the variants **side by side** and ask. Words alone cost several rounds here.
4. **Build it parametric.** Every dimension is a named constant, marked `measured` or `EST` (read from a photo), so a new measurement is a one-line change. The pattern in the example:
   - **a revolved profile** for round parts: list the outer surface as (radius, height); mirror it and extend it below the table; `offset(-wall)` gives an even wall normal to the surface; clip to the half-plane and revolve;
   - **cuts as solids**: a pocket in a shell is the outside cut *and* the cavity cut 2 mm further out, so the walls stay closed;
   - a panel that follows a sloped wall is a slab extruded from its (x, z) section, not a box;
   - a hollow lid needs a **stiffening rib** inside if a feature (a groove) is removed.
5. **Round the edges.** This is safety, not styling, on anything the public touches. Two passes:
   - **the profile:** round it in 2D before revolving (`offset(-r, Round).offset(r, Round)` rounds outside corners; the reverse rounds inside ones). Example: 4 mm outside, 3 mm inside;
   - **the cut edges:** `scripts/bevel.py` in Blender (`blender -b -P bevel.py -- in.stl out.stl 0.9`). **Width ≤ half the thinnest wall** (0.9 on 2 mm), because the overlap clamp must stay off: with it on, the boolean slivers shrink the bevel to nothing and the part comes out unchanged (same volume = it did nothing).
   - **A thin step (under ~2.5 mm) breaks the bevel** (loose triangles, not watertight): cut that feature **after** the bevel, in a `finish` step on the bevelled mesh (`Mesh.merge()` → `Manifold`, check `status()`), and keep only the largest body when saving. A hidden underside step doesn't need rounding anyway.
6. **Orient and check for printing.** Put the biggest flat face that isn't seen on the plate; for a lid that's usually its flat top (upside down), which gives the visible face the plate's finish. Then:
   - `analyze.py <file> --printer <model>` for the overhangs and bed contact (its 10 mm safety margin makes a 250 mm part on a 256 plate "too big": the slicer decides, not that check);
   - **turn flat ledges that would hang into 45° slopes** (a rim step, the floor of a panel), keeping the dimensions that fit;
   - support marks land on whatever faces down: when they would be on the visible face, say so and offer the alternative (removing the feature, with what it costs: flex, look).
7. **Slice it as it will really print:** `python scripts/slice_with.py part.stl --printer P1S --material PETG --set enable_support=1 support_type="normal(auto)" support_on_build_plate_only=1 wall_loops=5 brim_type=no_brim`.
   - **A part within ~10 mm of the plate edge:** Bambu Studio refuses **tree supports** and **auto brim** ("no object fully inside" plate, code -50), because their footprint spills off the plate. Use normal supports, no brim.
   - Give the user time and grams **with supports**, beside the bare figure. The difference (here 5 h 06 → 6 h 29, 178 → 219 g) is real and changes the quote.
8. **Fit-test before the real material:** a flat ring or plate, ~1.6 mm thick, with the exact outline and holes, in any cheap PLA (here 34 min, 22 g). The user pins it onto the original or the mounting. If one hole looks off, ask how far and which way. Under ~1 mm, the hole's play takes it. Over that, check against the mounting, not the original: an old part's tabs may have been broken and glued back. Offer **slots** (e.g. 5 × 7 mm) if the mounting itself is imprecise.
9. **Record the job.** Keep the user's photos untouched in a `received/` folder; the measurements table (measured / EST); the material and print settings; the slice figures; the chain of commands that rebuilds everything (`model.py` → `bevel.py` → `finish` → `slice_with.py`). Commit the scripts, the print file, the sliced `.3mf` and the photos; leave out intermediates and preview renders.

## Rules

- **Never invent a fit dimension.** Shape details can be estimated from photos and marked EST; the outer size, the hole positions and the wall can't.
- **One question round per reply, with pictures.** People measuring an object answer a labelled drawing faster than a list of words.
- **Look at every render before showing it,** and compare it to the user's photo of the same side.
- **Say what a change costs** before making it: removing a feature for support marks costs stiffness and the look; a 45° slope instead of a step changes how the part looks where it's mounted.
- **The user starts the print** (bambu-studio-ai's rule); offer the slicer file, don't send it to the printer.
