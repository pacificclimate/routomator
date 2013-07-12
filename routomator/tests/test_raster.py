import pytest

# Cell Neighbors
@pytest.mark.parametrize(('input', 'expected'), [
    ((5,5), [(4,4),(4,5),(4,6),
                 (5,4),(5,6),
                 (6,4),(6,5),(6,6)]),
    ((0,0), [(0,1),(1,0),(1,1)]),
    ((9,9), [(8,9),(9,8),(8,8)])
    ])
def test_neighbors(raster, input, expected):
    assert set(raster.cell_neighbors((input))) == set(expected)

# Raster Coords
@pytest.mark.parametrize(('input', 'expected'), [
    ((47.34375,-138.78125), (3,4)),
    ((47.15625,-138.78125), (3,7)),
    ((47.28125,-138.40625), (9,5))
    ])
def test_raster_coords(raster, input, expected):
    assert raster.raster_coords(input) == expected

# Vic Coords
@pytest.mark.parametrize(('input', 'expected'), [    
    ((47.34375,-138.78125), (3,5)),
    ((47.15625,-138.78125), (3,2)),
    ((47.28125,-138.40625), (9,4))        
    ])    
def test_vic_coords(raster, input, expected):
    assert raster.vic_coords(input) == expected

