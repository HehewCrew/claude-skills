"""Measure voice-over WAVs with ffmpeg, and simulate a processing chain on them.

Usage:
  python vo_measure.py raw <take.wav>
      Format, parts (split on silences >= 1.5 s), loudness and peak per part, speech-level
      percentiles (50 ms windows), room tone (the last silence >= 15 s) level and spectrum,
      what the loudest peaks are made of, peak-to-loudness ratio.
  python vo_measure.py simulate <take.wav> --voice-end S [--hp 80] [--pre -26] [--th -24]
      [--ratio 3] [--attack 10] [--release 100] [--target -16] [--limit -2]
      Runs high-pass -> gain to --pre LUFS -> compressor -> gain to --target LUFS (dual mono,
      like Audacity's "treat mono as dual-mono") -> limiter at --limit dBFS, on 0..voice-end.
      Prints what the compressor did, how often the limiter acts, final LUFS and peak.
      Noise reduction is not simulated (ffmpeg's differs from Audacity's).
  python vo_measure.py processed <final.wav>
      Format, loudness as mono and as stereo (how an editor plays it), peak, clipped samples,
      every gap >= 0.15 s below -40 dB, and the quietest 50 ms windows.

Needs only ffmpeg on PATH and the Python standard library. Set PYTHONIOENCODING=utf-8.
Trap: never pass a Windows path to ffmpeg's `ametadata=...:file=` (the drive colon splits the
option); this script reads ametadata from stderr instead.
"""
import argparse, math, re, subprocess, sys

def ff(path, af, ss=None, to=None):
    cmd = ['ffmpeg', '-hide_banner', '-nostats']
    if ss is not None: cmd += ['-ss', str(ss)]
    if to is not None: cmd += ['-to', str(to)]
    cmd += ['-i', path, '-af', af, '-f', 'null', '-']
    return subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace').stderr

def fmt(path):
    out = subprocess.run(['ffprobe', '-v', 'error', '-show_entries',
                          'stream=codec_name,sample_rate,channels,bits_per_sample:format=duration',
                          '-of', 'default=nw=1', path], capture_output=True, text=True).stdout
    d = dict(l.split('=', 1) for l in out.split() if '=' in l)
    return d

def ebu(path, ss=None, to=None, pre=''):
    e = ff(path, (pre + ',' if pre else '') + 'ebur128=peak=true', ss, to)
    s = e[e.rfind('Summary'):]
    g = lambda k: float(re.search(k + r':\s+(-?[\d.]+|-inf)', s).group(1).replace('-inf', '-120'))
    return {'I': g('I'), 'LRA': g('LRA'), 'TP': g('Peak')}

def stats(path, ss=None, to=None, pre=''):
    e = ff(path, (pre + ',' if pre else '') +
           'astats=measure_overall=Peak_level+RMS_level+Peak_count+Flat_factor:measure_perchannel=none', ss, to)
    v = lambda k: float(re.findall(k + r' dB: (-?[\d.]+|-inf)', e)[-1].replace('-inf', '-120'))
    pc = re.findall(r'Peak count: ([\d.]+)', e)
    ffl = re.findall(r'Flat factor: ([\d.]+)', e)
    return {'peak': v('Peak level'), 'rms': v('RMS level'),
            'peak_count': float(pc[-1]) if pc else 0, 'flat': float(ffl[-1]) if ffl else 0}

def series(path, ms=50, key='RMS_level', ss=None, to=None, pre=''):
    n = int(48 * ms)  # samples at 48 kHz
    e = ff(path, (pre + ',' if pre else '') + f'asetnsamples=n={n}:p=0,astats=metadata=1:reset=1:'
           f'measure_perchannel=none:measure_overall={key},ametadata=print:key=lavfi.astats.Overall.{key}', ss, to)
    return [float(x.replace('-inf', '-120')) for x in re.findall(key + r'=(-?[\d.]+|-inf)', e)]

def silences(path, noise=-45, d=1.5):
    e = ff(path, f'silencedetect=noise={noise}dB:d={d}')
    st = [float(x) for x in re.findall(r'silence_start: (-?[\d.]+)', e)]
    en = [float(x) for x in re.findall(r'silence_end: ([\d.]+)', e)]
    return list(zip(st, en + [None] * (len(st) - len(en))))

