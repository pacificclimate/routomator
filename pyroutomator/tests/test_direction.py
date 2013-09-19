import pytest

from tempfile import NamedTemporaryFile

from routomator.raster import AsciiRaster, DirectionRaster

def raster_from_string(s):
    with NamedTemporaryFile('w', suffix='.txt') as f:
        f.write(s)
        f.flush()
        r = AsciiRaster(f.name)
    return r

# Cell Direction
@pytest.mark.parametrize(('input', 'expected'), [
    ((7,4), '4'),
    ((3,6), '1'),
    ((5,8), '2')
    ])
def test_cell_direction(dir_raster, input, expected):
    assert dir_raster._cell_direction(input) == expected

# Next Downstream Cell
@pytest.mark.parametrize(('input', 'expected'), [
    ((7,4), (8,5)),
    ((3,6), (3,5)),
    ((8,5), (9,5))
    ])
def test_next_downstream_cell(dir_raster, input, expected):
    assert dir_raster.next_downstream_cell(input) == expected

# All Downstream Cells
@pytest.mark.parametrize(('input', 'expected'), [
    ((7,4), [(7,4), (8,5), (9,5)]),
    ((3,6), [(3,6), (3,5), (4,5), (5,5), (6,5), (7,5), (8,5), (9,5)]),
    ((5,8), [(5,8), (6,7), (7,6), (8,5), (9,5)])
    ])
def test_downstream(dir_raster, input, expected):
    assert set(dir_raster.all_downstream_cells(input)) == set(expected)

# Directly Upstream Cells
@pytest.mark.parametrize(('input', 'expected'), [
    ((3,3), [(3,2), (2,2), (4,2)]),
    ((3,5), [(2,4), (2,5), (2,6), (3,6), (4,4), (4,6)])
    ])
def test_directly_upstream(dir_raster, input, expected):
    assert set(dir_raster.directly_upstream_cells(input)) == set(expected)

# All Upstream Cells
@pytest.mark.parametrize(('input', 'expected'), [
    ((3,4), [(3,4), (3,2), (3,3), (4,2), (4,3), (2,2), (2,3)])
    ])
def test_all_upstream(dir_raster, input, expected):
    assert set(dir_raster.all_upstream_cells(input)) == set(expected)

# Catchement Area
@pytest.mark.parametrize(('input', 'expected'), [
    ((3,4), raster_from_string("""ncols 10
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
""")),
    ((3,7), raster_from_string("""ncols 10
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
"""))
    ])
def test_catchment(dir_raster, input, expected):
    assert dir_raster.catchment(input).raster == expected.raster


