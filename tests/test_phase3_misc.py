"""Phase 3 (owner Nov 26): pronunciation dictionary, content mix, cross-platform baselines, Piper peak limit."""
import wave

import numpy as np

from studio import make_video, mix, pronounce, xplat


def test_dictionary_respells_for_the_voice_only_and_leaves_english_alone():
    es = pronounce.apply("La casa de Jason está en Key Lento, en Vice City.", "es")
    assert "Yéison" in es and "Ki Lento" in es and "Váis Síti" in es
    assert pronounce.apply("Jason lives in Vice City.", "en") == "Jason lives in Vice City."
    assert "GTA" in pronounce.apply("GTA seis", "es")  # Piper says GTA right: no respelling (voice check Nov 26)
    assert pronounce.lang_of_voice("piper:es_MX-claude-high") == "es" and pronounce.lang_of_voice("af_heart") == "en"


def test_peak_limit_removes_clipping(tmp_path):
    p = tmp_path / "x.wav"
    with wave.open(str(p), "wb") as w:
        w.setnchannels(1), w.setsampwidth(2), w.setframerate(22050)
        w.writeframes((np.sin(np.linspace(0, 200, 22050)) * 32767).astype(np.int16).tobytes())
    make_video.peak_limit(p)
    with wave.open(str(p)) as w:
        x = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16)
    assert 20 * np.log10(np.abs(x).max() / 32767) <= -1.4


def test_mix_categories():
    assert mix.category({"slug": "gta6-interactive-map-howto", "short": [{"media": "media/site/a.mp4"}]}) == "map_tutorial"
    assert mix.category({"slug": "gta6-skunk-ape-where", "short_title": "GTA 6 Bigfoot location"}) == "secrets"
    assert mix.category({"slug": "gta6-barber-shop-where", "short": [{"chart": {"type": "map"}}]}) == "location"
    assert mix.category({"slug": "x", "experiment": True}) == "experimental"
    assert sum(mix.targets().values()) == 100


def test_xplat_keeps_platforms_separate():
    rows = [{"platform": "tiktok", "lang": "en", "views": v, "format": "news/facts"} for v in (100, 120, 140)] + \
           [{"platform": "tiktok", "lang": "en", "views": 7000, "format": "map/location"}] + \
           [{"platform": "instagram", "lang": "en", "views": None, "likes": v, "format": "news/facts"} for v in (5, 8, 9, 40)]
    base = xplat.add_baselines(rows)
    assert base[("tiktok", "en")] == 130 and base[("instagram", "en")] == 8.5
    assert rows[3]["rel"] == round(7000 / 130, 2)
    t = xplat.across(rows)
    assert "tiktok" in t["news/facts"]["median_rel"] and t["map/location"]["n"] == {"tiktok": 1}
    assert xplat.fmt_of("GTA 6 barber shop location: the closest one") == "map/location"
    assert xplat.fmt_of("GTA protagonists ranked: CJ isn't S tier") == "tier list"