def pct(v, p):
    v = sorted(v); return v[min(len(v) - 1, int(p / 100 * len(v)))]

def cmd_raw(a):
    f = fmt(a.wav); dur = float(f['duration'])
    print(f"format: {f.get('codec_name')} {f.get('sample_rate')} Hz, {f.get('channels')} ch, "
          f"{f.get('bits_per_sample')}-bit, {dur:.1f} s")
    sil = [(s, e if e is not None else dur) for s, e in silences(a.wav)]
    room = next(((s, e) for s, e in reversed(sil) if e - s >= 15), None)
    voice_end = room[0] if room else dur
    cuts = [0.0]
    for s, e in sil:
        if e <= voice_end: cuts += [s, e]
    cuts.append(voice_end)
    parts = [(cuts[i], cuts[i + 1]) for i in range(0, len(cuts) - 1, 2) if cuts[i + 1] - cuts[i] > 0.3]
    print(f'voice ends at {voice_end:.2f} s; room tone: ' + (f'{room[0]:.2f}-{room[1]:.2f} s' if room else 'none found (need >= 15 s of silence)'))
    for i, (s, e) in enumerate(parts, 1):
        m = ebu(a.wav, s, e); st = stats(a.wav, s, e)
        print(f'part {i}: {s:6.2f}-{e:6.2f} s  I {m["I"]:6.1f} LUFS  peak {st["peak"]:6.1f} dB  LRA {m["LRA"]:.1f}')
    v = ebu(a.wav, 0, voice_end); vs = stats(a.wav, 0, voice_end)
    print(f'voice overall: I {v["I"]:.1f} LUFS, peak {vs["peak"]:.1f} dB -> peak-to-loudness {vs["peak"] - v["I"]:.1f} dB '
          f'(<= 15 needed for -16 LUFS under -1 dB; more means a limiter is needed)')
    sr = series(a.wav, 50, ss=0, to=voice_end)
    if room:
        rr = series(a.wav, 50, ss=room[0] + 1, to=room[1] - 1)
        thr = pct(rr, 90) + 15
        sp = [x for x in sr if x > thr]
        print('speech 50 ms RMS: ' + ' '.join(f'p{p} {pct(sp, p):.1f}' for p in (10, 25, 50, 75, 90, 99)))
        rs = stats(a.wav, room[0] + 1, room[1] - 1)
        print(f'room tone: RMS {rs["rms"]:.1f} dB, peak {rs["peak"]:.1f} dB, median 50 ms {pct(rr, 50):.1f} dB '
              f'-> speech median is {pct(sp, 50) - pct(rr, 50):.0f} dB above it')
        bands = [('<60 Hz', 'lowpass=f=60'), ('50 Hz hum', 'bandpass=f=50:width_type=q:w=20'),
                 ('75 Hz ref', 'bandpass=f=75:width_type=q:w=20'), ('100 Hz hum', 'bandpass=f=100:width_type=q:w=20'),
                 ('125 Hz ref', 'bandpass=f=125:width_type=q:w=20'), ('120-500', 'highpass=f=120,lowpass=f=500'),
                 ('500-2k', 'highpass=f=500,lowpass=f=2000'), ('2k-8k', 'highpass=f=2000,lowpass=f=8000'),
                 ('>8k (hiss)', 'highpass=f=8000')]
        print('room tone by band (RMS dB; a hum band >= 6 dB over its ref = mains hum):')
        print('  ' + ' · '.join(f'{n} {stats(a.wav, room[0] + 1, room[1] - 1, b)["rms"]:.1f}' for n, b in bands))
    lo = [('all', ''), ('<80 Hz', 'lowpass=f=80'), ('100-300', 'highpass=f=100,lowpass=f=300')]
    print('voice low end (RMS dB): ' + ' · '.join(f'{n} {stats(a.wav, 0, voice_end, b)["rms"]:.1f}' for n, b in lo))
    pa = series(a.wav, 10, 'Peak_level', 0, voice_end)
    pl = series(a.wav, 10, 'Peak_level', 0, voice_end, 'lowpass=f=200:poles=2')
    ph = series(a.wav, 10, 'Peak_level', 0, voice_end, 'highpass=f=3000')
    seen = []
    for i in sorted(range(len(pa)), key=lambda i: -pa[i]):
        if any(abs(i - j) < 10 for j in seen): continue
        seen.append(i)
        if len(seen) > 5: break
    print('loudest peaks (a <200 Hz part within ~6 dB = pops; >3 kHz within ~6 dB = sibilance; else syllable onsets):')
    for i in seen:
        print(f'  t={i * 0.01:6.2f}s peak {pa[i]:6.1f}  <200 Hz {pl[i]:6.1f}  >3 kHz {ph[i]:6.1f}')

