"""Pronunciation dictionary for the narration (owner Nov 26, Phase 3 #7: "Build a pronunciation dictionary for
difficult terms, including GTA, Vice City, character names and location names").

Only the voice sees these respellings: on-screen text and captions keep the real names. One file per language,
config/pronounce-<lang>.json: {"terms": {"Vice City": "Vais Síti", ...}}. Whole words, case-insensitive, longest
first. Respellings follow how Spanish-speaking GTA creators say them (English names said the English way, written
so the Mexican Spanish Piper voice reads them like that). Test a change with
`python -m studio.voice_eval` (word match + per-term check).
"""
import json
import re
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


@lru_cache(maxsize=4)
def terms(lang):
    p = ROOT / "config" / f"pronounce-{lang}.json"
    try:
        return json.loads(p.read_text()).get("terms", {})
    except (OSError, ValueError):
        return {}


def apply(text, lang):
    t = terms(lang)
    if not t or not text:
        return text
    for k in sorted(t, key=len, reverse=True):
        text = re.sub(r"(?<![\w'])" + re.escape(k) + r"(?![\w'])", t[k], text, flags=re.I)
    return text


def lang_of_voice(voice):
    v = (voice or "").lower()
    return "es" if v.startswith(("piper:es", "em_", "ef_")) or "viral-adam" in v else "en"
