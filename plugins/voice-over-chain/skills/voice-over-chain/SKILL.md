---
name: voice-over-chain
description: Set up a voice-over recording and lock its Audacity processing chain from measurements, not defaults, then run it on each full take (noise-margin re-check, room-tone handling, presets back to back, hand edits last, background-noise scan) - mic check (device, the mic's noise cancelling A/B, placement, level vs room noise), a short test recording of real script lines, ffmpeg measurements of that WAV, each chain value derived and simulated on it, the user running it in Audacity, then the processed WAV re-measured before it goes to the video editor. Use when the user sets up a new mic or room, records a voice-over or a test take, asks "is my level OK", "what settings for the compressor/limiter", "check my recording", "is this ready for Resolve/Premiere", wants an Audacity macro or presets for the chain, or invokes /voice-over-chain.
---

# Voice-over chain

A voice-over chain is only right for **this voice, this mic, this room**. This skill measures all three, derives every value from the numbers, simulates the chain on the real take, and checks what Audacity actually produced. Generic "voice-over presets" are where it goes wrong: a threshold copied from a tutorial can sit above a quiet voice and never act at all.

**Project settings first:** look for a chain the project already locked (search its docs for "processing chain" or "locked"). If one exists, reuse its setup and values and only re-measure: **Step 5b and Step 6 on every new take**, Steps 3–5 again only if the mic, room or placement changed.

## Steps

1. **Setup, one decision at a time** (the user decides; write each down as it's settled):
   - device + app (a USB-C wireless receiver on a PC without USB-C needs a USB-C female → USB-A adapter; a USB-C to USB-A cable won't fit a receiver that is itself a plug);
   - **mono**, 48 kHz, WAV; Audacity works in 32-bit float, export 24-bit; on Windows MME, set the device's Windows format to 48000 Hz so Windows doesn't resample;
   - **the mic's built-in noise cancelling: A/B by ear.** It is burned into the file and can't be undone; Audacity's noise reduction can be redone. Voices often sound more natural with it off (breaths come back: expected, and handled later);
   - placement: one transmitter only (two mics on one voice = comb filtering + twice the room). A clip-on mic fixed to something on the head (e.g. under a cap brim) keeps the distance to the mouth constant when the head moves.
2. **Quick level check in Audacity:** select a clip → Amplify → the proposed "Amplification" = −(peak). **If the slider sits at its 50 dB maximum, read "New peak amplitude" and subtract 50** (e.g. −7.05 → noise at −57 dB). Do it on speech and on a silence. Never judge the level from the waveform's height: the display is linear, and a **dragged clip volume line** (the line with a dot along the top of the clip) boosts what you see. Reset it before judging.
3. **The test recording (~80 s):** a lively opening, one normal paragraph with numbers, the closing line, 2 s of silence between parts, then **30 s of room tone** (still and silent). Real script lines, the real setup. Export untouched to `<project>/audio/test-raw.wav`.
4. **Measure it:** `python <this skill's folder>/vo_measure.py raw <test-raw.wav>` (needs only ffmpeg; set `PYTHONIOENCODING=utf-8` on Windows). Read:
   - **speech percentiles vs room tone** → the noise margin; a speech median ~28 dB above the room is workable with noise reduction;
   - **room tone bands** → hiss (>8 kHz), low murmur, or mains hum (a hum band ≥ 6 dB over its reference). Hum gets switched off at the source, not filtered;
   - **voice below 80 Hz** vs the whole voice → whether a high-pass at 80 Hz costs the voice anything;
   - **peak-to-loudness ratio.** Over 15 dB means a **limiter** is needed to reach −16 LUFS under −1 dB; no compressor setting catches fast syllable onsets (a real case: 25 dB, onsets in 200 Hz–3 kHz, not pops or sibilance);
   - **the loudest peaks' makeup** → pops (placement or a windshield) vs sibilance (a de-esser) vs onsets (a limiter).
5. **Derive, simulate, then propose** each value with the number it came from: `vo_measure.py simulate <wav> --voice-end <s> [--hp --pre --th --ratio --attack --release --target --limit]`. A chain that worked:
   1. **Noise Reduction**, profile from the room tone, amount by the user's ear (e.g. 8 dB);
   2. **High-Pass Filter** 80 Hz, 12 dB/oct;
   3. **Loudness Normalization −26 LUFS**: gives the compressor the same input every time. Never normalize to a peak when peak-to-loudness is high: one syllable would set the whole level. **Ask whether "treat mono as dual-mono" is ticked here**: ticked, the mono file lands 3 dB lower (−29 as measured) and the same threshold compresses less. Simulate with `--pre -29` when ticked;
   4. **Compressor**: threshold from the measured speech levels **after** step 3 (e.g. loud words ~−21, normal ~−28 → **−24 dB**), 3:1, 10 ms, 100 ms, make-up 0. Aim for ~3–6 dB of gain reduction on loud words;
   5. **Breaths**: by hand, by ear (lower them −6 to −10 dB rather than cut: cut pauses sound dead). **Done last, after step 7** (see the order below);
   6. **Loudness Normalization −16 LUFS**, "treat mono as dual-mono" ticked (the mono file then reads −19; on two speakers −16);
   7. **Limiter**: threshold **−2 dB** and output **−2 dB**, lookahead 5 ms, knee 2 dB, release 50 ms. ⚠️ Audacity's default **−6 → −1 adds +5 dB of make-up gain** and undoes step 6: the output must equal the threshold.
   Say which values are measured and which aren't yet. Nothing is locked until it's measured or the user picks it.

   **The order to run it: every preset back to back, every hand edit last.** Noise profile → 1 → 2 → 3 → 4 → 6 → 7, then breaths (5), cleaning cuts and pause tightening, all on the processed sound, so the user judges pauses as they will finally sound. It's safe: steps 1, 2, 4 and 7 act locally, and loudness normalization gates out silence, so later cuts barely move the level (the export is re-measured anyway). Two conditions: take the noise profile before any cut, and cut inside pauses, never into a limited word's attack (it clicks).

5b. **Before running a locked chain on a full take, re-check the noise margin** (voice LUFS vs room-tone RMS in clean 1–1.5 s pauses without breaths, ffmpeg `astats`). If it dropped against the test take, the locked Noise Reduction is too weak: A/B a higher amount. A real case: ~29 dB on the test, ~22 dB on the full take (room ~4 dB louder, voice 3.6 dB quieter), and the noise reduction went from 8 to 12 dB by ear. Use the Noise Reduction dialog's **Preview** for the A/B: nothing to undo. Listen in a quiet pause; reject an amount that makes the voice metallic or "underwater".

   **Room tone on the same track as the voice rides along:** selecting the track selects both, and an export mixes everything unmuted. After **Get Noise Profile**, export the room tone alone (selection only) as `room-tone.wav`, then delete it from the project. The profile stays in Audacity's memory until it closes (it isn't saved in the project), so keep the WAV for any later re-run.
6. **The user runs it in Audacity, exports, and you re-measure:** `vo_measure.py processed <final.wav>`. Pass: **−16 ±0.5 LUFS on two speakers**, true peak ≤ −1 dB, flat factor 0 (no clipping). Also report the gaps list: **0 gaps ≥ 0.15 s means every pause was cut**, including any deliberate breath pauses in the script; flag it against the script and the edit (cards and visuals need pauses). A take with every pause tightened is fine when the user shapes the stops in the video editor: say so, and that those gaps are reopened there with a pause cut from the processed file.
   - **Background noises (a dog, a door):** with word timings (e.g. a local Whisper transcript), mask the words ±60 ms and list 20 ms windows above −50 dB outside them. Loud hits (−14 to −25 dB) are usually mistimed word edges; **faint ones (−35 to −45 dB) are background**: give those times to the user first. Fixes, cheapest first: in a pause → select it → Silence (the processed noise floor makes it invisible); under a word → leave it if a music bed will cover it, else a local denoiser on those seconds only (e.g. DeepFilterNet, free), else re-take the line.
7. **Delivery (optional):** if a delivery-check skill is installed, run it on the take. Otherwise report what's measurable: words/s per part, phrases whose end fades ≥ 6 dB (a key number or the closing line swallowed), pauses present. Say plainly that tone itself can't be heard, only measured by proxies.
8. **Lock and record:** each value with its measurement and the test result, dated, where the project keeps its production settings. Then set up repeatability (below).

## Repeatability: presets, or a macro

**Audacity 4.0 has no macros** (the Macro Manager and scripting pipe were 3.x features; planned for 4.1). In 4.0, save each step as an **effect preset** (the preset list + save button in every effect window), named e.g. `VO <n> - <step>`, the first time it's applied with the locked values; each run is then: open effect → pick preset → Apply. **Noise Reduction has no preset in 4.0:** record its three values with the chain (reduction, sensitivity, frequency smoothing) and type them in.

With 3.x or 4.1+, use macros. A macro can't capture a noise profile or judge breaths; with the hand edits last, the chain is **one macro between two manual steps**:
- manual: select the room tone → Noise Reduction → **Get Noise Profile**; export the room tone, delete it from the project;
- **the macro** (voice selected): Noise Reduction → High-Pass Filter → Loudness Normalization −26 → Compressor → Loudness Normalization −16 (dual-mono) → Limiter;
- manual: breaths, mistakes, pauses.

Run them on the **voice only**: the room tone's long silence skews loudness normalization. For gap fill in the editor, cut a pause from the processed voice (it matches exactly). Menus move between versions: ask for a screenshot rather than guess. After building, re-run `processed` on a file made with the presets or macro: it must match the hand-made result.

## Rules

- **No assumed values.** Every locked value names the measurement it came from or the user's pick. A generic default is labelled as one.
- **Keep the raw take untouched.** Export it before any edit; process a copy.
- **You can't hear.** Pace, pauses, levels and spectra are measured; how it sounds is the user's call, and every "sounds better" is theirs.
- **Correct yourself in the open** when a new measurement contradicts an earlier estimate (screenshot readings are estimates; the file is the truth).
- ffmpeg on Windows: never put a Windows path in `ametadata=...:file=` (the drive colon splits the option). The script reads stderr instead.
