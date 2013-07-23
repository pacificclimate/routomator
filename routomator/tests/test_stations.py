import pytest

from tempfile import NamedTemporaryFile

from routomator.station import Station, generate_shortnames, load_stations, directly_downstream_station, generate_upstream_station_dict, generate_single_subbasin_mask
from routomator.raster import AsciiRaster, DirectionRaster

def raster_from_string(s):
    with NamedTemporaryFile('w', suffix='.txt') as f:
        f.write(s)
        f.flush()
        r = AsciiRaster(f.name)
    return r

s = '''ID,STATION,LAT,LONG,PROVINCE,GROSS_AREA,EFFECTIVE_
"07EA001","FINLAY RIVER AT WARE",47.34375,-138.78125,"BC",8000,
"07EA002","KWADACHA RIVER NEAR WARE",47.15625,-138.78125,"BC",2410,
"07EA004","INGENIKA RIVER ABOVE SWANNELL RIVER",47.28125,-138.40625,"BC",10000,
'''.split('\n')

# Station Raster Coords
@pytest.mark.parametrize(('input', 'expected'), [
    (Station("FINLAY RIVER AT WARE",47.34375,-138.78125), (3,4)),
    (Station("KWADACHA RIVER NEAR WARE",47.15625,-138.78125), (3,7)),
    (Station("INGENIKA RIVER ABOVE SWANNELL RIVER",47.28125,-138.40625), (9,5))
    ])
def test_station_raster_coords(raster, input, expected):
    assert input.raster_coords(raster) == expected

# Station Vic Coords
@pytest.mark.parametrize(('input', 'expected'), [
    (Station("FINLAY RIVER AT WARE",47.34375,-138.78125), (3,5)),
    (Station("KWADACHA RIVER NEAR WARE",47.15625,-138.78125), (3,2)),
    (Station("INGENIKA RIVER ABOVE SWANNELL RIVER",47.28125,-138.40625), (9,4))
    ])    
def test_station_vic_coords(raster, input, expected):
    assert input.vic_coords(raster) == expected

# Station Loading
@pytest.mark.parametrize(('input', 'expected'), [
    (Station("FINLAY RIVER AT WARE",47.34375,-138.78125), 0),
    (Station("KWADACHA RIVER NEAR WARE",47.15625,-138.78125), 1),
    (Station("INGENIKA RIVER ABOVE SWANNELL RIVER",47.28125,-138.40625), 2)
    ])
def test_station_load(test_stations, input, expected):
    assert input == test_stations[expected]

# Downstream Station
@pytest.mark.parametrize(('input', 'expected'), [
    ((3,4), (9,5)),
    ((3,7), (9,5))
    ])
def test_downstream_station(dir_raster, test_stations, input, expected):
    assert directly_downstream_station(test_stations, input, dir_raster) == expected

# Upstream stations
def test_upstream_station_dict(test_stations, dir_raster):
    from collections import defaultdict
    d = defaultdict(list)
    d[(9,5)] = [(3,4), (3,7)]
    assert generate_upstream_station_dict(test_stations, dir_raster) == d

# Station catchments
def test_subbasin_masks(dir_raster):
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
    assert generate_single_subbasin_mask([(3,4), (3,7)], dir_raster).raster == expected.raster

# Station shortname generation
@pytest.mark.parametrize(('input', 'expected'), [
    (
        [Station("FINLAY RIVER AT WARE",47.34375,-138.78125)],
        [Station("FINLAY RIVER AT WARE",47.34375,-138.78125, "FINLA")]
    ),
    (
        [
            Station("KWADACHA RIVER NEAR WARE",47.15625,-138.78125),
            Station("INGENIKA RIVER ABOVE SWANNELL RIVER",47.28125,-138.40625)
        ],
        [
            Station("KWADACHA RIVER NEAR WARE",47.15625,-138.78125, "KWADA"),
            Station("INGENIKA RIVER ABOVE SWANNELL RIVER",47.28125,-138.40625, "INGEN")
        ]
    )
])
def test_station_shortname(input, expected):
    generate_shortnames(input)
    assert input == expected