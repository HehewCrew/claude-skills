"""Slice with Bambu Studio's own engine and profiles, plus process overrides
(supports, walls, brim...), which the bambu-studio-ai skill's slice.py has no
flags for. Reports time, grams and the slicer's warnings.

Run with the bambu-studio-ai venv:
    python slice_with.py part.stl --printer P1S --material PETG \
        --set enable_support=1 support_type="normal(auto)" support_on_build_plate_only=1 \
              wall_loops=5 brim_type=no_brim

Values are Bambu Studio process keys, as strings. Useful ones:
  enable_support=1 · support_type=normal(auto)|tree(auto) · support_on_build_plate_only=1
  wall_loops=N · sparse_infill_density=15% · brim_type=no_brim|auto_brim
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path.home() / ".claude/skills/bambu-studio-ai/scripts"))
import slice as s  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("model")
ap.add_argument("--printer", default="P1S")
ap.add_argument("--material", default="PLA")
ap.add_argument("--quality", default="standard", choices=["draft", "standard", "fine"])
ap.add_argument("--set", nargs="*", default=[], metavar="KEY=VALUE")
ap.add_argument("-o", "--output")
a = ap.parse_args()

model = Path(a.model).resolve()
out = Path(a.output).resolve() if a.output else model.with_name(model.stem + "_sliced.3mf")
cli, library, _ = s.load_library(as_json=False)
choice = s.resolve_profiles(library, s.PrintRequest(printer=a.printer, nozzle_mm=0.4, material=a.material,
                                                    quality=a.quality, layer_height_mm=None))
process = library.flatten("process", choice.process)
process.update(dict(kv.split("=", 1) for kv in a.set))
job = s.SliceJob(model=model, output=out, timeout_s=600, bed_type=choice.bed_type,
                 machine=library.flatten("machine", choice.machine), process=process,
                 filament=library.flatten("filament", choice.filament))
e = s.run_slice(cli, job).estimate
h, m = int(e.print_time_s // 3600), round(e.print_time_s % 3600 / 60)
print(f"~ {h} h {m:02d} min, {e.filaments[0].grams:.0f} g {a.material}, "
      f"warnings: {list(e.warnings) or 'none'} -> {out.name}")
