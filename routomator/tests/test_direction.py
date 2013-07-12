import pytest

@pytest.mark.parametrize(('input', 'expected'), [
    ((7,4), '4'),
    ((3,6), '1'),
    ((5,8), '2')
    ])
def test_cell_direction(dir_raster, input, expected):
    assert dir_raster._cell_direction(input) == expected

@pytest.mark.parametrize(('input', 'expected'), [
    ((7,4), (8,5)),
    ((3,6), (3,5)),
    ((8,5), (9,5))
    ])
def test_next_downstream_cell(dir_raster, input, expected):
    assert dir_raster.next_downstream_cell(input) == expected

@pytest.mark.parametrize(('input', 'expected'), [
    ((7,4), [(7,4), (8,5), (9,5)]),
    ((3,6), [(3,6), (3,5), (4,5), (5,5), (6,5), (7,5), (8,5), (9,5)]),
    ((5,8), [(5,8), (6,7), (7,6), (8,5), (9,5)])
    ])
def test_downstream(dir_raster, input, expected):
    assert set(dir_raster.all_downstream_cells(input)) == set(expected)


'''    
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
'''
