import pytest

from tempfile import NamedTemporaryFile

from routomator.raster import AsciiRaster

test_data = """ncols 10
nrows 10
xllcorner -139
yllcorner 47
cellsize 0.0625
NODATA_value 0
0 0 0 0 0 0 0 0 0 0
0 0 0 0 0 0 0 0 0 0
0 0 4 5 6 4 0 0 0 0
0 0 4 5 6 4 4 0 0 0
0 0 4 4 6 5 4 4 0 0
0 0 3 3 3 3 3 3 3 -9
0 0 2 1 8 1 2 2 0 0
0 0 2 1 8 2 2 0 0 0
0 0 2 1 8 2 0 0 0 0
0 0 0 0 0 0 0 0 0 0
"""

@pytest.fixture(scope="session")
def raster():
    with NamedTemporaryFile('w', suffix='.txt') as f:
        f.write(test_data)
        f.flush()
        r = AsciiRaster(f.name)
    return r
