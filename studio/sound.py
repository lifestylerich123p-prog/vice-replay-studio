"""Original, synthesized audio for Vice Replay: a synthwave theme and transition sound effects.
Everything is generated from code, so there is nothing to license and no Content ID risk."""
import wave
from pathlib import Path

import numpy as np

SR = 48000


def _write(path, x):
    x = np.asarray(x, dtype=np.float32)
    if x.ndim == 1:
        x = np.stack([x, x], axis=1)
    peak = np.max(np.abs(x)) or 1.0
    x = (x / peak * 0.89 * 32767).astype(np.int16)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(x.tobytes())
    return path


def _lowpass(x, cutoff):
    """One-pole lowpass; cutoff may be a scalar or a per-sample array."""
    cutoff = np.broadcast_to(np.asarray(cutoff, dtype=np.float64), x.shape)
    a = 1 - np.exp(-2 * np.pi * cutoff / SR)
    y = np.empty_like(x)
    acc = 0.0
    for i in range(len(x)):
        acc += a[i] * (x[i] - acc)
        y[i] = acc
    return y


def _lowpass_fast(x, cutoff):
    # vectorised fixed-cutoff one-pole via scipy-free recursion in chunks (good enough for pads/bass)
    a = 1 - np.exp(-2 * np.pi * cutoff / SR)
    y = np.empty_like(x)
    acc = 0.0
    for i, v in enumerate(x):
        acc += a * (v - acc)
        y[i] = acc
    return y


def _saw(freq, n, detune=0.0):
    t = np.arange(n) / SR
    f = freq * (1 + detune)
    return 2 * ((t * f) % 1.0) - 1


def _env(n, attack, release):
    e = np.ones(n)
    a, r = int(attack * SR), int(release * SR)
    if a:
        e[:a] = np.linspace(0, 1, a)
    if r:
        e[-r:] *= np.linspace(1, 0, r)
    return e


def note(name):
    names = {"C": -9, "C#": -8, "D": -7, "D#": -6, "E": -5, "F": -4, "F#": -3, "G": -2, "G#": -1, "A": 0, "A#": 1, "B": 2}
    pitch, octave = name[:-1], int(name[-1])
    return 440.0 * 2 ** ((names[pitch] + 12 * (octave - 4)) / 12)


# Our own Content-ID-safe tracks (Nov 22, owner: "find better audio that connects"): one song on every video was
# tiring and another "template" signal. Each mood: (bpm, chords, bass roots). make_video picks one per episode.
MOODS = {
    "night": (100, [["A3", "C4", "E4"], ["F3", "A3", "C4"], ["C4", "E4", "G4"], ["G3", "B3", "D4"]], ["A1", "F1", "C2", "G1"]),
    "hype": (124, [["E3", "G3", "B3"], ["C3", "E3", "G3"], ["G3", "B3", "D4"], ["D3", "F#3", "A3"]], ["E1", "C1", "G1", "D1"]),
    "tension": (112, [["D3", "F3", "A3"], ["A#2", "D3", "F3"], ["F3", "A3", "C4"], ["C3", "E3", "G3"]], ["D1", "A#0", "F1", "C1"]),
    "bright": (118, [["C3", "E3", "G3"], ["G3", "B3", "D4"], ["A3", "C4", "E4"], ["F3", "A3", "C4"]], ["C1", "G1", "A1", "F1"]),
}


