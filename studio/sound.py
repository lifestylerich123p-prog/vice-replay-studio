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


def pop(dur=0.16, seed=3):
    """A short, soft synth pop for a word or number landing on a lettering card (Nov 23)."""
    rng = np.random.default_rng(seed)
    t = np.arange(int(dur * SR)) / SR
    tone = np.sin(2 * np.pi * (520 + 700 * np.exp(-t * 40)) * t) * np.exp(-t * 28)
    tick = rng.standard_normal(len(t)) * np.exp(-t * 220) * 0.35
    return tone + _lowpass_fast(tick, 5000)


def swell(dur=0.42, seed=4):
    """Nov 24 (owner: "change the sound used to change between slides, I don't like it"): a soft synthwave swell
    instead of the noise whoosh. Two detuned saws a fifth apart glide up, filtered and faded in/out: musical, quiet."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    f0 = 220 * np.geomspace(1.0, 1.5, n)
    y = np.zeros(n)
    for mult, det in ((1.0, 0.0), (1.0, 0.006), (1.5, 0.004)):
        ph = 2 * np.pi * np.cumsum(f0 * mult * (1 + det)) / SR
        y += 2 * ((ph / (2 * np.pi)) % 1.0) - 1
    y = _lowpass(y, np.geomspace(600, 2600, n))
    env = np.sin(np.linspace(0, np.pi, n)) ** 1.5
    return y * env


def tick(dur=0.09, seed=5):
    """A tiny, clean UI tick (the most minimal option)."""
    t = np.arange(int(dur * SR)) / SR
    return np.sin(2 * np.pi * 1800 * t) * np.exp(-t * 90)


TRANSITIONS = {"swell": (swell, 0.30), "tick": (tick, 0.22), "whoosh": (whoosh, 0.45), "none": (None, 0.0)}


def transition_choice():
    """config/channel.json "transition_sound": swell (default since Nov 24) | tick | whoosh (the old one) | none."""
    import json
    try:
        cfg = json.loads((Path(__file__).resolve().parent.parent / "config" / "channel.json").read_text())
        name = cfg.get("transition_sound", "swell")
    except (OSError, ValueError):
        name = "swell"
    return name if name in TRANSITIONS else "swell"


def sfx_track(path, total, whooshes, impacts, pops=()):
    """One stereo track with a transition sound on segment cuts (config "transition_sound"), impacts on the hook and
    soft pops where the lettering cards land a word or number (studio/vicecards.py `hits`)."""
    out = np.zeros(int(total * SR) + SR)
    make, level = TRANSITIONS[transition_choice()]
    w = make() if make else np.zeros(1)
    im, pp = impact(), pop()
    for tm in pops:
        s = max(0, int(tm * SR))
        seg = pp[: len(out) - s]
        out[s:s + len(seg)] += 0.32 * seg / (np.max(np.abs(pp)) or 1)
    for tm in whooshes if make else ():
        s = max(0, int((tm - len(w) / SR / 2) * SR))
        seg = w[: len(out) - s]
        out[s:s + len(seg)] += level * seg / (np.max(np.abs(w)) or 1)
    for tm in impacts:
        s = max(0, int(tm * SR))
        seg = im[: len(out) - s]
        out[s:s + len(seg)] += 0.8 * seg / (np.max(np.abs(im)) or 1)
    return _write(path, out[: int(total * SR)])

def dembow(path, bpm=96, bars=16, seed=11):
    """Our own reggaeton/dembow beat (owner Nov 24: "the video itself has to have that Latino way"; Spanish channel,
    Miami Latino audience). Built here from scratch, so it is Content-ID safe: dembow kick/snare pattern (3+3+2 feel),
    a guira-style shaker on every 16th, a bass on the tresillo, and a marimba-like pluck on the Am-F-C-G loop."""
    rng = np.random.default_rng(seed)
    step = 60.0 / bpm / 4
    n_step = int(step * SR)
    total = n_step * 16 * bars
    out = np.zeros(total + SR)

    def add(sig, at, gain):
        i = int(at)
        j = min(len(out), i + len(sig))
        out[i:j] += gain * sig[: j - i]

    def kick():
        n = int(0.32 * SR); t = np.arange(n) / SR
        f = 48 + 90 * np.exp(-t * 28)
        return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 9)

    def snare():
        n = int(0.16 * SR); t = np.arange(n) / SR
        noise = np.diff(rng.standard_normal(n + 1))  # crude highpass
        return (0.55 * noise / 3 + 0.5 * np.sin(2 * np.pi * 210 * t)) * np.exp(-t * 26)

    def shaker(accent):
        n = int(0.05 * SR); t = np.arange(n) / SR
        noise = np.diff(np.diff(rng.standard_normal(n + 2)))
        return noise / 6 * np.exp(-t * (70 if accent else 110))

    def pluck(freq):
        n = int(0.28 * SR); t = np.arange(n) / SR
        return (np.sin(2 * np.pi * freq * t) + 0.35 * np.sin(2 * np.pi * 4 * freq * t) * np.exp(-t * 30)) * np.exp(-t * 11)

    def bass(freq, dur):
        n = int(dur * SR); t = np.arange(n) / SR
        return np.tanh(1.8 * np.sin(2 * np.pi * freq * t)) * np.exp(-t * 3.2) * _env(n, 0.005, 0.03)

    chords = [["A3", "C4", "E4"], ["F3", "A3", "C4"], ["C4", "E4", "G4"], ["G3", "B3", "D4"]]
    roots = ["A1", "F1", "C2", "G1"]
    K, S = kick(), snare()
    for b in range(bars):
        base = b * 16 * n_step
        ch, root = chords[b % 4], note(roots[b % 4])
        for s in (0, 4, 8, 12):
            add(K, base + s * n_step, 0.95)
        for s in (3, 6, 11, 14):  # the dembow snare
            add(S, base + s * n_step, 0.55)
        for s in range(16):
            add(shaker(s % 2 == 0), base + s * n_step, 0.22 if s % 2 == 0 else 0.13)
        for s, ln in ((0, 3), (3, 3), (6, 2), (8, 3), (11, 3), (14, 2)):  # tresillo bass
            add(bass(root, ln * step), base + s * n_step, 0.5)
        for s in (2, 6, 10, 14):  # off-beat marimba stab
            for k, nm in enumerate(ch):
                add(pluck(note(nm)), base + s * n_step + k * 40, 0.16)
    x = out[:total]
    x = np.tanh(1.3 * x / (np.max(np.abs(x)) or 1))
    return _write(path, x)

if __name__ == "__main__":
    root = Path(__file__).resolve().parent.parent / "assets" / "music"
    root.mkdir(parents=True, exist_ok=True)
    print(theme(root / "vice-replay-theme.wav"))
