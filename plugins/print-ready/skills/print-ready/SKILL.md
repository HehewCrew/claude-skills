---
name: print-ready
description: Turn a set of 3D models into print-ready Bambu Studio projects and a real cost - scale a set to several sizes (chess sets, product lines), lay out one-colour plates, bake per-height settings into the 3MF (e.g. a heavier 40 % infill base) so the file opens and prints with nothing to configure, re-slice with the project's own settings, keep big files as 3MF not STL, and cost each piece and set from the slicer (filament price per kg, electricity per kWh, a machine-hour rate, a savings reserve, what a selling price earns per printer hour). Use when the user asks for "the 3mf ready to use", "make it heavier", "sizes 4 and 5", "how much does a set cost to print", "what does an hour earn at this price", or prices a printed product line; works with the bambu-studio-ai skill (Python environment, slice.py).
---

# Print-ready

From models to files the user only opens and sends, and to prices that hold up. *(Harvested from a 3D-printed chess line: three sizes, six ready projects, prices anchored on a competitor's moulded set. Each trap below cost a round there.)*

Tools: the **bambu-studio-ai** skill's Python environment (trimesh, manifold3d) and its `slice.py`; Bambu Studio installed (its command line does the slicing). Scripts here: [scripts/plate.py](scripts/plate.py), [scripts/make_ready.py](scripts/make_ready.py), [scripts/cost.py](scripts/cost.py). If the `replacement-part` skill is installed, its `slice_with.py` adds process overrides (supports, walls) to a slice.

## Steps

1. **Sizes from one reference dimension.** Scale every piece by `target / current` of the defining part (a chess king's height: size 3 ≈ 76 mm, size 4 ≈ 89, size 5 = 95, the scale most chess shops use; the pawn then lands near the 50/95 ratio). Measure the real models first (trimesh `extents`), never trust a remembered size: stock believed to be "size 4" measured as size 3. Write the generator as a script in the project (one folder per size, one file per piece) so any size can be rebuilt.
2. **Plates as 3MF.** `plate.py out.3mf --scale k --cols 5 rook.stl:2 … pawn.stl:8` (one colour per plate: a half chess set is 16 pieces + the king's cross). Detailed meshes make **STL plates of ~100 MB** and a lineup of 190 MB, over GitHub's 100 MB file limit; the same plate as 3MF is a third. Keep the plate inside the bed minus ~10 mm; the script warns.
3. **Slice for the numbers**, default profile first: `slice.py plate.3mf --printer P1S --material PLA --json` (a Bambu filament name such as `"Bambu PLA Wood"` for other materials). Compare with **one real print the user made**: their own settings can run well above the slicer (here **~1.5× the time and grams**). Ask which basis prices use; a heavier, slower personal profile changes every price.
4. **Heavier pieces: test the options before recommending one.** Splitting a plate at a height and slicing the two parts with different infill estimates it, but the split adds ~0.6 h and ~18 g (a second start sequence, extra shells at the cut): measure that overhead by slicing the split at default and subtract it. Measured on a 95 mm-king set: default 269 g / 7.6 h · 15 mm base at 40 % **326 g / 8.3 h** · 60 % 388 g / 9.3 h · solid 7.5 mm base 408 g / 9.4 h · solid 15 mm base 510 g / 10.7 h. The bases hold most of the volume, so "solid bases" is the wrong reflex; plastic can't reach weighted-piece weight (~430–440 g for a single-weighted 95 mm set) cheaply, steel can. Show the table, then recommend.
5. **Make the files ready** (for "nothing to configure"):
   - slice the plate once into a full project: `slice.py plate.3mf --printer P1S --material PLA -o base.3mf`;
   - `make_ready.py base.3mf ready.3mf <height> 40%` bakes a height-range modifier (the bottom H mm at that infill) and re-slices with the project's own settings;
   - check its line: **`ranges kept: True` and the grams up** (a size 5 plate went 135 → 173 g). One file per size × material, named so the user picks by name (`<set>_size5_half-set_PLA.3mf`). Each holds the G-code, the settings and the range; the only choice left is which spool.
6. **Cost and price.** `cost.py --grams G --hours H --filament <per kg> --kwh <price> --kw 0.12 --rate <machine-hour> --reserve <per hour> --price <p>`. Report filament + electricity, the 3× floor, the machine-hour floor, and **what the price earns per printer hour**. A price anchored on a competitor's moulded product often earns far under the machine-hour bar: say so plainly, and that single pieces or variants carry the margin.
7. **A price ladder when sets and singles both sell:** the full set at the anchor, a half set ~7 % above half of it (two halves always dearer than the set), single pieces above the half-set share; a premium material +5–10 % (filament is a small part of the cost, printer hours are most of it). Check each step with `cost.py`.
8. **Keep models out of git** when the user wants that: `*.stl`, `*.3mf` in `.gitignore`, and `git rm --cached` for files already tracked (on the user's yes; they stay on disk). Commit the generator scripts, so every file can be rebuilt.

## Traps

- **`layer_config_ranges.xml` needs `<object id="1">`** for a one-object project. The id written in `model_settings.config` (2) and 0 are **silently ignored**: same grams, ranges dropped from the output. `make_ready.py` defaults to 1 and warns.
- **100 % infill needs zig-zag or rectilinear**, or the command line fails with "Invalid parameter value(s) included in the 3mf file. (code -18)". Pass `--key sparse_infill_pattern=zig-zag`.
- **Never `--load-settings` when re-slicing a project**: it replaces the project's settings.
- Calling bambu-studio-ai's `slice.py` functions from your own script: `PrintRequest(quality="standard")`, not `None` ("Unknown quality None").
- **Windows:** Git Bash's `/tmp` is not Windows Python's; write outputs under a Windows path. A `c:/…` argument has a colon, which is why `plate.py` reads `file.stl:count` after the extension.
- **Electricity:** a printer's power-supply rating (~1 kW) is not its draw. A P1S on PLA averages roughly 0.10–0.15 kW; per-hour figures built on the rating overstate it several times. It rarely changes a price, but say so.
- trimesh's plane slicing needs `shapely`; without it, cut with manifold3d (`Manifold.trim_by_plane`).

## Rules

- **Measure, then recommend.** Every weight and time claim comes from a slice, labelled slicer or real.
- **The user prints.** Files go to Bambu Studio for the user to send; never start a print.
- **Ask which basis** (their settings or new ones) before pricing, and ask before printing stock nobody ordered: the user may prefer to show variants without printing them.
- Big models stay local unless the user wants them in git.