def theme(path, bpm=100, loops=2, seed=7, mood=None):
    """Synthwave loop: pad + 8th-note octave bass + drums (8 bars per loop). Default Am - F - C - G (the original
    night-drive theme); mood="hype"/"tension"/"bright" changes tempo and chords."""
    rng = np.random.default_rng(seed)
    chords = [["A3", "C4", "E4"], ["F3", "A3", "C4"], ["C4", "E4", "G4"], ["G3", "B3", "D4"]]
    roots = ["A1", "F1", "C2", "G1"]
    if mood:
        bpm, chords, roots = MOODS[mood]
    beat = 60 / bpm
    bar = 4 * beat
    total = int(8 * bar * loops * SR)
    mix = np.zeros(total)
    for lp in range(loops):
        for ci in range(4):
            start = int((lp * 8 + ci * 2) * bar * SR)
            n = int(2 * bar * SR)
            # pad: 3 detuned saws per chord note, soft attack, lowpassed
            pad = np.zeros(n)
            for nm in chords[ci]:
                for d in (-0.006, 0.0, 0.007):
                    pad += _saw(note(nm), n, d)
            pad = _lowpass_fast(pad / 9, 1400) * _env(n, 0.35, 0.4)
            mix[start:start + n] += 0.32 * pad
            # bass: 8th-note octave pattern on the root
            step = int(beat / 2 * SR)
            for k in range(16):
                f = note(roots[ci]) * (2 if k % 2 else 1)
                m = step
                b = _saw(f, m) * _env(m, 0.005, 0.06)
                s = start + k * step
                mix[s:s + m] += 0.30 * _lowpass_fast(b, 700)
    # drums
    beat_n = int(beat * SR)
    t = np.arange(int(0.45 * SR)) / SR
    kick = np.sin(2 * np.pi * (45 + 110 * np.exp(-t * 28)) * t) * np.exp(-t * 7)
    t2 = np.arange(int(0.25 * SR)) / SR
    snare = (rng.standard_normal(len(t2)) * 0.6 + np.sin(2 * np.pi * 190 * t2) * 0.4) * np.exp(-t2 * 16)
    t3 = np.arange(int(0.05 * SR)) / SR
    hat_noise = rng.standard_normal(len(t3))
    hat = (hat_noise - _lowpass_fast(hat_noise, 6000)) * np.exp(-t3 * 70)
    beats = int(total / beat_n)
    for b in range(beats):
        s = b * beat_n
        if b % 4 in (0, 2):
            mix[s:s + len(kick)] += 0.9 * kick[:max(0, total - s)]
        if b % 4 in (1, 3):
            mix[s:s + len(snare)] += 0.35 * snare[:max(0, total - s)]
        for h in (0, beat_n // 2):
            hs = s + h
            mix[hs:hs + len(hat)] += 0.12 * hat[:max(0, total - hs)]
    # simple stereo width: delayed copy on the right channel
    d = int(0.012 * SR)
    right = np.concatenate([np.zeros(d), mix[:-d]])
    return _write(path, np.stack([mix, 0.85 * mix + 0.15 * right], axis=1))


def whoosh(dur=0.55, seed=1):
    rng = np.random.default_rng(seed)
    n = int(dur * SR)
    x = rng.standard_normal(n)
    sweep = np.geomspace(300, 7000, n)
    y = _lowpass(x, sweep) - _lowpass(x, sweep * 0.35)
    env = np.sin(np.linspace(0, np.pi, n)) ** 2
    return y * env


def impact(dur=0.9, seed=2):
    rng = np.random.default_rng(seed)
    t = np.arange(int(dur * SR)) / SR
    boom = np.sin(2 * np.pi * (38 + 90 * np.exp(-t * 18)) * t) * np.exp(-t * 4.5)
    click = rng.standard_normal(len(t)) * np.exp(-t * 60) * 0.5
    return boom + _lowpass_fast(click, 3000)


def sfx_track(path, total, whooshes, impacts):
    """One stereo track with whooshes centred on segment cuts and impacts on the hook."""
    out = np.zeros(int(total * SR) + SR)
    w, im = whoosh(), impact()
    for tm in whooshes:
        s = max(0, int((tm - 0.28) * SR))
        seg = w[: len(out) - s]
        out[s:s + len(seg)] += 0.45 * seg / (np.max(np.abs(w)) or 1)
    for tm in impacts:
        s = max(0, int(tm * SR))
        seg = im[: len(out) - s]
        out[s:s + len(seg)] += 0.8 * seg / (np.max(np.abs(im)) or 1)
    return _write(path, out[: int(total * SR)])


if __name__ == "__main__":
    root = Path(__file__).resolve().parent.parent / "assets" / "music"
    root.mkdir(parents=True, exist_ok=True)
    print(theme(root / "vice-replay-theme.wav"))
