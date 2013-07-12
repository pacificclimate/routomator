import pytest

from routomator.station import Station, load_stations

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

@pytest.mark.parametrize(('input', 'expected'), [
    (Station("FINLAY RIVER AT WARE",47.34375,-138.78125), 0),
    (Station("KWADACHA RIVER NEAR WARE",47.15625,-138.78125), 1),
    (Station("INGENIKA RIVER ABOVE SWANNELL RIVER",47.28125,-138.40625), 2)
    ])
def test_station_load(test_stations, input, expected):
    assert input == test_stations[expected]