def cmd_simulate(a):
    T = a.voice_end
    hp = f'highpass=f={a.hp}:poles=2'
    I0 = ebu(a.wav, 0, T, hp)['I']; g1 = a.pre - I0
    comp = (f'{hp},volume={g1}dB,acompressor=threshold={a.th}dB:ratio={a.ratio}:attack={a.attack}:'
            f'release={a.release}:knee=2:detection=rms')
    I1 = ebu(a.wav, 0, T, comp)['I']
    g2 = (a.target - 3.0) - I1  # dual mono: a mono file reads 3 dB under its two-speaker loudness
    pre_lim = f'{comp},volume={g2}dB'
    pk = series(a.wav, 50, 'Peak_level', 0, T, pre_lim)
    over = [p - a.limit for p in pk if p > a.limit]
    lim = 10 ** (a.limit / 20)
    fin = ebu(a.wav, 0, T, f'{pre_lim},alimiter=limit={lim:.4f}:attack=5:release=50:level=0,pan=stereo|c0=c0|c1=c0')
    print(f'pre-gain to {a.pre} LUFS: {g1:+.1f} dB · compressor lowers loudness {a.pre - I1:.1f} dB')
    print(f'limiter acts on {len(over)}/{len(pk)} 50 ms windows'
          + (f', avg {sum(over) / len(over):.1f} dB, max {max(over):.1f} dB' if over else ''))
    print(f'final (two speakers): I {fin["I"]:.1f} LUFS, true peak {fin["TP"]:.1f} dBFS')

def cmd_processed(a):
    f = fmt(a.wav)
    print(f"format: {f.get('codec_name')} {f.get('sample_rate')} Hz, {f.get('channels')} ch, "
          f"{f.get('bits_per_sample')}-bit, {float(f['duration']):.1f} s")
    m = ebu(a.wav); st = stats(a.wav)
    ch = int(f.get('channels', 1))
    s2 = ebu(a.wav, pre='pan=stereo|c0=c0|c1=c0') if ch == 1 else m
    print(f'loudness: {m["I"]:.1f} LUFS as the file · {s2["I"]:.1f} LUFS on two speakers · true peak {m["TP"]:.1f} dBFS')
    print(f'sample peak {st["peak"]:.2f} dB · samples at the peak value {st["peak_count"]:.0f} · flat factor {st["flat"]:.1f} '
          '(flat factor > 0 = clipped runs)')
    e = ff(a.wav, 'silencedetect=noise=-40dB:d=0.15')
    gaps = re.findall(r'silence_end: ([\d.]+) \| silence_duration: ([\d.]+)', e)
    print(f'gaps >= 0.15 s under -40 dB: {len(gaps)}' + ('' if not gaps else ' -> ' +
          ', '.join(f'{float(t) - float(d):.2f}s ({float(d):.2f})' for t, d in gaps)))
    q = sorted(series(a.wav, 50))[:5]
    print('quietest 50 ms windows (noise between words): ' + ' '.join(f'{x:.1f}' for x in q))

if __name__ == '__main__':
    p = argparse.ArgumentParser(); sub = p.add_subparsers(dest='c', required=True)
    r = sub.add_parser('raw'); r.add_argument('wav')
    s = sub.add_parser('simulate'); s.add_argument('wav'); s.add_argument('--voice-end', type=float, required=True)
    for k, d in [('hp', 80), ('pre', -26), ('th', -24), ('ratio', 3), ('attack', 10), ('release', 100),
                 ('target', -16), ('limit', -2)]:
        s.add_argument('--' + k, type=float, default=d)
    q = sub.add_parser('processed'); q.add_argument('wav')
    a = p.parse_args()
    {'raw': cmd_raw, 'simulate': cmd_simulate, 'processed': cmd_processed}[a.c](a)
