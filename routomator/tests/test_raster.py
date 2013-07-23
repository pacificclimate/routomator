import pytest

from tempfile import NamedTemporaryFile

from routomator.raster import AsciiRaster, DirectionRaster

def raster_from_string(s):
    with NamedTemporaryFile('w', suffix='.txt') as f:
        f.write(s)
        f.flush()
        r = AsciiRaster(f.name)
    return r

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

def test_union(raster):
    r1 = raster_from_string("""ncols 10
nrows 10
xllcorner -139
yllcorner 47
cellsize 0.0625
NODATA_value 0
0 0 0 0 0 0 0 0 0 0
0 0 0 0 0 0 0 0 0 0
0 0 1 1 1 0 0 0 0 0
0 0 1 1 1 0 0 0 0 0
0 0 0 2 0 0 0 0 0 0
0 0 0 0 0 0 0 0 0 0
0 0 0 0 0 0 0 0 0 0
0 0 0 0 0 0 0 0 0 0
0 0 0 0 0 0 0 0 0 0
0 0 0 0 0 0 0 0 0 0
""")
    r2 = raster_from_string("""ncols 10
nrows 10
xllcorner -139
yllcorner 47
cellsize 0.0625
NODATA_value 0
0 0 0 0 0 0 0 0 0 0
0 0 0 0 0 0 0 0 0 0
0 0 0 0 0 0 0 0 0 0
0 0 0 0 0 0 0 0 0 0
0 0 0 0 0 0 0 0 0 0
0 0 0 0 0 0 0 0 0 0
0 0 0 0 0 0 0 0 0 0
0 0 0 2 0 0 0 0 0 0
0 0 1 1 1 0 0 0 0 0
0 0 0 0 0 0 0 0 0 0
""")
    expected = raster_from_string("""ncols 10
nrows 10
xllcorner -139
yllcorner 47
cellsize 0.0625
NODATA_value 0
0 0 0 0 0 0 0 0 0 0
0 0 0 0 0 0 0 0 0 0
0 0 1 1 1 0 0 0 0 0
0 0 1 1 1 0 0 0 0 0
0 0 0 2 0 0 0 0 0 0
0 0 0 0 0 0 0 0 0 0
0 0 0 0 0 0 0 0 0 0
0 0 0 2 0 0 0 0 0 0
0 0 1 1 1 0 0 0 0 0
0 0 0 0 0 0 0 0 0 0
""")
    r1.union(r2)
    assert r1.raster == expected.raster

@pytest.mark.parametrize(('input', 'expected'), [
    (raster_from_string("""ncols 5
nrows 5
xllcorner -139
yllcorner 47
cellsize 0.0625
NODATA_value 0
0 0 1 1 1
0 0 1 1 1
0 0 1 1 1
0 0 1 1 1
0 0 1 1 1
"""), raster_from_string("""ncols 5
nrows 5
xllcorner -139
yllcorner 47
cellsize 0.0625
NODATA_value 2
2 2 1 1 1
2 2 1 1 1
2 2 1 1 1
2 2 1 1 1
2 2 1 1 1
"""))
    ])
def test_change_nodata(input, expected):
    input.change_nodata(2)
    assert input.raster == expected.raster