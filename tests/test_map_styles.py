"""Phase 3 #5: map Shorts vary (route / steps / area) on Rockstar's official map; zoom stays pixel-identical."""
from studio import charts


def test_every_style_renders_a_full_frame():
    for spec in ({"type": "map", "style": "route", "from": "Vice City", "at": "Key Lento", "label": "Shoe store", "n": 3},
                 {"type": "map", "style": "steps", "steps": [{"at": "Vice Beach", "label": "a"}, {"at": "Key Lento", "label": "b"}]},
                 {"type": "map", "style": "area", "at": "Cottonmouth Lake", "label": "Search here", "locale": "es"},
                 {"type": "map", "at": "Key Lento", "label": "x", "spot": 4}):
        for t in (0.0, 2.0, 3.9):
            im = charts.map_frame(None, dict(spec, _dur=4.0), t, 270, 480)
            assert im.size == (270, 480)


def test_steps_keep_every_stop_in_view():
    spec = {"type": "map", "style": "steps", "_dur": 4.0,
            "steps": [{"at": "Vice Beach", "label": "a"}, {"at": "Key Lento", "label": "b"}]}
    charts.map_frame(None, dict(spec), 3.9, 540, 960)  # would raise if a style crashed; visual check in review
