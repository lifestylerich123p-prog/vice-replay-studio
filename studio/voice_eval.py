"""Objective checks for the free narration voices (owner Nov 26, Phase 3 #7: "speech recognition accuracy alone does
not establish that a voice is natural or entertaining. Evaluate: pronunciation, natural pacing, emotional expression,
comedic timing, audio clipping, intelligibility, Spanish accents, English GTA place names, audience retention").

    python -m studio.voice_eval            # Spanish: Piper raw vs Piper + dictionary vs Kokoro em_alex + dictionary

Measured here (free, local): pace (words/s), clipping (peak dBFS, share of samples at full scale), loudness (RMS),
pauses (silence share, longest gap), intelligibility (Whisper word match) and, per GTA term, whether Whisper heard
it as the real name. NOT measurable here, written as such in the report: emotional expression, comedic timing and
accent naturalness (need a listener) and retention (needs the Spanish channel's Analytics per voice). Writes
content/learn/voice-eval-<date>.md.
"""
import datetime as dt
import difflib
import json
import re
import tempfile
import unicodedata
import wave
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
TEST_ES = [
    ("Tu primera máscara en GTA seis está en Key Lento, junto a la casa de Jason.", ["GTA", "Key Lento", "Jason"]),
    ("Vice City es Miami de verdad, y Little Cuba es la Pequeña Habana.", ["Vice City", "Little Cuba"]),
    ("La barbería más cercana es Barnacle Beauties, en el sur de Key Lento.", ["Barnacle Beauties", "Key Lento"]),
    ("Las guías cuentan diecinueve Pay 'n' Spray, de Key Lento a Port Gellhorn.", ["Pay 'n' Spray", "Port Gellhorn"]),
    ("El Bigfoot de GTA seis aparece de noche en Cottonmouth Lake, ¡no lo pierdas!", ["Bigfoot", "Cottonmouth Lake"]),
]
SAY_AS = {"GTA": ["gta", "ge te a", "getea", "g t a"]}  # what counts as "heard right" besides the spelling itself


def norm(s):
    s = unicodedata.normalize("NFKD", s.lower())
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9 ]+", " ", s).split()


def audio_stats(wav_path):
    with wave.open(str(wav_path)) as w:
        sr, n, ch, sw = w.getframerate(), w.getnframes(), w.getnchannels(), w.getsampwidth()
        raw = w.readframes(n)
    x = np.frombuffer(raw, dtype={2: np.int16, 4: np.int32}[sw]).astype(np.float64)
    x = x.reshape(-1, ch).mean(axis=1) / float(2 ** (8 * sw - 1))
    dur = len(x) / sr
    peak = float(np.max(np.abs(x))) or 1e-9
    rms = float(np.sqrt(np.mean(x ** 2))) or 1e-9
    win = int(sr * 0.03)
    frames = x[: len(x) // win * win].reshape(-1, win)
    db = 20 * np.log10(np.sqrt((frames ** 2).mean(axis=1)) + 1e-9)
    silent = db < -40
    longest, run = 0, 0
    for s in silent[2:-2]:  # ignore the edges
        run = run + 1 if s else 0
        longest = max(longest, run)
    return {"dur": round(dur, 2), "peak_dbfs": round(20 * np.log10(peak), 1),
            "clipped_pct": round(100 * float(np.mean(np.abs(x) >= 0.999)), 3), "rms_dbfs": round(20 * np.log10(rms), 1),
            "silence_pct": round(100 * float(silent.mean()), 1), "longest_pause_s": round(longest * 0.03, 2)}


def heard(term, transcript):
    tw, want = norm(transcript), [norm(term)] + [norm(a) for a in SAY_AS.get(term, [])]
    for w in want:
        k = len(w)
        for i in range(len(tw) - k + 1):
            if difflib.SequenceMatcher(None, " ".join(tw[i:i + k]), " ".join(w)).ratio() >= 0.8:
                return True
    return False


def word_match(script, transcript):
    a, b = norm(script), norm(transcript)
    return round(difflib.SequenceMatcher(None, a, b).ratio(), 2)


def run(variants=None, tests=TEST_ES, lang="es"):
    from . import make_video, pronounce
    from .vice import qc
    variants = variants or [("Piper es_MX, no dictionary", "piper:es_MX-claude-high", False),
                            ("Piper es_MX + dictionary", "piper:es_MX-claude-high", True),
                            ("Kokoro em_alex + dictionary", "em_alex", True)]
    real_apply = pronounce.apply
    rows = []
    with tempfile.TemporaryDirectory() as td:
        for name, voice, lex in variants:
            pronounce.apply = real_apply if lex else (lambda text, lang_: text)
            per = []
            try:
                for k, (sent, terms) in enumerate(tests):
                    base = Path(td) / f"{abs(hash(name)) % 10**6}_{k}"
                    out = make_video.tts(sent, voice, "+8%", base)
                    wav = Path(out) if out else base.with_suffix(".wav")
                    if wav.suffix != ".wav":
                        conv = wav.with_suffix(".conv.wav")
                        make_video.subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(wav), str(conv)], check=True)
                        wav = conv
                    st = audio_stats(wav)
                    words = qc.transcribe(wav, lang=lang)
                    text = " ".join(w["w"] for w in words) if words else ""
                    per.append({**st, "wps": round(len(sent.split()) / max(st["dur"], 0.1), 2),
                                "match": word_match(sent, text), "terms": {t: heard(t, text) for t in terms},
                                "heard": text.strip()})
            finally:
                pronounce.apply = real_apply
            terms = [ok for p in per for ok in p["terms"].values()]
            rows.append({"voice": name, "per": per,
                         "wps": round(float(np.mean([p["wps"] for p in per])), 2),
                         "match": round(float(np.mean([p["match"] for p in per])), 2),
                         "terms_ok": f"{sum(terms)}/{len(terms)}",
                         "peak_dbfs": max(p["peak_dbfs"] for p in per), "clipped_pct": max(p["clipped_pct"] for p in per),
                         "longest_pause_s": max(p["longest_pause_s"] for p in per)})
    return rows


def report(rows, lang="es"):
    day = dt.date.today().isoformat()
    L = [f"# Voice check ({lang}), {day} (`python -m studio.voice_eval`)", "",
         "| Voice | Words/s | Whisper word match | GTA terms heard right | Peak dBFS | Clipped % | Longest pause |",
         "|---|---|---|---|---|---|---|"]
    for r in rows:
        L.append(f"| {r['voice']} | {r['wps']} | {r['match']} | {r['terms_ok']} | {r['peak_dbfs']} | {r['clipped_pct']} | "
                 f"{r['longest_pause_s']} s |")
    L += ["", "Per sentence (what Whisper heard):"]
    for r in rows:
        L.append(f"- **{r['voice']}**")
        for p in r["per"]:
            miss = [t for t, ok in p["terms"].items() if not ok]
            L.append(f"  - {p['heard'][:110]!r} (match {p['match']}{', missed: ' + ', '.join(miss) if miss else ''})")
    L += ["", "Not measured here (needs a listener or real data): emotional expression, comedic timing, how natural the "
          "accent sounds to Latin American / Spanish / US Latino viewers, and retention (compare % watched by voice once "
          "the Spanish channel's Analytics are pulled). Natural pace for Spanish Shorts narration is roughly 2.5-3.2 "
          "words/s; clipping should stay at 0% with peaks under -1 dBFS.", ""]
    out = ROOT / "content" / "learn" / f"voice-eval-{day}.md"
    out.write_text("\n".join(L))
    return out


def main():
    rows = run()
    out = report(rows)
    print(out.read_text())


if __name__ == "__main__":
    main()
