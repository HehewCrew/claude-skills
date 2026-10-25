"""Turn a sliced Bambu Studio project into a print-ready one with a height-range modifier baked in:
the bottom H mm of the object gets its own settings (e.g. 40 % infill for heavier bases), then the
project is re-sliced by Bambu Studio's CLI with the project's OWN settings, so the file opens ready to
print with nothing to configure.

Steps:
    1. slice the plate once to get a full project (bambu-studio-ai's slice.py, or slice_with.py):
       python slice.py plate.3mf --printer P1S --material PLA -o base.3mf
    2. python make_ready.py base.3mf ready.3mf 15 40%  [--key sparse_infill_pattern=zig-zag ...] [--object-id 1]

Traps:
  * The ranges file is Metadata/layer_config_ranges.xml, and its <object id> must be **1** for a one-object
    project. The id Bambu writes in model_settings.config (2) is silently ignored, and so is 0: the slice
    comes out unchanged and the file loses the ranges. Check the printed "ranges kept" and the grams.
  * Don't pass --load-settings to the CLI here: it would replace the project's settings.
  * 100 % infill needs a pattern that allows it (zig-zag / rectilinear), or the CLI fails with
    "Invalid parameter value(s) included in the 3mf file. (code -18)".
"""
import argparse, json, re, shutil, subprocess, sys, tempfile, zipfile
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("src"); ap.add_argument("out")
ap.add_argument("height", type=float, help="top of the range, mm from the bed")
ap.add_argument("infill", help="e.g. 40%%")
ap.add_argument("--key", action="append", default=[], help="extra key=value for the range")
ap.add_argument("--object-id", default="1")
ap.add_argument("--cli", default=r"C:\Program Files\Bambu Studio\bambu-studio.exe",
                help="the Bambu Studio executable (macOS: /Applications/BambuStudio.app/Contents/MacOS/BambuStudio)")
a = ap.parse_args()
src, out = Path(a.src).resolve(), Path(a.out).resolve()

opts = {"layer_height": "0.2", "sparse_infill_density": a.infill}
opts.update(dict(kv.split("=", 1) for kv in a.key))
ranges = ('<?xml version="1.0" encoding="utf-8"?>\n<objects>\n'
          f' <object id="{a.object_id}">\n  <range min_z="0" max_z="{a.height:g}">\n'
          + "".join(f'   <option opt_key="{k}">{v}</option>\n' for k, v in opts.items())
          + '  </range>\n </object>\n</objects>\n')

work = Path(tempfile.mkdtemp(prefix="ready-", dir=out.parent))
mid = work / "in.3mf"
with zipfile.ZipFile(src) as z, zipfile.ZipFile(mid, "w", zipfile.ZIP_DEFLATED) as w:
    for n in z.namelist():
        if n.startswith("Metadata/plate_1.gcode") or n == "Metadata/layer_config_ranges.xml":
            continue  # the old G-code is regenerated below
        w.writestr(n, z.read(n))
    w.writestr("Metadata/layer_config_ranges.xml", ranges)

r = subprocess.run([a.cli, "--slice", "0", "--outputdir", str(work), "--export-3mf", "ready.3mf", str(mid)],
                   cwd=work, capture_output=True, encoding="utf-8", errors="replace")
if r.returncode != 0 or not (work / "ready.3mf").exists():
    res = work / "result.json"
    print("FAILED", r.returncode, json.loads(res.read_text(encoding="utf-8")).get("error_string") if res.exists() else r.stderr[-600:])
    sys.exit(1)
shutil.move(str(work / "ready.3mf"), out)
shutil.rmtree(work, ignore_errors=True)
with zipfile.ZipFile(out) as z:
    info = z.read("Metadata/slice_info.config").decode("utf-8")
    kept = "Metadata/layer_config_ranges.xml" in z.namelist()
g = re.search(r'used_g="([\d.]+)"', info); t = re.search(r'key="prediction" value="(\d+)"', info)
print(f"{out.name}: {g.group(1) if g else '?'} g, {int(t.group(1)) / 3600:.2f} h, ranges kept: {kept}")
if not kept:
    print("WARNING: the range was ignored (wrong --object-id?): the slice is the unmodified one")
