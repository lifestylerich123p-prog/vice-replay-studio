import pytest
from studio import mappins


def test_places_and_grid_cells():
    x, y = mappins.where("Vice City")
    assert 0.6 < x < 0.75 and 0.45 < y < 0.6
    gx, gy = mappins.where("g7")
    assert abs(gx - x) < 0.08 and abs(gy - y) < 0.05  # Vice City sits in grid cell G7 on Rockstar's map
    with pytest.raises(KeyError):
        mappins.where("Los Santos")
