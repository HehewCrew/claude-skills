---
name: print-svg
description: Make print-ready SVG artwork for a 3D-printed piece - text on a keychain tag or plate, a name, a phrase, a heart or other simple shape, a corner monogram - for slicers like Bambu Studio, PrusaSlicer or Orca. Covers finding a font close to a customer's reference photo (rendered drafts on the real text), outlining the text, fitting it to the plate, drawing shapes as filled rings (slicers ignore strokes), measuring the real stroke width against the nozzle, letter spacing, and thickening without closing the letters. Use when a customer order needs custom lettering or a shape ("find a close font to this", "make me an SVG of the heart", "build the SVG with this text"), when preparing any text or icon SVG for a slicer, or when asked whether lettering is too thin to print.
---

# Print SVG

Turns a customer's text and a reference (a photo, an Etsy listing) into an SVG a slicer imports cleanly and a 0.4 mm nozzle prints. The traps below each cost a retry on a real order: a text + heart + monogram tag on a 60 × 18 mm plate.

Scripts are in `scripts/`. They need `uharfbuzz fonttools shapely pillow numpy`: install them into a **scratch folder**, not a project's venv, and pass that folder with `--lib`:

```bash
python -m pip install -q --target lib uharfbuzz fonttools shapely pillow numpy
```

## Steps

0. **Check an SVG is needed at all.** For plain text in one installed font, the slicer's own text tool (Bambu Studio's *Text Shape*: font, bold, thickness, embed depth) is simpler and stays editable. Build an SVG when there's a shape (a heart, an icon), an exact multi-element layout (text + monogram), a font the slicer can't load, or several pieces to batch.
1. **Ask what changes the result, once** (AskUserQuestion): the artwork alone or the plate too; the plate size (or "I'll scale it"); raised in one colour or flush with a colour change. Don't guess the plate: the text size depends on it.
2. **Find the font from drafts, not from memory.** Download 10–15 candidates from Google Fonts (open licences: prints can be sold) and render the customer's **real text** with `scripts/font_sheet.py`, the reference crop on top. Look at the sheet; name the closest 1–3 by the letterforms that match (a curled `d`, an `f` dropping below the line), not by family names. Show the sheet. If the user says the letters look cramped, offer open-letter alternatives on a second sheet, and spacing variants (step 4).
3. **Build with `scripts/build_plate.py`.** It shapes the text with HarfBuzz (kerning), converts it to outlines (no font needed in the slicer), shrinks it until the line, plus the heart if any, fits between the hole zone and the margin, and puts the monogram in the bottom-right corner:
   ```bash
   python build_plate.py --lib lib --font F.ttf --text "Happy birthday, Sam" --heart --mono S \
       --plate 60 18 --hole-zone 10 --track 0.045 --base 9 --out out/tag
   ```
   Look at `OUT-preview.png` once; fix and rebuild rather than describing a problem.
4. **Letter spacing costs size.** The line can't get wider than the plate, so more `--track` means smaller letters. Render 3–4 values side by side (0, 0.025, 0.045, 0.065) and let the user pick; 0.045 was the pick on a heavy casual font. Say the trade in one line, and that a longer plate is the way to keep both.
5. **Check the real stroke width** the script prints. Under **0.8 mm** (two lines of a 0.4 nozzle), raised letters print broken. Say so with the three ways out: print flush in a second colour (AMS), a 0.2 nozzle, or `--grow`.
6. **Thicken carefully** with `--grow` (letters only; the heart is built at 0.8 mm already). Start at **0.08 mm** on a heavy font. The script prints the counters before/after: if any closed, or the preview shows an `S` turning into an `8`, grow less. Deliver both files: plain for flush, `-thick` for raised.
7. **Deliver** the folder (SVGs, previews, the font files), the cap height and stroke width, and where to place it on the plate in the slicer. If the slicer sizes the SVG to its artwork rather than the viewBox, give the offset from the plate's top-left corner (the script prints the artwork bounds).

## Traps

- **Slicers ignore SVG strokes.** Bambu Studio imports fills. Every outline (a heart, a ring, a frame) must be a **filled ring**: buffer the centre line by half the stroke, `fill-rule="evenodd"`.
- **Measure stroke width as 2 × area / perimeter** of plain letters (`l r i v n`). The bounding box of an `l` includes its slant and read 1.03 mm for a real 0.5 mm, and a wrong figure like that reaches the customer.
- **Too much growth closes counters.** 0.15 mm on a heavy hand-lettered font at 2.65 mm caps nearly filled the heart and made the S read as 8.
- **A small heart at the text's stroke fills in.** Build it ~1.4 × the cap height with a 0.8 mm outline and a gap of ~0.7 × the cap height.
- **The Noto emoji repo moved** (its raw GitHub `svg/emoji_u*.svg` paths now 404). For emoji artwork, render with the Noto Color Emoji font from Google Fonts instead.
- **Etsy and similar listings are references, not sources.** Rebuild the look from an open font and your own shape; never trace the seller's artwork.

## Rules

- Never pick a font without showing a rendered sheet of the real text.
- Never claim a stroke width you didn't compute with the method above.
- Only open-licence fonts (Google Fonts: OFL / Apache) for anything sold.
- Keep drafts in a scratch folder; only the final SVG(s) belong in a project.
