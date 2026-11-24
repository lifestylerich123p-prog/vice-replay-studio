import pytest
from studio import mappins


def test_places_and_grid_cells():
    x, y = mappins.where("Vice City")
    assert 0.6 < x < 0.75 and 0.45 < y < 0.6
    gx, gy = mappins.where("g7")
    assert abs(gx - x) < 0.08 and abs(gy - y) < 0.05  # Vice City sits in grid cell G7 on Rockstar's map
    with pytest.raises(KeyError):
        mappins.where("Los Santos")


def test_map_card_zooms_to_the_pin():
    from studio import charts
    spec = {"type": "map", "at": "Kelly County", "label": "UFO", "n": 1, "_dur": 2.0}
    first = charts.map_frame(None, spec, 0.0, 108, 192)
    last = charts.map_frame(None, spec, 1.9, 108, 192)
    assert first.size == last.size == (108, 192) and first.tobytes() != last.tobytes()
