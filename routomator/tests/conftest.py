import pytest

from tempfile import NamedTemporaryFile

from routomator.raster import AsciiRaster

raster_data = """ncols 10
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
        f.write(raster_data)
        f.flush()
        r = AsciiRaster(f.name)
    return r

from routomator.station import load_stations

station_data = '''ID,STATION,LAT,LONG,PROVINCE,GROSS_AREA,EFFECTIVE_
"07EA001","FINLAY RIVER AT WARE",47.34375,-138.78125,"BC",8000,
"07EA002","KWADACHA RIVER NEAR WARE",47.15625,-138.78125,"BC",2410,
"07EA004","INGENIKA RIVER ABOVE SWANNELL RIVER",47.28125,-138.40625,"BC",10000,
'''

@pytest.fixture(scope="session")
def test_stations():
    with NamedTemporaryFile('w', suffix='.csv') as f:
        f.write(station_data)
        f.flush()
        stations = load_stations(f.name)
    return stations
